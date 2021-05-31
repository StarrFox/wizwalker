import asyncio
import re
import sys
import threading
from typing import Any, Coroutine, Union

import aioconsole
import terminaltables
from aiomonitor import Monitor, cli, start_monitor
from aiomonitor.utils import close_server, console_proxy
from pymem import Pymem

from wizwalker import XYZ
from wizwalker.memory import InstanceFinder


def init_console_server(host: str, port: int, _locals, loop):
    def _factory(streams=None) -> aioconsole.AsynchronousConsole:
        return NoBannerConsole(locals=_locals, streams=streams, loop=loop)

    coro = aioconsole.start_interactive_server(
        host=host, port=port, factory=_factory, loop=loop
    )
    console_future = asyncio.run_coroutine_threadsafe(coro, loop=loop)
    return console_future


class NoBannerConsole(aioconsole.AsynchronousConsole):
    async def _interact(self, banner=None):
        # Get ps1 and ps2
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        # Run loop
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = await self.raw_input(prompt)
                except EOFError:
                    self.write("\n")
                    await self.flush()
                    break
                else:
                    more = await self.push(line)
            except asyncio.CancelledError:
                self.write("\nKeyboardInterrupt\n")
                await self.flush()
                self.resetbuffer()
                more = 0


class WizWalkerConsole(Monitor):
    intro = "WizWalkerCLI\n{tasknum} task{s} running. Use help (?) for commands.\n"
    prompt = "WW > "

    def write(self, message: str):
        self._sout.write(message + "\n")
        self._sout.flush()

    def get_local(self, name: str) -> Any:
        res = self._locals.get(name)
        if res is None:
            raise ValueError(f"{name} not in locals")

        return res

    def run_coro(self, coro: Coroutine, timeout: Union[int, None] = 10):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)

        try:
            result = future.result(timeout)
        except asyncio.TimeoutError:
            self.write(f"Timeout error with coro {coro.__name__}")
            future.cancel()
        except Exception as exc:
            import traceback

            traceback.print_exception(type(exc), exc, exc.__traceback__)
        else:
            return result

    def do_console(self):
        """Switch to async Python REPL"""
        if not self._console_enabled:
            self.write("Python console disabled for this session")
            return

        fut = init_console_server(
            self._host, self._console_port, self._locals, self._loop
        )
        server = fut.result(timeout=3)
        try:
            console_proxy(self._sin, self._sout, self._host, self._console_port)
        finally:
            coro = close_server(server)
            close_fut = asyncio.run_coroutine_threadsafe(coro, loop=self._loop)
            close_fut.result(timeout=15)

    def do_start(self):
        """Attach and hook to all clients"""
        walker = self.get_local("walker")
        walker.get_new_clients()
        self.write(f"Attached to {len(walker.clients)} clients")
        for idx, client in enumerate(walker.clients):
            self.run_coro(client.activate_hooks(), None)
            self.write(f"client-{idx}: hooked all")

    def do_exit(self) -> None:
        """exit walker and re-write hooks"""
        walker = self.get_local("walker")
        self.write("Closing wizwalker, hooks should be rewritten")
        self.run_coro(walker.close())

    def do_info(self):
        """Print out info from each client"""
        walker = self.get_local("walker")

        for idx, client in enumerate(walker.clients):
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
                    [attr, self.run_coro(getattr(client.hook_handler, attr)())]
                )

            table = terminaltables.AsciiTable(table_data, f"client-{idx}")
            self.write(table.table)

    def do_position(self):
        """Print out each client's body position"""
        walker = self.get_local("walker")

        for idx, client in enumerate(walker.clients):
            self.write(f"client-{idx}: {self.run_coro(client.body.position())}")

    def do_cache(self):
        """Cache data"""
        walker = self.get_local("walker")
        self.run_coro(walker.cache())
        self.write("Cached data")

    def do_teleport(self, x: float, y: float, z: float = None, yaw: float = None):
        """Teleport to a location

        x y z and yaw are all optional
        """
        walker = self.get_local("walker")
        for client in walker.clients:
            current_position = self.run_coro(client.body.position())
            new_position = XYZ(x, y, z or current_position.z)
            self.run_coro(client.teleport(new_position, yaw))

        self.write("Teleported")

    def do_goto(self, x: float, y: float):
        """Go to a location in the world"""
        walker = self.get_local("walker")
        for client in walker.clients:
            self.run_coro(client.goto(x, y))

        self.write("Completed goto")

    def do_getid(self, pattern: str):
        """Get templateid items that match a pattern

        cache command must be run first
        """
        walker = self.get_local("walker")
        client = walker.clients[0]
        template_ids: dict = self.run_coro(client.get_template_ids())

        regex = re.compile(pattern, re.IGNORECASE)
        for tid, name in template_ids.items():
            if regex.match(name):
                self.write(f"{tid=} {name=}")

    def do_checkid(self, tid: str):
        """Get the name mapped to a templateid

        cache command must be run first
        """
        walker = self.get_local("walker")
        client = walker.clients[0]
        template_ids: dict = self.run_coro(client.get_template_ids())

        try:
            self.write(f"{tid} => {template_ids[tid]}")
        except KeyError:
            self.write(f"No item with id {tid}")

    def do_click(self, x: int, y: int):
        """Click a certain x, y"""
        walker = self.get_local("walker")
        for client in walker.clients:
            self.run_coro(client.click(x, y))

        self.write("Completed click")

    def do_findinstances(self, class_name: str):
        """Find instances of a class"""
        pm = Pymem("WizardGraphicalClient.exe")
        finder = InstanceFinder(pm, class_name)
        instances = self.run_coro(finder.get_instances(), None)

        self.write(str(instances))
        
    def do_owo(self):
        self.write("⠀⠀⠀⣠⣾⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣷⣄⠀\n⠀⠀⠀⣿⣿⡇⠀⠀⢸⣿⢰⣿⡆⠀⣾⣿⡆⠀⣾⣷⠀⣿⣿⡇⠀⠀⢸⣿⣿⠀\n⠀⠀⠀⣿⣿⡇⠀⠀⢸⣿⠘⣿⣿⣤⣿⣿⣿⣤⣿⡇⠀⢻⣿⡇⠀⠀⢸⣿⣿⠀\n⠀⠀⠀⣿⣿⡇⠀⠀⢸⡿⠀⢹⣿⣿⣿⣿⣿⣿⣿⠁⠀⢸⣿⣇⠀⠀⢸⣿⣿⠀\n⠀⠀⠀⠙⢿⣷⣶⣶⡿⠁⠀⠈⣿⣿⠟⠀⣿⣿⠇⠀⠀⠈⠻⣿⣿⣿⣿⡿⠋")


def test_monitor():
    cli.monitor_client(cli.MONITOR_HOST, cli.MONITOR_PORT)


# TODO: replace app with walker when WizWalker has run loop
def start_console(loop=None, locals=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    def app():
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Closing wizwalker; hooks should be rewritten")
            loop.run_until_complete(locals["walker"].close())

            tasks = asyncio.Task.all_tasks(loop)
            for task in tasks:
                if not task.done():
                    task.cancel()

            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    def run_monitor():
        cli.monitor_client(cli.MONITOR_HOST, cli.MONITOR_PORT)

    monitor_thread = threading.Thread(target=run_monitor, daemon=True)
    monitor_thread.start()

    # monitor_proc = multiprocessing.Process(target=test_monitor, daemon=True)
    # loop.call_later(2, monitor_proc.start)

    with start_monitor(loop, monitor=WizWalkerConsole, locals=locals):
        app()
