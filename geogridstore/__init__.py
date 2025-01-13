from importlib.metadata import version
import logging

from .namespace_utils import load_store_configs
from .config import *

#     modules     #
###################
from .geogridstore import * # top level functions

# should index functionality be available without the extra import (import geogridfusion.index)
from . import index 

###################

load_store_configs()

__version__ = version("geogridstore")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel("DEBUG")