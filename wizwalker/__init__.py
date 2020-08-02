import logging

from . import packets, utils, windows, cli
from .client import Client
from .application import WizWalker

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s",
    level=logging.INFO,
    # Todo: remove
    filename="debug.log",
    filemode='w+'
)

logging.getLogger(__name__)
logging.getLogger("pymem").setLevel(logging.ERROR)
