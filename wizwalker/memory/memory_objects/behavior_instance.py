from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject


class BehaviorInstance(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def behavior_template_name_id(self) -> int:
        return await self.read_value_from_offset(104, "unsigned int")

    async def write_behavior_template_name_id(self, behavior_template_name_id: int):
        await self.write_value_to_offset(104, behavior_template_name_id, "unsigned int")


class DynamicBehaviorInstance(DynamicMemoryObject, BehaviorInstance):
    pass
