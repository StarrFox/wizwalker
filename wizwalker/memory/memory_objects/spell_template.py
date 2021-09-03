from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import DelayOrder, SpellSourceType
from .spell_effect import DynamicSpellEffect


class SpellTemplate(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    # def behaviors(self) -> class BehaviorTemplate*:
    #     return self.read_value_from_offset(72, "class BehaviorTemplate*")

    def name(self) -> str:
        return self.read_string_from_offset(96)

    def write_name(self, name: str):
        self.write_string_to_offset(96, name)

    def description(self) -> str:
        return self.read_string_from_offset(168)

    def write_description(self, description: str):
        self.write_string_to_offset(168, description)

    def display_name(self) -> str:
        return self.read_string_from_offset(136)

    def write_display_name(self, display_name: str):
        self.write_string_to_offset(136, display_name)

    def spell_base(self) -> str:
        return self.read_string_from_offset(208)

    def write_spell_base(self, spell_base: str):
        self.write_string_to_offset(208, spell_base)

    def effects(self) -> list[DynamicSpellEffect]:
        effects = []
        for addr in self.read_shared_vector(240):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects

    def magic_school_name(self) -> str:
        return self.read_string_from_offset(272)

    def write_magic_school_name(self, magic_school_name: str):
        self.write_string_to_offset(272, magic_school_name)

    def type_name(self) -> str:
        return self.read_string_from_offset(312)

    def write_type_name(self, type_name: str):
        self.write_string_to_offset(312, type_name)

    def training_cost(self) -> int:
        return self.read_value_from_offset(344, "int")

    def write_training_cost(self, training_cost: int):
        self.write_value_to_offset(344, training_cost, "int")

    def accuracy(self) -> int:
        return self.read_value_from_offset(348, "int")

    def write_accuracy(self, accuracy: int):
        self.write_value_to_offset(348, accuracy, "int")

    def base_cost(self) -> int:
        return self.read_value_from_offset(200, "int")

    def write_base_cost(self, base_cost: int):
        self.write_value_to_offset(200, base_cost, "int")

    def credits_cost(self) -> int:
        return self.read_value_from_offset(204, "int")

    def write_credits_cost(self, credits_cost: int):
        self.write_value_to_offset(204, credits_cost, "int")

    def booster_pack_icon(self) -> str:
        return self.read_string_from_offset(456)

    def write_booster_pack_icon(self, booster_pack_icon: str):
        self.write_string_to_offset(456, booster_pack_icon)

    def valid_target_spells(self) -> int:
        return self.read_value_from_offset(352, "unsigned int")

    def write_valid_target_spells(self, valid_target_spells: int):
        self.write_value_to_offset(352, valid_target_spells, "unsigned int")

    def pvp(self) -> bool:
        return self.read_value_from_offset(368, "bool")

    def write_pvp(self, pvp: bool):
        self.write_value_to_offset(368, pvp, "bool")

    def pve(self) -> bool:
        return self.read_value_from_offset(369, "bool")

    def write_pve(self, pve: bool):
        self.write_value_to_offset(369, pve, "bool")

    def no_pvp_enchant(self) -> bool:
        return self.read_value_from_offset(370, "bool")

    def write_no_pvp_enchant(self, no_pvp_enchant: bool):
        self.write_value_to_offset(370, no_pvp_enchant, "bool")

    def no_pve_enchant(self) -> bool:
        return self.read_value_from_offset(371, "bool")

    def write_no_pve_enchant(self, no_pve_enchant: bool):
        self.write_value_to_offset(371, no_pve_enchant, "bool")

    def battlegrounds_only(self) -> bool:
        return self.read_value_from_offset(372, "bool")

    def write_battlegrounds_only(self, battlegrounds_only: bool):
        self.write_value_to_offset(372, battlegrounds_only, "bool")

    def treasure(self) -> bool:
        return self.read_value_from_offset(373, "bool")

    def write_treasure(self, treasure: bool):
        self.write_value_to_offset(373, treasure, "bool")

    def no_discard(self) -> bool:
        return self.read_value_from_offset(374, "bool")

    def write_no_discard(self, no_discard: bool):
        self.write_value_to_offset(374, no_discard, "bool")

    def leaves_play_when_cast(self) -> bool:
        return self.read_value_from_offset(492, "bool")

    def write_leaves_play_when_cast(self, leaves_play_when_cast: bool):
        self.write_value_to_offset(492, leaves_play_when_cast, "bool")

    def image_index(self) -> int:
        return self.read_value_from_offset(376, "int")

    def write_image_index(self, image_index: int):
        self.write_value_to_offset(376, image_index, "int")

    def image_name(self) -> str:
        return self.read_string_from_offset(384)

    def write_image_name(self, image_name: str):
        self.write_string_to_offset(384, image_name)

    def cloaked(self) -> bool:
        return self.read_value_from_offset(449, "bool")

    def write_cloaked(self, cloaked: bool):
        self.write_value_to_offset(449, cloaked, "bool")

    def caster_invisible(self) -> bool:
        return self.read_value_from_offset(450, "bool")

    def write_caster_invisible(self, caster_invisible: bool):
        self.write_value_to_offset(450, caster_invisible, "bool")

    def adjectives(self) -> str:
        return self.read_string_from_offset(536)

    def write_adjectives(self, adjectives: str):
        self.write_string_to_offset(536, adjectives)

    def spell_source_type(self) -> SpellSourceType:
        return self.read_enum(488, SpellSourceType)

    def write_spell_source_type(self, spell_source_type: SpellSourceType):
        self.write_enum(488, spell_source_type)

    def cloaked_name(self) -> str:
        return self.read_string_from_offset(496)

    def write_cloaked_name(self, cloaked_name: str):
        self.write_string_to_offset(496, cloaked_name)

    # def purchase_requirements(self) -> class RequirementList*:
    #     return self.read_value_from_offset(568, "class RequirementList*")

    def description_trainer(self) -> str:
        return self.read_string_from_offset(576)

    def write_description_trainer(self, description_trainer: str):
        self.write_string_to_offset(576, description_trainer)

    def description_combat_hud(self) -> str:
        return self.read_string_from_offset(608)

    def write_description_combat_hud(self, description_combat_hud: str):
        self.write_string_to_offset(608, description_combat_hud)

    def display_index(self) -> int:
        return self.read_value_from_offset(640, "int")

    def write_display_index(self, display_index: int):
        self.write_value_to_offset(640, display_index, "int")

    def hidden_from_effects_window(self) -> bool:
        return self.read_value_from_offset(644, "bool")

    def write_hidden_from_effects_window(self, hidden_from_effects_window: bool):
        self.write_value_to_offset(644, hidden_from_effects_window, "bool")

    def ignore_charms(self) -> bool:
        return self.read_value_from_offset(645, "bool")

    def write_ignore_charms(self, ignore_charms: bool):
        self.write_value_to_offset(645, ignore_charms, "bool")

    def always_fizzle(self) -> bool:
        return self.read_value_from_offset(646, "bool")

    def write_always_fizzle(self, always_fizzle: bool):
        self.write_value_to_offset(646, always_fizzle, "bool")

    def spell_category(self) -> str:
        return self.read_string_from_offset(648)

    def write_spell_category(self, spell_category: str):
        self.write_string_to_offset(648, spell_category)

    def show_polymorphed_name(self) -> bool:
        return self.read_value_from_offset(680, "bool")

    def write_show_polymorphed_name(self, show_polymorphed_name: bool):
        self.write_value_to_offset(680, show_polymorphed_name, "bool")

    def skip_truncation(self) -> bool:
        return self.read_value_from_offset(681, "bool")

    def write_skip_truncation(self, skip_truncation: bool):
        self.write_value_to_offset(681, skip_truncation, "bool")

    def max_copies(self) -> int:
        return self.read_value_from_offset(684, "unsigned int")

    def write_max_copies(self, max_copies: int):
        self.write_value_to_offset(684, max_copies, "unsigned int")

    def level_restriction(self) -> int:
        return self.read_value_from_offset(688, "int")

    def write_level_restriction(self, level_restriction: int):
        self.write_value_to_offset(688, level_restriction, "int")

    def delay_enchantment(self) -> bool:
        return self.read_value_from_offset(692, "bool")

    def write_delay_enchantment(self, delay_enchantment: bool):
        self.write_value_to_offset(692, delay_enchantment, "bool")

    def delay_enchantment_order(self) -> DelayOrder:
        return self.read_enum(696, DelayOrder)

    def write_delay_enchantment_order(self, delay_enchantment_order: DelayOrder):
        self.write_enum(696, delay_enchantment_order)

    def previous_spell_name(self) -> str:
        return self.read_string_from_offset(704)

    def write_previous_spell_name(self, previous_spell_name: str):
        self.write_string_to_offset(704, previous_spell_name)

    def card_front(self) -> str:
        return self.read_string_from_offset(416)

    def write_card_front(self, card_front: str):
        self.write_string_to_offset(416, card_front)

    def use_gloss(self) -> bool:
        return self.read_value_from_offset(448, "bool")

    def write_use_gloss(self, use_gloss: bool):
        self.write_value_to_offset(448, use_gloss, "bool")

    def ignore_dispel(self) -> bool:
        return self.read_value_from_offset(736, "bool")

    def write_ignore_dispel(self, ignore_dispel: bool):
        self.write_value_to_offset(736, ignore_dispel, "bool")


class DynamicSpellTemplate(DynamicMemoryObject, SpellTemplate):
    pass
