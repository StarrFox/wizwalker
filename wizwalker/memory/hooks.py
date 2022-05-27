import asyncio
import ctypes
import ctypes.wintypes
import struct
from typing import Any, Tuple
from contextlib import suppress

from loguru import logger

from .memory_handler import MemoryHandler
from wizwalker.constants import kernel32


class MemoryHook(MemoryHandler):
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
            packed_addr = struct.pack("<Q", addr)
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
                b"\x49\x8D\x86\xFC\x0C\x00\x00"  # lea rcx,[r14+CFC]
                b"\x48\xA3" + packed_exports[0][1] +  # mov [export],rcx
                b"\x58"  # pop rcx
                b"\xF3\x41\x0F\x10\x86\xFC\x0C\x00\x00"  # original code
        )
        # fmt: on
        return bytecode


# NOTE: CombatPlanningPhaseWindow::handle
class DuelHook(SimpleHook):
    pattern = (
        rb"\x44\x0F\xB6\xE0\x88\x44\x24\x60\xE8....\x44\x8D\x6B\x0F"
        rb"\x44\x8D\x73\x10\x4C\x8D.....\x83\xF8\x64\x7E\x0A\xE8....\xE9"
    )
    exports = [("current_duel_addr", 8), ("current_duel_phase", 4)]
    instruction_length = 8
    noops = 3

    async def bytecode_generator(self, packed_exports):
        # fmt: off
        bytecode = (
                # if al == 1 rcx is ClientDuel
                b"\x84\xc0"  # test al,al
                b"\x74\x20"  # je 32 (to original code)
                b"\x50"  # push rax
                b"\x48\x89\xc8"  # mov rax,rcx
                b"\x48\xA3" + packed_exports[0][1] +  # movabs [current_duel_addr],rax
                b"\x48\x8B\x80\xC0\x00\x00\x00"  # mov rax,[rax+C0]
                b"\x48\xA3" + packed_exports[1][1] +  # movabs [current_duel_phase],rax
                b"\x58"  # pop rax
                # original code
                b"\x44\x0F\xB6\xE0"  # movzx r12d,al
                b"\x88\x44\x24\x60"  # mov [rsp+60],al
        )
        # fmt: on

        return bytecode

    async def posthook(self):
        # init duel phase with 7 so in_combat returns False
        await self.write_typed(self.current_duel_phase, 7, "unsigned int")


class ClientHook(SimpleHook):
    pattern = (
        rb"\x18\x48......\x48\x8B\x7C\x24\x40\x48\x85\xFF\x74\x29\x8B\xC6\xF0\x0F\xC1\x47\x08\x83\xF8\x01\x75\x1D"
        rb"\x48\x8B\x07\x48\x8B\xCF\xFF\x50\x08\xF0\x0F\xC1\x77\x0C"
    )
    exports = [("current_client_addr", 8)]
    instruction_length = 7
    noops = 2

    # this is because the 18 byte at the start was tacked on
    async def get_jump_address(self, pattern: bytes, module: str = None) -> int:
        """
        gets the address to write jump at
        """
        jump_address = await self.pattern_scan(pattern, module=module)
        return jump_address + 1

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


class MovementTeleportHook(SimpleHook):
    pattern = rb"\x40\x57\x48\x83\xEC\x30\x48\xC7\x44\x24\x20\xFE" \
              rb"\xFF\xFF\xFF\x48\x89\x5C\x24\x40\x48\x8B\x99\xB0" \
              rb"\x01\x00\x00\x48\x85\xDB\x74\x13\x4C\x8B\x43\x70" \
              rb"\x48\x8B\x5B\x78\x48\x85\xDB\x74\x0C\xF0\xFF\x43" \
              rb"\x08\xEB\x06\x45\x33\xC0\x41\x8B\xD8\x4D\x85\xC0\x74\x19"
    instruction_length = 6
    noops = 1
    # position vector = 12 + 1 for update bool + 8 for target object address
    exports = [("teleport_helper", 21)]

    _old_jes_bytes = None
    _old_collision_jes_bytes = None
    _collision_je_addrs = None
    _old_je_page_protection = None

    def _set_page_protection(self, address: int, protections: int, size: int = 24) -> int:
        old_protection = ctypes.wintypes.DWORD()
        target_address_passable = ctypes.c_uint64(address)

        result = kernel32.VirtualProtectEx(
            self.hook_handler.process.process_handle,
            target_address_passable,
            size,
            protections,
            ctypes.byref(old_protection),
        )

        if result == 0:
            raise RuntimeError(f"Movement teleport virtual protect returned 0 result={result}")

        return old_protection.value

    async def _wait_for_update_bool_unset_with_timeout(self):
        async def _inner():
            while True:
                should_update = await self.hook_handler.client._teleport_helper.should_update()

                if should_update is False:
                    return

                await asyncio.sleep(0.2)

        with suppress(asyncio.TimeoutError):
            return await asyncio.wait_for(_inner(), 5)

    async def prehook(self):
        jes = await self.hook_handler.client._get_je_instruction_forward_backwards()

        target_address = jes[0]

        inside_event_je_addr = await self.pattern_scan(
            rb"\x74.\xF3\x0F\x10\x55\xA8",
            module="WizardGraphicalClient.exe",
        )
        event_dispatch_je_addr = await self.pattern_scan(
            rb"\x74.\xF3\x0F\x10\x44\x24\x54\xF3\x0F",
            module="WizardGraphicalClient.exe",
        )

        old_inside_event_je_bytes = await self.read_bytes(inside_event_je_addr, 2)
        old_event_dispatch_je_addr = await self.read_bytes(event_dispatch_je_addr, 2)

        self._collision_je_addrs = (inside_event_je_addr, event_dispatch_je_addr)
        self._old_collision_jes_bytes = (old_inside_event_je_bytes, old_event_dispatch_je_addr)

        for addr in self._collision_je_addrs:
            await self.write_bytes(addr, b"\x90\x90")

        # 0x40 is read, write, execute
        self._old_je_page_protection = self._set_page_protection(target_address, 0x40)

    async def bytecode_generator(self, packed_exports):
        packed_should_update = bytearray(packed_exports[0][1])
        packed_should_update[0] += 12

        packed_z = bytearray(packed_exports[0][1])
        packed_z[0] += 8

        packed_target_addr = bytearray(packed_exports[0][1])
        packed_target_addr[0] += 13

        jes = await self.hook_handler.client._get_je_instruction_forward_backwards()

        jes_and_bytes = await self.hook_handler.read_bytes(jes[0], 8)
        jes_cmp_bytes = await self.hook_handler.read_bytes(jes[1], 8)

        self._old_jes_bytes = (jes_and_bytes, jes_cmp_bytes)

        packed_jes_and = struct.pack("<Q", jes[0])
        packed_jes_cmp = struct.pack("<Q", jes[1])

        # fmt: off
        bytecode = (
            b"\x50"  # push rax
            # b"\x48\x8B\x81\xA0\x01\x00\x00"  # mov rax,[rcx+1A0]
            # b"\x48\x85\xC0"  # test rax,rax
            b"\x48\xa1" + packed_target_addr +  # mov rax,[target_object_addr]
            b"\x48\x39\xC1"  # cmp rcx,rax
            b"\x58"  # pop rax
            b"\x0F\x84\x05\x00\x00\x00"  # je down 5 (local client object)
            b"\xE9\x6E\x00\x00\x00"  # jmp ( not local client object)
            b"\x50"  # push rax
            b"\xA0" + packed_should_update +  # mov al,[should_update_bool]
            b"\x84\xC0"  # test al,al (test if should_update is True)
            b"\x58"  # pop rax
            b"\x0F\x85\x05\x00\x00\x00"  # jne 5 (should_update is True)
            b"\xE9\x56\x00\x00\x00"  # jmp (should_update is False)
            b"\x50"  # push rax
            b"\x48\xA1" + packed_exports[0][1] +  # mov rax, [new_pos]
            b"\x48\x89\x02"  # mov[rdx], rax
            b"\xA1" + packed_z +  # mov eax, [7FF7E5541010]
            b"\x89\x42\x08"  # mov[rdx+08], eax
            b"\x48\xB8\x00\x00\x00\x00\x00\x00\x00\x00"  # mov rax,0000000000000000
            b"\xA2" + packed_should_update +  # mov [should_update_bool],al
            b"\x48\xB8" + jes_and_bytes +
            b"\x48\xA3" + packed_jes_and +
            b"\x48\xB8" + jes_cmp_bytes +
            b"\x48\xA3" + packed_jes_cmp +
            b"\x58"  # pop rax
            b"\x57"  # push rdi (original bytes)
            b"\x48\x83\xEC\x30"  # sub rsp, 30 (original bytes)
        )
        # fmt: on

        return bytecode

    async def hook(self):
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        pattern, module = await self.get_pattern()

        self.jump_address = await self.get_jump_address(pattern, module=module)
        self.hook_address = await self.get_hook_address(200)

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
        # with suppress(ExceptionalTimeout):
        #     await maybe_wait_for_value_with_timeout(
        #         self.hook_handler.client._teleport_helper.should_update,
        #         value=False,
        #         timeout=0.5,
        #     )

        # await wait_for_value(
        #     self.hook_handler.client._teleport_helper.should_update,
        #     False,
        #     ignore_errors=False,
        # )

        await self._wait_for_update_bool_unset_with_timeout()

        await super().unhook()

        if self._old_jes_bytes is None:
            return

        jes = await self.hook_handler.client._get_je_instruction_forward_backwards()

        for je, je_bytes in zip(jes, self._old_jes_bytes):
            await self.hook_handler.write_bytes(je, je_bytes)

        for addr, old_bytes in zip(self._collision_je_addrs, self._old_collision_jes_bytes):
            await self.write_bytes(addr, old_bytes)

        self._set_page_protection(jes[0], self._old_je_page_protection)


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
            addr = await self.get_address_from_symbol("user32.dll", "GetClassInfoExA")
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

    async def hook(self):
        """
        Writes jump_bytecode to jump address and hook bytecode to hook address
        """
        User32GetClassInfoBaseHook._hooked_instances += 1

        self.jump_address = await self.get_jump_address()
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

    async def posthook(self):
        bool_one_address = await self.pattern_scan(
            rb"\x00\xFF\x50\x18\x66\xC7", module="WizardGraphicalClient.exe"
        )
        bool_two_address = await self.pattern_scan(
            rb"\xC6\x86...\x00.\x33\xFF",
            module="WizardGraphicalClient.exe",
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

    async def get_jump_address(self) -> int:
        """
        gets the address to write jump at
        """
        return await self.get_address_from_symbol("user32.dll", "GetCursorPos")

    async def get_jump_bytecode(self) -> bytes:
        # distance = end - start
        distance = self.hook_address - self.jump_address
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump

    async def get_hook_bytecode(self) -> bytes:
        await self.set_mouse_pos_addr()
        packed_mouse_pos_addr = struct.pack("<Q", self.mouse_pos_addr)

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

    async def unhook(self):
        await super().unhook()
        await self.free_mouse_pos_addr()
        for bool_addr in self.toggle_bool_addrs:
            await self.write_bytes(bool_addr, b"\x00")
