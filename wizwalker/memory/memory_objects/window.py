from typing import Callable, Optional
from contextlib import suppress

from loguru import logger

from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import WindowFlags, WindowStyle
from .spell import DynamicGraphicalSpell
from .combat_participant import DynamicCombatParticipant
from wizwalker import AddressOutOfRange, MemoryReadError, Rectangle, utils


# TODO: Window.click
class Window(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def debug_print_ui_tree(self, depth: int = 0):
        print(
            f"{'-' * depth} [{self.name()}] {self.maybe_read_type_name()}"
        )

        for child in utils.wait_for_non_error(self.children):
            child.debug_print_ui_tree(depth + 1)

    def debug_paint(self):
        rect = self.scale_to_client()
        rect.paint_on_screen(self.hook_handler.client.window_handle)

    def scale_to_client(self):
        rect = self.window_rectangle()

        parent_rects = []
        for parent in self.get_parents():
            parent_rects.append(parent.window_rectangle())

        ui_scale = self.hook_handler.client.render_context.ui_scale()

        return rect.scale_to_client(parent_rects, ui_scale)

    def get_windows_with_type(self, type_name: str) -> list["DynamicWindow"]:
        def _pred(window):
            return window.maybe_read_type_name() == type_name

        return self.get_windows_with_predicate(_pred)

    def get_windows_with_name(self, name: str) -> list["DynamicWindow"]:
        def _pred(window):
            return window.name() == name

        return self.get_windows_with_predicate(_pred)

    def _recursive_get_windows_by_predicate(self, predicate, windows):
        with suppress(ValueError, MemoryReadError, AddressOutOfRange):
            for child in self.children():
                if predicate(child):
                    windows.append(child)

                child._recursive_get_windows_by_predicate(predicate, windows)

    def get_windows_with_predicate(
        self, predicate: Callable
    ) -> list["DynamicWindow"]:
        """
        def my_pred(window) -> bool:
            if window.name() == "friend's list":
              return True

            return False

        client.root_window.get_windows_by_predicate(my_pred)
        """
        windows = []

        # check our own children
        try:
            children = self.children()
        except (ValueError, MemoryReadError, AddressOutOfRange):
            children = []

        for child in children:
            if predicate(child):
                windows.append(child)

        for child in children:
            child._recursive_get_windows_by_predicate(predicate, windows)

        return windows

    def get_parents(self) -> list["DynamicWindow"]:
        parents = []
        current = self
        while (parent := current.parent()) is not None:
            parents.append(parent)
            current = parent

        return parents

    def get_child_by_name(self, name: str) -> "DynamicWindow":
        children = self.children()
        for child in children:
            if child.name() == name:
                return child

        raise ValueError(f"No child named {name}")

    def is_visible(self):
        return WindowFlags.visible in self.flags()

    # This is here because checking in .children slows down window filtering majorly
    def maybe_graphical_spell(
        self, *, check_type: bool = False
    ) -> Optional[DynamicGraphicalSpell]:
        if check_type:
            type_name = self.maybe_read_type_name()
            if type_name != "SpellCheckBox":
                raise ValueError(f"This object is a {type_name} not a SpellCheckBox.")

        addr = self.read_value_from_offset(952, "long long")

        if addr == 0:
            return None

        return DynamicGraphicalSpell(self.hook_handler, addr)

    # see maybe_graphical_spell
    # note: not defined
    def maybe_spell_grayed(self, *, check_type: bool = False) -> bool:
        if check_type:
            type_name = self.maybe_read_type_name()
            if type_name != "SpellCheckBox":
                raise ValueError(f"This object is a {type_name} not a SpellCheckBox")

        return self.read_value_from_offset(1024, "bool")

    # See maybe_graphical_spell
    def maybe_combat_participant(
        self, *, check_type: bool = False
    ) -> Optional[DynamicCombatParticipant]:
        if check_type:
            type_name = self.maybe_read_type_name()
            if type_name != "CombatantDataControl":
                raise ValueError(
                    f"This object is a {type_name} not a CombatantDataControl."
                )

        addr = self.read_value_from_offset(1624, "long long")

        if addr == 0:
            return None

        return DynamicCombatParticipant(self.hook_handler, addr)

    # See maybe_graphical_spell
    def maybe_text(self, *, check_type: bool = False) -> str:
        # TODO: see if all types with .text have Control prefix
        #  and if so check that they have it
        return self.read_wide_string_from_offset(584)

    def write_maybe_text(self, text: str):
        """
        Writing to this when there isn't actually a .text could crash
        """
        self.write_wide_string_to_offset(584, text)

    def name(self) -> str:
        return self.read_string_from_offset(80)

    def write_name(self, name: str):
        self.write_string_to_offset(80, name)

    def children(self) -> list["DynamicWindow"]:
        try:
            pointers = self.read_shared_vector(112)
        except (ValueError, MemoryReadError):
            logger.error("Issue while reading children vector raised to upper level")
            return []

        windows = []
        for addr in pointers:
            if addr == 0:
                logger.error("0 address while reading children")

            else:
                windows.append(DynamicWindow(self.hook_handler, addr))

        return windows

    def parent(self) -> Optional["DynamicWindow"]:
        addr = self.read_value_from_offset(136, "long long")
        # the root window has no parents
        if addr == 0:
            return None

        return DynamicWindow(self.hook_handler, addr)

    def style(self) -> WindowStyle:
        style = self.read_value_from_offset(152, "long")
        return WindowStyle(style)

    def write_style(self, style: WindowStyle):
        self.write_value_to_offset(152, int(style), "long")

    def flags(self) -> WindowFlags:
        flags = self.read_value_from_offset(156, "unsigned long")
        return WindowFlags(flags)

    def write_flags(self, flags: WindowFlags):
        self.write_value_to_offset(156, int(flags), "unsigned long")

    def window_rectangle(self) -> Rectangle:
        rect = self.read_vector(160, 4, "int")
        return Rectangle(*rect)

    def write_window_rectangle(self, window_rectangle: Rectangle):
        self.write_vector(160, tuple(window_rectangle), 4, "int")

    def target_alpha(self) -> float:
        return self.read_value_from_offset(212, "float")

    def write_target_alpha(self, target_alpha: float):
        self.write_value_to_offset(212, target_alpha, "float")

    def disabled_alpha(self) -> float:
        return self.read_value_from_offset(216, "float")

    def write_disabled_alpha(self, disabled_alpha: float):
        self.write_value_to_offset(216, disabled_alpha, "float")

    def alpha(self) -> float:
        return self.read_value_from_offset(208, "float")

    def write_alpha(self, alpha: float):
        self.write_value_to_offset(208, alpha, "float")

    # def window_style(self) -> class SharedPointer<class WindowStyle>:
    #     return self.read_value_from_offset(232, "class SharedPointer<class WindowStyle>")

    def help(self) -> str:
        return self.read_string_from_offset(248)

    def write_help(self, _help: str):
        self.write_string_to_offset(248, _help)

    def script(self) -> str:
        return self.read_string_from_offset(352)

    def write_script(self, script: str):
        self.write_string_to_offset(352, script)

    def offset(self) -> tuple:
        return self.read_vector(192, 2, "int")

    def write_offset(self, offset: tuple):
        self.write_vector(192, offset, 2, "int")

    def scale(self) -> tuple:
        return self.read_vector(200, 2)

    def write_scale(self, scale: tuple):
        self.write_vector(200, scale, 2)

    def tip(self) -> str:
        return self.read_string_from_offset(392)

    def write_tip(self, tip: str):
        self.write_string_to_offset(392, tip)

    # def bubble_list(self) -> class WindowBubble:
    #     return self.read_value_from_offset(424, "class WindowBubble")

    def parent_offset(self) -> tuple:
        return self.read_vector(176, 4, "int")

    def write_parent_offset(self, parent_offset: tuple):
        self.write_vector(176, parent_offset, 4, "int")


class DynamicWindow(DynamicMemoryObject, Window):
    pass


class CurrentRootWindow(Window):
    def read_base_address(self) -> int:
        return self.hook_handler.read_current_root_window_base()
