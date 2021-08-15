from typing import List

from wizwalker.memory.memory_object import PropertyClass


class PlayDeck(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def deck_to_save(self) -> List["AddressedPlaySpellData"]:
        spell_data = []
        for addr in await self.read_shared_vector(72):
            spell_data.append(AddressedPlaySpellData(self.hook_handler, addr))

        return spell_data

    async def graveyard_to_save(self) -> List["AddressedPlaySpellData"]:
        spell_data = []
        for addr in await self.read_shared_vector(96):
            spell_data.append(AddressedPlaySpellData(self.hook_handler, addr))

        return spell_data


class AddressedPlayDeck(PlayDeck):
    pass


class PlaySpellData(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def template_id(self) -> int:
        return await self.read_value_from_offset(72, "unsigned int")

    async def enchantment(self) -> int:
        return await self.read_value_from_offset(76, "unsigned int")


class AddressedPlaySpellData(PlaySpellData):
    pass
