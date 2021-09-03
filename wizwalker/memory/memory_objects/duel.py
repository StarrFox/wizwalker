from typing import Optional

from wizwalker.utils import XYZ
from wizwalker.memory.memory_object import PropertyClass
from .combat_participant import DynamicCombatParticipant
from .enums import DuelExecutionOrder, DuelPhase, SigilInitiativeSwitchMode
from .combat_resolver import DynamicCombatResolver


class Duel(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def participant_list(
        self,
    ) -> list[DynamicCombatParticipant]:
        pointers = self.read_shared_vector(80)

        participants = []
        for addr in pointers:
            participants.append(DynamicCombatParticipant(self.hook_handler, addr))

        return participants

    def duel_id_full(self) -> int:
        return self.read_value_from_offset(72, "unsigned long long")

    def write_duel_id_full(self, duel_id_full: int):
        self.write_value_to_offset(72, duel_id_full, "unsigned long long")

    def planning_timer(self) -> float:
        return self.read_value_from_offset(112, "float")

    def write_planning_timer(self, planning_timer: float):
        self.write_value_to_offset(112, planning_timer, "float")

    def position(self) -> XYZ:
        return self.read_xyz(116)

    def write_position(self, position: XYZ):
        self.write_xyz(116, position)

    def yaw(self) -> float:
        return self.read_value_from_offset(128, "float")

    def write_yaw(self, yaw: float):
        self.write_value_to_offset(128, yaw, "float")

    def disable_timer(self) -> bool:
        return self.read_value_from_offset(146, "bool")

    def write_disable_timer(self, disable_timer: bool):
        self.write_value_to_offset(146, disable_timer, "bool")

    def tutorial_mode(self) -> bool:
        return self.read_value_from_offset(147, "bool")

    def write_tutorial_mode(self, tutorial_mode: bool):
        self.write_value_to_offset(147, tutorial_mode, "bool")

    def first_team_to_act(self) -> int:
        return self.read_value_from_offset(148, "int")

    def write_first_team_to_act(self, first_team_to_act: int):
        self.write_value_to_offset(148, first_team_to_act, "int")

    def combat_resolver(self) -> Optional[DynamicCombatResolver]:
        addr = self.read_value_from_offset(104, "long long")

        if addr == 0:
            return None

        return DynamicCombatResolver(self.hook_handler, addr)

    def pvp(self) -> bool:
        return self.read_value_from_offset(144, "bool")

    def write_pvp(self, pvp: bool):
        self.write_value_to_offset(144, pvp, "bool")

    def battleground(self) -> bool:
        return self.read_value_from_offset(145, "bool")

    def write_battleground(self, b_battleground: bool):
        self.write_value_to_offset(145, b_battleground, "bool")

    def round_num(self) -> int:
        return self.read_value_from_offset(156, "int")

    def write_round_num(self, round_num: int):
        self.write_value_to_offset(156, round_num, "int")

    def execution_phase_timer(self) -> float:
        return self.read_value_from_offset(164, "float")

    def write_execution_phase_timer(self, execution_phase_timer: float):
        self.write_value_to_offset(164, execution_phase_timer, "float")

    # note: this seems to be unused
    # def execution_phase_combat_actions(self) -> class CombatAction:
    #     return self.read_value_from_offset(168, "class CombatAction")

    # note: this also seems to be unused
    # def sigil_actions(self) -> class CombatAction:
    #     return self.read_value_from_offset(184, "class CombatAction")

    # def shadow_pip_rule(self) -> class SharedPointer<class ShadowPipRule>:
    #     return self.read_value_from_offset(240, "class SharedPointer<class ShadowPipRule>")

    # def game_object_anim_state_tracker(self) -> class GameObjectAnimStateTracker:
    #     return self.read_value_from_offset(256, "class GameObjectAnimStateTracker")

    def duel_phase(self) -> DuelPhase:
        return self.read_enum(160, DuelPhase)

    def write_duel_phase(self, duel_phase: DuelPhase):
        self.write_enum(160, duel_phase)

    # def duel_modifier(self) -> class SharedPointer<class DuelModifier>:
    #     return self.read_value_from_offset(224, "class SharedPointer<class DuelModifier>")

    def initiative_switch_mode(self) -> SigilInitiativeSwitchMode:
        return self.read_enum(344, SigilInitiativeSwitchMode)

    def write_initiative_switch_mode(
        self, initiative_switch_mode: SigilInitiativeSwitchMode
    ):
        self.write_enum(344, initiative_switch_mode)

    def initiative_switch_rounds(self) -> int:
        return self.read_value_from_offset(348, "int")

    def write_initiative_switch_rounds(self, initiative_switch_rounds: int):
        self.write_value_to_offset(348, initiative_switch_rounds, "int")

    # def combat_rules(self) -> class SharedPointer<class CombatRule>:
    #     return self.read_value_from_offset(424, "class SharedPointer<class CombatRule>")

    # def alternate_turn_combat_rule(self) -> class SharedPointer<class AlternateTurnsCombatRule>:
    #     return self.read_value_from_offset(440, "class SharedPointer<class AlternateTurnsCombatRule>")

    def alt_turn_counter(self) -> int:
        return self.read_value_from_offset(416, "int")

    def write_alt_turn_counter(self, alt_turn_counter: int):
        self.write_value_to_offset(416, alt_turn_counter, "int")

    def original_first_team_to_act(self) -> int:
        return self.read_value_from_offset(152, "int")

    def write_original_first_team_to_act(self, original_first_team_to_act: int):
        self.write_value_to_offset(152, original_first_team_to_act, "int")

    def execution_order(self) -> DuelExecutionOrder:
        return self.read_enum(456, DuelExecutionOrder)

    def write_execution_order(self, execution_order: DuelExecutionOrder):
        self.write_enum(456, execution_order)

    def no_henchmen(self) -> bool:
        return self.read_value_from_offset(460, "bool")

    def write_no_henchmen(self, no_henchmen: bool):
        self.write_value_to_offset(460, no_henchmen, "bool")

    def spell_truncation(self) -> bool:
        return self.read_value_from_offset(461, "bool")

    def write_spell_truncation(self, spell_truncation: bool):
        self.write_value_to_offset(461, spell_truncation, "bool")

    def shadow_threshold_factor(self) -> float:
        return self.read_value_from_offset(468, "float")

    def write_shadow_threshold_factor(self, shadow_threshold_factor: float):
        self.write_value_to_offset(468, shadow_threshold_factor, "float")

    def shadow_pip_rating_factor(self) -> float:
        return self.read_value_from_offset(472, "float")

    def write_shadow_pip_rating_factor(self, shadow_pip_rating_factor: float):
        self.write_value_to_offset(472, shadow_pip_rating_factor, "float")

    def default_shadow_pip_rating(self) -> float:
        return self.read_value_from_offset(476, "float")

    def write_default_shadow_pip_rating(self, default_shadow_pip_rating: float):
        self.write_value_to_offset(476, default_shadow_pip_rating, "float")

    def shadow_pip_threshold_team0(self) -> float:
        return self.read_value_from_offset(480, "float")

    def write_shadow_pip_threshold_team0(self, shadow_pip_threshold_team0: float):
        self.write_value_to_offset(480, shadow_pip_threshold_team0, "float")

    def shadow_pip_threshold_team1(self) -> float:
        return self.read_value_from_offset(484, "float")

    def write_shadow_pip_threshold_team1(self, shadow_pip_threshold_team1: float):
        self.write_value_to_offset(484, shadow_pip_threshold_team1, "float")

    def scalar_damage(self) -> float:
        return self.read_value_from_offset(512, "float")

    def write_scalar_damage(self, scalar_damage: float):
        self.write_value_to_offset(512, scalar_damage, "float")

    def scalar_resist(self) -> float:
        return self.read_value_from_offset(516, "float")

    def write_scalar_resist(self, scalar_resist: float):
        self.write_value_to_offset(516, scalar_resist, "float")

    def scalar_pierce(self) -> float:
        return self.read_value_from_offset(520, "float")

    def write_scalar_pierce(self, scalar_pierce: float):
        self.write_value_to_offset(520, scalar_pierce, "float")

    def damage_limit(self) -> float:
        return self.read_value_from_offset(524, "float")

    def write_damage_limit(self, damage_limit: float):
        self.write_value_to_offset(524, damage_limit, "float")

    def d_k0(self) -> float:
        return self.read_value_from_offset(528, "float")

    def write_d_k0(self, d_k0: float):
        self.write_value_to_offset(528, d_k0, "float")

    def d_n0(self) -> float:
        return self.read_value_from_offset(532, "float")

    def write_d_n0(self, d_n0: float):
        self.write_value_to_offset(532, d_n0, "float")

    def resist_limit(self) -> float:
        return self.read_value_from_offset(536, "float")

    def write_resist_limit(self, resist_limit: float):
        self.write_value_to_offset(536, resist_limit, "float")

    def r_k0(self) -> float:
        return self.read_value_from_offset(540, "float")

    def write_r_k0(self, r_k0: float):
        self.write_value_to_offset(540, r_k0, "float")

    def r_n0(self) -> float:
        return self.read_value_from_offset(544, "float")

    def write_r_n0(self, r_n0: float):
        self.write_value_to_offset(544, r_n0, "float")

    def full_party_group(self) -> bool:
        return self.read_value_from_offset(548, "bool")

    def write_full_party_group(self, full_party_group: bool):
        self.write_value_to_offset(548, full_party_group, "bool")


class CurrentDuel(Duel):
    def read_base_address(self) -> int:
        return self.hook_handler.read_current_duel_base()
