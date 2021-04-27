import asyncio
import functools
import struct
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


class MemoryHandler:
    """
    Handles the internal memory calls, not for public use
    """

    def __init__(self, pid: int):
        self.process = pymem.Pymem()
        self.process.open_process_from_id(pid)
        self.process.check_wow64()

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

        self.active_hooks = defaultdict(lambda: False)

    def set_hook_active(self, hook):
        self.active_hooks[hook] = True

    def hook_functs(self):
        hooks = {}
        # Couldn't get anything else working for this, other than manually setting
        # some attr on each hook method
        for thing in dir(self):
            if thing.startswith("hook_") and not any(
                thing.endswith(i) for i in ("all", "functs")
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
        hooks = []
        for hook in self.hook_functs().values():
            # Need the coroutine objects
            hooks.append(hook())

        # return_exceptions=True will make all exceptions return as results
        return await asyncio.gather(*hooks, return_exceptions=True)

    @register_hook("player_struct")
    @utils.executor_function
    def hook_player_struct(self):
        player_hook = PlayerHook(self)
        player_hook.hook()

        self.hooks.append(player_hook)
        self.player_struct_addr = player_hook.player_struct

    @register_hook("quest_struct")
    @utils.executor_function
    def hook_quest_struct(self):
        quest_hook = QuestHook(self)
        quest_hook.hook()

        self.hooks.append(quest_hook)
        self.quest_struct_addr = quest_hook.cord_struct

    @register_hook("player_stat_struct")
    @utils.executor_function
    def hook_player_stat_struct(self):
        player_stat_hook = PlayerStatHook(self)
        player_stat_hook.hook()

        self.hooks.append(player_stat_hook)
        self.player_stat_addr = player_stat_hook.stat_addr

    @register_hook("backpack_stat_struct")
    @utils.executor_function
    def hook_backpack_stat_struct(self):
        backpack_stat_hook = BackpackStatHook(self)
        backpack_stat_hook.hook()

        self.hooks.append(backpack_stat_hook)
        self.backpack_stat_addr = backpack_stat_hook.backpack_struct_addr

    # @register_hook("move_lock")
    # @utils.executor_function
    # def hook_move_lock(self):
    #     move_lock_hook = MoveLockHook(self)
    #     move_lock_hook.hook()
    #
    #     self.hooks.append(move_lock_hook)
    #     self.move_lock_addr = move_lock_hook.move_lock_addr

    @register_hook("duel")
    @utils.executor_function
    def hook_duel(self):
        duel_hook = DuelHook(self)
        duel_hook.hook()

        self.hooks.append(duel_hook)
        self.current_duel_addr = duel_hook.current_duel_addr

    @register_hook("mouseless_cursor_move")
    @utils.executor_function
    def hook_mouseless_cursor_move(self):
        mouseless_cursor_hook = MouselessCursorMoveHook(self)
        mouseless_cursor_hook.hook()

        self.hooks.append(mouseless_cursor_hook)
        self.mouse_pos = mouseless_cursor_hook.mouse_pos_addr

        self.process.write_longlong(self.mouse_pos, 0)
