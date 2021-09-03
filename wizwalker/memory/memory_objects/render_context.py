from wizwalker.memory.memory_object import MemoryObject


class RenderContext(MemoryObject):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def ui_scale(self) -> float:
        return self.read_value_from_offset(152, "float")


class CurrentRenderContext(RenderContext):
    def read_base_address(self) -> int:
        return self.hook_handler.read_current_render_context_base()
