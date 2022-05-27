from typing import Optional, Union

from wizwalker import XYZ
from wizwalker.memory.memory_object import MemoryObject, DynamicMemoryObject

from .client_object import DynamicClientObject, ClientObject


class CameraController(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    # TODO: camera 0x88 offset

    async def position(self) -> XYZ:
        return await self.read_xyz(108)

    async def write_position(self, position: XYZ):
        await self.write_xyz(108, position)

    async def pitch(self) -> float:
        return await self.read_value_from_offset(120, "float")

    async def write_pitch(self, pitch: float):
        await self.write_value_to_offset(120, pitch, "float")

    async def roll(self) -> float:
        return await self.read_value_from_offset(124, "float")

    async def write_roll(self, roll: float):
        await self.write_value_to_offset(124, roll, "float")

    async def yaw(self) -> float:
        return await self.read_value_from_offset(128, "float")

    async def write_yaw(self, yaw: float):
        await self.write_value_to_offset(128, yaw, "float")


class FreeCameraController(CameraController):
    async def read_base_address(self) -> int:
        raise NotImplementedError()


class ElasticCameraController(CameraController):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def attached_client_object(self) -> Optional[DynamicClientObject]:
        addr = await self.read_value_from_offset(264, "unsigned long long")

        if addr == 0:
            return None

        return DynamicClientObject(self.hook_handler, addr)

    async def write_attached_client_object(self, attached_client_object: Union[ClientObject, int]):
        if isinstance(attached_client_object, ClientObject):
            attached_client_object = await attached_client_object.read_base_address()

        await self.write_value_to_offset(264, attached_client_object, "unsigned long long")

    async def check_collisions(self) -> bool:
        return await self.read_value_from_offset(608, "bool")

    async def write_check_collisions(self, check_collisions: bool):
        await self.write_value_to_offset(608, check_collisions, "bool")

    async def distance(self) -> float:
        return await self.read_value_from_offset(300, "float")

    async def write_distance(self, distance: float):
        await self.write_value_to_offset(300, distance, "float")

    async def distance_target(self) -> float:
        return await self.read_value_from_offset(304, "float")

    async def write_distance_target(self, distance_target: float):
        await self.write_value_to_offset(304, distance_target, "float")

    async def zoom_resolution(self) -> float:
        return await self.read_value_from_offset(324, "float")

    async def write_zoom_resolution(self, zoom_resolution: float):
        await self.write_value_to_offset(324, zoom_resolution, "float")

    async def max_distance(self) -> float:
        return await self.read_value_from_offset(328, "float")

    async def write_max_distance(self, max_distance: float):
        await self.write_value_to_offset(328, max_distance, "float")

    async def min_distance(self) -> float:
        return await self.read_value_from_offset(332, "float")

    async def write_min_distance(self, min_distance: float):
        await self.write_value_to_offset(332, min_distance, "float")


class DynamicCameraController(DynamicMemoryObject, CameraController):
    pass


class DynamicFreeCameraController(DynamicMemoryObject, FreeCameraController):
    pass


class DynamicElasticCameraController(DynamicMemoryObject, ElasticCameraController):
    pass
