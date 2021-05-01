from .memory_object import MemoryObject, DynamicMemoryObject
from .enums import WindowStyle, WindowFlags


class Window(MemoryObject):
    async def read_base_address(self):
        raise NotImplementedError()

    async def name(self) -> str:
        return await self.read_string(80)

    async def write_name(self, name: str):
        await self.write_string(80, name)

    # Cannot type this as List[DynamicWindow] due to scope
    async def children(self) -> list:
        pointers = await self.read_shared_vector(112)

        windows = []
        for addr in pointers:
            windows.append(DynamicWindow(self.hook_handler, addr))

        return windows

    # async def write_children(self, children: class SharedPointer<class Window>):
    #     await self.write_value_to_offset(112, children, "class SharedPointer<class Window>")

    async def style(self) -> WindowStyle:
        style = await self.read_value_from_offset(152, "unsigned long")
        return WindowStyle(style)

    async def write_style(self, style: WindowStyle):
        await self.write_value_to_offset(152, int(style), "unsigned long")

    async def flags(self) -> WindowFlags:
        flags = await self.read_value_from_offset(156, "unsigned long")
        return WindowFlags(flags)

    async def write_flags(self, flags: WindowFlags):
        await self.write_value_to_offset(156, int(flags), "unsigned long")

    async def window(self) -> tuple:
        return await self.read_vector(160, 4, "int")

    async def write_window(self, window: tuple):
        await self.write_vector(160, window, 4, "int")

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
        return await self.read_string(248)

    async def write_help(self, _help: str):
        await self.write_string(248, _help)

    async def script(self) -> str:
        return await self.read_string(352)

    async def write_script(self, script: str):
        await self.write_string(352, script)

    async def offset(self) -> tuple:
        return await self.read_vector(192, 2, "int")

    async def write_offset(self, offset: tuple):
        await self.write_vector(192, offset, 2, "int")

    async def scale(self) -> tuple:
        return await self.read_vector(200, 2)

    async def write_scale(self, scale: tuple):
        await self.write_vector(200, scale, 2)

    async def tip(self) -> str:
        return await self.read_string(392)

    async def write_tip(self, tip: str):
        await self.write_string(392, tip)

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
