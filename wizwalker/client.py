import ctypes.wintypes

from .windows import KeyboardHandler, MemoryHandler, user32


class Client:
    """Represents a connected wizard client"""
    def __init__(self, window_handle: int):
        self.window_handle = window_handle
        self.process_id = self._get_pid()
        self.keyboard = KeyboardHandler(window_handle)
        self.memory = MemoryHandler(self.process_id)

    def _get_pid(self):
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
        pid = ctypes.wintypes.DWORD()
        pid_ref = ctypes.byref(pid)  # we need a pointer to the pid val's memory
        user32.GetWindowThreadProcessId(self.window_handle, pid_ref)
        return pid.value

    @property
    def xyz(self) -> tuple:
        return self.memory.x, self.memory.y, self.memory.z

    # Movement

    # def forward(self, units: int):
    #     self._keyboard.send_key("W", units)
    #
    # def backward(self, units: int):
    #     self._keyboard.send_key("S", units)
    #
    # def right(self, units: int):
    #     self._keyboard.send_key("D", units)
    #
    # def left(self, units: int):
    #     self._keyboard.send_key("A", units)
