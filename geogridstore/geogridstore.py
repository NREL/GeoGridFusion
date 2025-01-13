"""
Top level functions for interacting with gridded geospatial data
"""

# Correct initialization of an "empty" Zarr dataset for region-based writing. #8878
# https://github.com/pydata/xarray/discussions/8878

from typing import Union
import xarray as xr
import pandas as pd
import numpy as np
import yaml

from geogridstore import (
    index,
    USER_PATHS,
    load_store_configs
)

from geogridstore.namespace_utils import NestedNamespace
from geogridstore.display import display_user_paths

def add_user_path(
    name : str,
    path : str,
    periods : str,
    grid_resolution: str,
    template_ds: xr.Dataset,
) -> None:
    """
    add a path that can be accessed by geogridstore

    Parameters
    ----------
    name : str
        variable name that will be used to access reference the store
    path: str
        path to the store, use absolute paths for safety
    periods: str
        number of entries on time axis. this should be changed to periods or length. 
        if data does not depend on time, enter ???
    grid_resolution: str
        resoultion in km. ex on a 2x2 km grid enter "2", for 4x4 km enter "4".
    template_ds: xr.Dataset
        template xarray dataset used to lazily intialize a zarr store, actual data not required.
        it is possible to use a lazy schema but we will not do this
    """

    # we assume there is nothing at the path already
    # add check for this

    if not isinstance(template_ds, xr.Dataset):
        raise ValueError("template_ds must be an Xarray Dataset.")

    with open(USER_PATHS, 'r') as user_paths:
        user_config = yaml.safe_load(user_paths) or {}

    if name not in user_config:
        user_config[name] = {}

    user_config[name].update({
        'path': path,
        'periods': periods,
        'grid_resolution': grid_resolution
    })

    xr.zeros_like(template_ds).to_zarr(store=path, compute=False)

    with open(USER_PATHS, 'w') as user_paths:
        yaml.safe_dump(user_config, user_paths)
    
    # update top level namespace names defined in yaml
    load_store_configs()
    


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
    source : NestedNamespace,
    # source : str,
    # group : str,
    # seperate : bool,
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

   
    Returns
    -------
    loaded_ds : xr.Dataset
        Dataset loaded as saved 
        Weather data for all locations requested in an xarray.Dataset using a dask array backend. This may be larger than memory.
    """

    combined_ds = xr.open_zarr(
        store=source.path
    )

    return combined_ds

def store(dataset: xr.Dataset, store: NestedNamespace, grid_points_fn : str, overwrite: bool = False) -> None:
    """
    Add geospatial meteorolical data to your zarr store. Data will be saved to the correct group based on its periodicity.

    This maps arbitrary spatial indexes "gids" to spatially signficant indexes that are only used to check for duplicates and repeat entries.

    Hourly PVGIS data will be saved to "PVGIS-1hr", 30 minute PVGIS to "PVGIS-30min", similarly 15 minute PVGIS will be saved to "PVGIS-15min"

    Parameters
    -----------
    dataset: xr.Dataset
        dataset to store with "ref_grid_id" or "gid" dimension, and "latitude:" and "longitude" coordinates
    name: str
        geogridfusion datastore name to utilize
    map_index: str
        remap index "gid" to pre-baked uniform resolution grid indexes. 
        unless your input data has spatially significant and unique indexes like a geospatial id "gid", do not turn this off.
    overwrite: bool (default = False)
        overwrite entires with identical indexes if they already exist
    """

    # open store, check if time entry length (periods) in the store yaml match the provided dataset
    if "time" in dataset.sizes and int(store.periods) != dataset.sizes["time"]:
        return ValueError(f"""
            dataset time axis (periods) do not match store periods.
            store   time entries | {store.periods}
            dataset time entries | {dataset.sizes["time"]}
        """)

    ref_coordinates = index.unform_coordinates_array(grid_points_fn=grid_points_fn)

    # remap indexes    
    search_coords = np.column_stack([dataset.latitude.values, dataset.longitude.values])
    ref_grid_index = index.coords_to_unique_index(coords=search_coords, reference_grid_coordinates=ref_coordinates) # map to new grid indexes
    # ref grid index can only return unique values but we should deal with this differently

    # overwrite spatial index with meaningful reference index
    remapped_gid_ds = dataset.assign_coords(gid=("gid", ref_grid_index))

    # select only new gids from the input dataset to save
    existing_gids = xr.open_zarr(store="dir-a").gid.values
    non_overlaping_ref_grid_index = np.setdiff1d(ref_grid_index, existing_gids)
    no_overlap_remapped_ds = remapped_gid_ds.sel(gid=non_overlaping_ref_grid_index)

    # no overwriting exisitng entries
    no_overlap_remapped_ds.to_zarr(store="dir-a", mode="a", append_dim="gid")


def display_paths() -> None:
    """
    Display user paths in a jupyter notebook environment.
    """
    with open(USER_PATHS, 'r') as f:
        data = yaml.safe_load(f)

    display_user_paths(data)

