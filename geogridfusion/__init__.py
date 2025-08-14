from importlib_metadata import version
import logging

# Module Imports
from .config import (
    DATA_DIR,
    POSTGRES_EXE_PATH,
    REPO_NAME,
    GEOGRIDFUSION_DIR,
    WATCHDOG_PATH,
)

# top level namespace utilities
from .core import store_single, load_single, sources, load_many

from .startup import start
from .initdb import initdb
from .tables import initialize_tables

# 2nd tier namespace utilties
from . import queries

__version__ = version("geogridfusion")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel("DEBUG")
