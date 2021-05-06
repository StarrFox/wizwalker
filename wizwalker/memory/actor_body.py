from wizwalker.utils import XYZ
from .memory_object import PropertyClass


class ActorBody(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def position(self) -> XYZ:
        return await self.read_xyz(88)

    async def write_position(self, position: XYZ):
        await self.write_xyz(88, position)

    async def pitch(self) -> float:
        return await self.read_value_from_offset(100, "float")

    async def write_pitch(self, pitch: float):
        await self.write_value_to_offset(100, pitch, "float")

    async def roll(self) -> float:
        return await self.read_value_from_offset(104, "float")

    async def write_roll(self, roll: float):
        await self.write_value_to_offset(104, roll, "float")

    async def yaw(self) -> float:
        return await self.read_value_from_offset(108, "float")

    async def write_yaw(self, yaw: float):
        await self.write_value_to_offset(108, yaw, "float")

    async def height(self) -> float:
        return await self.read_value_from_offset(132, "float")

    async def write_height(self, height: float):
        await self.write_value_to_offset(132, height, "float")

    async def scale(self) -> float:
        return await self.read_value_from_offset(112, "float")

    async def write_scale(self, scale: float):
        await self.write_value_to_offset(112, scale, "float")


class CurrentActorBody(ActorBody):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_player_base()
