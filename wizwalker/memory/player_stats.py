from .memory_object import MemoryObject


class PlayerStats(MemoryObject):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_player_stat_base()

    async def base_hitpoints(self) -> int:
        return await self.read_value_from_offset(80, "int")

    async def base_mana(self) -> int:
        return await self.read_value_from_offset(84, "int")

    async def base_gold_pouch(self) -> int:
        return await self.read_value_from_offset(88, "int")

    async def base_event_currency1_pouch(self) -> int:
        return await self.read_value_from_offset(92, "int")

    async def base_event_currency2_pouch(self) -> int:
        return await self.read_value_from_offset(96, "int")

    async def energy_max(self) -> int:
        return await self.read_value_from_offset(100, "int")

    async def current_hitpoints(self) -> int:
        return await self.read_value_from_offset(104, "int")

    async def current_gold(self) -> int:
        return await self.read_value_from_offset(108, "int")

    async def current_event_currency1(self) -> int:
        return await self.read_value_from_offset(112, "int")

    async def current_event_currency2(self) -> int:
        return await self.read_value_from_offset(116, "int")

    async def current_mana(self) -> int:
        return await self.read_value_from_offset(120, "int")

    async def current_arena_points(self) -> int:
        return await self.read_value_from_offset(124, "int")

    async def spell_charge_base(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def potion_max(self) -> float:
        return await self.read_value_from_offset(152, "float")

    async def potion_charge(self) -> float:
        return await self.read_value_from_offset(156, "float")

    # TODO: arena_ladder, derby_ladder, bracket_lader

    async def bonus_hitpoints(self) -> int:
        return await self.read_value_from_offset(208, "int")

    async def bonus_mana(self) -> int:
        return await self.read_value_from_offset(212, "int")

    async def bonus_energy(self) -> int:
        return await self.read_value_from_offset(228, "int")

    async def critical_hit_percent_all(self) -> float:
        return await self.read_value_from_offset(232, "float")

    async def block_percent_all(self) -> float:
        return await self.read_value_from_offset(236, "float")

    async def critical_hit_rating_all(self) -> float:
        return await self.read_value_from_offset(240, "float")

    async def block_rating_all(self) -> float:
        return await self.read_value_from_offset(244, "float")

    async def reference_level(self) -> int:
        return await self.read_value_from_offset(308, "int")

    async def highest_character_level_on_account(self) -> int:
        return await self.read_value_from_offset(312, "int")

    async def pet_act_chance(self) -> int:
        return await self.read_value_from_offset(316, "int")

    async def dmg_bonus_percent(self) -> float:
        return await self.read_value_from_offset(320, "float")

    async def dmg_bonus_flat(self) -> float:
        return await self.read_value_from_offset(344, "float")

    async def acc_bonus_percent(self) -> float:
        return await self.read_value_from_offset(368, "float")

    async def ap_bonus_percent(self) -> float:
        return await self.read_value_from_offset(392, "float")

    async def dmg_reduce_percent(self) -> float:
        return await self.read_value_from_offset(416, "float")

    async def dmg_reduce_flat(self) -> float:
        return await self.read_value_from_offset(440, "float")

    async def acc_reduce_percent(self) -> float:
        return await self.read_value_from_offset(464, "float")

    async def heal_bonus_percent(self) -> float:
        return await self.read_value_from_offset(488, "float")

    async def heal_inc_bonus_percent(self) -> float:
        return await self.read_value_from_offset(512, "float")

    async def spell_charge_bonus(self) -> int:
        return await self.read_value_from_offset(560, "int")

    async def dmg_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(680, "float")

    async def dmg_bonus_flat_all(self) -> float:
        return await self.read_value_from_offset(684, "float")

    async def acc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(688, "float")

    async def ap_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(692, "float")

    async def dmg_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(696, "float")

    async def dmg_reduce_flat_all(self) -> float:
        return await self.read_value_from_offset(700, "float")

    async def acc_reduce_percent_all(self) -> float:
        return await self.read_value_from_offset(704, "float")

    async def heal_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(708, "float")

    async def heal_inc_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(712, "float")

    async def spell_charge_bonus_all(self) -> int:
        return await self.read_value_from_offset(720, "int")

    async def power_pip_base(self) -> float:
        return await self.read_value_from_offset(724, "float")

    async def power_pip_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(760, "float")

    async def xp_percent_increase(self) -> float:
        return await self.read_value_from_offset(768, "float")

    async def critical_hit_percent_by_school(self) -> float:
        return await self.read_value_from_offset(584, "float")

    async def block_percent_by_school(self) -> float:
        return await self.read_value_from_offset(608, "float")

    async def critical_hit_rating_by_school(self) -> float:
        return await self.read_value_from_offset(632, "float")

    async def block_rating_by_school(self) -> float:
        return await self.read_value_from_offset(656, "float")

    async def balance_mastery(self) -> int:
        return await self.read_value_from_offset(792, "int")

    async def death_mastery(self) -> int:
        return await self.read_value_from_offset(796, "int")

    async def fire_mastery(self) -> int:
        return await self.read_value_from_offset(800, "int")

    async def ice_mastery(self) -> int:
        return await self.read_value_from_offset(804, "int")

    async def life_mastery(self) -> int:
        return await self.read_value_from_offset(808, "int")

    async def myth_mastery(self) -> int:
        return await self.read_value_from_offset(812, "int")

    async def storm_mastery(self) -> int:
        return await self.read_value_from_offset(816, "int")

    async def maximum_number_of_islands(self) -> int:
        return await self.read_value_from_offset(820, "int")

    async def gardening_level(self) -> int:
        return await self.read_value_from_offset(824, "unsigned char")

    async def gardening_x_p(self) -> int:
        return await self.read_value_from_offset(828, "int")

    async def invisible_to_friends(self) -> bool:
        return await self.read_value_from_offset(832, "bool")

    async def show_item_lock(self) -> bool:
        return await self.read_value_from_offset(833, "bool")

    async def quest_finder_enabled(self) -> bool:
        return await self.read_value_from_offset(834, "bool")

    async def buddy_list_limit(self) -> int:
        return await self.read_value_from_offset(836, "int")

    async def dont_allow_friend_finder_codes(self) -> bool:
        return await self.read_value_from_offset(844, "bool")

    async def stun_resistance_percent(self) -> float:
        return await self.read_value_from_offset(840, "float")

    async def shadow_magic_unlocked(self) -> bool:
        return await self.read_value_from_offset(852, "bool")

    async def shadow_pip_max(self) -> int:
        return await self.read_value_from_offset(848, "int")

    async def fishing_level(self) -> int:
        return await self.read_value_from_offset(853, "unsigned char")

    async def fishing_x_p(self) -> int:
        return await self.read_value_from_offset(856, "int")

    async def fishing_luck_bonus_percent(self) -> float:
        return await self.read_value_from_offset(536, "float")

    async def fishing_luck_bonus_percent_all(self) -> float:
        return await self.read_value_from_offset(716, "float")

    async def subscriber_benefit_flags(self) -> int:
        return await self.read_value_from_offset(860, "unsigned int")

    async def elixir_benefit_flags(self) -> int:
        return await self.read_value_from_offset(864, "unsigned int")

    async def shadow_pip_bonus_percent(self) -> float:
        return await self.read_value_from_offset(764, "float")

    async def wisp_bonus_percent(self) -> float:
        return await self.read_value_from_offset(784, "float")

    async def pip_conversion_rating_all(self) -> float:
        return await self.read_value_from_offset(272, "float")

    async def pip_conversion_rating_per_school(self) -> float:
        return await self.read_value_from_offset(248, "float")

    async def pip_conversion_percent_all(self) -> float:
        return await self.read_value_from_offset(304, "float")

    async def pip_conversion_percent_per_school(self) -> float:
        return await self.read_value_from_offset(280, "float")

    async def monster_magic_level(self) -> int:
        return await self.read_value_from_offset(868, "unsigned char")

    async def monster_magic_x_p(self) -> int:
        return await self.read_value_from_offset(872, "int")

    async def player_chat_channel_is_public(self) -> bool:
        return await self.read_value_from_offset(876, "bool")

    async def extra_inventory_space(self) -> int:
        return await self.read_value_from_offset(880, "int")

    async def remember_last_realm(self) -> bool:
        return await self.read_value_from_offset(884, "bool")

    async def new_spellbook_layout_warning(self) -> bool:
        return await self.read_value_from_offset(885, "bool")

    async def pip_conversion_base_all_schools(self) -> int:
        return await self.read_value_from_offset(728, "int")

    async def pip_conversion_base_per_school(self) -> int:
        return await self.read_value_from_offset(736, "int")

    async def purchased_custom_emotes1(self) -> int:
        return await self.read_value_from_offset(888, "unsigned int")

    async def purchased_custom_teleport_effects1(self) -> int:
        return await self.read_value_from_offset(892, "unsigned int")

    async def equipped_teleport_effect(self) -> int:
        return await self.read_value_from_offset(896, "unsigned int")

    async def highest_world1_id(self) -> int:
        return await self.read_value_from_offset(900, "unsigned int")

    async def highest_world2_id(self) -> int:
        return await self.read_value_from_offset(904, "unsigned int")

    async def active_class_projects_list(self) -> int:
        return await self.read_value_from_offset(912, "unsigned int")

    async def disabled_item_slot_i_ds(self) -> int:
        return await self.read_value_from_offset(928, "unsigned int")

    async def adventure_power_cooldown_time(self) -> int:
        return await self.read_value_from_offset(944, "unsigned int")

    async def purchased_custom_emotes2(self) -> int:
        return await self.read_value_from_offset(948, "unsigned int")

    async def purchased_custom_teleport_effects2(self) -> int:
        return await self.read_value_from_offset(952, "unsigned int")

    async def purchased_custom_emotes3(self) -> int:
        return await self.read_value_from_offset(956, "unsigned int")

    async def purchased_custom_teleport_effects3(self) -> int:
        return await self.read_value_from_offset(960, "unsigned int")

    async def shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(964, "float")

    async def bonus_shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(968, "float")

    async def shadow_pip_rate_accumulated(self) -> float:
        return await self.read_value_from_offset(972, "float")

    async def shadow_pip_rate_threshold(self) -> float:
        return await self.read_value_from_offset(976, "float")

    async def shadow_pip_rate_percentage(self) -> int:
        return await self.read_value_from_offset(980, "int")

    async def friendly_player(self) -> bool:
        return await self.read_value_from_offset(984, "bool")
