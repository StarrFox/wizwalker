from typing import Callable, List, Optional

from .enums import WindowFlags, WindowStyle
from .memory_object import DynamicMemoryObject, PropertyClass
from .spell import DynamicGraphicalSpell


class Window(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def debug_print_ui_tree(self, depth: int = 0):
        print(
            f"{'-' * depth} [{await self.name()}] {await self.maybe_read_type_name()}"
        )

        for child in await self.children():
            await child.debug_print_ui_tree(depth + 1)

    async def get_windows_with_type(self, type_name: str) -> List["DynamicWindow"]:
        async def _pred(window):
            return await window.maybe_read_type_name() == type_name

        return await self.get_windows_with_predicate(_pred)

    async def get_windows_with_name(self, name: str) -> List["DynamicWindow"]:
        async def _pred(window):
            return await window.name() == name

        return await self.get_windows_with_predicate(_pred)

    async def _recursive_get_windows_by_predicate(self, predicate, windows):
        for child in await self.children():
            if await predicate(child):
                windows.append(child)

            await child._recursive_get_windows_by_predicate(predicate, windows)

    async def get_windows_with_predicate(
        self, predicate: Callable
    ) -> List["DynamicWindow"]:
        """
        async def my_pred(window) -> bool:
            if await window.name() == "friend's list":
              return True

            return False

        await client.root_window.get_windows_by_predicate(my_pred)
        """
        windows = []

        # check our own children
        children = await self.children()
        for child in children:
            if await predicate(child):
                windows.append(child)

        for child in children:
            await child._recursive_get_windows_by_predicate(predicate, windows)

        return windows

    async def get_child_by_name(self, name: str) -> "DynamicWindow":
        children = await self.children()
        for child in children:
            if await child.name() == name:
                return child

        raise ValueError(f"No child named {name}")

    # This is here because checking in .children slows down window filtering majorly
    async def maybe_graphical_spell(self) -> DynamicGraphicalSpell:
        type_name = await self.maybe_read_type_name()
        if type_name != "SpellCheckBox":
            raise ValueError("This object is not a SpellCheckBox")

        addr = await self.read_value_from_offset(952, "long long")
        return DynamicGraphicalSpell(self.hook_handler, addr)

    # See above
    async def maybe_text(self) -> str:
        # TODO: see if all types with .text have Control prefix
        #  and if so check that they have it
        return await self.read_wide_string_from_offset(584)

    # TODO: add back
    # async def write_maybe_text(self, text: str):
    #     """
    #     Writing to this when there isn't actually a .text could crash
    #     """
    #     await self.write_string_to_offset(584, text)

    async def name(self) -> str:
        return await self.read_string_from_offset(80)

    async def write_name(self, name: str):
        await self.write_string_to_offset(80, name)

    async def children(self) -> List["DynamicWindow"]:
        pointers = await self.read_shared_vector(112)

        windows = []
        for addr in pointers:
            windows.append(DynamicWindow(self.hook_handler, addr))

        return windows

    # async def write_children(self, children: class SharedPointer<class Window>):
    #     await self.write_value_to_offset(112, children, "class SharedPointer<class Window>")

    async def parent(self) -> Optional["DynamicWindow"]:
        addr = await self.read_value_from_offset(136, "long long")
        # the root window has no parents
        if addr == 0:
            return None

        return DynamicWindow(self.hook_handler, addr)

    # write parent

    async def style(self) -> WindowStyle:
        style = await self.read_value_from_offset(152, "long")
        return WindowStyle(style)

    async def write_style(self, style: WindowStyle):
        await self.write_value_to_offset(152, int(style), "long")

    async def flags(self) -> WindowFlags:
        flags = await self.read_value_from_offset(156, "unsigned long")
        return WindowFlags(flags)

    async def write_flags(self, flags: WindowFlags):
        await self.write_value_to_offset(156, int(flags), "unsigned long")

    async def window_rectangle(self) -> tuple:
        return await self.read_vector(160, 4, "int")

    async def write_window_rectangle(self, window_rectangle: tuple):
        await self.write_vector(160, window_rectangle, 4, "int")

    async def target_alpha(self) -> float:
        return await self.read_value_from_offset(212, "float")

    async def write_target_alpha(self, target_alpha: float):
        await self.write_value_to_offset(212, target_alpha, "float")

    async def disabled_alpha(self) -> float:
        return await self.read_value_from_offset(216, "float")

    async def write_disabled_alpha(self, disabled_alpha: float):
        await self.write_value_to_offset(216, disabled_alpha, "float")

    async def alpha(self) -> float:
        return await self.read_value_from_offset(208, "float")

    async def write_alpha(self, alpha: float):
        await self.write_value_to_offset(208, alpha, "float")

    # async def window_style(self) -> class SharedPointer<class WindowStyle>:
    #     return await self.read_value_from_offset(232, "class SharedPointer<class WindowStyle>")
    #
    # async def write_p_window_style(self, p_window_style: class SharedPointer<class WindowStyle>):
    #     await self.write_value_to_offset(232, p_window_style, "class SharedPointer<class WindowStyle>")

    async def help(self) -> str:
        return await self.read_string_from_offset(248)

    async def write_help(self, _help: str):
        await self.write_string_to_offset(248, _help)

    async def script(self) -> str:
        return await self.read_string_from_offset(352)

    async def write_script(self, script: str):
        await self.write_string_to_offset(352, script)

    async def offset(self) -> tuple:
        return await self.read_vector(192, 2, "int")

    async def write_offset(self, offset: tuple):
        await self.write_vector(192, offset, 2, "int")

    async def scale(self) -> tuple:
        return await self.read_vector(200, 2)

    async def write_scale(self, scale: tuple):
        await self.write_vector(200, scale, 2)

    async def tip(self) -> str:
        return await self.read_string_from_offset(392)

    async def write_tip(self, tip: str):
        await self.write_string_to_offset(392, tip)

    # async def bubble_list(self) -> class WindowBubble:
    #     return await self.read_value_from_offset(424, "class WindowBubble")
    #
    # async def write__bubble_list(self, _bubble_list: class WindowBubble):
    #     await self.write_value_to_offset(424, _bubble_list, "class WindowBubble")

    async def parent_offset(self) -> tuple:
        return await self.read_vector(176, 4, "int")

    async def write_parent_offset(self, parent_offset: tuple):
        await self.write_vector(176, parent_offset, 4, "int")


class DynamicWindow(DynamicMemoryObject, Window):
    pass


class CurrentRootWindow(Window):
    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_root_window_base()
