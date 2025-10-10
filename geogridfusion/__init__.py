from importlib_metadata import version
import logging

# Module Imports
from .config import (
    DATA_DIR,
    REPO_NAME,
    GEOGRIDFUSION_DIR,
)

# top level namespace utilities
from .core import geogridfusionStore as geogridfusionStore
from .container_runner import run_container

from .tables import initialize_tables

# 2nd tier namespace utilties
from . import queries

__version__ = version("geogridfusion")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel("DEBUG")
