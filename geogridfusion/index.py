"""
Functions to manage reference ids and mappings
"""

import numpy as np
from pyproj import Transformer
import sys
import os

from scipy.spatial import cKDTree

import geogridfusion

def unform_coordinates_array(resolution: str) ->np.ndarray:
    """
    grab-prebaked grid coordinates array
    """

    grid_points_fn = f"{resolution}km-points.npz"

    with open(os.path.join(geogridfusion.TREE_BINARIES_DIR, grid_points_fn), "rb") as fp:
        npz_file = np.load(fp)
        grid_points = npz_file["arr_0"]  # use numpy default key


    module = sys.modules["geogridfusion"]
    setattr(module, grid_points_fn.split(".")[0], grid_points)

    return grid_points

def get_search_tree(name: str, resolution: str) -> cKDTree:
    """
    name of tree
    ex: tree_4km, tree_10km
    """

    module = sys.modules["geogridfusion"]

    tree = getattr(module, name)

    if tree is None:
        reference_grid_coordinates = unform_coordinates_array(resolution=resolution)
        tree = cKDTree(data=reference_grid_coordinates)

        setattr(module, name, tree)

    return tree


# WARNING: can produce duplicate indexes
def coords_to_ref_index(
    coords: np.ndarray, 
    tree: cKDTree,
    ) -> np.ndarray:
    """
    Maps points to their nearest unique grid index at a specific resolution as specified by "grid_points_fn".
    This function handles file IO and rebuilds the spatial KDTree for each call, for efficiency minimize usage to avoid repeated work.

    Parameters
    ----------
    coords: np.ndarray
        tall numpy array of [[lat, lon], [lat, lon]]
    reference_grid_coordinates: np.ndarray
        tall numpy array of coordinates loaded from prebaked grids of uniform density
    grid_points_fn: str
        name of file storing compressed numpy array.
        THIS WILL CHANGE DURING DEVELOPMENT
    Returns
    --------
    indexes: np.ndarray
        1 dimensional numpy array of nearest indexes in the precomputed grid coresponding to each entry in the coordinates array input
    """

    # this is probably cartesian distance in the 2d plane of the tree
    # not meaningful for coordinates on earth (we need spherical distance)
    # can compute this using haversine distance indexing into the tree
    distance, idx =  tree.query(coords)

    # duplicates are okay here
    # we need to be aware of this though
    return idx
   

def degrees_to_meters(lat_deg, lon_deg, latitude):
    """
    Convert degrees of latitude and longitude to meters.
    
    Parameters:
        lat_deg (float): Change in degrees of latitude.
        lon_deg (float): Change in degrees of longitude.
        latitude (float): Latitude of the location in degrees.
    
    Returns:
        (lat_meters, lon_meters): Tuple of latitude and longitude distances in meters.
    """
    # Earth's radius-based constants
    meters_per_degree_lat = 111320  # Meters per degree of latitude
    meters_per_degree_lon = 111320 * np.cos(np.radians(latitude))  # Adjust for latitude
    
    # Convert degrees to meters
    lat_meters = lat_deg * meters_per_degree_lat
    lon_meters = lon_deg * meters_per_degree_lon
    
    return lat_meters, lon_meters

    
# review this heaviliy
def generate_spherical_grid_fixed(distance_km, radius=6371):
    """
    Generate points on a sphere with approximately uniform spacing.
    
    Args:
        distance_km (float): Desired spacing between points in kilometers.
        radius (float): Radius of the sphere (default is Earth's radius in km).
    
    Returns:
        points (ndarray): Array of (latitude, longitude) points in degrees.
    """
    # Convert distance to radians
    distance_rad = distance_km / radius

    # Generate latitudes
    latitudes = np.arange(-np.pi / 2, np.pi / 2 + distance_rad, distance_rad)
    
    points = []
    for lat in latitudes:
        # Calculate the number of longitudes at this latitude
        circumference = 2 * np.pi * radius * np.cos(lat)  # Circumference of latitude circle
        num_points = max(1, int(circumference / distance_km))  # Number of points in longitude
        longitudes = np.linspace(0, 2 * np.pi, num_points, endpoint=False)  # Evenly spaced

        # Add points for this latitude
        lat_array = np.full_like(longitudes, lat)  # Same latitude for all points
        points.append(np.stack((lat_array, longitudes), axis=-1))

    # Concatenate and convert to degrees
    points = np.vstack(points)  # Combine all latitude-longitude arrays
    points[:, 0] = np.degrees(points[:, 0])  # Convert latitudes to degrees
    points[:, 1] = np.degrees(points[:, 1])  # Convert longitudes to degrees

    # normalize to (-180, 180) degrees longitude
    points[:, 1] = ((points[:, 1] + 180) % 360) - 180

    return points