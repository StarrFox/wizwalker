import ctypes
import ctypes.wintypes
import time

import wizwalker
from wizwalker import user32


class MouseHandler:
    """
    Handles clicking/moving the mouse position
    """

    def __init__(self, client: "wizwalker.Client"):
        self.client = client

    def activate_mouseless(self):
        """
        Activates the mouseless hook
        """
        self.client.hook_handler.activate_mouseless_cursor_hook()

    def deactivate_mouseless(self):
        """
        Deactivates the mouseless hook
        """
        self.client.hook_handler.deactivate_mouseless_cursor_hook()

    def set_mouse_position_to_window(
        self, window: "wizwalker.memory.window.DynamicWindow", **kwargs
    ):
        """
        Set the mouse position to a window
        kwargs are passed to set_mouse_position

        Args:
            window: The window to set the mouse position to
        """
        scaled_rect = window.scale_to_client()
        center = scaled_rect.center()

        self.set_mouse_position(*center, **kwargs)

    def click_window(
        self, window: "wizwalker.memory.window.DynamicWindow", **kwargs
    ):
        """
        Click a window
        kwargs are passed to .click

        Args:
            window: The window to click
        """
        scaled_rect = window.scale_to_client()
        center = scaled_rect.center()

        self.click(*center, **kwargs)

    def click_window_with_name(self, name: str, **kwargs):
        """
        Click a window with a name
        kwargs are passed to .click

        Args:
            name: The name of the window to click

        Raises:
            ValueError: If no or too many windows where found
        """
        possible_window = self.client.root_window.get_windows_with_name(name)

        if not possible_window:
            raise ValueError(f"Window with name {name} not found.")

        elif len(possible_window) > 1:
            raise ValueError(f"Multiple windows with name {name}.")

        self.click_window(possible_window[0], **kwargs)

    # TODO: add errors (HookNotActive)
    def click(
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

        # TODO: test passing use_post
        self.set_mouse_position(x, y)
        # mouse button down
        send_method(self.client.window_handle, button_down_message, 1, 0)
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        # mouse button up
        send_method(self.client.window_handle, button_down_message + 1, 0, 0)
        # move mouse outside of client area
        self.set_mouse_position(-100, -100)

    def set_mouse_position(
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

        res = self.client.hook_handler.write_mouse_position(x, y)
        # position doesn't matter here; sending mouse move
        # mouse move is here so that items are highlighted
        send_method(self.client.window_handle, 0x200, 0, 0)
        return res
