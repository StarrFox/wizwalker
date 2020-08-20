import struct
import threading
from collections import namedtuple
from typing import Any, Optional, Tuple

import pymem
import pymem.pattern
from pymem.ressources.structure import MODULEINFO

from .. import utils


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
                self.memory_handler.process.process_handle, module, pattern, mask
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
            self.jump_address, len(self.jump_bytecode)
        )

        # Todo: Fix this whenever pymem is updated
        # self.memory_handler.process.write_bytes(
        #     self.hook_address, self.hook_bytecode, len(self.hook_bytecode),
        # )
        # self.memory_handler.process.write_bytes(
        #     self.jump_address, self.jump_bytecode, len(self.jump_bytecode),
        # )
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.hook_address,
            self.hook_bytecode,
            len(self.hook_bytecode),
        )
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.jump_address,
            self.jump_bytecode,
            len(self.jump_bytecode),
        )

    def unhook(self):
        """
        Deallocates hook memory and rewrites jump addr to it's origional code,
        also called when a client is closed
        """
        # Todo: fix when pymem updates
        # self.memory_handler.process.write_bytes(
        #     self.jump_address,
        #     self.jump_original_bytecode,
        #     len(self.jump_original_bytecode),
        # )
        pymem.memory.write_bytes(
            self.memory_handler.process.process_handle,
            self.jump_address,
            self.jump_original_bytecode,
            len(self.jump_original_bytecode),
        )
        self.memory_handler.process.free(self.hook_address)


class PlayerHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.player_struct = None

    def get_pattern_and_mask(self) -> Tuple[bytes, Optional[str], Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return b"\x8B\x48\x2C\x8B\x50\x30\x8B\x40\x34\xEB\x2A", None, module

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

        bytecode_lines = [
            b"\x8B\xC8",  # mov ecx,eax
            b"\x81\xC1\x2C\x03\x00\x00",  # add ecx,0000032C { 812 }
            b"\x8B\x11",  # mov edx,[ecx]
            # check if player
            b"\x83\xFA\x08",  # cmp edx,08 { 8 }
            b"\x0F\x85\x05\x00\x00\x00",  # jne 314B0036 (relative jump 5 down)
            b"\xA3" + packed_addr,
            # original code
            b"\x8B\x48\x2C",  # mov ecx,[eax+2C]
            b"\x8B\x50\x30",  # mov edx,[eax+30]
        ]

        bytecode = b"".join(bytecode_lines)

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

    def get_pattern_and_mask(self) -> Tuple[bytes, Optional[str], Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return b"\x89\x48\x40\x74\x69", None, module

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

        bytecode_lines = [
            b"\x89\x3D" + packed_tmp,  # mov [02661004],edi { (472) }
            b"\x8B\xF8",  # mov edi,eax
            b"\x83\xC7\x40",  # add edi,40 { 64 }
            b"\x89\x3D" + packed_addr,  # mov [player_stats],edi { (180) }
            b"\x8B\x3D" + packed_tmp,  # mov edi,[02661004] { (472) }
            # original code
            b"\x89\x48\x40",  # mov [eax+40],ecx
        ]

        bytecode = b"".join(bytecode_lines)

        # WizardGraphicalClient.exe+10060C3 + LEN(BYTECODE_LINES) - 6 (Length of this line)
        # 4 (length of target line) 1 (no idea)
        je_relitive_jump = (self.jump_address + 0x6e) - (self.hook_address + len(bytecode) + 6)
        packed_je_relitive_jump = struct.pack("<i", je_relitive_jump)

        bytecode += b"\x0F\x84" + packed_je_relitive_jump  # je WizardGraphicalClient.exe+10060C3

        jmp_relitive_jump = (self.jump_address + 0x5) - (self.hook_address + len(bytecode) + 5)
        packed_jmp_relitive_jump = struct.pack("<i", jmp_relitive_jump)

        bytecode += b"\xE9" + packed_jmp_relitive_jump  # jmp WizardGraphicalClient.exe+100605A"

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_stat_addr()


class QuestHook(MemoryHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.cord_struct = None

    def get_pattern_and_mask(self) -> Tuple[bytes, Optional[str], Optional[MODULEINFO]]:
        module = pymem.process.module_from_name(
            self.memory_handler.process.process_handle, "WizardGraphicalClient.exe"
        )
        return b"\xD9\x86\x1C\x08\x00\x00", "xxxx??", module

    def set_cord_struct(self):
        self.cord_struct = self.memory_handler.process.allocate(4)

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

        bytecode_lines = [
            # original code
            b"\xD9\x86\x1C\x08\x00\00",  # original instruction one
            b"\x8D\xBE\x1C\x08\x00\00",  # original instruction two
            b"\x89\x35" + packed_addr,
        ]

        bytecode = b"".join(bytecode_lines)

        return_addr = self.jump_address + len(self.jump_bytecode)

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += (
            b"\xE9" + packed_relitive_return_jump
        )  # jmp WizardGraphicalClient.exe+A4BAED

        return bytecode

    def unhook(self):
        super().unhook()
        self.free_cord_struct()


class MemoryHandler:
    def __init__(self, pid: int):
        self.process = pymem.Pymem()
        self.process.open_process_from_id(pid)
        self.process.check_wow64()

        self.is_injected = False

        self.memory_thread = None
        self.player_struct_addr = None
        self.quest_struct_addr = None
        self.player_stat_addr = None

        self.hooks = []

    def __repr__(self):
        return f"<MemoryHandler {self.player_struct_addr=} {self.quest_struct_addr=} {self.memory_thread=}>"

    @utils.executor_function
    def close(self):
        """
        Closes MemoryHandler, closing all hooks and threads
        """
        for hook in self.hooks:
            hook.unhook()

    @utils.executor_function
    def read_player_base(self):
        if not self.is_injected:
            return None

        return self.process.read_int(self.player_struct_addr)

    @utils.executor_function
    def read_player_stat_base(self):
        if not self.is_injected:
            return None

        return self.process.read_int(self.player_stat_addr)

    @utils.executor_function
    def read_xyz(self):
        if not self.is_injected:
            return None

        player_struct = self.process.read_int(self.player_struct_addr)
        x = self.process.read_float(player_struct + 0x2C)
        y = self.process.read_float(player_struct + 0x30)
        z = self.process.read_float(player_struct + 0x34)

        return utils.XYZ(x, y, z)

    @utils.executor_function
    def set_xyz(self, *, x=None, y=None, z=None):
        if not self.is_injected:
            return False

        player_struct = self.process.read_int(self.player_struct_addr)
        if x:
            self.process.write_float(player_struct + 0x2C, x)
        if y:
            self.process.write_float(player_struct + 0x30, y)
        if z:
            self.process.write_float(player_struct + 0x34, z)

        return True

    @utils.executor_function
    def read_player_yaw(self):
        if not self.is_injected:
            return None

        player_struct = self.process.read_int(self.player_struct_addr)
        return self.process.read_double(player_struct + 0x3C)

    @utils.executor_function
    def set_player_yaw(self, yaw):
        if not self.is_injected:
            return False

        player_struct = self.process.read_int(self.player_struct_addr)
        self.process.write_double(player_struct + 0x3C, yaw)

        return True

    @utils.executor_function
    def read_quest_xyz(self):
        if not self.is_injected:
            return None

        quest_struct = self.process.read_int(self.quest_struct_addr)
        x = self.process.read_float(quest_struct + 0x81C)
        y = self.process.read_float(quest_struct + 0x81C + 0x4)
        z = self.process.read_float(quest_struct + 0x81C + 0x8)

        return utils.XYZ(x, y, z)

    @utils.executor_function
    def read_player_health(self):
        if not self.is_injected:
            return None

        stat_addr = self.process.read_int(self.player_stat_addr)
        return self.process.read_int(stat_addr)

    @utils.executor_function
    def read_player_mana(self):
        if not self.is_injected:
            return None

        stat_addr = self.process.read_int(self.player_stat_addr)
        return self.process.read_int(stat_addr + 0x10)

    @utils.executor_function
    def read_player_potions(self):
        if not self.is_injected:
            return None

        stat_addr = self.process.read_int(self.player_stat_addr)
        # this is a float for some reason
        return int(self.process.read_float(stat_addr + 0x2C))

    @utils.executor_function
    def read_player_gold(self):
        if not self.is_injected:
            return None

        stat_addr = self.process.read_int(self.player_stat_addr)
        return self.process.read_int(stat_addr + 0x4)

    @utils.executor_function
    def inject(self):
        self.is_injected = True

        cord_hook = PlayerHook(self)
        cord_hook.hook()
        quest_hook = QuestHook(self)
        quest_hook.hook()
        stat_hook = PlayerStatHook(self)
        stat_hook.hook()
        self.hooks.append(cord_hook)
        self.hooks.append(quest_hook)
        self.hooks.append(stat_hook)
        self.player_struct_addr = cord_hook.player_struct
        self.quest_struct_addr = quest_hook.cord_struct
        self.player_stat_addr = stat_hook.stat_addr
