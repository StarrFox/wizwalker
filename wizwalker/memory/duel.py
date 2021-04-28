from typing import List

from .memory_object import MemoryObject
from .enums import DuelPhase, DuelExecutionOrder, SigilInitiativeSwitchMode
from .combat_participant import DynamicCombatParticipant
from wizwalker.utils import XYZ


class Duel(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def flat_participant_list(self,) -> List[DynamicCombatParticipant]:
        pointers = await self.read_shared_pointers(80)
        participants = []
        for pointer in pointers:
            participants.append(
                DynamicCombatParticipant(self.hook_handler, pointer.pointed_address)
            )

        return participants

    # async def write_flat_participant_list(self, flat_participant_list: class SharedPointer<class CombatParticipant>):
    #     await self.write_value_to_offset(80, flat_participant_list, "class SharedPointer<class CombatParticipant>")

    async def duel_id_full(self) -> int:
        return await self.read_value_from_offset(72, "unsigned long long")

    async def write_duel_id_full(self, duel_id_full: int):
        await self.write_value_to_offset(72, duel_id_full, "unsigned long long")

    async def planning_timer(self) -> float:
        return await self.read_value_from_offset(112, "float")

    async def write_planning_timer(self, planning_timer: float):
        await self.write_value_to_offset(112, planning_timer, "float")

    async def position(self) -> XYZ:
        return await self.read_xyz(116)

    async def write_position(self, position: XYZ):
        await self.write_xyz(116, position)

    async def yaw(self) -> float:
        return await self.read_value_from_offset(128, "float")

    async def write_yaw(self, yaw: float):
        await self.write_value_to_offset(128, yaw, "float")

    async def disable_timer(self) -> bool:
        return await self.read_value_from_offset(146, "bool")

    async def write_disable_timer(self, disable_timer: bool):
        await self.write_value_to_offset(146, disable_timer, "bool")

    async def tutorial_mode(self) -> bool:
        return await self.read_value_from_offset(147, "bool")

    async def write_tutorial_mode(self, tutorial_mode: bool):
        await self.write_value_to_offset(147, tutorial_mode, "bool")

    async def first_team_to_act(self) -> int:
        return await self.read_value_from_offset(148, "int")

    async def write_first_team_to_act(self, first_team_to_act: int):
        await self.write_value_to_offset(148, first_team_to_act, "int")

    # async def combat_resolver(self) -> class CombatResolver*:
    #     return await self.read_value_from_offset(104, "class CombatResolver*")
    #
    # async def write_combat_resolver(self, combat_resolver: class CombatResolver*):
    #     await self.write_value_to_offset(104, combat_resolver, "class CombatResolver*")

    async def pvp(self) -> bool:
        return await self.read_value_from_offset(144, "bool")

    async def write_pvp(self, pvp: bool):
        await self.write_value_to_offset(144, pvp, "bool")

    async def battleground(self) -> bool:
        return await self.read_value_from_offset(145, "bool")

    async def write_battleground(self, b_battleground: bool):
        await self.write_value_to_offset(145, b_battleground, "bool")

    async def round_num(self) -> int:
        return await self.read_value_from_offset(156, "int")

    async def write_round_num(self, round_num: int):
        await self.write_value_to_offset(156, round_num, "int")

    async def execution_phase_timer(self) -> float:
        return await self.read_value_from_offset(164, "float")

    async def write_execution_phase_timer(self, execution_phase_timer: float):
        await self.write_value_to_offset(164, execution_phase_timer, "float")

    # async def execution_phase_combat_actions(self) -> class CombatAction:
    #     return await self.read_value_from_offset(168, "class CombatAction")
    #
    # async def write_execution_phase_combat_actions(self, execution_phase_combat_actions: class CombatAction):
    #     await self.write_value_to_offset(168, execution_phase_combat_actions, "class CombatAction")

    # async def sigil_actions(self) -> class CombatAction:
    #     return await self.read_value_from_offset(184, "class CombatAction")
    #
    # async def write_sigil_actions(self, sigil_actions: class CombatAction):
    #     await self.write_value_to_offset(184, sigil_actions, "class CombatAction")

    # async def shadow_pip_rule(self) -> class SharedPointer<class ShadowPipRule>:
    #     return await self.read_value_from_offset(240, "class SharedPointer<class ShadowPipRule>")
    #
    # async def write_shadow_pip_rule(self, shadow_pip_rule: class SharedPointer<class ShadowPipRule>):
    #     await self.write_value_to_offset(240, shadow_pip_rule, "class SharedPointer<class ShadowPipRule>")

    # async def game_object_anim_state_tracker(self) -> class GameObjectAnimStateTracker:
    #     return await self.read_value_from_offset(256, "class GameObjectAnimStateTracker")
    #
    # async def write_game_object_anim_state_tracker(self, game_object_anim_state_tracker: GameObjectAnimStateTracker):
    #     await self.write_value_to_offset(256, game_object_anim_state_tracker, "class GameObjectAnimStateTracker")

    async def duel_phase(self) -> DuelPhase:
        return await self.read_enum(160, DuelPhase)

    async def write_duel_phase(self, duel_phase: DuelPhase):
        await self.write_enum(160, duel_phase)

    # async def duel_modifier(self) -> class SharedPointer<class DuelModifier>:
    #     return await self.read_value_from_offset(224, "class SharedPointer<class DuelModifier>")
    #
    # async def write_duel_modifier(self, duel_modifier: class SharedPointer<class DuelModifier>):
    #     await self.write_value_to_offset(224, duel_modifier, "class SharedPointer<class DuelModifier>")

    async def initiative_switch_mode(self) -> SigilInitiativeSwitchMode:
        return await self.read_enum(344, SigilInitiativeSwitchMode)

    async def write_initiative_switch_mode(
        self, initiative_switch_mode: SigilInitiativeSwitchMode
    ):
        await self.write_enum(344, initiative_switch_mode)

    async def initiative_switch_rounds(self) -> int:
        return await self.read_value_from_offset(348, "int")

    async def write_initiative_switch_rounds(self, initiative_switch_rounds: int):
        await self.write_value_to_offset(348, initiative_switch_rounds, "int")

    # async def combat_rules(self) -> class SharedPointer<class CombatRule>:
    #     return await self.read_value_from_offset(424, "class SharedPointer<class CombatRule>")
    #
    # async def write_combat_rules(self, combat_rules: class SharedPointer<class CombatRule>):
    #     await self.write_value_to_offset(424, combat_rules, "class SharedPointer<class CombatRule>")

    # async def alternate_turn_combat_rule(self) -> class SharedPointer<class AlternateTurnsCombatRule>:
    #     return await self.read_value_from_offset(440, "class SharedPointer<class AlternateTurnsCombatRule>")
    #
    # async def write_alternate_turn_combat_rule(self, alternate_turn_combat_rule: sharedpointer AlternateTurnsCombatRule):
    #     await self.write_value_to_offset(440, alternate_turn_combat_rule, SharedPointer<class AlternateTurnsCombatRule")

    async def alt_turn_counter(self) -> int:
        return await self.read_value_from_offset(416, "int")

    async def write_alt_turn_counter(self, alt_turn_counter: int):
        await self.write_value_to_offset(416, alt_turn_counter, "int")

    async def original_first_team_to_act(self) -> int:
        return await self.read_value_from_offset(152, "int")

    async def write_original_first_team_to_act(self, original_first_team_to_act: int):
        await self.write_value_to_offset(152, original_first_team_to_act, "int")

    async def execution_order(self) -> DuelExecutionOrder:
        return await self.read_enum(456, DuelExecutionOrder)

    async def write_execution_order(self, execution_order: DuelExecutionOrder):
        await self.write_enum(456, execution_order)

    async def no_henchmen(self) -> bool:
        return await self.read_value_from_offset(460, "bool")

    async def write_no_henchmen(self, no_henchmen: bool):
        await self.write_value_to_offset(460, no_henchmen, "bool")

    async def spell_truncation(self) -> bool:
        return await self.read_value_from_offset(461, "bool")

    async def write_spell_truncation(self, _spell_truncation: bool):
        await self.write_value_to_offset(461, _spell_truncation, "bool")

    async def shadow_threshold_factor(self) -> float:
        return await self.read_value_from_offset(468, "float")

    async def write_shadow_threshold_factor(self, shadow_threshold_factor: float):
        await self.write_value_to_offset(468, shadow_threshold_factor, "float")

    async def shadow_pip_rating_factor(self) -> float:
        return await self.read_value_from_offset(472, "float")

    async def write_shadow_pip_rating_factor(self, shadow_pip_rating_factor: float):
        await self.write_value_to_offset(472, shadow_pip_rating_factor, "float")

    async def default_shadow_pip_rating(self) -> float:
        return await self.read_value_from_offset(476, "float")

    async def write_default_shadow_pip_rating(self, default_shadow_pip_rating: float):
        await self.write_value_to_offset(476, default_shadow_pip_rating, "float")

    async def shadow_pip_threshold_team0(self) -> float:
        return await self.read_value_from_offset(480, "float")

    async def write_shadow_pip_threshold_team0(self, shadow_pip_threshold_team0: float):
        await self.write_value_to_offset(480, shadow_pip_threshold_team0, "float")

    async def shadow_pip_threshold_team1(self) -> float:
        return await self.read_value_from_offset(484, "float")

    async def write_shadow_pip_threshold_team1(self, shadow_pip_threshold_team1: float):
        await self.write_value_to_offset(484, shadow_pip_threshold_team1, "float")

    async def scalar_damage(self) -> float:
        return await self.read_value_from_offset(512, "float")

    async def write_scalar_damage(self, scalar_damage: float):
        await self.write_value_to_offset(512, scalar_damage, "float")

    async def scalar_resist(self) -> float:
        return await self.read_value_from_offset(516, "float")

    async def write_scalar_resist(self, scalar_resist: float):
        await self.write_value_to_offset(516, scalar_resist, "float")

    async def scalar_pierce(self) -> float:
        return await self.read_value_from_offset(520, "float")

    async def write_scalar_pierce(self, scalar_pierce: float):
        await self.write_value_to_offset(520, scalar_pierce, "float")

    async def damage_limit(self) -> float:
        return await self.read_value_from_offset(524, "float")

    async def write_damage_limit(self, damage_limit: float):
        await self.write_value_to_offset(524, damage_limit, "float")

    async def d_k0(self) -> float:
        return await self.read_value_from_offset(528, "float")

    async def write_d_k0(self, d_k0: float):
        await self.write_value_to_offset(528, d_k0, "float")

    async def d_n0(self) -> float:
        return await self.read_value_from_offset(532, "float")

    async def write_d_n0(self, d_n0: float):
        await self.write_value_to_offset(532, d_n0, "float")

    async def resist_limit(self) -> float:
        return await self.read_value_from_offset(536, "float")

    async def write_resist_limit(self, resist_limit: float):
        await self.write_value_to_offset(536, resist_limit, "float")

    async def r_k0(self) -> float:
        return await self.read_value_from_offset(540, "float")

    async def write_r_k0(self, r_k0: float):
        await self.write_value_to_offset(540, r_k0, "float")

    async def r_n0(self) -> float:
        return await self.read_value_from_offset(544, "float")

    async def write_r_n0(self, r_n0: float):
        await self.write_value_to_offset(544, r_n0, "float")


class PlayerDuel(Duel):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_duel_base()
