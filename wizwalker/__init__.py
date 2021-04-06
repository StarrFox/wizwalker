import logging

from loguru import logger

# TODO: remove windows folder and expose memory
from .constants import *
from .wad import Wad
from .nif import NifMap
from .errors import *
from . import packets, utils, windows, cli
from .application import WizWalker
from .client import Client

logger.disable("wizwalker")
logging.getLogger("pymem").setLevel(logging.FATAL)
