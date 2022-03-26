import struct
from enum import Enum
from typing import Any

import wizwalker
from wizwalker.constants import type_format_dict
from wizwalker.errors import (
    AddressOutOfRange,
    MemoryReadError,
    ReadingEnumFailed,
    WizWalkerMemoryError,
)
from wizwalker.utils import XYZ
from .handler import HookHandler
from .memory_handler import MemoryHandler


MAX_STRING = 5_000


# TODO: add .find_instances that find instances of whichever class used it
class MemoryObject(MemoryHandler):
    """
    Class for any represented classes from memory
    """

    def __init__(self, hook_handler: HookHandler):
        super().__init__(hook_handler.process)
        self.hook_handler = hook_handler

    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def read_value_from_offset(self, offset: int, data_type: str) -> Any:
        base_address = await self.read_base_address()
        return await self.read_typed(base_address + offset, data_type)

    async def write_value_to_offset(self, offset: int, value: Any, data_type: str):
        base_address = await self.read_base_address()
        await self.write_typed(base_address + offset, value, data_type)

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

    async def read_wide_string_from_offset(
        self, offset: int, encoding: str = "utf-16"
    ) -> str:
        base_address = await self.read_base_address()
        return await self.read_wide_string(base_address + offset, encoding)

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

    async def write_wide_string_to_offset(
        self, offset: int, string: str, encoding: str = "utf-8"
    ):
        base_address = await self.read_base_address()
        await self.write_string(base_address + offset, string, encoding)

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

    async def read_string_from_offset(
        self, offset: int, encoding: str = "utf-8", *, sso_size: int = 16
    ) -> str:
        base_address = await self.read_base_address()
        return await self.read_string(
            base_address + offset, encoding, sso_size=sso_size
        )

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

    async def write_string_to_offset(
        self, offset: int, string: str, encoding: str = "utf-8"
    ):
        base_address = await self.read_base_address()
        await self.write_string(base_address + offset, string, encoding)

    async def read_vector(self, offset: int, size: int = 3, data_type: str = "float"):
        type_str = type_format_dict[data_type].replace("<", "")
        size_per_type = struct.calcsize(type_str)

        base_address = await self.read_base_address()
        vector_bytes = await self.read_bytes(
            base_address + offset, size_per_type * size
        )

        return struct.unpack("<" + type_str * size, vector_bytes)

    async def write_vector(
        self, offset: int, value: tuple, size: int = 3, data_type: str = "float"
    ):
        type_str = type_format_dict[data_type].replace("<", "")

        base_address = await self.read_base_address()
        packed_bytes = struct.pack("<" + type_str * size, *value)

        await self.write_bytes(base_address + offset, packed_bytes)

    async def read_xyz(self, offset: int) -> XYZ:
        x, y, z = await self.read_vector(offset)
        return XYZ(x, y, z)

    async def write_xyz(self, offset: int, xyz: XYZ):
        await self.write_vector(offset, (xyz.x, xyz.y, xyz.z))

    async def read_enum(self, offset, enum: type[Enum]):
        value = await self.read_value_from_offset(offset, "int")
        try:
            res = enum(value)
        except ValueError:
            raise ReadingEnumFailed(enum, value)
        else:
            return res

    async def write_enum(self, offset, value: Enum):
        await self.write_value_to_offset(offset, value.value, "int")

    async def read_shared_vector(
        self, offset: int, *, max_size: int = 1000
    ) -> list[int]:
        start_address = await self.read_value_from_offset(offset, "long long")
        end_address = await self.read_value_from_offset(offset + 8, "long long")
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

    async def read_dynamic_vector(
        self, offset: int, data_type: str = "long long"
    ) -> list[int]:
        """
        Read a vector that changes in size
        """
        start_address = await self.read_value_from_offset(offset, "long long")
        end_address = await self.read_value_from_offset(offset + 8, "long long")

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

    async def read_shared_linked_list(self, offset: int) -> list[int]:
        list_addr = await self.read_value_from_offset(offset, "long long")

        addrs = []
        next_node_addr = list_addr
        list_size = await self.read_value_from_offset(offset + 8, "int")
        for _ in range(list_size):
            list_node = await self.read_typed(next_node_addr, "long long")
            next_node_addr = await self.read_typed(list_node, "long long")
            # pointer is +16 from "last" list node
            addrs.append(await self.read_typed(list_node + 16, "long long"))

        return addrs

    async def read_linked_list(self, offset: int) -> list[int]:
        list_addr = await self.read_value_from_offset(offset, "long long")
        list_size = await self.read_value_from_offset(offset + 8, "int")

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


class DynamicMemoryObject(MemoryObject):
    def __init__(self, hook_handler: HookHandler, base_address: int):
        super().__init__(hook_handler)

        # sanity check
        if base_address == 0:
            raise RuntimeError(
                f"Dynamic object {type(self).__name__} passed 0 base address."
            )

        self.base_address = base_address

    async def read_base_address(self) -> int:
        return self.base_address

    def __repr__(self):
        return f"<{type(self).__name__} {self.base_address=}>"


class PropertyClass(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def maybe_read_type_name(self) -> str:
        try:
            return await self.read_type_name()
        except (MemoryReadError, UnicodeDecodeError):
            return ""

    async def read_type_name(self) -> str:
        vtable = await self.read_value_from_offset(0, "long long")
        # first function
        get_class_name = await self.read_typed(vtable, "long long")
        # sometimes is a function with a jmp, sometimes just a body pointer
        maybe_jmp = await self.read_bytes(get_class_name, 5)
        # 233 is 0xE9 (jmp)
        if maybe_jmp[0] == 233:
            offset = struct.unpack("<i", maybe_jmp[1:])[0]
            # 5 is length of this jmp instruction
            actual_get_class_name = get_class_name + offset + 5
        else:
            actual_get_class_name = get_class_name

        # 63 is the length of the function up to the lea instruction
        lea_instruction = actual_get_class_name + 63
        # 48 8D 0D (here)
        lea_target = actual_get_class_name + 66
        rip_offset = await self.read_typed(lea_target, "int")

        # 7 is the size of this line (rip is set at the next instruction when this one is executed)
        type_name_addr = lea_instruction + rip_offset + 7

        # some of the class names can be quite long
        # i.e ClientShadowCreatureLevelTransitionCinematicAction
        return await self.read_null_terminated_string(type_name_addr, 60)


class PropertyContainer:
    def __init__(self):
        pass

    def __getattribute__(self, item: str):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            pass


class RawMemoryObject(DynamicMemoryObject):
    _prop_instances = {}

    def __init__(
        self,
        hook_handler: HookHandler,
        base_address: int,
        hash_data: "wizwalker.memory.hashmap.NodeData",
    ):
        super().__init__(hook_handler, base_address)
        self.hash_data = hash_data

    async def _generate_property_map(self):
        pass

    async def _get_prop_map(self) -> dict:
        return {}

    async def _get_prop(self, name: str):
        prop_map = await self._get_prop_map()

        if name not in prop_map.keys():
            class_name = await self.name()
            raise AttributeError(
                f"MemoryObject '{class_name}' has no attribute '{name}'"
            )

        return await prop_map[name]

    async def name(self) -> str:
        return await self.hash_data.name()

    async def get_bases(self) -> list[str]:
        bases = await self.hash_data.get_bases()
        return [await base.name() for base in bases]
