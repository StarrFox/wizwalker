from dataclasses import dataclass
from typing import List, Optional

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import DelayOrder
from .spell_template import DynamicSpellTemplate
from .spell_effect import DynamicSpellEffect


@dataclass
class RankStruct:
    regular_rank: int
    shadow_rank: int


class Spell(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def template_id(self) -> int:
        return await self.read_value_from_offset(128, "unsigned int")

    async def write_template_id(self, template_id: int):
        await self.write_value_to_offset(128, template_id, "unsigned int")

    # note: not defined
    async def spell_template(self) -> Optional[DynamicSpellTemplate]:
        addr = await self.read_value_from_offset(120, "long long")

        if addr == 0:
            return None

        return DynamicSpellTemplate(self.hook_handler, addr)

    # write spell_template

    async def enchantment(self) -> int:
        return await self.read_value_from_offset(80, "unsigned int")

    async def write_enchantment(self, enchantment: int):
        await self.write_value_to_offset(80, enchantment, "unsigned int")

    # note: this struct is just within the Spell class; wild
    async def rank(self) -> RankStruct:
        # further note: check RankStruct class for the 72 and 73 offsets
        regular_rank = await self.read_value_from_offset(176 + 72, "unsigned char")
        shadow_rank = await self.read_value_from_offset(176 + 73, "unsigned char")
        return RankStruct(regular_rank, shadow_rank)

    async def write_rank(self, rank: RankStruct):
        # see above for offset info
        await self.write_value_to_offset(176 + 72, rank.regular_rank, "unsigned char")
        await self.write_value_to_offset(176 + 73, rank.shadow_rank, "unsigned char")

    async def regular_adjust(self) -> int:
        return await self.read_value_from_offset(256, "int")

    async def write_regular_adjust(self, regular_adjust: int):
        await self.write_value_to_offset(256, regular_adjust, "int")

    async def shadow_adjust(self) -> int:
        return await self.read_value_from_offset(260, "int")

    async def write_shadow_adjust(self, shadow_adjust: int):
        await self.write_value_to_offset(260, shadow_adjust, "int")

    async def magic_school_id(self) -> int:
        return await self.read_value_from_offset(136, "unsigned int")

    async def write_magic_school_id(self, magic_school_id: int):
        await self.write_value_to_offset(136, magic_school_id, "unsigned int")

    async def accuracy(self) -> int:
        return await self.read_value_from_offset(132, "unsigned char")

    async def write_accuracy(self, accuracy: int):
        await self.write_value_to_offset(132, accuracy, "unsigned char")

    async def spell_effects(self) -> List[DynamicSpellEffect]:
        effects = []
        for addr in await self.read_shared_vector(88):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects

    async def treasure_card(self) -> bool:
        return await self.read_value_from_offset(265, "bool")

    async def write_treasure_card(self, treasure_card: bool):
        await self.write_value_to_offset(265, treasure_card, "bool")

    async def battle_card(self) -> bool:
        return await self.read_value_from_offset(266, "bool")

    async def write_battle_card(self, battle_card: bool):
        await self.write_value_to_offset(266, battle_card, "bool")

    async def item_card(self) -> bool:
        return await self.read_value_from_offset(267, "bool")

    async def write_item_card(self, item_card: bool):
        await self.write_value_to_offset(267, item_card, "bool")

    async def side_board(self) -> bool:
        return await self.read_value_from_offset(268, "bool")

    async def write_side_board(self, side_board: bool):
        await self.write_value_to_offset(268, side_board, "bool")

    async def spell_id(self) -> int:
        return await self.read_value_from_offset(272, "unsigned int")

    async def write_spell_id(self, spell_id: int):
        await self.write_value_to_offset(272, spell_id, "unsigned int")

    async def leaves_play_when_cast_override(self) -> bool:
        return await self.read_value_from_offset(284, "bool")

    async def write_leaves_play_when_cast_override(
        self, leaves_play_when_cast_override: bool
    ):
        await self.write_value_to_offset(284, leaves_play_when_cast_override, "bool")

    async def cloaked(self) -> bool:
        return await self.read_value_from_offset(264, "bool")

    async def write_cloaked(self, cloaked: bool):
        await self.write_value_to_offset(264, cloaked, "bool")

    async def enchantment_spell_is_item_card(self) -> bool:
        return await self.read_value_from_offset(76, "bool")

    async def write_enchantment_spell_is_item_card(
        self, enchantment_spell_is_item_card: bool
    ):
        await self.write_value_to_offset(76, enchantment_spell_is_item_card, "bool")

    async def premutation_spell_id(self) -> int:
        return await self.read_value_from_offset(112, "unsigned int")

    async def write_premutation_spell_id(self, premutation_spell_id: int):
        await self.write_value_to_offset(112, premutation_spell_id, "unsigned int")

    async def enchanted_this_combat(self) -> bool:
        return await self.read_value_from_offset(77, "bool")

    async def write_enchanted_this_combat(self, enchanted_this_combat: bool):
        await self.write_value_to_offset(77, enchanted_this_combat, "bool")

    # async def param_overrides(self) -> class SharedPointer<class SpellEffectParamOverride>:
    #     return await self.read_value_from_offset(288, "class SharedPointer<class SpellEffectParamOverride>")

    # async def sub_effect_meta(self) -> class SharedPointer<class SpellSubEffectMetadata>:
    #     return await self.read_value_from_offset(304, "class SharedPointer<class SpellSubEffectMetadata>")

    async def delay_enchantment(self) -> bool:
        return await self.read_value_from_offset(321, "bool")

    async def write_delay_enchantment(self, delay_enchantment: bool):
        await self.write_value_to_offset(321, delay_enchantment, "bool")

    async def pve(self) -> bool:
        return await self.read_value_from_offset(328, "bool")

    async def write_pve(self, pve: bool):
        await self.write_value_to_offset(328, pve, "bool")

    async def delay_enchantment_order(self) -> DelayOrder:
        return await self.read_enum(72, DelayOrder)

    async def write_delay_enchantment_order(self, delay_enchantment_order: DelayOrder):
        await self.write_enum(72, delay_enchantment_order)

    async def round_added_tc(self) -> int:
        return await self.read_value_from_offset(324, "int")

    async def write_round_added_tc(self, round_added_t_c: int):
        await self.write_value_to_offset(324, round_added_t_c, "int")


class GraphicalSpell(Spell):
    async def read_base_address(self) -> int:
        raise NotImplementedError()


class DynamicSpell(DynamicMemoryObject, Spell):
    pass


class DynamicGraphicalSpell(DynamicMemoryObject, GraphicalSpell):
    pass


class Hand(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def spell_list(self) -> List[DynamicSpell]:
        spells = []
        for addr in await self.read_shared_linked_list(72):
            spells.append(DynamicSpell(self.hook_handler, addr))

        return spells


class DynamicHand(DynamicMemoryObject, Hand):
    pass
