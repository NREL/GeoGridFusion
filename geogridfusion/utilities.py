from glob import glob
import pandas as pd
import xarray as xr
import hashlib
from psycopg2.extensions import cursor
import io

def hash_dataframe(df: pd.DataFrame, byte_count=None) -> tuple[str, str, int, bytes]:
    """
    Serialize the DataFrame to CSV in-memory and return hashes and size.
    """
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    data = buffer.getvalue()
    size = len(data)

    partial_hash = hashlib.blake2b(data[:byte_count or size]).hexdigest()
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



def ds_from_uniform_csv(fnames: list[str]):
    dfs = [pd.read_csv(fname) for fname in fnames]

    d = xr.combine_by_coords(
        [
            df_i.set_index('time').to_xarray().expand_dims(gid=i)
            for i, df_i in enumerate(dfs)
        ],
    )
    
    return d