from typing import List

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import DelayOrder, SpellSourceType
from .spell_effect import DynamicSpellEffect


class SpellTemplate(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # async def behaviors(self) -> class BehaviorTemplate*:
    #     return await self.read_value_from_offset(72, "class BehaviorTemplate*")

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

    async def effects(self) -> List[DynamicSpellEffect]:
        effects = []
        for addr in await self.read_shared_vector(240):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects

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

    async def write_pve(self, pve: bool):
        await self.write_value_to_offset(369, pve, "bool")

    async def no_pvp_enchant(self) -> bool:
        return await self.read_value_from_offset(370, "bool")

    async def write_no_pvp_enchant(self, no_pvp_enchant: bool):
        await self.write_value_to_offset(370, no_pvp_enchant, "bool")

    async def no_pve_enchant(self) -> bool:
        return await self.read_value_from_offset(371, "bool")

    async def write_no_pve_enchant(self, no_pve_enchant: bool):
        await self.write_value_to_offset(371, no_pve_enchant, "bool")

    async def battlegrounds_only(self) -> bool:
        return await self.read_value_from_offset(372, "bool")

    async def write_battlegrounds_only(self, battlegrounds_only: bool):
        await self.write_value_to_offset(372, battlegrounds_only, "bool")

    async def treasure(self) -> bool:
        return await self.read_value_from_offset(373, "bool")

    async def write_treasure(self, treasure: bool):
        await self.write_value_to_offset(373, treasure, "bool")

    async def no_discard(self) -> bool:
        return await self.read_value_from_offset(374, "bool")

    async def write_no_discard(self, no_discard: bool):
        await self.write_value_to_offset(374, no_discard, "bool")

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

    async def ignore_dispel(self) -> bool:
        return await self.read_value_from_offset(736, "bool")

    async def write_ignore_dispel(self, ignore_dispel: bool):
        await self.write_value_to_offset(736, ignore_dispel, "bool")


class DynamicSpellTemplate(DynamicMemoryObject, SpellTemplate):
    pass
