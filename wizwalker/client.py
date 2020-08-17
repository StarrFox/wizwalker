import ctypes.wintypes
from functools import cached_property
from typing import Optional

from . import utils
from .windows import KeyboardHandler, MemoryHandler, user32


class Client:
    """Represents a connected wizard client"""

    def __init__(self, window_handle: int):
        self.window_handle = window_handle
        self.keyboard = KeyboardHandler(window_handle)
        self.memory = MemoryHandler(self.process_id)

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

    async def xyz(self) -> Optional[utils.XYZ]:
        """
        Player xyz if memory hooks are injected, otherwise None
        """
        return await self.memory.read_xyz()

    async def quest_xyz(self) -> Optional[utils.XYZ]:
        """
        Quest xyz if memory hooks are injected, otherwise None
        """
        return await self.memory.read_quest_xyz
