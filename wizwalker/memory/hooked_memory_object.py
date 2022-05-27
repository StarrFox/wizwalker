from iced_x86 import (
    Instruction,
    Code,
    Register,
    MemoryOperand,
    BlockEncoder,
    Decoder,
)

from wizwalker import XYZ
from wizwalker.memory.memory_object import MemoryObject
from wizwalker.utils import maybe_wait_for_value_with_timeout

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


class HookedMemoryObject(MemoryObject):
    _hook_is_active = False
    _hook_named_space = {}
    _hook_original_bytes = None

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

        jump_address = await self.pattern_scan(self.HOOK_PATTERN, module=self.HOOK_MODULE)
        original_instructions = await self._hook_get_original_instructions(jump_address)

        hook_address = await self.allocate(self.HOOK_ALLOCATION)
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

        encoder = BlockEncoder(64)
        encoder.add_many(jump_instructions)

        jump_machine_code = encoder.encode(jump_address)

        await self.write_bytes(jump_address, jump_machine_code)
        _debug_print_disasm(jump_machine_code, jump_address, "jump code")

        self._hook_is_active = True

    async def _hook_get_original_instructions(self, jump_address: int) -> list[Instruction]:
        """Returns the original instructions (they include the jump back)"""
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

                if position > _HOOK_JUMP_NEEDED:
                    for _ in range(position - _HOOK_JUMP_NEEDED):
                        jump_back_instructions.append(Instruction.create(Code.NOPD))

                original_instructions += jump_back_instructions

                self._hook_original_bytes = (jump_address, search_bytes[:position])

                return original_instructions

        raise RuntimeError("Couldn't find enough bytes for jump")

    async def hook_deactivate(self):
        if not await self.hook_is_active():
            raise RuntimeError(f"{self.__class__.__name__} is not active")

        if self._hook_original_bytes:
            jump_address, original_bytes = self._hook_original_bytes

            print(f"writing {original_bytes} to {jump_address}")
            await self.write_bytes(jump_address, original_bytes)

    async def hook_wait_for_ready(self, timeout: float = 5.0, time_between_checks: float = 0.1):
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

    async def hook_get_machine_code(self, hook_address: int, original_instructions: list[Instruction]) -> bytes:
        raise NotImplementedError()


# TODO: decide if should be removed
# class HookedActorBody(HookedMemoryObject):
#     HOOK_PATTERN = rb"\xF2\x0F\x10\x40\x58\xF2"
#     HOOK_MODULE = "WizardGraphicalClient.exe"
#
#     async def hook_get_machine_code(self, hook_address: int, original_instructions: list[Instruction]) -> bytes:
#         actor_body = await self.hook_get_named_variable("actor body")
#
#         not_player_label = 1
#
#         instructions = [
#             Instruction.create_reg(Code.PUSH_R64, Register.RCX),
#             Instruction.create_reg_mem(
#                 Code.MOV_R64_RM64,
#                 Register.RCX,
#                 MemoryOperand(Register.RAX, displ=0x474)
#             ),
#             Instruction.create_reg_u32(Code.CMP_RM32_IMM8, Register.ECX, 8),
#             Instruction.create_reg(Code.POP_R64, Register.RCX),
#             Instruction.create_branch(Code.JNE_REL8_16, not_player_label),
#             # this is because our hook code pushes rax onto the stack and uses it to jump
#             Instruction.create_reg(Code.POP_R64, Register.RAX),
#             Instruction.create_mem_reg(
#                 Code.MOV_MOFFS64_RAX,
#                 MemoryOperand.ctor_u64(displ=actor_body, displ_size=8),
#                 Register.RAX,
#             ),
#             Instruction.create_reg(Code.PUSH_R64, Register.RAX)
#         ]
#
#         # this makes that branch jump here
#         original_instructions[0].ip = not_player_label
#
#         instructions += original_instructions
#
#         encoder = BlockEncoder(64)
#         encoder.add_many(instructions)
#
#         return encoder.encode(hook_address)


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
        quest_helper_pos = await self.hook_get_named_variable("quest helper pos", 12)

        res = await self.read_typed(quest_helper_pos, "unsigned long long")

        if res == 0:
            raise ValueError(f"Hook {self.__class__.__name__} is not ready yet")

        return res

    async def position(self) -> XYZ:
        return await self.read_xyz_from_offset(0)


if __name__ == "__main__":
    import asyncio

    from wizwalker import ClientHandler


    async def main():
        try:
            async with ClientHandler() as ch:
                client = ch.get_new_clients()[0]

                hooked_actor_body = HookedQuestHelperPosition(client.hook_handler)
                await hooked_actor_body.hook_activate()
                await hooked_actor_body.hook_wait_for_ready()

                for _ in range(50):
                    print(await hooked_actor_body.position())
                    await asyncio.sleep(0.1)

                # input("pause")

        finally:
            await hooked_actor_body.hook_deactivate()

    asyncio.run(main())
