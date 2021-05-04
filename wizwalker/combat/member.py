import wizwalker


class CombatMember:
    def __init__(
        self,
        combat_handler: "wizwalker.combat.CombatHandler",
        participant: "wizwalker.memory.combat_participant.DynamicCombatParticipant",
    ):
        self.combat_handler = combat_handler

        self._participant = participant

    # TODO
    async def name(self) -> str:
        pass
