import logging

from loguru import logger

from .wad import Wad
from . import cli, packets, utils, windows
from .application import WizWalker
from .client import Client


logger.disable("wizwalker")
logging.getLogger("pymem").setLevel(logging.FATAL)
