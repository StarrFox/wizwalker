import asyncio
import functools
import struct
from typing import Any

import pymem

from wizwalker import type_format_dict


class MemoryReader:
    """
    Represents anything that needs to read from memory
    """

    def __init__(self, process: pymem.Pymem):
        self.process = process

    @staticmethod
    async def run_in_executor(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        function = functools.partial(func, *args, **kwargs)

        return await loop.run_in_executor(None, function)

    @staticmethod
    def _scan_all_from(start_address: int, handle: int, pattern: bytes):
        next_region = start_address
        found = None

        while next_region < 0x7FFFFFFF0000:
            next_region, found = pymem.pattern.scan_pattern_page(
                handle, next_region, pattern
            )
            if found:
                break

        return found

    async def pattern_scan(self, pattern: bytes, *, module: str = None):
        if module:
            module = pymem.process.module_from_name(self.process.process_handle, module)
            jump_address = await self.run_in_executor(
                pymem.pattern.pattern_scan_module,
                self.process.process_handle,
                module,
                pattern,
            )

        else:
            jump_address = await self.run_in_executor(
                self._scan_all_from,
                self.process.process_base.lpBaseOfDll,
                self.process.process_handle,
                pattern,
            )

        return jump_address

    async def read_bytes(self, address: int, size: int) -> bytes:
        return await self.run_in_executor(self.process.read_bytes, address, size)

    async def write_bytes(self, address: int, _bytes: bytes):
        await self.run_in_executor(
            self.process.write_bytes, address, _bytes, len(_bytes),
        )

    async def read_typed(self, address: int, data_type: str) -> Any:
        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} is not a valid data type")

        data = await self.read_bytes(address, struct.calcsize(type_format))
        return struct.unpack(type_format, data)[0]

    async def write_typed(self, address: int, value: Any, data_type: str):
        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} is not a valid data type")

        packed_data = struct.pack(type_format, value)
        await self.write_bytes(address, packed_data)
