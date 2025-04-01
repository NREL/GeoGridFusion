"""
core set of functions and utilities for geogridfusion
"""

import os
import pandas as pd
import xarray as xr
from psycopg2.extensions import connection
from geogridfusion import DATA_DIR
from geogridfusion import utilities
import json

def store_single(conn: connection, weather_df: pd.DataFrame, meta: dict, tmy: bool, source_name: str = None, coerce_year: int=1979) -> None:

    # we may want to provide some more parsing/safety for these metadata fields, like tz_offset
    # see which of these we need
    latitude = meta.get("latitude")
    longitude = meta.get("longitude")
    source_name = meta.get("Source") or source_name
    altitude = meta.get("altitude")

    # we are going to get rid of these
    # wind_height = meta.get("wind_height")
    # station = meta.get("station")

    if latitude is None or longitude is None:
        raise ValueError("Missing required latitude or longitude in metadata.")


    tz_offset = meta.get("tz")

    if tmy and (tz_offset is None or tz_offset == "+0"):
        print("coercing tmy data to year 1979")
        weather_df.index = weather_df.index.map(lambda ts: ts.replace(year=coerce_year))

    partial_hash, full_hash, size = utilities.hash_dataframe(df=weather_df, byte_count=64 * 1024 )

    with conn.cursor() as cur:

        if utilities.check_dupe(cur=cur, partial_hash=partial_hash, full_hash=full_hash):
            print("duplicate file detected, skipping insert")
            print(f"metadata of duplicate file {meta}")
            return # no changes made

        cur.execute("""
            INSERT INTO files (latitude, longitude, size, partial_hash, full_hash)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (latitude, longitude, size, partial_hash, full_hash))

        file_id = cur.fetchone()[0]
        fp = DATA_DIR / f"{file_id}.csv"
        weather_df.to_csv(fp)

        cur.execute("UPDATE files SET file_path = %s WHERE id = %s", (str(fp), file_id))

        cur.execute("""
            INSERT INTO meta (id, length, source_name, tmy, altitude, serial)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            file_id, 
            len(weather_df), 
            source_name, 
            tmy, 
            altitude, 
            json.dumps(meta)
        ))

        conn.commit()

# we do not want this available at the top level
# TODO: automatically drop null attributes in the dictionary
def _meta_dict_from_id(conn: connection, id: int, drop_null_attributes:bool=True) -> dict:

    cur = conn.cursor()

    cur.execute("""
        SELECT length, source_name, tmy, altitude, serial
        FROM meta
        WHERE id = %s
    """, (id,))

    res = cur.fetchone()
    cur.close()

    if res is None:
        return ValueError(f"no metadata found for id: {id}")

    length, source_name, tmy, altitude, serial = res

    return serial


def sources(conn: connection) -> dict:
    """
    Returns a dictionary mapping each source_name to the number of files associated with it.
    """
    cur = conn.cursor()

    cur.execute("""
        SELECT source_name, COUNT(*) 
        FROM meta
        GROUP BY source_name
        ORDER BY COUNT(*) DESC;
    """)

    results = cur.fetchall()
    cur.close()

    return {source: count for source, count in results}


def load_single(conn: connection, latitude: float, longitude: float, source_name: str = None) -> tuple[pd.DataFrame, dict]:
    """
    load the closest file pair. optionally select a source. Source name must match exactly
    """

    cur = conn.cursor()

    if source_name:
        cur.execute("""
            SELECT f.id, f.file_path
            FROM files f
            JOIN meta m ON f.id = m.id
            WHERE m.source_name = %s
            ORDER BY coords <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 1;
        """, (source_name, longitude, latitude))
    else: # any source
        cur.execute("""
            SELECT id, file_path
            FROM files
            ORDER BY coords <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 1;
        """, (longitude, latitude))

    res = cur.fetchone()
    cur.close()

    if res is None:
        raise ValueError("No matching file found near given coordinate.")

    id, fp = res

    return pd.read_csv(fp, index_col = 0), _meta_dict_from_id(conn, id)