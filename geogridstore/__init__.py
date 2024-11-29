from importlib.metadata import version
import logging

from .config import *

#     modules     #
###################
from .geogridstore import *


###################

__version__ = version("geogridstore")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel("DEBUG")