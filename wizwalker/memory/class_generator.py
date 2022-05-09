import re


# PROPERTY_NAME_PREFIX = re.compile(r"m_(\w(?=[^a-z]))?")
# DECAMEL = re.compile(r"(?P<before>[a-z])(?P<target>[A-Z])(?P<after>[A-Z$]?)")
# PVP_OVERRIDE = re.compile(r"(?P<before>.?)(?P<target>PvP)(?P<after>.?)")
# ENUM_NAME_PREFIX = re.compile(r"(^[^_]+_)|(^\w(?=[^a-z]))")


# CLASS_TEMPLATE = Template("class $class_name($parent_class):\n$methods\n")
# METHOD_TEMPLATE = Template("async def $method_name(self, $arguments):\n$body")


class PythonCodeGenerator:
    def __init__(self, indent: str = "    "):
        self.indent = indent
        self.lines = []

    def generate(self, joiner: str = "\n") -> str:
        return joiner.join(self.lines)

    def add_line(self, line: str, level: int = 0):
        self.lines.append(self.indent * level + line)

    def add_blank_line(self):
        self.lines.append("")

    def add_block(self, lines: list[str], level: int = 0):
        for line in lines:
            self.add_line(line, level)

    def add_if(self, condition: str, body_lines: list[str], level: int = 0):
        self.add_line(f"if {condition}:", level)
        self.add_block(body_lines, level + 1)


class PythonFile(PythonCodeGenerator):
    classes = {}

    def add_class(self, python_class: "PythonClass"):
        if self.classes.get(python_class.name):
            raise ValueError(f"Class {python_class.name} already exists")

        self.classes[python_class.name] = python_class


class PythonClass(PythonCodeGenerator):
    def __init__(self, name: str,  indent: str = "    "):
        super().__init__(indent)
        self.name = name
        self.methods = {}

    def add_method(self, python_method: "PythonMethod"):
        if self.methods.get(python_method.name):
            raise ValueError(f"Method {python_method.name} already exists")

        self.methods[python_method.name] = python_method


class PythonMethod(PythonCodeGenerator):
    def __init__(self, name: str, indent: str = "    ", *, is_async: bool = False):
        super().__init__(indent)
        self.name = name
        self.is_async = is_async
        self.arguments = {}
        self.kwarguments = {}

    def generate(self, joiner: str = "\n") -> str:
        def_line = "async def" if self.is_async else "def"

        args = []
        for name, (type_name, default_value) in self.arguments.items():
            if default_value is not None:
                args.append(f"{name}: {type_name} = {default_value}")
            else:
                args.append(f"{name}: {type_name}")

        kwargs = []
        for name, (type_name, default_value) in self.kwarguments.items():
            if default_value is not None:
                kwargs.append(f"{name}: {type_name} = {default_value}")
            else:
                kwargs.append(f"{name}: {type_name}")

        def_line += f" {self.name}(self, "
        if args:
            def_line += ", ".join(args)

        if kwargs:
            def_line += ", *, " if args else "*,"
            def_line += ", ".join(kwargs)

        def_line += "):"

        self.lines = [def_line] + self.lines

        return super().generate(f"{joiner}{self.indent}")

    def add_argument(self, name: str, type_name: str, *, default_value: str = None):
        if self.arguments.get(name):
            raise ValueError(f"Argument {name} already exists")

        self.arguments[name] = (type_name, default_value)

    def add_kwargument(self, name: str, type_name: str, *, default_value: str = None):
        if self.kwarguments.get(name):
            raise ValueError(f"Kwargument {name} already exists")

        self.kwarguments[name] = (type_name, default_value)


# # TODO: come up with a reason this has to be a class
# class StringModifier:
#     @staticmethod
#     def decamel(name: str) -> str:
#         """
#         AbcDefXYZ -> abc_def_XYZ
#         """
#
#         def _pvp_override(match):
#             res = ""
#
#             before = match.group("before")
#             after = match.group("after")
#
#             if before:
#                 res += before + "_"
#
#             res += "pvp"
#
#             if after:
#                 res += "_" + after
#
#             return res
#
#         def _decamel_replacer(match):
#             res = match.group("before") + "_"
#
#             after = match.group("after")
#
#             if after:
#                 res += match.group("target") + after
#
#             else:
#                 res += match.group("target").lower()
#
#             return res
#
#         name = PVP_OVERRIDE.sub(_pvp_override, name)
#         return DECAMEL.sub(_decamel_replacer, name)
#
#     def clean_name(self, name: str, target_type: str) -> str:
#         match target_type:
#             case "class" | "return" | "enum" | "file":
#                 # class CoreObject -> CoreObject
#                 name = name.replace("class ", "")
#
#                 # Namespace::CoreObject -> Namespace_CoreObject
#                 name = name.replace("::", "_")
#
#             case "file":
#                 name = name.lower()
#
#             case "property":
#                 # m_duelID.m_full -> m_duelID_m_full
#                 name = name.replace(".", "_")
#
#                 # m_id -> id
#                 name = PROPERTY_NAME_PREFIX.sub("", name)
#
#                 # fullPartyGroup -> full_party_group
#                 name = self.decamel(name)
#
#                 # Battleground -> battleground
#                 name = name.lower()
#
#             case "enum" | "return":
#                 # enum kDuelExecutionOrder -> kDuelExecutionOrder
#                 name = name.replace("enum ", "")
#
#                 # TODO: handle this prefix
#                 # # kDuelExecutionOrder -> DuelExecutionOrder
#                 # name = name.lstrip("k")
#
#             case "return":
#                 # class SharedPointer<class CoreObject> -> class CoreObject
#                 name = name.replace("class SharedPointer<", "")
#                 name = name.replace(">", "")
#
#                 # unsigned int -> int
#                 name = name.replace("unsigned ", "")
#
#             case _:
#                 name = name.replace("*", "")
#
#         return name
#
#
# # TODO:
# #  goals:
# #   1. support for hidden properties
# #   2. clean interface that can be improved and adapted later
# class ClassGenerator:
#     """
#     Generates a file of classes generated from type information
#     """
#
#     def __init__(self, type_tree: dict[str, "wizwalker.memory.type_tree.HashNode"]):
#         self.type_tree = type_tree
#         self.string_modifier = StringModifier()
#
#     async def generate(self) -> str:
#         """
#         returns the generated class file as a string
#         """
#         class_file_string = ""
#
#         # we do this to order the class definitions so parent classes are defined before their subclasses
#         # number of bases: list[HashNode]
#         node_base_map = defaultdict(list)
#         for dirty_class_name, node in self.type_tree.items():
#             if any(
#                 (
#                     not dirty_class_name.startswith("class"),
#                     dirty_class_name.endswith("*"),
#                     dirty_class_name.startswith("class SharedPointer<"),
#                     dirty_class_name.startswith("class std::"),
#                 )
#             ):
#                 logger.debug(f"Invalid class type {dirty_class_name}")
#
#             else:
#                 # TODO: this is gotten once when getting the type tree also, fix
#                 type_data = await node.node_data()
#                 # the bases list if cached, so we don't need to store it
#                 node_base_map[len(await type_data.get_bases())].append(
#                     (dirty_class_name, type_data)
#                 )
#
#         for base_number in range(max(node_base_map.keys())):
#             for dirty_class_name, class_type in node_base_map[base_number]:
#                 class_file_string += await self.handle_class_type(
#                     dirty_class_name, class_type
#                 )
#
#         return class_file_string
#
#     async def handle_class_type(
#         self, dirty_class_name: str, class_type: "wizwalker.memory.type_tree.Type"
#     ) -> str:
#         class_name = self.string_modifier.clean_name(dirty_class_name, "class")
#
#         logger.debug(f"Cleaned class name {dirty_class_name} => {class_name}")
#         del dirty_class_name
#
#         bases = await class_type.get_bases()
#
#         if bases:
#             parent_class = bases[0]
#             dirty_parent_class = await parent_class.name()
#             parent_class = self.string_modifier.clean_name(dirty_parent_class, "class")
#
#             logger.debug(f"Cleaned parent name {dirty_parent_class} => {parent_class}")
#         else:
#             parent_class = ""
#
#         property_list = await class_type.property_list()
#
#         methods = (" " * 4) + "pass"
#
#         if not property_list:
#             logger.debug(f"No property list for class {class_name}")
#
#         else:
#             properties = await property_list.properties()
#
#             if not properties:
#                 logger.debug(f"No properties in list for class {class_name}")
#
#             else:
#                 methods = "    raise RuntimeError()"
#
#         return CLASS_TEMPLATE.substitute(
#             class_name=class_name, parent_class=parent_class, methods=methods
#         )


# class InheritanceTree:
#     def __init__(
#         self,
#         class_type: "wizwalker.memory.type_tree.Type",
#         class_generator: "ClassGenerator",
#     ):
#         # base type
#         self.class_type = class_type
#         self.class_generator = class_generator
#
#         self.class_strings: list[str] = []
#         self.imports = []
#         # {type: [method_name]}
#         self.impled_type_ref = defaultdict(lambda: list())
#
#     async def add_import(self, name: str, source: str):
#         pass
#
#     def check_if_impl(self, name: str, inheritance_path: list[str]) -> bool:
#         for super_class in inheritance_path:
#             if name in self.impled_type_ref[super_class]:
#                 return True
#
#         return False
#
#     def mark_impl(self, name: str, impled_name: str):
#         self.impled_type_ref[name].append(impled_name)
#
#     async def process(self):
#         pass
#
#     async def process_class(
#         self,
#         class_type: "wizwalker.memory.type_tree.Type",
#         *,
#         inheritance_path: list[str] = None,
#     ):
#         class_name = await class_type.name()
#         cleaned_class_name = self.clean_name(class_name, "class")
#         file_name = self.clean_name(class_name, "file")
#
#         property_list = await class_type.property_list()
#
#     # TODO: check if they override properties in subclasses? probably not
#     async def process_property(
#         self,
#         property_type: "wizwalker.memory.type_tree.Property",
#         *,
#         inheritance_path: list[str] = None,
#     ):
#         name = await property_type.name()
#
#         if inheritance_path:
#             if self.check_if_impl(name, inheritance_path):
#                 return None
#
#         self.mark_impl(inheritance_path[-1], name)
#
#         offset = await property_type.offset()
#
#         return_type = await property_type.type()
#         return_type_name = await return_type.name()
#         return_type_is_pointer = await return_type.is_pointer()
#
#         container = await property_type.container()
#         container_name = await container.name()
#         container_is_dynamic = await container.is_dynamic()
#
#         enum_options = await property_type.enum_options()
#
#         match container_name:
#             case "Static":
#                 method_string = await self.handle_static_container(
#                     name,
#                     offset,
#                     return_type_name,
#                     return_type_is_pointer,
#                 )
#             case "List" | "Vector":
#                 method_string = await self.handle_dynamic_container()
#             case _:
#                 raise RuntimeError(f"Unhandled container {container_name}")
#
#     async def process_enum(self):
#         pass
#
#     # TODO: handle write methods
#     async def handle_static_container(
#         self,
#         property_name: str,
#         offset: int,
#         return_name: str,
#         return_is_pointer: bool,
#     ) -> str:
#         clean_property_name = self.clean_name(property_name, "property")
#         clean_return = self.clean_name(return_name, "return")
#         arrow_return = clean_return
#
#         # TODO: handle Point and Rect special cases
#         # struct is just class with public members
#         if return_name.startswith("class ") or return_name.startswith("struct "):
#             if return_is_pointer:
#                 lines = [
#                     f'addr = await self.read_value_from_offset({offset}, "long long")',
#                     "if addr == 0:",
#                     "    return None",
#                     f"return {clean_return}(self.memory_reader, addr)",
#                 ]
#
#                 arrow_return = f"Optional[{clean_return}]"
#
#                 await self.add_import("Optional", "typing")
#
#             else:
#                 # TODO: vector3D -> XYZ?
#                 lines = [
#                     "base_address = await self.read_base_address()",
#                     f"return {clean_return}(self.memory_reader, base_address + {offset})",
#                 ]
#
#             await self.add_import(clean_return, ".")
#
#         elif return_name.startswith("enum "):
#             await self.add_import(clean_return, ".enums")
#             lines = [
#                 f"return await self.read_enum_from_offset({offset}, {clean_return})"
#             ]
#
#         elif return_name in wizwalker.type_format_dict.keys():
#             lines = [
#                 f'return await self.read_value_from_offset({offset}, "{return_name}")'
#             ]
#
#             if return_name in ["char", "unsigned char"]:
#                 arrow_return = "str"
#
#         else:
#             match return_name:
#                 case "__int64":
#                     lines = [
#                         f'return await self.read_value_from_offset({offset}, "long long")'
#                     ]
#                     arrow_return = "int"
#
#                 case "unsigned __int64" | "gid" | "union gid":
#                     lines = [
#                         f'return await self.read_value_from_offset({offset}, "unsigned long long")'
#                     ]
#                     arrow_return = "int"
#
#                 case "std::string":
#                     lines = [f"return await self.read_string_from_offset({offset})"]
#                     arrow_return = "str"
#
#                 case "std::wstring":
#                     lines = [
#                         f"return await self.read_wide_string_from_offset({offset})"
#                     ]
#                     arrow_return = "str"
#
#                 case "wchar_t":
#                     lines = [f"return await self.read_wchar({offset})"]
#                     arrow_return = "str"
#
#                 case "s24":
#                     lines = [
#                         "# TODO: read s24",
#                         "raise NotImplementedError()",
#                     ]
#
#                 case "bi6" | "bi7" | "bi5":
#                     lines = [
#                         f'return await self.read_value_from_offset({offset}, "int")'
#                     ]
#
#                 case "bui4" | "bui6" | "bui3" | "bui7" | "bui5":
#                     lines = [
#                         f'return await self.read_value_from_offset({offset}, "unsigned int")'
#                     ]
#
#                 case _:
#                     raise RuntimeError(f"Unhandled static type {return_name}")
#
#         return self.get_method_string(
#             clean_property_name, lines, return_type=arrow_return
#         )
#
#     # TODO
#     async def handle_dynamic_container(
#         self,
#         property_name: str,
#         offset,
#         return_name,
#         return_is_pointer: bool,
#     ) -> str:
#         pass
#
#     @staticmethod
#     def get_class_string(name: str, bases: list[str], methods: list[str]) -> str:
#         class_string = f"class {name}"
#
#         if bases:
#             class_string += "("
#             class_string += ", ".join(bases)
#             class_string += ")"
#
#         class_string += ":\n"
#
#         if not methods:
#             # fallback
#             class_string += "    pass"
#
#         else:
#             class_string += "\n\n".join(methods)
#
#         # apply ending newlines elsewhere
#         return class_string
#
#     @staticmethod
#     def get_method_string(
#         name: str,
#         lines: list[str],
#         *,
#         extra_args: list[str] = None,
#         extra_kwargs: list[str] = None,
#         is_async: bool = True,
#         return_type: str = None,
#     ) -> str:
#         method_string = _CLASS_SCOPE
#
#         if is_async:
#             method_string += "async "
#
#         method_string += f"def {name}(self"
#
#         if extra_args:
#             method_string += ", "
#             method_string += ", ".join(extra_args)
#
#         if extra_kwargs:
#             method_string += ", *, "
#             method_string += ", ".join(extra_kwargs)
#
#         method_string += ")"
#
#         if return_type:
#             method_string += f" -> {return_type}"
#
#         method_string += ":\n"
#
#         method_string += _METHOD_SCOPE
#         method_string += ("\n" + _METHOD_SCOPE).join(lines)
#
#         return method_string
#
#     @staticmethod
#     def clean_name(name: str, target_type: str) -> str:
#         match target_type:
#             case "class" | "return" | "enum" | "file":
#                 # class CoreObject -> CoreObject
#                 name = name.replace("class ", "")
#
#                 # Namespace::CoreObject -> Namespace_CoreObject
#                 name = name.replace("::", "_")
#
#             case "file":
#                 name = name.lower()
#
#             case "property":
#                 # m_duelID.m_full -> m_duelID_m_full
#                 name = name.replace(".", "_")
#
#                 # m_id -> id
#                 name = PROPERTY_NAME_PREFIX.sub("", name)
#
#                 # fullPartyGroup -> full_party_group
#                 name = decamel(name)
#
#                 # Battleground -> battleground
#                 name = name.lower()
#
#             case "enum" | "return":
#                 # enum kDuelExecutionOrder -> kDuelExecutionOrder
#                 name = name.replace("enum ", "")
#
#                 # TODO: handle this prefix
#                 # # kDuelExecutionOrder -> DuelExecutionOrder
#                 # name = name.lstrip("k")
#
#             case "return":
#                 # class SharedPointer<class CoreObject> -> class CoreObject
#                 name = name.replace("class SharedPointer<", "")
#                 name = name.replace(">", "")
#
#                 # unsigned int -> int
#                 name = name.replace("unsigned ", "")
#
#             case _:
#                 name = name.replace("*", "")
#
#         return name


# # TODO: finish
# class ClassGenerator:
#     def __init__(
#         self,
#         target_dir: str | Path,
#         type_tree: dict[str, "wizwalker.memory.type_tree.HashNode"],
#     ):
#         if isinstance(target_dir, str):
#             target_dir = Path(target_dir)
#
#         self.target_dir = target_dir
#         # deep copy so the type tree can be reused
#         self.type_tree = deepcopy(type_tree)
#         self._handled_enums = []
#
#     async def generate(self):
#         self.clean_type_tree()
#         property_class = await self.get_class_by_name("class PropertyClass")
#
#         if not property_class:
#             RuntimeError("Propertyclass not found")
#
#         property_inheritors = await self.get_direct_inheritors(property_class)
#
#         print(f"{len(property_inheritors)=}")
#
#         # TODO: remove debugging :10
#         for class_type in property_inheritors[:20]:
#             await self.handle_class(class_type, "PropertyClass")
#
#     # TODO: why is core_template duplicating
#     #  multiple inheritance paths?
#     async def handle_class(
#         self,
#         class_type: "wizwalker.memory.type_tree.Type",
#         parent: str,
#         file_contents: str = None,
#         import_string: str = None,
#         sub_base_class: str = None,
#         handled_properties: list = None,
#         dot_imports: set = None,
#         enum_imports: set = None,
#         extra_imports: set = None,
#     ):
#         class_name = await class_type.name()
#         class_name = self.clean_class_name(class_name)
#
#         property_list = await class_type.property_list()
#
#         methods = []
#
#         if not handled_properties:
#             handled_properties = []
#
#         if not dot_imports:
#             dot_imports = set()
#
#         if not enum_imports:
#             enum_imports = set()
#
#         if not extra_imports:
#             extra_imports = set()
#
#         for prop in await property_list.properties():
#             (
#                 name,
#                 offset,
#                 return_type_name,
#                 return_type_is_pointer,
#                 container_name,
#                 container_is_dynamic,
#                 enum_options,
#             ) = await self.get_property_info(prop)
#
#             name = self.clean_property_name(name)
#
#             if name in handled_properties:
#                 continue
#
#             handled_properties.append(name)
#
#             lines = []
#
#             cleaned_return_name = self.clean_return_type(return_type_name)
#             arrowed_return_name = cleaned_return_name
#
#             if enum_options:
#                 await self.handle_enum(cleaned_return_name, enum_options)
#
#             match container_name:
#                 case "Static":
#                     # TODO: handle Point and Rect special cases
#                     if return_type_name.startswith(
#                         "class "
#                     ) or return_type_name.startswith("struct "):
#                         if return_type_is_pointer:
#                             lines.extend(
#                                 [
#                                     f'addr = await self.read_value_from_offset({offset}, "long long")',
#                                     "if addr == 0:",
#                                     "    return None",
#                                     f"return {cleaned_return_name}(self.memory_reader, addr)",
#                                 ]
#                             )
#
#                             arrowed_return_name = f"Optional[{cleaned_return_name}]"
#
#                             extra_imports.add("from typing import Optional")
#
#                         else:
#                             # TODO: vector3D -> XYZ?
#                             lines.extend(
#                                 [
#                                     "base_address = await self.read_base_address()",
#                                     f"return {cleaned_return_name}(self.memory_reader, base_address + {offset})",
#                                 ]
#                             )
#
#                         dot_imports.add(cleaned_return_name)
#
#                     elif return_type_name.startswith("enum "):
#                         enum_imports.add(cleaned_return_name)
#
#                         lines.append(
#                             f"return await self.read_enum_from_offset({offset}, {cleaned_return_name})"
#                         )
#
#                     elif return_type_name in wizwalker.type_format_dict.keys():
#                         lines.append(
#                             f'return await self.read_value_from_offset({offset}, "{return_type_name}")'
#                         )
#
#                         if return_type_name in ["char", "unsigned char"]:
#                             arrowed_return_name = "str"
#
#                     else:
#                         match return_type_name:
#                             case "__int64":
#                                 lines.append(
#                                     f'return await self.read_value_from_offset({offset}, "long long")'
#                                 )
#                                 arrowed_return_name = "int"
#
#                             case "unsigned __int64" | "gid" | "union gid":
#                                 lines.append(
#                                     f'return await self.read_value_from_offset({offset}, "unsigned long long")'
#                                 )
#                                 arrowed_return_name = "int"
#
#                             case "std::string":
#                                 lines.append(
#                                     f"return await self.read_string_from_offset({offset})"
#                                 )
#                                 arrowed_return_name = "str"
#
#                             case "std::wstring":
#                                 lines.append(
#                                     f"return await self.read_wide_string_from_offset({offset})"
#                                 )
#                                 arrowed_return_name = "str"
#
#                             case "wchar_t":
#                                 lines.append(f"return await self.read_wchar({offset})")
#                                 arrowed_return_name = "str"
#
#                             case "s24":
#                                 lines.extend(
#                                     [
#                                         "# TODO: read s24",
#                                         "raise NotImplementedError()",
#                                     ]
#                                 )
#
#                             case "bi6" | "bi7" | "bi5":
#                                 lines.append(
#                                     f'return await self.read_value_from_offset({offset}, "int")'
#                                 )
#
#                             case "bui4" | "bui6" | "bui3" | "bui7" | "bui5":
#                                 lines.append(
#                                     f'return await self.read_value_from_offset({offset}, "unsigned int")'
#                                 )
#
#                             case _:
#                                 raise RuntimeError(
#                                     f"Unhandled static type {return_type_name}"
#                                 )
#
#                 case "List":
#                     # Todo: handle shared
#                     if container_is_dynamic:
#                         lines.extend(
#                             [
#                                 "# TODO",
#                                 f"# read dynamic list of {return_type_name}",
#                                 "raise NotImplementedError()",
#                             ]
#                         )
#
#                     else:
#                         lines.extend(
#                             [
#                                 "# TODO",
#                                 f"# read list of {return_type_name}",
#                                 "raise NotImplementedError()",
#                             ]
#                         )
#
#                 case "Vector":
#                     # TODO: handle what type is within the container
#                     # shared
#                     if return_type_name.startswith("class SharedPointer"):
#                         pass
#
#                     # dynamic
#                     else:
#                         if return_type_is_pointer:
#                             raise RuntimeError(
#                                 "Attempting to write inline vector for pointer vector"
#                             )
#                         pass
#
#                     lines.extend(["# TODO", "raise NotImplementedError()"])
#
#                 case _:
#                     raise RuntimeError(f"Unhandled container type {container_name}")
#
#             methods.append(
#                 self.get_method_string(name, lines, return_type=arrowed_return_name)
#             )
#
#         class_string = self.get_class_string(class_name, [parent], methods)
#
#         if not file_contents:
#             import_string = "from wizwalker.memory.memory_object import PropertyClass"
#             file_contents = class_string
#             sub_base_class = class_name
#
#         else:
#             file_contents += "\n\n\n" + class_string
#
#         inheritors = await self.get_direct_inheritors(class_type)
#
#         if not inheritors:
#             if dot_imports:
#                 import_string += "\nfrom . import " + ", ".join(dot_imports)
#
#             if enum_imports:
#                 import_string += "\nfrom .enums import " + ", ".join(enum_imports)
#
#             import_string += "\n\n\n"
#             file_contents = import_string + file_contents + "\n"
#
#             file_name = self.class_name_to_file_name(sub_base_class)
#             await self.create_file(file_name, file_contents)
#
#         else:
#             for inheritor in inheritors:
#                 await self.handle_class(
#                     inheritor,
#                     class_name,
#                     file_contents,
#                     import_string,
#                     sub_base_class,
#                     handled_properties,
#                     dot_imports,
#                     enum_imports,
#                     extra_imports,
#                 )
#
#     # TODO: add to enums file ignore __DEFAULT only option enums
#     #                  "m_applyNOT": {
#     #                     "type": "bool",
#     #                     "offset": 72,
#     #                     "flags": 31,
#     #                     "container": "Static",
#     #                     "dynamic": false,
#     #                     "pointer": false,
#     #                     "enum_options": {
#     #                         "__DEFAULT": "0"
#     #                     }
#     async def handle_enum(self, name: str, options: dict[str, int | str]):
#         if name in self._handled_enums:
#             return
#
#         print(f"Unhandled enum {name}")
#         self._handled_enums.append(name)
#
#     @staticmethod
#     async def get_property_info(property_type: "wizwalker.memory.type_tree.Property"):
#         name = await property_type.name()
#         offset = await property_type.offset()
#
#         return_type = await property_type.type()
#         return_type_name = await return_type.name()
#         return_type_is_pointer = await return_type.is_pointer()
#
#         container = await property_type.container()
#         container_name = await container.name()
#         container_is_dynamic = await container.is_dynamic()
#
#         enum_options = await property_type.enum_options()
#
#         return (
#             name,
#             offset,
#             return_type_name,
#             return_type_is_pointer,
#             container_name,
#             container_is_dynamic,
#             enum_options,
#         )
#
#     def clean_property_name(self, name: str) -> str:
#         # m_duelID.m_full -> m_duelID_m_full
#         name = name.replace(".", "_")
#
#         # m_id -> id
#         name = PROPERTY_NAME_PREFIX.sub("", name)
#
#         # fullPartyGroup -> full_party_group
#         name = self.decamel(name)
#
#         # Battleground -> battleground
#         name = name.lower()
#
#         return name
#
#     @staticmethod
#     def clean_class_name(name: str) -> str:
#         # class CoreObject -> CoreObject
#         name = name.replace("class ", "")
#
#         # Namespace::CoreObject -> Namespace_CoreObject
#         name = name.replace("::", "_")
#         return name
#
#     def clean_return_type(self, name: str) -> str:
#         # class SharedPointer<class CoreObject> -> class CoreObject
#         name = name.replace("class SharedPointer<", "")
#         name = name.replace(">", "")
#
#         # class CoreObject -> CoreObject
#         name = self.clean_class_name(name)
#
#         # CoreObject* -> CoreObject
#         name = name.replace("*", "")
#
#         # enum kDuelExecutionOrder -> DuelExecutionOrder
#         name = self.clean_enum_name(name)
#
#         # unsigned int -> int
#         name = name.replace("unsigned ", "")
#
#         return name
#
#     @staticmethod
#     def clean_enum_name(name: str) -> str:
#         # enum kDuelExecutionOrder -> kDuelExecutionOrder
#         name = name.replace("enum ", "")
#
#         # Duel::SigilInitiativeSwitchMode -> Duel_SigilInitiativeSwitchMode
#         name = name.replace("::", "_")
#
#         # TODO: handle this prefix
#         # # kDuelExecutionOrder -> DuelExecutionOrder
#         # name = name.lstrip("k")
#
#         return name
#
#     def class_name_to_file_name(self, name: str) -> str:
#         # NodeObject -> Node_object
#         name = self.decamel(name)
#         # Node_object -> node_object.py
#         return name.lower() + ".py"
#
#     @staticmethod
#     def decamel(name: str) -> str:
#         name = PVP_OVERRIDE.sub(_pvp_override, name)
#         return DECAMEL.sub(_decamel_replacer, name)
#
#     # TODO: this
#     async def create_enum(self):
#         pass
#
#     async def create_file(self, file_path: str | Path, content: str = None):
#         # str -> Path
#         file_path = self.target_dir / Path(file_path)
#         file_path.parent.mkdir(parents=True, exist_ok=True)
#
#         if file_path.exists():
#             print(f"Duplicate file {file_path}")
#
#             # TODO: remove debugging
#             # raise FileExistsError(f"{file_path} already exists")
#
#         file_path.touch()
#         await wizwalker.utils.run_in_executor(file_path.write_text, content)
#
#     @staticmethod
#     def get_class_string(name: str, bases: list[str], methods: list[str]) -> str:
#         class_string = f"class {name}"
#
#         if bases:
#             class_string += "("
#             class_string += ", ".join(bases)
#             class_string += ")"
#
#         class_string += ":\n"
#
#         if not methods:
#             # fallback
#             class_string += "    pass"
#
#         else:
#             class_string += "\n\n".join(methods)
#
#         # apply ending newlines elsewhere
#         return class_string
#
#     @staticmethod
#     def get_method_string(
#         name: str,
#         lines: list[str],
#         *,
#         extra_args: list[str] = None,
#         extra_kwargs: list[str] = None,
#         is_async: bool = True,
#         return_type: str = None,
#     ):
#         method_string = _CLASS_SCOPE
#
#         if is_async:
#             method_string += "async "
#
#         method_string += f"def {name}(self"
#
#         if extra_args:
#             method_string += ", "
#             method_string += ", ".join(extra_args)
#
#         if extra_kwargs:
#             method_string += ", *, "
#             method_string += ", ".join(extra_kwargs)
#
#         method_string += ")"
#
#         if return_type:
#             method_string += f" -> {return_type}"
#
#         method_string += ":\n"
#
#         method_string += _METHOD_SCOPE
#         method_string += ("\n" + _METHOD_SCOPE).join(lines)
#
#         return method_string
#
#     async def get_class_by_name(
#         self, name: str, *, remove_on_found: bool = True
#     ) -> Optional["wizwalker.memory.type_tree.Type"]:
#         res = self.type_tree.get(name)
#
#         if res:
#             if remove_on_found:
#                 del self.type_tree[name]
#
#             return await res.node_data()
#
#         return res
#
#     async def get_direct_inheritors(
#         self,
#         class_type: "wizwalker.memory.type_tree.Type",
#         *,
#         remove_on_found: bool = True,
#     ):
#         res = []
#
#         class_prop_list = await class_type.property_list()
#
#         # list so we can remove from the dict
#         for name, node in list(self.type_tree.items()):
#             data = await node.node_data()
#
#             # this is faster than get_bases
#             fields = await data.property_list()
#
#             if not fields:
#                 continue
#
#             base_fields = await fields.base_class_list()
#
#             if not base_fields:
#                 # todo: log a warning?
#                 continue
#
#             if base_fields.base_address == class_prop_list.base_address:
#                 # so we don't waste time scanning it again
#                 if remove_on_found:
#                     del self.type_tree[name]
#
#                 res.append(data)
#
#         return res
#
#     def clean_type_tree(self):
#         # list so we can edit the dict
#         for name in list(self.type_tree.keys()):
#             if any(
#                 [
#                     not name.startswith("class"),
#                     name.endswith("*"),
#                     name.startswith("class SharedPointer<"),
#                 ]
#             ):
#                 del self.type_tree[name]
