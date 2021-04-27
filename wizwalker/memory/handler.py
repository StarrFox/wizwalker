import asyncio
import struct
from typing import Any, Optional

import pymem
import pymem.exception

from wizwalker import HookAlreadyActivated, HookNotActive
from .hooks import (
    PlayerHook,
    QuestHook,
    PlayerStatHook,
    BackpackStatHook,
    DuelHook,
    MouselessCursorMoveHook,
)
from .memory_reader import MemoryReader


class HookHandler(MemoryReader):
    """
    Manages hooks
    """

    AUTOBOT_PATTERN = (
        rb"\x48\x8B\xC4\x55\x41\x54\x41\x55\x41\x56\x41\x57......."
        rb"\x48......\x48.......\x48\x89\x58\x10\x48\x89"
        rb"\x70\x18\x48\x89\x78\x20.......\x48\x33\xC4....."
        rb"..\x4C\x8B\xE9.......\x80"
    )
    # rounded down
    AUTOBOT_SIZE = 3900

    def __init__(self, process: pymem.Pymem):
        super().__init__(process)

        self.autobot_address = None
        self.autobot_lock = None
        self.original_autobot_bytes = None
        self.autobot_pos = 0

        self.active_hooks = []
        self.base_addrs = {}

    def get_open_autobot_address(self, size: int) -> int:
        if self.autobot_pos + size > self.AUTOBOT_SIZE:
            raise RuntimeError("Somehow went over autobot size")

        addr = self.autobot_address + self.autobot_pos
        self.autobot_pos += size
        return addr

    async def get_autobot_address(self):
        addr = await self.pattern_scan(self.AUTOBOT_PATTERN)
        if addr is None:
            raise RuntimeError("Pattern scan failed for autobot pattern")

        self.autobot_address = addr

    async def prepare_autobot(self):
        if self.autobot_address is None:
            await self.get_autobot_address()

            # noinspection PyTypeChecker
            self.original_autobot_bytes = await self.read_bytes(
                self.autobot_address, self.AUTOBOT_SIZE
            )

    async def rewrite_autobot(self):
        if self.autobot_address is not None:
            await self.write_bytes(self.autobot_address, self.original_autobot_bytes)

    async def close(self):
        await self.rewrite_autobot()

        for hook in self.active_hooks:
            await self.run_in_executor(hook.unhook())

    async def check_for_autobot(self):
        if self.autobot_lock is None:
            self.autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self.autobot_lock:
            await self.prepare_autobot()

    def check_if_hook_active(self, hook_type) -> bool:
        for hook in self.active_hooks:
            if isinstance(hook, hook_type):
                return True

        return False

    def get_hook_by_type(self, hook_type) -> Any:
        for hook in self.active_hooks:
            if isinstance(hook, hook_type):
                return hook

        return None

    async def activate_all_hooks(self):
        hooks = [
            self.activate_player_hook(),
            self.activate_duel_hook(),
            self.activate_quest_hook(),
            self.activate_mouseless_cursor_hook(),
            self.activate_backpack_stat_hook(),
            self.activate_player_stat_hook(),
        ]

        return await asyncio.gather(*hooks)

    async def activate_player_hook(self):
        if self.check_if_hook_active(PlayerHook):
            raise HookAlreadyActivated("Player hook already active")

        await self.check_for_autobot()

        player_hook = PlayerHook(self)
        await self.run_in_executor(player_hook.hook)

        self.active_hooks.append(player_hook)
        self.base_addrs["player_struct"] = player_hook.player_struct

    async def read_player_base(self) -> Optional[int]:
        addr = self.base_addrs.get("player_struct")
        if addr is None:
            raise HookNotActive("Player hook not active")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_duel_hook(self):
        if self.check_if_hook_active(DuelHook):
            raise HookAlreadyActivated("Duel hook already active")

        await self.check_for_autobot()

        duel_hook = DuelHook(self)
        await self.run_in_executor(duel_hook.hook)

        self.active_hooks.append(duel_hook)
        self.base_addrs["current_duel"] = duel_hook.current_duel_addr

    async def read_current_duel_base(self) -> Optional[int]:
        addr = self.base_addrs.get("current_duel")
        if addr is None:
            raise HookNotActive("Duel hook not active")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_quest_hook(self):
        if self.check_if_hook_active(QuestHook):
            raise HookAlreadyActivated("Quest hook already active")

        await self.check_for_autobot()

        quest_hook = QuestHook(self)
        await self.run_in_executor(quest_hook.hook)

        self.active_hooks.append(quest_hook)
        self.base_addrs["quest_struct"] = quest_hook.cord_struct

    async def read_quest_base(self) -> Optional[int]:
        addr = self.base_addrs.get("quest_struct")
        if addr is None:
            raise HookNotActive("Quest hook not active")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_player_stat_hook(self):
        if self.check_if_hook_active(PlayerStatHook):
            raise HookAlreadyActivated("Player stat hook already active")

        await self.check_for_autobot()

        player_stat_hook = PlayerStatHook(self)
        await self.run_in_executor(player_stat_hook.hook)

        self.active_hooks.append(player_stat_hook)
        self.base_addrs["player_stat_struct"] = player_stat_hook.stat_addr

    async def read_player_stat_base(self) -> Optional[int]:
        addr = self.base_addrs.get("player_stat_struct")
        if addr is None:
            raise HookNotActive("Player stat hook not active")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_backpack_stat_hook(self):
        if self.check_if_hook_active(BackpackStatHook):
            raise HookAlreadyActivated("Backpack stat hook already active")

        await self.check_for_autobot()

        backpack_stat_hook = BackpackStatHook(self)
        await self.run_in_executor(backpack_stat_hook.hook)

        self.active_hooks.append(backpack_stat_hook)
        self.base_addrs[
            "backpack_stat_struct"
        ] = backpack_stat_hook.backpack_struct_addr

    async def read_backpack_stat_base(self) -> Optional[int]:
        addr = self.base_addrs.get("backpack_stat_struct")
        if addr is None:
            raise HookNotActive("Backpack stat hook not active")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_mouseless_cursor_hook(self):
        if self.check_if_hook_active(MouselessCursorMoveHook):
            raise HookAlreadyActivated("Mouseless cursor hook already active")

        await self.check_for_autobot()

        mouseless_cursor_hook = MouselessCursorMoveHook(self)
        await self.run_in_executor(mouseless_cursor_hook.hook)

        self.active_hooks.append(mouseless_cursor_hook)
        self.base_addrs["mouse_position"] = mouseless_cursor_hook.mouse_pos_addr

        await self.write_mouse_position(0, 0)

    async def write_mouse_position(self, x: int, y: int):
        addr = self.base_addrs.get("mouse_position")
        if addr is None:
            raise HookNotActive("Mouseless cursor hook not active")

        packed_position = struct.pack("<ii", x, y)

        await self.write_bytes(addr, packed_position)
