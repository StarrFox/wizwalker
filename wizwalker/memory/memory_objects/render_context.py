from wizwalker.memory.memory_object import MemoryObject


class RenderContext(MemoryObject):
    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def ui_scale(self) -> float:
        return await self.read_value_from_offset(152, "float")


class CurrentRenderContext(RenderContext):
    async def read_base_address(self) -> int:
        return await self.memory_reader.read_current_render_context_base()
