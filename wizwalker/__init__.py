import logging

from loguru import logger

from .wad import Wad
from . import cli, packets, utils, windows
from .application import WizWalker
from .client import Client


# logging.basicConfig(
#     format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s",
#     level=logging.DEBUG,
#     # Todo: remove on release
#     filename="wizwalker_debug.log",
#     filemode="w+",
# )

logger.remove(0)
logger.add("wizwalker_debug.log", level="DEBUG", rotation="20 MB")

logging.getLogger("pymem").setLevel(logging.FATAL)
