import asyncio
import ctypes
import ctypes.wintypes
import struct

import wizwalker
from wizwalker import user32


class MouseHandler:
    """
    Handles clicking/moving the mouse position
    """

    def __init__(self, client: "wizwalker.Client"):
        self.client = client
        self.click_lock = None

        self._click_window_shell_code_address = None

    async def activate_mouseless(self):
        """
        Activates the mouseless hook
        """
        await self.client.hook_handler.activate_mouseless_cursor_hook()

    async def deactivate_mouseless(self):
        """
        Deactivates the mouseless hook
        """
        await self.client.hook_handler.deactivate_mouseless_cursor_hook()

    async def set_mouse_position_to_window(
        self, window: "wizwalker.memory.window.DynamicWindow", **kwargs
    ):
        """
        Set the mouse position to a window
        kwargs are passed to set_mouse_position

        Args:
            window: The window to set the mouse position to
        """
        scaled_rect = await window.scale_to_client()
        center = scaled_rect.center()

        await self.set_mouse_position(*center, **kwargs)

    async def click_window(
        self, window: "wizwalker.memory.window.DynamicWindow", **kwargs
    ):
        """
        Click a window
        kwargs are passed to .click

        Args:
            window: The window to click
        """
        await self._call_click_window_shell_code_with_window(window)

        if kwargs:
            scaled_rect = await window.scale_to_client()
            center = scaled_rect.center()

            await self.click(*center, **kwargs)

    async def click_window_with_name(self, name: str, **kwargs):
        """
        Click a window with a name
        kwargs are passed to .click

        Args:
            name: The name of the window to click

        Raises:
            ValueError: If no or too many windows where found
        """
        possible_window = await self.client.root_window.get_windows_with_name(name)

        if not possible_window:
            raise ValueError(f"Window with name {name} not found.")

        elif len(possible_window) > 1:
            raise ValueError(f"Multiple windows with name {name}.")

        await self.click_window(possible_window[0], **kwargs)

    async def _call_click_window_shell_code_with_window(self, window: "wizwalker.memory.window.DynamicWindow"):
        window_addr = await window.read_base_address()

        shell_code = await self._get_click_window_shell_code_address()
        self.client.hook_handler.process.start_thread(shell_code, window_addr)

    async def _get_click_window_shell_code_address(self) -> int:
        """
        push rcx
        push rdx
        push r8

        xor eax,eax
        xor ebx,ebx
        xor r15,r15
        xor r13,r13
        xor r12,r12
        xor r11,r11
        xor r10,r10
        xor r9,r9
        xor ebp,ebp
        xor edi,edi

        mov r8,zeroed_pos
        mov rdx,zeroed_arg2

        mov rax,window.click address
        call rax

        pop r8
        pop rdx
        pop rcx

        ret (for thread handling)
        """
        if self._click_window_shell_code_address:
            return self._click_window_shell_code_address

        zeroed_pos = await self.client.hook_handler.allocate(8)
        # zeroed_pos = 0x0000019D79254080
        # writes 0 to position (just to be sure)
        # await self.client.hook_handler.write_typed(zeroed_pos, 0, "long long")
        await self.client.hook_handler.write_typed(zeroed_pos, 10, "int")
        await self.client.hook_handler.write_typed(zeroed_pos + 4, 10, "int")
        # await self.client.hook_handler.write_typed(zeroed_pos, 0x0000019D79250CC0, "unsigned long long")

        # not sure what this argument is, it seems to always be 0 though
        zeroed_second_arg = await self.client.hook_handler.allocate(8)
        await self.client.hook_handler.write_typed(zeroed_second_arg, 0, "long long")

        packed_zeroed_pos = struct.pack("<Q", zeroed_pos)
        packed_zeroed_second_arg = struct.pack("<Q", zeroed_second_arg)

        window_click = await self.client.hook_handler.pattern_scan(
            rb"\x40\x53\x48\x83\xEC\x20\x48\x8B\x01\x48\x8B"
            rb"\xD9\x81\xA1\x9C\x00\x00\x00\xFF\xFF\xDF\xFF"
            rb"\xC6\x81\x61\x02\x00\x00\x00\xFF\x90\xB8\x01"
            rb"\x00\x00\x48\x8B\xCB\xE8",
            module="WizardGraphicalClient.exe"
        )

        packed_window_click = struct.pack("<Q", window_click)

        machine_code = (
                b"\x51\x52\x41\x50"

                b"\x31\xC0\x31\xDB\x4D\x31\xFF\x4D\x31"  # xor blob
                b"\xED\x4D\x31\xE4\x4D\x31\xDB\x4D\x31"
                b"\xD2\x4D\x31\xC9\x31\xED\x31\xFF"

                b"\x49\xB8" + packed_zeroed_pos +
                b"\x48\xBA" + packed_zeroed_second_arg +
                b"\x48\xB8" + packed_window_click +
                b"\xFF\xD0"  # call rax

                b"\x41\x58\x5A\x59"

                b"\xC3"  # ret
        )

        self._click_window_shell_code_address = await self.client.hook_handler.allocate(len(machine_code) + 10)

        await self.client.hook_handler.write_bytes(
            self._click_window_shell_code_address,
            machine_code,
        )

        return self._click_window_shell_code_address

    # TODO: add errors (HookNotActive)
    async def click(
        self,
        x: int,
        y: int,
        *,
        right_click: bool = False,
        sleep_duration: float = 0.0,
        use_post: bool = False,
    ):
        """
        Send a click to a certain x and y
        x and y positions are relative to the top left corner of the screen

        Args:
            x: x to click at
            y: y to click at
            right_click: If the click should be a right click
            sleep_duration: How long to sleep between messages
            use_post: If PostMessage should be used instead of SendMessage
        """
        # We don't have to check if the hook is active since it will just error
        if right_click:
            button_down_message = 0x204
        else:
            button_down_message = 0x201

        if use_post:
            send_method = user32.PostMessageW
        else:
            send_method = user32.SendMessageW

        # so MouseHandler can be inited in sync funcs like other __init__s
        if self.click_lock is None:
            self.click_lock = asyncio.Lock()

        # prevent multiple clicks from happening at the same time
        async with self.click_lock:
            # TODO: test passing use_post
            await self.set_mouse_position(x, y)
            # mouse button down
            send_method(self.client.window_handle, button_down_message, 1, 0)
            if sleep_duration > 0:
                await asyncio.sleep(sleep_duration)
            # mouse button up
            send_method(self.client.window_handle, button_down_message + 1, 0, 0)
            # move mouse outside of client area
            await self.set_mouse_position(-100, -100)

    async def set_mouse_position(
        self,
        x: int,
        y: int,
        *,
        convert_from_client: bool = True,
        use_post: bool = False,
    ):
        """
        Set's the mouse position to a certain x y relative to the
        top left corner of the client

        Args:
            x: x to set
            y: y to set
            convert_from_client: If the position should be converted from client to screen
            use_post: If PostMessage should be used instead of SendMessage
        """
        if use_post:
            send_method = user32.PostMessageW
        else:
            send_method = user32.SendMessageW

        if convert_from_client:
            point = ctypes.wintypes.tagPOINT(x, y)

            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-clienttoscreen
            if (
                user32.ClientToScreen(self.client.window_handle, ctypes.byref(point))
                == 0
            ):
                raise RuntimeError("Client to screen conversion failed")

            # same point structure is overwritten by ClientToScreen; these are also ints and not
            # c_longs for some reason?
            x = point.x
            y = point.y

        res = await self.client.hook_handler.write_mouse_position(x, y)
        # position doesn't matter here; sending mouse move
        # mouse move is here so that items are highlighted
        send_method(self.client.window_handle, 0x200, 0, 0)
        return res
