import logging

from loguru import logger

from .constants import *
from .wad import Wad
from .nif import NifMap
from .errors import *
from . import utils, cli, memory
from .application import WizWalker
from .client import Client

logger.disable("wizwalker")
logging.getLogger("pymem").setLevel(logging.FATAL)
