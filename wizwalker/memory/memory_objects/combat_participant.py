from typing import List, Optional

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import PipAquiredByEnum
from .game_stats import DynamicGameStats
from .spell import DynamicHand
from .play_deck import DynamicPlayDeck
from .spell_effect import DynamicSpellEffect


class CombatParticipant(PropertyClass):
    """
    Base class for CombatParticipants
    """

    def read_base_address(self) -> int:
        raise NotImplementedError()

    async def owner_id_full(self) -> int:
        """
        This combat participant's owner id
        """
        return await self.read_value_from_offset(112, "unsigned long long")

    async def write_owner_id_full(self, owner_id_full: int):
        """
        Write this combat participant's owner id

        Args:
            owner_id_full: The owner id to write
        """
        await self.write_value_to_offset(112, owner_id_full, "unsigned long long")

    async def template_id_full(self) -> int:
        """
        This combat participant's template id
        """
        return await self.read_value_from_offset(120, "unsigned long long")

    async def write_template_id_full(self, template_id_full: int):
        """
        Write this combat participant's template id

        Args:
            template_id_full: The template id to write
        """
        await self.write_value_to_offset(120, template_id_full, "unsigned long long")

    async def is_player(self) -> bool:
        """
        If this combat participant is a player
        """
        return await self.read_value_from_offset(128, "bool")

    async def write_is_player(self, is_player: bool):
        """
        Write if this combat participant is a player

        Args:
            is_player: The bool to write
        """
        await self.write_value_to_offset(128, is_player, "bool")

    async def zone_id_full(self) -> int:
        """
        This combat participant's zone id
        """
        return await self.read_value_from_offset(136, "unsigned long long")

    async def write_zone_id_full(self, zone_id_full: int):
        """
        Write this combat participant's zone id

        Args:
            zone_id_full: The zone id to write
        """
        await self.write_value_to_offset(136, zone_id_full, "unsigned long long")

    # TODO: look into what a team id is; i.e is it always the two ids
    async def team_id(self) -> int:
        """
        This combat participant's team id
        """
        return await self.read_value_from_offset(144, "int")

    async def write_team_id(self, team_id: int):
        """
        Write this combat participant's team id

        Args:
            team_id: The team id to write
        """
        await self.write_value_to_offset(144, team_id, "int")

    # TODO: turn this into an enum?
    async def primary_magic_school_id(self) -> int:
        """
        This combat participant's primary school id

        Notes:
            This is a template id
        """
        return await self.read_value_from_offset(148, "int")

    async def write_primary_magic_school_id(self, primary_magic_school_id: int):
        """
        Write this combat participant's primate school id

        Args:
            primary_magic_school_id: The school id to write

        Notes:
            this is a template id
        """
        await self.write_value_to_offset(148, primary_magic_school_id, "int")

    async def num_pips(self) -> int:
        """
        The number of pips this combat participant has
        """
        return await self.read_value_from_offset(152, "unsigned char")

    async def write_num_pips(self, num_pips: int):
        """
        Write this participant's pip number

        Args:
            num_pips: The pip number to write
        """
        await self.write_value_to_offset(152, num_pips, "unsigned char")

    async def num_power_pips(self) -> int:
        """
        The number of power pips this combat participant has
        """
        return await self.read_value_from_offset(153, "unsigned char")

    async def write_num_power_pips(self, num_power_pips: int):
        """
        Write the number of power pips this combat participant has

        Args:
            num_power_pips: The power pip number to write
        """
        await self.write_value_to_offset(153, num_power_pips, "unsigned char")

    async def num_shadow_pips(self) -> int:
        """
        The number of shadow pips this combat participant has
        """
        return await self.read_value_from_offset(154, "unsigned char")

    async def write_num_shadow_pips(self, num_shadow_pips: int):
        """
        Write the number of shadow pips this combat participant has

        Args:
            num_shadow_pips: The power pip number to write
        """
        await self.write_value_to_offset(154, num_shadow_pips, "unsigned char")

    # async def pip_round_rates(self) -> class SharedPointer<class ModifyPipRoundRateData>:
    #     return await self.read_value_from_offset(160, "class SharedPointer<class ModifyPipRoundRateData>")

    async def pips_suspended(self) -> bool:
        """
        If this participant's pips are suspended
        """
        return await self.read_value_from_offset(176, "bool")

    async def write_pips_suspended(self, pips_suspended: bool):
        """
        Write if this participant's pips are suspended

        Args:
            pips_suspended: bool if pips are suspended
        """
        await self.write_value_to_offset(176, pips_suspended, "bool")

    # TODO: finish docs
    async def stunned(self) -> int:
        return await self.read_value_from_offset(180, "int")

    async def write_stunned(self, stunned: int):
        await self.write_value_to_offset(180, stunned, "int")

    async def mindcontrolled(self) -> int:
        return await self.read_value_from_offset(208, "int")

    async def write_mindcontrolled(self, mindcontrolled: int):
        await self.write_value_to_offset(208, mindcontrolled, "int")

    async def original_team(self) -> int:
        return await self.read_value_from_offset(216, "int")

    async def write_original_team(self, original_team: int):
        await self.write_value_to_offset(216, original_team, "int")

    async def aura_turn_length(self) -> int:
        return await self.read_value_from_offset(228, "int")

    async def write_aura_turn_length(self, n_aura_turn_length: int):
        await self.write_value_to_offset(228, n_aura_turn_length, "int")

    async def clue(self) -> int:
        return await self.read_value_from_offset(220, "int")

    async def write_clue(self, clue: int):
        await self.write_value_to_offset(220, clue, "int")

    async def rounds_dead(self) -> int:
        return await self.read_value_from_offset(224, "int")

    async def write_rounds_dead(self, rounds_dead: int):
        await self.write_value_to_offset(224, rounds_dead, "int")

    async def polymorph_turn_length(self) -> int:
        return await self.read_value_from_offset(232, "int")

    async def write_polymorph_turn_length(self, n_polymorph_turn_length: int):
        await self.write_value_to_offset(232, n_polymorph_turn_length, "int")

    async def player_health(self) -> int:
        return await self.read_value_from_offset(236, "int")

    async def write_player_health(self, player_health: int):
        await self.write_value_to_offset(236, player_health, "int")

    async def max_player_health(self) -> int:
        return await self.read_value_from_offset(240, "int")

    async def write_max_player_health(self, max_player_health: int):
        await self.write_value_to_offset(240, max_player_health, "int")

    async def hide_current_hp(self) -> bool:
        return await self.read_value_from_offset(244, "bool")

    async def write_hide_current_hp(self, _hide_current_h_p: bool):
        await self.write_value_to_offset(244, _hide_current_h_p, "bool")

    async def max_hand_size(self) -> int:
        return await self.read_value_from_offset(248, "int")

    async def write_max_hand_size(self, max_hand_size: int):
        await self.write_value_to_offset(248, max_hand_size, "int")

    async def hand(self) -> Optional[DynamicHand]:
        addr = await self.read_value_from_offset(256, "long long")

        if addr == 0:
            return None

        return DynamicHand(self.hook_handler, addr)

    async def saved_hand(self) -> Optional[DynamicHand]:
        addr = await self.read_value_from_offset(264, "long long")

        if addr == 0:
            return None

        return DynamicHand(self.hook_handler, addr)

    async def play_deck(self) -> Optional[DynamicPlayDeck]:
        addr = await self.read_value_from_offset(272, "long long")

        if addr == 0:
            return None

        return DynamicPlayDeck(self.hook_handler, addr)

    async def saved_play_deck(self) -> Optional[DynamicPlayDeck]:
        addr = await self.read_value_from_offset(280, "long long")

        if addr == 0:
            return None

        return DynamicPlayDeck(self.hook_handler, addr)

    async def saved_game_stats(self) -> Optional[DynamicGameStats]:
        addr = await self.read_value_from_offset(288, "long long")

        if addr == 0:
            return None

        return DynamicGameStats(self.hook_handler, addr)

    async def saved_primary_magic_school_id(self) -> int:
        return await self.read_value_from_offset(304, "int")

    async def write_saved_primary_magic_school_id(
        self, saved_primary_magic_school_id: int
    ):
        await self.write_value_to_offset(304, saved_primary_magic_school_id, "int")

    async def game_stats(self) -> Optional[DynamicGameStats]:
        addr = await self.read_value_from_offset(312, "long long")

        if addr == 0:
            return None

        return DynamicGameStats(self.hook_handler, addr)

    # TODO: figure out what color is
    # async def color(self) -> class Color:
    #     return await self.read_value_from_offset(328, "class Color")
    #
    # async def write_color(self, color: class Color):
    #     await self.write_value_to_offset(328, color, "class Color")

    async def rotation(self) -> float:
        return await self.read_value_from_offset(332, "float")

    async def write_rotation(self, rotation: float):
        await self.write_value_to_offset(332, rotation, "float")

    async def radius(self) -> float:
        return await self.read_value_from_offset(336, "float")

    async def write_radius(self, radius: float):
        await self.write_value_to_offset(336, radius, "float")

    async def subcircle(self) -> int:
        return await self.read_value_from_offset(340, "int")

    async def write_subcircle(self, subcircle: int):
        await self.write_value_to_offset(340, subcircle, "int")

    async def pvp(self) -> bool:
        return await self.read_value_from_offset(344, "bool")

    async def write_pvp(self, pvp: bool):
        await self.write_value_to_offset(344, pvp, "bool")

    async def accuracy_bonus(self) -> float:
        return await self.read_value_from_offset(388, "float")

    async def write_accuracy_bonus(self, accuracy_bonus: float):
        await self.write_value_to_offset(388, accuracy_bonus, "float")

    async def minion_sub_circle(self) -> int:
        return await self.read_value_from_offset(392, "int")

    async def write_minion_sub_circle(self, minion_sub_circle: int):
        await self.write_value_to_offset(392, minion_sub_circle, "int")

    async def is_minion(self) -> bool:
        return await self.read_value_from_offset(396, "bool")

    async def write_is_minion(self, is_minion: bool):
        await self.write_value_to_offset(396, is_minion, "bool")

    async def hanging_effects(self) -> List[DynamicSpellEffect]:
        hanging_effects = []
        for addr in await self.read_linked_list(408):
            hanging_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return hanging_effects

    async def public_hanging_effects(self) -> List[DynamicSpellEffect]:
        hanging_effects = []
        for addr in await self.read_linked_list(424):
            hanging_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return hanging_effects

    async def aura_effects(self) -> List[DynamicSpellEffect]:
        aura_effects = []
        for addr in await self.read_linked_list(440):
            aura_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return aura_effects

    # TODO: add this class
    # async def shadow_effects(self) -> class SharedPointer<class ShadowSpellTrackingData>:
    #     return await self.read_value_from_offset(456, "class SharedPointer<class ShadowSpellTrackingData>")

    async def shadow_spell_effects(self) -> List[DynamicSpellEffect]:
        shadow_spell_effects = []
        for addr in await self.read_linked_list(472):
            shadow_spell_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return shadow_spell_effects

    async def death_activated_effects(self) -> List[DynamicSpellEffect]:
        death_activated_effects = []
        for addr in await self.read_shared_linked_list(504):
            death_activated_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return death_activated_effects

    # note: these are actually DelaySpellEffects
    async def delay_cast_effects(self) -> List[DynamicSpellEffect]:
        delay_cast_effects = []
        for addr in await self.read_linked_list(520):
            delay_cast_effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return delay_cast_effects

    async def polymorph_spell_template_id(self) -> int:
        return await self.read_value_from_offset(568, "unsigned int")

    async def write_polymorph_spell_template_id(self, polymorph_spell_template_id: int):
        await self.write_value_to_offset(
            568, polymorph_spell_template_id, "unsigned int"
        )

    async def side(self) -> str:
        return await self.read_string_from_offset(592)

    async def write_side(self, side: str):
        await self.write_string_to_offset(592, side)

    async def shadow_spells_disabled(self) -> bool:
        return await self.read_value_from_offset(637, "bool")

    async def write_shadow_spells_disabled(self, shadow_spells_disabled: bool):
        await self.write_value_to_offset(637, shadow_spells_disabled, "bool")

    async def boss_mob(self) -> bool:
        return await self.read_value_from_offset(638, "bool")

    async def write_boss_mob(self, boss_mob: bool):
        await self.write_value_to_offset(638, boss_mob, "bool")

    async def hide_pvp_enemy_chat(self) -> bool:
        return await self.read_value_from_offset(639, "bool")

    async def write_hide_pvp_enemy_chat(self, hide_pvp_enemy_chat: bool):
        await self.write_value_to_offset(639, hide_pvp_enemy_chat, "bool")

    async def combat_trigger_ids(self) -> int:
        return await self.read_value_from_offset(664, "int")

    async def write_combat_trigger_ids(self, combat_trigger_ids: int):
        await self.write_value_to_offset(664, combat_trigger_ids, "int")

    async def backlash(self) -> int:
        return await self.read_value_from_offset(692, "int")

    async def write_backlash(self, backlash: int):
        await self.write_value_to_offset(692, backlash, "int")

    async def past_backlash(self) -> int:
        return await self.read_value_from_offset(696, "int")

    async def write_past_backlash(self, past_backlash: int):
        await self.write_value_to_offset(696, past_backlash, "int")

    async def shadow_creature_level(self) -> int:
        return await self.read_value_from_offset(700, "int")

    async def write_shadow_creature_level(self, shadow_creature_level: int):
        await self.write_value_to_offset(700, shadow_creature_level, "int")

    async def past_shadow_creature_level(self) -> int:
        return await self.read_value_from_offset(704, "int")

    async def write_past_shadow_creature_level(self, past_shadow_creature_level: int):
        await self.write_value_to_offset(704, past_shadow_creature_level, "int")

    async def shadow_creature_level_count(self) -> int:
        return await self.read_value_from_offset(712, "int")

    async def write_shadow_creature_level_count(self, shadow_creature_level_count: int):
        await self.write_value_to_offset(712, shadow_creature_level_count, "int")

    async def intercept_effect(self) -> Optional[DynamicSpellEffect]:
        addr = await self.read_value_from_offset(736, "long long")

        if addr == 0:
            return None

        return DynamicSpellEffect(self.hook_handler, addr)

    async def rounds_since_shadow_pip(self) -> int:
        return await self.read_value_from_offset(768, "int")

    async def write_rounds_since_shadow_pip(self, rounds_since_shadow_pip: int):
        await self.write_value_to_offset(768, rounds_since_shadow_pip, "int")

    async def polymorph_effect(self) -> Optional[DynamicSpellEffect]:
        addr = await self.read_value_from_offset(792, "long long")

        if addr == 0:
            return None

        return DynamicSpellEffect(self.hook_handler, addr)

    async def confused(self) -> int:
        return await self.read_value_from_offset(188, "int")

    async def write_confused(self, confused: int):
        await self.write_value_to_offset(188, confused, "int")

    async def confusion_trigger(self) -> int:
        return await self.read_value_from_offset(192, "int")

    async def write_confusion_trigger(self, confusion_trigger: int):
        await self.write_value_to_offset(192, confusion_trigger, "int")

    async def confusion_display(self) -> bool:
        return await self.read_value_from_offset(196, "bool")

    async def write_confusion_display(self, confusion_display: bool):
        await self.write_value_to_offset(196, confusion_display, "bool")

    async def confused_target(self) -> bool:
        return await self.read_value_from_offset(197, "bool")

    async def write_confused_target(self, confused_target: bool):
        await self.write_value_to_offset(197, confused_target, "bool")

    async def untargetable(self) -> bool:
        return await self.read_value_from_offset(198, "bool")

    async def write_untargetable(self, untargetable: bool):
        await self.write_value_to_offset(198, untargetable, "bool")

    async def untargetable_rounds(self) -> int:
        return await self.read_value_from_offset(200, "int")

    async def write_untargetable_rounds(self, untargetable_rounds: int):
        await self.write_value_to_offset(200, untargetable_rounds, "int")

    async def restricted_target(self) -> bool:
        return await self.read_value_from_offset(204, "bool")

    async def write_restricted_target(self, restricted_target: bool):
        await self.write_value_to_offset(204, restricted_target, "bool")

    async def exit_combat(self) -> bool:
        return await self.read_value_from_offset(205, "bool")

    async def write_exit_combat(self, exit_combat: bool):
        await self.write_value_to_offset(205, exit_combat, "bool")

    async def stunned_display(self) -> bool:
        return await self.read_value_from_offset(184, "bool")

    async def write_stunned_display(self, stunned_display: bool):
        await self.write_value_to_offset(184, stunned_display, "bool")

    async def mindcontrolled_display(self) -> bool:
        return await self.read_value_from_offset(212, "bool")

    async def write_mindcontrolled_display(self, mindcontrolled_display: bool):
        await self.write_value_to_offset(212, mindcontrolled_display, "bool")

    async def auto_pass(self) -> bool:
        return await self.read_value_from_offset(688, "bool")

    async def write_auto_pass(self, auto_pass: bool):
        await self.write_value_to_offset(688, auto_pass, "bool")

    async def vanish(self) -> bool:
        return await self.read_value_from_offset(689, "bool")

    async def write_vanish(self, vanish: bool):
        await self.write_value_to_offset(689, vanish, "bool")

    async def my_team_turn(self) -> bool:
        return await self.read_value_from_offset(690, "bool")

    async def write_my_team_turn(self, my_team_turn: bool):
        await self.write_value_to_offset(690, my_team_turn, "bool")

    async def planning_phase_pip_aquired_type(self) -> PipAquiredByEnum:
        return await self.read_enum(784, PipAquiredByEnum)

    async def write_planning_phase_pip_aquired_type(
        self, planning_phase_pip_aquired_type: PipAquiredByEnum
    ):
        await self.write_enum(784, planning_phase_pip_aquired_type)

    # async def cheat_settings(self) -> class SharedPointer<class CombatCheatSettings>:
    #     return await self.read_value_from_offset(96, "class SharedPointer<class CombatCheatSettings>")

    async def is_monster(self) -> int:
        return await self.read_value_from_offset(400, "unsigned int")

    async def write_is_monster(self, is_monster: int):
        await self.write_value_to_offset(400, is_monster, "unsigned int")

    # async def weapon_nif_sound_list(self) -> class SharedPointer<class SpellNifSoundOverride>:
    #     return await self.read_value_from_offset(80, "class SharedPointer<class SpellNifSoundOverride>")

    async def pet_combat_trigger(self) -> int:
        return await self.read_value_from_offset(680, "int")

    async def write_pet_combat_trigger(self, pet_combat_trigger: int):
        await self.write_value_to_offset(680, pet_combat_trigger, "int")

    async def pet_combat_trigger_target(self) -> int:
        return await self.read_value_from_offset(684, "int")

    async def write_pet_combat_trigger_target(self, pet_combat_trigger_target: int):
        await self.write_value_to_offset(684, pet_combat_trigger_target, "int")

    async def shadow_pip_rate_threshold(self) -> float:
        return await self.read_value_from_offset(808, "float")

    async def write_shadow_pip_rate_threshold(self, shadow_pip_rate_threshold: float):
        await self.write_value_to_offset(808, shadow_pip_rate_threshold, "float")

    async def base_spell_damage(self) -> int:
        return await self.read_value_from_offset(812, "int")

    async def write_base_spell_damage(self, base_spell_damage: int):
        await self.write_value_to_offset(812, base_spell_damage, "int")

    async def stat_damage(self) -> float:
        return await self.read_value_from_offset(816, "float")

    async def write_stat_damage(self, stat_damage: float):
        await self.write_value_to_offset(816, stat_damage, "float")

    async def stat_resist(self) -> float:
        return await self.read_value_from_offset(820, "float")

    async def write_stat_resist(self, stat_resist: float):
        await self.write_value_to_offset(820, stat_resist, "float")

    async def stat_pierce(self) -> float:
        return await self.read_value_from_offset(824, "float")

    async def write_stat_pierce(self, stat_pierce: float):
        await self.write_value_to_offset(824, stat_pierce, "float")

    async def mob_level(self) -> int:
        return await self.read_value_from_offset(828, "int")

    async def write_mob_level(self, mob_level: int):
        await self.write_value_to_offset(828, mob_level, "int")

    async def player_time_updated(self) -> bool:
        return await self.read_value_from_offset(832, "bool")

    async def write_player_time_updated(self, player_time_updated: bool):
        await self.write_value_to_offset(832, player_time_updated, "bool")

    async def player_time_eliminated(self) -> bool:
        return await self.read_value_from_offset(833, "bool")

    async def write_player_time_eliminated(self, player_time_eliminated: bool):
        await self.write_value_to_offset(833, player_time_eliminated, "bool")


class DynamicCombatParticipant(DynamicMemoryObject, CombatParticipant):
    pass
