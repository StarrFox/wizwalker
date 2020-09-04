import asyncio
import sys

from loguru import logger

from wizwalker import WizWalker, utils
from wizwalker.cli import WizWalkerConsole

logger.enable("wizwalker")
logger.remove(0)
logger.add("wizwalker_debug.log", level="DEBUG", rotation="10 MB")


async def run_console():
    walker = WizWalker()
    console = WizWalkerConsole(walker)
    await console.interact()


def main():
    if sys.platform != "win32":
        raise RuntimeError(f"This program is windows only, not {sys.platform}")

    asyncio.run(run_console())

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


if __name__ == "__main__":
    main()
