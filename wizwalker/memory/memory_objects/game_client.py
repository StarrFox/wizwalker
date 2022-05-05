from typing import Union, Optional

from wizwalker.memory.memory_object import MemoryObject
from .camera_controller import (
    DynamicCameraController,
    CameraController,
    DynamicFreeCameraController,
    DynamicElasticCameraController,
)


# note: not defined
class GameClient(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def elastic_camera_controller(self) -> Optional[DynamicElasticCameraController]:
        offset = await self.pattern_scan_offset_cached(
            rb"\x48\x8B\x93\xD8\x1F\x02\x00\x41\xFF\xD1\x32"
            rb"\xC0\xEB\x05\x41\xFF\xD1\xB0\x01\x88\x83\x20"
            rb"\x20\x02\x00\x48\x8B\x07\x33\xD2\x48\x8B\xCF",
            3,
            "elastic_camera_controller",
            0x21fd8
        )

        addr = await self.read_value_from_offset(offset, "unsigned long long")

        if addr == 0:
            return None

        return DynamicElasticCameraController(self.hook_handler, addr)

    async def free_camera_controller(self) -> Optional[DynamicFreeCameraController]:
        offset = await self.pattern_scan_offset_cached(
            rb"\x48\x8B\x93\xE8\x1F\x02\x00\x48\x8B\x03\x4C"
            rb"\x8B\x88\x40\x04\x00\x00\x41\xB8\x01\x00\x00"
            rb"\x00\x48\x8B\xCB\x48\x3B\xFA\x75\x0E\x48\x8B"
            rb"\x93\xD8\x1F\x02",
            3,
            "free_camera_controller",
            0x21fe8
        )

        addr = await self.read_value_from_offset(offset, "unsigned long long")

        if addr == 0:
            return None

        return DynamicFreeCameraController(self.hook_handler, addr)

    async def selected_camera_controller(self) -> Optional[DynamicCameraController]:
        offset = await self.pattern_scan_offset_cached(
            rb"\x48\x89\x87\x08\x20\x02\x00\x48\x8D\x8F"
            rb"\x10\x20\x02\x00\x48\x8D\x54\x24\x40\xE8"
            rb"....\x90\x48\x8B\x4C\x24",
            3,
            "selected_camera_controller",
            0x22008
        )

        addr = await self.read_value_from_offset(offset, "unsigned long long")

        if addr == 0:
            return None

        return DynamicCameraController(self.hook_handler, addr)

    async def write_selected_camera_controller(self, selected_camera_controller: Union[CameraController, int]):
        if isinstance(selected_camera_controller, CameraController):
            selected_camera_controller = await selected_camera_controller.read_base_address()

        offset = await self.pattern_scan_offset_cached(
            rb"\x48\x89\x87\x08\x20\x02\x00\x48\x8D\x8F"
            rb"\x10\x20\x02\x00\x48\x8D\x54\x24\x40\xE8"
            rb"....\x90\x48\x8B\x4C\x24",
            3,
            "selected_camera_controller",
            0x22008
        )

        await self.write_value_to_offset(offset, selected_camera_controller, "unsigned long long")

    async def is_freecam(self) -> bool:
        offset = await self.pattern_scan_offset_cached(
            rb"\x0F\xB6\x88\x20\x20\x02\x00\x88\x8B\x6A"
            rb"\x02\x00\x00\x84\xC9\x0F\x85....\x48\x8D"
            rb"\x55\xE0\x48\x8B\xCB\xE8",
            3,
            "is_freecam",
            0x22020
        )
        return await self.read_value_from_offset(offset, "bool")

    async def write_is_freecam(self, is_freecam: bool):
        offset = await self.pattern_scan_offset_cached(
            rb"\x0F\xB6\x88\x20\x20\x02\x00\x88\x8B\x6A"
            rb"\x02\x00\x00\x84\xC9\x0F\x85....\x48\x8D"
            rb"\x55\xE0\x48\x8B\xCB\xE8",
            3,
            "is_freecam",
            0x22020
        )
        await self.write_value_to_offset(offset, is_freecam, "bool")


class CurrentGameClient(GameClient):
    _base_address = None

    async def read_base_address(self) -> int:
        if self._base_address is not None:
            return self._base_address

        addr = await self.pattern_scan(rb"\x48\x8B.....\x48\x8B\xD9\x80\xB8\x45")
        offset = await self.read_typed(addr + 3, "int")

        self._base_address = await self.read_typed(addr + 7 + offset, "unsigned long long")
        return self._base_address
