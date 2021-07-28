import struct
from typing import Any, Tuple

from loguru import logger

from .memory_reader import MemoryReader


def pack_to_int_or_longlong(num: int) -> bytes:
    try:
        return struct.pack("<i", num)
    except struct.error:
        return struct.pack("<q", num)


class MemoryHook(MemoryReader):
    def __init__(self, hook_handler):
        super().__init__(hook_handler.process)
        self.hook_handler = hook_handler
        self.jump_original_bytecode = None

        self.hook_address = None
        self.jump_address = None

        self.jump_bytecode = None
        self.hook_bytecode = None

        # so we can dealloc it on unhook
        self._allocated_addresses = []

    async def alloc(self, size: int) -> int:
        """
        Allocate <size> bytes
        """
        addr = await self.allocate(size)
        self._allocated_addresses.append(addr)
        return addr

    async def prehook(self):
        """
        Called after bytecode is prepared and before written
        """
        pass

    async def posthook(self):
        """
        Called after bytecode is written
        """
        pass

    async def get_jump_address(self, pattern: bytes, module: str = None) -> int:
        """
        gets the address to write jump at
        """
        jump_address = await self.pattern_scan(pattern, module=module)
        return jump_address

    async def get_hook_address(self, size: int) -> int:
        return await self.alloc(size)

    async def get_jump_bytecode(self) -> bytes:
        """
        Gets the bytecode to write to the jump address
        """
        raise NotImplemented()

    async def get_hook_bytecode(self) -> bytes:
        """
        Gets the bytecord to write to the hook address
        """
        raise NotImplemented()

    async def get_pattern(self) -> Tuple[bytes, str]:
        raise NotImplemented()

    async def hook(self):
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, module = await self.get_pattern()

        self.jump_address = await self.get_jump_address(pattern, module=module)
        self.hook_address = await self.get_hook_address(50)

        logger.debug(f"Got hook address {self.hook_address} in {type(self)}")
        logger.debug(f"Got jump address {self.jump_address} in {type(self)}")

        self.hook_bytecode = await self.get_hook_bytecode()
        self.jump_bytecode = await self.get_jump_bytecode()

        logger.debug(f"Got hook bytecode {self.hook_bytecode} in {type(self)}")
        logger.debug(f"Got jump bytecode {self.jump_bytecode} in {type(self)}")

        self.jump_original_bytecode = await self.read_bytes(
            self.jump_address, len(self.jump_bytecode)
        )

        logger.debug(
            f"Got jump original bytecode {self.jump_original_bytecode} in {type(self)}"
        )

        await self.prehook()

        await self.write_bytes(self.hook_address, self.hook_bytecode)
        await self.write_bytes(self.jump_address, self.jump_bytecode)

        await self.posthook()

    async def unhook(self):
        """
        Deallocates hook memory and rewrites jump addr to it's original code,
        also called when a client is closed
        """
        logger.debug(
            f"Writing original bytecode {self.jump_original_bytecode} to {self.jump_address}"
        )
        await self.write_bytes(self.jump_address, self.jump_original_bytecode)
        for addr in self._allocated_addresses:
            await self.free(addr)


class AutoBotBaseHook(MemoryHook):
    """
    Subclass of MemoryHook that uses an autobot function for bytes so addresses aren't huge
    """

    async def alloc(self, size: int) -> int:
        # noinspection PyProtectedMember
        return await self.hook_handler._allocate_autobot_bytes(size)

    # TODO: tell handler those bytes are free now?
    async def unhook(self):
        logger.debug(
            f"Writing original bytecode {self.jump_original_bytecode} to {self.jump_address}"
        )
        await self.write_bytes(self.jump_address, self.jump_original_bytecode)


class SimpleHook(AutoBotBaseHook):
    """
    Simple hook for writing hooks that are simple ofc
    """

    pattern = None
    module = "WizardGraphicalClient.exe"
    instruction_length = 5
    exports = None
    noops = 0

    async def get_pattern(self):
        return self.pattern, self.module

    async def get_jump_bytecode(self) -> bytes:
        distance = self.hook_address - self.jump_address

        relitive_jump = distance - 5
        packed_relitive_jump = struct.pack("<i", relitive_jump)

        return b"\xE9" + packed_relitive_jump + (b"\x90" * self.noops)

    async def bytecode_generator(self, packed_exports):
        raise NotImplemented()

    async def get_hook_bytecode(self) -> bytes:
        packed_exports = []
        for export in self.exports:
            # addr = self.alloc(export[1])
            addr = self.hook_handler.process.allocate(export[1])
            setattr(self, export[0], addr)
            packed_addr = pack_to_int_or_longlong(addr)
            packed_exports.append((export[0], packed_addr))

        bytecode = await self.bytecode_generator(packed_exports)

        return_addr = self.jump_address + self.instruction_length

        relitive_return_jump = return_addr - (self.hook_address + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump

        return bytecode

    async def unhook(self):
        await super().unhook()
        for export in self.exports:
            if getattr(self, export[0], None):
                await self.free(getattr(self, export[0]))


# TODO: depreciate in favor of ClientObject -> behaviors -> animationbehavior -> 0x70 (body)
class PlayerHook(SimpleHook):
    pattern = rb"\xF2\x0F\x10\x40\x58\xF2"
    exports = [("player_struct", 8)]

    async def bytecode_generator(self, packed_exports):
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


class PlayerStatHook(SimpleHook):
    pattern = rb"\x2B\xD8\xB8....\x0F\x49\xC3\x48\x83\xC4\x20\x5B\xC3"
    instruction_length = 7
    exports = [("stat_addr", 8)]
    noops = 2

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
                b"\x50"  # push rax
                b"\x48\x89\xC8"  # mov rax, rcx
                b"\x48\xA3" + packed_exports[0][1] +  # mov qword ptr [stat_export], rax
                b"\x58"  # pop rax
                # original code
                b"\x2B\xD8"  # sub ebx, eax
                b"\xB8\x00\x00\x00\x00"  # mov eax, 0
        )
        # fmt: on
        return bytecode


class QuestHook(SimpleHook):
    pattern = rb".........\xF3\x0F\x11\x45\xE0.........\xF3\x0F\x11\x4D\xE4.........\xF3\x0F\x11\x45\xE8\x48"
    exports = [("cord_struct", 4)]
    noops = 4

    async def bytecode_generator(self, packed_exports):
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


class DuelHook(SimpleHook):
    pattern = (
        rb"\x48\x89\x7C\x24\x58\x48\x89\x4C\x24\x50\x4C\x89\x7C\x24\x48\x89\x5C\x24\x40"
    )
    exports = [("current_duel_addr", 8)]

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
                b"\x48\x39\xD1"  # cmp rcx,rdx
                b"\x0F\x85\x10\x00\x00\x00"  # jne 16
                b"\x50"  # push rax
                b"\x49\x8B\x04\x24"  # mov rax,[r12]
                b"\x48\xA3" + packed_exports[0][1] +  # mov [current_duel],rax
                b"\x58"  # pop rax
                b"\x48\x89\x7C\x24\x58"  # original instruction
        )
        # fmt: on

        return bytecode


class ClientHook(SimpleHook):
    pattern = (
        rb"\x48......\x48\x8B\x7C\x24\x40\x48\x85\xFF\x74\x29\x8B\xC6\xF0\x0F\xC1\x47\x08\x83\xF8\x01\x75\x1D"
        rb"\x48\x8B\x07\x48\x8B\xCF\xFF\x50\x08\xF0\x0F\xC1\x77\x0C"
    )
    exports = [("current_client_addr", 8)]
    instruction_length = 7
    noops = 2

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
                # We use rax bc we're using movabs
                b"\x50"  # push rax
                b"\x48\x8B\xC7"  # mov rax,rdi
                b"\x48\xA3" + packed_exports[0][1] +  # mov [current_client], rax
                b"\x58"  # pop rax
                b"\x48\x8B\x9B\xB8\x01\x00\x00"  # original instruction
        )
        # fmt: on

        return bytecode


class RootWindowHook(SimpleHook):
    pattern = rb".......\x48\x8B\x01.......\xFF\x50\x70\x84"
    instruction_length = 7
    noops = 2
    exports = [("current_root_window_addr", 8)]

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
            b"\x50"  # push rax
            b"\x49\x8B\x87\xD8\x00\x00\x00"  # mov rax,[r15+D8]
            b"\x48\xA3" + packed_exports[0][1] +  # mov [current_root_window_addr], rax
            b"\x58"  # pop rax
            b"\x49\x8B\x8F\xD8\x00\x00\x00"  # original instruction
        )
        # fmt: on

        return bytecode


class RenderContextHook(SimpleHook):
    pattern = rb"..................\xF3\x41\x0F\x10\x28\xF3\x0F\x10\x56\x04\x48\x63\xC1"
    instruction_length = 9
    noops = 4
    exports = [("current_render_context_addr", 8)]

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
            b"\x50"  # push rax
            b"\x48\x89\xd8"  # mov rax,rbx
            b"\x48\xA3" + packed_exports[0][1] +  # mov [current_ui_scale_addr],rax
            b"\x58"  # pop rax
            b"\xF3\x44\x0F\x10\x8B\x98\x00\x00\x00"  # original instruction
        )
        # fmt: on

        return bytecode


# TODO: fix this hacky class
class User32GetClassInfoBaseHook(AutoBotBaseHook):
    """
    Subclass of MemoryHook that uses the user32.GetClassInfoExA for bytes so addresses arent huge
    """

    AUTOBOT_PATTERN = (
        rb"\x48\x89\x5C\x24\x20\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57........"
        rb"\x48......\x48\x8B\x05.+\x48\x33\xC4.+\x48\x8B\xDA\x4C"
    )
    # rounded down
    AUTOBOT_SIZE = 1200

    _autobot_addr = None
    # How far into the function we are
    _autobot_bytes_offset = 0

    _autobot_original_bytes = None

    # this is really hacky
    _hooked_instances = 0

    async def alloc(self, size: int) -> int:
        if self._autobot_addr is None:
            addr = await self.pattern_scan(self.AUTOBOT_PATTERN, module="user32.dll")
            # this is so all instances have the address
            User32GetClassInfoBaseHook._autobot_addr = addr

        if self._autobot_bytes_offset + size > self.AUTOBOT_SIZE:
            raise RuntimeError(
                "Somehow used the entirety of the GetClassInfoExA function"
            )

        if self._autobot_original_bytes is None:
            User32GetClassInfoBaseHook._autobot_original_bytes = await self.read_bytes(
                self._autobot_addr, self.AUTOBOT_SIZE
            )
            # this is so instructions don't collide
            await self.write_bytes(self._autobot_addr, b"\x00" * self.AUTOBOT_SIZE)

        addr = self._autobot_addr + self._autobot_bytes_offset
        User32GetClassInfoBaseHook._autobot_bytes_offset += size

        return addr

    async def hook(self) -> Any:
        User32GetClassInfoBaseHook._hooked_instances += 1
        return await super().hook()

    async def unhook(self):
        User32GetClassInfoBaseHook._hooked_instances -= 1
        await self.write_bytes(self.jump_address, self.jump_original_bytecode)

        if self._hooked_instances == 0:
            await self.write_bytes(self._autobot_addr, self._autobot_original_bytes)
            User32GetClassInfoBaseHook._autobot_bytes_offset = 0


class MouselessCursorMoveHook(User32GetClassInfoBaseHook):
    def __init__(self, memory_handler):
        super().__init__(memory_handler)
        self.mouse_pos_addr = None

        self.toggle_bool_addrs = ()

    async def posthook(self):
        bool_one_address = await self.pattern_scan(
            rb"\x00\xFF\x50\x18\x66\xC7", module="WizardGraphicalClient.exe"
        )
        bool_two_address = await self.pattern_scan(
            rb"\xC6\x86...\x00.\x33\xFF", module="WizardGraphicalClient.exe",
        )

        if bool_one_address is None or bool_two_address is None:
            raise RuntimeError("toogle bool address pattern failed")

        # bool is 6 away from pattern target
        bool_two_address += 6

        self.toggle_bool_addrs = (bool_one_address, bool_two_address)

        await self.write_bytes(bool_one_address, b"\x01")
        await self.write_bytes(bool_two_address, b"\x01")

    async def set_mouse_pos_addr(self):
        self.mouse_pos_addr = await self.allocate(8)

    async def free_mouse_pos_addr(self):
        await self.free(self.mouse_pos_addr)

    async def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    async def get_hook_bytecode(self) -> bytes:
        await self.set_mouse_pos_addr()
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

    async def get_pattern(self) -> Tuple[bytes, str]:
        # other processes love hooking this function
        return rb"[\xBA\xE9]....[\x44\x41][\x8D\xB8]..(..)?\x48\xFF\x25", "user32.dll"

    async def unhook(self):
        await super().unhook()
        await self.free_mouse_pos_addr()
        for bool_addr in self.toggle_bool_addrs:
            await self.write_bytes(bool_addr, b"\x00")
