from typing import Optional

from wizwalker.memory.memory_object import MemoryObject, DynamicMemoryObject
from .spell import DynamicSpell


# TODO: document
class CombatAction(MemoryObject):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def spell_caster(self) -> int:
        return self.read_value_from_offset(72, "int")

    def write_spell_caster(self, spell_caster: int):
        self.write_value_to_offset(72, spell_caster, "int")

    def spell(self) -> Optional[DynamicSpell]:
        addr = self.read_value_from_offset(96, "long long")

        if addr == 0:
            return None

        return DynamicSpell(self.hook_handler, addr)

    def spell_hits(self) -> int:
        return self.read_value_from_offset(112, "char")

    def write_spell_hits(self, spell_hits: int):
        self.write_value_to_offset(112, spell_hits, "char")

    def effect_chosen(self) -> int:
        return self.read_value_from_offset(212, "unsigned int")

    def write_effect_chosen(self, effect_chosen: int):
        self.write_value_to_offset(212, effect_chosen, "unsigned int")

    def interrupt(self) -> bool:
        return self.read_value_from_offset(113, "bool")

    def write_interrupt(self, interrupt: bool):
        self.write_value_to_offset(113, interrupt, "bool")

    def sigil_spell(self) -> bool:
        return self.read_value_from_offset(114, "bool")

    def write_sigil_spell(self, sigil_spell: bool):
        self.write_value_to_offset(114, sigil_spell, "bool")

    def show_cast(self) -> bool:
        return self.read_value_from_offset(115, "bool")

    def write_show_cast(self, show_cast: bool):
        self.write_value_to_offset(115, show_cast, "bool")

    def critical_hit_roll(self) -> int:
        return self.read_value_from_offset(116, "unsigned char")

    def write_critical_hit_roll(self, critical_hit_roll: int):
        self.write_value_to_offset(116, critical_hit_roll, "unsigned char")

    def stun_resist_roll(self) -> int:
        return self.read_value_from_offset(117, "unsigned char")

    def write_stun_resist_roll(self, stun_resist_roll: int):
        self.write_value_to_offset(117, stun_resist_roll, "unsigned char")

    def blocks_calculated(self) -> bool:
        return self.read_value_from_offset(152, "bool")

    def write_blocks_calculated(self, blocks_calculated: bool):
        self.write_value_to_offset(152, blocks_calculated, "bool")

    def serialized_blocks(self) -> str:
        return self.read_string_from_offset(160)

    def write_serialized_blocks(self, serialized_blocks: str):
        self.write_string_to_offset(160, serialized_blocks)

    def string_key_message(self) -> str:
        return self.read_string_from_offset(216)

    def write_string_key_message(self, string_key_message: str):
        self.write_string_to_offset(216, string_key_message)

    def sound_file_name(self) -> str:
        return self.read_string_from_offset(248)

    def write_sound_file_name(self, sound_file_name: str):
        self.write_string_to_offset(248, sound_file_name)

    def duration_modifier(self) -> float:
        return self.read_value_from_offset(280, "float")

    def write_duration_modifier(self, duration_modifier: float):
        self.write_value_to_offset(280, duration_modifier, "float")

    def serialized_targets_affected(self) -> str:
        return self.read_string_from_offset(288)

    def write_serialized_targets_affected(self, serialized_targets_affected: str):
        self.write_string_to_offset(288, serialized_targets_affected)

    def target_subcircle_list(self) -> int:
        return self.read_value_from_offset(80, "int")

    def write_target_subcircle_list(self, target_subcircle_list: int):
        self.write_value_to_offset(80, target_subcircle_list, "int")

    def pip_conversion_roll(self) -> int:
        return self.read_value_from_offset(120, "int")

    def write_pip_conversion_roll(self, pip_conversion_roll: int):
        self.write_value_to_offset(120, pip_conversion_roll, "int")

    def random_spell_effect_per_target_rolls(self) -> int:
        return self.read_value_from_offset(128, "int")

    def write_random_spell_effect_per_target_rolls(
        self, random_spell_effect_per_target_rolls: int
    ):
        self.write_value_to_offset(
            128, random_spell_effect_per_target_rolls, "int"
        )

    def handled_random_spell_per_target(self) -> bool:
        return self.read_value_from_offset(124, "bool")

    def write_handled_random_spell_per_target(
        self, handled_random_spell_per_target: bool
    ):
        self.write_value_to_offset(124, handled_random_spell_per_target, "bool")

    def confused_target(self) -> bool:
        return self.read_value_from_offset(208, "bool")

    def write_confused_target(self, confused_target: bool):
        self.write_value_to_offset(208, confused_target, "bool")

    def force_spell(self) -> bool:
        return self.read_value_from_offset(336, "bool")

    def write_force_spell(self, force_spell: bool):
        self.write_value_to_offset(336, force_spell, "bool")

    def after_died(self) -> bool:
        return self.read_value_from_offset(209, "bool")

    def write_after_died(self, after_died: bool):
        self.write_value_to_offset(209, after_died, "bool")

    def delayed(self) -> bool:
        return self.read_value_from_offset(337, "bool")

    def write_delayed(self, delayed: bool):
        self.write_value_to_offset(337, delayed, "bool")

    def delayed_enchanted(self) -> bool:
        return self.read_value_from_offset(338, "bool")

    def write_delayed_enchanted(self, delayed_enchanted: bool):
        self.write_value_to_offset(338, delayed_enchanted, "bool")

    def pet_cast(self) -> bool:
        return self.read_value_from_offset(339, "bool")

    def write_pet_cast(self, pet_cast: bool):
        self.write_value_to_offset(339, pet_cast, "bool")

    def pet_casted(self) -> bool:
        return self.read_value_from_offset(340, "bool")

    def write_pet_casted(self, pet_casted: bool):
        self.write_value_to_offset(340, pet_casted, "bool")

    def pet_cast_target(self) -> int:
        return self.read_value_from_offset(344, "int")

    def write_pet_cast_target(self, pet_cast_target: int):
        self.write_value_to_offset(344, pet_cast_target, "int")

    # def crit_hit_list(self) -> class TargetCritHit:
    #     return self.read_value_from_offset(352, "class TargetCritHit")


class DynamicCombatAction(DynamicMemoryObject, CombatAction):
    pass
