from typing import Optional

from wizwalker import XYZ
from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject
from .game_stats import DynamicGameStats
from .game_object_template import DynamicWizGameObjectTemplate
from .behavior_instance import DynamicBehaviorInstance
from .client_zone import DynamicClientZone


class ClientObject(PropertyClass):
    """
    Base class for ClientObjects
    """

    def read_base_address(self) -> int:
        raise NotImplementedError()

    # TODO: test if this actually active behaviors
    def inactive_behaviors(self) -> list[DynamicBehaviorInstance]:
        """
        This client object's inactive behaviors

        Returns:
            List of DynamicBehaviorInstace
        """
        behaviors = []
        for addr in self.read_shared_vector(224):
            if addr != 0:
                behaviors.append(DynamicBehaviorInstance(self.hook_handler, addr))

        return behaviors

    # convenience method
    def object_name(self) -> Optional[str]:
        """
        This client object's object name
        """
        object_template = self.object_template()
        if object_template is not None:
            return object_template.object_name()

        return None

    # note: not defined
    def parent(self) -> Optional["DynamicClientObject"]:
        """
        This client object's parent or None if it is the root client object

        Returns:
            DynamicClientObject
        """
        addr = self.read_value_from_offset(208, "long long")

        if addr == 0:
            return None

        return DynamicClientObject(self.hook_handler, addr)

    # note: not defined
    def children(self) -> list["DynamicClientObject"]:
        """
        This client object's child client objects

        Returns:
            List of DynamicClientObject
        """
        children = []
        for addr in self.read_shared_vector(384):
            children.append(DynamicClientObject(self.hook_handler, addr))

        return children

    # note: not defined
    def client_zone(self) -> Optional["DynamicClientZone"]:
        """
        This client object's client zone or None

        Returns:
            DynamicClientZone
        """
        addr = self.read_value_from_offset(304, "long long")

        if addr == 0:
            return None

        return DynamicClientZone(self.hook_handler, addr)

    # note: not defined
    def object_template(self) -> Optional[DynamicWizGameObjectTemplate]:
        """
        This client object's template object

        Returns:
            DynamicWizGameObjectTemplate
        """
        addr = self.read_value_from_offset(88, "long long")

        if addr == 0:
            return None

        return DynamicWizGameObjectTemplate(self.hook_handler, addr)

    def global_id_full(self) -> int:
        """
        This client object's global id
        """
        return self.read_value_from_offset(72, "unsigned long long")

    def write_global_id_full(self, global_id_full: int):
        """
        Write this client object's global id

        Args:
            global_id_full: The global id to write
        """
        self.write_value_to_offset(72, global_id_full, "unsigned long long")

    def perm_id(self) -> int:
        """
        This client object's perm id
        """
        return self.read_value_from_offset(80, "unsigned long long")

    def write_perm_id(self, perm_id: int):
        """
        Write this client object's perm id

        Args:
            perm_id: The perm id to write
        """
        self.write_value_to_offset(80, perm_id, "unsigned __int64")

    def location(self) -> XYZ:
        """
        This client object's location

        Returns:
            An XYZ representing the client object's location
        """
        return self.read_xyz(168)

    def write_location(self, location: XYZ):
        """
        Write this client object's location

        Notes:
            This seems to have no effect

        Args:
            location: The location to write
        """
        self.write_xyz(168, location)

    # TODO: check what order these are in and document it
    def orientation(self) -> tuple:
        """
        This client object's orientation
        """
        return self.read_vector(180)

    def write_orientation(self, orientation: tuple):
        """
        Write this client object's orientation

        Args:
            orientation: The orientation to write
        """
        self.write_vector(180, orientation)

    def scale(self) -> float:
        """
        This client object's scale
        """
        return self.read_value_from_offset(196, "float")

    def write_scale(self, scale: float):
        """
        Write this client object's scale

        Args:
            scale: The scale to write
        """
        self.write_value_to_offset(196, scale, "float")

    def template_id_full(self) -> int:
        """
        This client object's template id
        """
        return self.read_value_from_offset(96, "unsigned long long")

    def write_template_id_full(self, template_id_full: int):
        """
        Write this client object's template id

        Args:
            template_id_full: The template id to write
        """
        self.write_value_to_offset(96, template_id_full, "unsigned long long")

    def debug_name(self) -> str:
        """
        This client object's debug name

        Notes:
            This seems to always be empty; object_name is more reliable
        """
        return self.read_string_from_offset(104)

    def write_debug_name(self, debug_name: str):
        """
        Write this client's debug name

        Args:
            debug_name: The debug name to write
        """
        self.write_string_to_offset(104, debug_name)

    def display_key(self) -> str:
        """
        This client's display key
        """
        return self.read_string_from_offset(136)

    def write_display_key(self, display_key: str):
        """
        Write this client's display key

        Args:
            display_key: The display key to write
        """
        self.write_string_to_offset(136, display_key)

    def zone_tag_id(self) -> int:
        """
        This client object's zone tag id
        """
        return self.read_value_from_offset(344, "unsigned int")

    def write_zone_tag_id(self, zone_tag_id: int):
        """
        Write this client object's zone tag id

        Args:
            zone_tag_id: The zone tag id to write
        """
        self.write_value_to_offset(344, zone_tag_id, "unsigned int")

    def speed_multiplier(self) -> int:
        """
        This client object's speed multiplier
        """
        return self.read_value_from_offset(192, "short")

    def write_speed_multiplier(self, speed_multiplier: int):
        """
        Write this client object's speed multiplier

        Args:
            speed_multiplier: The speed multiplier to write
        """
        self.write_value_to_offset(192, speed_multiplier, "short")

    def mobile_id(self) -> int:
        """
        This client object's mobile id
        """
        return self.read_value_from_offset(194, "unsigned short")

    def write_mobile_id(self, mobile_id: int):
        """
        Write this client object's mobile id

        Args:
            mobile_id: The mobile id to write
        """
        self.write_value_to_offset(194, mobile_id, "unsigned short")

    def character_id(self) -> int:
        """
        This client object's character id
        """
        return self.read_value_from_offset(440, "unsigned long long")

    def write_character_id(self, character_id: int):
        """
        Write this client object's character id

        Args:
            character_id: The character id to write
        """
        self.write_value_to_offset(440, character_id, "unsigned long long")

    def game_stats(self) -> Optional[DynamicGameStats]:
        """
        This client object's game stats or None if doesn't have them

        Returns:
            DynamicGameStats
        """
        addr = self.read_value_from_offset(544, "long long")

        if addr == 0:
            return None

        return DynamicGameStats(self.hook_handler, addr)


class CurrentClientObject(ClientObject):
    """
    Client object tied to the client hook
    """

    def read_base_address(self) -> int:
        return self.hook_handler.read_current_client_base()


class DynamicClientObject(DynamicMemoryObject, ClientObject):
    """
    Dynamic client object that can take an address
    """

    pass
