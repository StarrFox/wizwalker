from typing import List, Optional

from wizwalker import XYZ
from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject
from .game_stats import DynamicGameStats
from .game_object_template import DynamicWizGameObjectTemplate
from .behavior_instance import DynamicBehaviorInstance


class ClientObject(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def inactive_behaviors(self) -> List[DynamicBehaviorInstance]:
        behaviors = []
        for addr in await self.read_shared_vector(224):
            if addr != 0:
                behaviors.append(DynamicBehaviorInstance(self.hook_handler, addr))

        return behaviors

    # convenience method
    async def object_name(self) -> Optional[str]:
        object_template = await self.object_template()
        if object_template is not None:
            return await object_template.object_name()

        return None

    # note: not defined
    async def parent(self) -> Optional["DynamicClientObject"]:
        addr = await self.read_value_from_offset(208, "long long")

        if addr == 0:
            return None

        return DynamicClientObject(self.hook_handler, addr)

    # note: not defined
    async def children(self) -> List["DynamicClientObject"]:
        children = []
        for addr in await self.read_shared_vector(384):
            children.append(DynamicClientObject(self.hook_handler, addr))

        return children

    # note: not defined
    async def client_zone(self) -> Optional["DynamicClientZone"]:
        addr = await self.read_value_from_offset(304, "long long")

        if addr == 0:
            return None

        return DynamicClientZone(self.hook_handler, addr)

    # note: not defined
    async def object_template(self) -> Optional[DynamicWizGameObjectTemplate]:
        addr = await self.read_value_from_offset(88, "long long")

        if addr == 0:
            return None

        return DynamicWizGameObjectTemplate(self.hook_handler, addr)

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

    async def debug_name(self) -> str:
        return await self.read_string_from_offset(104)

    async def write_debug_name(self, debug_name: str):
        await self.write_value_to_offset(104, debug_name)

    async def display_key(self) -> str:
        return await self.read_string_from_offset(136)

    async def write_display_key(self, display_key: str):
        await self.write_string_to_offset(136, display_key)

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


class CurrentClientObject(ClientObject):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_client_base()


class DynamicClientObject(DynamicMemoryObject, ClientObject):
    pass


class ClientZone(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def zone_id(self) -> int:
        return await self.read_value_from_offset(72, "long long")

    async def write_zone_id(self, zone_id: int):
        await self.write_value_to_offset(72, zone_id, "long long")

    async def zone_name(self) -> str:
        return await self.read_string_from_offset(88)

    async def write_zone_name(self, zone_name: str):
        await self.write_string_to_offset(88, zone_name)


class DynamicClientZone(DynamicClientObject, ClientZone):
    pass
