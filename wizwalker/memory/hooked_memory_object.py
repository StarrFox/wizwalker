from iced_x86 import (
    Instruction,
    Code,
    Register,
    MemoryOperand,
    BlockEncoder,
    Decoder,
)

import wizwalker
from wizwalker import XYZ
from wizwalker.memory.memory_object import MemoryObject
from wizwalker.utils import maybe_wait_for_value_with_timeout
from wizwalker.memory.memory_objects import Duel, DuelPhase, ClientObject

# size of
# push rax
# mov rax,0x1122334455667788
# jmp rax
# pop rax
_HOOK_JUMP_NEEDED = 14


def add_instruction_label(label_id: int, instruction: Instruction) -> Instruction:
    instruction.ip = label_id
    return instruction


def _debug_print_disasm(machine_code: bytes, rip: int, name: str = None):
    decoder = Decoder(64, machine_code, ip=rip)

    if name:
        print(f"{name}:")

    print(" ".join(map(hex, machine_code)))

    for instr in decoder:
        print(f"{instr.ip:016X} {instr}")


class HookVariable(MemoryObject):
    def __init__(self, memory_reader: "wizwalker.memory.MemoryHandler", size: int = 8):
        super().__init__(memory_reader)
        self.size = size

        self._variable_address = None

    def __del__(self):
        if self._variable_address:
            self.process.free(self._variable_address)

    async def read_base_address(self) -> int:
        if self._variable_address:
            return self._variable_address

        self._variable_address = await self.allocate(self.size)
        return self._variable_address


class HookedMemoryObject(MemoryObject):
    _hook_is_active = False
    _hook_named_space = {}
    _hook_original_bytes = None
    _hook_hook_address = None

    HOOK_PATTERN = None
    HOOK_MODULE = None
    HOOK_ALLOCATION = 1_000

    def __del__(self):
        for address in self._hook_named_space.values():
            self.process.free(address)

    async def hook_activate(self):
        if await self.hook_is_active():
            raise RuntimeError(f"{self.__class__.__name__} is already active")

        if self.HOOK_PATTERN is None:
            raise RuntimeError(f"HOOK_PATTERN not set on {self.__class__.__name__}")

        await self.hook_pre_hook()

        jump_address = await self.pattern_scan(self.HOOK_PATTERN, module=self.HOOK_MODULE)
        original_instructions, noops = await self._hook_get_original_instructions(jump_address)

        hook_address = await self.allocate(self.HOOK_ALLOCATION)
        self._hook_hook_address = hook_address

        hook_machine_code = await self.hook_get_machine_code(hook_address, original_instructions)

        await self.write_bytes(hook_address, hook_machine_code)
        _debug_print_disasm(hook_machine_code, hook_address, "hook code")

        jump_instructions = [
            Instruction.create_reg(Code.PUSH_R64, Register.RAX),
            Instruction.create_reg_u64(
                Code.MOV_R64_IMM64,
                Register.RAX,
                hook_address,
            ),
            Instruction.create_reg(Code.JMP_RM64, Register.RAX),
            Instruction.create_reg(Code.POP_R64, Register.RAX),
        ]

        if noops:
            for _ in range(noops):
                jump_instructions.append(Instruction.create(Code.NOPD))

        encoder = BlockEncoder(64)
        encoder.add_many(jump_instructions)

        jump_machine_code = encoder.encode(jump_address)

        await self.write_bytes(jump_address, jump_machine_code)
        _debug_print_disasm(jump_machine_code, jump_address, "jump code")

        self._hook_is_active = True

        await self.hook_post_hook()

    async def hook_pre_hook(self):
        """
        Method ran before hooking process
        """
        pass

    async def hook_post_hook(self):
        """
        Method ran after hooking process
        """
        pass

    async def _hook_get_original_instructions(self, jump_address: int) -> tuple[list[Instruction], int]:
        """Returns the original instructions (they include the jump back) and the number of no ops to add"""
        position = 0
        original_instructions = []

        search_bytes = await self.read_bytes(jump_address, _HOOK_JUMP_NEEDED + 10)

        print(f"{search_bytes=}")

        decoder = Decoder(64, search_bytes, ip=jump_address)

        for instruction in decoder:
            if not instruction:
                raise RuntimeError(f"Got unknown instruction in bytes {position=} {search_bytes=}")

            original_instructions.append(instruction)
            position += instruction.len

            if position >= _HOOK_JUMP_NEEDED:
                # - 1 on position is so the pop rax is run, - (position - needed) is for the no ops
                jump_back_instructions = [
                    Instruction.create_reg_i64(
                        Code.MOV_R64_IMM64,
                        Register.RAX,
                        jump_address + position - 1 - (position - _HOOK_JUMP_NEEDED)
                    ),
                    Instruction.create_reg(Code.JMP_RM64, Register.RAX),
                ]

                noops = 0
                if position > _HOOK_JUMP_NEEDED:
                    noops = position - _HOOK_JUMP_NEEDED
                    # for _ in range(position - _HOOK_JUMP_NEEDED):
                    #     jump_back_instructions.append(Instruction.create(Code.NOPD))

                original_instructions += jump_back_instructions

                self._hook_original_bytes = (jump_address, search_bytes[:position])

                return original_instructions, noops

        raise RuntimeError("Couldn't find enough bytes for jump")

    async def hook_deactivate(self):
        if not await self.hook_is_active():
            raise RuntimeError(f"{self.__class__.__name__} is not active")

        if self._hook_original_bytes:
            jump_address, original_bytes = self._hook_original_bytes

            print(f"writing {original_bytes} to {jump_address}")
            await self.write_bytes(jump_address, original_bytes)

        if self._hook_hook_address:
            await self.free(self._hook_hook_address)

    async def hook_wait_for_ready(self, timeout: float | None = 5.0, time_between_checks: float = 0.1):
        await maybe_wait_for_value_with_timeout(
            self.read_base_address,
            time_between_checks,
            timeout=timeout,
        )

    async def hook_is_active(self):
        return self._hook_is_active

    async def hook_get_named_variable(self, name: str, size: int = 8):
        try:
            return self._hook_named_space[name]
        except KeyError:
            self._hook_named_space[name] = await self.allocate(size)
            return self._hook_named_space[name]

    async def _hook_read_named_variable(self, name: str, size: int = 8) -> int:
        quest_helper_pos = await self.hook_get_named_variable(name, size)

        res = await self.read_typed(quest_helper_pos, "unsigned long long")

        if res == 0:
            raise ValueError(f"Hook {self.__class__.__name__} is not ready yet")

        return res

    async def hook_get_machine_code(
            self,
            hook_address: int,
            original_instructions: list[Instruction]
    ) -> bytes:
        raise NotImplementedError()


class HookedQuestHelperPosition(HookedMemoryObject):
    HOOK_PATTERN = rb".........\xF3\x0F\x11\x45\xE0.........\xF3\x0F\x11\x4D\xE4.........\xF3\x0F\x11\x45\xE8\x48"
    HOOK_MODULE = "WizardGraphicalClient.exe"

    async def hook_get_machine_code(
            self,
            hook_address: int,
            original_instructions: list[Instruction]
    ) -> bytes:
        # 12 bytes for float [4] * 3 (x, y, z)
        quest_helper_pos = await self.hook_get_named_variable("quest helper pos", 12)

        instructions = [
            Instruction.create_reg(Code.PUSH_R64, Register.RAX),
            Instruction.create_reg_mem(
                Code.LEA_R64_M,
                Register.RAX,
                MemoryOperand(Register.R14, displ=0xCFC)
            ),
            Instruction.create_mem_reg(
                Code.MOV_MOFFS64_RAX,
                MemoryOperand(displ=quest_helper_pos, displ_size=8),
                Register.RAX,
            ),
            Instruction.create_reg(Code.POP_R64, Register.RAX),
        ]

        instructions += original_instructions

        encoder = BlockEncoder(64)
        encoder.add_many(instructions)

        return encoder.encode(hook_address)

    async def read_base_address(self) -> int:
        return await self._hook_read_named_variable("quest helper pos", 12)

    async def position(self) -> XYZ:
        return await self.read_xyz_from_offset(0)


# NOTE: CombatPlanningPhaseWindow::handle
class HookedDuel(HookedMemoryObject, Duel):
    HOOK_PATTERN = rb"\x41\x8B\xD5\x0F\x57\xC0\x0F\x11\x45\x94\x45\x8B\xC6\x33\xC9"
    HOOK_MODULE = "WizardGraphicalClient.exe"

    async def hook_get_machine_code(
            self,
            hook_address: int,
            original_instructions: list[Instruction]
    ) -> bytes:
        client_duel_object = await self.hook_get_named_variable("client duel object")
        # we technically only need 2 bytes, but it makes it easier to use 8
        client_duel_phase = await self.hook_get_named_variable("client duel phase")

        not_client_duel_label = 1

        instructions = [
            # r12 is a bool that on if the current duel object is the client's
            # Instruction.create_reg_reg(Code.TEST_RM32_R32, Register.R12D, Register.R12D),
            Instruction.create_reg_i32(Code.CMP_RM32_IMM8, Register.R12D, 1),
            Instruction.create_branch(Code.JNE_REL32_64, not_client_duel_label),
            # we don't need to push rax because the jump in already stores it
            Instruction.create_reg_reg(Code.MOV_R64_RM64, Register.RAX, Register.RCX),
            Instruction.create_mem_reg(
                Code.MOV_MOFFS64_RAX,
                MemoryOperand(displ=client_duel_object, displ_size=8),
                Register.RAX,
            ),
            # C0 is the offset for duel.duel_phase
            Instruction.create_reg_mem(
                Code.MOV_R64_RM64,
                Register.RAX,
                MemoryOperand(Register.RAX, displ=0xC0),
            ),
            Instruction.create_mem_reg(
                Code.MOV_MOFFS64_RAX,
                MemoryOperand(displ=client_duel_phase, displ_size=8),
                Register.RAX,
            ),
        ]

        # jump to original instructions when not the client's duel
        original_instructions[0].ip = not_client_duel_label

        instructions += original_instructions

        encoder = BlockEncoder(64)
        encoder.add_many(instructions)

        return encoder.encode(hook_address)

    async def hook_post_hook(self):
        # Init the cached duel phase to ended
        await self.write_duel_phase(DuelPhase.ended)

    async def read_base_address(self) -> int:
        return await self._hook_read_named_variable("client duel object")

    async def duel_phase(self) -> DuelPhase:
        phase = await self._hook_read_named_variable("client duel phase")
        return DuelPhase(phase)

    async def write_duel_phase(self, duel_phase: DuelPhase):
        client_duel_phase = await self.hook_get_named_variable("client duel phase")
        await self.write_enum(client_duel_phase, duel_phase)


class HookedClientObject(HookedMemoryObject, ClientObject):
    HOOK_PATTERN = rb"\x48\x8B\x18\x48\x8B\x9B\xB8\x01\x00\x00\x48\x8B\x7C\x24\x40\x48\x85\xFF\x74\x29"
    HOOK_MODULE = "WizardGraphicalClient.exe"

    async def hook_get_machine_code(
            self,
            hook_address: int,
            original_instructions: list[Instruction]
    ) -> bytes:
        client_object = await self.hook_get_named_variable("client object")

        instructions = [
            Instruction.create_reg(Code.PUSH_R64, Register.RAX),
            Instruction.create_reg_reg(Code.CMOVE_R64_RM64, Register.RAX, Register.RDI),
            Instruction.create_mem_reg(
                Code.MOV_MOFFS64_RAX,
                MemoryOperand(displ=client_object, displ_size=8),
                Register.RAX,
            ),
            Instruction.create_reg(Code.POP_R64, Register.RAX),
        ]

        instructions += original_instructions

        encoder = BlockEncoder(64)
        encoder.add_many(instructions)

        return encoder.encode(hook_address)

    async def read_base_address(self) -> int:
        return await self._hook_read_named_variable("client object")


if __name__ == "__main__":
    import asyncio

    from wizwalker import ClientHandler


    async def main():
        try:
            async with ClientHandler() as ch:
                client = ch.get_new_clients()[0]

                tested_hook = HookedClientObject(client.hook_handler)
                await tested_hook.hook_activate()
                await tested_hook.hook_wait_for_ready(None)

                for _ in range(50):
                    print(await tested_hook.location())
                    await asyncio.sleep(0.1)

                # input("pause")

        finally:
            await tested_hook.hook_deactivate()

    asyncio.run(main())
