import ctypes
import asyncio

from .constants import keycodes

user32 = ctypes.WinDLL("user32")


class KeyboardHandler:
    def __init__(self, window_handle):
        self.window_handle = window_handle

    async def send_key(self, key, seconds):
        code = keycodes[key]
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendmessagew
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
        user32.PostMessageW(self.window_handle, 0x100, code, 0)
        # Todo: find way to continuously send keys so people can still click in the game window
        await asyncio.sleep(seconds)
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
        user32.PostMessageW(self.window_handle, 0x101, code, 0)

    async def beta_send_key(self, key, seconds):
        send_task = asyncio.create_task(self.key_send_task(key))
        await asyncio.sleep(seconds)
        send_task.cancel()

    async def key_send_task(self, key):
        while True:
            user32.PostMessageW(self.window_handle, 0x102, ord(key), 0)
            await asyncio.sleep(0.1)
