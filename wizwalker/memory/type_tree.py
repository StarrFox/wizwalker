from typing import Optional

import wizwalker
from .memory_object import DynamicMemoryObject


HASHCALLPATTERN = rb"\xE8....\x48\x3B\x18\x74\x12"


class HashNode(DynamicMemoryObject):
    def __eq__(self, other):
        return self.base_address == other.base_address

    def __hash__(self):
        return hash(self.base_address)

    def left(self) -> Optional["HashNode"]:
        addr = self.read_value_from_offset(0x0, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    def parent(self) -> Optional["HashNode"]:
        addr = self.read_value_from_offset(0x8, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    def right(self) -> Optional["HashNode"]:
        addr = self.read_value_from_offset(0x10, "long long")

        if not addr:
            return None

        return HashNode(self.hook_handler, addr)

    def is_leaf(self) -> bool:
        return self.read_value_from_offset(0x19, "bool")

    def hash(self) -> int:
        return self.read_value_from_offset(0x20, "int")

    def node_data(self) -> Optional["Type"]:
        addr = self.read_value_from_offset(0x28, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)


class Type(DynamicMemoryObject):
    # Note: helper method
    def get_bases(self) -> list["PropertyList"]:
        fields = self.property_list()

        if not fields:
            return []

        bases = []
        current_base = fields
        while base_type := current_base.base_class():
            bases.append(base_type)
            current_base = base_type

        return bases

    def alloc_thing(self):
        # TODO
        pass

    def allocator(self):
        vtable = self.read_value_from_offset(0x0, "long long")
        return self.read_typed(vtable + 0x10, "long long")

    def name(self) -> str:
        return self.read_string_from_offset(0x38)

    def hash(self) -> int:
        return self.read_value_from_offset(0x58, "int")

    def size(self) -> int:
        return self.read_value_from_offset(0x60, "int")

    def name_2(self) -> str:
        return self.read_string_from_offset(0x68)

    def is_pointer(self) -> bool:
        return self.read_value_from_offset(0x88, "bool")

    def is_ref(self) -> bool:
        return self.read_value_from_offset(0x89, "bool")

    def property_list(self) -> Optional["PropertyList"]:
        addr = self.read_value_from_offset(0x90, "long long")

        if not addr:
            return None

        return PropertyList(self.hook_handler, addr)


class PropertyList(DynamicMemoryObject):
    def is_singleton(self) -> bool:
        return self.read_value_from_offset(0x9, "bool")

    def offset(self) -> int:
        return self.read_value_from_offset(0x10, "int")

    def base_class_list(self) -> Optional["PropertyList"]:
        addr = self.read_value_from_offset(0x18, "long long")

        if not addr:  # No base class
            return None

        return PropertyList(self.hook_handler, addr)

    def type(self) -> Optional["Type"]:
        addr = self.read_value_from_offset(0x20, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    def pointer_version(self) -> Optional["Type"]:
        addr = self.read_value_from_offset(0x30)

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    def properties(self) -> list["Property"]:
        res = []

        for addr in self.read_shared_vector(0x58):
            res.append(Property(self.hook_handler, addr))

        return res

    # TODO
    def functions(self):
        pass

    def name(self) -> str:
        return self.read_string_from_offset(0xB8, sso_size=10)


class Property(DynamicMemoryObject):
    def parent_list(self) -> Optional["PropertyList"]:
        addr = self.read_value_from_offset(0x38, "long long")

        if not addr:
            return None

        return PropertyList(self.hook_handler, addr)

    def container(self) -> Optional["Container"]:
        addr = self.read_value_from_offset(0x40, "long long")

        if not addr:
            return None

        return Container(self.hook_handler, addr)

    def index(self) -> int:
        return self.read_value_from_offset(0x50, "int")

    def name(self) -> Optional[str]:
        addr = self.read_value_from_offset(0x58, "long long")

        if addr is None:
            return None

        return self.read_null_terminated_string(addr, 100)

    def name_hash(self) -> int:
        return self.read_value_from_offset(0x60, "int")

    def full_hash(self) -> int:
        return self.read_value_from_offset(0x64, "int")

    def offset(self) -> int:
        return self.read_value_from_offset(0x68, "int")

    def type(self) -> Optional["Type"]:
        addr = self.read_value_from_offset(0x70, "long long")

        if not addr:
            return None

        return Type(self.hook_handler, addr)

    def flags(self) -> int:
        return self.read_value_from_offset(0x80, "int")

    def note(self) -> str:
        return self.read_string_from_offset(0x88)

    def ps_info(self):
        return self.read_string_from_offset(0x90)

    def enum_options(self) -> Optional[dict[str, int]]:
        start = self.read_value_from_offset(0x98, "long long")

        if not start:
            return None

        end = self.read_value_from_offset(0xA0, "long long")
        total_size = end - start

        current = start
        enum_opts = {}
        for entry in range(total_size // 0x48):
            value = self.read_typed(current + 0x20, "int")
            name = self.read_string(current + 0x28)

            enum_opts[name] = value

            current += 0x48

        return enum_opts


class Container(DynamicMemoryObject):
    def name(self) -> str:
        vtable = self.read_value_from_offset(0x0, "long long")
        lea_func_addr = self.read_typed(vtable + 0x8, "long long")

        # 48 8D 05 [41 4A 15 02]

        # 3 is the length of the instruct before data
        name_offset = self.read_typed(lea_func_addr + 3, "int")

        # 7 is the length of the instruction
        return self.read_null_terminated_string(
            lea_func_addr + 7 + name_offset, max_size=50
        )

    def is_dynamic(self) -> bool:
        vtable = self.read_value_from_offset(0x0, "long long")
        get_dynamic_func_addr = self.read_typed(vtable + 0x20, "long long")
        res_byte = self.read_bytes(get_dynamic_func_addr + 1, 1)

        return res_byte == b"\x01"


def _get_root_node(client):
    handler: "wizwalker.memory.HookHandler" = client.hook_handler

    hash_call_addr = handler.pattern_scan(
        HASHCALLPATTERN, module="WizardGraphicalClient.exe"
    )

    # E8 [B2 43 00 00]
    call_offset = handler.read_typed(hash_call_addr + 1, "int")

    # 5 is the length of the call instruction
    call_addr = hash_call_addr + call_offset + 5

    # 48 8B 05 [BF 0A F7 01]
    hashtree_offset = handler.read_typed(call_addr + 53, "int")

    # 50 is start of the lea instruction and 7 is the length of it
    hashtree_addr = call_addr + 50 + hashtree_offset + 7

    return handler.read_typed(hashtree_addr, "long long")


def _get_children_nodes(node: HashNode, nodes: set):
    nodes.add(node)

    if not node.is_leaf():
        if left_node := node.left():
            _get_children_nodes(left_node, nodes)

        if right_node := node.right():
            _get_children_nodes(right_node, nodes)

    return nodes


def _read_all_nodes(client, root_addr):
    nodes = set()

    handler: "wizwalker.memory.HookHandler" = client.hook_handler

    root_node = HashNode(handler, handler.read_typed(root_addr, "long long"))

    first_node = root_node.parent()

    all_nodes = _get_children_nodes(first_node, nodes)

    return all_nodes


def get_hash_nodes(client: "wizwalker.Client") -> set[HashNode]:
    root_node = _get_root_node(client)
    return _read_all_nodes(client, root_node)


def get_hash_map(client: "wizwalker.Client") -> dict[str, HashNode]:
    nodes = get_hash_nodes(client)

    hash_map = {}

    for node in nodes:
        if node.is_leaf():
            continue

        data = node.node_data()

        if data:
            name = data.name()
            hash_map[name] = node

    return hash_map
