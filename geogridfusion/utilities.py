import pandas as pd
import hashlib
from psycopg2.extensions import cursor
import io
from geogridfusion import queries


def hash_dataframe(df: pd.DataFrame, byte_count=None) -> tuple[str, str, int, bytes]:
    """
    Serialize the DataFrame to CSV in-memory and return hashes and size.
    """
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    data = buffer.getvalue()
    size = len(data)

    partial_hash = hashlib.blake2b(data[: byte_count or size]).hexdigest()
    full_hash = hashlib.blake2b(data).hexdigest()

    return partial_hash, full_hash, size


def check_dupe(cur: cursor, partial_hash, full_hash) -> bool:
    """
    check if new file exists in database.
    """
    cur.execute("SELECT id FROM files WHERE partial_hash = %s", (partial_hash,))
    small_hash_dupe = cur.fetchone()
    if small_hash_dupe:
        cur.execute("SELECT id FROM files WHERE full_hash = %s", (full_hash,))
        full_hash_dupe = cur.fetchone()
        if full_hash_dupe:
            return True

    return False


def _parse_id_fp_serial_res(res):
    """
    SQL query result from columns file.id, file.file_path, meta.serial,
    parse to useful outputs.
    """

    weather_query = [(id, file_path) for id, file_path, _serial in res]
    meta_data = [serial for _id, _file_path, serial in res]
    meta_index = [id for id, _file_path, _serial in res]

    return weather_query, meta_data, meta_index


def greedy_nearest_neighbors(
    conn,
    limit: int,
    latitude: float,
    longitude: float,
    distance_floor: float = None,
    source_name: str = None,
):
    """
    greedy nearest neighbors using great circle/haversine distance
    """
    if source_name is None:
        print(
            "using points from every source, "
            "may cause errors or undesired behavior on concatenation/merge"
        )

    visited = set()  # points we have stood on
    explored = set()  # all points we have touched but not stood on

    lat, lon = latitude, longitude

    while limit is None or len(visited) < limit:
        # returns in order of distance from current (lat, lon)
        step_distances = queries._distances(
            conn,
            latitude=lat,
            longitude=lon,
            visited=list(visited),
            source_name=source_name,
            distance_floor=distance_floor,
        )

        if not step_distances:
            break

        # add current point (where we are standing)
        if step_distances[0][0] == 0:
            _, current_id, _, _ = step_distances[0]
            if current_id not in visited:
                visited.add(current_id)

        next_point = None
        for ref_dist, candidate_id, candidate_lat, candidate_lon in step_distances[1:]:
            if distance_floor and ref_dist < distance_floor:
                explored.add(candidate_id)
                continue

            next_point = (candidate_id, candidate_lat, candidate_lon)
            break

        if not next_point:
            break

        next_id, lat, lon = next_point
        visited.add(next_id)

    # get id, file_path and serial from id's
    loaded_tuples = queries.rows_by_id(conn=conn, ids=list(visited))
    return loaded_tuples


# def ds_from_uniform_csv(query_res: list[tuple]):
# moved to core.load_many
#     """
#     get dataset from many file_paths and id's.

#     query_res: list[tuple]
#         columns (id, file_path) from files table
#     """
#     dfs = [(id, pd.read_csv(fname)) for id, fname in query_res]

#     d = xr.combine_by_coords(
#         [
#             df_i.set_index('time').to_xarray().assign_coords({'gid':id}).expand_dims('gid')
#             for id, df_i in dfs
#         ],
#     )

#     return d
