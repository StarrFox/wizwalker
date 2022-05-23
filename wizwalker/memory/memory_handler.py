import regex
import struct
from enum import Enum
from typing import Any, Type

import pefile
import pymem
import pymem.exception
import pymem.process
import pymem.ressources.structure
from loguru import logger

from wizwalker import (
    AddressOutOfRange,
    ClientClosedError,
    MemoryReadError,
    MemoryWriteError,
    PatternFailed,
    PatternMultipleResults,
    WizWalkerMemoryError,
    XYZ,
    type_format_dict,
    utils,
)


MAX_STRING = 5_000


class MemoryHandler:
    """
    Represents anything that needs to read/write from/to memory
    """

    def __init__(self, process: pymem.Pymem):
        self.process = process

        self._symbol_table = {}

    @property
    def is_running(self) -> bool:
        """
        If the process we're reading/writing to/from is running
        """
        return utils.check_if_process_running(self.process.process_handle)

    def _get_symbols(self, file_path: str, *, force_reload: bool = False):
        if (dll_table := self._symbol_table.get(file_path)) and not force_reload:
            return dll_table

        # exe_path = utils.get_wiz_install() / "Bin" / "WizardGraphicalClient.exe"
        pe = pefile.PE(file_path)

        symbols = {}

        # noinspection PyUnresolvedReferences
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name:
                symbols[exp.name.decode()] = exp.address

            else:
                symbols[f"Ordinal {exp.ordinal}"] = exp.address

        self._symbol_table[file_path] = symbols
        return symbols

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

        for match in regex.finditer(pattern, page_bytes, regex.DOTALL):
            found_address = address + match.span()[0]
            found.append(found_address)

        return next_region, found

    def _scan_all(
        self,
        handle: int,
        pattern: bytes,
        return_multiple: bool = False,
    ):
        next_region = 0

        found = []
        while next_region < 0x7FFFFFFF0000:
            next_region, page_found = self._scan_page_return_all(
                handle, next_region, pattern
            )
            if page_found:
                found += page_found

            if not return_multiple and found:
                break

        return found

    def _scan_entire_module(self, handle, module, pattern):
        base_address = module.lpBaseOfDll
        max_address = module.lpBaseOfDll + module.SizeOfImage
        page_address = base_address

        found = []
        while page_address < max_address:
            page_address, page_found = self._scan_page_return_all(
                handle, page_address, pattern
            )
            if page_found:
                found += page_found

        return found

    async def pattern_scan(
        self, pattern: bytes, *, module: str = None, return_multiple: bool = False
    ) -> list | int:
        """
        Scan for a pattern

        Args:
            pattern: The byte pattern to search for
            module: What module to search or None to search all
            return_multiple: If multiple results should be returned

        Raises:
            PatternFailed: If the pattern returned no results
            PatternMultipleResults: If the pattern returned multiple results and return_multple is False

        Returns:
            A list of results if return_multple is True otherwise one result
        """
        if module:
            module_object = pymem.process.module_from_name(self.process.process_handle, module)

            if module_object is None:
                raise ValueError(f"{module} module not found.")

            found_addresses = await utils.run_in_executor(
                self._scan_entire_module,
                self.process.process_handle,
                module_object,
                pattern,
            )

        else:
            found_addresses = await utils.run_in_executor(
                self._scan_all,
                self.process.process_handle,
                pattern,
                return_multiple,
            )

        logger.debug(
            f"Got results (first 10) {found_addresses[:10]} from pattern {pattern}"
        )
        if (found_length := len(found_addresses)) == 0:
            raise PatternFailed(pattern)
        elif found_length > 1 and not return_multiple:
            raise PatternMultipleResults(f"Got {found_length} results for {pattern}")
        elif return_multiple:
            return found_addresses
        else:
            return found_addresses[0]

    async def get_address_from_symbol(
        self,
        module_name: str,
        symbol_name: str,
        *,
        module_dir: str = None,
        force_reload: bool = False,
    ) -> int:
        """
        Get an address from a module using its symbol

        Args:
            module_name: Name of the module
            symbol_name: Name of the symbol
            module_dir: Dir the module is within
            force_reload: Force export table reload

        Returns:
            The address of the symbol in memory

        Raises:
            ValueError: No symbol/module with that name
        """
        if not module_dir:
            module_dir = utils.get_system_directory()

        file_path = module_dir / module_name

        if not file_path.exists():
            raise ValueError(f"No module named {module_name}")

        symbols = await utils.run_in_executor(
            self._get_symbols, file_path, force_reload=force_reload
        )

        if not (symbol := symbols.get(symbol_name)):
            raise ValueError(f"No symbol named {symbol_name} in module {module_name}")

        module = pymem.process.module_from_name(
            self.process.process_handle, module_name
        )

        return module.lpBaseOfDll + symbol

    async def allocate(self, size: int) -> int:
        """
        Allocate some bytes

        Args:
            size: The number of bytes to allocate

        Returns:
            The allocated address
        """
        return self.process.allocate(size)

    async def free(self, address: int):
        """
        Free some bytes

        Args:
             address: The address to free
        """
        self.process.free(address)

    # TODO: figure out how params works
    async def start_thread(self, address: int):
        """
        Start a thread at an address

        Args:
            address: The address to start the thread at
        """
        await utils.run_in_executor(self.process.start_thread, address)

    async def read_bytes(self, address: int, size: int) -> bytes:
        """
        Read some bytes from memory

        Args:
            address: The address to read from
            size: The number of bytes to read

        Raises:
            ClientClosedError: If the client is closed
            MemoryReadError: If there was an error reading memory
            AddressOutOfRange: If the addrress is out of bounds
        """
        if not 0 < address <= 0x7FFFFFFFFFFFFFFF:
            raise AddressOutOfRange(address)

        try:
            return self.process.read_bytes(address, size)
        except pymem.exception.MemoryReadError:
            # we don't want to run is running for every read
            # so we just check after we error
            if not self.is_running:
                raise ClientClosedError()
            else:
                raise MemoryReadError(address)

    async def write_bytes(self, address: int, value: bytes):
        """
        Write bytes to memory

        Args:
            address: The address to write to
            value: The bytes to write
        """
        size = len(value)
        try:
            self.process.write_bytes(
                address,
                value,
                size,
            )
        except pymem.exception.MemoryWriteError:
            # see read_bytes
            if not self.is_running:
                raise ClientClosedError()
            else:
                raise MemoryWriteError(address)

    async def read_typed(self, address: int, data_type: str) -> Any:
        """
        Read typed bytes from memory

        Args:
            address: The address to read from
            data_type: The type to read (defined in constants)

        Returns:
            The converted data type
        """
        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} is not a valid data type")

        data = await self.read_bytes(address, struct.calcsize(type_format))
        return struct.unpack(type_format, data)[0]

    async def read_multiple_typed(self, address: int, *data_types: str) -> Any | tuple[Any]:
        """
        Read typed bytes from memory

        Args:
            address: The address to read from
            data_types: The type to read (defined in constants)

        Returns:
            The converted data type
        """
        type_format = "<"
        for data_type in data_types:
            data_type_format = type_format_dict.get(data_type)
            if data_type_format is None:
                raise ValueError(f"Invalid data type {data_type}")

            type_format += data_type_format.replace("<", "")

        data = await self.read_bytes(address, struct.calcsize(type_format))
        if len(data_types) == 1:
            return struct.unpack(type_format, data)[0]

        return struct.unpack(type_format, data)

    async def write_typed(self, address: int, value: Any, data_type: str):
        """
        Write typed bytes to memory

        Args:
            address: The address to write to
            value: The value to convert and then write
            data_type: The data type to convert to
        """
        type_format = type_format_dict.get(data_type)
        if type_format is None:
            raise ValueError(f"{data_type} is not a valid data type")

        packed_data = struct.pack(type_format, value)
        await self.write_bytes(address, packed_data)

    async def write_multiple_typed(self, address: int, values: Any | tuple[any], *data_types: str):
        """
        Write typed bytes to memory

        Args:
            address: The address to write to
            values: The value to convert and then write
            data_types: The data type to convert to
        """
        type_format = "<"
        for data_type in data_types:
            data_type_format = type_format_dict.get(data_type)
            if data_type_format is None:
                raise ValueError(f"Invalid data type {data_type}")

            type_format += data_type_format.removeprefix("<", "")

        packed_data = struct.pack(type_format, *values)
        await self.write_bytes(address, packed_data)

    async def read_null_terminated_string(
        self, address: int, max_size: int = 20, encoding: str = "utf-8"
    ):
        search_bytes = await self.read_bytes(address, max_size)
        string_end = search_bytes.find(b"\x00")

        if string_end == 0:
            return ""
        elif string_end == -1:
            raise MemoryReadError(f"Couldn't read string at {address}; no end byte.")

        # Don't include the 0 byte
        string_bytes = search_bytes[:string_end]
        return string_bytes.decode(encoding)

    async def read_wide_string(self, address: int, encoding: str = "utf-16") -> str:
        string_len = await self.read_typed(address + 16, "int")
        if string_len == 0:
            return ""

        # wide chars take 2 bytes
        string_len *= 2

        # wide strings larger than 8 bytes are pointers
        if string_len >= 8:
            string_address = await self.read_typed(address, "long long")
        else:
            string_address = address

        try:
            return (await self.read_bytes(string_address, string_len)).decode(encoding)
        except UnicodeDecodeError:
            return ""

    async def write_wide_string(
        self, address: int, string: str, encoding: str = "utf-8"
    ):
        string_len_addr = address + 16
        encoded = string.encode(encoding)
        # len(encoded) instead of string bc it can be larger in some encodings
        string_len = len(encoded)

        current_string_len = await self.read_typed(address + 16, "int")

        # we need to create a pointer to the string data
        if string_len >= 7 > current_string_len:
            # +1 for 0 byte after
            pointer_address = await self.allocate(string_len + 1)

            # need 0 byte for some c++ null termination standard
            await self.write_bytes(pointer_address, encoded + b"\x00")
            await self.write_typed(address, pointer_address, "long long")

        # string is already a pointer
        elif string_len >= 7 and current_string_len >= 8:
            pointer_address = await self.read_typed(address, "long long")
            await self.write_bytes(pointer_address, encoded + b"\x00")

        # normal buffer string
        else:
            await self.write_bytes(address, encoded + b"\x00")

        await self.write_typed(string_len_addr, string_len, "int")

    async def read_wchar(self, address: int):
        data = await self.read_bytes(address, 2)
        return data.decode("utf-16")

    async def write_wchar(self, address: int, wchar: str):
        data = wchar.encode("utf-16")
        await self.write_bytes(address, data)

    async def read_string(
        self, address: int, encoding: str = "utf-8", *, sso_size: int = 16
    ) -> str:
        string_len = await self.read_typed(address + 16, "int")

        if not 1 <= string_len <= MAX_STRING:
            return ""

        # strings larger than 16 bytes are pointers
        if string_len >= sso_size:
            string_address = await self.read_typed(address, "long long")
        else:
            string_address = address

        try:
            return (await self.read_bytes(string_address, string_len)).decode(encoding)
        except UnicodeDecodeError:
            return ""

    async def write_string(self, address: int, string: str, encoding: str = "utf-8"):
        string_len_addr = address + 16
        encoded = string.encode(encoding)
        # len(encoded) instead of string bc it can be larger in some encodings
        string_len = len(encoded)

        current_string_len = await self.read_typed(address + 16, "int")

        # we need to create a pointer to the string data
        if string_len >= 15 > current_string_len:
            # +1 for 0 byte after
            pointer_address = await self.allocate(string_len + 1)

            # need 0 byte for some c++ null termination standard
            await self.write_bytes(pointer_address, encoded + b"\x00")
            await self.write_typed(address, pointer_address, "long long")

        # string is already a pointer
        elif string_len >= 15 and current_string_len >= 15:
            pointer_address = await self.read_typed(address, "long long")
            await self.write_bytes(pointer_address, encoded + b"\x00")

        # normal buffer string
        else:
            await self.write_bytes(address, encoded + b"\x00")

        await self.write_typed(string_len_addr, string_len, "int")

    async def read_vector(self, address, size: int = 3, data_type: str = "float"):
        type_str = type_format_dict[data_type].replace("<", "")
        size_per_type = struct.calcsize(type_str)

        vector_bytes = await self.read_bytes(address, size_per_type * size)

        return struct.unpack("<" + type_str * size, vector_bytes)

    async def write_vector(
        self, address: int, value: tuple, size: int = 3, data_type: str = "float"
    ):
        type_str = type_format_dict[data_type].replace("<", "")
        packed_bytes = struct.pack("<" + type_str * size, *value)
        await self.write_bytes(address, packed_bytes)

    async def read_xyz(self, offset: int) -> XYZ:
        x, y, z = await self.read_vector(offset)
        return XYZ(x, y, z)

    async def write_xyz(self, offset: int, xyz: XYZ):
        await self.write_vector(offset, (xyz.x, xyz.y, xyz.z))

    async def read_enum(self, address, enum: Type[Enum]):
        value = await self.read_typed(address, "int")
        try:
            res = enum(value)
        except ValueError:
            raise WizWalkerMemoryError(
                f"{value} is not a valid value of {enum.__name__}"
            )
        else:
            return res

    async def write_enum(self, address, value: Enum):
        await self.write_typed(address, value.value, "int")

    async def read_shared_vector(
        self, address: int, *, max_size: int = 1000
    ) -> list[int]:
        start_address = await self.read_typed(address, "long long")
        end_address = await self.read_typed(address + 8, "long long")
        size = end_address - start_address

        element_number = size // 16

        if size == 0:
            return []

        # dealloc
        if size < 0:
            return []

        if element_number > max_size:
            raise ValueError(f"Size was {element_number} and the max was {max_size}")

        try:
            shared_pointers_data = await self.read_bytes(start_address, size)
        except (ValueError, AddressOutOfRange, MemoryError):
            return []

        pointers = []
        data_pos = 0
        # Shared pointers are 16 in length
        for _ in range(element_number):
            # fmt: off
            shared_pointer_data = shared_pointers_data[data_pos: data_pos + 16]
            # fmt: on

            # first 8 bytes are the address
            pointers.append(struct.unpack("<q", shared_pointer_data[:8])[0])

            data_pos += 16

        return pointers

    # note: dynamic actually has no meaning here
    # is just a pointer to
    async def read_dynamic_vector(
        self, address: int, data_type: str = "long long"
    ) -> list[int]:
        """
        Read a vector that changes in size
        """
        start_address = await self.read_typed(address, "long long")
        end_address = await self.read_typed(address + 8, "long long")

        type_str = type_format_dict[data_type].replace("<", "")
        size_per_type = struct.calcsize(type_str)

        size = (end_address - start_address) // size_per_type

        if size == 0:
            return []

        current_address = start_address
        pointers = []
        for _ in range(size):
            pointers.append(await self.read_typed(current_address, data_type))

            current_address += size_per_type

        return pointers

    async def read_shared_linked_list(self, address: int) -> list[int]:
        list_addr = await self.read_typed(address, "long long")
        list_size = await self.read_typed(address + 8, "int")

        addrs = []
        next_node_addr = list_addr
        for _ in range(list_size):
            list_node = await self.read_typed(next_node_addr, "long long")
            next_node_addr = await self.read_typed(list_node, "long long")
            # pointer is +16 from "last" list node
            addrs.append(await self.read_typed(list_node + 16, "long long"))

        return addrs

    async def read_linked_list(self, address: int) -> list[int]:
        list_addr = await self.read_typed(address, "long long")
        list_size = await self.read_typed(address + 8, "int")

        if list_size < 1:
            return []

        addrs = []
        list_node = await self.read_typed(list_addr, "long long")
        # object starts +16 from node
        addrs.append(list_node + 16)
        # -1 because we've already read one node
        for _ in range(list_size - 1):
            list_node = await self.read_typed(list_node, "long long")
            addrs.append(list_node + 16)

        return addrs
