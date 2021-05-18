import asyncio
from typing import List, Optional, Union

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
        self,
        target: Union["CombatCard", "wizwalker.combat.CombatMember", None],
        *,
        sleep_time: Optional[float] = 1.0
    ):
        """
        Cast this Card on another Card; a Member or with no target

        Args:
            target: Card, Member, or None if there is no target
            sleep_time: how long to sleep after enchants and between multicasts or None for no sleep
        """
        if isinstance(target, CombatCard):
            cards_len_before = len(await self.combat_handler.get_cards())

            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )

            await asyncio.sleep(sleep_time)

            await self.combat_handler.client.mouse_handler.set_mouse_position_to_window(
                target._spell_window
            )

            await asyncio.sleep(sleep_time)

            await self.combat_handler.client.mouse_handler.click_window(
                target._spell_window
            )

            # wait until card number goes down
            while len(await self.combat_handler.get_cards()) > cards_len_before:
                await asyncio.sleep(0.1)

            # wiz can't keep up with how fast we can cast
            if sleep_time is not None:
                await asyncio.sleep(sleep_time)

        elif target is None:
            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )
            # we don't need to sleep because nothing will be casted after

        else:
            await self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )

            # see above
            if sleep_time is not None:
                await asyncio.sleep(sleep_time)

            await self.combat_handler.client.mouse_handler.click_window(
                await target.get_health_text_window()
            )

    async def discard(self, *, sleep_time: Optional[float] = 1.0):
        """
        Discard this Card

        Args:
            sleep_time: Time to sleep after discard or None to not
        """
        cards_len_before = len(await self.combat_handler.get_cards())
        await self.combat_handler.client.mouse_handler.click_window(
            self._spell_window, right_click=True
        )

        # wait until card number goes down
        while len(await self.combat_handler.get_cards()) > cards_len_before:
            await asyncio.sleep(0.1)

        if sleep_time is not None:
            await asyncio.sleep(sleep_time)

    async def get_graphical_spell(
        self,
    ) -> "wizwalker.memory.memory_objects.spell.DynamicGraphicalSpell":
        """
        The GraphicalSpell with information about this card
        """
        res = await self._spell_window.maybe_graphical_spell()
        if res is None:
            raise ValueError("Graphical spell not found; probably reading too fast")

        return res

    async def wait_for_graphical_spell(self):
        """
        Wait for GraphicalSpell
        """
        return await wizwalker.utils.wait_for_non_error(self.get_graphical_spell)

    async def get_spell_effects(
        self,
    ) -> List["wizwalker.memory.memory_objects.spell_effect.DynamicSpellEffect"]:
        spell = await self.wait_for_graphical_spell()
        return await spell.spell_effects()

    async def name(self) -> str:
        """
        The name of this card
        """
        graphical_spell = await self.wait_for_graphical_spell()
        spell_template = await graphical_spell.spell_template()
        # name is the actual name; display name is local lang code
        return await spell_template.name()

    async def template_id(self) -> int:
        """
        This card's template id
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.template_id()

    async def spell_id(self) -> int:
        """
        This card's spell id
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.spell_id()

    async def accuracy(self) -> int:
        """
        Current accuracy of this card
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.accuracy()

    async def is_castable(self) -> bool:
        """
        If this card can be casted
        """
        spell_window = self._spell_window
        return not await spell_window.maybe_spell_grayed()

    async def is_enchanted(self) -> bool:
        """
        If this card is enchanted or not
        """
        grapical_spell = await self.wait_for_graphical_spell()
        return await grapical_spell.enchantment() != 0

    async def is_treasure_card(self) -> bool:
        """
        If this card is a treasure card
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.treasure_card()

    async def is_item_card(self) -> bool:
        """
        If this card is an item card
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.item_card()

    async def is_side_board(self) -> bool:
        """
        If this card is from the side deck
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.side_board()

    async def is_cloaked(self) -> bool:
        """
        If this card is cloaked
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.cloaked()

    async def is_enchanted_from_item_card(self) -> bool:
        """
        If this card was enchanted from an item card
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.enchantment_spell_is_item_card()

    async def is_pve_only(self) -> bool:
        """
        If this card can only be used in pve
        """
        graphical_spell = await self.wait_for_graphical_spell()
        return await graphical_spell.pve()
