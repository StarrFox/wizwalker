import struct
from enum import Enum
from typing import Any, Type

from wizwalker.errors import MemoryReadError
from .memory_handler import MemoryHandler


class MemoryObject(MemoryHandler):
    """
    Class for any represented classes from memory
    """

    def __init__(self, memory_reader: MemoryHandler, base_address: int = None):
        super().__init__(memory_reader.process)

        # sanity check
        if base_address == 0:
            raise RuntimeError(
                f"Dynamic object {type(self).__name__} passed 0 base address."
            )

        self.memory_reader = memory_reader
        self.base_address = base_address

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        if not self.base_address or other.base_address:
            return False

        return self.base_address == other.base_address

    async def find_other_instances(self, *, force_module: str = None):
        base_address = await self.read_base_address()
        vtable_bytes = await self.read_bytes(base_address, 8)

        other_instances = []

        for addr in await self.pattern_scan(
            vtable_bytes, return_multiple=True, module=force_module
        ):
            # don't include the base object
            if addr == base_address:
                continue

            other_instances.append(type(self)(self.memory_reader, addr))

        return other_instances

    async def read_base_address(self) -> int:
        # so subclasses can have dynamic base addresses
        # i.e Current* objects
        if self.base_address:
            return self.base_address

        else:
            raise TypeError("Nonetype base_address")

    async def read_value_from_offset(self, offset: int, data_type: str) -> Any:
        base_address = await self.read_base_address()
        return await self.read_typed(base_address + offset, data_type)

    async def write_value_to_offset(self, offset: int, value: Any, data_type: str):
        base_address = await self.read_base_address()
        await self.write_typed(base_address + offset, value, data_type)

    async def read_wide_string_from_offset(
        self, offset: int, encoding: str = "utf-16"
    ) -> str:
        base_address = await self.read_base_address()
        return await self.read_wide_string(base_address + offset, encoding)

    async def write_wide_string_to_offset(
        self, offset: int, string: str, encoding: str = "utf-16"
    ):
        base_address = await self.read_base_address()
        await self.write_string(base_address + offset, string, encoding)

    async def read_wchar_from_offset(self, offset: int) -> str:
        base_address = await self.read_base_address()
        return await self.read_wchar(base_address + offset)

    async def write_wchar_to_offset(self, offset: int, wchar: str):
        base_address = await self.read_base_address()
        await self.write_wchar(base_address + offset, wchar)

    async def read_string_from_offset(
        self, offset: int, encoding: str = "utf-8", *, sso_size: int = 16
    ) -> str:
        base_address = await self.read_base_address()
        return await self.read_string(
            base_address + offset, encoding, sso_size=sso_size
        )

    async def write_string_to_offset(
        self, offset: int, string: str, encoding: str = "utf-8"
    ):
        base_address = await self.read_base_address()
        await self.write_string(base_address + offset, string, encoding)

    async def read_vector_from_offset(
        self, offset: int, size: int = 3, data_type: str = "float"
    ):
        base_address = await self.read_base_address()
        return await self.read_vector(base_address + offset, size, data_type)

    async def write_vector_to_offset(
        self, offset: int, value: tuple, size: int = 3, data_type: str = "float"
    ):
        base_address = await self.read_base_address()
        await self.write_vector(base_address + offset, value, size, data_type)

    async def read_enum_from_offset(self, offset, enum: Type[Enum]):
        address = await self.read_base_address()
        return await self.read_enum(address + offset, enum)

    async def write_enum_to_offset(self, offset: int, value: Enum):
        address = await self.read_base_address()
        await self.write_enum(address + offset, value)

    async def read_shared_vector_from_offset(
        self, offset: int, *, max_size: int = 1000
    ) -> list[int]:
        address = await self.read_base_address()
        return await self.read_shared_vector(address + offset, max_size=max_size)

    async def read_dynamic_vector_from_offset(
        self, offset: int, data_type: str = "long long"
    ) -> list[int]:
        address = await self.read_base_address()
        return await self.read_dynamic_vector(address + offset, data_type)

    async def read_shared_linked_list_from_offset(self, offset: int) -> list[int]:
        address = await self.read_base_address()
        return await self.read_shared_linked_list(address + offset)

    async def read_linked_list_from_offset(self, offset: int) -> list[int]:
        address = await self.read_base_address()
        return await self.read_linked_list(address + offset)


# TODO: move this?
class PropertyClass(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # todo: remove
    async def maybe_read_type_name(self) -> str:
        try:
            return await self.read_type_name()
        except (MemoryReadError, UnicodeDecodeError):
            return ""

    async def read_type_name(self) -> str:
        vtable = await self.read_value_from_offset(0, "long long")
        # first function
        get_class_name = await self.read_typed(vtable, "long long")
        # sometimes is a function with a jmp, sometimes just a body pointer
        maybe_jmp = await self.read_bytes(get_class_name, 5)
        # 233 is 0xE9 (jmp)
        if maybe_jmp[0] == 233:
            offset = struct.unpack("<i", maybe_jmp[1:])[0]
            # 5 is length of this jmp instruction
            actual_get_class_name = get_class_name + offset + 5
        else:
            actual_get_class_name = get_class_name

        # 63 is the length of the function up to the lea instruction
        lea_instruction = actual_get_class_name + 63
        # 48 8D 0D (here)
        lea_target = actual_get_class_name + 66
        rip_offset = await self.read_typed(lea_target, "int")

        # 7 is the size of this line (rip is set at the next instruction when this one is executed)
        type_name_addr = lea_instruction + rip_offset + 7

        # some of the class names can be quite long
        # i.e ClientShadowCreatureLevelTransitionCinematicAction
        return await self.read_null_terminated_string(type_name_addr, 60)
