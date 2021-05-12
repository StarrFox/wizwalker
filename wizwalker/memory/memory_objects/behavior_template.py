from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject


class BehaviorTemplate(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def behavior_name(self) -> str:
        return await self.read_string_from_offset(72)

    async def write_behavior_name(self, behavior_name: str):
        await self.write_string_to_offset(72, behavior_name)


class DynamicBehaviorTemplate(DynamicMemoryObject, BehaviorTemplate):
    pass
