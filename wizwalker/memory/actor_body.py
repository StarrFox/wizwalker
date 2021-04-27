import struct

from .memory_object import MemoryObject
from wizwalker.utils import XYZ


class ActorBody(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def position(self) -> XYZ:
        base_address = await self.read_base_address()
        position_bytes = await self.read_bytes(base_address + 88, 12)
        x, y, z = struct.unpack("<fff", position_bytes)
        return XYZ(x, y, z)

    async def pitch(self) -> float:
        return await self.read_value_from_offset(100, "float")

    async def roll(self) -> float:
        return await self.read_value_from_offset(104, "float")

    async def yaw(self) -> float:
        return await self.read_value_from_offset(108, "float")

    async def height(self) -> float:
        return await self.read_value_from_offset(132, "float")

    async def scale(self) -> float:
        return await self.read_value_from_offset(112, "float")


class PlayerActorBody(ActorBody):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_player_base()
