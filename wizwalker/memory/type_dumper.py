import asyncio
import json
from pathlib import Path

import wizwalker


class TypeDumper:
    def __init__(self, type_tree: dict[str, "wizwalker.memory.type_tree.HashNode"]):
        self.type_tree = type_tree

    async def dump(self, output_file: str | Path):
        output = ""
        async for formated_class in self.class_loop(self.type_tree):
            output += formated_class

        await self.output(output_file, output)

    async def class_loop(self, type_tree):
        for name, node in type_tree.items():
            data = await node.node_data()

            property_list: "wizwalker.memory.type_tree.PropertyList"
            property_list = await data.property_list()

            formatted_properties = []

            if property_list:
                for property_ in await property_list.properties():
                    enum_options = await property_.enum_options()

                    formatted_enum_options = []
                    if enum_options:
                        for enum_option_name, enum_option_value in enum_options.items():
                            formatted_enum_options.append(
                                await self.format_enum_option(
                                    enum_option_name, enum_option_value
                                )
                            )

                    property_name, property_info = await self.get_property_info(
                        property_
                    )

                    formatted_properties.append(
                        await self.format_property(
                            property_name, property_info, formatted_enum_options
                        )
                    )

            base_names, class_hash = await self.get_class_info(data)
            formated_class = await self.format_class(
                name, base_names, class_hash, formatted_properties
            )

            yield formated_class

    @staticmethod
    async def output(output_file, output):
        def _output():
            with open(output_file, "w+") as fp:
                fp.write(output)

        await asyncio.to_thread(_output)

    @staticmethod
    async def get_class_info(node_data: "wizwalker.memory.type_tree.Type"):
        bases = await node_data.get_bases()
        class_hash = await node_data.hash()
        return [await base.name() for base in bases], class_hash

    @staticmethod
    async def get_property_info(property_: "wizwalker.memory.type_tree.Property"):
        property_name = await property_.name()
        property_type = await property_.type()

        container = await property_.container()

        property_info = {
            "type": await property_type.name(),
            "offset": await property_.offset(),
            "flags": await property_.flags(),
            "container": await container.name(),
            "dynamic": await container.is_dynamic(),
            "pointer": await property_type.is_pointer(),
            "hash": await property_.full_hash(),
        }

        return property_name, property_info

    async def format_enum_option(self, name: str, value: int):
        raise NotImplemented()

    async def format_property(
        self, name: str, info: dict[str, str], enum_options: list[str]
    ):
        raise NotImplemented()

    async def format_class(
        self, name: str, base_names: list[str], class_hash: int, properties: list[str]
    ):
        raise NotImplemented()


class TextTypeDumper(TypeDumper):
    async def dump(self, output_file: str | Path):
        output = ""
        async for formated_class in self.class_loop(self.type_tree):
            output += formated_class
            output += "\n"

        await self.output(output_file, output)

    async def format_enum_option(self, name: str, value: int):
        return f"\t\t{name} = {value}"

    async def format_property(
        self, name: str, info: dict[str, str], enum_options: list[str]
    ):
        res = f"\t{name}: {' '.join(f'{key}={value}' for key, value in info.items())}"
        if enum_options:
            res += "\n"
            res += "\n".join(enum_options)

        return res

    async def format_class(
        self, name: str, base_names: list[str], class_hash: int, properties: list[str]
    ):
        if properties:
            props = ":\n" + "\n".join(properties)
        else:
            props = ""

        class_hash = "{" + str(class_hash) + "}"

        return f"{name} {base_names} {class_hash}{props}"


class JsonTypeDumper(TypeDumper):
    async def dump(self, output_file: str | Path, *, indent: int = 4):
        output = {}
        async for formated_class in self.class_loop(self.type_tree):
            output.update(formated_class)

        await self.output(output_file, json.dumps(output, indent=indent))

    async def format_enum_option(self, name: str, value: int):
        return {name: value}

    async def format_property(
        self, name: str, info: dict[str, str], enum_options: list[dict]
    ):
        res = {name: info}

        if enum_options:
            options = {}

            for enum_dict in enum_options:
                options.update(enum_dict)

            # noinspection PyTypeChecker
            res[name]["enum_options"] = options

        return res

    async def format_class(
        self, name: str, base_names: list[str], class_hash: int, properties: dict
    ):
        props = {}

        for prop in properties:
            props.update(prop)

        return {name: {"bases": base_names, "hash": class_hash, "properties": props}}
