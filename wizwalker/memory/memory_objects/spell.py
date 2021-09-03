from dataclasses import dataclass
from typing import Optional

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import DelayOrder
from .spell_template import DynamicSpellTemplate
from .spell_effect import DynamicSpellEffect


@dataclass
class RankStruct:
    regular_rank: int
    shadow_rank: int


class Spell(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def template_id(self) -> int:
        return self.read_value_from_offset(128, "unsigned int")

    def write_template_id(self, template_id: int):
        self.write_value_to_offset(128, template_id, "unsigned int")

    # note: not defined
    def spell_template(self) -> Optional[DynamicSpellTemplate]:
        addr = self.read_value_from_offset(120, "long long")

        if addr == 0:
            return None

        return DynamicSpellTemplate(self.hook_handler, addr)

    # write spell_template

    def enchantment(self) -> int:
        return self.read_value_from_offset(80, "unsigned int")

    def write_enchantment(self, enchantment: int):
        self.write_value_to_offset(80, enchantment, "unsigned int")

    # note: this struct is just within the Spell class; wild
    def rank(self) -> RankStruct:
        # further note: check RankStruct class for the 72 and 73 offsets
        regular_rank = self.read_value_from_offset(176 + 72, "unsigned char")
        shadow_rank = self.read_value_from_offset(176 + 73, "unsigned char")
        return RankStruct(regular_rank, shadow_rank)

    def write_rank(self, rank: RankStruct):
        # see above for offset info
        self.write_value_to_offset(176 + 72, rank.regular_rank, "unsigned char")
        self.write_value_to_offset(176 + 73, rank.shadow_rank, "unsigned char")

    def regular_adjust(self) -> int:
        return self.read_value_from_offset(256, "int")

    def write_regular_adjust(self, regular_adjust: int):
        self.write_value_to_offset(256, regular_adjust, "int")

    def shadow_adjust(self) -> int:
        return self.read_value_from_offset(260, "int")

    def write_shadow_adjust(self, shadow_adjust: int):
        self.write_value_to_offset(260, shadow_adjust, "int")

    def magic_school_id(self) -> int:
        return self.read_value_from_offset(136, "unsigned int")

    def write_magic_school_id(self, magic_school_id: int):
        self.write_value_to_offset(136, magic_school_id, "unsigned int")

    def accuracy(self) -> int:
        return self.read_value_from_offset(132, "unsigned char")

    def write_accuracy(self, accuracy: int):
        self.write_value_to_offset(132, accuracy, "unsigned char")

    def spell_effects(self) -> list[DynamicSpellEffect]:
        effects = []
        for addr in self.read_shared_vector(88):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects

    def treasure_card(self) -> bool:
        return self.read_value_from_offset(265, "bool")

    def write_treasure_card(self, treasure_card: bool):
        self.write_value_to_offset(265, treasure_card, "bool")

    def battle_card(self) -> bool:
        return self.read_value_from_offset(266, "bool")

    def write_battle_card(self, battle_card: bool):
        self.write_value_to_offset(266, battle_card, "bool")

    def item_card(self) -> bool:
        return self.read_value_from_offset(267, "bool")

    def write_item_card(self, item_card: bool):
        self.write_value_to_offset(267, item_card, "bool")

    def side_board(self) -> bool:
        return self.read_value_from_offset(268, "bool")

    def write_side_board(self, side_board: bool):
        self.write_value_to_offset(268, side_board, "bool")

    def spell_id(self) -> int:
        return self.read_value_from_offset(272, "unsigned int")

    def write_spell_id(self, spell_id: int):
        self.write_value_to_offset(272, spell_id, "unsigned int")

    def leaves_play_when_cast_override(self) -> bool:
        return self.read_value_from_offset(284, "bool")

    def write_leaves_play_when_cast_override(
        self, leaves_play_when_cast_override: bool
    ):
        self.write_value_to_offset(284, leaves_play_when_cast_override, "bool")

    def cloaked(self) -> bool:
        return self.read_value_from_offset(264, "bool")

    def write_cloaked(self, cloaked: bool):
        self.write_value_to_offset(264, cloaked, "bool")

    def enchantment_spell_is_item_card(self) -> bool:
        return self.read_value_from_offset(76, "bool")

    def write_enchantment_spell_is_item_card(
        self, enchantment_spell_is_item_card: bool
    ):
        self.write_value_to_offset(76, enchantment_spell_is_item_card, "bool")

    def premutation_spell_id(self) -> int:
        return self.read_value_from_offset(112, "unsigned int")

    def write_premutation_spell_id(self, premutation_spell_id: int):
        self.write_value_to_offset(112, premutation_spell_id, "unsigned int")

    def enchanted_this_combat(self) -> bool:
        return self.read_value_from_offset(77, "bool")

    def write_enchanted_this_combat(self, enchanted_this_combat: bool):
        self.write_value_to_offset(77, enchanted_this_combat, "bool")

    # def param_overrides(self) -> class SharedPointer<class SpellEffectParamOverride>:
    #     return self.read_value_from_offset(288, "class SharedPointer<class SpellEffectParamOverride>")

    # def sub_effect_meta(self) -> class SharedPointer<class SpellSubEffectMetadata>:
    #     return self.read_value_from_offset(304, "class SharedPointer<class SpellSubEffectMetadata>")

    def delay_enchantment(self) -> bool:
        return self.read_value_from_offset(321, "bool")

    def write_delay_enchantment(self, delay_enchantment: bool):
        self.write_value_to_offset(321, delay_enchantment, "bool")

    def pve(self) -> bool:
        return self.read_value_from_offset(328, "bool")

    def write_pve(self, pve: bool):
        self.write_value_to_offset(328, pve, "bool")

    def delay_enchantment_order(self) -> DelayOrder:
        return self.read_enum(72, DelayOrder)

    def write_delay_enchantment_order(self, delay_enchantment_order: DelayOrder):
        self.write_enum(72, delay_enchantment_order)

    def round_added_tc(self) -> int:
        return self.read_value_from_offset(324, "int")

    def write_round_added_tc(self, round_added_t_c: int):
        self.write_value_to_offset(324, round_added_t_c, "int")


class GraphicalSpell(Spell):
    def read_base_address(self) -> int:
        raise NotImplementedError()


class DynamicSpell(DynamicMemoryObject, Spell):
    pass


class DynamicGraphicalSpell(DynamicMemoryObject, GraphicalSpell):
    pass


class Hand(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def spell_list(self) -> list[DynamicSpell]:
        spells = []
        for addr in self.read_shared_linked_list(72):
            spells.append(DynamicSpell(self.hook_handler, addr))

        return spells


class DynamicHand(DynamicMemoryObject, Hand):
    pass
