""" 
Configuration file for geogridstore package
"""

from pathlib import Path
import sys
import os

# Specify module directories
GEOGRIDSTORE_DIR = Path(__file__).parent
REPO_NAME = __name__
DATA_DIR = GEOGRIDSTORE_DIR / "data"
TEST_DIR = GEOGRIDSTORE_DIR.parent / "tests"
TEST_DATA_DIR = GEOGRIDSTORE_DIR.parent / "tests" / "data"

INDEX_PATH = Path.joinpath(GEOGRIDSTORE_DIR.parent / "spatial-index") 

# this should be renamed
TREE_BINARIES_DIR = GEOGRIDSTORE_DIR.parent / "grid-points-baked"

USER_PATHS = GEOGRIDSTORE_DIR / "user_paths" / "user_paths.yaml"