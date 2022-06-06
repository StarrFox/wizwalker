import re

import wizwalker


PROPERTY_NAME_PREFIX = re.compile(r"m_(\w(?=[^a-z]))?")
ENUM_NAME_PREFIX = re.compile(r"(^[^_]+_)|(^\w(?=[^a-z]))")


async def dump_enum_options(enum_options: dict[str, int], prefix: str = None) -> str:
    if prefix is None:
        prefix = ""

    res = ""

    for name, value in enum_options.items():
        name = ENUM_NAME_PREFIX.sub("", name)
        res += f"{prefix}{name} = {value}"

    return res


async def dump_properties(
    field_container: "wizwalker.memory.hashmap.FieldContainer", prefix: str = None
) -> str:
    if prefix is None:
        prefix = ""

    res = ""

    for prop in await field_container.properties():
        prop_type = await prop.type()
        type_name = await prop_type.name()
        is_pointer = await prop_type.is_pointer()

        container = await prop.container()
        container_name = await container.name()

        is_dynamic = await container.is_dynamic()

        name = await prop.name()
        name = PROPERTY_NAME_PREFIX.sub("", name)

        enum_options = await prop.enum_options()

        res += f"{prefix}{name}: "
        res += f"type={type_name} "
        res += f"offset={await prop.offset()} "
        res += f"flags={await prop.flags()} "
        res += f"container={container_name} "
        res += f"dynamic={is_dynamic} "
        res += f"pointer={is_pointer} "

        if enum_options:
            res += await dump_enum_options(enum_options, prefix="\n\t\t")

    return res


async def dump_class(name: str, node: "wizwalker.memory.hashmap.HashNode") -> str:
    res = f"{name}"

    data = await node.node_data()

    if not data:
        return res

    bases = await data.get_bases()
    base_names = [await base.name() for base in bases]

    res += f" {base_names}"

    fields = await data.field_container()

    if not fields:
        return res

    if fields:
        prop_info = await dump_properties(fields, "\n\t")

        res += f": {prop_info}"

    return res


# async def dump_types_to_file(file_path: str | Path, client: "wizwalker.Client"):
#     if isinstance(file_path, str):
#         file_path = Path(file_path)
#
#     hash_map = await get_hash_map(client)
