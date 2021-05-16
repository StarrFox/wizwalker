import logging

from loguru import logger

from .constants import *
from .errors import *
from .utils import XYZ, Rectangle
from . import cli, combat, memory, utils
from .file_readers import CacheHandler, NifMap, Wad
from .mouse_handler import MouseHandler
from .client import Client
from .client_handler import ClientHandler
from .application import WizWalker
from .hotkey import *

logger.disable("wizwalker")
logging.getLogger("pymem").setLevel(logging.FATAL)
