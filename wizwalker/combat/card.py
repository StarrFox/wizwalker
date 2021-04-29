from wizwalker.memory import Spell


class Card:
    """
    Represents a spell card
    """

    def __init__(self, name: str, position: int, spell: Spell):
        self.name = name
        self.position = position
        self._spell = spell

    async def spell_id(self) -> int:
        """
        This card's spell id
        """
        return await self._spell.spell_id()

    # TODO: test with accuracy enchants
    async def accuracy(self) -> int:
        """
        Current accuracy of this card
        """
        return await self._spell.accuracy()

    async def is_treasure_card(self) -> bool:
        """
        If this card is a treasure card
        """
        return await self._spell.treasure_card()

    async def is_item_card(self) -> bool:
        """
        If this card is an item card
        """
        return await self._spell.item_card()

    async def is_side_board(self) -> bool:
        """
        If this card is from the side deck
        """
        return await self._spell.side_board()

    async def is_cloaked(self) -> bool:
        """
        If this card is cloaked
        """
        return await self._spell.cloaked()

    async def is_enchanted_from_item_card(self) -> bool:
        """
        If this card was enchanted from an item card
        """
        return await self._spell.enchantment_spell_is_item_card()

    async def is_pve_only(self) -> bool:
        """
        If this card can only be used in pve
        """
        return await self._spell.pve()
