from typing import Optional

from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject
from .spell_effect import DynamicSpellEffect


class CombatResolver(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def bool_global_effect(self) -> bool:
        return self.read_value_from_offset(112, "bool")

    def write_bool_global_effect(self, bool_global_effect: bool):
        self.write_value_to_offset(112, bool_global_effect, "bool")

    def global_effect(self) -> Optional[DynamicSpellEffect]:
        addr = self.read_value_from_offset(120, "long long")

        if addr == 0:
            return None

        return DynamicSpellEffect(self.hook_handler, addr)

    def battlefield_effects(self) -> list[DynamicSpellEffect]:
        effects = []
        for addr in self.read_shared_vector(136):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects


class DynamicCombatResolver(DynamicMemoryObject, CombatResolver):
    pass
