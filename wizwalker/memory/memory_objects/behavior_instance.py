from typing import Optional

from wizwalker.memory.memory_object import PropertyClass
from .behavior_template import BehaviorTemplate


class BehaviorInstance(PropertyClass):
    """
    Base class for behavior instances
    """
    # note: helper method
    async def behavior_name(self) -> Optional[str]:
        template = await self.behavior_template()

        if template is None:
            return None

        return await template.behavior_name()

    async def behavior_template_name_id(self) -> int:
        """
        This behavior's template name id
        """
        return await self.read_value_from_offset(104, "unsigned int")

    async def write_behavior_template_name_id(self, behavior_template_name_id: int):
        """
        Write this behavior's template name id

        Args:
            behavior_template_name_id: The behavior template name to write
        """
        await self.write_value_to_offset(104, behavior_template_name_id, "unsigned int")

    # note: hidden
    async def behavior_template(self) -> Optional[BehaviorTemplate]:
        """
        Get this behavior's template
        """
        addr = await self.read_value_from_offset(0x58, "unsigned long long")

        if not addr:
            return None

        return BehaviorTemplate(self.memory_reader, addr)
