"""
module containing frequently used sql query wrappers for geogridfusion
"""

from psycopg2 import sql


def count_by_source(conn) -> dict:
    cur = conn.cursor()

    cur.execute("""
        SELECT source_name, COUNT(*)
        FROM meta
        GROUP BY source_name
        ORDER BY COUNT(*) DESC;
    """)

    results = cur.fetchall()
    cur.close()

    return results


def rows_by_id(conn, ids: list[int]) -> list[tuple]:
    with conn.cursor() as cur:
        ids = ids if ids else [-1]

        query = sql.SQL("""
            SELECT
                f.id,
                f.file_path,
                m.serial
            FROM files f
            JOIN meta m on f.id = m.id
            WHERE f.id IN ({ids});
        """).format(ids=sql.SQL(",").join(sql.Placeholder() * len(ids)))

        cur.execute(query, ids)

        res = cur.fetchall()
        return res


def all_from_source(conn, source_name: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT f.id, f.file_path, m.serial
        FROM files f
        JOIN meta m ON f.id = m.id
        WHERE m.source_name = %s;
        """,
            (source_name,),
        )

        res = cur.fetchall()
        return res


def limit_from_source(conn, source_name: str, limit: int) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT f.id, f.file_path, m.serial
        FROM files f
        JOIN meta m ON f.id = m.id
        WHERE m.source_name = %s
        LIMIT %s;
        """,
            (source_name, limit),
        )

        res = cur.fetchall()
        return res


def _distances(
    conn,
    longitude: float,
    latitude: float,
    visited: list[int],
    source_name: str = None,
    distance_floor: float = None,
):
    with conn.cursor() as cur:
        visited = visited if visited else [-1]
        visited_placeholders = sql.SQL(",").join(sql.Placeholder() * len(visited))

        exclusion_clause = sql.SQL("")
        if distance_floor is not None:
            exclusion_clause = sql.SQL("""
                AND NOT EXISTS (
                    SELECT 1 FROM files fv
                    WHERE fv.id = ANY(%s) AND
                    ST_DWithin(fv.coords, f.coords, %s)
                    )
            """)

        query = sql.SQL("""
            SELECT
                ST_Distance(ST_MakePoint(%s, %s)::geography, f.coords) as ref_distance,
                f.id,
                f.latitude,
                f.longitude
            FROM files f
            JOIN meta m on f.id = m.id
            WHERE
                f.id NOT IN ({visited_ids}) AND
                (%s IS NULL OR m.source_name = %s)
                {exclusion_clause}
            ORDER BY coords <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) ASC;
        """).format(visited_ids=visited_placeholders, exclusion_clause=exclusion_clause)
        params = [longitude, latitude] + list(visited) + [source_name, source_name]
        if distance_floor is not None:
            params += [visited, distance_floor]
        params += [longitude, latitude]

        cur.execute(query, params)

        res = cur.fetchall()
        return res
