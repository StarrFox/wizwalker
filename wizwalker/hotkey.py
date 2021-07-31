import asyncio
import ctypes
import ctypes.wintypes
from contextlib import suppress
from enum import IntFlag
from typing import Callable

from wizwalker.constants import Keycode, user32


MAX_HOTKEY_ID = 0xBFFF


class _GlobalHotkeyIdentifierManager:
    def __init__(self):
        self.hotkey_id_list = []
        self.hotkey_lock = asyncio.Lock()

    async def get_id(self) -> int:
        # so an id isn't given out twice
        async with self.hotkey_lock:
            if (id_list_len := len(self.hotkey_id_list)) == MAX_HOTKEY_ID:
                raise RuntimeError(f"Max hotkey id of {MAX_HOTKEY_ID} reached")

            # all True
            if sum(self.hotkey_id_list) == id_list_len:
                self.hotkey_id_list.append(True)
                return id_list_len + 1

            # at least one False
            else:
                index = self.hotkey_id_list.index(False)
                self.hotkey_id_list[index] = True
                return index + 1

    async def free_id(self, hotkey_id: int):
        async with self.hotkey_lock:
            self.hotkey_id_list[hotkey_id - 1] = False

            # all False
            if sum(self.hotkey_id_list) == 0:
                self.hotkey_id_list = []


_hotkey_id_manager = _GlobalHotkeyIdentifierManager()


class _GlobalHotkeyMessageLoop:
    def __init__(self):
        self.messages = []
        self.message_loop_task = None
        self.connected_instances = 0

    async def check_for_message(self, keycode: int, modifiers: int) -> bool:
        if (keycode, modifiers) in self.messages:
            self.messages.remove((keycode, modifiers))
            return True

        return False

    async def message_loop(self):
        while True:
            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagew
            message = ctypes.wintypes.MSG()
            is_message = user32.PeekMessageW(
                ctypes.byref(message), None, 0x311, 0x314, 1,
            )

            if is_message:
                # get lower 16 bits
                modifiers = message.lParam & 0b1111111111111111
                # get higher 16 bits
                keycode = message.lParam >> 16

                self.messages.append((keycode, modifiers))

                user32.DispatchMessageW(ctypes.byref(message))

            await asyncio.sleep(0.1)

    def connect(self):
        if not self.message_loop_task:
            self.message_loop_task = asyncio.create_task(self.message_loop())

        self.connected_instances += 1

    def disconnect(self):
        self.connected_instances -= 1

        if self.connected_instances == 0:
            if self.message_loop_task:
                with suppress(asyncio.CancelledError):
                    self.message_loop_task.cancel()


_hotkey_message_loop = _GlobalHotkeyMessageLoop()


class ModifierKeys(IntFlag):
    """
    Key modifiers
    """

    ALT = 0x1
    CTRL = 0x2
    NOREPEAT = 0x4000
    SHIFT = 0x4


# TODO: fix issue with non-norepeats taking up message queue
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
                        await listener.remove_hotkey(Keycode.A, modifiers=ModifierKeys.NOREPEAT)

                    await listener.add_hotkey(Keycode.A, callback, modifiers=ModifierKeys.NOREPEAT)

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

    @property
    def is_running(self) -> bool:
        """
        If this hotkey listener is running
        """
        return self._message_loop_task is not None

    async def start(self):
        """
        Start the listener
        """
        if self._message_loop_task:
            raise ValueError("This listener has already been started")

        _hotkey_message_loop.connect()

        self._message_loop_task = asyncio.create_task(self._message_loop())

        for keycode, modifiers in self._hotkeys:
            await self._register_hotkey(keycode, modifiers)

    async def stop(self):
        """
        Stop the listener
        """
        _hotkey_message_loop.disconnect()

        for hotkey_id in self._hotkeys.values():
            res = user32.UnregisterHotKey(None, hotkey_id)

            if res != 0:
                await _hotkey_id_manager.free_id(hotkey_id)

        with suppress(asyncio.CancelledError):
            if self._message_loop_task:
                self._message_loop_task.cancel()
                self._message_loop_task = None

            for task in self._callback_tasks:
                task.cancel()

    async def add_hotkey(
        self, key: Keycode, callback: Callable, *, modifiers: ModifierKeys = 0
    ):
        """
        Add a hotkey to listen for

        Args:
            key: The keycode to use
            callback: The hotkey callback
            modifiers: The hotkey modifer keys
        """
        if await self._register_hotkey(key.value, int(modifiers)):
            # No repeat is not included in the return message
            no_norepeat = modifiers & ~ModifierKeys.NOREPEAT
            self._callbacks[(key.value, no_norepeat)] = callback

        else:
            raise ValueError(f"{key} with modifers {modifiers} already registered")

    async def remove_hotkey(self, key: Keycode, *, modifiers: ModifierKeys = 0):
        """
        Remove a hotkey from this listener

        Args:
            key: The keycode of the hotkey to stop listening to
            modifiers: Modifers of the hotkey to stop listening to
        """
        if self._hotkeys.get((key.value, modifiers)) is None:
            raise ValueError(
                f"No hotkey registered for key {key} with modifiers {modifiers}"
            )

        if not await self._unregister_hotkey(key.value, int(modifiers)):
            raise ValueError(
                f"Unregistering hotkey failure for key {key} with modifiers {modifiers}"
            )

        del self._hotkeys[(key.value, modifiers)]

    # async so it isn't a breaking change later
    async def clear(self):
        """
        Remove all hotkeys from this listener
        """
        for hotkey_id in self._hotkeys.values():
            res = user32.UnregisterHotKey(None, hotkey_id)

            if res != 0:
                await _hotkey_id_manager.free_id(hotkey_id)

        self._callbacks = {}
        self._hotkeys = {}

    async def _message_loop(self):
        while True:
            for keycode, modifiers in self._callbacks.keys():
                if await _hotkey_message_loop.check_for_message(keycode, modifiers):
                    await self._handle_hotkey(keycode, modifiers)

            await asyncio.sleep(self.sleep_time)

    async def _handle_hotkey(self, keycode: int, modifiers: int):
        self._callback_tasks.append(
            asyncio.create_task(self._callbacks[(keycode, modifiers)]())
        )

    async def _register_hotkey(self, keycode: int, modifiers: int = 0) -> bool:
        hotkey_id = await _hotkey_id_manager.get_id()
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey
        res = user32.RegisterHotKey(None, hotkey_id, modifiers, keycode)

        success = res != 0

        if success:
            self._hotkeys[(keycode, modifiers)] = hotkey_id

        else:
            await _hotkey_id_manager.free_id(hotkey_id)

        return success

    async def _unregister_hotkey(self, keycode: int, modifiers: int = 0):
        hotkey_id = self._hotkeys[(keycode, modifiers)]

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unregisterhotkey
        res = user32.UnregisterHotKey(None, hotkey_id)

        success = res != 0

        if success:
            await _hotkey_id_manager.free_id(hotkey_id)

        return success
