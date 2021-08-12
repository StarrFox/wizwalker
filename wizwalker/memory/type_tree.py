from typing import Optional

import wizwalker
from .memory_object import AddressedMemoryObject


HASHCALLPATTERN = rb"\xE8....\x48\x3B\x18\x74\x12"


class HashNode(AddressedMemoryObject):
    def __hash__(self):
        return hash(self.base_address)

    async def left(self) -> Optional["HashNode"]:
        addr = await self.read_value_from_offset(0x0, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    async def parent(self) -> Optional["HashNode"]:
        addr = await self.read_value_from_offset(0x8, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    async def right(self) -> Optional["HashNode"]:
        addr = await self.read_value_from_offset(0x10, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    async def is_leaf(self) -> bool:
        return await self.read_value_from_offset(0x19, "bool")

    async def hash(self) -> int:
        return await self.read_value_from_offset(0x20, "int")

    async def node_data(self) -> Optional["Type"]:
        addr = await self.read_value_from_offset(0x28, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)


class Type(AddressedMemoryObject):
    _bases = None

    # Note: helper method
    async def get_bases(self) -> list["PropertyList"]:
        # so it only needs to be read once
        if self._bases:
            return self._bases

        fields = await self.property_list()

        if not fields:
            return []

        bases = []
        current_base = fields
        while base_type := await current_base.base_class_list():
            bases.append(base_type)
            current_base = base_type

        self._bases = bases
        return bases

    async def alloc_thing(self):
        # TODO
        pass

    async def allocator(self):
        vtable = await self.read_value_from_offset(0x0, "long long")
        return await self.read_typed(vtable + 0x10, "long long")

    async def name(self) -> str:
        return await self.read_string_from_offset(0x38)

    async def hash(self) -> int:
        return await self.read_value_from_offset(0x58, "int")

    async def size(self) -> int:
        return await self.read_value_from_offset(0x60, "int")

    async def name_2(self) -> str:
        return await self.read_string_from_offset(0x68)

    async def is_pointer(self) -> bool:
        return await self.read_value_from_offset(0x88, "bool")

    async def is_ref(self) -> bool:
        return await self.read_value_from_offset(0x89, "bool")

    async def property_list(self) -> Optional["PropertyList"]:
        addr = await self.read_value_from_offset(0x90, "long long")

        if not addr:
            return None

        return PropertyList(self.hook_handler, addr)


class PropertyList(AddressedMemoryObject):
    async def is_singleton(self) -> bool:
        return await self.read_value_from_offset(0x9, "bool")

    async def offset(self) -> int:
        return await self.read_value_from_offset(0x10, "int")

    async def base_class_list(self) -> Optional["PropertyList"]:
        addr = await self.read_value_from_offset(0x18, "long long")

        if not addr:  # No base class
            return None

        return PropertyList(self.hook_handler, addr)

    async def type(self) -> Optional["Type"]:
        addr = await self.read_value_from_offset(0x20, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    async def pointer_version(self) -> Optional["Type"]:
        addr = await self.read_value_from_offset(0x30)

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    async def properties(self) -> list["Property"]:
        res = []

        for addr in await self.read_shared_vector(0x58):
            res.append(Property(self.hook_handler, addr))

        return res

    # TODO
    async def functions(self):
        pass

    async def name(self) -> str:
        return await self.read_string_from_offset(0xB8, sso_size=10)


class Property(AddressedMemoryObject):
    async def parent_list(self) -> Optional["PropertyList"]:
        addr = await self.read_value_from_offset(0x38, "long long")

        if not addr:
            return None

        return PropertyList(self.hook_handler, addr)

    async def container(self) -> Optional["Container"]:
        addr = await self.read_value_from_offset(0x40, "long long")

        if not addr:
            return None

        return Container(self.hook_handler, addr)

    async def index(self) -> int:
        return await self.read_value_from_offset(0x50, "int")

    async def name(self) -> Optional[str]:
        addr = await self.read_value_from_offset(0x58, "long long")

        if addr is None:
            return None

        return await self.read_null_terminated_string(addr, 100)

    async def name_hash(self) -> int:
        return await self.read_value_from_offset(0x60, "int")

    async def full_hash(self) -> int:
        return await self.read_value_from_offset(0x64, "int")

    async def offset(self) -> int:
        return await self.read_value_from_offset(0x68, "int")

    async def type(self) -> Optional["Type"]:
        addr = await self.read_value_from_offset(0x70, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    async def flags(self) -> int:
        return await self.read_value_from_offset(0x80, "int")

    async def note(self) -> str:
        return await self.read_string_from_offset(0x88)

    async def ps_info(self):
        return await self.read_string_from_offset(0x90)

    async def enum_options(self) -> Optional[dict[str, int]]:
        start = await self.read_value_from_offset(0x98, "long long")

        if not start:
            return None

        end = await self.read_value_from_offset(0xA0, "long long")
        total_size = end - start

        current = start
        enum_opts = {}
        for entry in range(total_size // 0x48):
            value = await self.read_typed(current + 0x20, "int")
            name = await self.read_string(current + 0x28)

            enum_opts[name] = value

            current += 0x48

        return enum_opts


class Container(AddressedMemoryObject):
    async def name(self) -> str:
        vtable = await self.read_value_from_offset(0x0, "long long")
        lea_func_addr = await self.read_typed(vtable + 0x8, "long long")

        # 48 8D 05 [41 4A 15 02]

        # 3 is the length of the instruct before data
        name_offset = await self.read_typed(lea_func_addr + 3, "int")

        # 7 is the length of the instruction
        return await self.read_null_terminated_string(
            lea_func_addr + 7 + name_offset, max_size=50
        )

    async def is_dynamic(self) -> bool:
        vtable = await self.read_value_from_offset(0x0, "long long")
        get_dynamic_func_addr = await self.read_typed(vtable + 0x20, "long long")
        res_byte = await self.read_bytes(get_dynamic_func_addr + 1, 1)

        return res_byte == b"\x01"


async def _get_root_node(client):
    handler: "wizwalker.memory.HookHandler" = client.hook_handler

    hash_call_addr = await handler.pattern_scan(
        HASHCALLPATTERN, module="WizardGraphicalClient.exe"
    )

    # E8 [B2 43 00 00]
    call_offset = await handler.read_typed(hash_call_addr + 1, "int")

    # 5 is the length of the call instruction
    call_addr = hash_call_addr + call_offset + 5

    # 48 8B 05 [BF 0A F7 01]
    hashtree_offset = await handler.read_typed(call_addr + 53, "int")

    # 50 is start of the lea instruction and 7 is the length of it
    hashtree_addr = call_addr + 50 + hashtree_offset + 7

    return await handler.read_typed(hashtree_addr, "long long")


async def _get_children_nodes(node: HashNode, nodes: set):
    nodes.add(node)

    if not await node.is_leaf():
        if left_node := await node.left():
            await _get_children_nodes(left_node, nodes)

        if right_node := await node.right():
            await _get_children_nodes(right_node, nodes)

    return nodes


async def _read_all_nodes(client, root_addr):
    nodes = set()

    handler: "wizwalker.memory.HookHandler" = client.hook_handler

    root_node = HashNode(handler, await handler.read_typed(root_addr, "long long"))

    first_node = await root_node.parent()

    all_nodes = await _get_children_nodes(first_node, nodes)

    return all_nodes


async def get_hash_nodes(client: "wizwalker.Client") -> set[HashNode]:
    root_node = await _get_root_node(client)
    return await _read_all_nodes(client, root_node)


async def get_type_tree(client: "wizwalker.Client") -> dict[str, HashNode]:
    nodes = await get_hash_nodes(client)

    hash_map = {}

    for node in nodes:
        if await node.is_leaf():
            continue

        data = await node.node_data()

        if data:
            name = await data.name()
            hash_map[name] = node

    return hash_map
