from wizwalker.combat import CombatHandler


class ScriptableCombatHandler(CombatHandler):
    async def handle_round(self):
        pass

    async def get_card_with(self, card_type: str, *, param: int):
        async def _pred(card):
            spell = await card.wait_for_graphical_spell()
            template = await spell.spell_template()

            effects = await template.effects()
