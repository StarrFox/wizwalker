import asyncio
import sys
from pathlib import Path
import json

import click
from click_default_group import DefaultGroup
from loguru import logger

from wizwalker import Wad, utils, ClientHandler
from wizwalker.memory.type_tree import get_hash_map
from wizwalker.cli import run_cmd, dump_class_to_string, dump_class_to_json


logger.enable("wizwalker")
logger.remove(0)

logfile = utils.get_logs_folder() / "debug.log"
logger.add(logfile, level="DEBUG", rotation="1 week", enqueue=True)


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

    run_cmd()


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
def dump():
    """
    Class dumping commands
    """
    pass


@dump.command()
@click.argument("file_path", type=click.Path(dir_okay=False), default="dumped.txt")
def text(file_path):
    """
    Dump classes to file
    """
    file_path = Path(file_path)

    if file_path.exists():
        if not click.confirm(f"{file_path} already exists overwrite it?", default=True):
            exit(0)

    async def _dump():
        async with ClientHandler() as ch:
            clients = ch.get_new_clients()

            if not clients:
                click.echo("No open wizard101 instances to read from")
                return

            client = clients[0]

            hash_map = await get_hash_map(client)

            out = file_path.open("w+")

            with click.progressbar(
                list(hash_map.items()),
                show_pos=True,
                show_percent=False,
                item_show_func=lambda i: i[0][:40] if i else i,
                show_eta=False,
            ) as items:
                for name, node in items:
                    out.write(await dump_class_to_string(name, node))
                    out.write("\n")

    asyncio.run(_dump())


@dump.command(name="json")
@click.argument("file_path", type=click.Path(dir_okay=False), default="dumped.json")
@click.option("--indent", default=4, show_default=True, help="indent in json")
def json_(file_path, indent):
    """
    Dump classes to file
    """
    file_path = Path(file_path)

    if file_path.exists():
        if not click.confirm(f"{file_path} already exists overwrite it?", default=True):
            exit(0)

    async def _dump():
        async with ClientHandler() as ch:
            clients = ch.get_new_clients()

            if not clients:
                click.echo("No open wizard101 instances to read from")
                return

            client = clients[0]

            hash_map = await get_hash_map(client)

            res = {}

            with click.progressbar(
                list(hash_map.items()),
                show_pos=True,
                show_percent=False,
                item_show_func=lambda i: i[0][:40] if i else i,
                show_eta=False,
            ) as items:
                for name, node in items:
                    res.update(await dump_class_to_json(name, node))

            json.dump(res, file_path.open("w+"), indent=indent)

    asyncio.run(_dump())


@dump.command()
@click.argument("file_one", type=click.Path(dir_okay=False, exists=True))
@click.argument("file_two", type=click.Path(dir_okay=False, exists=True))
def compare(file_one, file_two):
    """
    Compare two json dumps
    """
    file_one = Path(file_one)
    file_two = Path(file_two)

    loaded_file_one = json.load(file_one.open())
    loaded_file_two = json.load(file_two.open())

    for class_name in loaded_file_two.keys():
        if class_name not in loaded_file_one.keys():
            click.echo(f"New class {class_name}")

    for class_name in loaded_file_one.keys():
        # classes without properties
        if not loaded_file_one[class_name].get("properties"):
            continue

        old_props = loaded_file_one[class_name]["properties"]
        new_props = loaded_file_two[class_name]["properties"]

        for prop in new_props.keys():
            if prop not in old_props.keys():
                click.echo(f"New property {prop} on {class_name}")

            elif (new_offset := new_props[prop]["offset"]) != old_props[prop]["offset"]:
                click.echo(
                    f"New offset {new_offset} on property {prop} on {class_name}"
                )

        for prop in old_props.keys():
            if prop not in new_props.keys():
                click.echo(f"Deleted property {prop} on {class_name}")


@main.group()
def wad():
    """
    Wad manipulation commands
    """
    pass


# # TODO: finish
# @wad.command()
# def archive():
#     """
#     Create a wad from a directory
#     """
#     click.echo("Not implimented")


@wad.command(short_help="Unarchive a wad into a directory")
@click.argument("input_wad", type=str)
@click.argument("output_dir", type=click.Path(file_okay=False), default=".")
def unarchive(input_wad, output_dir):
    """
    Unarchive a wad into a directory

    input_wad automatically fills in the rest of the path so you only need the name; i.e "root"
    output_dir defaults to the current directory
    """
    maybe_path = Path(input_wad)

    maybe_path.suffix = ".wad"

    if maybe_path.exists() and maybe_path.is_file():
        wad_ = Wad(maybe_path)

    else:
        wad_ = Wad.from_game_data(input_wad)

    path = Path(output_dir)

    if not path.exists():
        if click.confirm(f"{path} does not exsist; create it?", default=True):
            path.mkdir(exist_ok=True)
        else:
            exit(0)

    click.echo("Unarchiving...")

    import time

    start = time.perf_counter()
    asyncio.run(wad_.unarchive(path))
    end = time.perf_counter()

    click.echo(
        f"Unarchived {len(wad_._file_map.keys())} files in {int(end - start)} seconds"
    )


@wad.command(short_help="Extract a single file from a wad")
@click.argument("input_wad", type=str)
@click.argument("file_name")
def extract(input_wad, file_name):
    """
    Extract a single file from a wad

    input_wad automatically fills in the rest of the path so you only need the name; i.e "root"
    """
    maybe_path = Path(input_wad)

    maybe_path.suffix = ".wad"

    if maybe_path.exists() and maybe_path.is_file():
        wad_ = Wad(maybe_path)

    else:
        wad_ = Wad.from_game_data(input_wad)

    async def _extract_file():
        try:
            file_data = await wad_.get_file(file_name)
        except ValueError:
            click.echo(f"No file named {file_name} found.")
        else:
            if not file_data:
                click.echo(
                    f"{file_name} has not yet been patched by the game; must get the game to load it"
                )
                exit(0)

            relitive_file_name = file_name.split("/")[-1]

            with open(relitive_file_name, "wb+") as fp:
                click.echo("Writing...")
                fp.write(file_data)

    asyncio.run(_extract_file())


# # TODO: finish
# @wad.command()
# def insert():
#     """
#     Insert a single file into a wad
#     """
#     click.echo("Not implimented")


if __name__ == "__main__":
    main()
