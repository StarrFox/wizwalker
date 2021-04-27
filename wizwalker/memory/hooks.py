import re
import struct
import ctypes.wintypes
from typing import Any, Tuple, Callable, Type, List

import pymem
import pymem.pattern
import pymem.ressources.kernel32

from wizwalker import HookPatternFailed


def pack_to_int_or_longlong(num: int) -> bytes:
    try:
        return struct.pack("<i", num)
    except struct.error:
        return struct.pack("<q", num)


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


def scan_all_from(start_address: int, handle: int, pattern: bytes):
    next_region = start_address
    found = None

    while next_region < 0x7FFFFFFF0000:
        next_region, found = pymem.pattern.scan_pattern_page(
            handle, next_region, pattern
        )
        if found:
            break

    return found


class MemoryHook:
    def __init__(self, hook_handler):
        self.hook_handler = hook_handler
        self.jump_original_bytecode = None

        self.hook_address = None
        self.jump_address = None

        self.jump_bytecode = None
        self.hook_bytecode = None

        # so we can dealloc it on unhook
        self._allocated_addresses = []

    def alloc(self, size: int) -> int:
        """
        Allocate <size> bytes
        """
        addr = self.hook_handler.process.allocate(size)
        self._allocated_addresses.append(addr)
        return addr

    def prehook(self):
        """
        Called after bytecode is prepared and before written
        """
        pass

    def posthook(self):
        """
        Called after bytecode is written
        """
        pass

    def pattern_scan(self, pattern: bytes, *, module: str = None):
        if module:
            module = pymem.process.module_from_name(
                self.hook_handler.process.process_handle, module
            )
            jump_address = pymem.pattern.pattern_scan_module(
                self.hook_handler.process.process_handle, module, pattern
            )

        else:
            jump_address = scan_all_from(
                self.hook_handler.process.process_base.lpBaseOfDll,
                self.hook_handler.process.process_handle,
                pattern,
            )

        # TODO: maybe error if None?

        return jump_address

    def read_bytes(self, address: int, size: int) -> bytes:
        return self.hook_handler.process.read_bytes(address, size)

    def write_bytes(self, address: int, _bytes: bytes):
        self.hook_handler.process.write_bytes(
            address, _bytes, len(_bytes),
        )

    def get_jump_address(self, pattern: bytes, module: str = None) -> int:
        """
        gets the address to write jump at
        """
        jump_address = self.pattern_scan(pattern, module=module)

        if jump_address is None:
            raise HookPatternFailed()

        return jump_address

    def get_hook_address(self, size: int) -> int:
        return self.alloc(size)

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

    def get_pattern(self) -> Tuple[bytes, str]:
        raise NotImplemented()

    def hook(self) -> Any:
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, module = self.get_pattern()

        self.jump_address = self.get_jump_address(pattern, module=module)
        self.hook_address = self.get_hook_address(50)

        self.hook_bytecode = self.get_hook_bytecode()
        self.jump_bytecode = self.get_jump_bytecode()

        self.jump_original_bytecode = self.read_bytes(
            self.jump_address, len(self.jump_bytecode)
        )

        self.prehook()

        self.write_bytes(self.hook_address, self.hook_bytecode)
        self.write_bytes(self.jump_address, self.jump_bytecode)

        self.posthook()

    def unhook(self):
        """
        Deallocates hook memory and rewrites jump addr to it's origional code,
        also called when a client is closed
        """
        self.write_bytes(self.jump_address, self.jump_original_bytecode)
        for addr in self._allocated_addresses:
            self.hook_handler.process.free(addr)


class AutoBotBaseHook(MemoryHook):
    """
    Subclass of MemoryHook that uses an autobot function for bytes so addresses arent huge
    """

    def alloc(self, size: int) -> int:
        return self.hook_handler.get_open_autobot_address(size)

    # This if overwritten bc we never call free
    def unhook(self):
        self.write_bytes(self.jump_address, self.jump_original_bytecode)


# This is a function and not a subclass so I don't have to change anything in handler
def simple_hook(
    *,
    pattern: bytes,
    module: str = "WizardGraphicalClient.exe",
    bytecode_generator: Callable,
    instruction_length: int = 5,
    exports: List[Tuple],
    noops: int = 0,
) -> Type[MemoryHook]:
    """
    Create a simple hook from base args

    Args:
        pattern: The pattern to scan for
        module: The module to scan within (None) for all; defaults to exe
        bytecode_generator: A function that returns the bytecode to write
        instruction_length: length of instructions at jump address
        exports: list of tuples in the form (name, size)
        noops: number of noops to put at jump
    """

    class _memory_hook(AutoBotBaseHook):
        def __init__(self, memory_handler):
            super().__init__(memory_handler)

        def get_pattern(self):
            return pattern, module

        def get_jump_bytecode(self) -> bytes:
            distance = self.hook_address - self.jump_address

            relitive_jump = distance - 5
            packed_relitive_jump = struct.pack("<i", relitive_jump)

            return b"\xE9" + packed_relitive_jump + (b"\x90" * noops)

        def get_hook_bytecode(self) -> bytes:
            packed_exports = []
            for export in exports:
                # addr = self.alloc(export[1])
                addr = self.hook_handler.process.allocate(export[1])
                setattr(self, export[0], addr)
                packed_addr = pack_to_int_or_longlong(addr)
                packed_exports.append((export[0], packed_addr))

            bytecode = bytecode_generator(self, packed_exports)

            return_addr = self.jump_address + instruction_length

            relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
            packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

            bytecode += b"\xE9" + packed_relitive_return_jump

            return bytecode

        def unhook(self):
            super().unhook()
            for export in exports:
                if getattr(self, export[0], None):
                    self.hook_handler.process.free(getattr(self, export[0]))

    return _memory_hook


def player_hook_bytecode_gen(_, packed_exports):
    # We use ecx bc we want 4 bytes only
    bytecode = (
        b"\x51"  # push rcx
        b"\x8B\x88\x74\x04\x00\x00"  # mov ecx,[rax+474]
        # check if player
        b"\x83\xF9\x08"  # cmp ecx,08
        b"\x59"  # pop rcx
        b"\x0F\x85\x0A\x00\x00\x00"  # jne 10 down
        # mov(abs) [addr], rax
        b"\x48\xA3" + packed_exports[0][1] +
        # original code
        b"\xF2\x0F\x10\x40\x58"  # movsd xxmo,[rax+58]
    )
    return bytecode


PlayerHook = simple_hook(
    pattern=rb"\xF2\x0F\x10\x40\x58\xF2",
    bytecode_generator=player_hook_bytecode_gen,
    exports=[("player_struct", 8)],
)


def player_stat_hook_bytecode_gen(_, packed_exports):
    # fmt: off
    bytecode = (
        b"\x50"  # push rax
        b"\x48\x89\xC8"  # mov rax, rcx
        b"\x48\xA3" + packed_exports[0][1] +  # mov qword ptr [stat_export], rax
        b"\x58"  # pop rax
        # original code
        b"\x03\x59\x54"  # add ebx, dword ptr [rcx+0x54]
        b"\x0F\x29\x74\x24\x20"  # movaps [rsp+20],xmm6
    )
    # fmt: on
    return bytecode


PlayerStatHook = simple_hook(
    pattern=rb"\x03\x59\x54\x0F\x29\x74\x24\x20\x0F\x57\xF6\xC7\x44......\x66\x0F\x6E\xC3\x0F\x5B\xC0",
    bytecode_generator=player_stat_hook_bytecode_gen,
    instruction_length=8,
    exports=[("stat_addr", 8)],
)


def quest_hook_bytecode_gen(_, packed_exports):
    # fmt: off
    bytecode = (
        b"\x50"  # push rcx
        b"\x49\x8D\x86\xAC\x0C\x00\x00"  # lea rcx,[r14+CAC]
        b"\x48\xA3" + packed_exports[0][1] +  # mov [export],rcx
        b"\x58"  # pop rcx
        b"\xF3\x41\x0F\x10\x86\xAC\x0C\x00\x00"  # original code
    )
    # fmt: on
    return bytecode


QuestHook = simple_hook(
    pattern=rb".........\xF3\x0F\x11\x45\xE0.........\xF3\x0F\x11\x4D\xE4.........\xF3\x0F\x11\x45\xE8\x48",
    bytecode_generator=quest_hook_bytecode_gen,
    exports=[("cord_struct", 4)],
    noops=4,
)


def backpack_stat_bytecode_gen(_, packed_exports):
    # fmt: off
    bytecode = (
        b"\x50"  # push rax
        b"\x48\x8D\x83\x38\x05\x00\x00"  # lea rax,[rbx+538]
        b"\x48\xA3" + packed_exports[0][1] +  # mov [export],rax
        b"\x58"  # pop rax
        b"\x01\x83\x38\x05\x00\x00"  # original code
    )
    # fmt: on
    return bytecode


BackpackStatHook = simple_hook(
    pattern=rb"\x01............\x48\x85\xC9\x74\x0B\xE8....\x01.....\x48\x83",
    bytecode_generator=backpack_stat_bytecode_gen,
    instruction_length=6,
    exports=[("backpack_struct_addr", 8)],
    noops=1,
)


def duel_hook_bytecode_gen(_, exports):
    # fmt: off
    bytecode = (
        b"\x48\x39\xD1"  # cmp rcx,rdx
        b"\x0F\x85\x0F\x00\x00\x00"  # jne 15
        b"\x50"  # push rax
        b"\x49\x8B\x07"  # mov rax,[r15]
        b"\x48\xA3" + exports[0][1] +  # mov [current_duel],rax
        b"\x58"  # pop rax
        b"\x48\x89\x4C\x24\x50"  # original instruction
    )
    # fmt: on

    return bytecode


DuelHook = simple_hook(
    pattern=rb"\x48\x89\x4C\x24\x50\x4C\x89\x74\x24\x48",
    bytecode_generator=duel_hook_bytecode_gen,
    exports=[("current_duel_addr", 8)],
)


class User32GetClassInfoBaseHook(AutoBotBaseHook):
    """
    Subclass of MemoryHook that uses the user32.GetClassInfoExA for bytes so addresses arent huge
    """

    AUTOBOT_PATTERN = (
        rb"\x48\x89\x5C\x24\x20\x55\x56\x57\x41\x54"
        rb"\x41\x55\x41\x56\x41\x57........\x48......\x48\x8B\x05\x9A"
    )
    # rounded down
    AUTOBOT_SIZE = 1200

    _autobot_addr = None
    # How far into the function we are
    _autobot_bytes_offset = 0

    _autobot_original_bytes = None

    # this is really hacky
    _hooked_instances = 0

    def alloc(self, size: int) -> int:
        if self._autobot_addr is None:
            addr = self.pattern_scan(self.AUTOBOT_PATTERN)
            # this is so all instances have the address
            User32GetClassInfoBaseHook._autobot_addr = addr

        if self._autobot_bytes_offset + size > self.AUTOBOT_SIZE:
            raise RuntimeError("Somehow used the entirety of the autobot function")

        if self._autobot_original_bytes is None:
            User32GetClassInfoBaseHook._autobot_original_bytes = self.read_bytes(
                self._autobot_addr, self.AUTOBOT_SIZE
            )
            # this is so instructions don't collide
            self.write_bytes(self._autobot_addr, b"\x00" * self.AUTOBOT_SIZE)

        addr = self._autobot_addr + self._autobot_bytes_offset
        User32GetClassInfoBaseHook._autobot_bytes_offset += size

        return addr

    def hook(self) -> Any:
        User32GetClassInfoBaseHook._hooked_instances += 1
        return super().hook()

    def unhook(self):
        User32GetClassInfoBaseHook._hooked_instances -= 1
        self.write_bytes(self.jump_address, self.jump_original_bytecode)

        if self._hooked_instances == 0:
            self.write_bytes(self._autobot_addr, self._autobot_original_bytes)
            User32GetClassInfoBaseHook._autobot_bytes_offset = 0


class MouselessCursorMoveHook(User32GetClassInfoBaseHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.mouse_pos_addr = None

        self.toggle_bool_addrs = ()

    def posthook(self):
        bool_one_address = self.pattern_scan(
            rb"[\x00\x01]\xFF\x50\x18\x66\xC7", module="WizardGraphicalClient.exe"
        )
        bool_two_address = self.pattern_scan(
            rb"[\x00\x01]\x33\xFF\x89....\x00.....\x8D",
            module="WizardGraphicalClient.exe",
        )

        if bool_one_address is None or bool_two_address is None:
            raise RuntimeError("toogle bool address pattern failed")

        self.toggle_bool_addrs = (bool_one_address, bool_two_address)
        self.hook_handler.process.write_uchar(bool_one_address, 1)
        self.hook_handler.process.write_uchar(bool_two_address, 1)

    def set_mouse_pos_addr(self):
        self.mouse_pos_addr = self.hook_handler.process.allocate(8)

    def free_mouse_pos_addr(self):
        self.hook_handler.process.free(self.mouse_pos_addr)

    def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    def get_hook_bytecode(self) -> bytes:
        self.set_mouse_pos_addr()
        packed_mouse_pos_addr = pack_to_int_or_longlong(self.mouse_pos_addr)

        # fmt: off
        bytecode = (
            b"\x50"  # push rax
            b"\x48\xA1" + packed_mouse_pos_addr +  # mov rax, mouse_pos
            b"\x48\x89\x01"  # mov [rcx], rax
            b"\x58"  # pop rax
            b"\xC3"  # ret
        )
        # fmt: on

        return bytecode

    def get_pattern(self) -> Tuple[re.Pattern, str]:
        return (
            re.compile(rb"[\xBA\xE9]....\x44\x8D\x42\x7E\x48\xFF\x25"),
            "user32.dll",
        )

    def unhook(self):
        super().unhook()
        self.free_mouse_pos_addr()
        for bool_addr in self.toggle_bool_addrs:
            self.hook_handler.process.write_uchar(bool_addr, 0)
