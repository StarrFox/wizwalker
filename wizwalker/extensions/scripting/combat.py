from wizwalker.combat import CombatHandler


class ScriptableCombatHandler(CombatHandler):
    async def handle_round(self):
        raise NotImplementedError()

    async def get_damaging_aoes(self, *, check_enchanted: bool = True):
        """
        Get a list of all damaging aoes in hand
        """

        async def _pred(card):
            if check_enchanted:
                if not await card.is_enchanted():
                    return False

            if await card.type_name() != "AOE":
                return False

            effects = await card.get_spell_effects()

            for effect in effects:
                effect_type = await effect.maybe_read_type_name()
                if "random" in effect_type.lower():
                    pass

        return await self.get_cards_with_predicate(_pred)

    # async def get_card_with(self, card_type: str, *, param: int):
    #     async def _pred(card):
    #         spell = await card.wait_for_graphical_spell()
    #         template = await spell.spell_template()
    #
    #         effects = await template.effects()
