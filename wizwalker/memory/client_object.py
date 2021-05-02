from .game_stats import DynamicGameStats
from .memory_object import PropertyClass
from wizwalker import XYZ


class ClientObject(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # async def inactive_behaviors(self) -> class SharedPointer<class BehaviorInstance>:
    #     return await self.read_value_from_offset(224, "class SharedPointer<class BehaviorInstance>")
    #
    # async def write_inactive_behaviors(self, inactive_behaviors: class SharedPointer<class BehaviorInstance>):
    #     await self.write_value_to_offset(224, inactive_behaviors, "class SharedPointer<class BehaviorInstance>")

    async def global_id_full(self) -> int:
        return await self.read_value_from_offset(72, "unsigned long long")

    async def write_global_id_full(self, global_id_full: int):
        await self.write_value_to_offset(72, global_id_full, "unsigned long long")

    async def perm_id(self) -> int:
        return await self.read_value_from_offset(80, "unsigned long long")

    async def write_perm_id(self, perm_id: int):
        await self.write_value_to_offset(80, perm_id, "unsigned __int64")

    async def location(self) -> XYZ:
        return await self.read_xyz(168)

    async def write_location(self, location: XYZ):
        await self.write_xyz(168, location)

    async def orientation(self) -> tuple:
        return await self.read_vector(180)

    async def write_orientation(self, orientation: tuple):
        await self.write_vector(180, orientation)

    async def scale(self) -> float:
        return await self.read_value_from_offset(196, "float")

    async def write_scale(self, scale: float):
        await self.write_value_to_offset(196, scale, "float")

    async def template_id_full(self) -> int:
        return await self.read_value_from_offset(96, "unsigned long long")

    async def write_template_id_full(self, template_id_full: int):
        await self.write_value_to_offset(96, template_id_full, "unsigned long long")

    # async def debug_name(self) -> std::string:
    #     return await self.read_value_from_offset(104, "std::string")
    #
    # async def write_debug_name(self, debug_name: std::string):
    #     await self.write_value_to_offset(104, debug_name, "std::string")

    # async def display_key(self) -> std::string:
    #     return await self.read_value_from_offset(136, "std::string")
    #
    # async def write_display_key(self, display_key: std::string):
    #     await self.write_value_to_offset(136, display_key, "std::string")

    async def zone_tag_id(self) -> int:
        return await self.read_value_from_offset(344, "unsigned int")

    async def write_zone_tag_id(self, zone_tag_id: int):
        await self.write_value_to_offset(344, zone_tag_id, "unsigned int")

    async def speed_multiplier(self) -> int:
        return await self.read_value_from_offset(192, "short")

    async def write_speed_multiplier(self, speed_multiplier: int):
        await self.write_value_to_offset(192, speed_multiplier, "short")

    async def mobile_id(self) -> int:
        return await self.read_value_from_offset(194, "unsigned short")

    async def write_mobile_id(self, mobile_id: int):
        await self.write_value_to_offset(194, mobile_id, "unsigned short")

    async def character_id(self) -> int:
        return await self.read_value_from_offset(440, "unsigned long long")

    async def write_character_id(self, character_id: int):
        await self.write_value_to_offset(440, character_id, "unsigned long long")

    async def game_stats(self) -> DynamicGameStats:
        addr = await self.read_value_from_offset(544, "long long")
        return DynamicGameStats(self.hook_handler, addr)

    # async def write_game_stats(self, game_stats: class WizGameStats*):
    #     await self.write_value_to_offset(544, game_stats, "class WizGameStats*")


class CurrentClientObject(ClientObject):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_client_base()
