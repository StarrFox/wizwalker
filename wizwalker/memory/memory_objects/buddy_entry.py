from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import PlayerStatus


class BuddyEntry(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError

    # note: not defined
    async def gender(self) -> bool:
        """
        Gender of this buddy
        True if female False if male
        """
        name_tuple = await self.name_tuple()
        return name_tuple[0] == 128

    # note: actual .name is name_tuple
    async def name(self) -> str:
        """
        Name of this buddy
        """
        cache_handler = self.hook_handler.client.cache_handler
        langcode_prefix = "CharacterNames_"

        gender, first, middle, last = await self.name_tuple()

        if gender == 128:
            first_mid = "First_Girl_"

        else:
            first_mid = "First_Boy_"

        first_name = await cache_handler.get_langcode_name(
            langcode_prefix + first_mid + str(first)
        )

        if middle != 0:
            # they have a typo in the lang file for character names
            # so we need to account for it here
            if middle < 49:
                middle_name = await cache_handler.get_langcode_name(
                    langcode_prefix + "Middle_" + str(middle - 1)
                )
            else:
                middle_name = await cache_handler.get_langcode_name(
                    langcode_prefix + "Middle_" + str(middle)
                )
        else:
            # 0 is (empty) name
            middle_name = ""

        if last != 0:
            last_name = await cache_handler.get_langcode_name(
                langcode_prefix + "Last_" + str(last - 1)
            )
        else:
            # 0 is (empty) name
            last_name = ""

        return f"{first_name} {middle_name}{last_name}"

    # note: this is actually .name defined
    async def name_tuple(self) -> tuple:
        """
        Name tuple of this buddy
        (gender, first, middle, last)
        gender of 128 means Female while 130 is Male
        """
        # 128 -> Female
        # 130 -> Male
        #
        # for middle: - 1 if below 49 and no change if above or equal
        return await self.read_vector(72, 4, "unsigned char")

    async def character_id(self) -> int:
        """
        Character id of this buddy
        """
        return await self.read_value_from_offset(104, "unsigned long long")

    async def game_object_id(self) -> int:
        """
        Game Object id of this buddy
        """
        return await self.read_value_from_offset(120, "unsigned long long")

    async def status(self) -> PlayerStatus:
        """
        Status of this buddy
        """
        return await self.read_enum(112, PlayerStatus)
