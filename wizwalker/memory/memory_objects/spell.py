from typing import List

from wizwalker.memory.memory_objects.enums import DelayOrder, SpellSourceType
from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass


class Spell(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def template_id(self) -> int:
        return await self.read_value_from_offset(128, "unsigned int")

    async def write_template_id(self, template_id: int):
        await self.write_value_to_offset(128, template_id, "unsigned int")

    # note: not defined
    async def spell_template(self) -> "SpellTemplate":
        addr = await self.read_value_from_offset(120, "long long")
        return DynamicSpellTemplate(self.hook_handler, addr)

    # write spell_template

    async def enchantment(self) -> int:
        return await self.read_value_from_offset(80, "unsigned int")

    async def write_enchantment(self, enchantment: int):
        await self.write_value_to_offset(80, enchantment, "unsigned int")

    # async def rank(self) -> class RankStruct:
    #     return await self.read_value_from_offset(176, "class RankStruct")
    #
    # async def write_rank(self, rank: class RankStruct):
    #     await self.write_value_to_offset(176, rank, "class RankStruct")

    async def regular_adjust(self) -> int:
        return await self.read_value_from_offset(256, "int")

    async def write_regular_adjust(self, regular_adjust: int):
        await self.write_value_to_offset(256, regular_adjust, "int")

    async def shadow_adjust(self) -> int:
        return await self.read_value_from_offset(260, "int")

    async def write_shadow_adjust(self, shadow_adjust: int):
        await self.write_value_to_offset(260, shadow_adjust, "int")

    # note for future: not defined in class def
    async def school_name(self) -> str:
        return await self.read_string_from_offset(144)

    async def write_school_name(self, school_name: str):
        await self.write_string_to_offset(144, school_name)

    async def magic_school_id(self) -> int:
        return await self.read_value_from_offset(136, "unsigned int")

    async def write_magic_school_id(self, magic_school_id: int):
        await self.write_value_to_offset(136, magic_school_id, "unsigned int")

    async def accuracy(self) -> int:
        return await self.read_value_from_offset(132, "unsigned char")

    async def write_accuracy(self, accuracy: int):
        await self.write_value_to_offset(132, accuracy, "unsigned char")

    # async def spell_effects(self) -> class SharedPointer<class SpellEffect>:
    #     return await self.read_value_from_offset(88, "class SharedPointer<class SpellEffect>")
    #
    # async def write_spell_effects(self, spell_effects: class SharedPointer<class SpellEffect>):
    #     await self.write_value_to_offset(88, spell_effects, "class SharedPointer<class SpellEffect>")

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
    #
    # async def write_param_overrides(self, param_overrides: class SharedPointer<class SpellEffectParamOverride>):
    #     await self.write_value_to_offset(288, param_overrides, "class SharedPointer<class SpellEffectParamOverride>")
    #
    # async def sub_effect_meta(self) -> class SharedPointer<class SpellSubEffectMetadata>:
    #     return await self.read_value_from_offset(304, "class SharedPointer<class SpellSubEffectMetadata>")
    #
    # async def write_sub_effect_meta(self, sub_effect_meta: class SharedPointer<class SpellSubEffectMetadata>):
    #     await self.write_value_to_offset(304, sub_effect_meta, "class SharedPointer<class SpellSubEffectMetadata>")

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
        # is pointed back to by last element
        list_addr = await self.read_value_from_offset(72, "long long")

        spells = []
        next_node_addr = list_addr
        list_size = await self.read_value_from_offset(80, "int")
        for _ in range(list_size):
            list_node = await self.read_typed(next_node_addr, "long long")
            next_node_addr = await self.read_typed(list_node, "long long")
            # spell is +16 from each list node
            spell_addr = await self.read_typed(list_node + 16, "long long")
            spells.append(DynamicSpell(self.hook_handler, spell_addr))

        return spells


class DynamicHand(DynamicMemoryObject, Hand):
    pass


class SpellTemplate(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # async def behaviors(self) -> class BehaviorTemplate*:
    #     return await self.read_value_from_offset(72, "class BehaviorTemplate*")
    #
    # async def write_behaviors(self, behaviors: class BehaviorTemplate*):
    #     await self.write_value_to_offset(72, behaviors, "class BehaviorTemplate*")

    async def name(self) -> str:
        return await self.read_string_from_offset(96)

    async def write_name(self, name: str):
        await self.write_string_to_offset(96, name)

    async def description(self) -> str:
        return await self.read_string_from_offset(168)

    async def write_description(self, description: str):
        await self.write_string_to_offset(168, description)

    async def display_name(self) -> str:
        return await self.read_string_from_offset(136)

    async def write_display_name(self, display_name: str):
        await self.write_string_to_offset(136, display_name)

    async def spell_base(self) -> str:
        return await self.read_string_from_offset(208)

    async def write_spell_base(self, spell_base: str):
        await self.write_string_to_offset(208, spell_base)

    # TODO: SpellEffect is very useful
    # async def effects(self) -> class SharedPointer<class SpellEffect>:
    #     return await self.read_value_from_offset(240, "class SharedPointer<class SpellEffect>")
    #
    # async def write_effects(self, effects: class SharedPointer<class SpellEffect>):
    #     await self.write_value_to_offset(240, effects, "class SharedPointer<class SpellEffect>")

    async def magic_school_name(self) -> str:
        return await self.read_string_from_offset(272)

    async def write_magic_school_name(self, magic_school_name: str):
        await self.write_string_to_offset(272, magic_school_name)

    async def type_name(self) -> str:
        return await self.read_string_from_offset(312)

    async def write_type_name(self, type_name: str):
        await self.write_string_to_offset(312, type_name)

    async def training_cost(self) -> int:
        return await self.read_value_from_offset(344, "int")

    async def write_training_cost(self, training_cost: int):
        await self.write_value_to_offset(344, training_cost, "int")

    async def accuracy(self) -> int:
        return await self.read_value_from_offset(348, "int")

    async def write_accuracy(self, accuracy: int):
        await self.write_value_to_offset(348, accuracy, "int")

    async def base_cost(self) -> int:
        return await self.read_value_from_offset(200, "int")

    async def write_base_cost(self, base_cost: int):
        await self.write_value_to_offset(200, base_cost, "int")

    async def credits_cost(self) -> int:
        return await self.read_value_from_offset(204, "int")

    async def write_credits_cost(self, credits_cost: int):
        await self.write_value_to_offset(204, credits_cost, "int")

    async def booster_pack_icon(self) -> str:
        return await self.read_string_from_offset(456)

    async def write_booster_pack_icon(self, booster_pack_icon: str):
        await self.write_string_to_offset(456, booster_pack_icon)

    async def valid_target_spells(self) -> int:
        return await self.read_value_from_offset(352, "unsigned int")

    async def write_valid_target_spells(self, valid_target_spells: int):
        await self.write_value_to_offset(352, valid_target_spells, "unsigned int")

    async def pvp(self) -> bool:
        return await self.read_value_from_offset(368, "bool")

    async def write_pvp(self, pvp: bool):
        await self.write_value_to_offset(368, pvp, "bool")

    async def pve(self) -> bool:
        return await self.read_value_from_offset(369, "bool")

    async def write_pve(self, _pv_e: bool):
        await self.write_value_to_offset(369, _pv_e, "bool")

    async def battlegrounds_only(self) -> bool:
        return await self.read_value_from_offset(370, "bool")

    async def write_battlegrounds_only(self, battlegrounds_only: bool):
        await self.write_value_to_offset(370, battlegrounds_only, "bool")

    async def treasure(self) -> bool:
        return await self.read_value_from_offset(371, "bool")

    async def write_treasure(self, treasure: bool):
        await self.write_value_to_offset(371, treasure, "bool")

    async def no_discard(self) -> bool:
        return await self.read_value_from_offset(372, "bool")

    async def write_no_discard(self, no_discard: bool):
        await self.write_value_to_offset(372, no_discard, "bool")

    async def leaves_play_when_cast(self) -> bool:
        return await self.read_value_from_offset(492, "bool")

    async def write_leaves_play_when_cast(self, leaves_play_when_cast: bool):
        await self.write_value_to_offset(492, leaves_play_when_cast, "bool")

    async def image_index(self) -> int:
        return await self.read_value_from_offset(376, "int")

    async def write_image_index(self, image_index: int):
        await self.write_value_to_offset(376, image_index, "int")

    async def image_name(self) -> str:
        return await self.read_string_from_offset(384)

    async def write_image_name(self, image_name: str):
        await self.write_string_to_offset(384, image_name)

    async def cloaked(self) -> bool:
        return await self.read_value_from_offset(449, "bool")

    async def write_cloaked(self, cloaked: bool):
        await self.write_value_to_offset(449, cloaked, "bool")

    async def caster_invisible(self) -> bool:
        return await self.read_value_from_offset(450, "bool")

    async def write_caster_invisible(self, caster_invisible: bool):
        await self.write_value_to_offset(450, caster_invisible, "bool")

    async def adjectives(self) -> str:
        return await self.read_string_from_offset(536)

    async def write_adjectives(self, adjectives: str):
        await self.write_string_to_offset(536, adjectives)

    async def spell_source_type(self) -> SpellSourceType:
        return await self.read_enum(488, SpellSourceType)

    async def write_spell_source_type(self, spell_source_type: SpellSourceType):
        await self.write_enum(488, spell_source_type)

    async def cloaked_name(self) -> str:
        return await self.read_string_from_offset(496)

    async def write_cloaked_name(self, cloaked_name: str):
        await self.write_string_to_offset(496, cloaked_name)

    # async def purchase_requirements(self) -> class RequirementList*:
    #     return await self.read_value_from_offset(568, "class RequirementList*")
    #
    # async def write_purchase_requirements(self, purchase_requirements: class RequirementList*):
    #     await self.write_value_to_offset(568, purchase_requirements, "class RequirementList*")

    async def description_trainer(self) -> str:
        return await self.read_string_from_offset(576)

    async def write_description_trainer(self, description_trainer: str):
        await self.write_string_to_offset(576, description_trainer)

    async def description_combat_hud(self) -> str:
        return await self.read_string_from_offset(608)

    async def write_description_combat_hud(self, description_combat_hud: str):
        await self.write_string_to_offset(608, description_combat_hud)

    async def display_index(self) -> int:
        return await self.read_value_from_offset(640, "int")

    async def write_display_index(self, display_index: int):
        await self.write_value_to_offset(640, display_index, "int")

    async def hidden_from_effects_window(self) -> bool:
        return await self.read_value_from_offset(644, "bool")

    async def write_hidden_from_effects_window(self, hidden_from_effects_window: bool):
        await self.write_value_to_offset(644, hidden_from_effects_window, "bool")

    async def ignore_charms(self) -> bool:
        return await self.read_value_from_offset(645, "bool")

    async def write_ignore_charms(self, ignore_charms: bool):
        await self.write_value_to_offset(645, ignore_charms, "bool")

    async def always_fizzle(self) -> bool:
        return await self.read_value_from_offset(646, "bool")

    async def write_always_fizzle(self, always_fizzle: bool):
        await self.write_value_to_offset(646, always_fizzle, "bool")

    async def spell_category(self) -> str:
        return await self.read_string_from_offset(648)

    async def write_spell_category(self, spell_category: str):
        await self.write_string_to_offset(648, spell_category)

    async def show_polymorphed_name(self) -> bool:
        return await self.read_value_from_offset(680, "bool")

    async def write_show_polymorphed_name(self, show_polymorphed_name: bool):
        await self.write_value_to_offset(680, show_polymorphed_name, "bool")

    async def skip_truncation(self) -> bool:
        return await self.read_value_from_offset(681, "bool")

    async def write_skip_truncation(self, skip_truncation: bool):
        await self.write_value_to_offset(681, skip_truncation, "bool")

    async def max_copies(self) -> int:
        return await self.read_value_from_offset(684, "unsigned int")

    async def write_max_copies(self, max_copies: int):
        await self.write_value_to_offset(684, max_copies, "unsigned int")

    async def level_restriction(self) -> int:
        return await self.read_value_from_offset(688, "int")

    async def write_level_restriction(self, level_restriction: int):
        await self.write_value_to_offset(688, level_restriction, "int")

    async def delay_enchantment(self) -> bool:
        return await self.read_value_from_offset(692, "bool")

    async def write_delay_enchantment(self, delay_enchantment: bool):
        await self.write_value_to_offset(692, delay_enchantment, "bool")

    async def delay_enchantment_order(self) -> DelayOrder:
        return await self.read_enum(696, DelayOrder)

    async def write_delay_enchantment_order(self, delay_enchantment_order: DelayOrder):
        await self.write_enum(696, delay_enchantment_order)

    async def previous_spell_name(self) -> str:
        return await self.read_string_from_offset(704)

    async def write_previous_spell_name(self, previous_spell_name: str):
        await self.write_string_to_offset(704, previous_spell_name)

    async def card_front(self) -> str:
        return await self.read_string_from_offset(416)

    async def write_card_front(self, card_front: str):
        await self.write_string_to_offset(416, card_front)

    async def use_gloss(self) -> bool:
        return await self.read_value_from_offset(448, "bool")

    async def write_use_gloss(self, use_gloss: bool):
        await self.write_value_to_offset(448, use_gloss, "bool")


class DynamicSpellTemplate(DynamicMemoryObject, SpellTemplate):
    pass
