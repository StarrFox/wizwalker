from typing import List

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass


class GameStats(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def max_hitpoints(self) -> int:
        """
        Client's max hitpoints; base + bonus
        """
        base = await self.base_hitpoints()
        bonus = await self.bonus_hitpoints()
        return base + bonus

    async def max_mana(self) -> int:
        """
        Clients's max mana; base + bonus
        """
        base = await self.base_mana()
        bonus = await self.bonus_mana()
        return base + bonus

    async def base_hitpoints(self) -> int:
        return await self.read_value_from_offset(80, "int")

    async def write_base_hitpoints(self, base_hitpoints: int):
        await self.write_value_to_offset(80, base_hitpoints, "int")

    async def base_mana(self) -> int:
        return await self.read_value_from_offset(84, "int")

    async def write_base_mana(self, base_mana: int):
        await self.write_value_to_offset(84, base_mana, "int")

    async def base_gold_pouch(self) -> int:
        return await self.read_value_from_offset(88, "int")

    async def write_base_gold_pouch(self, base_gold_pouch: int):
        await self.write_value_to_offset(88, base_gold_pouch, "int")

    async def base_event_currency1_pouch(self) -> int:
        return await self.read_value_from_offset(92, "int")

    async def write_base_event_currency1_pouch(self, base_event_currency1_pouch: int):
        await self.write_value_to_offset(92, base_event_currency1_pouch, "int")

    async def base_event_currency2_pouch(self) -> int:
        return await self.read_value_from_offset(96, "int")

    async def write_base_event_currency2_pouch(self, base_event_currency2_pouch: int):
        await self.write_value_to_offset(96, base_event_currency2_pouch, "int")

    async def base_pvp_currency_pouch(self) -> int:
        return await self.read_value_from_offset(100, "int")

    async def write_base_pvp_currency_pouch(self, base_pvp_currency_pouch: int):
        await self.write_value_to_offset(100, base_pvp_currency_pouch, "int")

    async def energy_max(self) -> int:
        return await self.read_value_from_offset(104, "int")

    async def write_energy_max(self, energy_max: int):
        await self.write_value_to_offset(104, energy_max, "int")

    async def current_hitpoints(self) -> int:
        return await self.read_value_from_offset(108, "int")

    async def write_current_hitpoints(self, current_hitpoints: int):
        await self.write_value_to_offset(108, current_hitpoints, "int")

    async def current_gold(self) -> int:
        return await self.read_value_from_offset(112, "int")

    async def write_current_gold(self, current_gold: int):
        await self.write_value_to_offset(112, current_gold, "int")

    async def current_event_currency1(self) -> int:
        return await self.read_value_from_offset(116, "int")

    async def write_current_event_currency1(self, current_event_currency1: int):
        await self.write_value_to_offset(116, current_event_currency1, "int")

    async def current_event_currency2(self) -> int:
        return await self.read_value_from_offset(120, "int")

    async def write_current_event_currency2(self, current_event_currency2: int):
        await self.write_value_to_offset(120, current_event_currency2, "int")

    async def current_pvp_currency(self) -> int:
        return await self.read_value_from_offset(124, "int")

    async def write_current_pvp_currency(self, current_pvp_currency: int):
        await self.write_value_to_offset(124, current_pvp_currency, "int")

    async def current_mana(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def write_current_mana(self, current_mana: int):
        await self.write_value_to_offset(128, current_mana, "int")

    async def current_arena_points(self) -> int:
        return await self.read_value_from_offset(132, "int")

    async def write_current_arena_points(self, current_arena_points: int):
        await self.write_value_to_offset(132, current_arena_points, "int")

    async def spell_charge_base(self) -> List[int]:
        return await self.read_dynamic_vector(136, "int")

    # TODO: add write_dynamic_vector
    # async def write_spell_charge_base(self, spell_charge_base: int):
    #     await self.write_value_to_offset(128, spell_charge_base, "int")

    async def potion_max(self) -> float:
        return await self.read_value_from_offset(160, "float")

    async def write_potion_max(self, potion_max: float):
        await self.write_value_to_offset(160, potion_max, "float")

    async def potion_charge(self) -> float:
        return await self.read_value_from_offset(164, "float")

    async def write_potion_charge(self, potion_charge: float):
        await self.write_value_to_offset(164, potion_charge, "float")

    # async def arena_ladder(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(160, "class SharedPointer<class Ladder>")

    # async def derby_ladder(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(176, "class SharedPointer<class Ladder>")

    # async def bracket_lader(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(192, "class SharedPointer<class Ladder>")

    async def bonus_hitpoints(self) -> int:
        return await self.read_value_from_offset(216, "int")

    async def write_bonus_hitpoints(self, bonus_hitpoints: int):
        await self.write_value_to_offset(216, bonus_hitpoints, "int")

    async def bonus_mana(self) -> int:
        return await self.read_value_from_offset(220, "int")

    async def write_bonus_mana(self, bonus_mana: int):
        await self.write_value_to_offset(220, bonus_mana, "int")

    async def bonus_energy(self) -> int:
        return await self.read_value_from_offset(236, "int")

    async def write_bonus_energy(self, bonus_energy: int):
        await self.write_value_to_offset(236, bonus_energy, "int")

    async def critical_hit_percent_all(self) -> float:
        return await self.read_value_from_offset(240, "float")

    async def write_critical_hit_percent_all(self, critical_hit_percent_all: float):
        await self.write_value_to_offset(240, critical_hit_percent_all, "float")

    async def block_percent_all(self) -> float:
        return await self.read_value_from_offset(244, "float")

    async def write_block_percent_all(self, block_percent_all: float):
        await self.write_value_to_offset(244, block_percent_all, "float")

    async def critical_hit_rating_all(self) -> float:
        return await self.read_value_from_offset(248, "float")

    async def write_critical_hit_rating_all(self, critical_hit_rating_all: float):
        await self.write_value_to_offset(248, critical_hit_rating_all, "float")

    async def block_rating_all(self) -> float:
        return await self.read_value_from_offset(252, "float")

    async def write_block_rating_all(self, block_rating_all: float):
        await self.write_value_to_offset(252, block_rating_all, "float")

    async def reference_level(self) -> int:
        return await self.read_value_from_offset(316, "int")

    async def write_reference_level(self, reference_level: int):
        await self.write_value_to_offset(316, reference_level, "int")

    async def highest_character_level_on_account(self) -> int:
        return await self.read_value_from_offset(320, "int")

    async def write_highest_character_level_on_account(
        self, highest_character_level_on_account: int
    ):
        await self.write_value_to_offset(320, highest_character_level_on_account, "int")

    async def pet_act_chance(self) -> int:
        return await self.read_value_from_offset(324, "int")

    async def write_pet_act_chance(self, pet_act_chance: int):
        await self.write_value_to_offset(324, pet_act_chance, "int")

    async def dmg_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(328, "float")

    async def write_dmg_bonus_percent(self, dmg_bonus_percent: float):
        await self.write_value_to_offset(328, dmg_bonus_percent, "float")

    async def dmg_bonus_flat(self) -> List[float]:
        return await self.read_dynamic_vector(352, "float")

    async def write_dmg_bonus_flat(self, dmg_bonus_flat: float):
        await self.write_value_to_offset(352, dmg_bonus_flat, "float")

    async def acc_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(376, "float")

    async def write_acc_bonus_percent(self, acc_bonus_percent: float):
        await self.write_value_to_offset(376, acc_bonus_percent, "float")

    async def ap_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(400, "float")

    async def write_ap_bonus_percent(self, ap_bonus_percent: float):
        await self.write_value_to_offset(400, ap_bonus_percent, "float")

    async def dmg_reduce_percent(self) -> List[float]:
        return await self.read_dynamic_vector(424, "float")

    async def write_dmg_reduce_percent(self, dmg_reduce_percent: float):
        await self.write_value_to_offset(424, dmg_reduce_percent, "float")

    async def dmg_reduce_flat(self) -> List[float]:
        return await self.read_dynamic_vector(448, "float")

    async def write_dmg_reduce_flat(self, dmg_reduce_flat: float):
        await self.write_value_to_offset(448, dmg_reduce_flat, "float")

    async def acc_reduce_percent(self) -> List[float]:
        return await self.read_dynamic_vector(472, "float")

    async def write_acc_reduce_percent(self, acc_reduce_percent: float):
        await self.write_value_to_offset(472, acc_reduce_percent, "float")

    async def heal_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(496, "float")

    async def write_heal_bonus_percent(self, heal_bonus_percent: float):
        await self.write_value_to_offset(496, heal_bonus_percent, "float")

    async def heal_inc_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(520, "float")

    async def write_heal_inc_bonus_percent(self, heal_inc_bonus_percent: float):
        await self.write_value_to_offset(520, heal_inc_bonus_percent, "float")

    async def spell_charge_bonus(self) -> List[int]:
        return await self.read_dynamic_vector(568, "int")

    async def write_spell_charge_bonus(self, spell_charge_bonus: int):
        await self.write_value_to_offset(568, spell_charge_bonus, "int")

    async def dmg_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(688, "float")

    async def write_dmg_bonus_percent_all(self, dmg_bonus_percent_all: float):
        await self.write_value_to_offset(688, dmg_bonus_percent_all, "float")

    async def dmg_bonus_flat_all(self) -> float:
        return await self.read_value_from_offset(692, "float")

    async def write_dmg_bonus_flat_all(self, dmg_bonus_flat_all: float):
        await self.write_value_to_offset(692, dmg_bonus_flat_all, "float")

    async def acc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(696, "float")

    async def write_acc_bonus_percent_all(self, acc_bonus_percent_all: float):
        await self.write_value_to_offset(696, acc_bonus_percent_all, "float")

    async def ap_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(700, "float")

    async def write_ap_bonus_percent_all(self, ap_bonus_percent_all: float):
        await self.write_value_to_offset(700, ap_bonus_percent_all, "float")

    async def dmg_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(704, "float")

    async def write_dmg_reduce_percent_all(self, dmg_reduce_percent_all: float):
        await self.write_value_to_offset(704, dmg_reduce_percent_all, "float")

    async def dmg_reduce_flat_all(self) -> float:
        return await self.read_value_from_offset(708, "float")

    async def write_dmg_reduce_flat_all(self, dmg_reduce_flat_all: float):
        await self.write_value_to_offset(708, dmg_reduce_flat_all, "float")

    async def acc_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(712, "float")

    async def write_acc_reduce_percent_all(self, acc_reduce_percent_all: float):
        await self.write_value_to_offset(712, acc_reduce_percent_all, "float")

    async def heal_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(716, "float")

    async def write_heal_bonus_percent_all(self, heal_bonus_percent_all: float):
        await self.write_value_to_offset(716, heal_bonus_percent_all, "float")

    async def heal_inc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(720, "float")

    async def write_heal_inc_bonus_percent_all(self, heal_inc_bonus_percent_all: float):
        await self.write_value_to_offset(720, heal_inc_bonus_percent_all, "float")

    async def spell_charge_bonus_all(self) -> int:
        return await self.read_value_from_offset(728, "int")

    async def write_spell_charge_bonus_all(self, spell_charge_bonus_all: int):
        await self.write_value_to_offset(728, spell_charge_bonus_all, "int")

    async def power_pip_base(self) -> float:
        return await self.read_value_from_offset(732, "float")

    async def write_power_pip_base(self, power_pip_base: float):
        await self.write_value_to_offset(732, power_pip_base, "float")

    async def power_pip_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(768, "float")

    async def write_power_pip_bonus_percent_all(
        self, power_pip_bonus_percent_all: float
    ):
        await self.write_value_to_offset(768, power_pip_bonus_percent_all, "float")

    async def xp_percent_increase(self) -> float:
        return await self.read_value_from_offset(776, "float")

    async def write_xp_percent_increase(self, xp_percent_increase: float):
        await self.write_value_to_offset(776, xp_percent_increase, "float")

    async def critical_hit_percent_by_school(self) -> List[float]:
        return await self.read_dynamic_vector(592, "float")

    async def write_critical_hit_percent_by_school(
        self, critical_hit_percent_by_school: float
    ):
        await self.write_value_to_offset(592, critical_hit_percent_by_school, "float")

    async def block_percent_by_school(self) -> List[float]:
        return await self.read_dynamic_vector(616, "float")

    async def write_block_percent_by_school(self, block_percent_by_school: float):
        await self.write_value_to_offset(616, block_percent_by_school, "float")

    async def critical_hit_rating_by_school(self) -> List[float]:
        return await self.read_dynamic_vector(640, "float")

    async def write_critical_hit_rating_by_school(
        self, critical_hit_rating_by_school: float
    ):
        await self.write_value_to_offset(640, critical_hit_rating_by_school, "float")

    async def block_rating_by_school(self) -> List[float]:
        return await self.read_dynamic_vector(664, "float")

    async def write_block_rating_by_school(self, block_rating_by_school: float):
        await self.write_value_to_offset(664, block_rating_by_school, "float")

    async def balance_mastery(self) -> int:
        return await self.read_value_from_offset(804, "int")

    async def write_balance_mastery(self, balance_mastery: int):
        await self.write_value_to_offset(804, balance_mastery, "int")

    async def death_mastery(self) -> int:
        return await self.read_value_from_offset(808, "int")

    async def write_death_mastery(self, death_mastery: int):
        await self.write_value_to_offset(808, death_mastery, "int")

    async def fire_mastery(self) -> int:
        return await self.read_value_from_offset(812, "int")

    async def write_fire_mastery(self, fire_mastery: int):
        await self.write_value_to_offset(812, fire_mastery, "int")

    async def ice_mastery(self) -> int:
        return await self.read_value_from_offset(816, "int")

    async def write_ice_mastery(self, ice_mastery: int):
        await self.write_value_to_offset(816, ice_mastery, "int")

    async def life_mastery(self) -> int:
        return await self.read_value_from_offset(820, "int")

    async def write_life_mastery(self, life_mastery: int):
        await self.write_value_to_offset(820, life_mastery, "int")

    async def myth_mastery(self) -> int:
        return await self.read_value_from_offset(824, "int")

    async def write_myth_mastery(self, myth_mastery: int):
        await self.write_value_to_offset(824, myth_mastery, "int")

    async def storm_mastery(self) -> int:
        return await self.read_value_from_offset(828, "int")

    async def write_storm_mastery(self, storm_mastery: int):
        await self.write_value_to_offset(828, storm_mastery, "int")

    async def maximum_number_of_islands(self) -> int:
        return await self.read_value_from_offset(832, "int")

    async def write_maximum_number_of_islands(self, maximum_number_of_islands: int):
        await self.write_value_to_offset(832, maximum_number_of_islands, "int")

    async def gardening_level(self) -> int:
        return await self.read_value_from_offset(836, "unsigned char")

    async def write_gardening_level(self, gardening_level: int):
        await self.write_value_to_offset(836, gardening_level, "unsigned char")

    async def gardening_xp(self) -> int:
        return await self.read_value_from_offset(840, "int")

    async def write_gardening_xp(self, gardening_xp: int):
        await self.write_value_to_offset(840, gardening_xp, "int")

    async def invisible_to_friends(self) -> bool:
        return await self.read_value_from_offset(844, "bool")

    async def write_invisible_to_friends(self, invisible_to_friends: bool):
        await self.write_value_to_offset(844, invisible_to_friends, "bool")

    async def show_item_lock(self) -> bool:
        return await self.read_value_from_offset(845, "bool")

    async def write_show_item_lock(self, show_item_lock: bool):
        await self.write_value_to_offset(845, show_item_lock, "bool")

    async def quest_finder_enabled(self) -> bool:
        return await self.read_value_from_offset(846, "bool")

    async def write_quest_finder_enabled(self, quest_finder_enabled: bool):
        await self.write_value_to_offset(846, quest_finder_enabled, "bool")

    async def buddy_list_limit(self) -> int:
        return await self.read_value_from_offset(848, "int")

    async def write_buddy_list_limit(self, buddy_list_limit: int):
        await self.write_value_to_offset(848, buddy_list_limit, "int")

    async def dont_allow_friend_finder_codes(self) -> bool:
        return await self.read_value_from_offset(856, "bool")

    async def write_dont_allow_friend_finder_codes(
        self, dont_allow_friend_finder_codes: bool
    ):
        await self.write_value_to_offset(856, dont_allow_friend_finder_codes, "bool")

    async def stun_resistance_percent(self) -> float:
        return await self.read_value_from_offset(852, "float")

    async def write_stun_resistance_percent(self, stun_resistance_percent: float):
        await self.write_value_to_offset(852, stun_resistance_percent, "float")

    async def shadow_magic_unlocked(self) -> bool:
        return await self.read_value_from_offset(864, "bool")

    async def write_shadow_magic_unlocked(self, shadow_magic_unlocked: bool):
        await self.write_value_to_offset(864, shadow_magic_unlocked, "bool")

    async def shadow_pip_max(self) -> int:
        return await self.read_value_from_offset(860, "int")

    async def write_shadow_pip_max(self, shadow_pip_max: int):
        await self.write_value_to_offset(860, shadow_pip_max, "int")

    async def fishing_level(self) -> int:
        return await self.read_value_from_offset(865, "unsigned char")

    async def write_fishing_level(self, fishing_level: int):
        await self.write_value_to_offset(865, fishing_level, "unsigned char")

    async def fishing_xp(self) -> int:
        return await self.read_value_from_offset(868, "int")

    async def write_fishing_xp(self, fishing_xp: int):
        await self.write_value_to_offset(868, fishing_xp, "int")

    async def fishing_luck_bonus_percent(self) -> List[float]:
        return await self.read_dynamic_vector(544, "float")

    async def write_fishing_luck_bonus_percent(self, fishing_luck_bonus_percent: float):
        await self.write_value_to_offset(544, fishing_luck_bonus_percent, "float")

    async def fishing_luck_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(724, "float")

    async def write_fishing_luck_bonus_percent_all(
        self, fishing_luck_bonus_percent_all: float
    ):
        await self.write_value_to_offset(724, fishing_luck_bonus_percent_all, "float")

    async def subscriber_benefit_flags(self) -> int:
        return await self.read_value_from_offset(872, "unsigned int")

    async def write_subscriber_benefit_flags(self, subscriber_benefit_flags: int):
        await self.write_value_to_offset(872, subscriber_benefit_flags, "unsigned int")

    async def elixir_benefit_flags(self) -> int:
        return await self.read_value_from_offset(876, "unsigned int")

    async def write_elixir_benefit_flags(self, elixir_benefit_flags: int):
        await self.write_value_to_offset(876, elixir_benefit_flags, "unsigned int")

    async def shadow_pip_bonus_percent(self) -> float:
        return await self.read_value_from_offset(772, "float")

    async def write_shadow_pip_bonus_percent(self, shadow_pip_bonus_percent: float):
        await self.write_value_to_offset(772, shadow_pip_bonus_percent, "float")

    async def wisp_bonus_percent(self) -> float:
        return await self.read_value_from_offset(796, "float")

    async def write_wisp_bonus_percent(self, wisp_bonus_percent: float):
        await self.write_value_to_offset(796, wisp_bonus_percent, "float")

    async def pip_conversion_rating_all(self) -> float:
        return await self.read_value_from_offset(280, "float")

    async def write_pip_conversion_rating_all(self, pip_conversion_rating_all: float):
        await self.write_value_to_offset(280, pip_conversion_rating_all, "float")

    async def pip_conversion_rating_per_school(self) -> List[float]:
        return await self.read_dynamic_vector(256, "float")

    async def write_pip_conversion_rating_per_school(
        self, pip_conversion_rating_per_school: float
    ):
        await self.write_value_to_offset(256, pip_conversion_rating_per_school, "float")

    async def pip_conversion_percent_all(self) -> float:
        return await self.read_value_from_offset(312, "float")

    async def write_pip_conversion_percent_all(self, pip_conversion_percent_all: float):
        await self.write_value_to_offset(312, pip_conversion_percent_all, "float")

    async def pip_conversion_percent_per_school(self) -> List[float]:
        return await self.read_dynamic_vector(288, "float")

    async def write_pip_conversion_percent_per_school(
        self, pip_conversion_percent_per_school: float
    ):
        await self.write_value_to_offset(
            288, pip_conversion_percent_per_school, "float"
        )

    async def monster_magic_level(self) -> int:
        return await self.read_value_from_offset(880, "unsigned char")

    async def write_monster_magic_level(self, monster_magic_level: int):
        await self.write_value_to_offset(880, monster_magic_level, "unsigned char")

    async def monster_magic_xp(self) -> int:
        return await self.read_value_from_offset(884, "int")

    async def write_monster_magic_xp(self, monster_magic_xp: int):
        await self.write_value_to_offset(884, monster_magic_xp, "int")

    async def player_chat_channel_is_public(self) -> bool:
        return await self.read_value_from_offset(888, "bool")

    async def write_player_chat_channel_is_public(
        self, player_chat_channel_is_public: bool
    ):
        await self.write_value_to_offset(888, player_chat_channel_is_public, "bool")

    async def extra_inventory_space(self) -> int:
        return await self.read_value_from_offset(892, "int")

    async def write_extra_inventory_space(self, extra_inventory_space: int):
        await self.write_value_to_offset(892, extra_inventory_space, "int")

    async def remember_last_realm(self) -> bool:
        return await self.read_value_from_offset(896, "bool")

    async def write_remember_last_realm(self, remember_last_realm: bool):
        await self.write_value_to_offset(896, remember_last_realm, "bool")

    async def new_spellbook_layout_warning(self) -> bool:
        return await self.read_value_from_offset(897, "bool")

    async def write_new_spellbook_layout_warning(
        self, new_spellbook_layout_warning: bool
    ):
        await self.write_value_to_offset(897, new_spellbook_layout_warning, "bool")

    async def pip_conversion_base_all_schools(self) -> int:
        return await self.read_value_from_offset(736, "int")

    async def write_pip_conversion_base_all_schools(
        self, pip_conversion_base_all_schools: int
    ):
        await self.write_value_to_offset(736, pip_conversion_base_all_schools, "int")

    async def pip_conversion_base_per_school(self) -> List[int]:
        return await self.read_dynamic_vector(744, "int")

    async def write_pip_conversion_base_per_school(
        self, pip_conversion_base_per_school: int
    ):
        await self.write_value_to_offset(744, pip_conversion_base_per_school, "int")

    async def purchased_custom_emotes1(self) -> int:
        return await self.read_value_from_offset(900, "unsigned int")

    async def write_purchased_custom_emotes1(self, purchased_custom_emotes1: int):
        await self.write_value_to_offset(900, purchased_custom_emotes1, "unsigned int")

    async def purchased_custom_teleport_effects1(self) -> int:
        return await self.read_value_from_offset(904, "unsigned int")

    async def write_purchased_custom_teleport_effects1(
        self, purchased_custom_teleport_effects1: int
    ):
        await self.write_value_to_offset(
            904, purchased_custom_teleport_effects1, "unsigned int"
        )

    async def equipped_teleport_effect(self) -> int:
        return await self.read_value_from_offset(908, "unsigned int")

    async def write_equipped_teleport_effect(self, equipped_teleport_effect: int):
        await self.write_value_to_offset(908, equipped_teleport_effect, "unsigned int")

    async def highest_world1_id(self) -> int:
        return await self.read_value_from_offset(912, "unsigned int")

    async def write_highest_world1_id(self, highest_world1_id: int):
        await self.write_value_to_offset(912, highest_world1_id, "unsigned int")

    async def highest_world2_id(self) -> int:
        return await self.read_value_from_offset(916, "unsigned int")

    async def write_highest_world2_id(self, highest_world2_i_d: int):
        await self.write_value_to_offset(916, highest_world2_i_d, "unsigned int")

    async def active_class_projects_list(self) -> int:
        return await self.read_value_from_offset(920, "unsigned int")

    async def write_active_class_projects_list(self, active_class_projects_list: int):
        await self.write_value_to_offset(
            920, active_class_projects_list, "unsigned int"
        )

    async def disabled_item_slot_ids(self) -> int:
        return await self.read_value_from_offset(936, "unsigned int")

    async def write_disabled_item_slot_ids(self, disabled_item_slot_ids: int):
        await self.write_value_to_offset(936, disabled_item_slot_ids, "unsigned int")

    async def adventure_power_cooldown_time(self) -> int:
        return await self.read_value_from_offset(952, "unsigned int")

    async def write_adventure_power_cooldown_time(
        self, adventure_power_cooldown_time: int
    ):
        await self.write_value_to_offset(
            952, adventure_power_cooldown_time, "unsigned int"
        )

    async def purchased_custom_emotes2(self) -> int:
        return await self.read_value_from_offset(956, "unsigned int")

    async def write_purchased_custom_emotes2(self, purchased_custom_emotes2: int):
        await self.write_value_to_offset(956, purchased_custom_emotes2, "unsigned int")

    async def purchased_custom_teleport_effects2(self) -> int:
        return await self.read_value_from_offset(960, "unsigned int")

    async def write_purchased_custom_teleport_effects2(
        self, purchased_custom_teleport_effects2: int
    ):
        await self.write_value_to_offset(
            960, purchased_custom_teleport_effects2, "unsigned int"
        )

    async def purchased_custom_emotes3(self) -> int:
        return await self.read_value_from_offset(964, "unsigned int")

    async def write_purchased_custom_emotes3(self, purchased_custom_emotes3: int):
        await self.write_value_to_offset(964, purchased_custom_emotes3, "unsigned int")

    async def purchased_custom_teleport_effects3(self) -> int:
        return await self.read_value_from_offset(968, "unsigned int")

    async def write_purchased_custom_teleport_effects3(
        self, purchased_custom_teleport_effects3: int
    ):
        await self.write_value_to_offset(
            968, purchased_custom_teleport_effects3, "unsigned int"
        )

    async def shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(972, "float")

    async def write_shadow_pip_rating(self, shadow_pip_rating: float):
        await self.write_value_to_offset(972, shadow_pip_rating, "float")

    async def bonus_shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(976, "float")

    async def write_bonus_shadow_pip_rating(self, bonus_shadow_pip_rating: float):
        await self.write_value_to_offset(976, bonus_shadow_pip_rating, "float")

    async def shadow_pip_rate_accumulated(self) -> float:
        return await self.read_value_from_offset(980, "float")

    async def write_shadow_pip_rate_accumulated(
        self, shadow_pip_rate_accumulated: float
    ):
        await self.write_value_to_offset(980, shadow_pip_rate_accumulated, "float")

    async def shadow_pip_rate_threshold(self) -> float:
        return await self.read_value_from_offset(984, "float")

    async def write_shadow_pip_rate_threshold(self, shadow_pip_rate_threshold: float):
        await self.write_value_to_offset(984, shadow_pip_rate_threshold, "float")

    async def shadow_pip_rate_percentage(self) -> int:
        return await self.read_value_from_offset(988, "int")

    async def write_shadow_pip_rate_percentage(self, shadow_pip_rate_percentage: int):
        await self.write_value_to_offset(988, shadow_pip_rate_percentage, "int")

    async def friendly_player(self) -> bool:
        return await self.read_value_from_offset(992, "bool")

    async def write_friendly_player(self, friendly_player: bool):
        await self.write_value_to_offset(992, friendly_player, "bool")

    async def emoji_skin_tone(self) -> int:
        return await self.read_value_from_offset(996, "int")

    async def write_emoji_skin_tone(self, emoji_skin_tone: int):
        await self.write_value_to_offset(996, emoji_skin_tone, "int")

    async def show_pvp_option(self) -> int:
        return await self.read_value_from_offset(1000, "unsigned int")

    async def write_show_pvp_option(self, show_pvp_option: int):
        await self.write_value_to_offset(1000, show_pvp_option, "unsigned int")

    async def favorite_slot(self) -> int:
        return await self.read_value_from_offset(1004, "int")

    async def write_favorite_slot(self, favorite_slot: int):
        await self.write_value_to_offset(1004, favorite_slot, "int")

    async def cantrip_level(self) -> int:
        return await self.read_value_from_offset(1008, "unsigned char")

    async def write_cantrip_level(self, cantrip_level: int):
        await self.write_value_to_offset(1008, cantrip_level, "unsigned char")

    async def cantrip_xp(self) -> int:
        return await self.read_value_from_offset(1012, "int")

    async def write_cantrip_xp(self, cantrip_xp: int):
        await self.write_value_to_offset(1012, cantrip_xp, "int")


class CurrentGameStats(GameStats):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_player_stat_base()


class DynamicGameStats(DynamicMemoryObject, GameStats):
    pass
