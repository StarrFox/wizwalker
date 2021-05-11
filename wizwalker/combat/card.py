import asyncio
from typing import Union

import wizwalker


class CombatCard:
    """
    Represents a spell card
    """

    def __init__(
        self, combat_handler, spell_window: "wizwalker.memory.window.DynamicWindow",
    ):
        self.combat_handler = combat_handler

        self._spell_window = spell_window

    # TODO: add checks before casting
    async def cast(
        self, target: Union["CombatCard", "wizwalker.combat.CombatMember", None]
    ):
        """
        Cast this Card on another Card; a Member or with no target

        Args:
            target: Card, Member, or None if there is no target
        """
        if isinstance(target, CombatCard):
            cards_len_before = len(await self.combat_handler.get_cards())

            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )
            await self.combat_handler.client.mouse_handler.click_window(
                target._spell_window
            )

            # wait until card number goes down
            while len(await self.combat_handler.get_cards()) > cards_len_before:
                await asyncio.sleep(0.1)

            # wiz can't keep up with how fast we can cast
            await asyncio.sleep(1)

        elif target is None:
            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )

        else:
            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )
            await self.combat_handler.client.mouse_handler.click_window(
                await target.get_health_text_window()
            )

    async def discard(self):
        """
        Discard this Card
        """
        cards_len_before = len(await self.combat_handler.get_cards())
        await self.combat_handler.client.mouse_handler.click_window(
            self._spell_window, right_click=True
        )

        # wait until card number goes down
        while len(await self.combat_handler.get_cards()) > cards_len_before:
            await asyncio.sleep(0.1)

        # wiz can't keep up with how fast we can cast
        await asyncio.sleep(1)

    async def get_graphical_spell(
        self,
    ) -> "wizwalker.memory.spell.DynamicGraphicalSpell":
        """
        The GraphicalSpell with information about this card
        """
        return await self._spell_window.maybe_graphical_spell()

    async def name(self) -> str:
        """
        The name of this card
        """
        graphical_spell = await self.get_graphical_spell()
        spell_template = await graphical_spell.spell_template()
        # name is the actual name; display name is some wack stuff
        return await spell_template.name()

    async def template_id(self) -> int:
        """
        This card's template id
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.template_id()

    async def spell_id(self) -> int:
        """
        This card's spell id
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.spell_id()

    async def accuracy(self) -> int:
        """
        Current accuracy of this card
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.accuracy()

    async def is_castable(self) -> bool:
        """
        If this card can be casted
        """
        spell_window = self._spell_window
        return not spell_window.maybe_spell_grayed()

    async def is_enchanted(self) -> bool:
        """
        If this card is enchanted or not
        """
        grapical_spell = await self.get_graphical_spell()
        return await grapical_spell.enchantment() != 0

    async def is_treasure_card(self) -> bool:
        """
        If this card is a treasure card
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.treasure_card()

    async def is_item_card(self) -> bool:
        """
        If this card is an item card
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.item_card()

    async def is_side_board(self) -> bool:
        """
        If this card is from the side deck
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.side_board()

    async def is_cloaked(self) -> bool:
        """
        If this card is cloaked
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.cloaked()

    async def is_enchanted_from_item_card(self) -> bool:
        """
        If this card was enchanted from an item card
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.enchantment_spell_is_item_card()

    async def is_pve_only(self) -> bool:
        """
        If this card can only be used in pve
        """
        graphical_spell = await self.get_graphical_spell()
        return await graphical_spell.pve()
