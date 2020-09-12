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
    PacketHook,
    MoveLockHook,
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
        self.packet_socket_discriptor_addr = None
        self.packet_buffer_addr = None
        self.packet_buffer_len = None
        self.move_lock_addr = None

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
                pass

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

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_base(self):
        return self.process.read_int(self.player_struct_addr)

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_stat_base(self):
        return self.process.read_int(self.player_stat_addr)

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_backpack_stat_base(self):
        return self.process.read_int(self.backpack_stat_addr)

    @uses_hook("quest_struct")
    @utils.executor_function
    def read_quest_base(self):
        return self.process.read_int(self.quest_struct_addr)

    @uses_hook("player_struct")
    @utils.executor_function
    def read_xyz(self):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            x = self.process.read_float(player_struct + 0x2C)
            y = self.process.read_float(player_struct + 0x30)
            z = self.process.read_float(player_struct + 0x34)
        except pymem.exception.MemoryReadError:
            return None
        else:
            return utils.XYZ(x, y, z)

    @uses_hook("player_struct")
    @utils.executor_function
    def set_xyz(self, *, x=None, y=None, z=None):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            if x is not None:
                self.process.write_float(player_struct + 0x2C, x)
            if y is not None:
                self.process.write_float(player_struct + 0x30, y)
            if z is not None:
                self.process.write_float(player_struct + 0x34, z)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_yaw(self):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x40)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_yaw(self, yaw):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x40, yaw)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_pitch(self):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x38)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_pitch(self, pitch):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x38, pitch)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("player_struct")
    @utils.executor_function
    def read_player_roll(self):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            return self.process.read_float(player_struct + 0x3C)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_struct")
    @utils.executor_function
    def set_player_roll(self, roll):
        player_struct = self.process.read_int(self.player_struct_addr)
        try:
            self.process.write_float(player_struct + 0x3C, roll)
        except pymem.exception.MemoryWriteError:
            return False
        else:
            return True

    @uses_hook("quest_struct")
    @utils.executor_function
    def read_quest_xyz(self):
        quest_struct = self.process.read_int(self.quest_struct_addr)
        try:
            x = self.process.read_float(quest_struct + 0x81C)
            y = self.process.read_float(quest_struct + 0x81C + 0x4)
            z = self.process.read_float(quest_struct + 0x81C + 0x8)

            return utils.XYZ(x, y, z)

        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_health(self):
        stat_addr = self.process.read_int(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x40)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_mana(self):
        stat_addr = self.process.read_int(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x10 + 0x40)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_energy(self):
        stat_addr = self.process.read_int(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x3C)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_potions(self):
        stat_addr = self.process.read_int(self.player_stat_addr)
        try:
            # this is a float for some reason
            return int(self.process.read_float(stat_addr + 0x2C + 0x40))
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("player_stat_struct")
    @utils.executor_function
    def read_player_gold(self):
        stat_addr = self.process.read_int(self.player_stat_addr)
        try:
            return self.process.read_int(stat_addr + 0x4 + 0x40)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_player_backpack_used(self):
        backpack_addr = self.process.read_int(self.backpack_stat_addr)
        try:
            return self.process.read_int(backpack_addr)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("backpack_stat_struct")
    @utils.executor_function
    def read_player_backpack_total(self):
        backpack_addr = self.process.read_int(self.backpack_stat_addr)
        try:
            return self.process.read_int(backpack_addr + 0x4)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("packet_recv")
    @utils.executor_function
    def read_packet_socket_discriptor(self):
        try:
            return self.process.read_bytes(self.packet_socket_discriptor_addr, 20)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("packet_recv")
    @utils.executor_function
    def read_packet_buffer(self):
        buffer_addr = self.process.read_int(self.packet_buffer_addr)
        buffer_len = self.process.read_int(self.packet_buffer_len)
        try:
            return self.process.read_bytes(buffer_addr, buffer_len)
        except pymem.exception.MemoryReadError:
            return None

    @uses_hook("move_lock")
    @utils.executor_function
    def read_move_lock(self):
        move_lock = self.process.read_int(self.move_lock_addr)
        try:
            data = self.process.read_bytes(move_lock, 1)
            return struct.unpack("?", data)[0]
        except pymem.exception.MemoryReadError:
            return None

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

    @register_hook("packet_recv")
    @utils.executor_function
    def hook_packet_recv(self):
        packet_recv_hook = PacketHook(self)
        packet_recv_hook.hook()

        self.hooks.append(packet_recv_hook)
        self.packet_socket_discriptor_addr = packet_recv_hook.socket_discriptor
        self.packet_buffer_addr = packet_recv_hook.packet_buffer_addr
        self.packet_buffer_len = packet_recv_hook.packet_buffer_len

    @register_hook("move_lock")
    @utils.executor_function
    def hook_move_lock(self):
        move_lock_hook = MoveLockHook(self)
        move_lock_hook.hook()

        self.hooks.append(move_lock_hook)
        self.move_lock_addr = move_lock_hook.move_lock_addr

    # @register_hook("ignore_mouse_leave")
    # @utils.executor_function
    # def hook_ignore_mouse_leave(self):
    #     mouse_leave_hook = IgnoreMouseLeaveHook(self)
    #     mouse_leave_hook.hook()
    #
    #     self.hooks.append(mouse_leave_hook)
