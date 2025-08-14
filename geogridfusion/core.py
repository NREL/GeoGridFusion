"""
core set of functions and utilities for geogridfusion
"""

import pandas as pd
import xarray as xr
from psycopg2.extensions import connection
from geogridfusion import (
    DATA_DIR,
    utilities,
    queries,
)

import json


def store_single(
    conn: connection,
    weather_df: pd.DataFrame,
    meta: dict,
    tmy: bool,
    source_name: str = None,
    coerce_year: int = 1979,
) -> None:
    # may want to provide some more parsing/safety for metadata fields
    # ex) tz_offset
    # see which of these we need
    latitude = meta.get("latitude")
    longitude = meta.get("longitude")
    source_name = meta.get("Source") or meta.get("source") or source_name
    altitude = meta.get("altitude")

    if source_name is None:
        raise ValueError(
            "Missing source name: source must be in 'meta' "
            "or manually provided in 'source_name'"
        )

    if latitude is None or longitude is None:
        raise ValueError("Missing required latitude or longitude in metadata.")

    tz_offset = meta.get("tz")

    if tmy and (tz_offset is None or tz_offset == "+0"):
        print("coercing tmy data to year 1979")
        weather_df.index = weather_df.index.map(lambda ts: ts.replace(year=coerce_year))

    partial_hash, full_hash, size = utilities.hash_dataframe(
        df=weather_df, byte_count=64 * 1024
    )

    with conn.cursor() as cur:
        if utilities.check_dupe(
            cur=cur, partial_hash=partial_hash, full_hash=full_hash
        ):
            print("duplicate file detected, skipping insert")
            print(f"metadata of duplicate file {meta}")
            return  # no changes made

        cur.execute(
            """
            INSERT INTO files (latitude, longitude, size, partial_hash, full_hash)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """,
            (float(latitude), float(longitude), size, partial_hash, full_hash),
        )

        file_id = cur.fetchone()[0]
        fp = DATA_DIR / f"{file_id}.csv"
        weather_df.to_csv(fp)

        cur.execute("UPDATE files SET file_path = %s WHERE id = %s", (str(fp), file_id))

        cur.execute(
            """
            INSERT INTO meta (id, length, source_name, tmy, altitude, serial)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                file_id,
                len(weather_df),
                source_name.lower(),
                tmy,
                altitude,
                json.dumps(meta),
            ),
        )

        conn.commit()


# we do not want this available at the top level
# TODO: automatically drop null attributes in the dictionary
def _meta_dict_from_id(
    conn: connection, id: int, drop_null_attributes: bool = True
) -> dict:
    cur = conn.cursor()

    cur.execute(
        """
        SELECT length, source_name, tmy, altitude, serial
        FROM meta
        WHERE id = %s
    """,
        (id,),
    )

    res = cur.fetchone()
    cur.close()

    if res is None:
        return ValueError(f"no metadata found for id: {id}")

    length, source_name, tmy, altitude, serial = res

    return serial


def sources(conn: connection) -> dict:
    """
    Returns a dictionary mapping unqiue source_names to its number of files in storage.

    ```{name: file_count}```
    """
    results = queries.count_by_source(conn=conn)

    return {source: count for source, count in results}


def load_single(
    conn: connection, latitude: float, longitude: float, source_name: str = None
) -> tuple[pd.DataFrame, dict]:
    """
    Load the closest file pair.

    Optionally select a source, name must match exactly.
    """

    cur = conn.cursor()

    if source_name:
        cur.execute(
            """
            SELECT f.id, f.file_path
            FROM files f
            JOIN meta m ON f.id = m.id
            WHERE m.source_name = %s
            ORDER BY coords <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 1;
        """,
            (source_name.lower(), longitude, latitude),
        )
    else:  # any source
        cur.execute(
            """
            SELECT id, file_path
            FROM files
            ORDER BY coords <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 1;
        """,
            (longitude, latitude),
        )

    res = cur.fetchone()
    cur.close()

    if res is None:
        raise ValueError("No matching file found near given coordinate.")

    id, fp = res

    return pd.read_csv(fp, index_col=0), _meta_dict_from_id(conn, id)


# TODO: add skip bad dims support
# TODO: add overlapping time checks, arguments
def load_many(
    conn: connection,
    source_name: str = None,
    limit: int = None,
    skip_bad_dims: bool = False,
    spatial_search: bool = False,
    spatial_search_latitude0: float = None,
    spatial_search_longitude0: float = None,
    spatial_search_distance_floor: float = None,
) -> tuple[xr.Dataset, pd.DataFrame]:
    if limit is not None and spatial_search is False:
        res = queries.limit_from_source(conn=conn, source_name=source_name, limit=limit)

    elif limit is None and spatial_search is False:
        res = queries.all_from_source(conn=conn, source_name=source_name)

    elif spatial_search is True:
        res = utilities.greedy_nearest_neighbors(
            conn=conn,
            limit=limit,
            source_name=source_name,
            latitude=spatial_search_latitude0,
            longitude=spatial_search_longitude0,
            distance_floor=spatial_search_distance_floor,
        )

    weather_query, meta_data, meta_index = utilities._parse_id_fp_serial_res(res=res)

    dfs = [(id, pd.read_csv(fname)) for id, fname in weather_query]

    # check if dataframe dimensions are different, if so report issue
    # option to skip bad dataframes?
    if any(dfs[0][1].shape != df.shape for _id, df in dfs[1:]):  # generator expr
        raise ValueError("""mismatched dimensions... (expand error for usefulness)""")

    weather_ds = xr.combine_by_coords(
        [
            df_i.set_index("time")
            .to_xarray()
            .assign_coords({"gid": id})
            .expand_dims("gid")
            for id, df_i in dfs
        ],
    )

    meta_df = pd.DataFrame(data=meta_data, index=meta_index)

    return weather_ds, meta_df
