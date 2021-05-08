import wizwalker


class CombatMember:
    def __init__(
        self,
        combat_handler: "wizwalker.combat.CombatHandler",
        combatant_control: "wizwalker.memory.DynamicWindow",
    ):
        self.combat_handler = combat_handler

        self._combatant_control = combatant_control

    async def get_particpant(self):
        return await self._combatant_control.maybe_combat_participant()

    async def get_stats(self):
        part = await self.get_particpant()
        return await part.game_stats()

    async def is_client(self) -> bool:
        """
        If this member is the local client
        """
        owner_id = await self.owner_id()
        character_id = await self.combat_handler.client.client_object.character_id()
        return owner_id + 2 == character_id

    async def is_player(self) -> bool:
        """
        If this member is a player
        """
        part = await self.get_particpant()
        return await part.is_player()

    async def is_monster(self) -> bool:
        """
        If this member is a mob
        """
        part = await self.get_particpant()
        return bool(await part.is_monster())

    async def is_minion(self) -> bool:
        """
        If this member is a minion
        """
        part = await self.get_particpant()
        return await part.is_minion()

    async def is_boss(self) -> bool:
        """
        If this member is a boss
        """
        part = await self.get_particpant()
        return await part.boss_mob()

    async def owner_id(self) -> int:
        """
        This member's owner id
        """
        part = await self.get_particpant()
        return await part.owner_id_full()

    async def template_id(self) -> int:
        part = await self.get_particpant()
        return await part.template_id_full()

    async def normal_pips(self) -> int:
        part = await self.get_particpant()
        return await part.num_pips()

    async def power_pips(self) -> int:
        part = await self.get_particpant()
        return await part.num_power_pips()

    async def shadow_pips(self) -> int:
        part = await self.get_particpant()
        return await part.num_shadow_pips()

    # TODO: should this be called hitpoints
    async def health(self) -> int:
        stats = await self.get_stats()
        return await stats.current_hitpoints()

    async def max_health(self) -> int:
        stats = await self.get_stats()
        return await stats.max_hitpoints()

    async def mana(self) -> int:
        stats = await self.get_stats()
        return await stats.current_mana()

    async def max_mana(self) -> int:
        stats = await self.get_stats()
        return await stats.max_mana()

    async def level(self) -> int:
        stats = await self.get_stats()
        return await stats.reference_level()
