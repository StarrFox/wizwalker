from wizwalker.memory.memory_object import PropertyClass, AddressedMemoryObject


class BehaviorTemplate(PropertyClass):
    """
    Base class for behavior templates
    """

    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def behavior_name(self) -> str:
        """
        This behavior template's name
        """
        return await self.read_string_from_offset(72)

    async def write_behavior_name(self, behavior_name: str):
        """
        Write this behavior template's name

        Args:
            behavior_name: The behavior name to write
        """
        await self.write_string_to_offset(72, behavior_name)


class AddressedBehaviorTemplate(AddressedMemoryObject, BehaviorTemplate):
    """
    Dynamic behavior template that can be given an address
    """

    pass
