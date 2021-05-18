import asyncio
from typing import List
from warnings import warn

from .member import CombatMember
from .card import CombatCard
from ..memory import DuelPhase, WindowFlags
from wizwalker import utils


class CombatHandler:
    """
    Handles client's battles
    """

    def __init__(self, client):
        self.client = client

        self._spell_check_boxes = None

    async def handle_round(self):
        """
        Called at the start of each round
        """
        raise NotImplementedError()

    async def handle_combat(self):
        """
        Handles an entire combat interaction
        """
        while await self.in_combat():
            await self.wait_for_planning_phase()
            round_number = await self.round_number()
            # TODO: handle this taking longer than planning timer time
            await self.handle_round()
            await self.wait_until_next_round(round_number)

    # TODO: remove in 2.0
    async def wait_for_hand_visible(self, sleep_time: float = 0.5):
        """
        Wait for the hand window to be visible
        """
        warn(
            "This method is depreciated and will be removed in 2.0 please use wait_for_planning_phase instead",
            DeprecationWarning,
        )

        hand = await self.client.root_window.get_windows_with_name("Hand")
        # this window is always in ui tree
        hand = hand[0]
        while WindowFlags.visible not in await hand.flags():
            await asyncio.sleep(sleep_time)

    async def wait_for_planning_phase(self, sleep_time: float = 0.5):
        """
        Wait for the duel to enter the planning phase

        Args:
            sleep_time: Time to sleep between checks
        """
        await utils.wait_for_value(
            self.client.duel.duel_phase, DuelPhase.planning, sleep_time
        )

    async def wait_for_combat(self, sleep_time: float = 0.5):
        """
        Wait until in combat
        """
        await utils.wait_for_value(self.in_combat, True, sleep_time)
        await self.handle_combat()

    async def wait_until_next_round(self, current_round: int, sleep_time: float = 0.5):
        """
        Wait for the round number to change
        """
        # can't use wait_for_value bc of the special in_combat condition
        # so we don't get stuck waiting if combat ends
        while await self.in_combat():
            new_round_number = await self.round_number()
            if new_round_number > current_round:
                return

            await asyncio.sleep(sleep_time)

    async def in_combat(self) -> bool:
        """
        If the client is in combat or not
        """
        return await self.client.in_battle()

    async def _get_card_windows(self):
        # these can be cached bc they are static
        if self._spell_check_boxes:
            return self._spell_check_boxes

        spell_checkbox_windows = await self.client.root_window.get_windows_with_type(
            "SpellCheckBox"
        )
        # last SpellCheckBox isn't a card
        spell_checkbox_windows.pop()

        self._spell_check_boxes = spell_checkbox_windows
        return self._spell_check_boxes

    async def get_cards(self) -> List[CombatCard]:
        """
        List of active CombatCards
        """
        spell_checkbox_windows = await self._get_card_windows()

        cards = []
        # cards are ordered right to left so we need to flip them
        for spell_checkbox in spell_checkbox_windows[::-1]:
            if WindowFlags.visible in await spell_checkbox.flags():
                card = CombatCard(self, spell_checkbox)
                cards.append(card)

        return cards

    async def get_members(self) -> List[CombatMember]:
        """
        List of active CombatMembers
        """
        combatant_windows = await self.client.root_window.get_windows_with_name(
            "CombatantControl"
        )

        members = []

        for window in combatant_windows:
            members.append(CombatMember(self, window))

        return members

    async def get_client_member(self) -> CombatMember:
        """
        Get the client's CombatMember
        """
        members = await self.get_members()

        for member in members:
            if await member.is_client():
                return member

        # this shouldn't be possible
        raise ValueError("Couldn't find client's CombatMember")

    async def get_all_monster_members(self) -> List[CombatMember]:
        """
        Get all members who are monsters
        """
        members = await self.get_members()

        monsters = []
        for member in members:
            if await member.is_monster():
                monsters.append(member)

        return monsters

    async def get_all_player_members(self) -> List[CombatMember]:
        """
        Get all members who are players
        """
        members = await self.get_members()

        players = []
        for member in members:
            if await member.is_player():
                players.append(member)

        return players

    async def get_card_named(self, name: str) -> CombatCard:
        """
        Returns the first Card with name
        """
        cards = await self.get_cards()

        for card in cards:
            if name.lower() == (await card.name()).lower():
                return card

        raise ValueError(f"Couldn't find a card named {name}")

    async def get_member_named(self, name: str) -> CombatMember:
        """
        Returns the first Member with name
        """
        members = await self.get_members()

        for member in members:
            if name.lower() in (await member.name()).lower():
                return member

        raise ValueError(f"Couldn't find a member named {name}")

    async def attempt_cast(
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
            card = await self.get_card_named(name)

            if on_member:
                target = await self.get_member_named(on_member)
                await card.cast(target)

            elif on_card:
                target = await self.get_card_named(on_card)
                await card.cast(target)

            elif on_client:
                target = await self.get_client_member()
                await card.cast(target)

            else:
                await card.cast(None)

            return True

        except ValueError:
            return False

    async def round_number(self) -> int:
        """
        Current round number
        """
        return await self.client.duel.round_num()

    async def pass_button(self):
        """
        Click the pass button
        """
        await self.client.mouse_handler.click_window_with_name("Focus")

    async def draw_button(self):
        """
        Click the draw button
        """
        await self.client.mouse_handler.click_window_with_name("Draw")

    async def flee_button(self):
        """
        Click the free button
        """
        await self.client.mouse_handler.click_window_with_name("Flee")
