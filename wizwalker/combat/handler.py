import time
from collections.abc import Callable

from .member import CombatMember
from .card import CombatCard
from ..memory import DuelPhase, EffectTarget, SpellEffects, WindowFlags
from wizwalker import utils


class CombatHandler:
    """
    Handles client's battles
    """

    def __init__(self, client):
        self.client = client

        self._spell_check_boxes = None

    def handle_round(self):
        """
        Called at the start of each round
        """
        raise NotImplementedError()

    def handle_combat(self):
        """
        Handles an entire combat interaction
        """
        while self.in_combat():
            self.wait_for_planning_phase()
            round_number = self.round_number()
            # TODO: handle this taking longer than planning timer time
            self.handle_round()
            self.wait_until_next_round(round_number)

        self._spell_check_boxes = None

    def wait_for_planning_phase(self, sleep_time: float = 0.5):
        """
        Wait for the duel to enter the planning phase

        Args:
            sleep_time: Time to sleep between checks
        """
        utils.wait_for_value(
            self.client.duel.duel_phase, DuelPhase.planning, sleep_time
        )

    def wait_for_combat(self, sleep_time: float = 0.5):
        """
        Wait until in combat
        """
        utils.wait_for_value(self.in_combat, True, sleep_time)
        self.handle_combat()

    def wait_until_next_round(self, current_round: int, sleep_time: float = 0.5):
        """
        Wait for the round number to change
        """
        # can't use wait_for_value bc of the special in_combat condition
        # so we don't get stuck waiting if combat ends
        while self.in_combat():
            new_round_number = self.round_number()
            if new_round_number > current_round:
                return

            time.sleep(sleep_time)

    def in_combat(self) -> bool:
        """
        If the client is in combat or not
        """
        return self.client.in_battle()

    def _get_card_windows(self):
        # these can be cached bc they are static
        if self._spell_check_boxes:
            return self._spell_check_boxes

        spell_checkbox_windows = self.client.root_window.get_windows_with_type(
            "SpellCheckBox"
        )

        self._spell_check_boxes = spell_checkbox_windows
        return self._spell_check_boxes

    def get_cards(self) -> list[CombatCard]:
        """
        List of active CombatCards
        """
        spell_checkbox_windows = self._get_card_windows()

        cards = []
        # cards are ordered right to left so we need to flip them
        for spell_checkbox in spell_checkbox_windows[::-1]:
            if WindowFlags.visible in spell_checkbox.flags():
                card = CombatCard(self, spell_checkbox)
                cards.append(card)

        return cards

    def get_cards_with_predicate(self, pred: Callable) -> list[CombatCard]:
        """
        Return cards that match a predicate

        Args:
            pred: The predicate function
        """
        cards = []

        for card in self.get_cards():
            if pred(card):
                cards.append(card)

        return cards

    def get_card_named(self, name: str) -> CombatCard:
        """
        Returns the first Card with name
        """

        def _pred(card):
            return name.lower() == card.display_name().lower()

        try:
            possible = self.get_cards_with_predicate(_pred)
        except ValueError as e:
            raise RuntimeError(e)

        if possible:
            return possible[0]

        raise ValueError(f"Couldn't find a card named {name}")

    # TODO: add allow_treasure_cards that defaults to False
    def get_damaging_aoes(self, *, check_enchanted: bool = None):
        """
        Get a list of all damaging aoes in hand

        Keyword Args:
            check_enchanted: None -> don't check enchanted; False -> non-enchanted; True -> enchanted
        """

        def _pred(card):
            if check_enchanted is True:
                if not card.is_enchanted():
                    return False

            elif check_enchanted is False:
                if card.is_enchanted():
                    return False

            if card.type_name() != "AOE":
                return False

            effects = card.get_spell_effects()

            for effect in effects:
                effect_type = effect.maybe_read_type_name()
                if effect_type.lower() in ("variable", "random"):
                    for sub_effect in effect.maybe_effect_list():
                        if sub_effect.effect_target() in (
                            EffectTarget.enemy_team,
                            EffectTarget.enemy_team_all_at_once,
                        ):
                            return True

                else:
                    if effect.effect_target() in (
                        EffectTarget.enemy_team,
                        EffectTarget.enemy_team_all_at_once,
                    ):
                        return True

        return self.get_cards_with_predicate(_pred)

    def get_damage_enchants(self, *, sort_by_damage: bool = False):
        """
        Get enchants that increse the damage of spells

        Keyword Args:
            sort_by_damage: If enchants should be sorted by how much damage they add
        """

        def _pred(card):
            if card.type_name() != "Enchantment":
                return False

            for effect in card.get_spell_effects():
                if effect.effect_type() == SpellEffects.modify_card_damage:
                    return True

            return False

        damage_enchants = self.get_cards_with_predicate(_pred)

        if not sort_by_damage:
            return damage_enchants

        def _sort_by_damage(card):
            effect = card.get_spell_effects()[0]
            return effect.effect_param()

        return sorted(damage_enchants, key=_sort_by_damage)

    def get_members(self) -> list[CombatMember]:
        """
        List of active CombatMembers
        """
        combatant_windows = self.client.root_window.get_windows_with_name(
            "CombatantControl"
        )

        members = []

        for window in combatant_windows:
            members.append(CombatMember(self, window))

        return members

    def get_members_with_predicate(self, pred: Callable) -> list[CombatMember]:
        """
        Return members that match a predicate

        Args:
            pred: The predicate function
        """
        members = []

        for member in self.get_members():
            if pred(member):
                members.append(member)

        return members

    def get_client_member(self) -> CombatMember:
        """
        Get the client's CombatMember
        """
        members = self.get_members()

        for member in members:
            if member.is_client():
                return member

        raise ValueError("Couldn't find client's CombatMember")

    def get_all_monster_members(self) -> list[CombatMember]:
        """
        Get all members who are monsters
        """
        members = self.get_members()

        monsters = []
        for member in members:
            if member.is_monster():
                monsters.append(member)

        return monsters

    def get_all_player_members(self) -> list[CombatMember]:
        """
        Get all members who are players
        """
        members = self.get_members()

        players = []
        for member in members:
            if member.is_player():
                players.append(member)

        return players

    def get_member_named(self, name: str) -> CombatMember:
        """
        Returns the first Member with name
        """
        members = self.get_members()

        for member in members:
            if name.lower() in member.name().lower():
                return member

        raise ValueError(f"Couldn't find a member named {name}")

    def attempt_cast(
        self,
        name: str,
        *,
        on_member: str = None,
        on_card: str = None,
        on_client: bool = False,
    ):
        """
        Attempt to cast a card

        Args:
            name: Name of the card to cast
            on_member: Name of the member to cast the card on
            on_card: Name of the card to cast the card on
            on_client: Bool if the card should be cast on the client
        """
        try:
            card = self.get_card_named(name)

            if on_member:
                target = self.get_member_named(on_member)
                card.cast(target)

            elif on_card:
                target = self.get_card_named(on_card)
                card.cast(target)

            elif on_client:
                target = self.get_client_member()
                card.cast(target)

            else:
                card.cast(None)

            return True

        except ValueError:
            return False

    def round_number(self) -> int:
        """
        Current round number
        """
        return self.client.duel.round_num()

    def pass_button(self):
        """
        Click the pass button
        """
        pos_done_window = self.client.root_window.get_windows_with_name(
            "DoneWindow"
        )
        if pos_done_window:
            done_window = pos_done_window[0]

            if done_window.is_visible():
                pos_defeated_pass_button = done_window.get_windows_with_name(
                    "DefeatedPassButton"
                )
                defeated_pass_button = pos_defeated_pass_button[0]

                return self.client.mouse_handler.click_window(
                    defeated_pass_button
                )

        self.client.mouse_handler.click_window_with_name("Focus")

    def draw_button(self):
        """
        Click the draw button
        """
        self.client.mouse_handler.click_window_with_name("Draw")

    def flee_button(self):
        """
        Click the free button
        """
        pos_done_window = self.client.root_window.get_windows_with_name(
            "DoneWindow"
        )
        if pos_done_window:
            done_window = pos_done_window[0]

            if done_window.is_visible():
                pos_defeated_flee_button = done_window.get_windows_with_name(
                    "DefeatedFleeButton"
                )
                defeated_flee_button = pos_defeated_flee_button[0]

                return self.client.mouse_handler.click_window(
                    defeated_flee_button
                )

        self.client.mouse_handler.click_window_with_name("Flee")


class AoeHandler(CombatHandler):
    """
    Subclass of CombatHandler that just casts enchanted aoes
    """

    def handle_round(self):
        enchanted_aoes = self.get_damaging_aoes(check_enchanted=True)
        if enchanted_aoes:
            enchanted_aoes[0].cast(None)

        unenchanted_aoes = self.get_damaging_aoes(check_enchanted=False)
        enchants = self.get_damage_enchants(sort_by_damage=True)

        # enchant card then cast card
        if enchants and unenchanted_aoes:
            enchants[0].cast(unenchanted_aoes[0])
            enchanted_aoes = self.get_damaging_aoes(check_enchanted=True)

            if not enchanted_aoes:
                raise Exception("Enchant failure")

            to_cast = enchanted_aoes[0]

            if to_cast.is_castable():
                to_cast.cast(None)

        # no enchants so just cast card
        elif not enchants and unenchanted_aoes:
            to_cast = unenchanted_aoes[0]

            if to_cast.is_castable():
                to_cast.cast(None)

        # hand full of enchants or enchants + other cards
        elif enchants and not unenchanted_aoes:
            if len(self.get_cards()) == 7:
                enchants[0].discard()

            # TODO: draw tc?
            else:
                raise Exception("No hits in hand")

        # no enchants or aoes in hand
        else:
            # TODO: maybe flee instead?
            if len(self.get_cards()) == 0:
                raise Exception("Out of cards")

            # TODO: add method for people to subclass for this?
            raise Exception("Out of hits and enchants")
