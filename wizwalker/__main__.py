import sys
from pathlib import Path

from wizwalker import WizWalker
from wizwalker.cli import WizWalkerCli

# https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
if getattr(sys, "frozen", False):
    root = Path(sys.executable).parent
else:
    root = Path(__file__).parent.parent

cache_dir = root / "cache"
if not cache_dir.exists():
    cache_dir.mkdir()


def main():
    if sys.platform != "win32":
        raise RuntimeError(f"This program is windows only, not {sys.platform}")

    walker = WizWalker()
    cli = WizWalkerCli(walker)
    cli.run()

    # app = WizWalker()
    #
    # # close WizWalker when app is closed
    # atexit.register(app.close)
    #
    # app.run()


if __name__ == "__main__":
    main()
