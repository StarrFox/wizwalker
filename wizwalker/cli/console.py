import argparse
import asyncio
import re
import sys
from collections.abc import Coroutine
from typing import Optional

import cmd2
import terminaltables
from pymem import Pymem

from wizwalker import ClientHandler, CacheHandler
from wizwalker import XYZ
from wizwalker.memory import InstanceFinder


class WizWalkerConsole(cmd2.Cmd):
    def __init__(self):
        super().__init__()
        self.client_handler = ClientHandler()
        self.cache_handler = CacheHandler()
        self.instance_finders = {}

        self.prompt = "WW > "
        self.intro = "WizWalkerCLI\nUse help (?) for commands."

    @staticmethod
    def write(message: str):
        print(message)

    def run_coro(self, coro: Coroutine, timeout: Optional[int] = 10):
        try:
            result = asyncio.run(asyncio.wait_for(coro, timeout))
        except asyncio.TimeoutError:
            self.write(f"Timeout error with coro {coro.__name__}")
        except Exception as exc:
            import traceback

            traceback.print_exception(type(exc), exc, exc.__traceback__)
        else:
            return result

    def do_start(self, _):
        """
        Attach and hook to all new clients
        """
        clients = self.client_handler.get_new_clients()
        self.write(f"Attached to {len(clients)} new clients")

        for idx, client in enumerate(clients):
            self.run_coro(client.activate_hooks(), None)
            self.write(f"client-{idx}: hooked all")

    def do_exit(self, _) -> None:
        """
        Exit walker and re-write hooks
        """
        self.write("Closing client handler, hooks should be rewritten")
        self.run_coro(self.client_handler.close())

    def do_info(self, _):
        """
        Print out info from each client
        """
        for idx, client in enumerate(self.client_handler.clients):
            table_data = [["attribute", "value"]]

            hook_handler_attrs = [
                "read_current_player_base",
                "read_current_duel_base",
                "read_current_quest_base",
                "read_current_player_stat_base",
                "read_current_client_base",
                "read_current_root_window_base",
                "read_current_render_context_base",
            ]
            for attr in hook_handler_attrs:
                table_data.append(
                    [attr, hex(self.run_coro(getattr(client.hook_handler, attr)()))]
                )

            table = terminaltables.AsciiTable(table_data, f"client-{idx}")
            self.write(table.table)

    def do_position(self, _):
        """
        Print out each client's body position
        """
        for idx, client in enumerate(self.client_handler.clients):
            self.write(f"client-{idx}: {self.run_coro(client.body.position())}")

    teleport_parser = argparse.ArgumentParser()
    teleport_parser.add_argument("x", type=float, help="X to teleport to")
    teleport_parser.add_argument("y", type=float, help="Y to teleport to")
    teleport_parser.add_argument(
        "-z", "--z", type=float, help="Z to teleport to", default=None
    )
    teleport_parser.add_argument(
        "-y", "--yaw", type=float, help="Yaw to set", default=None
    )

    @cmd2.with_argparser(teleport_parser)
    def do_teleport(self, args):
        """
        Teleport to a location
        """
        for client in self.client_handler.clients:
            current_position = self.run_coro(client.body.position())
            new_position = XYZ(
                args.x, args.y, args.z if args.z is not None else current_position.z
            )
            self.run_coro(client.teleport(new_position, args.yaw))

        self.write("Teleported")

    goto_parser = argparse.ArgumentParser()
    goto_parser.add_argument("x", type=float, help="X to go to")
    goto_parser.add_argument("y", type=float, help="Y to go to")

    @cmd2.with_argparser(goto_parser)
    def do_goto(self, args):
        """
        Go to a location in the world
        """
        for client in self.client_handler.clients:
            self.run_coro(client.goto(args.x, args.y))

        self.write("Completed goto")

    getid_parser = argparse.ArgumentParser()
    getid_parser.add_argument("pattern", help="Pattern to search for")

    @cmd2.with_argparser(getid_parser)
    def do_getid(self, args):
        """
        Get templateid items that match a pattern
        """
        template_ids = self.run_coro(self.cache_handler.get_template_ids())

        regex = re.compile(args.pattern, re.IGNORECASE)
        for tid, name in template_ids.items():
            if regex.match(name):
                self.write(f"{tid=} {name=}")

    checkid_parser = argparse.ArgumentParser()
    checkid_parser.add_argument("template_id", help="Template id to check for")

    @cmd2.with_argparser(checkid_parser)
    def do_checkid(self, args):
        """
        Get the name mapped to a templateid
        """
        template_ids: dict = self.run_coro(self.cache_handler.get_template_ids())

        try:
            self.write(f"{args.template_id} => {template_ids[args.template_id]}")
        except KeyError:
            self.write(f"No item with id {args.template_id}")

    click_parser = argparse.ArgumentParser()
    click_parser.add_argument("x", type=int, help="X to click")
    click_parser.add_argument("y", type=int, help="Y to click")

    @cmd2.with_argparser(click_parser)
    def do_click(self, args):
        """
        Click a certain x, y
        """
        for client in self.client_handler.clients:
            self.run_coro(client.mouse_handler.click(args.x, args.y))

        self.write("Completed click")

    findinstances_parser = argparse.ArgumentParser()
    findinstances_parser.add_argument(
        "class_name", help="Class name to find instances of"
    )

    @cmd2.with_argparser(findinstances_parser)
    def do_findinstances(self, args):
        """
        Find instances of a class
        """
        class_name = args.class_name

        if self.instance_finders.get(class_name):
            finder = self.instance_finders[class_name]

        else:
            pm = Pymem("WizardGraphicalClient.exe")
            finder = InstanceFinder(pm, class_name)
            self.instance_finders[class_name] = finder

        instances = self.run_coro(finder.get_instances(), None)

        self.write(str(instances))


def run_cmd():
    app = WizWalkerConsole()
    sys.exit(app.cmdloop())
