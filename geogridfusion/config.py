"""
Configuration file for geogridfusion package
"""

from pathlib import Path
import sys
import os

# Specify module directories
GEOGRIDFUSION = Path(__file__).parent
REPO_NAME = __name__
DATA_DIR = GEOGRIDFUSION / "data"
TEST_DIR = GEOGRIDFUSION.parent / "tests"
TEST_DATA_DIR = GEOGRIDFUSION.parent / "tests" / "data"

INDEX_PATH = Path.joinpath(GEOGRIDFUSION.parent / "spatial-index")

# this should be renamed
TREE_BINARIES_DIR = GEOGRIDFUSION.parent / "grid-points-baked/"

USER_PATHS = GEOGRIDFUSION / "user_paths" / "user_paths.yaml"
