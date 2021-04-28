from .memory_object import MemoryObject
from wizwalker import XYZ


class CurrentQuestPosition(MemoryObject):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_quest_base()

    async def position(self) -> XYZ:
        return await self.read_xyz(0)

    async def write_position(self, position: XYZ):
        await self.write_xyz(0, position)
