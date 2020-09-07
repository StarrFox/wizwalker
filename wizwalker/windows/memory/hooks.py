import re
import struct
from typing import Any, Tuple, Optional

import pymem
import pymem.pattern
from pymem.ressources.structure import MODULEINFO


# Modified to not handle memory protections and use re for matching
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
    mbi = pymem.memory.virtual_query(handle, address)
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


class PlayerHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.player_struct = None

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return re.compile(rb"\x8B\x48\x2C\x8B\x50\x30\x8B\x40\x34\xEB\x2A"), module

    def set_player_struct(self):
        self.player_struct = self.memory_handler.process.allocate(4)

    def free_player_struct(self):
        if self.player_struct:
            self.memory_handler.process.free(self.player_struct)

    def get_jump_bytecode(self) -> bytes:
        """
        INJECT                           - E9 14458E01           - jmp 02730000
        WizardGraphicalClient.exe+A4BAEC - 90                    - nop
        """
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x90"

    def get_hook_bytecode(self) -> bytes:
        self.set_player_struct()
        packed_addr = struct.pack("<i", self.player_struct)

        bytecode = (
            b"\x8B\xC8"  # mov ecx,eax
            b"\x81\xC1\x2C\x03\x00\x00"  # add ecx,0000032C { 812 }
            b"\x8B\x11"  # mov edx,[ecx]
            # check if player
            b"\x83\xFA\x08"  # cmp edx,08 { 8 }
            b"\x0F\x85\x05\x00\x00\x00"  # jne 314B0036 (relative jump 5 down)
            b"\xA3" + packed_addr +
            # original code
            b"\x8B\x48\x2C"  # mov ecx,[eax+2C]
            b"\x8B\x50\x30"  # mov edx,[eax+30]
        )

        return_addr = self.jump_address + len(self.jump_bytecode)

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += (
            b"\xE9" + packed_relitive_return_jump
        )  # jmp WizardGraphicalClient.exe+A4BAED

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_player_struct()


class PlayerStatHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.stat_addr = None

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return re.compile(rb"\x89\x48\x40\x74\x69"), module

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


class QuestHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.cord_struct = None

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return re.compile(rb"\xD9\x86\x1C\x08.."), module

    def set_cord_struct(self):
        self.cord_struct = self.memory_handler.process.allocate(4)

    def free_cord_struct(self):
        if self.cord_struct:
            self.memory_handler.process.free(self.cord_struct)

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x90"

    def get_hook_bytecode(self) -> bytes:
        self.set_cord_struct()
        packed_addr = struct.pack("<i", self.cord_struct)  # little-endian int

        bytecode = (
            # original code
            b"\xD9\x86\x1C\x08\x00\00"  # original instruction one
            b"\x8D\xBE\x1C\x08\x00\00"  # original instruction two
            b"\x89\x35" + packed_addr
        )

        return_addr = self.jump_address + len(self.jump_bytecode)

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_cord_struct()


class BackpackStatHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.backpack_struct_addr = None

    def set_backpack_struct(self):
        self.backpack_struct_addr = self.memory_handler.process.allocate(4)

    def free_backpack_struct(self):
        self.memory_handler.process.free(self.backpack_struct_addr)

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return re.compile(rb"\xC7\x86\x70\x03\x00\x00\x00\x00\x00\x00\x74"), module

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x0F\x1F\x44"

    def get_hook_bytecode(self) -> bytes:
        self.set_backpack_struct()
        packed_addr = struct.pack("<i", self.backpack_struct_addr)  # little-endian int

        ecx_tmp = self.memory_handler.process.allocate(4)
        packed_ecx_tmp = struct.pack("<i", ecx_tmp)

        bytecode = (
            b"\x89\x0D"
            + packed_ecx_tmp  # mov [02A91004],ecx { (0) }
            + b"\x8B\xCE"  # mov ecx,esi
            b"\x81\xC1\x70\x03\x00\x00"  # add ecx,00000370 { 880 }
            b"\x89\x0D"
            + packed_addr  # mov [packed_addr],ecx { (0) }
            + b"\x8B\x0D"
            + packed_ecx_tmp  # mov ecx,[02A91004] { (0) }
            +
            # original code
            b"\xC7\x86\x70\x03\x00\x00\x00\x00\x00\x00"  # mov [esi+00000370],00000000 { 0 }
        )

        # len of code at jump_address
        return_addr = self.jump_address + 10

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += (
            b"\xE9" + packed_relitive_return_jump
        )  # jmp WizardGraphicalClient.exe+43ECD5

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_backpack_struct()


class PacketHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.packet_buffer_addr = None
        self.socket_discriptor = None
        self.packet_buffer_len = None

        self.old_protection = None

    def set_packet_buffer_addr(self):
        self.packet_buffer_addr = self.memory_handler.process.allocate(4)

    def set_socket_discriptor(self):
        self.socket_discriptor = self.memory_handler.process.allocate(4)

    def set_packet_buffer_len(self):
        self.packet_buffer_len = self.memory_handler.process.allocate(4)

    def free_packet_buffer_addr(self):
        self.memory_handler.process.free(self.packet_buffer_addr)

    def free_socket_discriptor(self):
        self.memory_handler.process.free(self.socket_discriptor)

    def free_packet_buffer_len(self):
        self.memory_handler.process.free(self.packet_buffer_len)

    def get_jump_address(self, pattern: re.Pattern, *, module=None) -> int:
        """
        gets the address to write jump at
        """
        # exact location of wsock.recv + 2 which should never change
        jump_address = module.lpBaseOfDll + 0x1E32
        # I could read jump_address and compare to pattern but it's really unneeded
        return jump_address

    def get_pattern(self) -> Tuple[re.Pattern, Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WSOCK32.dll"
        )
        return (
            re.compile(rb"\x8B\xFF\x55\x8B\xEC\x83\xEC\x10\x8B\x45\x10\x89\x45\xF0"),
            module,
        )

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x90"

    def get_hook_bytecode(self) -> bytes:
        self.set_packet_buffer_addr()
        packed_buffer_addr = struct.pack("<i", self.packet_buffer_addr)

        self.set_socket_discriptor()
        packed_socket_discriptor = struct.pack("<i", self.socket_discriptor)

        self.set_packet_buffer_len()
        packed_buffer_len = struct.pack("<i", self.packet_buffer_len)

        ecx_tmp = self.memory_handler.process.allocate(4)
        packed_ecx_tmp = struct.pack("<i", ecx_tmp)

        # stack is stored here so we can restore it
        stack_buffer_tmp = self.memory_handler.process.allocate(16)
        packed_stack_buffer_tmp = struct.pack("<i", stack_buffer_tmp)
        packed_stack_buffer_tmp_4 = struct.pack("<i", stack_buffer_tmp + 0x4)
        packed_stack_buffer_tmp_8 = struct.pack("<i", stack_buffer_tmp + 0x8)
        packed_stack_buffer_tmp_12 = struct.pack("<i", stack_buffer_tmp + 0x12)

        # this is the function I'm hooking
        # int recv(
        #  SOCKET s,
        #  char * buf,
        #  int len,
        #  int flags);

        bytecode = (
            b"\x89\x0D" + packed_ecx_tmp +  # mov [ecx_tmp],ecx
            # reading args backwards (__stdcall)
            # int flags
            b"\x59"  # pop ecx
            b"\x89\x0D" + packed_stack_buffer_tmp +  # mov [stack_buffer],ecx
            # int len
            b"\x59"  # pop ecx
            b"\x89\x0D"
            + packed_stack_buffer_tmp_4  # mov [stack_buffer+4],ecx
            + b"\x89\x0D"
            + packed_buffer_len  # mov [buffer_len],ecx
            +
            # char * buf
            b"\x59"  # pop ecx
            b"\x89\x0D" + packed_stack_buffer_tmp_8 +  # mov [stack_buffer+8],ecx
            # move the buf pointer to our address
            b"\x89\x0D" + packed_buffer_addr +  # mov [buffer_addr],ecx
            # SOCKET s
            b"\x59"  # pop ecx
            b"\x89\x0D" + packed_stack_buffer_tmp_12 +  # mov [stack_buffer+12],ecx
            # move the socket descriptor to our addr
            b"\x89\x0D"
            + packed_socket_discriptor  # mov [socket_descriptor],ecx { (32768) }
            +
            # fix the stack for the rest of the recv function
            b"\x8B\x0D"
            + packed_stack_buffer_tmp_12  # mov ecx,[stack_buffer+12]
            + b"\x51"  # push ecx
            b"\x8B\x0D"
            + packed_stack_buffer_tmp_8  # mov ecx,[stack_buffer+8]
            + b"\x51"  # push ecx
            b"\x8B\x0D" + packed_stack_buffer_tmp_4 + b"\x51"  # see above
            b"\x8B\x0D" + packed_stack_buffer_tmp + b"\x51"
            b"\x8B\x0D" + packed_ecx_tmp +  # move ecx,[ecx_tmp]
            # original code
            b"\x55"  # push ebp
            b"\x8B\xEC"  # mov ebp,esp
            b"\x83\xEC\x10"  # sub esp,10
        )

        # WSOCK.recv+8 (jump_address is +2)
        return_addr = self.jump_address + 6

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_packet_buffer_addr()
        self.free_packet_buffer_len()
        self.free_socket_discriptor()
