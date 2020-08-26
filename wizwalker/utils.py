import asyncio
import ctypes
import functools
import io
import struct
import winreg
import zlib
from collections import namedtuple
from concurrent.futures.thread import ThreadPoolExecutor
from os import system as cmd
from typing import Callable, Union
from xml.etree import ElementTree
from ctypes import WinDLL
from pathlib import Path

from pymem.ptypes import RemotePointer

user32 = WinDLL("user32")
XYZ = namedtuple("XYZ", "x, y, z")


# Modified from https://github.com/Gorialis/jishaku/blob/master/jishaku/functools.py#L19
# This license covers the below function
# MIT License
#
# Copyright (c) 2020 Devon (Gorialis) R
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
def executor_function(sync_function: Callable):
    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)

        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, internal_function)

    return sync_wrapper


def get_wiz_install() -> Path:
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
            winreg.KEY_READ,
        )
    except OSError:
        raise Exception("Wizard101 install not found, do you have it installed?")

    install_location = Path(winreg.QueryValueEx(key, "InstallLocation")[0]).absolute()
    return install_location


def start_wiz(location: Union[Path, str]):
    """
    <location>Bin\WizardGraphicalClient.exe -L login.us.wizard101.com 12000
    """
    # Todo: make a non shit way to do this
    cmd(
        f'start /D "{location}\\Bin" WizardGraphicalClient.exe -L login.us.wizard101.com 12000'
    )


def quick_launch():
    location = get_wiz_install()
    start_wiz(location)


def wiz_login(window_handle: int, username: str, password: str):
    def send_chars(chars: str):
        for char in chars:
            user32.PostMessageW(window_handle, 0x102, ord(char), 0)

    send_chars(username)
    # tab
    user32.PostMessageW(window_handle, 0x102, 9, 0)
    send_chars(password)
    # enter
    user32.PostMessageW(window_handle, 0x102, 13, 0)


def resolve_pointer(handle, base, offsets):
    last = base
    for offset in offsets:
        last = RemotePointer(handle, last.value + offset)

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
        ctypes.POINTER(ctypes.c_int),  # arg2 type
    )

    # Transform callback into a form we can pass to the dll
    callback = enumwindows_func_type(callback)

    # EnumWindows takes a callback every iteration is passed to
    # and an lparam
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows
    user32.EnumWindows(callback, 0)

    return handles


def pharse_template_id_file(file_data: bytes) -> dict:
    if not file_data.startswith(b"BINd"):
        raise RuntimeError("No BINd id string")

    data = zlib.decompress(file_data[0xD:])

    total_size = len(data)
    data = io.BytesIO(data)

    data.seek(0x24)

    out = {}
    while data.tell() < total_size:
        size = ord(data.read(1)) // 2

        string = data.read(size).decode()
        data.read(8)  # unknown bytes

        # Little endian int
        entry_id = struct.unpack("<i", data.read(4))[0]

        data.read(0x10)  # next entry

        out[entry_id] = string

    return out


def pharse_message_file(file_data: bytes):
    decoded = file_data.decode(errors="ignore")
    root = ElementTree.fromstring(decoded)

    service_data = root.find("_ProtocolInfo").find("RECORD")
    service_id = int(service_data.find("ServiceID").text)
    pharsed_service_data = {
        "type": service_data.find("ProtocolType").text,
        "description": service_data.find("ProtocolDescription").text,
    }

    messages = root[1:]

    def msg_sorter(m):
        # Function to sort messages by
        return m[0].find("_MsgName").text

    parsed_msgs = {}
    for index, msg in enumerate(sorted(messages, key=msg_sorter), 1):
        # msg[0] is the RECORD element
        msg_data = msg[0]

        msg_name = msg_data.find("_MsgName").text
        msg_description = msg_data.find("_MsgDescription").text

        params = []

        for child in msg_data:
            # Message meta info starts with _
            if not child.tag.startswith("_"):
                params.append({"name": child.tag, "type": child.get("TYPE")})

        parsed_msgs[index] = {
            "name": msg_name,
            "description": msg_description,
            "params": params,
        }

    pharsed_service_data["messages"] = parsed_msgs

    return {service_id: pharsed_service_data}


def pharse_node_data(file_data: bytes) -> dict:
    """
    Converts data into a dict of node nums to points
    """
    entry_start = b"\xFE\xDB\xAE\x04"

    node_data = {}
    # no nodes
    if len(file_data) == 20:
        return node_data

    # header
    file_data = file_data[20:]

    last_start = 0
    while file_data:
        start = file_data.find(entry_start, last_start)
        if start == -1:
            break

        entry = file_data[start:start + 48 + 2]

        cords_data = entry[16:16 + (4 * 3)]
        x = struct.unpack("<f", cords_data[0:4])[0]
        y = struct.unpack("<f", cords_data[4:8])[0]
        z = struct.unpack("<f", cords_data[8:12])[0]

        node_num = entry[48:48 + 2]
        unpacked_num = struct.unpack("<H", node_num)[0]

        node_data[unpacked_num] = (x, y, z)

    return node_data
