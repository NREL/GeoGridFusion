"""
Top level functions for interacting with gridded geospatial data
"""

from typing import Union
import xarray as xr
import pandas as pd
import yaml

from geogridstore import USER_PATHS
from geogridstore.display import display_user_paths

def add_user_path(
    name : str,
    path : str,
    freqency : str,
) -> None:
    """
    add a path that can be accessed by geogridstore

    Parameters
    ----------
    name : str
        variable name that will be used to access reference the store
    path: str
        path to the store, use absolute paths for safety
    """

    with open(USER_PATHS, 'r') as user_paths:
        user_config = yaml.safe_load(user_paths) or {}

    if name not in user_config:
        user_config[name] = {}

    user_config[name]['path'] = path
    user_config[name]['freq'] = freqency

    with open(USER_PATHS, 'w') as user_paths:
        yaml.safe_dump(user_config, user_paths)


def remove_user_path(
    name : str,
    # delete : bool, # this feels dangerous
) -> None:
    """
    delete a path from geogrid store

    Parameters
    ----------
    name : str
        variable name to delete store.
    delete : bool
        delete all data at the path store.
    """

    with open(USER_PATHS, 'r') as user_paths:
        user_config = yaml.safe_load(user_paths) or {}

    if name not in user_config:
        raise ValueError(f'name: "{name}" not in saved names.')

    del user_config[name]

    with open(USER_PATHS, 'w') as user_paths:
        yaml.safe_dump(user_config, user_paths)

    
def get(
    source : str,
    group : str,
    seperate : bool,
) -> Union[tuple[xr.Dataset, pd.DataFrame], xr.Dataset]:
    """
    Extract a weather xarray dataset and metadata pandas dataframe from your zarr store. 
    `get` pulls the entire datastore into these objects. PVDeg does not make indexing available at this stage. 
    This is practical because all datavariables are stored in dask arrays so they are loaded lazily instead of into memmory when this is called.
    Choose the points you need after this method is called by using `sel`, `isel`, `loc, `iloc`.

    `store.get` is meant to match the API of other geospatial weather api's from pvdeg like `pvdeg.weather.get`, `pvdeg.weather.distributed_weather`, `GeospatialScenario.get_geospatial_data`

    Parameters
    -----------
    source : str
        name of store used by geogridstore to reference the path to your store

    group : str
        name of the group to access from your local zarr store. 
        Groups are created automatically in your store when you save data using `pvdeg.store.store`.

        *From `pvdeg.store.store` docstring*   
        Hourly PVGIS data will be saved to "PVGIS-1hr", 30 minute PVGIS to "PVGIS-30min", similarly 15 minute PVGIS will be saved to "PVGIS-15min"

    seperate : bool
        gridded geospatial data is stored joined with its metadata, if true, returns discrete data and metadata structures, otherwise returns a single xarray.Dataset
    
    Returns
    -------
    weather_ds : xr.Dataset
        Weather data for all locations requested in an xarray.Dataset using a dask array backend. This may be larger than memory.
    meta_df : pd.DataFrame
        Pandas DataFrame containing metadata for all requested locations. Each row maps to a single entry in the weather_ds.
    """

    # open dataset that lives at a path
    # split if desired
    # return appropriate result

    combined_ds = xr.open_zarr(
        store=TEMP_PATH,
        group=group 
    )

    # weather_ds, meta_df = _seperate_geo_weather_meta(ds_from_zarr=combined_ds)

    # return weather_ds, meta_df
    ...

def display_paths() -> None:
    """
    Display user paths in a jupyter notebook environment.
    """
    with open(USER_PATHS, 'r') as f:
        data = yaml.safe_load(f)

    display_user_paths(data)

