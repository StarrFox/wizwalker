import time
from typing import Optional, Union

import wizwalker


# TODO: add way to cast divide spells (remember to click the confirm button after targeting)
#  cast_divide?
class CombatCard:
    """
    Represents a spell card
    """

    def __init__(
        self,
        combat_handler,
        spell_window: "wizwalker.memory.window.DynamicWindow",
    ):
        self.combat_handler = combat_handler

        self._spell_window = spell_window

    # TODO: add checks before casting
    def cast(
        self,
        target: Optional[Union["CombatCard", "wizwalker.combat.CombatMember"]],
        *,
        sleep_time: Optional[float] = 1.0,
        debug_paint: bool = False,
    ):
        """
        Cast this Card on another Card; a Member or with no target

        Args:
            target: Card, Member, or None if there is no target
            sleep_time: How long to sleep after enchants and between multicasts or None for no sleep
            debug_paint: If the card should be highlighted before clicking
        """
        if isinstance(target, CombatCard):
            cards_len_before = len(self.combat_handler.get_cards())

            self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )

            time.sleep(sleep_time)

            self.combat_handler.client.mouse_handler.set_mouse_position_to_window(
                target._spell_window
            )

            time.sleep(sleep_time)

            if debug_paint:
                target._spell_window.debug_paint()

            self.combat_handler.client.mouse_handler.click_window(
                target._spell_window
            )

            # wait until card number goes down
            while len(self.combat_handler.get_cards()) > cards_len_before:
                time.sleep(0.1)

            # wiz can't keep up with how fast we can cast
            if sleep_time is not None:
                time.sleep(sleep_time)

        elif target is None:
            self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )
            # we don't need to sleep because nothing will be casted after

        else:
            self.combat_handler.client.mouse_handler.click_window(
                self._spell_window
            )

            # see above
            if sleep_time is not None:
                time.sleep(sleep_time)

            self.combat_handler.client.mouse_handler.click_window(
                target.get_health_text_window()
            )

    def discard(self, *, sleep_time: Optional[float] = 1.0):
        """
        Discard this Card

        Args:
            sleep_time: Time to sleep after discard or None to not
        """
        cards_len_before = len(self.combat_handler.get_cards())
        self.combat_handler.client.mouse_handler.click_window(
            self._spell_window, right_click=True
        )

        # wait until card number goes down
        while len(self.combat_handler.get_cards()) > cards_len_before:
            time.sleep(0.1)

        if sleep_time is not None:
            time.sleep(sleep_time)

    def graphical_spell(
        self,
    ) -> "wizwalker.memory.memory_objects.spell.DynamicGraphicalSpell":
        """
        The GraphicalSpell with information about this card
        """
        res = self._spell_window.maybe_graphical_spell()
        if res is None:
            raise ValueError("Graphical spell not found; probably reading too fast")

        return res

    def wait_for_graphical_spell(
        self,
    ) -> "wizwalker.memory.memory_objects.spell.DynamicGraphicalSpell":
        """
        Wait for GraphicalSpell
        """
        return wizwalker.utils.wait_for_non_error(self.graphical_spell)

    def spell_effects(
        self,
    ) -> list["wizwalker.memory.memory_objects.spell_effect.DynamicSpellEffect"]:
        spell = self.wait_for_graphical_spell()
        return spell.spell_effects()

    def name(self) -> str:
        """
        The name of this card
        """
        graphical_spell = self.wait_for_graphical_spell()
        spell_template = graphical_spell.spell_template()
        return spell_template.name()

    def display_name_code(self) -> str:
        """
        The display name code of this card
        """
        graphical_spell = self.wait_for_graphical_spell()
        spell_template = graphical_spell.spell_template()
        return spell_template.display_name()

    def display_name(self) -> str:
        """
        the display name of this card
        """
        code = self.display_name_code()
        return self.combat_handler.client.cache_handler.get_langcode_name(code)

    def type_name(self) -> str:
        """
        The type name of this card
        """
        graphical_spell = self.wait_for_graphical_spell()
        spell_template = graphical_spell.spell_template()
        return spell_template.type_name()

    def template_id(self) -> int:
        """
        This card's template id
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.template_id()

    def spell_id(self) -> int:
        """
        This card's spell id
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.spell_id()

    def accuracy(self) -> int:
        """
        Current accuracy of this card
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.accuracy()

    def is_castable(self) -> bool:
        """
        If this card can be casted
        """
        spell_window = self._spell_window
        return not spell_window.maybe_spell_grayed()

    def is_enchanted(self) -> bool:
        """
        If this card is enchanted or not
        """
        grapical_spell = self.wait_for_graphical_spell()
        return grapical_spell.enchantment() != 0

    def is_treasure_card(self) -> bool:
        """
        If this card is a treasure card
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.treasure_card()

    def is_item_card(self) -> bool:
        """
        If this card is an item card
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.item_card()

    def is_side_board(self) -> bool:
        """
        If this card is from the side deck
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.side_board()

    def is_cloaked(self) -> bool:
        """
        If this card is cloaked
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.cloaked()

    def is_enchanted_from_item_card(self) -> bool:
        """
        If this card was enchanted from an item card
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.enchantment_spell_is_item_card()

    def is_pve_only(self) -> bool:
        """
        If this card can only be used in pve
        """
        graphical_spell = self.wait_for_graphical_spell()
        return graphical_spell.pve()
