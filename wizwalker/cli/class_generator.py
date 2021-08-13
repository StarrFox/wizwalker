import re
from pathlib import Path

import wizwalker
from wizwalker.memory.type_tree import get_type_tree, Type


PROPERTY_NAME_PREFIX = re.compile(r"m_(\w(?=[^a-z]))?")
ENUM_NAME_PREFIX = re.compile(r"(^[^_]+_)|(^\w(?=[^a-z]))")


class ClassGenerator:
    def __init__(self, target_dir: str | Path, client: "wizwalker.Client"):
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)

        self.target_dir = target_dir
        self.client = client

    async def generate(self):
        type_tree = await get_type_tree(self.client)
        property_class = self._get_property_class(type_tree)
        property_class_data = await property_class.node_data()

        test = await self._get_direct_inheritors(property_class_data, type_tree)
        print(len(test))

    @staticmethod
    def _get_property_class(type_tree):
        if not (property_class := type_tree.get("class PropertyClass")):
            raise RuntimeError("Propertyclass not found")

        return property_class

    @staticmethod
    async def _get_direct_inheritors(class_type: Type, type_tree):
        res = []

        class_prop_list = await class_type.property_list()

        for node in type_tree.values():
            data = await node.node_data()

            bases = await data.get_bases()

            if not bases:
                continue

            # if not await bases[0].name() == (await class_type.name()).replace(
            #     "class ", ""
            # ):
            #     continue
            if not bases[0] == class_prop_list:
                continue

            res.append(node)

        return res

    # async def get_base_classes(self, type_tree) -> list[Type]:
    #     res = []
    #     for name, node in type_tree.items():
    #         if any(
    #             [
    #                 name.startswith("class std::list"),
    #                 name.startswith("enum "),
    #                 name.startswith("class std::vector"),
    #                 name.startswith("class SharedPointer"),
    #                 # name.startswith("struct std::pair"),
    #                 name.startswith("class Size"),
    #                 not name.startswith("class"),
    #                 name.startswith("class std::basic_string"),
    #                 # name.startswith("class Rect"),
    #                 # name.startswith("class Point<"),
    #                 name.endswith("*"),
    #             ]
    #         ):
    #             continue
    #
    #         data = await node.node_data()
    #         if not await data.get_bases():
    #             res.append(data)
    #
    #     return res


# TODO: remove
if __name__ == "__main__":

    async def _main():
        async with wizwalker.ClientHandler() as ch:
            client = ch.get_new_clients()[0]
            gen = ClassGenerator(".", client)

            await gen.generate()

    import asyncio

    asyncio.run(_main())
