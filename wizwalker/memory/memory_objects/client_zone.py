from wizwalker.memory.memory_object import PropertyClass, DynamicMemoryObject


class ClientZone(PropertyClass):
    """
    Base class for ClientZones
    """

    def read_base_address(self) -> int:
        raise NotImplementedError()

    def zone_id(self) -> int:
        """
        This client zone's zone id
        """
        return self.read_value_from_offset(72, "long long")

    def write_zone_id(self, zone_id: int):
        """
        Write this client zone's zone id

        Args:
            zone_id: The zone id to write
        """
        self.write_value_to_offset(72, zone_id, "long long")

    def zone_name(self) -> str:
        """
        This client zone's zone name
        """
        return self.read_string_from_offset(88)

    def write_zone_name(self, zone_name: str):
        """
        Write this client zone's zone name

        Args:
            zone_name: The zone name to write
        """
        self.write_string_to_offset(88, zone_name)


class DynamicClientZone(DynamicMemoryObject, ClientZone):
    """
    Dynamic client zone that can take an address
    """

    pass
