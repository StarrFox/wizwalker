import asyncio

import aiofiles
from argparse import ArgumentParser
from aioconsole import AsynchronousCli

from wizwalker import Wad, utils
from wizwalker.windows.memory import MemoryHandler


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

        login_parser = ArgumentParser("login to a client")
        login_parser.add_argument("client_index", type=int)
        login_parser.add_argument("username", type=str)
        login_parser.add_argument("password", type=str)
        commands["login"] = (self.login_command, login_parser)

        hook_parser = ArgumentParser(description="Hooks into all processes")
        hook_parser.add_argument("--target_hook", type=str)
        commands["hook"] = (self.hook_command, hook_parser)

        player_parser = ArgumentParser(description="Output various player information")
        commands["player"] = (self.player_command, player_parser)

        backpack_parser = ArgumentParser(description="Output various backpack information")
        commands["backpack"] = (self.backpack_command, backpack_parser)

        quest_parser = ArgumentParser(description="Output various quest information")
        commands["quest"] = (self.quest_command, quest_parser)

        packet_parser = ArgumentParser(description="Output packet socket and buffer")
        commands["packet"] = (self.packet_command, packet_parser)

        watch_parser = ArgumentParser(description="Watch packets for information")
        commands["watch"] = (self.watch_command, watch_parser)

        zone_parser = ArgumentParser(description="Show current zone for each client")
        commands["zone"] = (self.zone_command, zone_parser)

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
        teleport_parser.add_argument("--yaw", type=float)
        commands["teleport"] = (self.teleport_command, teleport_parser)

        return commands

    async def attach_command(self, _, writer):
        self.walker.get_clients()
        writer.write(f"Attached to {len(self.walker.clients)} clients\n")

    async def login_command(self, _, writer, client_index, username, password):
        try:
            self.walker.clients[client_index].login(username, password)
        except KeyError:
            writer.write(
                f"No client with index {client_index}, you only have {len(self.walker.clients)} clients\n"
            )
        else:
            writer.write(f"client-{client_index}: Logged in\n")

    async def hook_command(self, _, writer, target_hook: str = None):
        hook = False
        if target_hook is not None:
            md_dir = dir(MemoryHandler)
            try:
                hook_index = md_dir.index("hook_" + target_hook.replace(" ", "_"))
            except ValueError:
                writer.write(f"Hook {target_hook} not found\n")
                return
            else:
                hook = md_dir[hook_index]

        for idx, client in enumerate(self.walker.clients):
            if hook:
                await getattr(client.memory, hook)()
                writer.write(f"client-{idx}: hooked {target_hook}\n")
            else:
                await client.memory.hook_all()
                writer.write(f"client-{idx}: hooked all\n")

    async def player_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(
                f"client-{idx}: xyz={await client.xyz()} "
                f"health={await client.health()} "
                f"mana={await client.mana()} "
                f"potions={await client.potions()} "
                f"gold={await client.gold()} "
                f"yaw={await client.yaw()} "
                f"player_base={hex(await client.memory.read_player_base())} "
                f"player_stat_base={hex(await client.memory.read_player_stat_base())}\n"
            )

    async def backpack_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(
                f"client-{idx}: used_space={await client.backpack_space_used()} "
                f"total_space={await client.backpack_space_total()} "
                f"backpack_struct_addr={hex(await client.memory.read_backpack_stat_base())}\n"
            )

    async def quest_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(f"client-{idx}: quest_xyz={await client.quest_xyz()}\n")

    async def packet_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(
                f"client-{idx}: socket={await client.memory.read_packet_socket_discriptor()} "
                f"packet_buffer={await client.memory.read_packet_buffer()}\n"
            )

    async def watch_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            client.watch_packets()
            writer.write(f"client-{idx}: watching packets\n")

    async def zone_command(self, _, writer):
        for idx, client in enumerate(self.walker.clients):
            writer.write(f"client-{idx}: current zone={client.current_zone}\n")

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

    async def teleport_command(self, _, writer, x, y, z=None, yaw=None):
        for client in self.walker.clients:
            await client.teleport(
                x=x,
                y=y,
                z=z,
                yaw=yaw
            )

        writer.write("Teleported\n")
