import asyncio
import ctypes
import ctypes.wintypes
import math
import subprocess

# noinspection PyCompatibility
import winreg
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

import appdirs

from wizwalker import ExceptionalTimeout
from wizwalker.constants import Keycode, kernel32, user32, gdi32


async def async_sorted(iterable, /, *, key=None, reverse=False):
    """
    sorted but key function is awaited
    """
    if key is None:
        return sorted(iterable, reverse=reverse)

    evaluated = {}

    for item in iterable:
        evaluated[item] = await key(item)

    return [
        i[0] for i in sorted(evaluated.items(), key=lambda it: it[1], reverse=reverse)
    ]


class XYZ:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return self.distance(other)

    def __str__(self):
        return f"<XYZ ({self.x}, {self.y}, {self.z})>"

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def distance(self, other):
        """
        Calculate the distance between two points
        this does not account for z axis
        """
        if not isinstance(other, type(self)):
            raise ValueError(
                f"Can only calculate distance between instances of {type(self)} not {type(other)}"
            )

        return math.dist((self.x, self.y), (other.x, other.y))

    def yaw(self, other):
        """Calculate perfect yaw to reach another xyz"""
        if not isinstance(other, type(self)):
            raise ValueError(
                f"Can only calculate yaw between instances of {type(self)} not {type(other)}"
            )

        return calculate_perfect_yaw(self, other)

    def relative_yaw(self, *, x: float = None, y: float = None):
        """Calculate relative yaw to reach another x and/or y relative to current"""
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        other = type(self)(x, y, self.z)
        return self.yaw(other)


class Rectangle:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return f"<Rectangle ({self.x1}, {self.y1}, {self.x2}, {self.y2})>"

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter((self.x1, self.x2, self.y1, self.y2))

    def scale_to_client(self, parents: List["Rectangle"], factor: float) -> "Rectangle":
        """
        Scale this rectangle base on parents and a scale factor

        Args:
            parents: List of other rectangles
            factor: Factor to scale by

        Returns:
            The scaled rectangle
        """
        x1_sum = self.x1
        y1_sum = self.y1

        for rect in parents:
            x1_sum += rect.x1
            y1_sum += rect.y1

        converted = Rectangle(
            int(x1_sum * factor),
            int(y1_sum * factor),
            int(((self.x2 - self.x1) * factor) + (x1_sum * factor)),
            int(((self.y2 - self.y1) * factor) + (y1_sum * factor)),
        )

        return converted

    def center(self):
        """
        Get the center point of this rectangle

        Returns:
            The center point
        """
        center_x = ((self.x2 - self.x1) // 2) + self.x1
        center_y = ((self.y2 - self.y1) // 2) + self.y1

        return center_x, center_y

    def paint_on_screen(self, window_handle: int, *, rgb: tuple = (255, 0, 0)):
        """
        Paint this rectangle to the screen for debugging

        Args:
            rgb: Red, green, blue tuple to define the color of the rectangle
            window_handle: Handle to the window to paint the rectangle on
        """
        paint_struct = PAINTSTRUCT()
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdc
        device_context = user32.GetDC(window_handle)
        brush = gdi32.CreateSolidBrush(ctypes.wintypes.RGB(*rgb))

        user32.BeginPaint(window_handle, ctypes.byref(paint_struct))

        # left, top = top left corner; right, bottom = bottom right corner
        draw_rect = ctypes.wintypes.RECT()
        draw_rect.left = self.x1
        draw_rect.top = self.y1
        draw_rect.right = self.x2
        draw_rect.bottom = self.y2

        # https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createrectrgnindirect
        region = gdi32.CreateRectRgnIndirect(ctypes.byref(draw_rect))
        # https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-fillrgn
        gdi32.FillRgn(device_context, region, brush)

        user32.EndPaint(window_handle, ctypes.byref(paint_struct))
        user32.ReleaseDC(window_handle, device_context)
        gdi32.DeleteObject(brush)
        gdi32.DeleteObject(region)


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", ctypes.wintypes.HDC),
        ("fErase", ctypes.wintypes.BOOL),
        ("rcPaint", ctypes.wintypes.RECT),
        ("fRestore", ctypes.wintypes.BOOL),
        ("fIncUpdate", ctypes.wintypes.BOOL),
        ("rgbReserved", ctypes.c_char * 32),
    ]


def order_clients(clients):
    def sort_clients(client):
        rect = client.window_rectangle
        return rect.y1, rect.x1

    return sorted(clients, key=sort_clients)


# TODO: add support for all other uninstall registry locations
def get_wiz_install() -> Path:
    """
    Get the game install root dir
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{A9E27FF5-6294-46A8-B8FD-77B1DECA3021}",
            0,
            winreg.KEY_ALL_ACCESS,
        ) as key:
            install_location = Path(
                winreg.QueryValueEx(key, "InstallLocation")[0]
            ).absolute()
            return install_location
    except OSError:
        raise Exception("Wizard101 install not found.")


def start_instance():
    """
    Starts a wizard101 instance
    """
    location = get_wiz_install()
    subprocess.Popen(
        rf"{location}\Bin\WizardGraphicalClient.exe -L login.us.wizard101.com 12000",
        cwd=rf"{location}\Bin",
    )


def instance_login(window_handle: int, username: str, password: str):
    """
    Login to an instance on the login screen

    Args:
        window_handle: Handle to window
        username: Username to login with
        password: Password to login with
    """

    def send_chars(chars: str):
        for char in chars:
            user32.SendMessageW(window_handle, 0x102, ord(char), 0)

    send_chars(username)
    # tab
    user32.SendMessageW(window_handle, 0x102, 9, 0)
    send_chars(password)
    # enter
    user32.SendMessageW(window_handle, 0x102, 13, 0)


# TODO: use login window for this
# -- [LoginWindow] GameLoginWindow
# --- [title1 shadow] ControlText
# --- [loginPassword] ControlEdit
# --- [passwordText] ControlText
# --- [accountText] ControlText
# --- [okButton] ControlButton
# --- [cancelButton] ControlButton
# --- [title1] ControlText
# --- [loginName] ControlEdit
async def start_instances_with_login(instance_number: int, logins: Iterable):
    """
    Start a number of instances and login to them with logins

    Args:
        instance_number: number of instances to start
        logins: logins to use
    """
    start_handles = set(get_all_wizard_handles())

    for _ in range(instance_number):
        start_instance()

    # TODO: have way to properly check if instances are on login screen
    # waiting for instances to start
    await asyncio.sleep(7)

    new_handles = set(get_all_wizard_handles()).difference(start_handles)

    for handle, username_password in zip(new_handles, logins):
        username, password = username_password.split(":")
        instance_login(handle, username, password)


def calculate_perfect_yaw(current_xyz: XYZ, target_xyz: XYZ) -> float:
    """
    Calculates the perfect yaw to reach an xyz in a stright line

    Args:
        current_xyz: Starting position xyz
        target_xyz: Ending position xyz
    """
    target_line = math.dist(
        (current_xyz.x, current_xyz.y), (target_xyz.x, target_xyz.y)
    )
    origin_line = math.dist(
        (current_xyz.x, current_xyz.y), (current_xyz.x, current_xyz.y - 1)
    )
    target_to_origin_line = math.dist(
        (target_xyz.x, target_xyz.y), (current_xyz.x, current_xyz.y - 1)
    )
    # target_angle = math.cos(origin_line / target_line)
    target_angle = math.acos(
        (pow(target_line, 2) + pow(origin_line, 2) - pow(target_to_origin_line, 2))
        / (2 * origin_line * target_line)
    )

    if target_xyz.x > current_xyz.x:
        # outside
        target_angle_degres = math.degrees(target_angle)
        perfect_yaw = math.radians(360 - target_angle_degres)
    else:
        # inside
        perfect_yaw = target_angle

    return perfect_yaw


async def wait_for_value(
    coro, want, sleep_time: float = 0.5, *, ignore_errors: bool = True
):
    """
    Wait for a coro to return a value

    Args:
        coro: Coro to wait for
        want: Value wanted
        sleep_time: Time between calls
        ignore_errors: If errors should be ignored
    """
    while True:
        try:
            now = await coro()
            if now == want:
                return now

        except Exception as e:
            if ignore_errors:
                await asyncio.sleep(sleep_time)

            else:
                raise e


async def wait_for_non_error(coro, sleep_time: float = 0.5):
    """
    Wait for a coro to not error

    Args:
        coro: Coro to wait for
        sleep_time: Time between calls
    """
    while True:
        # noinspection PyBroadException
        try:
            now = await coro()
            return now

        except Exception:
            await asyncio.sleep(sleep_time)


async def maybe_wait_for_value_with_timeout(
    coro,
    sleep_time: float = 0.5,
    *,
    value: Any = None,
    timeout: Optional[float] = None,
    ignore_exceptions: bool = True,
    inverse_value: bool = False,
):
    possible_exception = None

    async def _inner():
        nonlocal possible_exception

        while True:
            try:
                res = await coro()
                if value is not None and inverse_value and res != value:
                    return res

                elif value is not None and not inverse_value and res == value:
                    return res

                else:
                    return res

            except Exception as e:
                if ignore_exceptions:
                    possible_exception = e
                    await asyncio.sleep(sleep_time)

                else:
                    raise e

    try:
        return await asyncio.wait_for(_inner(), timeout)
    except asyncio.TimeoutError:
        raise ExceptionalTimeout(
            f"Timed out waiting for coro {coro.__name__}", possible_exception
        )


def get_cache_folder() -> Path:
    """
    Get the wizwalker cache folder
    """
    app_name = "WizWalker"
    app_author = "StarrFox"
    cache_dir = Path(appdirs.user_cache_dir(app_name, app_author))

    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def get_logs_folder() -> Path:
    """
    Get the wizwalker log folder
    """
    app_name = "WizWalker"
    app_author = "StarrFox"
    log_dir = Path(appdirs.user_log_dir(app_name, app_author))

    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir


def get_foreground_window() -> Optional[int]:
    """
    Get the window currently in the forground

    Returns:
        Handle to the window currently in the forground
    """
    return user32.GetForegroundWindow()


def set_foreground_window(window_handle: int) -> bool:
    """
    Bring a window to the foreground

    Args:
        window_handle: Handle to the window to bring to the foreground

    Returns:
        False if the operation failed True otherwise
    """
    return user32.SetForegroundWindow(window_handle) != 0


def get_window_title(handle: int, max_size: int = 100) -> str:
    """
    Get a window's title bar text

    Args:
        handle: Handle to the window
        max_size: Max size to read

    Returns:
        The window title
    """
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowtextw
    window_title = ctypes.create_unicode_buffer(max_size)
    user32.GetWindowTextW(handle, ctypes.byref(window_title), max_size)
    return window_title.value


def set_window_title(handle: int, window_title: str):
    """
    Set a window's title bar text

    Args:
        handle: Handle to the window
        window_title: Title to write
    """
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowtextw
    user32.SetWindowTextW(handle, window_title)


def get_window_rectangle(handle: int) -> Rectangle:
    """
    Get a window's Rectangle

    Args:
        handle: Handle to the window

    Returns:
        The window's Rectangle
    """
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(handle, ctypes.byref(rect))

    # noinspection PyTypeChecker
    return Rectangle(rect.right, rect.top, rect.left, rect.bottom)


def check_if_process_running(handle: int) -> bool:
    """
    Checks if a process is still running
    True = Running
    False = Not
    """
    # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getexitcodeprocess
    exit_code = ctypes.wintypes.DWORD()
    kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
    # 259 is the value of IS_ALIVE
    return exit_code.value == 259


def get_pid_from_handle(handle: int) -> int:
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
    return pid.value


def get_all_wizard_handles() -> list:
    """
    Get handles to all currently open wizard clients
    """
    target_class = "Wizard Graphical Client"

    def callback(handle):
        class_name = ctypes.create_unicode_buffer(len(target_class))
        user32.GetClassNameW(handle, class_name, len(target_class) + 1)
        if target_class == class_name.value:
            return True

    return get_windows_from_predicate(callback)


def get_windows_from_predicate(predicate: Callable) -> list:
    """
    Get all windows that match a predicate

    Args:
        predicate: the predicate windows should pass

    Examples:
        .. code-block:: py

            def predicate(window_handle):
                if window_handle == 0:
                    # handle will be returned
                    return True
                else:
                    # handle will not be returned
                    return False
    """
    handles = []

    def callback(handle, _):
        if predicate(handle):
            handles.append(handle)

        # iterate all windows, (True)
        return 1

    enumwindows_func_type = ctypes.WINFUNCTYPE(
        ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
    )

    callback = enumwindows_func_type(callback)
    user32.EnumWindows(callback, 0)

    return handles


async def send_hotkey(window_handle: int, modifers: List[Keycode], key: Keycode):
    """
    Send a hotkey

    Args:
        window_handle: Handle to the window to send the hotkey to
        modifers: Keys to hold down
        key: The key to press
    """
    for modifier in modifers:
        user32.SendMessageW(window_handle, 0x100, modifier.value, 0)

    user32.SendMessageW(window_handle, 0x100, key.value, 0)
    user32.SendMessageW(window_handle, 0x101, key.value, 0)

    for modifier in modifers:
        user32.SendMessageW(window_handle, 0x101, modifier.value, 0)


async def timed_send_key(window_handle: int, key: Keycode, seconds: float):
    """
    Send a key for a number of seconds

    Args:
        window_handle: Handle to window to send key to
        key: The key to send
        seconds: Number of seconds to send the key
    """
    keydown_task = asyncio.create_task(_send_keydown_forever(window_handle, key))
    await asyncio.sleep(seconds)
    keydown_task.cancel()
    user32.SendMessageW(window_handle, 0x101, key.value, 0)


async def _send_keydown_forever(window_handle: int, key: Keycode):
    while True:
        user32.SendMessageW(window_handle, 0x100, key.value, 0)
        await asyncio.sleep(0.05)
