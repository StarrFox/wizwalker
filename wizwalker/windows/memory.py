import logging
import struct
import threading
from typing import Any, Tuple, Optional

import pymem
import pymem.pattern

from pymem.ressources.structure import MODULEINFO

logger = logging.getLogger(__name__)


class MemoryHook:
    def __init__(self, memory_handler):
        self.memory_handler = memory_handler
        self.jump_original_bytecode = None

        self.hook_address = None
        self.jump_address = None

        self.jump_bytecode = None
        self.hook_bytecode = None

    def get_jump_address(self, pattern: bytes, mask: str, *, module=None) -> int:
        """
        gets the address to write jump at
        """
        if module:
            jump_address = pymem.pattern.pattern_scan_module(
                self.memory_handler.process.process_handle,
                module,
                pattern,
                mask
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

    def get_pattern_and_mask(self) -> Tuple[bytes, Optional[str], Optional[MODULEINFO]]:
        raise NotImplemented()

    def hook(self) -> Any:
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, mask, module = self.get_pattern_and_mask()

        if mask is None:
            mask = "x" * len(pattern)

        self.jump_address = self.get_jump_address(pattern, mask, module=module)
        self.hook_address = self.get_hook_address(200)

        self.jump_bytecode = self.get_jump_bytecode()
        self.hook_bytecode = self.get_hook_bytecode()

        self.jump_original_bytecode = self.memory_handler.process.read_bytes(
            self.jump_address,
            len(self.jump_bytecode)
        )

        # pymem doesnt have write_bytes on the Pymem obj, will fix later
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.hook_address,
            self.hook_bytecode,
            len(self.hook_bytecode)
        )
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.jump_address,
            self.jump_bytecode,
            len(self.jump_bytecode)
        )

        return None

    def unhook(self):
        """
        Deallocates hook memory and rewrites jump addr to it's origional code,
        also called when a client is closed
        """
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.jump_address,
            self.jump_original_bytecode,
            len(self.jump_original_bytecode)
        )
        self.memory_handler.process.free(self.hook_address)


class CordHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.cord_struct = None

    def get_pattern_and_mask(self) -> Tuple[bytes, Optional[str], Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle,
            "WizardGraphicalClient.exe"
        )
        return b"\x8B\x48\x2C\x8B\x50\x30\x8B\x40\x34\xEB\x2A", None, module

    def set_cord_struct(self):
        self.cord_struct = self.memory_handler.process.allocate(12)

    def free_cord_struct(self):
        if self.cord_struct:
            self.memory_handler.process.free(self.cord_struct)

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
        self.set_cord_struct()
        packed_addr = struct.pack("<i", self.cord_struct)  # little-endian int
        packed_addr_4 = struct.pack("<i", self.cord_struct + 0x4)
        packed_addr_8 = struct.pack("<i", self.cord_struct + 0x8)

        bytecode_lines = [
            b"\x8B\xC8",  # mov ecx,eax
            b"\x81\xC1\x2C\x03\x00\x00",  # add ecx,0000032C { 812 }
            b"\x8B\x11",  # mov edx,[ecx]
            # check if player
            b"\x83\xFA\x08",  # cmp edx,08 { 8 }
            b"\x0F\x85\x23\x00\x00\x00",  # jne 314B0036 (relitive jump 23 down)
            b"\x8B\xC8",  # mov ecx,eax
            b"\x83\xC1\x2C",  # add ecx,2C { 44 }
            b"\x8B\x11",  # mov edx,[ecx]
            # X
            b"\x89\x15" + packed_addr,  # mov [player_cords],edx { (790.40) }
            b"\x83\xC1\x04",  # add ecx,04 { 4 }
            b"\x8B\x11",  # mov edx,[ecx]
            # Y
            b"\x89\x15" + packed_addr_4,  # mov [314B0804],edx { (-15.88) }
            b"\x83\xC1\x04",  # add ecx,04 { 4 }
            b"\x8B\x11",  # mov edx,[ecx]
            # Z
            b"\x89\x15" + packed_addr_8,  # mov [314B0808],edx { (-28.79) }
            # origional code
            b"\x8B\x48\x2C",  # mov ecx,[eax+2C]
            b"\x8B\x50\x30",  # mov edx,[eax+30]
        ]

        bytecode = b"".join(bytecode_lines)

        return_addr = self.jump_address + len(self.jump_bytecode)

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump  # jmp WizardGraphicalClient.exe+A4BAED

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_cord_struct()


class CordReaderThread(threading.Thread):
    def __init__(self, memory_handler):
        super().__init__()
        self.memory_handler = memory_handler

    def run(self) -> None:
        process = self.memory_handler.process
        cord_struct = self.memory_handler.cord_struct_addr
        while True:
            self.memory_handler.x = process.read_float(cord_struct)
            self.memory_handler.y = process.read_float(cord_struct + 0x4)
            self.memory_handler.z = process.read_float(cord_struct + 0x8)


class MemoryHandler:
    def __init__(self, pid: int):
        self.process = pymem.Pymem()
        self.process.open_process_from_id(pid)
        self.process.check_wow64()

        self.cord_thread = None
        self.cord_struct_addr = None
        self.x = None
        self.y = None
        self.z = None

        self.hooks = []

    def close(self):
        """
        Closes MemoryHandler, closing all hooks and threads
        """
        for hook in self.hooks:
            hook.unhook()

    def start_cord_thread(self):
        cord_hook = CordHook(self)
        cord_hook.hook()
        self.hooks.append(cord_hook)
        self.cord_struct_addr = cord_hook.cord_struct
        self.cord_thread = CordReaderThread(self)
        self.cord_thread.start()
