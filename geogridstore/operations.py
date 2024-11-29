import xarray as xr
import numpy as np
from shapely.geometry import polygon

# def is_disjoint(a : xr.Dataset, b: xr.Dataset) -> bool:
#     """
#     Determine if two sets are have no overlap.

#     $A \cap B = \empty$
#     """
#     raise NotImplementedError


# def intersection(a : xr.Dataset, b: xr.Dataset) -> np.ndarray:
#     """
#     Get the coordinates overlapping points of sets A and B.

#     Returns
#     -------
#     coordinates: np.ndarray
#         long numpy array [2, entries] where row 0 is latitude, row 1 is longitude.
#     """
#     raise NotImplementedError

# def compliment(a : xr.Dataset, b: xr.Dataset) -> np.ndarray:
#     """
#     Get elements in not in a that exist in B
#     """
#     raise NotImplementedError

# do we care? about any of the above


def grid_from_polygon(poly : polygon, resolution : str, reference_coords : tuple) -> any:
    """
    Create a grid of datapoints from a `shapely.geometry.polygon`, at a fixed gridded resolution (2km, 4km, 100m, etc.), provided with a reference coordiante to start.
    This grid will be normal, with points generated horizontally (east, west) and vertically (north, south) from the reference coords at the resolution specified.
    """

    # https://stackoverflow.com/questions/74054997/create-point-grid-inside-a-shapefile-using-python
    # gdf_grid = gpd.GeoDataFrame(
    #     geometry=[
    #         shapely.geometry.Point(x, y)
    #         for x in np.arange(a, c, STEP)
    #         for y in np.arange(b, d, STEP)
    #     ],
    #     crs=crs,
    # ).to_crs(gdf.crs)

    raise NotImplementedError

def polygon_from_grid(a : xr.Dataset) -> polygon:
    """
    Extract a polygon from a dataset.
    """
    raise NotImplementedError

def missing_from_polygon(grid : xr.Dataset, poly : polygon ) -> np.ndarray:
    """
    Compare a dataset to a polygon, see if any 
    """


# need methods to compare polygons directly (this exists in shapely already)
# need methods to check polygons against datasets, this can be done by converting to polygons and comparing