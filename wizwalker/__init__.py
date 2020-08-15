import logging

from . import packets, utils, windows, cli
from .client import Client
from .application import WizWalker
from .wad import Wad

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s",
    level=logging.DEBUG,
    # Todo: remove on release
    filename="wizwalker_debug.log",
    filemode="w+",
)

logging.getLogger(__name__)
logging.getLogger("pymem").setLevel(logging.FATAL)
