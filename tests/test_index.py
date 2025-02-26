import geogridfusion
import numpy as np
import pandas as pd
import pytest

REF_COORDS_4km = geogridfusion.index.unform_coordinates_array(resolution=4)
# this will work with resolution = '4' as well

# initialize 4km tree to the module
geogridfusion.index.get_search_tree(name="tree_4km", resolution="4")


def test_mapping_4km():
    search_coords = np.array(
        [
            [38.84514507, -102.87527778],
            [40.68317413, -105.00891744],
            [40.9416718, -106.53279772],
            [40.67504283, -107.42960328],
            [38.1384219, -106.36023717],
            [37.24595954, -105.57154995],
            [40.60236194, -105.07338283],
            [37.05220985, -106.26357842],
            [39.88593969, -108.64902031],
            [39.08215587, -105.17784537],
            [40.21242034, -104.45850212],
            [40.45644866, -107.63472267],
            [40.6334712, -103.29862351],
            [39.13510199, -103.22778341],
            [39.85160064, -103.63637327],
            [39.84651495, -103.92922397],
            [37.39560002, -102.91318493],
            [39.89283547, -107.92266061],
            [38.3012948, -105.77029205],
            [39.79345908, -107.45827889],
            [37.79113294, -108.00357174],
            [37.24284263, -103.90792405],
            [37.54555183, -104.23952525],
            [40.68591959, -106.35781757],
            [38.86731694, -105.88579877],
            [40.47775724, -105.0979982],
            [38.65337592, -103.61482998],
            [40.14164811, -106.84051338],
            [37.48793946, -105.6749957],
            [39.90716844, -103.50953251],
        ]
    )

    # this tree is initialzed to the module at the top of the file
    grid_index = geogridfusion.index.coords_to_ref_index(
        coords=search_coords, tree=geogridfusion.tree_4km
    )

    index_res = np.array(
        [
            6085385,
            6260808,
            6285766,
            6260757,
            6019332,
            5935175,
            6253727,
            5917982,
            6183109,
            6105136,
            6214677,
            6239528,
            6253764,
            6111839,
            6179777,
            6179771,
            5948819,
            6183125,
            6035877,
            6172839,
            5985719,
            5935211,
            5965653,
            6260779,
            6085320,
            6239582,
            6065642,
            6207555,
            5958896,
            6183219,
        ]
    )

    np.testing.assert_array_equal(grid_index, index_res)


# TODO: write new test
# the original test wanted to ensure that we had NO duplicate gids and the function
# "coords_to_ref_index" would raise a ValueError if there were any duplicate gids
# in the result, this has since been removed and the function no longer raises an error

# def test_mapping_duplicate_reference_index():
#     problem_coords = np.array([
#         [  38.845145, -102.87527778], # a
#         [  38.845148, -102.87527778], # b
#         [  40.9416718 , -106.53279772],
#     ])

#     # a, b will resolve to same reference grid index when mapped
#     # this test will detect that the duplicate is generated
#     with pytest.raises(ValueError, match="Duplicate reference gid created"):
#         geogridfusion.index.coords_to_ref_index(coords=problem_coords, tree=geogridfusion.tree_4km)
