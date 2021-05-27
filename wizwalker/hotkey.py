import asyncio
import ctypes
import ctypes.wintypes
from enum import IntFlag
from typing import Callable, Union

import janus

from wizwalker import HotkeyAlreadyRegistered
from wizwalker.constants import Keycode, user32


class ModifierKeys(IntFlag):
    """
    Key modifiers
    """

    ALT = 0x1
    CTRL = 0x2
    NOREPEAT = 0x4000
    SHIFT = 0x4


# TODO: add properties to set attrs after init?
class Hotkey:
    """
    A hotkey to be listened to

    Args:
        keycode: Keycode to listen for
        callback: Coroutine to run when the key is pressed
        modifiers: Key modifiers to apply
    """

    def __init__(
        self,
        keycode: Keycode,
        callback: Callable,
        *,
        modifiers: Union[ModifierKeys, int] = 0,
    ):
        self.keycode = keycode
        self.modifiers = modifiers
        self.callback = callback


# TODO: test removing executor; add sleep_time kwarg to class or listen? default to 0.1
# TODO: add .close that unregisters hotkeys and ends tasks
class Listener:
    """
    Hotkey listener

    Args:
        hotkeys: list of Hotkeys to be listened for
        loop: The event loop to use; defaults to current

    Examples:
        .. code-block:: py

                import asyncio

                from wizwalker import Hotkey, Keycode, Listener


                async def main():
                    async def callback():
                        print("a was pressed")

                    hotkey = Hotkey(Keycode.A, callback)
                    listener = Listener(hotkey)

                    listener.listen_forever()

                    try:
                        # your program here
                        while True:
                            await asyncio.sleep(1)

                    finally:
                        await listener.close()


                if __name__ == "__main__":
                    asyncio.run(main())

    """

    def __init__(self, *hotkeys: Hotkey):
        self.ready = False

        self._loop = asyncio.get_event_loop()
        self._hotkeys = hotkeys
        self._callbacks = {}
        self._queue = None
        self._message_task = None
        self._id_counter = 1
        self._closed = False

    def listen_forever(self) -> asyncio.Task:
        """
        return a task listening to events
        """
        return asyncio.create_task(self._listen_forever_loop())

    async def _listen_forever_loop(self):
        while True:
            await self.listen()

    async def listen(self):
        """
        Listen for one event
        """
        self._queue = janus.Queue()
        if self._message_task is None:
            self._message_task = self._loop.run_in_executor(None, self._add_and_listen)

        message = await self._queue.async_q.get()
        keycode, modifiers = message.split("|")
        keycode = int(keycode)
        modifiers = int(modifiers)

        # TODO: add to self._tasks and cancel in self.close
        self._loop.create_task(self._callbacks[keycode + modifiers]())

    # async for future proofing
    async def close(self):
        self._closed = True

    def _add_and_listen(self):
        if not self.ready:
            self._add_hotkeys()
        self.ready = True

        while True:
            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagew
            message = ctypes.wintypes.MSG()
            is_message = user32.PeekMessageW(
                ctypes.byref(message), None, 0x311, 0x314, 1,
            )

            if is_message:
                modifiers = message.lParam & 0b1111111111111111
                keycode = message.lParam >> 16

                self._queue.sync_q.put(f"{keycode}|{modifiers}")

                user32.DispatchMessageW(ctypes.byref(message))

            else:
                if self._closed:
                    break

    def _add_hotkeys(self):
        for hotkey in self._hotkeys:
            if self._register_hotkey(hotkey.keycode.value, int(hotkey.modifiers)):
                # No repeat is not included in the return message
                no_norepeat = hotkey.modifiers & ~ModifierKeys.NOREPEAT
                self._callbacks[hotkey.keycode.value + no_norepeat] = hotkey.callback

            else:
                raise HotkeyAlreadyRegistered(
                    f"{hotkey.keycode} with modifers {hotkey.modifiers}"
                )

    def _register_hotkey(self, keycode: int, modifiers: int = 0) -> bool:
        res = user32.RegisterHotKey(None, self._id_counter, modifiers, keycode)
        self._id_counter += 1

        return res != 0
