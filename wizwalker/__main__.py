import asyncio
import sys

import click
from click_default_group import DefaultGroup
from loguru import logger

from wizwalker import WizWalker, utils
from wizwalker.cli import WizWalkerConsole

logger.enable("wizwalker")
logger.remove(0)
logger.add("wizwalker_debug.log", level="DEBUG", rotation="10 MB")


@click.group(
    help="Wizwalker cli", cls=DefaultGroup, default="cli", default_if_no_args=True,
)
def main():
    pass
    # app = WizWalker()
    #
    # # close WizWalker when app is closed
    # atexit.register(app.close)
    #
    # app.run()


@main.command(help="Start a cli instance")
def cli():
    if sys.platform != "win32":
        raise RuntimeError(f"This program is windows only, not {sys.platform}")

    async def _run_console():
        walker = WizWalker()
        console = WizWalkerConsole(walker)
        await console.interact()

    asyncio.run(_run_console())


@main.command(help="Start (a/some) wizard101 instance(s)")
@click.option(
    "--instances", default=1, show_default=True, help="Number of instances to start"
)
@click.argument("logins", nargs=-1)
def start_wiz(instances, logins):
    """
    called when someone uses the "wiz" console command
    """
    if instances != len(logins) and instances != 1:
        click.echo("Not enough or too many logins for the number of instances")
        exit(1)

    asyncio.run(utils.start_instances_with_login(instances, logins))

    # utils.quick_launch()
    #
    # # speed is the name :sunglasses:
    # import time
    #
    # # this probably isn't enough time for some computers
    # time.sleep(7)
    #
    # handles = utils.get_all_wizard_handles()
    # newest_handle = sorted(handles)[-1]
    #
    # utils.wiz_login(newest_handle, username, password)


if __name__ == "__main__":
    main()
