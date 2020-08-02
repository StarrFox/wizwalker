import ctypes
import winreg
from os import system as cmd

from pymem.ptypes import RemotePointer

from wizwalker.windows import user32


def get_wiz_install():
    r"""
    Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\
    {A9E27FF5-6294-46A8-B8FD-77B1DECA3021}

    <InstallLocation> value
    """
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    try:
        key = winreg.OpenKey(
            reg,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{A9E27FF5-6294-46A8-B8FD-77B1DECA3021}",
            0,
            winreg.KEY_READ
            )
    except OSError:
        raise Exception("Wizard101 install not found, do you have it installed?")

    install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
    return install_location


def start_wiz(location: str):
    """
    <location>Bin\WizardGraphicalClient.exe -L login.us.wizard101.com 12000
    """
    # Todo: make a non shit way to do this
    cmd(f"start /D \"{location}\\Bin\" WizardGraphicalClient.exe -L login.us.wizard101.com 12000")


def quick_launch():
    location = get_wiz_install()
    start_wiz(location)


def resolve_pointer(handle, base, offsets):
    last = base
    for offset in offsets:
        last = RemotePointer(
            handle,
            last.value + offset
        )

    return last.v.value


def get_all_wizard_handles() -> list:
    target_class = "Wizard Graphical Client"

    handles = []

    # callback takes a window handle and an lparam and returns true/false on if we should stop
    # iterating
    # https://docs.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms633498(v=vs.85)
    def callback(handle, _):
        class_name = ctypes.create_unicode_buffer(len(target_class))
        user32.GetClassNameW(handle, class_name, len(target_class) + 1)
        if target_class == class_name.value:
            handles.append(handle)

        # iterate all windows
        return False

    # https://docs.python.org/3/library/ctypes.html#callback-functions
    enumwindows_func_type = ctypes.WINFUNCTYPE(
        ctypes.c_bool,  # return type
        ctypes.c_int,  # arg1 type
        ctypes.POINTER(ctypes.c_int)  # arg2 type
    )

    # Transform callback into a form we can pass to the dll
    callback = enumwindows_func_type(callback)

    # EnumWindows takes a callback every iteration is passed to
    # and an lparam
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows
    user32.EnumWindows(callback, 0)

    return handles
