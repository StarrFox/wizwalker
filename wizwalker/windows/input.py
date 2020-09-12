import asyncio
import ctypes

from .constants import keycodes

user32 = ctypes.WinDLL("user32")


class InputHandler:
    def __init__(self, window_handle):
        self.window_handle = window_handle

    async def send_key(self, key, seconds):
        code = keycodes[key]
        send_task = asyncio.create_task(self._key_send_task(code))
        await asyncio.sleep(seconds)
        send_task.cancel()
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
        user32.PostMessageW(self.window_handle, 0x101, code, 0)

    async def _key_send_task(self, code):
        while True:
            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendmessagew
            # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
            user32.PostMessageW(self.window_handle, 0x100, code, 0)
            await asyncio.sleep(0.1)

    # async def click(self, x: int, y: int):
    #     pos_lparam = y << 16 | x
    #     # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mouseactivate
    #     user32.PostMessageW(self.window_handle, 0x21, self.window_handle, 0x2010001)
    #     # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
    #     user32.PostMessageW(self.window_handle, 0x200, 0, pos_lparam)
    #     # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
    #     user32.PostMessageW(self.window_handle, 0x201, 1, pos_lparam)
    #     # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
    #     user32.PostMessageW(self.window_handle, 0x202, 0, pos_lparam)
