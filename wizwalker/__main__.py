import asyncio
import sys
from pathlib import Path

import click
import aiofiles
from click_default_group import DefaultGroup
from loguru import logger

from wizwalker import WizWalker, utils, Wad
from wizwalker.cli import WizWalkerConsole

logger.enable("wizwalker")
logger.remove(0)
logger.add("wizwalker_debug.log", level="DEBUG", rotation="10 MB")


@click.group(cls=DefaultGroup, default="cli", default_if_no_args=True)
def main():
    """
    Wizwalker cli
    """
    pass
    # app = WizWalker()
    #
    # # close WizWalker when app is closed
    # atexit.register(app.close)
    #
    # app.run()


@main.command()
def cli():
    """
    Start a cli instance
    """
    if sys.platform != "win32":
        raise RuntimeError(f"This program is windows only, not {sys.platform}")

    async def _run_console():
        walker = WizWalker()
        console = WizWalkerConsole(walker)
        await console.interact()

    asyncio.run(_run_console())


@main.command()
@click.option(
    "--instances", default=1, show_default=True, help="Number of instances to start"
)
@click.argument("logins", nargs=-1)
def start_wiz(instances, logins):
    """
    Start multiple wizard101 instances and optionally login to them
    """
    if instances != len(logins) and instances != 1:
        click.echo("Not enough or too many logins for the number of instances")
        exit(1)

    asyncio.run(utils.start_instances_with_login(instances, logins))


@main.group()
def wad():
    """
    Wad manipulation commands
    """
    pass


# TODO: finish
@wad.command()
def archive():
    """
    Create a wad from a directory
    """
    click.echo("Not implimented")


@wad.command(short_help="Unarchive a wad into a directory")
@click.argument("input_wad", type=str)
@click.argument(
    "output_dir", type=click.Path(exists=True, file_okay=False), default="."
)
def unarchive(input_wad, output_dir):
    """
    Unarchive a wad into a directory

    input_wad automatically fills in the rest of the path so you only need the name; i.e "root"
    output_dir defaults to the current directory
    """
    wad_file = Wad(input_wad)
    path = Path(output_dir)

    if not path.exists():
        if click.confirm(f"{path} does not exsist; create it?", default=True):
            path.mkdir()
        else:
            exit(0)

    async def _unarchive_wad():
        # we don't use wad_file.unarchive so we can have this nice progress bar
        with click.progressbar(
            await wad_file.names(),
            show_pos=True,
            item_show_func=lambda i: i.split("/")[-1] if i else i,
            show_eta=False,
        ) as names:
            for file_name in names:
                dirs = file_name.split("/")
                # not a base level file
                if len(dirs) != 1:
                    current = path
                    for next_dir in dirs[:-1]:
                        current = current / next_dir
                        if not current.exists():
                            current.mkdir()

                file_path = path / file_name
                file_data = await wad_file.get_file(file_name)

                async with aiofiles.open(file_path, "wb") as fp:
                    await fp.write(file_data)

    asyncio.run(_unarchive_wad())


@wad.command(short_help="Extract a single file from a wad")
@click.argument("input_wad", type=str)
@click.argument("file_name")
def extract(input_wad, file_name):
    """
    Extract a single file from a wad

    input_wad automatically fills in the rest of the path so you only need the name; i.e "root"
    """
    wad_file = Wad(input_wad)

    async def _extract_file():
        try:
            file_data = await wad_file.get_file(file_name)
        except ValueError:
            click.echo(f"No file named {file_name} found.")
            exit(0)

        relitive_file_name = file_name.split("/")[-1]

        async with aiofiles.open(relitive_file_name, "wb+") as fp:
            click.echo("Writing...")
            await fp.write(file_data)

    asyncio.run(_extract_file())


# TODO: finish
@wad.command()
def insert():
    """
    Insert a single file into a wad
    """
    click.echo("Not implimented")


if __name__ == "__main__":
    main()
