import asyncio
import functools
import struct
import re
from typing import Any, Union

import pymem
import pymem.exception
import pymem.ressources.structure

from wizwalker import (
    PatternFailed,
    PatternMultipleResults,
    type_format_dict,
    utils,
    MemoryReadError,
    MemoryWriteError,
    ClientClosedError,
)


class MemoryReader:
    """
    Represents anything that needs to read from memory
    """

    def __init__(self, process: pymem.Pymem):
        self.process = process

    def is_running(self) -> bool:
        """
        Bool if the process we're reading/writing to/from is running
        """
        return utils.check_if_process_running(self.process.process_handle)

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

        # pattern scan expects a list
        if found is None:
            return []
        else:
            return [found]

    @staticmethod
    def _scan_page_return_all(handle, address, pattern):
        mbi = pymem.memory.virtual_query(handle, address)
        next_region = mbi.BaseAddress + mbi.RegionSize
        allowed_protections = [
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READ,
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READWRITE,
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_READWRITE,
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_READONLY,
        ]
        if (
            mbi.state != pymem.ressources.structure.MEMORY_STATE.MEM_COMMIT
            or mbi.protect not in allowed_protections
        ):
            return next_region, None

        page_bytes = pymem.memory.read_bytes(handle, address, mbi.RegionSize)

        found = []

        for match in re.finditer(pattern, page_bytes):
            found.append(address + match.span()[0])

        return next_region, found

    def _scan_entire_module(self, handle, module, pattern):
        base_address = module.lpBaseOfDll
        max_address = module.lpBaseOfDll + module.SizeOfImage
        page_address = base_address

        found = []
        while page_address < max_address:
            next_page, page_found = self._scan_page_return_all(
                handle, page_address, pattern
            )
            if page_found:
                found += page_found
            page_address = next_page

        return found

    async def pattern_scan(
        self, pattern: bytes, *, module: str = None, error_on_multiple: bool = True
    ) -> Union[list, int]:
        if module:
            module = pymem.process.module_from_name(self.process.process_handle, module)
            found_addresses = await self.run_in_executor(
                self._scan_entire_module, self.process.process_handle, module, pattern,
            )

        else:
            found_addresses = await self.run_in_executor(
                self._scan_all_from,
                self.process.process_base.lpBaseOfDll,
                self.process.process_handle,
                pattern,
            )

        if (found_length := len(found_addresses)) == 0:
            raise PatternFailed(pattern)
        elif found_length > 1 and error_on_multiple:
            raise PatternMultipleResults(f"Got {found_length} results for {pattern}")
        elif found_length > 1 and not error_on_multiple:
            return found_addresses
        else:
            return found_addresses[0]

    async def allocate(self, size: int) -> int:
        return await self.run_in_executor(self.process.allocate, size)

    async def free(self, address: int):
        await self.run_in_executor(self.process.free, address)

    async def read_bytes(self, address: int, size: int) -> bytes:
        try:
            return await self.run_in_executor(self.process.read_bytes, address, size)
        except pymem.exception.MemoryReadError:
            # we don't want to run is running for every read
            # so we just check after we error
            if not self.is_running():
                raise ClientClosedError()
            else:
                raise MemoryReadError(address)

    async def write_bytes(self, address: int, _bytes: bytes):
        try:
            await self.run_in_executor(
                self.process.write_bytes, address, _bytes, len(_bytes),
            )
        except pymem.exception.MemoryWriteError:
            # see read_bytes
            if not self.is_running():
                raise ClientClosedError()
            else:
                raise MemoryWriteError(address)

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
