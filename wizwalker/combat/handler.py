import asyncio
from typing import List

from .member import CombatMember
from .card import CombatCard
from ..memory import WindowFlags


class CombatHandler:
    """
    Handles client's battles
    """

    def __init__(self, client):
        self.client = client

        self._spell_check_boxes = None

    async def handle_round(self):
        raise NotImplementedError()

    async def handle_combat(self):
        while await self.in_combat():
            # give game time to prepare combat
            await asyncio.sleep(1)
            round_number = await self.round_number()
            await self.handle_round()
            await self.wait_until_next_round(round_number)

    async def wait_until_next_round(self, current_round: int, sleep_time: float = 0.5):
        """
        Wait for the round number to change
        """
        # so we don't get stuck waiting if combat ends
        while await self.in_combat():
            new_round_number = await self.round_number()
            if new_round_number > current_round:
                return

            await asyncio.sleep(sleep_time)

    async def in_combat(self) -> bool:
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

    # async def get_cards_with(
    #     self, *, name: str = None, enchanted: bool = None, template_id: int = None
    # ):
    #     # filter cards
    #     pass

    # async def get_members_with(self):
    #     # filter members
    #     pass

    async def round_number(self) -> int:
        return await self.client.duel.round_num()

    async def pass_button(self):
        pass

    async def draw_button(self):
        pass

    async def flee_button(self):
        pass
