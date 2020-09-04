import ctypes.wintypes
from functools import cached_property
from typing import Optional

from . import utils
from .packets import PacketHookWatcher
from .windows import KeyboardHandler, MemoryHandler, user32


WIZARD_SPEED = 580


class Client:
    """Represents a connected wizard client"""

    def __init__(self, window_handle: int):
        self.window_handle = window_handle
        self._keyboard = KeyboardHandler(window_handle)
        self._memory = MemoryHandler(self.process_id)
        self.current_zone = None

        self.packet_watcher = PacketHookWatcher(self)

    def __repr__(self):
        return f"<Client {self.window_handle=} {self.process_id=}>"

    async def close(self):
        await self._memory.close()

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

    def get_hooks(self) -> list:
        """
        return a list of hook_names from the underlying MemoryHandler
        """
        return self._memory.hook_functs().keys()

    async def activate_hooks(self, *hook_names: Optional[str]):
        """
        Activate a number of hooks
        or pass None to activate all
        """
        if not hook_names:
            await self._memory.hook_all()

        else:
            for hook_name in hook_names:
                hook = getattr(self._memory, "hook_" + hook_name, None)
                if not hook:
                    raise ValueError(f"{hook_name} is not a valid hook")

                await hook()

    async def goto(self, x: float, y: float, *, use_nodes: bool = False):
        """
        Moves the player to a specific x and y
        """
        if use_nodes is False:
            await self._to_point(x, y)
        else:
            raise NotImplemented("WIP")

    async def _to_point(self, x, y):
        """
        do not use
        """
        current_xyz = await self.xyz()
        target_xyz = utils.XYZ(x, y, current_xyz.z)
        distance = current_xyz - target_xyz
        move_seconds = distance / WIZARD_SPEED
        yaw = utils.calculate_perfect_yaw(current_xyz, target_xyz)

        await self.set_yaw(yaw)
        await self._keyboard.send_key("W", move_seconds)

    async def teleport(
        self, *, x: float = None, y: float = None, z: float = None, yaw: float = None
    ):
        """
        Teleport the player to a set x, y, z
        returns raises RuntimeError if not injected, True otherwise
        """
        res = await self._memory.set_xyz(x=x, y=y, z=z,)

        if yaw is not None:
            await self._memory.set_player_yaw(yaw)

        return res

    async def xyz(self) -> Optional[utils.XYZ]:
        """
        Player xyz if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self._memory.read_xyz()

    async def yaw(self) -> Optional[float]:
        """
        Player yaw if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self._memory.read_player_yaw()

    async def set_yaw(self, yaw: float) -> bool:
        """
        Set the player yaw to this value,
        returns True if injected and value was set, otherwise raises RuntimeError
        """
        return await self._memory.set_player_yaw(yaw)

    async def roll(self) -> Optional[float]:
        """
        Player yaw if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self._memory.read_player_roll()

    async def set_roll(self, roll: float) -> bool:
        """
        Set the player roll to this value,
        returns True if injected and value was set, otherwise raises RuntimeError
        """
        return await self._memory.set_player_roll(roll)

    async def pitch(self) -> Optional[float]:
        """
        Player yaw if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self._memory.read_player_pitch()

    async def set_pitch(self, pitch: float) -> bool:
        """
        Set the player pitch to this value,
        returns True if injected and value was set, otherwise raises RuntimeError
        """
        return await self._memory.set_player_roll(pitch)

    async def quest_xyz(self) -> Optional[utils.XYZ]:
        """
        Quest xyz if memory hooks are injected, otherwise raises RuntimeError
        """
        return await self._memory.read_quest_xyz()

    async def health(self) -> Optional[int]:
        """
        Player health if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_health()

    async def mana(self) -> Optional[int]:
        """
        Player mana if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_mana()

    async def energy(self) -> Optional[int]:
        """
        Player energy if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_energy()

    async def potions(self) -> Optional[int]:
        """
        Player full potions if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_potions()

    async def gold(self) -> Optional[int]:
        """
        Player gold if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_gold()

    async def backpack_space_used(self) -> Optional[int]:
        """
        Player backpack used space if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_backpack_used()

    async def backpack_space_total(self) -> Optional[int]:
        """
        Player backpack total space if memory hooks are injected, otherwise raises RuntimeError
        Can also be None if the injected function hasn't been triggered yet
        """
        return await self._memory.read_player_backpack_total()
