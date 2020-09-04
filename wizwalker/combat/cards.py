from typing import List, Union
from wizwalker import NotEnoughMana, NotEnoughPips, CardNotFound, CardAlreadyEnchanted


class Hand:
    def __init__(self, client: "wizwalker.Client"):
        self.client = client
        self._cards: List[Card] = []

    async def _update_card_data(self):
        pass
        # self._cards = new_data

    def _search_card(self, name):
        pass
        # raise CardNotFound(name)

    def _card_from_position(self, position):
        pass
        # raise CardNotFound(position)

    async def size(self) -> int:
        pass

    # TODO: generic with types str and int
    async def get_card(self, card_name_or_positon: Union[str, int]) -> "Card":
        """
        Get a card based on a name or position
        """
        if not isinstance(card_name_or_positon, (str, int)):
            raise ValueError(
                f"Card_name_or_position must be str or int not {card_name_or_positon.__class__!r}"
            )

        await self._update_card_data()

        if isinstance(card_name_or_positon, str):
            card = self._search_card(card_name_or_positon)

        else:
            card = self._card_from_position(card_name_or_positon)

        return Card()

    async def get_all_cards(self) -> list:
        await self._update_card_data()
        return self._cards


class Card:
    def __init__(self):
        self.position = None
        self.name = None
        self.pips = None
        self.shadow_pips = None
        self.is_enchanted = None

    async def enchant(self, card: "Card"):
        if card.is_enchanted:
            raise CardAlreadyEnchanted()

        # enchant code here
        card.is_enchanted = True
        raise NotImplementedError()

    async def target(self, combat_position: int):
        raise NotImplementedError()

    async def discard(self):
        raise NotImplementedError()
