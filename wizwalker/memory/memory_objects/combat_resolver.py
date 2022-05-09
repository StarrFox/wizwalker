from typing import Optional

from wizwalker.memory.memory_object import PropertyClass
from .spell_effect import SpellEffect


class CombatResolver(PropertyClass):
    async def bool_global_effect(self) -> bool:
        return await self.read_value_from_offset(112, "bool")

    async def write_bool_global_effect(self, bool_global_effect: bool):
        await self.write_value_to_offset(112, bool_global_effect, "bool")

    async def global_effect(self) -> Optional[SpellEffect]:
        addr = await self.read_value_from_offset(120, "long long")

        if addr == 0:
            return None

        return SpellEffect(self.memory_reader, addr)

    async def battlefield_effects(self) -> list[SpellEffect]:
        effects = []
        for addr in await self.read_shared_vector(136):
            effects.append(SpellEffect(self.memory_reader, addr))

        return effects
