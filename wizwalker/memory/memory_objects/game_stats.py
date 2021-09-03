from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass


class GameStats(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def max_hitpoints(self) -> int:
        """
        Client's max hitpoints; base + bonus
        """
        base = self.base_hitpoints()
        bonus = self.bonus_hitpoints()
        return base + bonus

    def max_mana(self) -> int:
        """
        Clients's max mana; base + bonus
        """
        base = self.base_mana()
        bonus = self.bonus_mana()
        return base + bonus

    def base_hitpoints(self) -> int:
        return self.read_value_from_offset(80, "int")

    def write_base_hitpoints(self, base_hitpoints: int):
        self.write_value_to_offset(80, base_hitpoints, "int")

    def base_mana(self) -> int:
        return self.read_value_from_offset(84, "int")

    def write_base_mana(self, base_mana: int):
        self.write_value_to_offset(84, base_mana, "int")

    def base_gold_pouch(self) -> int:
        return self.read_value_from_offset(88, "int")

    def write_base_gold_pouch(self, base_gold_pouch: int):
        self.write_value_to_offset(88, base_gold_pouch, "int")

    def base_event_currency1_pouch(self) -> int:
        return self.read_value_from_offset(92, "int")

    def write_base_event_currency1_pouch(self, base_event_currency1_pouch: int):
        self.write_value_to_offset(92, base_event_currency1_pouch, "int")

    def base_event_currency2_pouch(self) -> int:
        return self.read_value_from_offset(96, "int")

    def write_base_event_currency2_pouch(self, base_event_currency2_pouch: int):
        self.write_value_to_offset(96, base_event_currency2_pouch, "int")

    def energy_max(self) -> int:
        return self.read_value_from_offset(100, "int")

    def write_energy_max(self, energy_max: int):
        self.write_value_to_offset(100, energy_max, "int")

    def current_hitpoints(self) -> int:
        return self.read_value_from_offset(104, "int")

    def write_current_hitpoints(self, current_hitpoints: int):
        self.write_value_to_offset(104, current_hitpoints, "int")

    def current_gold(self) -> int:
        return self.read_value_from_offset(108, "int")

    def write_current_gold(self, current_gold: int):
        self.write_value_to_offset(108, current_gold, "int")

    def current_event_currency1(self) -> int:
        return self.read_value_from_offset(112, "int")

    def write_current_event_currency1(self, current_event_currency1: int):
        self.write_value_to_offset(112, current_event_currency1, "int")

    def current_event_currency2(self) -> int:
        return self.read_value_from_offset(116, "int")

    def write_current_event_currency2(self, current_event_currency2: int):
        self.write_value_to_offset(116, current_event_currency2, "int")

    def current_mana(self) -> int:
        return self.read_value_from_offset(120, "int")

    def write_current_mana(self, current_mana: int):
        self.write_value_to_offset(120, current_mana, "int")

    def current_arena_points(self) -> int:
        return self.read_value_from_offset(124, "int")

    def write_current_arena_points(self, current_arena_points: int):
        self.write_value_to_offset(124, current_arena_points, "int")

    def spell_charge_base(self) -> list[int]:
        return self.read_dynamic_vector(128, "int")

    # TODO: add write_dynamic_vector
    # def write_spell_charge_base(self, spell_charge_base: int):
    #     self.write_value_to_offset(128, spell_charge_base, "int")

    def potion_max(self) -> float:
        return self.read_value_from_offset(152, "float")

    def write_potion_max(self, potion_max: float):
        self.write_value_to_offset(152, potion_max, "float")

    def potion_charge(self) -> float:
        return self.read_value_from_offset(156, "float")

    def write_potion_charge(self, potion_charge: float):
        self.write_value_to_offset(156, potion_charge, "float")

    # def arena_ladder(self) -> class SharedPointer<class Ladder>:
    #     return self.read_value_from_offset(160, "class SharedPointer<class Ladder>")

    # def derby_ladder(self) -> class SharedPointer<class Ladder>:
    #     return self.read_value_from_offset(176, "class SharedPointer<class Ladder>")

    # def bracket_lader(self) -> class SharedPointer<class Ladder>:
    #     return self.read_value_from_offset(192, "class SharedPointer<class Ladder>")

    def bonus_hitpoints(self) -> int:
        return self.read_value_from_offset(208, "int")

    def write_bonus_hitpoints(self, bonus_hitpoints: int):
        self.write_value_to_offset(208, bonus_hitpoints, "int")

    def bonus_mana(self) -> int:
        return self.read_value_from_offset(212, "int")

    def write_bonus_mana(self, bonus_mana: int):
        self.write_value_to_offset(212, bonus_mana, "int")

    def bonus_energy(self) -> int:
        return self.read_value_from_offset(228, "int")

    def write_bonus_energy(self, bonus_energy: int):
        self.write_value_to_offset(228, bonus_energy, "int")

    def critical_hit_percent_all(self) -> float:
        return self.read_value_from_offset(232, "float")

    def write_critical_hit_percent_all(self, critical_hit_percent_all: float):
        self.write_value_to_offset(232, critical_hit_percent_all, "float")

    def block_percent_all(self) -> float:
        return self.read_value_from_offset(236, "float")

    def write_block_percent_all(self, block_percent_all: float):
        self.write_value_to_offset(236, block_percent_all, "float")

    def critical_hit_rating_all(self) -> float:
        return self.read_value_from_offset(240, "float")

    def write_critical_hit_rating_all(self, critical_hit_rating_all: float):
        self.write_value_to_offset(240, critical_hit_rating_all, "float")

    def block_rating_all(self) -> float:
        return self.read_value_from_offset(244, "float")

    def write_block_rating_all(self, block_rating_all: float):
        self.write_value_to_offset(244, block_rating_all, "float")

    def reference_level(self) -> int:
        return self.read_value_from_offset(308, "int")

    def write_reference_level(self, reference_level: int):
        self.write_value_to_offset(308, reference_level, "int")

    def highest_character_level_on_account(self) -> int:
        return self.read_value_from_offset(312, "int")

    def write_highest_character_level_on_account(
        self, highest_character_level_on_account: int
    ):
        self.write_value_to_offset(312, highest_character_level_on_account, "int")

    def pet_act_chance(self) -> int:
        return self.read_value_from_offset(316, "int")

    def write_pet_act_chance(self, pet_act_chance: int):
        self.write_value_to_offset(316, pet_act_chance, "int")

    def dmg_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(320, "float")

    # def write_dmg_bonus_percent(self, dmg_bonus_percent: float):
    #     self.write_value_to_offset(320, dmg_bonus_percent, "float")

    def dmg_bonus_flat(self) -> list[float]:
        return self.read_dynamic_vector(344, "float")

    # def write_dmg_bonus_flat(self, dmg_bonus_flat: float):
    #     self.write_value_to_offset(344, dmg_bonus_flat, "float")

    def acc_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(368, "float")

    # def write_acc_bonus_percent(self, acc_bonus_percent: float):
    #     self.write_value_to_offset(368, acc_bonus_percent, "float")

    def ap_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(392, "float")

    # def write_ap_bonus_percent(self, ap_bonus_percent: float):
    #     self.write_value_to_offset(392, ap_bonus_percent, "float")

    def dmg_reduce_percent(self) -> list[float]:
        return self.read_dynamic_vector(416, "float")

    # def write_dmg_reduce_percent(self, dmg_reduce_percent: float):
    #     self.write_value_to_offset(416, dmg_reduce_percent, "float")

    def dmg_reduce_flat(self) -> list[float]:
        return self.read_dynamic_vector(440, "float")

    # def write_dmg_reduce_flat(self, dmg_reduce_flat: float):
    #     self.write_value_to_offset(440, dmg_reduce_flat, "float")

    def acc_reduce_percent(self) -> list[float]:
        return self.read_dynamic_vector(464, "float")

    # def write_acc_reduce_percent(self, acc_reduce_percent: float):
    #     self.write_value_to_offset(464, acc_reduce_percent, "float")

    def heal_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(488, "float")

    # def write_heal_bonus_percent(self, heal_bonus_percent: float):
    #     self.write_value_to_offset(488, heal_bonus_percent, "float")

    def heal_inc_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(512, "float")

    # def write_heal_inc_bonus_percent(self, heal_inc_bonus_percent: float):
    #     self.write_value_to_offset(512, heal_inc_bonus_percent, "float")

    def spell_charge_bonus(self) -> list[int]:
        return self.read_dynamic_vector(560, "int")

    # def write_spell_charge_bonus(self, spell_charge_bonus: int):
    #     self.write_value_to_offset(560, spell_charge_bonus, "int")

    def dmg_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(680, "float")

    def write_dmg_bonus_percent_all(self, dmg_bonus_percent_all: float):
        self.write_value_to_offset(680, dmg_bonus_percent_all, "float")

    def dmg_bonus_flat_all(self) -> float:
        return self.read_value_from_offset(684, "float")

    def write_dmg_bonus_flat_all(self, dmg_bonus_flat_all: float):
        self.write_value_to_offset(684, dmg_bonus_flat_all, "float")

    def acc_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(688, "float")

    def write_acc_bonus_percent_all(self, acc_bonus_percent_all: float):
        self.write_value_to_offset(688, acc_bonus_percent_all, "float")

    def ap_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(692, "float")

    def write_ap_bonus_percent_all(self, ap_bonus_percent_all: float):
        self.write_value_to_offset(692, ap_bonus_percent_all, "float")

    def dmg_reduce_percent_all(self) -> float:
        return self.read_value_from_offset(696, "float")

    def write_dmg_reduce_percent_all(self, dmg_reduce_percent_all: float):
        self.write_value_to_offset(696, dmg_reduce_percent_all, "float")

    def dmg_reduce_flat_all(self) -> float:
        return self.read_value_from_offset(700, "float")

    def write_dmg_reduce_flat_all(self, dmg_reduce_flat_all: float):
        self.write_value_to_offset(700, dmg_reduce_flat_all, "float")

    def acc_reduce_percent_all(self) -> float:
        return self.read_value_from_offset(704, "float")

    def write_acc_reduce_percent_all(self, acc_reduce_percent_all: float):
        self.write_value_to_offset(704, acc_reduce_percent_all, "float")

    def heal_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(708, "float")

    def write_heal_bonus_percent_all(self, heal_bonus_percent_all: float):
        self.write_value_to_offset(708, heal_bonus_percent_all, "float")

    def heal_inc_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(712, "float")

    def write_heal_inc_bonus_percent_all(self, heal_inc_bonus_percent_all: float):
        self.write_value_to_offset(712, heal_inc_bonus_percent_all, "float")

    def spell_charge_bonus_all(self) -> int:
        return self.read_value_from_offset(720, "int")

    def write_spell_charge_bonus_all(self, spell_charge_bonus_all: int):
        self.write_value_to_offset(720, spell_charge_bonus_all, "int")

    def power_pip_base(self) -> float:
        return self.read_value_from_offset(724, "float")

    def write_power_pip_base(self, power_pip_base: float):
        self.write_value_to_offset(724, power_pip_base, "float")

    def power_pip_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(760, "float")

    def write_power_pip_bonus_percent_all(
        self, power_pip_bonus_percent_all: float
    ):
        self.write_value_to_offset(760, power_pip_bonus_percent_all, "float")

    def xp_percent_increase(self) -> float:
        return self.read_value_from_offset(768, "float")

    def write_xp_percent_increase(self, xp_percent_increase: float):
        self.write_value_to_offset(768, xp_percent_increase, "float")

    def critical_hit_percent_by_school(self) -> list[float]:
        return self.read_dynamic_vector(584, "float")

    # def write_critical_hit_percent_by_school(
    #     self, critical_hit_percent_by_school: float
    # ):
    #     self.write_value_to_offset(584, critical_hit_percent_by_school, "float")

    def block_percent_by_school(self) -> list[float]:
        return self.read_dynamic_vector(608, "float")

    # def write_block_percent_by_school(self, block_percent_by_school: float):
    #     self.write_value_to_offset(608, block_percent_by_school, "float")

    def critical_hit_rating_by_school(self) -> list[float]:
        return self.read_dynamic_vector(632, "float")

    # def write_critical_hit_rating_by_school(
    #     self, critical_hit_rating_by_school: float
    # ):
    #     self.write_value_to_offset(632, critical_hit_rating_by_school, "float")

    def block_rating_by_school(self) -> list[float]:
        return self.read_dynamic_vector(656, "float")

    # def write_block_rating_by_school(self, block_rating_by_school: float):
    #     self.write_value_to_offset(656, block_rating_by_school, "float")

    def balance_mastery(self) -> int:
        return self.read_value_from_offset(792, "int")

    def write_balance_mastery(self, balance_mastery: int):
        self.write_value_to_offset(792, balance_mastery, "int")

    def death_mastery(self) -> int:
        return self.read_value_from_offset(796, "int")

    def write_death_mastery(self, death_mastery: int):
        self.write_value_to_offset(796, death_mastery, "int")

    def fire_mastery(self) -> int:
        return self.read_value_from_offset(800, "int")

    def write_fire_mastery(self, fire_mastery: int):
        self.write_value_to_offset(800, fire_mastery, "int")

    def ice_mastery(self) -> int:
        return self.read_value_from_offset(804, "int")

    def write_ice_mastery(self, ice_mastery: int):
        self.write_value_to_offset(804, ice_mastery, "int")

    def life_mastery(self) -> int:
        return self.read_value_from_offset(808, "int")

    def write_life_mastery(self, life_mastery: int):
        self.write_value_to_offset(808, life_mastery, "int")

    def myth_mastery(self) -> int:
        return self.read_value_from_offset(812, "int")

    def write_myth_mastery(self, myth_mastery: int):
        self.write_value_to_offset(812, myth_mastery, "int")

    def storm_mastery(self) -> int:
        return self.read_value_from_offset(816, "int")

    def write_storm_mastery(self, storm_mastery: int):
        self.write_value_to_offset(816, storm_mastery, "int")

    def maximum_number_of_islands(self) -> int:
        return self.read_value_from_offset(820, "int")

    def write_maximum_number_of_islands(self, maximum_number_of_islands: int):
        self.write_value_to_offset(820, maximum_number_of_islands, "int")

    def gardening_level(self) -> int:
        return self.read_value_from_offset(824, "unsigned char")

    def write_gardening_level(self, gardening_level: int):
        self.write_value_to_offset(824, gardening_level, "unsigned char")

    def gardening_xp(self) -> int:
        return self.read_value_from_offset(828, "int")

    def write_gardening_xp(self, gardening_xp: int):
        self.write_value_to_offset(828, gardening_xp, "int")

    def invisible_to_friends(self) -> bool:
        return self.read_value_from_offset(832, "bool")

    def write_invisible_to_friends(self, invisible_to_friends: bool):
        self.write_value_to_offset(832, invisible_to_friends, "bool")

    def show_item_lock(self) -> bool:
        return self.read_value_from_offset(833, "bool")

    def write_show_item_lock(self, show_item_lock: bool):
        self.write_value_to_offset(833, show_item_lock, "bool")

    def quest_finder_enabled(self) -> bool:
        return self.read_value_from_offset(834, "bool")

    def write_quest_finder_enabled(self, quest_finder_enabled: bool):
        self.write_value_to_offset(834, quest_finder_enabled, "bool")

    def buddy_list_limit(self) -> int:
        return self.read_value_from_offset(836, "int")

    def write_buddy_list_limit(self, buddy_list_limit: int):
        self.write_value_to_offset(836, buddy_list_limit, "int")

    def dont_allow_friend_finder_codes(self) -> bool:
        return self.read_value_from_offset(844, "bool")

    def write_dont_allow_friend_finder_codes(
        self, dont_allow_friend_finder_codes: bool
    ):
        self.write_value_to_offset(844, dont_allow_friend_finder_codes, "bool")

    def stun_resistance_percent(self) -> float:
        return self.read_value_from_offset(840, "float")

    def write_stun_resistance_percent(self, stun_resistance_percent: float):
        self.write_value_to_offset(840, stun_resistance_percent, "float")

    def shadow_magic_unlocked(self) -> bool:
        return self.read_value_from_offset(852, "bool")

    def write_shadow_magic_unlocked(self, shadow_magic_unlocked: bool):
        self.write_value_to_offset(852, shadow_magic_unlocked, "bool")

    def shadow_pip_max(self) -> int:
        return self.read_value_from_offset(848, "int")

    def write_shadow_pip_max(self, shadow_pip_max: int):
        self.write_value_to_offset(848, shadow_pip_max, "int")

    def fishing_level(self) -> int:
        return self.read_value_from_offset(853, "unsigned char")

    def write_fishing_level(self, fishing_level: int):
        self.write_value_to_offset(853, fishing_level, "unsigned char")

    def fishing_xp(self) -> int:
        return self.read_value_from_offset(856, "int")

    def write_fishing_xp(self, fishing_xp: int):
        self.write_value_to_offset(856, fishing_xp, "int")

    def fishing_luck_bonus_percent(self) -> list[float]:
        return self.read_dynamic_vector(536, "float")

    # def write_fishing_luck_bonus_percent(self, fishing_luck_bonus_percent: float):
    #     self.write_value_to_offset(536, fishing_luck_bonus_percent, "float")

    def fishing_luck_bonus_percent_all(self) -> float:
        return self.read_value_from_offset(716, "float")

    def write_fishing_luck_bonus_percent_all(
        self, fishing_luck_bonus_percent_all: float
    ):
        self.write_value_to_offset(716, fishing_luck_bonus_percent_all, "float")

    def subscriber_benefit_flags(self) -> int:
        return self.read_value_from_offset(860, "unsigned int")

    def write_subscriber_benefit_flags(self, subscriber_benefit_flags: int):
        self.write_value_to_offset(860, subscriber_benefit_flags, "unsigned int")

    def elixir_benefit_flags(self) -> int:
        return self.read_value_from_offset(864, "unsigned int")

    def write_elixir_benefit_flags(self, elixir_benefit_flags: int):
        self.write_value_to_offset(864, elixir_benefit_flags, "unsigned int")

    def shadow_pip_bonus_percent(self) -> float:
        return self.read_value_from_offset(764, "float")

    def write_shadow_pip_bonus_percent(self, shadow_pip_bonus_percent: float):
        self.write_value_to_offset(764, shadow_pip_bonus_percent, "float")

    def wisp_bonus_percent(self) -> float:
        return self.read_value_from_offset(784, "float")

    def write_wisp_bonus_percent(self, wisp_bonus_percent: float):
        self.write_value_to_offset(784, wisp_bonus_percent, "float")

    def pip_conversion_rating_all(self) -> float:
        return self.read_value_from_offset(272, "float")

    def write_pip_conversion_rating_all(self, pip_conversion_rating_all: float):
        self.write_value_to_offset(272, pip_conversion_rating_all, "float")

    def pip_conversion_rating_per_school(self) -> list[float]:
        return self.read_dynamic_vector(248, "float")

    # def write_pip_conversion_rating_per_school(
    #     self, pip_conversion_rating_per_school: float
    # ):
    #     self.write_value_to_offset(248, pip_conversion_rating_per_school, "float")

    def pip_conversion_percent_all(self) -> float:
        return self.read_value_from_offset(304, "float")

    def write_pip_conversion_percent_all(self, pip_conversion_percent_all: float):
        self.write_value_to_offset(304, pip_conversion_percent_all, "float")

    def pip_conversion_percent_per_school(self) -> list[float]:
        return self.read_dynamic_vector(280, "float")

    # def write_pip_conversion_percent_per_school(
    #     self, pip_conversion_percent_per_school: float
    # ):
    #     self.write_value_to_offset(
    #         280, pip_conversion_percent_per_school, "float"
    #     )

    def monster_magic_level(self) -> int:
        return self.read_value_from_offset(868, "unsigned char")

    def write_monster_magic_level(self, monster_magic_level: int):
        self.write_value_to_offset(868, monster_magic_level, "unsigned char")

    def monster_magic_xp(self) -> int:
        return self.read_value_from_offset(872, "int")

    def write_monster_magic_xp(self, monster_magic_xp: int):
        self.write_value_to_offset(872, monster_magic_xp, "int")

    def player_chat_channel_is_public(self) -> bool:
        return self.read_value_from_offset(876, "bool")

    def write_player_chat_channel_is_public(
        self, player_chat_channel_is_public: bool
    ):
        self.write_value_to_offset(876, player_chat_channel_is_public, "bool")

    def extra_inventory_space(self) -> int:
        return self.read_value_from_offset(880, "int")

    def write_extra_inventory_space(self, extra_inventory_space: int):
        self.write_value_to_offset(880, extra_inventory_space, "int")

    def remember_last_realm(self) -> bool:
        return self.read_value_from_offset(884, "bool")

    def write_remember_last_realm(self, remember_last_realm: bool):
        self.write_value_to_offset(884, remember_last_realm, "bool")

    def new_spellbook_layout_warning(self) -> bool:
        return self.read_value_from_offset(885, "bool")

    def write_new_spellbook_layout_warning(
        self, new_spellbook_layout_warning: bool
    ):
        self.write_value_to_offset(885, new_spellbook_layout_warning, "bool")

    def pip_conversion_base_all_schools(self) -> int:
        return self.read_value_from_offset(728, "int")

    def write_pip_conversion_base_all_schools(
        self, pip_conversion_base_all_schools: int
    ):
        self.write_value_to_offset(728, pip_conversion_base_all_schools, "int")

    def pip_conversion_base_per_school(self) -> list[int]:
        return self.read_dynamic_vector(736, "int")

    # def write_pip_conversion_base_per_school(
    #     self, pip_conversion_base_per_school: int
    # ):
    #     self.write_value_to_offset(736, pip_conversion_base_per_school, "int")

    def purchased_custom_emotes1(self) -> int:
        return self.read_value_from_offset(888, "unsigned int")

    def write_purchased_custom_emotes1(self, purchased_custom_emotes1: int):
        self.write_value_to_offset(888, purchased_custom_emotes1, "unsigned int")

    def purchased_custom_teleport_effects1(self) -> int:
        return self.read_value_from_offset(892, "unsigned int")

    def write_purchased_custom_teleport_effects1(
        self, purchased_custom_teleport_effects1: int
    ):
        self.write_value_to_offset(
            892, purchased_custom_teleport_effects1, "unsigned int"
        )

    def equipped_teleport_effect(self) -> int:
        return self.read_value_from_offset(896, "unsigned int")

    def write_equipped_teleport_effect(self, equipped_teleport_effect: int):
        self.write_value_to_offset(896, equipped_teleport_effect, "unsigned int")

    def highest_world1_id(self) -> int:
        return self.read_value_from_offset(900, "unsigned int")

    def write_highest_world1_id(self, highest_world1_id: int):
        self.write_value_to_offset(900, highest_world1_id, "unsigned int")

    def highest_world2_id(self) -> int:
        return self.read_value_from_offset(904, "unsigned int")

    def write_highest_world2_id(self, highest_world2_i_d: int):
        self.write_value_to_offset(904, highest_world2_i_d, "unsigned int")

    def active_class_projects_list(self) -> int:
        return self.read_value_from_offset(912, "unsigned int")

    def write_active_class_projects_list(self, active_class_projects_list: int):
        self.write_value_to_offset(
            912, active_class_projects_list, "unsigned int"
        )

    def disabled_item_slot_ids(self) -> int:
        return self.read_value_from_offset(928, "unsigned int")

    def write_disabled_item_slot_ids(self, disabled_item_slot_ids: int):
        self.write_value_to_offset(928, disabled_item_slot_ids, "unsigned int")

    def adventure_power_cooldown_time(self) -> int:
        return self.read_value_from_offset(944, "unsigned int")

    def write_adventure_power_cooldown_time(
        self, adventure_power_cooldown_time: int
    ):
        self.write_value_to_offset(
            944, adventure_power_cooldown_time, "unsigned int"
        )

    def purchased_custom_emotes2(self) -> int:
        return self.read_value_from_offset(948, "unsigned int")

    def write_purchased_custom_emotes2(self, purchased_custom_emotes2: int):
        self.write_value_to_offset(948, purchased_custom_emotes2, "unsigned int")

    def purchased_custom_teleport_effects2(self) -> int:
        return self.read_value_from_offset(952, "unsigned int")

    def write_purchased_custom_teleport_effects2(
        self, purchased_custom_teleport_effects2: int
    ):
        self.write_value_to_offset(
            952, purchased_custom_teleport_effects2, "unsigned int"
        )

    def purchased_custom_emotes3(self) -> int:
        return self.read_value_from_offset(956, "unsigned int")

    def write_purchased_custom_emotes3(self, purchased_custom_emotes3: int):
        self.write_value_to_offset(956, purchased_custom_emotes3, "unsigned int")

    def purchased_custom_teleport_effects3(self) -> int:
        return self.read_value_from_offset(960, "unsigned int")

    def write_purchased_custom_teleport_effects3(
        self, purchased_custom_teleport_effects3: int
    ):
        self.write_value_to_offset(
            960, purchased_custom_teleport_effects3, "unsigned int"
        )

    def shadow_pip_rating(self) -> float:
        return self.read_value_from_offset(964, "float")

    def write_shadow_pip_rating(self, shadow_pip_rating: float):
        self.write_value_to_offset(964, shadow_pip_rating, "float")

    def bonus_shadow_pip_rating(self) -> float:
        return self.read_value_from_offset(968, "float")

    def write_bonus_shadow_pip_rating(self, bonus_shadow_pip_rating: float):
        self.write_value_to_offset(968, bonus_shadow_pip_rating, "float")

    def shadow_pip_rate_accumulated(self) -> float:
        return self.read_value_from_offset(972, "float")

    def write_shadow_pip_rate_accumulated(
        self, shadow_pip_rate_accumulated: float
    ):
        self.write_value_to_offset(972, shadow_pip_rate_accumulated, "float")

    def shadow_pip_rate_threshold(self) -> float:
        return self.read_value_from_offset(976, "float")

    def write_shadow_pip_rate_threshold(self, shadow_pip_rate_threshold: float):
        self.write_value_to_offset(976, shadow_pip_rate_threshold, "float")

    def shadow_pip_rate_percentage(self) -> int:
        return self.read_value_from_offset(980, "int")

    def write_shadow_pip_rate_percentage(self, shadow_pip_rate_percentage: int):
        self.write_value_to_offset(980, shadow_pip_rate_percentage, "int")

    def friendly_player(self) -> bool:
        return self.read_value_from_offset(984, "bool")

    def write_friendly_player(self, friendly_player: bool):
        self.write_value_to_offset(984, friendly_player, "bool")

    def emoji_skin_tone(self) -> int:
        return self.read_value_from_offset(988, "int")

    def write_emoji_skin_tone(self, emoji_skin_tone: int):
        self.write_value_to_offset(988, emoji_skin_tone, "int")


class CurrentGameStats(GameStats):
    def read_base_address(self) -> int:
        return self.hook_handler.read_current_player_stat_base()


class DynamicGameStats(DynamicMemoryObject, GameStats):
    pass
