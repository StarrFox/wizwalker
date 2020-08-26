import sys
import asyncio
from pathlib import Path

from wizwalker import WizWalker, utils
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


def wiz_command():
    """
    called when someone uses the "wiz" console command
    """
    try:
        login_flag = sys.argv[1]
    except IndexError:
        utils.quick_launch()
        return

    if login_flag != "--login":
        print(f"{login_flag} is not a valid flag")
        return

    try:
        username = sys.argv[2]
    except IndexError:
        print("Missing username")
        return

    try:
        password = sys.argv[3]
    except IndexError:
        print("Missing password")
        return

    utils.quick_launch()

    # speed is the name :sunglasses:
    import time
    # this probably isn't enough time for some computers
    time.sleep(7)

    handles = utils.get_all_wizard_handles()
    newest_handle = sorted(handles)[-1]

    utils.wiz_login(newest_handle, username, password)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
