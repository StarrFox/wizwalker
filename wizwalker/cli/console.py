import asyncio
import re
import threading
import sys
from typing import Any, Coroutine, Union


import terminaltables
import aioconsole
from aiomonitor import Monitor, start_monitor, cli
from aiomonitor.utils import close_server, console_proxy


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
            self.write(f"Error in coro {coro.__name__}: {exc}")
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
        walker.get_clients()
        self.write(f"Attached to {len(walker.clients)} clients")
        for idx, client in enumerate(walker.clients):
            self.run_coro(client.activate_hooks())
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

            # TODO: add player_base and player_stat_base and all other base address (optional arg)
            client_attrs = [
                "xyz",
                "yaw",
                "roll",
                "pitch",
                "scale",
                "quest_xyz",
                "health",
                "mana",
                "potions",
                "gold",
                "energy",
                "backpack_space_used",
                "backpack_space_total",
                "move_lock",
            ]
            for attr in client_attrs:
                table_data.append([attr, self.run_coro(getattr(client, attr)())])

            table = terminaltables.AsciiTable(table_data, f"client-{idx}")
            self.write(table.table)

    def do_cache(self):
        """Cache data"""
        walker = self.get_local("walker")
        self.run_coro(walker.cache_data())
        self.write("Cached data")

    def do_teleport(self, x: float, y: float, z: float = None, yaw: float = None):
        """Teleport to a location

        x y z and yaw are all optional
        """
        walker = self.get_local("walker")
        for client in walker.clients:
            self.run_coro(client.teleport(x=x, y=y, z=z, yaw=yaw))

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
        template_ids = self.run_coro(walker.get_template_ids())

        regex = re.compile(pattern, re.IGNORECASE)
        for tid, name in template_ids.items():
            if regex.match(name):
                self.write(f"{tid=} {name=}")

    def do_checkid(self, tid: str):
        """Get the name mapped to a templateid

        cache command must be run first
        """
        walker = self.get_local("walker")
        template_ids: dict = self.run_coro(walker.get_template_ids())

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

    def do_onehook(self, name: str):
        """Get clients and activate one hook"""
        walker = self.get_local("walker")
        walker.get_clients()
        self.write(f"Attached to {len(walker.clients)} clients")

        for client in walker.clients:
            self.run_coro(client.activate_hooks(name))

        self.write(f"Hooked {name} on all clients")


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
