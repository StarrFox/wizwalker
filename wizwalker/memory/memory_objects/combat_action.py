from typing import Optional

from wizwalker.memory.memory_object import MemoryObject, DynamicMemoryObject
from .spell import DynamicSpell


# TODO: document
class CombatAction(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def spell_caster(self) -> int:
        return await self.read_value_from_offset(72, "int")

    async def write_spell_caster(self, spell_caster: int):
        await self.write_value_to_offset(72, spell_caster, "int")

    async def spell(self) -> Optional[DynamicSpell]:
        addr = await self.read_value_from_offset(96, "long long")

        if addr == 0:
            return None

        return DynamicSpell(self.hook_handler, addr)

    async def spell_hits(self) -> int:
        return await self.read_value_from_offset(112, "char")

    async def write_spell_hits(self, spell_hits: int):
        await self.write_value_to_offset(112, spell_hits, "char")

    async def effect_chosen(self) -> int:
        return await self.read_value_from_offset(212, "unsigned int")

    async def write_effect_chosen(self, effect_chosen: int):
        await self.write_value_to_offset(212, effect_chosen, "unsigned int")

    async def interrupt(self) -> bool:
        return await self.read_value_from_offset(113, "bool")

    async def write_interrupt(self, interrupt: bool):
        await self.write_value_to_offset(113, interrupt, "bool")

    async def sigil_spell(self) -> bool:
        return await self.read_value_from_offset(114, "bool")

    async def write_sigil_spell(self, sigil_spell: bool):
        await self.write_value_to_offset(114, sigil_spell, "bool")

    async def show_cast(self) -> bool:
        return await self.read_value_from_offset(115, "bool")

    async def write_show_cast(self, show_cast: bool):
        await self.write_value_to_offset(115, show_cast, "bool")

    async def critical_hit_roll(self) -> int:
        return await self.read_value_from_offset(116, "unsigned char")

    async def write_critical_hit_roll(self, critical_hit_roll: int):
        await self.write_value_to_offset(116, critical_hit_roll, "unsigned char")

    async def stun_resist_roll(self) -> int:
        return await self.read_value_from_offset(117, "unsigned char")

    async def write_stun_resist_roll(self, stun_resist_roll: int):
        await self.write_value_to_offset(117, stun_resist_roll, "unsigned char")

    async def blocks_calculated(self) -> bool:
        return await self.read_value_from_offset(152, "bool")

    async def write_blocks_calculated(self, blocks_calculated: bool):
        await self.write_value_to_offset(152, blocks_calculated, "bool")

    async def serialized_blocks(self) -> str:
        return await self.read_string_from_offset(160)

    async def write_serialized_blocks(self, serialized_blocks: str):
        await self.write_string_to_offset(160, serialized_blocks)

    async def string_key_message(self) -> str:
        return await self.read_string_from_offset(216)

    async def write_string_key_message(self, string_key_message: str):
        await self.write_string_to_offset(216, string_key_message)

    async def sound_file_name(self) -> str:
        return await self.read_string_from_offset(248)

    async def write_sound_file_name(self, sound_file_name: str):
        await self.write_string_to_offset(248, sound_file_name)

    async def duration_modifier(self) -> float:
        return await self.read_value_from_offset(280, "float")

    async def write_duration_modifier(self, duration_modifier: float):
        await self.write_value_to_offset(280, duration_modifier, "float")

    async def serialized_targets_affected(self) -> str:
        return await self.read_string_from_offset(288)

    async def write_serialized_targets_affected(self, serialized_targets_affected: str):
        await self.write_string_to_offset(288, serialized_targets_affected)

    async def target_subcircle_list(self) -> int:
        return await self.read_value_from_offset(80, "int")

    async def write_target_subcircle_list(self, target_subcircle_list: int):
        await self.write_value_to_offset(80, target_subcircle_list, "int")

    async def pip_conversion_roll(self) -> int:
        return await self.read_value_from_offset(120, "int")

    async def write_pip_conversion_roll(self, pip_conversion_roll: int):
        await self.write_value_to_offset(120, pip_conversion_roll, "int")

    async def random_spell_effect_per_target_rolls(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def write_random_spell_effect_per_target_rolls(
        self, random_spell_effect_per_target_rolls: int
    ):
        await self.write_value_to_offset(
            128, random_spell_effect_per_target_rolls, "int"
        )

    async def handled_random_spell_per_target(self) -> bool:
        return await self.read_value_from_offset(124, "bool")

    async def write_handled_random_spell_per_target(
        self, handled_random_spell_per_target: bool
    ):
        await self.write_value_to_offset(124, handled_random_spell_per_target, "bool")

    async def confused_target(self) -> bool:
        return await self.read_value_from_offset(208, "bool")

    async def write_confused_target(self, confused_target: bool):
        await self.write_value_to_offset(208, confused_target, "bool")

    async def force_spell(self) -> bool:
        return await self.read_value_from_offset(336, "bool")

    async def write_force_spell(self, force_spell: bool):
        await self.write_value_to_offset(336, force_spell, "bool")

    async def after_died(self) -> bool:
        return await self.read_value_from_offset(209, "bool")

    async def write_after_died(self, after_died: bool):
        await self.write_value_to_offset(209, after_died, "bool")

    async def delayed(self) -> bool:
        return await self.read_value_from_offset(337, "bool")

    async def write_delayed(self, delayed: bool):
        await self.write_value_to_offset(337, delayed, "bool")

    async def delayed_enchanted(self) -> bool:
        return await self.read_value_from_offset(338, "bool")

    async def write_delayed_enchanted(self, delayed_enchanted: bool):
        await self.write_value_to_offset(338, delayed_enchanted, "bool")

    async def pet_cast(self) -> bool:
        return await self.read_value_from_offset(339, "bool")

    async def write_pet_cast(self, pet_cast: bool):
        await self.write_value_to_offset(339, pet_cast, "bool")

    async def pet_casted(self) -> bool:
        return await self.read_value_from_offset(340, "bool")

    async def write_pet_casted(self, pet_casted: bool):
        await self.write_value_to_offset(340, pet_casted, "bool")

    async def pet_cast_target(self) -> int:
        return await self.read_value_from_offset(344, "int")

    async def write_pet_cast_target(self, pet_cast_target: int):
        await self.write_value_to_offset(344, pet_cast_target, "int")

    # async def crit_hit_list(self) -> class TargetCritHit:
    #     return await self.read_value_from_offset(352, "class TargetCritHit")


class DynamicCombatAction(DynamicMemoryObject, CombatAction):
    pass
