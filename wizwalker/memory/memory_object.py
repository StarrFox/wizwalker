import struct
from enum import Enum
from typing import Any, List, Type

from .memory_reader import MemoryReader
from .handler import HookHandler
from wizwalker.utils import XYZ
from wizwalker.errors import MemoryReadError, ReadingEnumFailed, WizWalkerMemoryError
from wizwalker.constants import type_format_dict


# # TODO: figure out what other 8 bytes are
# class SharedPointer:
#     def __init__(self, entry_bytes: bytes):
#         self.pointed_address: int = struct.unpack("<q", entry_bytes[:8])[0]


class MemoryObject(MemoryReader):
    """
    Class for any represented classes from memory
    """

    def __init__(self, hook_handler: HookHandler):
        super().__init__(hook_handler.process)
        self.hook_handler = hook_handler

    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def read_value_from_offset(self, offset: int, data_type: str) -> Any:
        base_address = await self.read_base_address()
        return await self.read_typed(base_address + offset, data_type)

    async def write_value_to_offset(self, offset: int, value: Any, data_type: str):
        base_address = await self.read_base_address()
        await self.write_typed(base_address + offset, value, data_type)

    async def read_string(
        self, offset: int, max_size: int = 20, encoding: str = "utf-8"
    ) -> str:
        base_address = await self.read_base_address()
        search_bytes = await self.read_bytes(base_address + offset, max_size)
        string_end = search_bytes.find(b"\x00")
        if string_end == 0:
            return ""
        elif string_end == -1:
            raise WizWalkerMemoryError(
                f"Couldn't read string at {base_address + offset}; no end byte."
            )
        # Don't include the 0 byte
        string_bytes = search_bytes[:string_end]
        return string_bytes.decode(encoding)

    async def write_string(self, offset: int, string: str, encoding: str = "utf-8"):
        base_address = await self.read_base_address()
        await self.write_bytes(base_address + offset, string.encode(encoding))

    async def read_vector(self, offset: int, size: int = 3, data_type: str = "float"):
        type_str = type_format_dict[data_type].replace("<", "")
        size_per_type = struct.calcsize(type_str)

        base_address = await self.read_base_address()
        vector_bytes = await self.read_bytes(
            base_address + offset, size_per_type * size
        )

        return struct.unpack("<" + type_str * size, vector_bytes)

    async def write_vector(
        self, offset: int, value: tuple, size: int = 3, data_type: str = "float"
    ):
        type_str = type_format_dict[data_type].replace("<", "")

        base_address = await self.read_base_address()
        packed_bytes = struct.pack("<" + type_str * size, *value)

        await self.write_bytes(base_address + offset, packed_bytes)

    async def read_xyz(self, offset: int) -> XYZ:
        x, y, z = await self.read_vector(offset)
        return XYZ(x, y, z)

    async def write_xyz(self, offset: int, xyz: XYZ):
        await self.write_vector(offset, (xyz.x, xyz.y, xyz.z))

    async def read_enum(self, offset, enum: Type[Enum]):
        value = await self.read_value_from_offset(offset, "int")
        try:
            res = enum(value)
        except ValueError:
            raise ReadingEnumFailed(enum, value)
        else:
            return res

    async def write_enum(self, offset, value: Enum):
        await self.write_value_to_offset(offset, value.value, "int")

    async def read_shared_vector(self, offset: int) -> List[int]:
        start_address = await self.read_value_from_offset(offset, "long long")
        end_address = await self.read_value_from_offset(offset + 8, "long long")
        size = end_address - start_address

        shared_pointers_data = await self.read_bytes(start_address, size)
        pointers = []
        data_pos = 0
        # Shared pointers are 16 in length
        for _ in range(size // 16):
            # fmt: off
            shared_pointer_data = shared_pointers_data[data_pos: data_pos + 16]
            # fmt: on

            # first 8 bytes are the address
            pointers.append(struct.unpack("<q", shared_pointer_data[:8])[0])

            data_pos += 16

        return pointers


class DynamicMemoryObject(MemoryObject):
    def __init__(self, hook_handler: HookHandler, base_address: int):
        super().__init__(hook_handler)
        self.base_address = base_address

    async def read_base_address(self) -> int:
        return self.base_address
