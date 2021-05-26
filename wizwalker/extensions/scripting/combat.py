from wizwalker.combat import CombatHandler


class ScriptableCombatHandler(CombatHandler):
    async def handle_round(self):
        raise NotImplementedError()
