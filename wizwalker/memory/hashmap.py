from typing import Optional

import wizwalker
from .memory_object import DynamicMemoryObject


HASHCALLPATTERN = rb"\xE8....\x48\x3B\x18\x74\x12"


class HashNode(DynamicMemoryObject):
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

    async def node_data(self) -> Optional["NodeData"]:
        addr = await self.read_value_from_offset(0x28, "long long")

        if not addr:
            return None

        return NodeData(self.hook_handler, addr)


class NodeData(DynamicMemoryObject):
    async def alloc_thing(self):
        # TODO
        pass

    async def name(self) -> str:
        return await self.read_string_from_offset(0x38)

    async def size(self) -> int:
        return await self.read_value_from_offset(0x60, "int")

    async def name_2(self) -> str:
        return await self.read_string_from_offset(0x68)

    async def is_pointer(self) -> bool:
        return await self.read_value_from_offset(0x88, "bool")

    async def is_ref(self) -> bool:
        return await self.read_value_from_offset(0x89, "bool")

    async def field_container(self) -> Optional["FieldContainer"]:
        addr = await self.read_value_from_offset(0x90, "long long")

        if not addr:
            return None

        return FieldContainer(self.hook_handler, addr)


class FieldContainer(DynamicMemoryObject):
    async def has_singleton(self) -> bool:
        return await self.read_value_from_offset(0x9, "bool")

    async def offset(self) -> int:
        return await self.read_value_from_offset(0x10, "int")

    async def base_class(self) -> Optional["FieldContainer"]:
        addr = await self.read_value_from_offset(0x18, "long long")

        if not addr:  # No base class
            return None

        return FieldContainer(self.hook_handler, addr)

    async def type(self) -> Optional["NodeData"]:
        addr = await self.read_value_from_offset(0x20, "long long")

        if not addr:
            return None

        return NodeData(self.hook_handler, addr)

    async def properties(self) -> list["Property"]:
        res = []

        for addr in await self.read_shared_vector(0x58):
            res.append(Property(self.hook_handler, addr))

        return res

    async def functions(self):
        # TODO
        pass


class Property(DynamicMemoryObject):
    async def field_container(self) -> Optional["FieldContainer"]:
        addr = await self.read_value_from_offset(0x38, "long long")

        if not addr:
            return None

        return FieldContainer(self.hook_handler, addr)

    async def container():
        # TODO
        pass

    async def index(self) -> int:
        return await self.read_value_from_offset(0x50, "int")

    async def name(self) -> Optional[str]:
        addr = await self.read_value_from_offset(0x58, "long long")

        if addr is None:
            return None

        return await self.read_null_terminated_string(addr, 100)

    async def hash(self) -> int:
        return await self.read_value_from_offset(0x64, "int")

    async def offset(self) -> int:
        return await self.read_value_from_offset(0x68, "int")

    async def type(self) -> Optional["NodeData"]:
        addr = await self.read_value_from_offset(0x70, "long long")

        if not addr:
            return None

        return NodeData(self.hook_handler, addr)

    async def flags(self) -> int:
        return await self.read_value_from_offset(0x80, "int")

    async def note(self) -> str:
        return await self.read_string_from_offset(0x88)

    async def ps_info(self):
        # TODO
        pass


async def _get_root_node(client):
    handler: "wizwalker.memory.HookHandler" = client.hook_handler

    hash_call_addr = await handler.pattern_scan(
        HASHCALLPATTERN, module="WizardGraphicalClient.exe"
    )

    # E8 [B2 43 00 00]

    call_offset = await handler.read_typed(hash_call_addr + 1, "int")

    # 5 is the length of the lea instruction
    call_addr = hash_call_addr + call_offset + 5

    # 48 8B 05 BF 0A F7 01

    hashmap_offset = await handler.read_typed(call_addr + 53, "int")

    # 50 is start of the call instruction and 7 is the length of it
    hashmap_addr = call_addr + 50 + hashmap_offset + 7

    return await handler.read_typed(hashmap_addr, "long long")


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

    return await _get_children_nodes(first_node, nodes)


async def get_hash_nodes(client: "wizwalker.Client") -> set[HashNode]:
    root_node = await _get_root_node(client)
    return await _read_all_nodes(client, root_node)


async def get_hash_map(client: "wizwalker.Client") -> dict:
    nodes = await get_hash_nodes(client)

    hash_map = {}

    for node in nodes:
        data = await node.node_data()
        hash_ = await node.hash()

        if data:
            name = await data.name()

            if "*" in name:
                continue

            size = await data.size()
            is_pointer = await data.is_pointer()
            is_ref = await data.is_ref()

            field_container = await data.field_container()

            if field_container:
                has_singleton = await field_container.has_singleton()
                offset = await field_container.offset()

                base = await field_container.base_class()

                if base:
                    base_type = await base.type()

                    if base_type:
                        base_name = await base_type.name()

                else:
                    base_name = None

                properties = await field_container.properties()

                prop_info = {}
                for prop in properties:
                    prop_name = await prop.name()
                    prop_index = await prop.index()
                    prop_offset = await prop.offset()
                    prop_hash = await prop.hash()
                    prop_flags = await prop.flags()
                    prop_note = await prop.note()

                    prop_type = await prop.type()

                    if prop_type:
                        prop_type_name = await prop_type.name()

                    else:
                        prop_type_name = None

                    prop_info[prop_name] = {
                        "index": prop_index,
                        "offset": prop_offset,
                        "hash": prop_hash,
                        "flags": prop_flags,
                        "note": prop_note,
                        "type": prop_type_name,
                    }

            else:
                has_singleton = None
                offset = None
                base_name = None
                prop_info = None

            hash_map[name] = {
                "size": size,
                "is_pointer": is_pointer,
                "is_ref": is_ref,
                "hash": hash_,
                "has_singleton": has_singleton,
                "offset": offset,
                "base_class": base_name,
                "properties": prop_info,
            }

    return hash_map
