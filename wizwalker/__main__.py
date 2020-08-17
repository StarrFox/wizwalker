import sys
import asyncio
from pathlib import Path

from wizwalker import WizWalker
from wizwalker.cli import WizWalkerConsole

# https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
if getattr(sys, "frozen", False):
    root = Path(sys.executable).parent
else:
    root = Path(__file__).parent.parent

cache_dir = root / "cache"
if not cache_dir.exists():
    cache_dir.mkdir()


async def main():
    if sys.platform != "win32":
        raise RuntimeError(f"This program is windows only, not {sys.platform}")

    walker = WizWalker()
    console = WizWalkerConsole(walker)
    await console.interact()
    await walker.close()

    # app = WizWalker()
    #
    # # close WizWalker when app is closed
    # atexit.register(app.close)
    #
    # app.run()


if __name__ == "__main__":
    asyncio.run(main())
