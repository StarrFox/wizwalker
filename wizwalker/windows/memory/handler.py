import asyncio
import functools
from collections import defaultdict

import pymem

from wizwalker import HookAlreadyActivated, utils, HookNotActive
from .hooks import (
    PlayerHook,
    QuestHook,
    PlayerStatHook,
    BackpackStatHook,
    DuelHook,
    MouselessCursorMoveHook,
)


def uses_hook(hook: str):
    def decorator(function):
        @functools.wraps(function)
        async def wrapped(*args, **kwargs):
            memory_handler = args[0]
            if not memory_handler.active_hooks[hook]:
                raise HookNotActive(hook)

            return await function(*args, **kwargs)

        return wrapped

    return decorator


def register_hook(hook: str):
    def decorator(function):
        @functools.wraps(function)
        async def wrapped(*args, **kwargs):
            memory_handler = args[0]
            if memory_handler.active_hooks[hook]:
                raise HookAlreadyActivated(hook)

            memory_handler.set_hook_active(hook)

            return await function(*args, **kwargs)

        return wrapped

    return decorator


def scan_all_from(start_address: int, handle: int, pattern: bytes):
    next_region = start_address
    found = None

    while next_region < 0x7FFFFFFF0000:
        next_region, found = pymem.pattern.scan_pattern_page(
            handle, next_region, pattern
        )
        if found:
            break

    return found


class HookHandler:
    AUTOBOT_PATTERN = (
        rb"\x48\x8B\xC4\x55\x41\x54\x41\x55\x41\x56\x41\x57......."
        rb"\x48......\x48.......\x48\x89\x58\x10\x48\x89"
        rb"\x70\x18\x48\x89\x78\x20.......\x48\x33\xC4....."
        rb"..\x4C\x8B\xE9.......\x80"
    )
    # rounded down
    AUTOBOT_SIZE = 3900

    def __init__(self, memory_handler):
        self.process = memory_handler.process
        self.memory_handler = memory_handler

        self.autobot_address = None
        self.autobot_lock = None
        self.original_autobot_bytes = None
        self.autobot_pos = 0

    @staticmethod
    async def run_in_executor(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        function = functools.partial(func, *args, **kwargs)

        return await loop.run_in_executor(None, function)

    # TODO: replace with abstract memory-object
    # This could be blocking; handle that
    def pattern_scan(self, pattern: bytes, *, module: str = None):
        if module:
            module = pymem.process.module_from_name(
                self.memory_handler.process.process_handle, module
            )
            jump_address = pymem.pattern.pattern_scan_module(
                self.memory_handler.process.process_handle, module, pattern
            )

        else:
            jump_address = scan_all_from(
                self.memory_handler.process.process_base.lpBaseOfDll,
                self.memory_handler.process.process_handle,
                pattern,
            )

        return jump_address

    def read_bytes(self, address: int, size: int) -> bytes:
        return self.memory_handler.process.read_bytes(address, size)

    def write_bytes(self, address: int, _bytes: bytes):
        self.memory_handler.process.write_bytes(
            address, _bytes, len(_bytes),
        )

    def get_open_autobot_address(self, size: int) -> int:
        if self.autobot_pos + size > self.AUTOBOT_SIZE:
            raise RuntimeError("Somehow went over autobot size")

        addr = self.autobot_address + self.autobot_pos
        self.autobot_pos += size
        return addr

    def get_autobot_address(self):
        addr = self.pattern_scan(self.AUTOBOT_PATTERN)
        if addr is None:
            raise RuntimeError("Pattern scan failed for autobot pattern")

        self.autobot_address = addr

    def prepare_autobot(self):
        if self.autobot_address is None:
            self.get_autobot_address()

            self.original_autobot_bytes = self.read_bytes(
                self.autobot_address, self.AUTOBOT_SIZE
            )

    # also blocking
    def rewrite_autobot(self):
        if self.autobot_address is not None:
            self.write_bytes(self.autobot_address, self.original_autobot_bytes)

    def close(self):
        self.rewrite_autobot()

    async def activate_player_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        player_hook = PlayerHook(self.memory_handler)
        player_hook.hook()
        # await self.run_in_executor(player_hook.hook)

        self.memory_handler.hooks.append(player_hook)
        self.memory_handler.player_struct_addr = player_hook.player_struct

    async def activate_duel_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        duel_hook = DuelHook(self.memory_handler)
        await self.run_in_executor(duel_hook.hook)

        self.memory_handler.hooks.append(duel_hook)
        self.memory_handler.current_duel_addr = duel_hook.current_duel_addr

    async def activate_quest_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        quest_hook = QuestHook(self.memory_handler)
        await self.run_in_executor(quest_hook.hook)

        self.memory_handler.hooks.append(quest_hook)
        self.memory_handler.quest_struct_addr = quest_hook.cord_struct

    async def activate_player_stat_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        player_stat_hook = PlayerStatHook(self.memory_handler)
        await self.run_in_executor(player_stat_hook.hook)

        self.memory_handler.hooks.append(player_stat_hook)
        self.memory_handler.player_stat_addr = player_stat_hook.stat_addr

    async def activate_backpack_stat_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        backpack_stat_hook = BackpackStatHook(self.memory_handler)
        await self.run_in_executor(backpack_stat_hook.hook)

        self.memory_handler.hooks.append(backpack_stat_hook)
        self.memory_handler.backpack_stat_addr = backpack_stat_hook.backpack_struct_addr

    async def activate_mouseless_cursor_hook(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            self.prepare_autobot()

        mouseless_cursor_hook = MouselessCursorMoveHook(self.memory_handler)
        await self.run_in_executor(mouseless_cursor_hook.hook)

        self.memory_handler.hooks.append(mouseless_cursor_hook)
        self.memory_handler.mouse_pos = mouseless_cursor_hook.mouse_pos_addr

        self.process.write_longlong(self.memory_handler.mouse_pos, 0)


class MemoryHandler:
    """
    Handles the internal memory calls, not for public use
    """

    def __init__(self, pid: int):
        self.process = pymem.Pymem()
        self.process.open_process_from_id(pid)
        self.process.check_wow64()

        self.hook_handler = HookHandler(self)

        self.player_struct_addr = None
        self.quest_struct_addr = None
        self.player_stat_addr = None
        self.backpack_stat_addr = None
        self.move_lock_addr = None
        self.current_duel_addr = None

        self.mouse_pos = None

        self.hooks = []
        self.active_hooks = defaultdict(lambda: False)

    @utils.executor_function
    def close(self):
        """
        Closes MemoryHandler, closing all hooks
        """
        for hook in self.hooks:
            try:
                hook.unhook()
            except pymem.exception.MemoryWriteError:
                # TODO: error here
                pass

        self.hook_handler.close()
        self.active_hooks = defaultdict(lambda: False)

    def set_hook_active(self, hook):
        self.active_hooks[hook] = True

    def hook_functs(self):
        hooks = {}
        # Couldn't get anything else working for this, other than manually setting
        # some attr on each hook method
        for thing in dir(self):
            if thing.startswith("hook_") and not any(
                thing.endswith(i) for i in ("all", "functs", "handler")
            ):
                hooks[thing.replace("hook_", "")] = getattr(self, thing)

        return hooks

    def is_hook_active(self, hook):
        return self.active_hooks[hook]

    @uses_hook("duel")
    @utils.executor_function
    def is_in_battle(self):
        """True if in battle; False if None"""
        current_battle_addr = self.process.read_longlong(self.current_duel_addr)
        try:
            duel_phase = self.process.read_int(current_battle_addr + 160)
        except pymem.exception.MemoryReadError:
            return None
        else:
            return duel_phase in (0, 1, 2, 3, 4, 5, 6)

    @uses_hook("mouseless_cursor_move")
    @utils.executor_function
    def write_mouse_position(self, x: int, y: int):
        self.process.write_int(self.mouse_pos, x)
        self.process.write_int(self.mouse_pos + 4, y)

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_base(self):
        return self.process.read_longlong(self.player_struct_addr)

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_stat_base(self):
        return self.process.read_longlong(self.player_stat_addr)

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_backpack_stat_base(self):
        return self.process.read_int(self.backpack_stat_addr)

    @uses_hook("quest_struct")
    @utils.executor_function
    def read_quest_base(self):
        return self.process.read_longlong(self.quest_struct_addr)

    @uses_hook("player_struct")
    @utils.executor_function
    def read_xyz(self):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            x = self.process.read_float(player_struct + 0x58)  # was 2c
            y = self.process.read_float(player_struct + 0x58 + 4)
            z = self.process.read_float(player_struct + 0x58 + 4 + 4)
        except pymem.exception.MemoryReadError:
            return None
        else:
            return utils.XYZ(x, y, z)

    @uses_hook("player_struct")
    @utils.executor_function
    def set_xyz(self, x=None, y=None, z=None):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            if x is not None:
                self.process.write_float(player_struct + 0x58, x)
            if y is not None:
                self.process.write_float(player_struct + 0x58 + 4, y)
            if z is not None:
                self.process.write_float(player_struct + 0x58 + 4 + 4, z)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_yaw(self):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x58 + 20)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_yaw(self, yaw):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x58 + 20, yaw)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_pitch(self):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x58 + 12)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_pitch(self, pitch):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x58 + 12, pitch)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_roll(self):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x58 + 16)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_roll(self, roll):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x58 + 16, roll)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_scale(self):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x58 + 24)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_scale(self, scale):
        player_struct = self.process.read_longlong(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x58 + 24, scale)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("quest_struct")
    @utils.executor_function
    def read_quest_xyz(self):
        quest_struct = self.process.read_longlong(self.quest_struct_addr)
        try:
            x = self.process.read_float(quest_struct)
            y = self.process.read_float(quest_struct + 0x4)
            z = self.process.read_float(quest_struct + 0x8)

            return utils.XYZ(x, y, z)

        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_level(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 308)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_gardening_level(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_uchar(stat_addr + 824)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_gardening_experience(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 828)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_fishing_level(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_uchar(stat_addr + 853)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_fishing_experience(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 856)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_health(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x68)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_health_max(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            base = self.process.read_int(stat_addr + 80)
            bonus = self.process.read_int(stat_addr + 208)
            return base + bonus
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_mana(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x78)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_mana_max(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            base = self.process.read_int(stat_addr + 84)
            bonus = self.process.read_int(stat_addr + 212)
            return base + bonus
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_energy(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x64)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_potions(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            # this is a float for some reason
            # it's because you can partially fill potions with minigames -Forrest
            return self.process.read_float(stat_addr + 156)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_potions_max(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_float(stat_addr + 152)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_gold(self):
        stat_addr = self.process.read_longlong(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 108)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_player_backpack_used(self):
        backpack_addr = self.process.read_longlong(self.backpack_stat_addr)
        try:
            return self.process.read_int(backpack_addr)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_player_backpack_total(self):
        backpack_addr = self.process.read_longlong(self.backpack_stat_addr)
        try:
            return self.process.read_int(backpack_addr + 0x4)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("duel")
    @utils.executor_function
    def read_move_lock(self):
        current_battle_addr = self.process.read_longlong(self.current_duel_addr)
        try:
            duel_phase = self.process.read_int(current_battle_addr + 160)
        except pymem.exception.MemoryReadError:
            return None
        else:
            return duel_phase in (0, 1, 2, 3, 4, 5, 6)

    async def hook_all(self):
        hooks = [
            self.hook_player_struct(),
            self.hook_quest_struct(),
            self.hook_backpack_stat_struct(),
            self.hook_duel(),
            self.hook_mouseless_cursor_move(),
            self.hook_player_stat_struct(),
        ]

        # return_exceptions=True will make all exceptions return as results
        return await asyncio.gather(*hooks, return_exceptions=True)

    @register_hook("player_struct")
    async def hook_player_struct(self):
        await self.hook_handler.activate_player_hook()

    @register_hook("quest_struct")
    async def hook_quest_struct(self):
        await self.hook_handler.activate_quest_hook()

    @register_hook("player_stat_struct")
    async def hook_player_stat_struct(self):
        await self.hook_handler.activate_player_stat_hook()

    @register_hook("backpack_stat_struct")
    async def hook_backpack_stat_struct(self):
        await self.hook_handler.activate_backpack_stat_hook()

    @register_hook("duel")
    async def hook_duel(self):
        await self.hook_handler.activate_duel_hook()

    @register_hook("mouseless_cursor_move")
    async def hook_mouseless_cursor_move(self):
        await self.hook_handler.activate_mouseless_cursor_hook()
