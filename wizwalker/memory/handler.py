import asyncio
import struct
from typing import Any, Optional

import pymem
import pymem.exception
from loguru import logger

from wizwalker import HookAlreadyActivated, HookNotActive
from .hooks import (
    PlayerHook,
    QuestHook,
    PlayerStatHook,
    BackpackStatHook,
    DuelHook,
    MouselessCursorMoveHook,
    ClientHook,
    RootWindowHook,
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

        self._autobot_address = None
        self._autobot_lock = None
        self._original_autobot_bytes = b""
        self._autobot_pos = 0

        self._active_hooks = []
        self._base_addrs = {}

    async def _get_open_autobot_address(self, size: int) -> int:
        if self._autobot_pos + size > self.AUTOBOT_SIZE:
            raise RuntimeError("Somehow went over autobot size")

        addr = self._autobot_address + self._autobot_pos
        self._autobot_pos += size

        logger.debug(
            f"Allocating autobot address {addr}; autobto position is now {self._autobot_pos}"
        )
        return addr

    async def _get_autobot_address(self):
        addr = await self.pattern_scan(self.AUTOBOT_PATTERN)
        if addr is None:
            raise RuntimeError("Pattern scan failed for autobot pattern")

        self._autobot_address = addr

    async def _prepare_autobot(self):
        if self._autobot_address is None:
            await self._get_autobot_address()

            # we only need to write back the pattern
            self._original_autobot_bytes = await self.read_bytes(
                self._autobot_address, len(self.AUTOBOT_PATTERN)
            )
            logger.debug(
                f"Got original bytes {self._original_autobot_bytes} from autobot"
            )
            await self.write_bytes(self._autobot_address, b"\x00" * self.AUTOBOT_SIZE)

    async def _rewrite_autobot(self):
        if self._autobot_address is not None:
            compare_bytes = await self.read_bytes(
                self._autobot_address, len(self.AUTOBOT_PATTERN)
            )
            # Give some time for execution point to leave hooks
            await asyncio.sleep(1)

            # Only write if the pattern isn't there
            if compare_bytes != self._original_autobot_bytes:
                logger.debug(
                    f"Rewriting bytes {self._original_autobot_bytes} to autbot"
                )
                await self.write_bytes(
                    self._autobot_address, self._original_autobot_bytes
                )

    async def _allocate_autobot_bytes(self, size: int) -> int:
        address = await self._get_open_autobot_address(size)

        return address

    async def close(self):
        for hook in self._active_hooks:
            await hook.unhook()

        await self._rewrite_autobot()

        self._active_hooks = []
        self._autobot_pos = 0
        self._autobot_address = None
        self._base_addrs = {}

    async def _check_for_autobot(self):
        if self._autobot_lock is None:
            self._autobot_lock = asyncio.Lock()

        # this is so it isn't prepared more than once
        async with self._autobot_lock:
            await self._prepare_autobot()

    def _check_if_hook_active(self, hook_type) -> bool:
        for hook in self._active_hooks:
            if isinstance(hook, hook_type):
                return True

        return False

    def _get_hook_by_type(self, hook_type) -> Any:
        for hook in self._active_hooks:
            if isinstance(hook, hook_type):
                return hook

        return None

    async def _read_hook_base_addr(self, addr_name: str, hook_name: str):
        addr = self._base_addrs.get(addr_name)
        if addr is None:
            raise HookNotActive(hook_name)

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_all_hooks(self):
        """
        Activate all hooks but mouseless
        """
        hooks = [
            self.activate_player_hook(),
            self.activate_duel_hook(),
            self.activate_quest_hook(),
            self.activate_backpack_stat_hook(),
            self.activate_player_stat_hook(),
            self.activate_client_hook(),
            self.activate_root_window_hook(),
        ]

        return await asyncio.gather(*hooks)

    async def activate_player_hook(self):
        if self._check_if_hook_active(PlayerHook):
            raise HookAlreadyActivated("Player")

        await self._check_for_autobot()

        player_hook = PlayerHook(self)
        await player_hook.hook()

        self._active_hooks.append(player_hook)
        self._base_addrs["player_struct"] = player_hook.player_struct

    async def read_player_base(self) -> Optional[int]:
        return await self._read_hook_base_addr("player_struct", "Player")

    async def activate_duel_hook(self):
        if self._check_if_hook_active(DuelHook):
            raise HookAlreadyActivated("Duel")

        await self._check_for_autobot()

        duel_hook = DuelHook(self)
        await duel_hook.hook()

        self._active_hooks.append(duel_hook)
        self._base_addrs["current_duel"] = duel_hook.current_duel_addr

    async def read_current_duel_base(self) -> Optional[int]:
        return await self._read_hook_base_addr("current_duel", "Duel")

    async def activate_quest_hook(self):
        if self._check_if_hook_active(QuestHook):
            raise HookAlreadyActivated("Quest")

        await self._check_for_autobot()

        quest_hook = QuestHook(self)
        await quest_hook.hook()

        self._active_hooks.append(quest_hook)
        self._base_addrs["quest_struct"] = quest_hook.cord_struct

    async def read_quest_base(self) -> Optional[int]:
        return await self._read_hook_base_addr("quest_struct", "Quest")

    async def activate_player_stat_hook(self):
        if self._check_if_hook_active(PlayerStatHook):
            raise HookAlreadyActivated("Player stat")

        await self._check_for_autobot()

        player_stat_hook = PlayerStatHook(self)
        await player_stat_hook.hook()

        self._active_hooks.append(player_stat_hook)
        self._base_addrs["player_stat_struct"] = player_stat_hook.stat_addr

    async def read_player_stat_base(self) -> Optional[int]:
        return await self._read_hook_base_addr("player_stat_struct", "Player stat")

    async def activate_backpack_stat_hook(self):
        if self._check_if_hook_active(BackpackStatHook):
            raise HookAlreadyActivated("Backpack stat")

        await self._check_for_autobot()

        backpack_stat_hook = BackpackStatHook(self)
        await backpack_stat_hook.hook()

        self._active_hooks.append(backpack_stat_hook)
        self._base_addrs[
            "backpack_stat_struct"
        ] = backpack_stat_hook.backpack_struct_addr

    async def read_backpack_stat_base(self) -> Optional[int]:
        addr = self._base_addrs.get("backpack_stat_struct")
        if addr is None:
            raise HookNotActive("Backpack stat")

        try:
            return await self.read_typed(addr, "long long")
        except pymem.exception.MemoryReadError:
            return None

    async def activate_client_hook(self):
        if self._check_if_hook_active(ClientHook):
            raise HookAlreadyActivated("Client")

        await self._check_for_autobot()

        client_hook = ClientHook(self)
        await client_hook.hook()

        self._active_hooks.append(client_hook)
        self._base_addrs["current_client"] = client_hook.current_client_addr

    async def read_current_client_base(self):
        return await self._read_hook_base_addr("current_client", "Client")

    async def activate_root_window_hook(self):
        if self._check_if_hook_active(RootWindowHook):
            raise HookAlreadyActivated("Root window")

        await self._check_for_autobot()

        root_window_hook = RootWindowHook(self)
        await root_window_hook.hook()

        self._active_hooks.append(root_window_hook)
        self._base_addrs[
            "current_root_window"
        ] = root_window_hook.current_root_window_addr

    async def read_current_root_window_base(self):
        return await self._read_hook_base_addr("current_root_window", "Root window")

    async def activate_mouseless_cursor_hook(self):
        if self._check_if_hook_active(MouselessCursorMoveHook):
            raise HookAlreadyActivated("Mouseless cursor")

        await self._check_for_autobot()

        mouseless_cursor_hook = MouselessCursorMoveHook(self)
        await mouseless_cursor_hook.hook()

        self._active_hooks.append(mouseless_cursor_hook)
        self._base_addrs["mouse_position"] = mouseless_cursor_hook.mouse_pos_addr

        await self.write_mouse_position(0, 0)

    async def write_mouse_position(self, x: int, y: int):
        addr = self._base_addrs.get("mouse_position")
        if addr is None:
            raise HookNotActive("Mouseless cursor")

        packed_position = struct.pack("<ii", x, y)

        await self.write_bytes(addr, packed_position)