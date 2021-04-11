import re
import struct
import ctypes
import ctypes.wintypes
from typing import Any, Tuple, Optional, Callable, Type, List

import pymem
import pymem.pattern
from pymem.ressources.structure import MODULEINFO


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("PartitionId", ctypes.wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
    ]


# Modified to not handle memory protections, use re for matching
# This licence covers the below function
# MIT License
# Copyright (c) 2018 pymem
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
def scan_pattern_page(handle: int, address: int, pattern: re.Pattern):
    mbi = MEMORY_BASIC_INFORMATION()

    ctypes.windll.kernel32.VirtualQueryEx(
        handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)
    )

    next_region = mbi.BaseAddress + mbi.RegionSize
    page_bytes = pymem.memory.read_bytes(handle, address, mbi.RegionSize)

    found = None

    match = pattern.search(page_bytes)

    if match:
        found = address + match.span()[0]

    return next_region, found


# This licence covers the below function
# MIT License
# Copyright (c) 2018 pymem
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
def pattern_scan_module(handle: int, module: MODULEINFO, pattern: re.Pattern):
    base_address = module.lpBaseOfDll
    max_address = module.lpBaseOfDll + module.SizeOfImage
    page_address = base_address

    found = None
    while page_address < max_address:
        next_page, found = scan_pattern_page(handle, page_address, pattern)

        if found:
            break

        page_address = next_page

    return found


class MemoryHook:
    def __init__(self, memory_handler):
        self.memory_handler = memory_handler
        self.jump_original_bytecode = None

        self.hook_address = None
        self.jump_address = None

        self.jump_bytecode = None
        self.hook_bytecode = None

    def get_jump_address(self, pattern: re.Pattern, *, module=None) -> int:
        """
        gets the address to write jump at
        """
        if module:
            # noinspection PyTypeChecker
            jump_address = pattern_scan_module(
                self.memory_handler.process.process_handle, module, pattern
            )

        else:
            # Todo: find faster way than scanning entire memory
            raise NotImplemented()

        return jump_address

    def get_hook_address(self, size: int) -> int:
        hook_address = self.memory_handler.process.allocate(size)
        return hook_address

    def get_jump_bytecode(self) -> bytes:
        """
        Gets the bytecode to write to the jump address
        """
        raise NotImplemented()

    def get_hook_bytecode(self) -> bytes:
        """
        Gets the bytecord to write to the hook address
        """
        raise NotImplemented()

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        raise NotImplemented()

    def hook(self) -> Any:
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, module = self.get_pattern()

        self.jump_address = self.get_jump_address(pattern, module=module)
        self.hook_address = self.get_hook_address(200)

        self.jump_bytecode = self.get_jump_bytecode()
        self.hook_bytecode = self.get_hook_bytecode()

        self.jump_original_bytecode = self.memory_handler.process.read_bytes(
            self.jump_address, len(self.jump_bytecode)
        )

        self.memory_handler.process.write_bytes(
            self.hook_address, self.hook_bytecode, len(self.hook_bytecode),
        )
        self.memory_handler.process.write_bytes(
            self.jump_address, self.jump_bytecode, len(self.jump_bytecode),
        )

    def unhook(self):
        """
        Deallocates hook memory and rewrites jump addr to it's origional code,
        also called when a client is closed
        """
        self.memory_handler.process.write_bytes(
            self.jump_address,
            self.jump_original_bytecode,
            len(self.jump_original_bytecode),
        )
        self.memory_handler.process.free(self.hook_address)


def simple_hook(
    *,
    pattern: bytes,
    module: str = "WizardGraphicalClient.exe",
    bytecode_generator: Callable,
    instruction_length: int = None,
    exports: List[Tuple],
) -> Type[MemoryHook]:
    """
    Create a simple hook from base args

    Args:
        pattern: The pattern to scan for
        module: The module to scan within (None) for all; defaults to exe
        bytecode_generator: A function that returns the bytecode to write
        instruction_length: length of instructions at jump address
        exports: list of tuples in the form (name, size)
    """

    class _memory_hook(MemoryHook):
        def __init__(self, memory_handler):
            super().__init__(memory_handler)

        def get_pattern(self):
            res_module = pymem.process.module_from_name(
                self.memory_handler.process.process_handle, module
            )
            return re.compile(pattern), res_module

        def get_jump_bytecode(self) -> bytes:
            distance = self.hook_address - self.jump_address
            relitive_jump = distance - 5
            packed_relitive_jump = struct.pack("<i", relitive_jump)
            return b"\xE9" + packed_relitive_jump + b"\x90"

        def get_hook_bytecode(self) -> bytes:
            packed_exports = []
            for export in exports:
                addr = self.memory_handler.process.allocate(export[1])
                setattr(self, export[0], addr)
                packed_addr = struct.pack("<i", addr)
                packed_exports.append((export[0], packed_addr))

            bytecode = bytecode_generator(self, packed_exports)

            if not instruction_length:
                return_addr = self.jump_address + len(self.jump_bytecode)
            else:
                return_addr = self.jump_address + instruction_length

            relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
            packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

            bytecode += b"\xE9" + packed_relitive_return_jump

            return bytecode

        def unhook(self):
            super().unhook()
            for export in exports:
                if getattr(self, export[0], None):
                    self.memory_handler.process.free(getattr(self, export[0]))

    return _memory_hook


def player_hook_bytecode_gen(_, packed_exports):
    bytecode = (
        b"\x8B\xC8"  # mov ecx,eax
        b"\x81\xC1\x2C\x03\x00\x00"  # add ecx,0000032C { 812 }
        b"\x8B\x11"  # mov edx,[ecx]
        # check if player
        b"\x83\xFA\x08"  # cmp edx,08 { 8 }
        b"\x0F\x85\x05\x00\x00\x00"  # jne 314B0036 (relative jump 5 down)
        b"\xA3" + packed_exports[0][1] +
        # original code
        b"\x8B\x48\x2C"  # mov ecx,[eax+2C]
        b"\x8B\x50\x30"  # mov edx,[eax+30]
    )
    return bytecode


PlayerHook = simple_hook(
    pattern=rb"\x8B\x48.\x8B\x50.\x8B\x40.\xEB.\xD9\x87",
    bytecode_generator=player_hook_bytecode_gen,
    exports=[("player_struct", 4)],
)

# TODO: make this one work
#  issue is je_relitive_jump = (self.jump_address + 0x6E) - (
#             self.hook_address + len(bytecode) + 6
#         )
# def player_stat_hook_bytecode_gen(hook, packed_exports):
#     tmp = hook.memory_handler.process.allocate(4)
#     packed_tmp = struct.pack("<i", tmp)
#
#     bytecode = (
#         # mov [tmp],edi
#         b"\x89\x3D" + packed_tmp + b"\x8B\xF8"  # mov edi,eax
#         b"\x89\x3D"
#         + packed_exports[0][1]  # mov [stat_addr],edi
#         + b"\x8B\x3D"
#         + packed_tmp
#         +  # mov edi,[tmp]
#         # original code
#         b"\x89\x48\x40"  # mov [eax+40],ecx
#     )
#
#     return bytecode
#
#
# PlayerStatHook = simple_hook(
#     pattern=rb"\x89\x48.\x74.\xA1",
#     bytecode_generator=player_hook_bytecode_gen,
#     exports=[("stat_addr", 4)],
# )


# TODO: switch to just lea stat_addr, eax
class PlayerStatHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.stat_addr = None

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return re.compile(rb"\x89\x48.\x74.\xA1"), module

    def set_stat_addr(self):
        self.stat_addr = self.memory_handler.process.allocate(4)

    def free_stat_addr(self):
        if self.stat_addr:
            self.memory_handler.process.free(self.stat_addr)

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    def get_hook_bytecode(self) -> bytes:
        self.set_stat_addr()
        packed_addr = struct.pack("<i", self.stat_addr)

        # registers gay
        tmp = self.memory_handler.process.allocate(4)
        packed_tmp = struct.pack("<i", tmp)

        bytecode = (
            # mov [tmp],edi
            b"\x89\x3D" + packed_tmp + b"\x8B\xF8"  # mov edi,eax
            b"\x89\x3D"
            + packed_addr  # mov [stat_addr],edi
            + b"\x8B\x3D"
            + packed_tmp
            +  # mov edi,[tmp]
            # original code
            b"\x89\x48\x40"  # mov [eax+40],ecx
        )

        # WizardGraphicalClient.exe+10060C3 + LEN(BYTECODE_LINES) - 6 (Length of this line)
        # 4 (length of target line) 1 (no idea)
        je_relitive_jump = (self.jump_address + 0x6E) - (
            self.hook_address + len(bytecode) + 6
        )
        packed_je_relitive_jump = struct.pack("<i", je_relitive_jump)

        bytecode += (
            b"\x0F\x84" + packed_je_relitive_jump
        )  # je WizardGraphicalClient.exe+10060C3

        jmp_relitive_jump = (self.jump_address + 0x5) - (
            self.hook_address + len(bytecode) + 5
        )
        packed_jmp_relitive_jump = struct.pack("<i", jmp_relitive_jump)

        bytecode += (
            b"\xE9" + packed_jmp_relitive_jump
        )  # jmp WizardGraphicalClient.exe+100605A"

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_stat_addr()


def quest_hook_bytecode_gen(_, packed_exports):
    bytecode = (
        # original code
        b"\xD9\x86\x1C\x08\x00\00"  # original instruction one
        b"\x8D\xBE\x1C\x08\x00\00"  # original instruction two
        b"\x89\x35" + packed_exports[0][1]
    )
    return bytecode


QuestHook = simple_hook(
    pattern=rb"\xD9\x86....\x8D\xBE....\xD9\x9C",
    bytecode_generator=quest_hook_bytecode_gen,
    exports=[("cord_struct", 4)],
)


def backpack_stat_bytecode_gen(hook, packed_exports):
    # TODO: rewrite to not use this
    ecx_tmp = hook.memory_handler.process.allocate(4)
    packed_ecx_tmp = struct.pack("<i", ecx_tmp)

    bytecode = (
        b"\x89\x0D"
        + packed_ecx_tmp  # mov [02A91004],ecx { (0) }
        + b"\x8B\xCE"  # mov ecx,esi
        b"\x81\xC1\x70\x03\x00\x00"  # add ecx,00000370 { 880 }
        b"\x89\x0D"
        + packed_exports[0][1]  # mov [packed_addr],ecx { (0) }
        + b"\x8B\x0D"
        + packed_ecx_tmp  # mov ecx,[02A91004] { (0) }
        +
        # original code
        b"\xC7\x86\x70\x03\x00\x00\x00\x00\x00\x00"  # mov [esi+00000370],00000000 { 0 }
    )

    return bytecode


BackpackStatHook = simple_hook(
    pattern=rb"\xC7\x86\x70\x03\x00\x00....\x74",
    bytecode_generator=backpack_stat_bytecode_gen,
    instruction_length=10,
    exports=[("backpack_struct_addr", 4)],
)


class MoveLockHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.move_lock_addr = None

    def set_move_lock_addr(self):
        self.move_lock_addr = self.memory_handler.process.allocate(4)

    def free_move_lock_addr(self):
        self.memory_handler.process.free(self.move_lock_addr)

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return (
            re.compile(rb"\xCC\x8A\x44..\x8B\x11\x88\x81"),
            module,
        )

    def get_jump_address(self, pattern: re.Pattern, *, module=None) -> int:
        """
        gets the address to write jump at
        """
        jump_address = pattern_scan_module(
            self.memory_handler.process.process_handle, module, pattern
        )

        return jump_address + 0x7

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x90"

    def get_hook_bytecode(self) -> bytes:
        self.set_move_lock_addr()
        packed_move_lock_addr = struct.pack("<i", self.move_lock_addr)

        bytecode = (
            b"\x52\x8D\x91\x08\x02\x00\x00\x89\x15"
            + packed_move_lock_addr
            + b"\x5A\x88\x81\x08\x02\x00\x00"
        )

        return_addr = self.jump_address + 6

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_move_lock_addr()


class PotionsAltHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.potions_alt_addr = None

    def set_potions_alt_addr(self):
        self.potions_alt_addr = self.memory_handler.process.allocate(4)

    def free_potions_alt_addr(self):
        self.memory_handler.process.free(self.potions_alt_addr)

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return (
            re.compile(rb"\xD9\x40.\xD9\x1E"),
            module,
        )

    def get_jump_address(self, pattern: re.Pattern, *, module=None) -> int:
        """
        gets the address to write jump at
        """
        jump_address = pattern_scan_module(
            self.memory_handler.process.process_handle, module, pattern
        )

        return jump_address

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    def get_hook_bytecode(self) -> bytes:
        self.set_potions_alt_addr()
        packed_potions_alt_addr = struct.pack("<i", self.potions_alt_addr)

        bytecode = (
            b"\x52"  # push edx
            + b"\x8B\x50\x6C"  # mov edx,[eax+0x6C]
            + b"\x89\x15"
            + packed_potions_alt_addr  # mov dword ptr [packed_potion_addr],edx
            + b"\x5A"  # pop edx
            # original code
            + b"\xD9\x40\x6C"  # fld ptr [eax+6C]
            + b"\xD9\x1E"  # fstp ptr [esi]
        )

        return_addr = self.jump_address + 5

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_potions_alt_addr()


class MouselessCursorMoveHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.x_addr = None
        self.y_addr = None

    def set_mouse_pos_addrs(self):
        self.x_addr = self.memory_handler.process.allocate(4)
        self.y_addr = self.memory_handler.process.allocate(4)

    def free_mouse_pos_addrs(self):
        self.memory_handler.process.free(self.x_addr)
        self.memory_handler.process.free(self.y_addr)

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    def get_hook_bytecode(self) -> bytes:
        self.set_mouse_pos_addrs()
        packed_xpos_addr = struct.pack("<i", self.x_addr)
        packed_ypos_addr = struct.pack("<i", self.y_addr)

        bytecode = (
            b"\x50"  # push eax
            b"\x8b\x44\x24\x08"  # mov eax, dword ptr [esp+0x8]
            b"\x51"  # push ecx
            b"\x8b\x0d"
            + packed_xpos_addr
            + b"\x89\x08"  # mov ecx, dword ptr x_addr  # mov dword ptr [eax], ecx
            b"\x8b\x0d"
            + packed_ypos_addr
            + b"\x89\x48\x04"  # mov ecx, dword ptr y_addr  # mov dword ptr [eax+0x4], ecx
            b"\x59"  # pop ecx
            b"\x58"  # pop eax
            b"\xc2\x04\x00"  # ret 0x4
        )

        return bytecode

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "user32.dll"
        )
        return (
            re.compile(rb"((\x8B\xFF\x55\x8B\xEC)|(\xE9....))\x6A\x7F\x6A\x01"),
            module,
        )

    def hook(self) -> Any:
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, module = self.get_pattern()

        self.jump_address = self.get_jump_address(pattern, module=module)
        self.hook_address = self.get_hook_address(200)

        self.jump_bytecode = self.get_jump_bytecode()
        self.hook_bytecode = self.get_hook_bytecode()

        self.jump_original_bytecode = self.memory_handler.process.read_bytes(
            self.jump_address, len(self.jump_bytecode)
        )

        self.memory_handler.process.write_bytes(
            self.hook_address, self.hook_bytecode, len(self.hook_bytecode),
        )
        self.memory_handler.process.write_bytes(
            self.jump_address, self.jump_bytecode, len(self.jump_bytecode),
        )

        # TODO: replace static address
        self.memory_handler.process.write_char(0x012E973C + 6, chr(1))

    def unhook(self):
        super().unhook()
        self.free_mouse_pos_addrs()
        self.memory_handler.process.write_char(0x012E973C + 6, chr(0))
