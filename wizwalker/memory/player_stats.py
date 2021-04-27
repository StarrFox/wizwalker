from .memory_object import MemoryObject


class PlayerStats(MemoryObject):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_player_stat_base()

    async def max_hitpoints(self):
        base = await self.base_hitpoints()
        bonus = await self.bonus_hitpoints()
        return base + bonus

    async def max_mana(self):
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

    async def energy_max(self) -> int:
        return await self.read_value_from_offset(100, "int")

    async def write_energy_max(self, energy_max: int):
        await self.write_value_to_offset(100, energy_max, "int")

    async def current_hitpoints(self) -> int:
        return await self.read_value_from_offset(104, "int")

    async def write_current_hitpoints(self, current_hitpoints: int):
        await self.write_value_to_offset(104, current_hitpoints, "int")

    async def current_gold(self) -> int:
        return await self.read_value_from_offset(108, "int")

    async def write_current_gold(self, current_gold: int):
        await self.write_value_to_offset(108, current_gold, "int")

    async def current_event_currency1(self) -> int:
        return await self.read_value_from_offset(112, "int")

    async def write_current_event_currency1(self, current_event_currency1: int):
        await self.write_value_to_offset(112, current_event_currency1, "int")

    async def current_event_currency2(self) -> int:
        return await self.read_value_from_offset(116, "int")

    async def write_current_event_currency2(self, current_event_currency2: int):
        await self.write_value_to_offset(116, current_event_currency2, "int")

    async def current_mana(self) -> int:
        return await self.read_value_from_offset(120, "int")

    async def write_current_mana(self, current_mana: int):
        await self.write_value_to_offset(120, current_mana, "int")

    async def current_arena_points(self) -> int:
        return await self.read_value_from_offset(124, "int")

    async def write_current_arena_points(self, current_arena_points: int):
        await self.write_value_to_offset(124, current_arena_points, "int")

    async def spell_charge_base(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def write_spell_charge_base(self, spell_charge_base: int):
        await self.write_value_to_offset(128, spell_charge_base, "int")

    async def potion_max(self) -> float:
        return await self.read_value_from_offset(152, "float")

    async def write_potion_max(self, potion_max: float):
        await self.write_value_to_offset(152, potion_max, "float")

    async def potion_charge(self) -> float:
        return await self.read_value_from_offset(156, "float")

    async def write_potion_charge(self, potion_charge: float):
        await self.write_value_to_offset(156, potion_charge, "float")

    # async def p_arena_ladder(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(160, "class SharedPointer<class Ladder>")
    #
    # async def write_p_arena_ladder(self, p_arena_ladder: class SharedPointer<class Ladder>):
    #     await self.write_value_to_offset(160, p_arena_ladder, "class SharedPointer<class Ladder>")
    #
    # async def p_derby_ladder(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(176, "class SharedPointer<class Ladder>")
    #
    # async def write_p_derby_ladder(self, p_derby_ladder: class SharedPointer<class Ladder>):
    #     await self.write_value_to_offset(176, p_derby_ladder, "class SharedPointer<class Ladder>")
    #
    # async def bracket_lader(self) -> class SharedPointer<class Ladder>:
    #     return await self.read_value_from_offset(192, "class SharedPointer<class Ladder>")
    #
    # async def write_bracket_lader(self, bracket_lader: class SharedPointer<class Ladder>):
    #     await self.write_value_to_offset(192, bracket_lader, "class SharedPointer<class Ladder>")

    async def bonus_hitpoints(self) -> int:
        return await self.read_value_from_offset(208, "int")

    async def write_bonus_hitpoints(self, bonus_hitpoints: int):
        await self.write_value_to_offset(208, bonus_hitpoints, "int")

    async def bonus_mana(self) -> int:
        return await self.read_value_from_offset(212, "int")

    async def write_bonus_mana(self, bonus_mana: int):
        await self.write_value_to_offset(212, bonus_mana, "int")

    async def bonus_energy(self) -> int:
        return await self.read_value_from_offset(228, "int")

    async def write_bonus_energy(self, bonus_energy: int):
        await self.write_value_to_offset(228, bonus_energy, "int")

    async def critical_hit_percent_all(self) -> float:
        return await self.read_value_from_offset(232, "float")

    async def write_critical_hit_percent_all(self, critical_hit_percent_all: float):
        await self.write_value_to_offset(232, critical_hit_percent_all, "float")

    async def block_percent_all(self) -> float:
        return await self.read_value_from_offset(236, "float")

    async def write_block_percent_all(self, block_percent_all: float):
        await self.write_value_to_offset(236, block_percent_all, "float")

    async def critical_hit_rating_all(self) -> float:
        return await self.read_value_from_offset(240, "float")

    async def write_critical_hit_rating_all(self, critical_hit_rating_all: float):
        await self.write_value_to_offset(240, critical_hit_rating_all, "float")

    async def block_rating_all(self) -> float:
        return await self.read_value_from_offset(244, "float")

    async def write_block_rating_all(self, block_rating_all: float):
        await self.write_value_to_offset(244, block_rating_all, "float")

    async def reference_level(self) -> int:
        return await self.read_value_from_offset(308, "int")

    async def write_reference_level(self, reference_level: int):
        await self.write_value_to_offset(308, reference_level, "int")

    async def highest_character_level_on_account(self) -> int:
        return await self.read_value_from_offset(312, "int")

    async def write_highest_character_level_on_account(
        self, highest_character_level_on_account: int
    ):
        await self.write_value_to_offset(312, highest_character_level_on_account, "int")

    async def pet_act_chance(self) -> int:
        return await self.read_value_from_offset(316, "int")

    async def write_pet_act_chance(self, pet_act_chance: int):
        await self.write_value_to_offset(316, pet_act_chance, "int")

    async def dmg_bonus_percent(self) -> float:
        return await self.read_value_from_offset(320, "float")

    async def write_dmg_bonus_percent(self, dmg_bonus_percent: float):
        await self.write_value_to_offset(320, dmg_bonus_percent, "float")

    async def dmg_bonus_flat(self) -> float:
        return await self.read_value_from_offset(344, "float")

    async def write_dmg_bonus_flat(self, dmg_bonus_flat: float):
        await self.write_value_to_offset(344, dmg_bonus_flat, "float")

    async def acc_bonus_percent(self) -> float:
        return await self.read_value_from_offset(368, "float")

    async def write_acc_bonus_percent(self, acc_bonus_percent: float):
        await self.write_value_to_offset(368, acc_bonus_percent, "float")

    async def ap_bonus_percent(self) -> float:
        return await self.read_value_from_offset(392, "float")

    async def write_ap_bonus_percent(self, ap_bonus_percent: float):
        await self.write_value_to_offset(392, ap_bonus_percent, "float")

    async def dmg_reduce_percent(self) -> float:
        return await self.read_value_from_offset(416, "float")

    async def write_dmg_reduce_percent(self, dmg_reduce_percent: float):
        await self.write_value_to_offset(416, dmg_reduce_percent, "float")

    async def dmg_reduce_flat(self) -> float:
        return await self.read_value_from_offset(440, "float")

    async def write_dmg_reduce_flat(self, dmg_reduce_flat: float):
        await self.write_value_to_offset(440, dmg_reduce_flat, "float")

    async def acc_reduce_percent(self) -> float:
        return await self.read_value_from_offset(464, "float")

    async def write_acc_reduce_percent(self, acc_reduce_percent: float):
        await self.write_value_to_offset(464, acc_reduce_percent, "float")

    async def heal_bonus_percent(self) -> float:
        return await self.read_value_from_offset(488, "float")

    async def write_heal_bonus_percent(self, heal_bonus_percent: float):
        await self.write_value_to_offset(488, heal_bonus_percent, "float")

    async def heal_inc_bonus_percent(self) -> float:
        return await self.read_value_from_offset(512, "float")

    async def write_heal_inc_bonus_percent(self, heal_inc_bonus_percent: float):
        await self.write_value_to_offset(512, heal_inc_bonus_percent, "float")

    async def spell_charge_bonus(self) -> int:
        return await self.read_value_from_offset(560, "int")

    async def write_spell_charge_bonus(self, spell_charge_bonus: int):
        await self.write_value_to_offset(560, spell_charge_bonus, "int")

    async def dmg_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(680, "float")

    async def write_dmg_bonus_percent_all(self, dmg_bonus_percent_all: float):
        await self.write_value_to_offset(680, dmg_bonus_percent_all, "float")

    async def dmg_bonus_flat_all(self) -> float:
        return await self.read_value_from_offset(684, "float")

    async def write_dmg_bonus_flat_all(self, dmg_bonus_flat_all: float):
        await self.write_value_to_offset(684, dmg_bonus_flat_all, "float")

    async def acc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(688, "float")

    async def write_acc_bonus_percent_all(self, acc_bonus_percent_all: float):
        await self.write_value_to_offset(688, acc_bonus_percent_all, "float")

    async def ap_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(692, "float")

    async def write_ap_bonus_percent_all(self, ap_bonus_percent_all: float):
        await self.write_value_to_offset(692, ap_bonus_percent_all, "float")

    async def dmg_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(696, "float")

    async def write_dmg_reduce_percent_all(self, dmg_reduce_percent_all: float):
        await self.write_value_to_offset(696, dmg_reduce_percent_all, "float")

    async def dmg_reduce_flat_all(self) -> float:
        return await self.read_value_from_offset(700, "float")

    async def write_dmg_reduce_flat_all(self, dmg_reduce_flat_all: float):
        await self.write_value_to_offset(700, dmg_reduce_flat_all, "float")

    async def acc_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(704, "float")

    async def write_acc_reduce_percent_all(self, acc_reduce_percent_all: float):
        await self.write_value_to_offset(704, acc_reduce_percent_all, "float")

    async def heal_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(708, "float")

    async def write_heal_bonus_percent_all(self, heal_bonus_percent_all: float):
        await self.write_value_to_offset(708, heal_bonus_percent_all, "float")

    async def heal_inc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(712, "float")

    async def write_heal_inc_bonus_percent_all(self, heal_inc_bonus_percent_all: float):
        await self.write_value_to_offset(712, heal_inc_bonus_percent_all, "float")

    async def spell_charge_bonus_all(self) -> int:
        return await self.read_value_from_offset(720, "int")

    async def write_spell_charge_bonus_all(self, spell_charge_bonus_all: int):
        await self.write_value_to_offset(720, spell_charge_bonus_all, "int")

    async def power_pip_base(self) -> float:
        return await self.read_value_from_offset(724, "float")

    async def write_power_pip_base(self, power_pip_base: float):
        await self.write_value_to_offset(724, power_pip_base, "float")

    async def power_pip_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(760, "float")

    async def write_power_pip_bonus_percent_all(
        self, power_pip_bonus_percent_all: float
    ):
        await self.write_value_to_offset(760, power_pip_bonus_percent_all, "float")

    async def xp_percent_increase(self) -> float:
        return await self.read_value_from_offset(768, "float")

    async def write_xp_percent_increase(self, xp_percent_increase: float):
        await self.write_value_to_offset(768, xp_percent_increase, "float")

    async def critical_hit_percent_by_school(self) -> float:
        return await self.read_value_from_offset(584, "float")

    async def write_critical_hit_percent_by_school(
        self, critical_hit_percent_by_school: float
    ):
        await self.write_value_to_offset(584, critical_hit_percent_by_school, "float")

    async def block_percent_by_school(self) -> float:
        return await self.read_value_from_offset(608, "float")

    async def write_block_percent_by_school(self, block_percent_by_school: float):
        await self.write_value_to_offset(608, block_percent_by_school, "float")

    async def critical_hit_rating_by_school(self) -> float:
        return await self.read_value_from_offset(632, "float")

    async def write_critical_hit_rating_by_school(
        self, critical_hit_rating_by_school: float
    ):
        await self.write_value_to_offset(632, critical_hit_rating_by_school, "float")

    async def block_rating_by_school(self) -> float:
        return await self.read_value_from_offset(656, "float")

    async def write_block_rating_by_school(self, block_rating_by_school: float):
        await self.write_value_to_offset(656, block_rating_by_school, "float")

    async def balance_mastery(self) -> int:
        return await self.read_value_from_offset(792, "int")

    async def write_balance_mastery(self, balance_mastery: int):
        await self.write_value_to_offset(792, balance_mastery, "int")

    async def death_mastery(self) -> int:
        return await self.read_value_from_offset(796, "int")

    async def write_death_mastery(self, death_mastery: int):
        await self.write_value_to_offset(796, death_mastery, "int")

    async def fire_mastery(self) -> int:
        return await self.read_value_from_offset(800, "int")

    async def write_fire_mastery(self, fire_mastery: int):
        await self.write_value_to_offset(800, fire_mastery, "int")

    async def ice_mastery(self) -> int:
        return await self.read_value_from_offset(804, "int")

    async def write_ice_mastery(self, ice_mastery: int):
        await self.write_value_to_offset(804, ice_mastery, "int")

    async def life_mastery(self) -> int:
        return await self.read_value_from_offset(808, "int")

    async def write_life_mastery(self, life_mastery: int):
        await self.write_value_to_offset(808, life_mastery, "int")

    async def myth_mastery(self) -> int:
        return await self.read_value_from_offset(812, "int")

    async def write_myth_mastery(self, myth_mastery: int):
        await self.write_value_to_offset(812, myth_mastery, "int")

    async def storm_mastery(self) -> int:
        return await self.read_value_from_offset(816, "int")

    async def write_storm_mastery(self, storm_mastery: int):
        await self.write_value_to_offset(816, storm_mastery, "int")

    async def maximum_number_of_islands(self) -> int:
        return await self.read_value_from_offset(820, "int")

    async def write_maximum_number_of_islands(self, maximum_number_of_islands: int):
        await self.write_value_to_offset(820, maximum_number_of_islands, "int")

    async def gardening_level(self) -> int:
        return await self.read_value_from_offset(824, "unsigned char")

    async def write_gardening_level(self, gardening_level: int):
        await self.write_value_to_offset(824, gardening_level, "unsigned char")

    async def gardening_x_p(self) -> int:
        return await self.read_value_from_offset(828, "int")

    async def write_gardening_x_p(self, gardening_x_p: int):
        await self.write_value_to_offset(828, gardening_x_p, "int")

    async def invisible_to_friends(self) -> bool:
        return await self.read_value_from_offset(832, "bool")

    async def write_invisible_to_friends(self, invisible_to_friends: bool):
        await self.write_value_to_offset(832, invisible_to_friends, "bool")

    async def show_item_lock(self) -> bool:
        return await self.read_value_from_offset(833, "bool")

    async def write_show_item_lock(self, show_item_lock: bool):
        await self.write_value_to_offset(833, show_item_lock, "bool")

    async def quest_finder_enabled(self) -> bool:
        return await self.read_value_from_offset(834, "bool")

    async def write_quest_finder_enabled(self, quest_finder_enabled: bool):
        await self.write_value_to_offset(834, quest_finder_enabled, "bool")

    async def buddy_list_limit(self) -> int:
        return await self.read_value_from_offset(836, "int")

    async def write_buddy_list_limit(self, buddy_list_limit: int):
        await self.write_value_to_offset(836, buddy_list_limit, "int")

    async def dont_allow_friend_finder_codes(self) -> bool:
        return await self.read_value_from_offset(844, "bool")

    async def write_dont_allow_friend_finder_codes(
        self, dont_allow_friend_finder_codes: bool
    ):
        await self.write_value_to_offset(844, dont_allow_friend_finder_codes, "bool")

    async def stun_resistance_percent(self) -> float:
        return await self.read_value_from_offset(840, "float")

    async def write_stun_resistance_percent(self, stun_resistance_percent: float):
        await self.write_value_to_offset(840, stun_resistance_percent, "float")

    async def shadow_magic_unlocked(self) -> bool:
        return await self.read_value_from_offset(852, "bool")

    async def write_shadow_magic_unlocked(self, shadow_magic_unlocked: bool):
        await self.write_value_to_offset(852, shadow_magic_unlocked, "bool")

    async def shadow_pip_max(self) -> int:
        return await self.read_value_from_offset(848, "int")

    async def write_shadow_pip_max(self, shadow_pip_max: int):
        await self.write_value_to_offset(848, shadow_pip_max, "int")

    async def fishing_level(self) -> int:
        return await self.read_value_from_offset(853, "unsigned char")

    async def write_fishing_level(self, fishing_level: int):
        await self.write_value_to_offset(853, fishing_level, "unsigned char")

    async def fishing_x_p(self) -> int:
        return await self.read_value_from_offset(856, "int")

    async def write_fishing_x_p(self, fishing_x_p: int):
        await self.write_value_to_offset(856, fishing_x_p, "int")

    async def fishing_luck_bonus_percent(self) -> float:
        return await self.read_value_from_offset(536, "float")

    async def write_fishing_luck_bonus_percent(self, fishing_luck_bonus_percent: float):
        await self.write_value_to_offset(536, fishing_luck_bonus_percent, "float")

    async def fishing_luck_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(716, "float")

    async def write_fishing_luck_bonus_percent_all(
        self, fishing_luck_bonus_percent_all: float
    ):
        await self.write_value_to_offset(716, fishing_luck_bonus_percent_all, "float")

    async def subscriber_benefit_flags(self) -> int:
        return await self.read_value_from_offset(860, "unsigned int")

    async def write_subscriber_benefit_flags(self, subscriber_benefit_flags: int):
        await self.write_value_to_offset(860, subscriber_benefit_flags, "unsigned int")

    async def elixir_benefit_flags(self) -> int:
        return await self.read_value_from_offset(864, "unsigned int")

    async def write_elixir_benefit_flags(self, elixir_benefit_flags: int):
        await self.write_value_to_offset(864, elixir_benefit_flags, "unsigned int")

    async def shadow_pip_bonus_percent(self) -> float:
        return await self.read_value_from_offset(764, "float")

    async def write_shadow_pip_bonus_percent(self, shadow_pip_bonus_percent: float):
        await self.write_value_to_offset(764, shadow_pip_bonus_percent, "float")

    async def wisp_bonus_percent(self) -> float:
        return await self.read_value_from_offset(784, "float")

    async def write_wisp_bonus_percent(self, wisp_bonus_percent: float):
        await self.write_value_to_offset(784, wisp_bonus_percent, "float")

    async def pip_conversion_rating_all(self) -> float:
        return await self.read_value_from_offset(272, "float")

    async def write_pip_conversion_rating_all(self, pip_conversion_rating_all: float):
        await self.write_value_to_offset(272, pip_conversion_rating_all, "float")

    async def pip_conversion_rating_per_school(self) -> float:
        return await self.read_value_from_offset(248, "float")

    async def write_pip_conversion_rating_per_school(
        self, pip_conversion_rating_per_school: float
    ):
        await self.write_value_to_offset(248, pip_conversion_rating_per_school, "float")

    async def pip_conversion_percent_all(self) -> float:
        return await self.read_value_from_offset(304, "float")

    async def write_pip_conversion_percent_all(self, pip_conversion_percent_all: float):
        await self.write_value_to_offset(304, pip_conversion_percent_all, "float")

    async def pip_conversion_percent_per_school(self) -> float:
        return await self.read_value_from_offset(280, "float")

    async def write_pip_conversion_percent_per_school(
        self, pip_conversion_percent_per_school: float
    ):
        await self.write_value_to_offset(
            280, pip_conversion_percent_per_school, "float"
        )

    async def monster_magic_level(self) -> int:
        return await self.read_value_from_offset(868, "unsigned char")

    async def write_monster_magic_level(self, monster_magic_level: int):
        await self.write_value_to_offset(868, monster_magic_level, "unsigned char")

    async def monster_magic_x_p(self) -> int:
        return await self.read_value_from_offset(872, "int")

    async def write_monster_magic_x_p(self, monster_magic_x_p: int):
        await self.write_value_to_offset(872, monster_magic_x_p, "int")

    async def player_chat_channel_is_public(self) -> bool:
        return await self.read_value_from_offset(876, "bool")

    async def write_player_chat_channel_is_public(
        self, player_chat_channel_is_public: bool
    ):
        await self.write_value_to_offset(876, player_chat_channel_is_public, "bool")

    async def extra_inventory_space(self) -> int:
        return await self.read_value_from_offset(880, "int")

    async def write_extra_inventory_space(self, extra_inventory_space: int):
        await self.write_value_to_offset(880, extra_inventory_space, "int")

    async def remember_last_realm(self) -> bool:
        return await self.read_value_from_offset(884, "bool")

    async def write_remember_last_realm(self, remember_last_realm: bool):
        await self.write_value_to_offset(884, remember_last_realm, "bool")

    async def new_spellbook_layout_warning(self) -> bool:
        return await self.read_value_from_offset(885, "bool")

    async def write_new_spellbook_layout_warning(
        self, new_spellbook_layout_warning: bool
    ):
        await self.write_value_to_offset(885, new_spellbook_layout_warning, "bool")

    async def pip_conversion_base_all_schools(self) -> int:
        return await self.read_value_from_offset(728, "int")

    async def write_pip_conversion_base_all_schools(
        self, pip_conversion_base_all_schools: int
    ):
        await self.write_value_to_offset(728, pip_conversion_base_all_schools, "int")

    async def pip_conversion_base_per_school(self) -> int:
        return await self.read_value_from_offset(736, "int")

    async def write_pip_conversion_base_per_school(
        self, pip_conversion_base_per_school: int
    ):
        await self.write_value_to_offset(736, pip_conversion_base_per_school, "int")

    async def purchased_custom_emotes1(self) -> int:
        return await self.read_value_from_offset(888, "unsigned int")

    async def write_purchased_custom_emotes1(self, purchased_custom_emotes1: int):
        await self.write_value_to_offset(888, purchased_custom_emotes1, "unsigned int")

    async def purchased_custom_teleport_effects1(self) -> int:
        return await self.read_value_from_offset(892, "unsigned int")

    async def write_purchased_custom_teleport_effects1(
        self, purchased_custom_teleport_effects1: int
    ):
        await self.write_value_to_offset(
            892, purchased_custom_teleport_effects1, "unsigned int"
        )

    async def equipped_teleport_effect(self) -> int:
        return await self.read_value_from_offset(896, "unsigned int")

    async def write_equipped_teleport_effect(self, equipped_teleport_effect: int):
        await self.write_value_to_offset(896, equipped_teleport_effect, "unsigned int")

    async def highest_world1_id(self) -> int:
        return await self.read_value_from_offset(900, "unsigned int")

    async def write_highest_world1_id(self, highest_world1_i_d: int):
        await self.write_value_to_offset(900, highest_world1_i_d, "unsigned int")

    async def highest_world2_id(self) -> int:
        return await self.read_value_from_offset(904, "unsigned int")

    async def write_highest_world2_id(self, highest_world2_i_d: int):
        await self.write_value_to_offset(904, highest_world2_i_d, "unsigned int")

    async def active_class_projects_list(self) -> int:
        return await self.read_value_from_offset(912, "unsigned int")

    async def write_active_class_projects_list(self, active_class_projects_list: int):
        await self.write_value_to_offset(
            912, active_class_projects_list, "unsigned int"
        )

    async def disabled_item_slot_ids(self) -> int:
        return await self.read_value_from_offset(928, "unsigned int")

    async def write_disabled_item_slot_ids(self, disabled_item_slot_ids: int):
        await self.write_value_to_offset(928, disabled_item_slot_ids, "unsigned int")

    async def adventure_power_cooldown_time(self) -> int:
        return await self.read_value_from_offset(944, "unsigned int")

    async def write_adventure_power_cooldown_time(
        self, adventure_power_cooldown_time: int
    ):
        await self.write_value_to_offset(
            944, adventure_power_cooldown_time, "unsigned int"
        )

    async def purchased_custom_emotes2(self) -> int:
        return await self.read_value_from_offset(948, "unsigned int")

    async def write_purchased_custom_emotes2(self, purchased_custom_emotes2: int):
        await self.write_value_to_offset(948, purchased_custom_emotes2, "unsigned int")

    async def purchased_custom_teleport_effects2(self) -> int:
        return await self.read_value_from_offset(952, "unsigned int")

    async def write_purchased_custom_teleport_effects2(
        self, purchased_custom_teleport_effects2: int
    ):
        await self.write_value_to_offset(
            952, purchased_custom_teleport_effects2, "unsigned int"
        )

    async def purchased_custom_emotes3(self) -> int:
        return await self.read_value_from_offset(956, "unsigned int")

    async def write_purchased_custom_emotes3(self, purchased_custom_emotes3: int):
        await self.write_value_to_offset(956, purchased_custom_emotes3, "unsigned int")

    async def purchased_custom_teleport_effects3(self) -> int:
        return await self.read_value_from_offset(960, "unsigned int")

    async def write_purchased_custom_teleport_effects3(
        self, purchased_custom_teleport_effects3: int
    ):
        await self.write_value_to_offset(
            960, purchased_custom_teleport_effects3, "unsigned int"
        )

    async def shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(964, "float")

    async def write_shadow_pip_rating(self, shadow_pip_rating: float):
        await self.write_value_to_offset(964, shadow_pip_rating, "float")

    async def bonus_shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(968, "float")

    async def write_bonus_shadow_pip_rating(self, bonus_shadow_pip_rating: float):
        await self.write_value_to_offset(968, bonus_shadow_pip_rating, "float")

    async def shadow_pip_rate_accumulated(self) -> float:
        return await self.read_value_from_offset(972, "float")

    async def write_shadow_pip_rate_accumulated(
        self, shadow_pip_rate_accumulated: float
    ):
        await self.write_value_to_offset(972, shadow_pip_rate_accumulated, "float")

    async def shadow_pip_rate_threshold(self) -> float:
        return await self.read_value_from_offset(976, "float")

    async def write_shadow_pip_rate_threshold(self, shadow_pip_rate_threshold: float):
        await self.write_value_to_offset(976, shadow_pip_rate_threshold, "float")

    async def shadow_pip_rate_percentage(self) -> int:
        return await self.read_value_from_offset(980, "int")

    async def write_shadow_pip_rate_percentage(self, shadow_pip_rate_percentage: int):
        await self.write_value_to_offset(980, shadow_pip_rate_percentage, "int")

    async def friendly_player(self) -> bool:
        return await self.read_value_from_offset(984, "bool")

    async def write_friendly_player(self, friendly_player: bool):
        await self.write_value_to_offset(984, friendly_player, "bool")
