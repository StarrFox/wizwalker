import re
from pathlib import Path
from copy import deepcopy
from typing import Optional

import wizwalker


PROPERTY_NAME_PREFIX = re.compile(r"m_(\w(?=[^a-z]))?")
ENUM_NAME_PREFIX = re.compile(r"(^[^_]+_)|(^\w(?=[^a-z]))")


_CLASS_SCOPE = "    "
_METHOD_SCOPE = _CLASS_SCOPE + _CLASS_SCOPE


# TODO: finish
class ClassGenerator:
    def __init__(
        self,
        target_dir: str | Path,
        type_tree: dict[str, "wizwalker.memory.type_tree.HashNode"],
    ):
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)

        self.target_dir = target_dir
        # deep copy so the type tree can be reused
        self.type_tree = deepcopy(type_tree)

    async def generate(self):
        self.clean_type_tree()
        property_class = await self.get_class_by_name("class PropertyClass")

        if not property_class:
            RuntimeError("Propertyclass not found")

        property_inheritors = await self.get_direct_inheritors(property_class)

        print(f"{len(property_inheritors)=}")

        for class_type in property_inheritors:
            await self.handle_class(class_type)

    # TODO: handle class names like class PathManager::NodeTemplateList
    async def handle_class(self, class_type: "wizwalker.memory.type_tree.Type"):
        print(await class_type.name())

    async def create_file(self, file_name: str, content: str = None):
        pass

    def get_class_string(self, name: str, bases: list[str], methods: list[str]) -> str:
        class_string = f"class {name}"

        if bases:
            class_string += "("
            class_string += ", ".join(bases)
            class_string += ")"

        class_string += ":\n"

        if not methods:
            # fallback
            class_string += "    pass"

        else:
            class_string += "\n\n".join(methods)

        # apply ending newlines elsewhere
        return class_string

    def get_method_string(
        self,
        name: str,
        lines: list[str],
        *,
        extra_args: list[str] = None,
        extra_kwargs: list[str] = None,
        is_async: bool = True,
    ):
        method_string = _CLASS_SCOPE

        if is_async:
            method_string += "async "

        method_string += f"def {name}(self"

        if extra_args:
            method_string += ", "
            method_string += ", ".join(extra_args)

        if extra_kwargs:
            method_string += ", *, "
            method_string += ", ".join(extra_kwargs)

        method_string += "):\n"
        method_string += _METHOD_SCOPE
        method_string += ("\n" + _METHOD_SCOPE).join(lines)

        return method_string

    async def get_class_by_name(
        self, name: str, *, remove_on_found: bool = True
    ) -> Optional["wizwalker.memory.type_tree.Type"]:
        res = self.type_tree.get(name)

        if res:
            if remove_on_found:
                del self.type_tree[name]

            return await res.node_data()

        return res

    async def get_direct_inheritors(
        self,
        class_type: "wizwalker.memory.type_tree.Type",
        *,
        remove_on_found: bool = True,
    ):
        res = []

        class_prop_list = await class_type.property_list()

        # list so we can remove from the dict
        for name, node in list(self.type_tree.items()):
            data = await node.node_data()

            # this is faster than get_bases
            fields = await data.property_list()

            if not fields:
                continue

            base_fields = await fields.base_class_list()

            if not base_fields:
                # todo: log a warning?
                continue

            if base_fields.base_address == class_prop_list.base_address:
                # so we don't waste time scanning it again
                if remove_on_found:
                    del self.type_tree[name]

                res.append(data)

        return res

    def clean_type_tree(self):
        # list so we can edit the dict
        for name in list(self.type_tree.keys()):
            if any(
                [
                    not name.startswith("class"),
                    name.endswith("*"),
                    name.startswith("class SharedPointer<"),
                ]
            ):
                del self.type_tree[name]
