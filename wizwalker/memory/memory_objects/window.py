from typing import Callable, List, Optional
from contextlib import suppress

from loguru import logger

from wizwalker.memory.memory_object import PropertyClass
from .enums import WindowFlags, WindowStyle
from .spell import AddressedGraphicalSpell
from .combat_participant import AddressedCombatParticipant
from wizwalker import AddressOutOfRange, MemoryReadError, Rectangle, utils


# TODO: Window.click
class Window(PropertyClass):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def debug_print_ui_tree(self, depth: int = 0):
        print(
            f"{'-' * depth} [{await self.name()}] {await self.maybe_read_type_name()}"
        )

        for child in await utils.wait_for_non_error(self.children):
            await child.debug_print_ui_tree(depth + 1)

    async def debug_paint(self):
        rect = await self.scale_to_client()
        rect.paint_on_screen(self.memory_reader.client.window_handle)

    async def scale_to_client(self):
        rect = await self.window_rectangle()

        parent_rects = []
        for parent in await self.get_parents():
            parent_rects.append(await parent.window_rectangle())

        ui_scale = await self.memory_reader.client.render_context.ui_scale()

        return rect.scale_to_client(parent_rects, ui_scale)

    async def get_windows_with_type(self, type_name: str) -> List["AddressedWindow"]:
        async def _pred(window):
            return await window.maybe_read_type_name() == type_name

        return await self.get_windows_with_predicate(_pred)

    async def get_windows_with_name(self, name: str) -> List["AddressedWindow"]:
        async def _pred(window):
            return await window.name() == name

        return await self.get_windows_with_predicate(_pred)

    async def _recursive_get_windows_by_predicate(self, predicate, windows):
        with suppress(ValueError, MemoryReadError, AddressOutOfRange):
            for child in await self.children():
                if await predicate(child):
                    windows.append(child)

                await child._recursive_get_windows_by_predicate(predicate, windows)

    async def get_windows_with_predicate(
        self, predicate: Callable
    ) -> List["AddressedWindow"]:
        """
        async def my_pred(window) -> bool:
            if await window.name() == "friend's list":
              return True

            return False

        await client.root_window.get_windows_by_predicate(my_pred)
        """
        windows = []

        # check our own children
        try:
            children = await self.children()
        except (ValueError, MemoryReadError, AddressOutOfRange):
            children = []

        for child in children:
            if await predicate(child):
                windows.append(child)

        for child in children:
            await child._recursive_get_windows_by_predicate(predicate, windows)

        return windows

    async def get_parents(self) -> List["AddressedWindow"]:
        parents = []
        current = self
        while (parent := await current.parent()) is not None:
            parents.append(parent)
            current = parent

        return parents

    async def get_child_by_name(self, name: str) -> "AddressedWindow":
        children = await self.children()
        for child in children:
            if await child.name() == name:
                return child

        raise ValueError(f"No child named {name}")

    async def is_visible(self):
        return WindowFlags.visible in await self.flags()

    # This is here because checking in .children slows down window filtering majorly
    async def maybe_graphical_spell(
        self, *, check_type: bool = False
    ) -> Optional[AddressedGraphicalSpell]:
        if check_type:
            type_name = await self.maybe_read_type_name()
            if type_name != "SpellCheckBox":
                raise ValueError(f"This object is a {type_name} not a SpellCheckBox.")

        addr = await self.read_value_from_offset(952, "long long")

        if addr == 0:
            return None

        return AddressedGraphicalSpell(self.memory_reader, addr)

    # see maybe_graphical_spell
    # note: not defined
    async def maybe_spell_grayed(self, *, check_type: bool = False) -> bool:
        if check_type:
            type_name = await self.maybe_read_type_name()
            if type_name != "SpellCheckBox":
                raise ValueError(f"This object is a {type_name} not a SpellCheckBox")

        return await self.read_value_from_offset(1024, "bool")

    # See maybe_graphical_spell
    async def maybe_combat_participant(
        self, *, check_type: bool = False
    ) -> Optional[AddressedCombatParticipant]:
        if check_type:
            type_name = await self.maybe_read_type_name()
            if type_name != "CombatantDataControl":
                raise ValueError(
                    f"This object is a {type_name} not a CombatantDataControl."
                )

        addr = await self.read_value_from_offset(1656, "long long")

        if addr == 0:
            return None

        return AddressedCombatParticipant(self.memory_reader, addr)

    # See maybe_graphical_spell
    async def maybe_text(self, *, check_type: bool = False) -> str:
        # TODO: see if all types with .text have Control prefix
        #  and if so check that they have it
        return await self.read_wide_string_from_offset(584)

    async def write_maybe_text(self, text: str):
        """
        Writing to this when there isn't actually a .text could crash
        """
        await self.write_wide_string_to_offset(584, text)

    async def name(self) -> str:
        return await self.read_string_from_offset(80)

    async def write_name(self, name: str):
        await self.write_string_to_offset(80, name)

    async def children(self) -> List["AddressedWindow"]:
        try:
            pointers = await self.read_shared_vector(112)
        except (ValueError, MemoryReadError):
            logger.error("Issue while reading children vector raised to upper level")
            return []

        windows = []
        for addr in pointers:
            if addr == 0:
                logger.error("0 address while reading children")

            else:
                windows.append(AddressedWindow(self.memory_reader, addr))

        return windows

    async def parent(self) -> Optional["AddressedWindow"]:
        addr = await self.read_value_from_offset(136, "long long")
        # the root window has no parents
        if addr == 0:
            return None

        return AddressedWindow(self.memory_reader, addr)

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

    async def window_rectangle(self) -> Rectangle:
        rect = await self.read_vector(160, 4, "int")
        return Rectangle(*rect)

    async def write_window_rectangle(self, window_rectangle: Rectangle):
        await self.write_vector(160, tuple(window_rectangle), 4, "int")

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

    async def parent_offset(self) -> tuple:
        return await self.read_vector(176, 4, "int")

    async def write_parent_offset(self, parent_offset: tuple):
        await self.write_vector(176, parent_offset, 4, "int")


class AddressedWindow(Window):
    pass


class CurrentRootWindow(Window):
    async def read_base_address(self) -> int:
        return await self.memory_reader.read_current_root_window_base()
