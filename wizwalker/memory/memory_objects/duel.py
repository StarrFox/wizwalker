from typing import List, Optional

from wizwalker.utils import XYZ
from wizwalker.memory.memory_object import PropertyClass
from .combat_participant import AddressedCombatParticipant
from .enums import DuelExecutionOrder, DuelPhase, SigilInitiativeSwitchMode
from .combat_resolver import AddressedCombatResolver


# TODO: add m_gameEffectInfo and friends, and fix offsets
class Duel(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def participant_list(
        self,
    ) -> List[AddressedCombatParticipant]:
        pointers = await self.read_shared_vector(80)

        participants = []
        for addr in pointers:
            participants.append(AddressedCombatParticipant(self.memory_reader, addr))

        return participants

    # TODO: need to add new type
    # async def dynamicTeams offset=104

    async def dynamic_turn(self) -> int:
        return await self.read_value_from_offset(120, "unsigned int")

    async def write_dynamic_turn(self, dynamic_turn: int):
        await self.write_value_to_offset(120, dynamic_turn, "unsigned int")

    async def dynamic_turn_subcircles(self) -> int:
        return await self.read_value_from_offset(124, "unsigned int")

    async def write_dynamic_turn_subcircle(self, dynamic_turn_subcircle: int):
        await self.write_value_to_offset(124, dynamic_turn_subcircle, "unsigned int")

    async def dynamic_turn_counter(self) -> int:
        return await self.read_value_from_offset(128, "int")

    async def write_dynamic_turn_counter(self, dynamic_turn_counter: int):
        await self.write_value_to_offset(128, dynamic_turn_counter, "int")

    async def duel_id_full(self) -> int:
        return await self.read_value_from_offset(72, "unsigned long long")

    async def write_duel_id_full(self, duel_id_full: int):
        await self.write_value_to_offset(72, duel_id_full, "unsigned long long")

    async def planning_timer(self) -> float:
        return await self.read_value_from_offset(144, "float")

    async def write_planning_timer(self, planning_timer: float):
        await self.write_value_to_offset(144, planning_timer, "float")

    async def position(self) -> XYZ:
        return await self.read_xyz(148)

    async def write_position(self, position: XYZ):
        await self.write_xyz(148, position)

    async def yaw(self) -> float:
        return await self.read_value_from_offset(160, "float")

    async def write_yaw(self, yaw: float):
        await self.write_value_to_offset(160, yaw, "float")

    async def disable_timer(self) -> bool:
        return await self.read_value_from_offset(178, "bool")

    async def write_disable_timer(self, disable_timer: bool):
        await self.write_value_to_offset(178, disable_timer, "bool")

    async def tutorial_mode(self) -> bool:
        return await self.read_value_from_offset(179, "bool")

    async def write_tutorial_mode(self, tutorial_mode: bool):
        await self.write_value_to_offset(179, tutorial_mode, "bool")

    async def first_team_to_act(self) -> int:
        return await self.read_value_from_offset(180, "int")

    async def write_first_team_to_act(self, first_team_to_act: int):
        await self.write_value_to_offset(180, first_team_to_act, "int")

    async def combat_resolver(self) -> Optional[AddressedCombatResolver]:
        addr = await self.read_value_from_offset(136, "long long")

        if addr == 0:
            return None

        return AddressedCombatResolver(self.memory_reader, addr)

    async def pvp(self) -> bool:
        return await self.read_value_from_offset(176, "bool")

    async def write_pvp(self, pvp: bool):
        await self.write_value_to_offset(176, pvp, "bool")

    async def battleground(self) -> bool:
        return await self.read_value_from_offset(177, "bool")

    async def write_battleground(self, b_battleground: bool):
        await self.write_value_to_offset(177, b_battleground, "bool")

    async def round_num(self) -> int:
        return await self.read_value_from_offset(188, "int")

    async def write_round_num(self, round_num: int):
        await self.write_value_to_offset(188, round_num, "int")

    async def execution_phase_timer(self) -> float:
        return await self.read_value_from_offset(196, "float")

    async def write_execution_phase_timer(self, execution_phase_timer: float):
        await self.write_value_to_offset(196, execution_phase_timer, "float")

    # note: this seems to be unused
    # async def execution_phase_combat_actions(self) -> class CombatAction:
    #     return await self.read_value_from_offset(168, "class CombatAction")

    # note: this also seems to be unused
    # async def sigil_actions(self) -> class CombatAction:
    #     return await self.read_value_from_offset(184, "class CombatAction")

    # async def shadow_pip_rule(self) -> class SharedPointer<class ShadowPipRule>:
    #     return await self.read_value_from_offset(240, "class SharedPointer<class ShadowPipRule>")

    # async def game_object_anim_state_tracker(self) -> class GameObjectAnimStateTracker:
    #     return await self.read_value_from_offset(256, "class GameObjectAnimStateTracker")

    async def duel_phase(self) -> DuelPhase:
        return await self.read_enum(192, DuelPhase)

    async def write_duel_phase(self, duel_phase: DuelPhase):
        await self.write_enum(192, duel_phase)

    # async def duel_modifier(self) -> class SharedPointer<class DuelModifier>:
    #     return await self.read_value_from_offset(224, "class SharedPointer<class DuelModifier>")

    async def initiative_switch_mode(self) -> SigilInitiativeSwitchMode:
        return await self.read_enum(376, SigilInitiativeSwitchMode)

    async def write_initiative_switch_mode(
        self, initiative_switch_mode: SigilInitiativeSwitchMode
    ):
        await self.write_enum(376, initiative_switch_mode)

    async def initiative_switch_rounds(self) -> int:
        return await self.read_value_from_offset(380, "int")

    async def write_initiative_switch_rounds(self, initiative_switch_rounds: int):
        await self.write_value_to_offset(380, initiative_switch_rounds, "int")

    # async def combat_rules(self) -> class SharedPointer<class CombatRule>:
    #     return await self.read_value_from_offset(456, "class SharedPointer<class CombatRule>")

    # async def alternate_turn_combat_rule(self) -> class SharedPointer<class AlternateTurnsCombatRule>:
    #     return await self.read_value_from_offset(472, "class SharedPointer<class AlternateTurnsCombatRule>")

    # async def game_effect_info(self):
    #     pass

    async def alt_turn_counter(self) -> int:
        return await self.read_value_from_offset(448, "int")

    async def write_alt_turn_counter(self, alt_turn_counter: int):
        await self.write_value_to_offset(448, alt_turn_counter, "int")

    async def original_first_team_to_act(self) -> int:
        return await self.read_value_from_offset(184, "int")

    async def write_original_first_team_to_act(self, original_first_team_to_act: int):
        await self.write_value_to_offset(184, original_first_team_to_act, "int")

    async def execution_order(self) -> DuelExecutionOrder:
        return await self.read_enum(520, DuelExecutionOrder)

    async def write_execution_order(self, execution_order: DuelExecutionOrder):
        await self.write_enum(520, execution_order)

    async def no_henchmen(self) -> bool:
        return await self.read_value_from_offset(524, "bool")

    async def write_no_henchmen(self, no_henchmen: bool):
        await self.write_value_to_offset(524, no_henchmen, "bool")

    async def spell_truncation(self) -> bool:
        return await self.read_value_from_offset(532, "bool")

    async def write_spell_truncation(self, spell_truncation: bool):
        await self.write_value_to_offset(532, spell_truncation, "bool")

    async def shadow_threshold_factor(self) -> float:
        return await self.read_value_from_offset(540, "float")

    async def write_shadow_threshold_factor(self, shadow_threshold_factor: float):
        await self.write_value_to_offset(540, shadow_threshold_factor, "float")

    async def shadow_pip_rating_factor(self) -> float:
        return await self.read_value_from_offset(544, "float")

    async def write_shadow_pip_rating_factor(self, shadow_pip_rating_factor: float):
        await self.write_value_to_offset(544, shadow_pip_rating_factor, "float")

    async def default_shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(548, "float")

    async def write_default_shadow_pip_rating(self, default_shadow_pip_rating: float):
        await self.write_value_to_offset(548, default_shadow_pip_rating, "float")

    async def shadow_pip_threshold_team0(self) -> float:
        return await self.read_value_from_offset(552, "float")

    async def write_shadow_pip_threshold_team0(self, shadow_pip_threshold_team0: float):
        await self.write_value_to_offset(552, shadow_pip_threshold_team0, "float")

    async def shadow_pip_threshold_team1(self) -> float:
        return await self.read_value_from_offset(556, "float")

    async def write_shadow_pip_threshold_team1(self, shadow_pip_threshold_team1: float):
        await self.write_value_to_offset(556, shadow_pip_threshold_team1, "float")

    async def scalar_damage(self) -> float:
        return await self.read_value_from_offset(584, "float")

    async def write_scalar_damage(self, scalar_damage: float):
        await self.write_value_to_offset(584, scalar_damage, "float")

    async def scalar_resist(self) -> float:
        return await self.read_value_from_offset(588, "float")

    async def write_scalar_resist(self, scalar_resist: float):
        await self.write_value_to_offset(588, scalar_resist, "float")

    async def scalar_pierce(self) -> float:
        return await self.read_value_from_offset(592, "float")

    async def write_scalar_pierce(self, scalar_pierce: float):
        await self.write_value_to_offset(592, scalar_pierce, "float")

    async def damage_limit(self) -> float:
        return await self.read_value_from_offset(596, "float")

    async def write_damage_limit(self, damage_limit: float):
        await self.write_value_to_offset(596, damage_limit, "float")

    # TODO 2.0: this d_ shouldn't be here
    async def d_k0(self) -> float:
        return await self.read_value_from_offset(600, "float")

    async def write_d_k0(self, d_k0: float):
        await self.write_value_to_offset(600, d_k0, "float")

    async def d_n0(self) -> float:
        return await self.read_value_from_offset(604, "float")

    async def write_d_n0(self, d_n0: float):
        await self.write_value_to_offset(604, d_n0, "float")

    async def resist_limit(self) -> float:
        return await self.read_value_from_offset(608, "float")

    async def write_resist_limit(self, resist_limit: float):
        await self.write_value_to_offset(608, resist_limit, "float")

    async def r_k0(self) -> float:
        return await self.read_value_from_offset(612, "float")

    async def write_r_k0(self, r_k0: float):
        await self.write_value_to_offset(612, r_k0, "float")

    async def r_n0(self) -> float:
        return await self.read_value_from_offset(616, "float")

    async def write_r_n0(self, r_n0: float):
        await self.write_value_to_offset(616, r_n0, "float")

    async def full_party_group(self) -> bool:
        return await self.read_value_from_offset(620, "bool")

    async def write_full_party_group(self, full_party_group: bool):
        await self.write_value_to_offset(620, full_party_group, "bool")

    async def match_timer(self) -> float:
        return await self.read_value_from_offset(640, "float")

    async def write_match_timer(self, match_timer: float):
        await self.write_value_to_offset(640, match_timer, "float")

    async def bonus_time(self) -> int:
        return await self.read_value_from_offset(644, "int")

    async def write_bonus_time(self, bonus_time: int):
        await self.write_value_to_offset(644, bonus_time, "int")

    async def pass_penalty(self) -> int:
        return await self.read_value_from_offset(648, "int")

    async def write_pass_penalty(self, pass_penalty: int):
        await self.write_value_to_offset(648, pass_penalty, "int")

    async def yellow_time(self) -> int:
        return await self.read_value_from_offset(652, "int")

    async def write_yellow_time(self, yellow_time: int):
        await self.write_value_to_offset(652, yellow_time, "int")

    async def red_time(self) -> int:
        return await self.read_value_from_offset(656, "int")

    async def write_red_time(self, red_time: int):
        await self.write_value_to_offset(656, red_time, "int")

    async def min_turn_time(self) -> int:
        return await self.read_value_from_offset(660, "int")

    async def write_min_turn_time(self, min_turn_time: int):
        await self.write_value_to_offset(660, min_turn_time, "int")

    async def is_player_timed_duel(self) -> bool:
        return await self.read_value_from_offset(621, "bool")

    async def write_is_player_timed_duel(self, is_player_timed_duel: bool):
        await self.write_value_to_offset(621, is_player_timed_duel, "bool")

    async def hide_noncombatant_distance(self) -> float:
        return await self.read_value_from_offset(528, "float")

    async def write_hide_noncombatant_distance(self, hide_noncombatant_distance: float):
        await self.write_value_to_offset(528, hide_noncombatant_distance, "float")


class CurrentDuel(Duel):
    async def read_base_address(self) -> int:
        return await self.memory_reader.read_current_duel_base()
