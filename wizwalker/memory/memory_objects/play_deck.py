from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject


class PlayDeck(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def deck_to_save(self) -> list["DynamicPlaySpellData"]:
        spell_data = []
        for addr in self.read_shared_vector(72):
            spell_data.append(DynamicPlaySpellData(self.hook_handler, addr))

        return spell_data

    def graveyard_to_save(self) -> list["DynamicPlaySpellData"]:
        spell_data = []
        for addr in self.read_shared_vector(96):
            spell_data.append(DynamicPlaySpellData(self.hook_handler, addr))

        return spell_data


class DynamicPlayDeck(DynamicMemoryObject, PlayDeck):
    pass


class PlaySpellData(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def template_id(self) -> int:
        return self.read_value_from_offset(72, "unsigned int")

    def enchantment(self) -> int:
        return self.read_value_from_offset(76, "unsigned int")


class DynamicPlaySpellData(DynamicMemoryObject, PlaySpellData):
    pass
