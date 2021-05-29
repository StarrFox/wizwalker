import asyncio
import ctypes
import ctypes.wintypes
from contextlib import suppress
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


# TODO: remove in 2.0
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


# TODO: remove in 2.0, make sure to also remove janus requirement
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


class HotkeyListener:
    """
    Examples:
        .. code-block:: py
                import asyncio

                from wizwalker import Keycode, HotkeyListener, ModifierKeys


                async def main():
                    listener = HotkeyListener()

                    async def callback():
                        print("a was pressed; removing it")
                        listener.remove_hotkey(Keycode.A, modifiers=ModifierKeys.NOREPEAT)

                    listener.add_hotkey(Keycode.A, callback, modifiers=ModifierKeys.NOREPEAT)

                    listener.start()

                    try:
                        # your program here
                        while True:
                            await asyncio.sleep(1)

                    finally:
                        await listener.stop()


                if __name__ == "__main__":
                    asyncio.run(main())
    """

    def __init__(self, *, sleep_time: float = 0.1):
        self.sleep_time = sleep_time

        self._hotkeys = {}
        self._callbacks = {}
        self._callback_tasks = []

        self._message_loop_task = None

        self._id_counter = 1

    def start(self):
        if self._message_loop_task:
            raise ValueError("This listener has already been started")

        self._message_loop_task = asyncio.create_task(self._message_loop())

    def stop(self):
        # expected failure for hotkeys already unregistered
        for hotkey_id in range(1, self._id_counter + 1):
            user32.UnregisterHotKey(None, hotkey_id)

        with suppress(asyncio.CancelledError):
            if self._message_loop_task:
                self._message_loop_task.cancel()

            for task in self._callback_tasks:
                task.cancel()

    def add_hotkey(
        self, key: Keycode, callback: Callable, *, modifiers: ModifierKeys = 0
    ):
        if self._register_hotkey(key.value, int(modifiers)):
            # No repeat is not included in the return message
            no_norepeat = modifiers & ~ModifierKeys.NOREPEAT
            self._callbacks[key.value + no_norepeat] = callback

        else:
            raise ValueError(f"{key} with modifers {modifiers} already registered")

    def remove_hotkey(self, key: Keycode, *, modifiers: ModifierKeys = 0):
        if self._hotkeys.get(key.value + modifiers) is None:
            raise ValueError(
                f"No hotkey registered for key {key} with modifiers {modifiers}"
            )

        if not self._unregister_hotkey(key.value, int(modifiers)):
            raise ValueError(
                f"Unregistering hotkey failure for key {key} with modifiers {modifiers}"
            )

    async def _message_loop(self):
        while True:
            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagew
            message = ctypes.wintypes.MSG()
            is_message = user32.PeekMessageW(
                ctypes.byref(message), None, 0x311, 0x314, 1,
            )

            if is_message:
                modifiers = message.lParam & 0b1111111111111111
                keycode = message.lParam >> 16

                await self._handle_hotkey(keycode, modifiers)

                user32.DispatchMessageW(ctypes.byref(message))

            await asyncio.sleep(self.sleep_time)

    async def _handle_hotkey(self, keycode: int, modifiers: int):
        self._callback_tasks.append(
            asyncio.create_task(self._callbacks[keycode + modifiers]())
        )

    def _register_hotkey(self, keycode: int, modifiers: int = 0) -> bool:
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey
        res = user32.RegisterHotKey(None, self._id_counter, modifiers, keycode)

        success = res != 0

        if success:
            self._hotkeys[keycode + modifiers] = self._id_counter
            self._id_counter += 1

        return success

    def _unregister_hotkey(self, keycode: int, modifiers: int = 0):
        hotkey_id = self._hotkeys[keycode + modifiers]

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unregisterhotkey
        res = user32.UnregisterHotKey(None, hotkey_id)

        return res != 0
