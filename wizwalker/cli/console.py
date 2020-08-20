import asyncio

import aiofiles
from argparse import ArgumentParser
from aioconsole import AsynchronousCli

from wizwalker import Wad, utils


class WizWalkerConsole(AsynchronousCli):
    def __init__(self, walker, **kwargs):
        commands = self.get_commands()
        super().__init__(commands, **kwargs)

        self.walker = walker

    def get_default_banner(self):
        msg = "WizWalker cli,\n"
        msg += "send list for the command list"
        return msg

    def get_commands(self):
        commands = {}

        attach_parser = ArgumentParser(description="Attach to currently running wiz instances")
        commands["attach"] = (self.attach_command, attach_parser)

        inject_parser = ArgumentParser(description="Inject hooks into all processes")
        commands["inject"] = (self.inject_command, inject_parser)

        player_parser = ArgumentParser(description="Output various player information")
        commands["player"] = (self.player_command, player_parser)

        quest_parser = ArgumentParser(description="Output various quest information")
        commands["quest"] = (self.quest_command, quest_parser)

        wad_parser = ArgumentParser(description="Extract a wad file")
        wad_parser.add_argument("wad_name", type=str)
        wad_parser.add_argument("file_name", type=str)
        wad_parser.add_argument("--output_name", type=str)
        commands["wad"] = (self.wad_command, wad_parser)

        cache_parser = ArgumentParser(description="Cache Wad data")
        commands["cache"] = (self.cache_command, cache_parser)

        wiz_parser = ArgumentParser(description="Start a Wizard101 instance")
        commands["wiz"] = (self.wiz_command, wiz_parser)

        send_parser = ArgumentParser(description="Send a key to all clients")
        send_parser.add_argument("key", type=str)
        send_parser.add_argument("seconds", type=float)
        commands["send"] = (self.send_command, send_parser)

        teleport_parser = ArgumentParser(description="Teleport to a certain x,y,z")
        teleport_parser.add_argument("x", type=float)
        teleport_parser.add_argument("y", type=float)
        teleport_parser.add_argument("--z", type=float)
        commands["teleport"] = (self.teleport_command, teleport_parser)

        return commands

    async def attach_command(self, _, writer):
        self.walker.get_clients()
        writer.write(f"Attached to {len(self.walker.clients)} clients\n")

    async def inject_command(self, _, writer):
        for client in self.walker.clients:
            await client.memory.inject()

        writer.write("Injected\n")

    async def player_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(
                f"client-{idx}: xyz={await client.xyz()} "
                f"health={await client.health()} "
                f"mana={await client.mana()} "
                f"potions={await client.potions()} "
                f"gold={await client.gold()} "
                f"player_base={hex(await client.memory.read_player_base())} "
                f"player_stat_base={hex(await client.memory.read_player_stat_base())}\n"
            )

    async def quest_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(f"client-{idx}: quest_xyz={await client.quest_xyz()}\n")

    @staticmethod
    async def wad_command(_, writer, wad_name, file_name, output_name=None):
        wad = Wad(wad_name)
        file_data = await wad.get_file(file_name)

        if output_name is None:
            output_name = file_name

        async with aiofiles.open(output_name, "wb+") as fp:
            await fp.write(file_data)

        writer.write(f"Extracted {wad_name=}, {file_name=}\n")

    async def cache_command(self, _, writer):
        await self.walker.cache_data()
        writer.write("Cached\n")

    @staticmethod
    async def wiz_command(_, writer):
        utils.quick_launch()
        writer.write("Launched wizard101 instance\n")

    async def send_command(self, _, writer, key, seconds):
        if len(key) == 1:
            key = key.upper()

        for client in self.walker.clients:
            asyncio.create_task(client.keyboard.send_key(key, seconds))

        writer.write("Started\n")

    async def teleport_command(self, _, writer, x, y, z=None):
        for client in self.walker.clients:
            await client.teleport(
                x=x,
                y=y,
                z=z,
            )

        writer.write("Teleported\n")
