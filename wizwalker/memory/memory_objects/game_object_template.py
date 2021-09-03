from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject
from .enums import ObjectType
from .behavior_template import DynamicBehaviorTemplate


class WizGameObjectTemplate(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    # TODO: add all behavior template types
    def behaviors(self) -> list[DynamicBehaviorTemplate]:
        behaviors = []
        for addr in self.read_dynamic_vector(72):
            # they sometimes set these to 0
            if addr != 0:
                behaviors.append(DynamicBehaviorTemplate(self.hook_handler, addr))

        return behaviors

    def object_name(self) -> str:
        return self.read_string_from_offset(96)

    def write_object_name(self, object_name: str):
        self.write_string_to_offset(96, object_name)

    def template_id(self) -> int:
        return self.read_value_from_offset(128, "unsigned int")

    def write_template_id(self, template_id: int):
        self.write_value_to_offset(128, template_id, "unsigned int")

    def visual_id(self) -> int:
        return self.read_value_from_offset(132, "unsigned int")

    def write_visual_id(self, visual_id: int):
        self.write_value_to_offset(132, visual_id, "unsigned int")

    def adjective_list(self) -> str:
        return self.read_string_from_offset(248)

    def write_adjective_list(self, adjective_list: str):
        self.write_string_to_offset(248, adjective_list)

    def exempt_from_aoi(self) -> bool:
        return self.read_value_from_offset(240, "bool")

    def write_exempt_from_aoi(self, exempt_from_aoi: bool):
        self.write_value_to_offset(240, exempt_from_aoi, "bool")

    def display_name(self) -> str:
        return self.read_string_from_offset(168)

    def write_display_name(self, display_name: str):
        self.write_string_to_offset(168, display_name)

    def description(self) -> str:
        return self.read_string_from_offset(136)

    def write_description(self, description: str):
        self.write_string_to_offset(136, description)

    def object_type(self) -> ObjectType:
        return self.read_enum(200, ObjectType)

    def icon(self) -> str:
        return self.read_string_from_offset(208)

    def write_icon(self, icon: str):
        self.write_string_to_offset(208, icon)

    def loot_table(self) -> str:
        return self.read_string_from_offset(280)

    def write_loot_table(self, loot_table: str):
        self.write_string_to_offset(280, loot_table)

    def death_particles(self) -> str:
        return self.read_string_from_offset(296)

    def write_death_particles(self, death_particles: str):
        self.write_string_to_offset(296, death_particles)

    def death_sound(self) -> str:
        return self.read_string_from_offset(328)

    def write_death_sound(self, death_sound: str):
        self.write_string_to_offset(328, death_sound)

    def hit_sound(self) -> str:
        return self.read_string_from_offset(360)

    def write_hit_sound(self, hit_sound: str):
        self.write_string_to_offset(360, hit_sound)

    def cast_sound(self) -> str:
        return self.read_string_from_offset(392)

    def write_cast_sound(self, cast_sound: str):
        self.write_string_to_offset(392, cast_sound)

    def aggro_sound(self) -> str:
        return self.read_string_from_offset(424)

    def write_aggro_sound(self, aggro_sound: str):
        self.write_string_to_offset(424, aggro_sound)

    def primary_school_name(self) -> str:
        return self.read_string_from_offset(456)

    def write_primary_school_name(self, primary_school_name: str):
        self.write_string_to_offset(456, primary_school_name)

    def location_preference(self) -> str:
        return self.read_string_from_offset(488)

    def write_location_preference(self, location_preference: str):
        self.write_string_to_offset(488, location_preference)

    # def leash_offset_override(self) -> class SharedPointer<class LeashOffsetOverride>:
    #     return self.read_value_from_offset(528, "class SharedPointer<class LeashOffsetOverride>")


class DynamicWizGameObjectTemplate(DynamicMemoryObject, WizGameObjectTemplate):
    pass
