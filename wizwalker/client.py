import ctypes.wintypes
from functools import cached_property
from typing import Optional

from . import utils
from .windows import KeyboardHandler, MemoryHandler, user32
from .packets import PacketHookWatcher


class Client:
    """Represents a connected wizard client"""

    def __init__(self, window_handle: int):
        self.window_handle = window_handle
        self.keyboard = KeyboardHandler(window_handle)
        self.memory = MemoryHandler(self.process_id)
        self.current_zone = None

        self.packet_watcher = PacketHookWatcher(self)

    def __repr__(self):
        return f"<Client {self.window_handle=} {self.process_id=} {self.memory=}>"

    async def close(self):
        await self.memory.close()

    @cached_property
    def process_id(self):
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
        pid = ctypes.wintypes.DWORD()
        pid_ref = ctypes.byref(pid)  # we need a pointer to the pid val's memory
        user32.GetWindowThreadProcessId(self.window_handle, pid_ref)
        return pid.value

    def login(self, username: str, password: str):
        """
        Login to a client that is at the login screen
        """
        utils.wiz_login(self.window_handle, username, password)

    def watch_packets(self):
        """
        Start Watching packets for information
        """
        self.packet_watcher.start()

    async def teleport(self, *, x: float = None, y: float = None, z: float = None, yaw: float = None):
        """
        Teleport the player to a set x, y, z
        returns raises RuntimeError if not injected, True otherwise
        """
        res = await self.memory.set_xyz(
            x=x,
            y=y,
            z=z,
        )

        if yaw:
            await self.memory.set_player_yaw(yaw)

        return res

    async def xyz(self) -> Optional[utils.XYZ]:
        """
        Player xyz if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self.memory.read_xyz()

    async def yaw(self) -> Optional[float]:
        """
        Player yaw if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self.memory.read_player_yaw()

    async def set_yaw(self, yaw: float) -> bool:
        """
        Set the player yaw to this value,
        returns True if injected and value was set, otherwise raises RuntimeError
        """
        return await self.memory.set_player_yaw(yaw)

    async def quest_xyz(self) -> Optional[utils.XYZ]:
        """
        Quest xyz if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self.memory.read_quest_xyz()

    async def health(self) -> Optional[int]:
        """
        Player health if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_health()

    async def mana(self) -> Optional[int]:
        """
        Player mana if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_mana()

    async def potions(self) -> Optional[int]:
        """
        Player full potions if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_potions()

    async def gold(self) -> Optional[int]:
        """
        Player gold if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_gold()

    async def backpack_space_used(self) -> Optional[int]:
        """
        Player backpack used space if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_backpack_used()

    async def backpack_space_total(self) -> Optional[int]:
        """
        Player backpack total space if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self.memory.read_player_backpack_total()
