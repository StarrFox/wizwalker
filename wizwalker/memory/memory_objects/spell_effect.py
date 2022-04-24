from typing import List

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import SpellEffects, EffectTarget, HangingDisposition


class SpellEffect(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def effect_type(self) -> SpellEffects:
        return await self.read_enum(72, SpellEffects)

    async def write_effect_type(self, effect_type: SpellEffects):
        await self.write_enum(72, effect_type)

    async def effect_param(self) -> int:
        return await self.read_value_from_offset(76, "int")

    async def write_effect_param(self, effect_param: int):
        await self.write_value_to_offset(76, effect_param, "int")

    async def string_damage_type(self) -> str:
        return await self.read_string_from_offset(88)

    async def write_string_damage_type(self, string_damage_type: str):
        await self.write_string_to_offset(88, string_damage_type)

    async def disposition(self) -> HangingDisposition:
        return await self.read_enum(80, HangingDisposition)

    async def write_disposition(self, disposition: HangingDisposition):
        await self.write_enum(80, disposition)

    async def damage_type(self) -> int:
        return await self.read_value_from_offset(84, "unsigned int")

    async def write_damage_type(self, damage_type: int):
        await self.write_value_to_offset(84, damage_type, "unsigned int")

    async def pip_num(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def write_pip_num(self, pip_num: int):
        await self.write_value_to_offset(128, pip_num, "int")

    async def act_num(self) -> int:
        return await self.read_value_from_offset(132, "int")

    async def write_act_num(self, act_num: int):
        await self.write_value_to_offset(132, act_num, "int")

    async def effect_target(self) -> EffectTarget:
        return await self.read_enum(140, EffectTarget)

    async def write_effect_target(self, effect_target: EffectTarget):
        await self.write_enum(140, effect_target)

    async def num_rounds(self) -> int:
        return await self.read_value_from_offset(144, "int")

    async def write_num_rounds(self, num_rounds: int):
        await self.write_value_to_offset(144, num_rounds, "int")

    async def param_per_round(self) -> int:
        return await self.read_value_from_offset(148, "int")

    async def write_param_per_round(self, param_per_round: int):
        await self.write_value_to_offset(148, param_per_round, "int")

    async def heal_modifier(self) -> float:
        return await self.read_value_from_offset(152, "float")

    async def write_heal_modifier(self, heal_modifier: float):
        await self.write_value_to_offset(152, heal_modifier, "float")

    async def spell_template_id(self) -> int:
        return await self.read_value_from_offset(120, "unsigned int")

    async def write_spell_template_id(self, spell_template_id: int):
        await self.write_value_to_offset(120, spell_template_id, "unsigned int")

    async def enchantment_spell_template_id(self) -> int:
        return await self.read_value_from_offset(124, "unsigned int")

    async def write_enchantment_spell_template_id(
        self, enchantment_spell_template_id: int
    ):
        await self.write_value_to_offset(
            124, enchantment_spell_template_id, "unsigned int"
        )

    async def act(self) -> bool:
        return await self.read_value_from_offset(136, "bool")

    async def write_act(self, act: bool):
        await self.write_value_to_offset(136, act, "bool")

    async def cloaked(self) -> bool:
        return await self.read_value_from_offset(157, "bool")

    async def write_cloaked(self, cloaked: bool):
        await self.write_value_to_offset(157, cloaked, "bool")

    async def armor_piercing_param(self) -> int:
        return await self.read_value_from_offset(160, "int")

    async def write_armor_piercing_param(self, armor_piercing_param: int):
        await self.write_value_to_offset(160, armor_piercing_param, "int")

    async def chance_per_target(self) -> int:
        return await self.read_value_from_offset(164, "int")

    async def write_chance_per_target(self, chance_per_target: int):
        await self.write_value_to_offset(164, chance_per_target, "int")

    async def protected(self) -> bool:
        return await self.read_value_from_offset(168, "bool")

    async def write_protected(self, protected: bool):
        await self.write_value_to_offset(168, protected, "bool")

    async def converted(self) -> bool:
        return await self.read_value_from_offset(169, "bool")

    async def write_converted(self, converted: bool):
        await self.write_value_to_offset(169, converted, "bool")

    async def rank(self) -> int:
        return await self.read_value_from_offset(208, "int")

    async def write_rank(self, rank: int):
        await self.write_value_to_offset(208, rank, "int")

    async def maybe_effect_list(
        self, *, check_type: bool = False
    ) -> List["DynamicSpellEffect"]:
        if check_type:
            type_name = await self.maybe_read_type_name()
            if type_name not in ("RandomSpellEffect", "RandomPerTargetSpellEffect", "VariableSpellEffect"):
                raise ValueError(
                    f"This object is a {type_name} not a"
                    f" Random/RandomPerTarget/Variable SpellEffect."
                )

        effects = []

        for addr in await self.read_shared_linked_list(224):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects


class DynamicSpellEffect(DynamicMemoryObject, SpellEffect):
    pass
