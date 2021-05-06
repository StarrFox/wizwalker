from typing import Callable, List

from .card import CombatCard


class CombatHandler:
    """
    Handles client's battles
    """

    def __init__(self, client):
        self.client = client

        self._spell_check_boxes = None
        self._cards = []
        self._positions = {}

    async def in_combat(self) -> bool:
        return await self.client.in_battle()

    # better to cache this
    async def _get_card_windows(self):
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
        List of CombatCards
        """
        if self._cards:
            return self._cards

        spell_checkbox_windows = await self._get_card_windows()

        # cards are ordered right to left so we need to flip them

        position = 0
        for spell_checkbox in spell_checkbox_windows[::-1]:
            card = CombatCard(self, spell_checkbox)
            self._positions[position] = card
            self._cards.append(card)

        return self._cards

    # TODO: how does this work with _cards being static?
    # async def get_cards_with(
    #     self, *, name: str = None, enchanted: bool = None, template_id: int = None
    # ):
    #     # filter cards
    #     pass

    # TODO
    # async def get_members_with(self):
    #     # filter members
    #     pass

    # TODO
    async def round_number(self) -> int:
        pass

    # TODO: maybe keep this?
    async def do_combat(self, battle_callback: Callable):
        while await self.in_combat():
            await battle_callback(await self.round_number(), self)
            await self.wait_until_next_round()

    # TODO
    async def wait_until_next_round(self):
        # TODO: replace this doc
        """
        while handler.in_battle():
            # to battle stuff
            await handler.wait_until_next_round()
        """
        pass

    # TODO
    # can't be named pass
    async def pass_button(self):
        pass

    # _button suffix for consistency
    async def draw_button(self):
        pass

    # see draw_button
    async def flee_button(self):
        pass
