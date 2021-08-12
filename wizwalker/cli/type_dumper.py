import wizwalker


async def _dump_enum_options_to_string(
    enum_options: dict[str, int], prefix: str = None
) -> str:
    if prefix is None:
        prefix = ""

    res = ""

    for name, value in enum_options.items():
        res += f"{prefix}{name} = {value}"

    return res


async def _dump_properties_to_string(
    field_container: "wizwalker.memory.type_tree.PropertyList", prefix: str = None
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

        enum_options = await prop.enum_options()

        res += f"{prefix}{name}: "
        res += f"type={type_name} "
        res += f"offset={await prop.offset()} "
        res += f"flags={await prop.flags()} "
        res += f"container={container_name} "
        res += f"dynamic={is_dynamic} "
        res += f"pointer={is_pointer} "

        if enum_options:
            res += await _dump_enum_options_to_string(enum_options, prefix="\n\t\t")

    return res


async def dump_class_to_string(
    name: str, node: "wizwalker.memory.type_tree.HashNode"
) -> str:
    res = f"{name}"

    data = await node.node_data()

    if not data:
        return res

    bases = await data.get_bases()
    base_names = [await base.name() for base in bases]

    res += f" {base_names}"

    fields = await data.property_list()

    if not fields:
        return res

    prop_info = await _dump_properties_to_string(fields, "\n\t")
    res += f": {prop_info}"

    return res


async def _dump_enum_options_to_json(enum_options) -> dict:
    res = {}

    for name, value in enum_options.items():
        res[name] = value

    return res


async def _dump_properties_to_json(field_container) -> dict[str, dict]:
    res = {}

    for prop in await field_container.properties():
        prop_type = await prop.type()
        type_name = await prop_type.name()
        is_pointer = await prop_type.is_pointer()

        container = await prop.container()
        container_name = await container.name()

        is_dynamic = await container.is_dynamic()

        name = await prop.name()

        res[name] = {
            "type": type_name,
            "offset": await prop.offset(),
            "flags": await prop.flags(),
            "container": container_name,
            "dynamic": is_dynamic,
            "pointer": is_pointer,
        }

        enum_options = await prop.enum_options()
        if enum_options:
            res[name]["enum_options"] = await _dump_enum_options_to_json(enum_options)

    return res


async def dump_class_to_json(
    name: str, node: "wizwalker.memory.type_tree.HashNode"
) -> dict[str, dict]:
    data = await node.node_data()

    res = {name: {}}

    if not data:
        return res

    bases = await data.get_bases()
    base_names = [await base.name() for base in bases]

    res[name]["bases"] = base_names

    fields = await data.property_list()

    if not fields:
        return res

    res[name]["properties"] = await _dump_properties_to_json(fields)

    return res
