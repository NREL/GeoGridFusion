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
import zarr
import zarr.errors

from geogridfusion import index, USER_PATHS, load_store_configs

from geogridfusion.namespace_utils import NestedNamespace
from geogridfusion.display import display_user_paths


def add_user_path(
    name: str,
    path: str,
    periods: str,
    grid_resolution: str,
    template_ds: xr.Dataset,
) -> None:
    """
    add a path that can be accessed by geogridfusion

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

    if not isinstance(template_ds, xr.Dataset):
        raise ValueError("template_ds must be an Xarray Dataset.")

    with open(USER_PATHS, "r") as user_paths:
        user_config = yaml.safe_load(user_paths) or {}

    if name not in user_config:
        user_config[name] = {}

    user_config[name].update(
        {"path": path, "periods": periods, "grid_resolution": grid_resolution}
    )

    try:
        xr.zeros_like(template_ds).to_zarr(store=path, compute=False)
    except zarr.errors.ContainsGroupError:
        raise zarr.errors.ContainsGroupError(
            f"A zarr store already exists at {path}, operation failed."
        )

    with open(USER_PATHS, "w") as user_paths:
        yaml.safe_dump(user_config, user_paths)

    # update top level namespace names defined in yaml
    load_store_configs()


def remove_user_path(
    name: str,
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

    with open(USER_PATHS, "r") as user_paths:
        user_config = yaml.safe_load(user_paths) or {}

    if name not in user_config:
        raise ValueError(f'name: "{name}" not in saved names.')

    del user_config[name]

    with open(USER_PATHS, "w") as user_paths:
        yaml.safe_dump(user_config, user_paths)


def get(
    source: NestedNamespace, sort: bool = True
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
        name of store used by geogridfusion to reference the path to your store

    group : str
        name of the group to access from your local zarr store.
        Groups are created automatically in your store when you save data using `pvdeg.store.store`.

        *From `pvdeg.store.store` docstring*
        Hourly PVGIS data will be saved to "PVGIS-1hr", 30 minute PVGIS to "PVGIS-30min", similarly 15 minute PVGIS will be saved to "PVGIS-15min"

    sort : bool
        sort by gid on load from disk. disable for potentially significant speedup on larger datasets

    Returns
    -------
    loaded_ds : xr.Dataset
        Dataset loaded as saved
        Weather data for all locations requested in an xarray.Dataset using a dask array backend. This may be larger than memory.
    """

    combined_ds = xr.open_zarr(store=source.path)

    if sort:
        return combined_ds.sortby("gid")
    return combined_ds


def _check_matching_config(new: xr.Dataset, store: NestedNamespace) -> None:
    if "time" in new.sizes and int(store.periods) != new.sizes["time"]:
        return ValueError(f"""
            from user_paths.yaml
            dataset time axis (periods) do not match store periods.
            store   time entries | {store.periods}
            dataset time entries | {new.sizes["time"]}
        """)


# TODO: add datatype check to each data_var
def _check_matching_data_vars(existing: xr.Dataset, new: xr.Dataset) -> None:
    """
    Check if the data variables in two xarray.Datasets match.

    Parameters:
    - existing: The existing xarray.Dataset.
    - new: The new xarray.Dataset.

    Raises:
    - ValueError: If the data variables do not match, with details about the differences.
    """
    existing_vars = set(existing.data_vars)
    new_vars = set(new.data_vars)

    if existing_vars != new_vars:
        missing_in_new = existing_vars - new_vars
        missing_in_existing = new_vars - existing_vars

        allowed_vars = "\n".join(
            f"    {var} {tuple(existing[var].dims)} {existing[var].dtype}"
            for var in existing.data_vars
        )

        error_message = "Data variables in the datasets do not match.\n"
        if missing_in_new:
            error_message += f"Missing Variables in the new dataset: {missing_in_new}\n"
        if missing_in_existing:
            error_message += (
                f"Extra variables in the new dataset: {missing_in_existing}\n"
            )

        error_message += (
            "Only the following data_var are allowed from the new dataset:\n"
            f"Data variables:\n{allowed_vars}"
        )

        raise ValueError(error_message)


def _check_matching_time_coord(existing: xr.Dataset, new: xr.Dataset) -> None:
    # currently we only support datasets with a time axis
    if "time" not in existing.coords:
        raise ValueError("The existing dataset does not have a 'time' coordinate.")
    if "time" not in new.coords:
        raise ValueError("The new dataset is missing the 'time' coordinate.")

    # Check if the time coordinates match
    if not existing.time.equals(new.time):
        raise ValueError(
            f"The time coordinates do not match.\n"
            f"Existing time: {existing.time.values}\n"
            f"New time: {new.time.values}"
        )


def _map_dataset_to_ref_index(
    dataset: xr.Dataset, store: NestedNamespace
) -> xr.Dataset:
    """convert existing dataset gids to meaningful reference grid index"""
    search_coords = np.column_stack([dataset.latitude.values, dataset.longitude.values])

    resolution = store.grid_resolution
    tree_name = f"tree_{resolution}km"
    tree = index.get_search_tree(name=tree_name, resolution=resolution)

    ref_grid_index = index.coords_to_ref_index(coords=search_coords, tree=tree)

    remapped_gid_ds = dataset.assign_coords(gid=("gid", ref_grid_index))

    return remapped_gid_ds


def store(
    dataset: xr.Dataset,
    store: NestedNamespace,
    map_index: bool = True,
    remove_duplicates: bool = True,
) -> None:
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
    map_index: bool
        remap index "gid" to pre-baked uniform resolution grid indexes.
        unless your input data has spatially significant and unique indexes like a geospatial id "gid", do not turn this off.
    remove_duplicates: bool
        remove duplicate points in new dataset at resolution of store provided
    """

    # check if new dataset aligns with existing
    #############################################
    # check if dataset matches yaml config
    _check_matching_config(new=dataset, store=store)

    existing_store = xr.open_zarr(store.path)

    # check if shapes and coordinate values match
    _check_matching_time_coord(existing=existing_store, new=dataset)
    _check_matching_data_vars(existing=existing_store, new=dataset)

    remapped_gid_ds = (
        _map_dataset_to_ref_index(dataset=dataset, store=store)
        if map_index
        else dataset
    )

    if remove_duplicates:
        remapped_gid_ds.groupby("gid").first()

    # save to existing dataset
    ##########################
    new_gids = np.setdiff1d(remapped_gid_ds.gid, existing_store.gid)
    cleaned_ds = remapped_gid_ds.sel({"gid": new_gids})  # downsample to only new points

    # save back to store
    #####################
    cleaned_ds.to_zarr(store=store.path, mode="a", append_dim="gid")


def display_paths() -> None:
    """
    Display user paths in a jupyter notebook environment.
    """
    with open(USER_PATHS, "r") as f:
        data = yaml.safe_load(f)

    display_user_paths(data)
