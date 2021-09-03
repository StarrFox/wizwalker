from wizwalker import XYZ
from wizwalker.memory.memory_object import MemoryObject


class CurrentQuestPosition(MemoryObject):
    def read_base_address(self) -> int:
        return self.hook_handler.read_current_quest_base()

    def position(self) -> XYZ:
        return self.read_xyz(0)

    def write_position(self, position: XYZ):
        self.write_xyz(0, position)
