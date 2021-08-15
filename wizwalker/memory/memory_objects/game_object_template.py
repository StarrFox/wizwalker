from typing import List

from wizwalker.memory.memory_object import PropertyClass
from .enums import ObjectType
from .behavior_template import AddressedBehaviorTemplate


class WizGameObjectTemplate(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # TODO: add all behavior template types
    async def behaviors(self) -> List[AddressedBehaviorTemplate]:
        behaviors = []
        for addr in await self.read_dynamic_vector(72):
            # they sometimes set these to 0
            if addr != 0:
                behaviors.append(AddressedBehaviorTemplate(self.hook_handler, addr))

        return behaviors

    async def object_name(self) -> str:
        return await self.read_string_from_offset(96)

    async def write_object_name(self, object_name: str):
        await self.write_string_to_offset(96, object_name)

    async def template_id(self) -> int:
        return await self.read_value_from_offset(128, "unsigned int")

    async def write_template_id(self, template_id: int):
        await self.write_value_to_offset(128, template_id, "unsigned int")

    async def visual_id(self) -> int:
        return await self.read_value_from_offset(132, "unsigned int")

    async def write_visual_id(self, visual_id: int):
        await self.write_value_to_offset(132, visual_id, "unsigned int")

    async def adjective_list(self) -> str:
        return await self.read_string_from_offset(248)

    async def write_adjective_list(self, adjective_list: str):
        await self.write_string_to_offset(248, adjective_list)

    async def exempt_from_aoi(self) -> bool:
        return await self.read_value_from_offset(240, "bool")

    async def write_exempt_from_aoi(self, exempt_from_aoi: bool):
        await self.write_value_to_offset(240, exempt_from_aoi, "bool")

    async def display_name(self) -> str:
        return await self.read_string_from_offset(168)

    async def write_display_name(self, display_name: str):
        await self.write_string_to_offset(168, display_name)

    async def description(self) -> str:
        return await self.read_string_from_offset(136)

    async def write_description(self, description: str):
        await self.write_string_to_offset(136, description)

    async def object_type(self) -> ObjectType:
        return await self.read_enum(200, ObjectType)

    async def icon(self) -> str:
        return await self.read_string_from_offset(208)

    async def write_icon(self, icon: str):
        await self.write_string_to_offset(208, icon)

    async def loot_table(self) -> str:
        return await self.read_string_from_offset(280)

    async def write_loot_table(self, loot_table: str):
        await self.write_string_to_offset(280, loot_table)

    async def death_particles(self) -> str:
        return await self.read_string_from_offset(296)

    async def write_death_particles(self, death_particles: str):
        await self.write_string_to_offset(296, death_particles)

    async def death_sound(self) -> str:
        return await self.read_string_from_offset(328)

    async def write_death_sound(self, death_sound: str):
        await self.write_string_to_offset(328, death_sound)

    async def hit_sound(self) -> str:
        return await self.read_string_from_offset(360)

    async def write_hit_sound(self, hit_sound: str):
        await self.write_string_to_offset(360, hit_sound)

    async def cast_sound(self) -> str:
        return await self.read_string_from_offset(392)

    async def write_cast_sound(self, cast_sound: str):
        await self.write_string_to_offset(392, cast_sound)

    async def aggro_sound(self) -> str:
        return await self.read_string_from_offset(424)

    async def write_aggro_sound(self, aggro_sound: str):
        await self.write_string_to_offset(424, aggro_sound)

    async def primary_school_name(self) -> str:
        return await self.read_string_from_offset(456)

    async def write_primary_school_name(self, primary_school_name: str):
        await self.write_string_to_offset(456, primary_school_name)

    async def location_preference(self) -> str:
        return await self.read_string_from_offset(488)

    async def write_location_preference(self, location_preference: str):
        await self.write_string_to_offset(488, location_preference)

    # async def leash_offset_override(self) -> class SharedPointer<class LeashOffsetOverride>:
    #     return await self.read_value_from_offset(528, "class SharedPointer<class LeashOffsetOverride>")


class AddressedWizGameObjectTemplate(WizGameObjectTemplate):
    pass
