import logging
from sys import platform

from wizwalker import WizWalker

logger = logging.getLogger(__name__)


def main():
    if platform != "win32":
        raise RuntimeError(f"This program is windows only, not {platform}")

    app = WizWalker()
    app.run()


if __name__ == "__main__":
    main()
