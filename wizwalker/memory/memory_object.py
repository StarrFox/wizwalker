import struct
from enum import Enum
from typing import Any, Type

from .memory_reader import MemoryReader
from .handler import HookHandler
from wizwalker.utils import XYZ


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

    async def read_xyz(self, offset: int) -> XYZ:
        base_address = await self.read_base_address()
        position_bytes = await self.read_bytes(base_address + offset, 12)
        x, y, z = struct.unpack("<fff", position_bytes)
        return XYZ(x, y, z)

    async def write_xyz(self, offset: int, xyz: XYZ):
        base_address = await self.read_base_address()
        packed_position = struct.pack("<fff", *xyz)
        await self.write_bytes(base_address + offset, packed_position)

    async def read_enum(self, offset, enum: Type[Enum]):
        value = self.read_value_from_offset(offset, "int")
        # TODO: catch and raise my own error for ValueError?
        return enum(value)

    async def write_enum(self, offset, value: Enum):
        await self.write_value_to_offset(offset, value.value, "int")
