from wizwalker.utils import XYZ
from wizwalker.memory.memory_object import PropertyClass


class ActorBody(PropertyClass):
    """
    Base class for ActorBodys
    """

    async def read_base_address(self) -> int:
        raise NotImplementedError()

    async def position(self) -> XYZ:
        """
        This body's position

        Returns:
            An XYZ representing the position
        """
        return await self.read_xyz(88)

    async def write_position(self, position: XYZ):
        """
        Write this body's position

        Args:
            position: The position to write
        """
        await self.write_xyz(88, position)

    async def pitch(self) -> float:
        """
        This body's pitch

        Returns:
            Float representing pitch
        """
        return await self.read_value_from_offset(100, "float")

    async def write_pitch(self, pitch: float):
        """
        Write this body's pitch

        Args:
            pitch: The pitch to write
        """
        await self.write_value_to_offset(100, pitch, "float")

    async def roll(self) -> float:
        """
        This body's roll

        Returns:
            Float representing roll
        """
        return await self.read_value_from_offset(104, "float")

    async def write_roll(self, roll: float):
        """
        Write this body's roll

        Args:
            roll: The roll to write
        """
        await self.write_value_to_offset(104, roll, "float")

    async def yaw(self) -> float:
        """
        The body's yaw

        Returns:
            Float representing yaw
        """
        return await self.read_value_from_offset(108, "float")

    async def write_yaw(self, yaw: float):
        """
        Write this body's yaw

        Args:
            yaw: The yaw to write
        """
        await self.write_value_to_offset(108, yaw, "float")

    async def height(self) -> float:
        """
        This body's height

        Returns:
            Float representing height
        """
        return await self.read_value_from_offset(132, "float")

    async def write_height(self, height: float):
        """
        Write this body's height

        Args:
            height: The height to write
        """
        await self.write_value_to_offset(132, height, "float")

    async def scale(self) -> float:
        """
        This body's scale

        Returns:
            Float representing scale
        """
        return await self.read_value_from_offset(112, "float")

    async def write_scale(self, scale: float):
        """
        Write this body's scale

        Args:
            scale: The scale to write
        """
        await self.write_value_to_offset(112, scale, "float")
        
    async def model_update_scheduled(self) -> bool:
        """
        If this body should have their model resynced with it's position

        Returns:
            Boolean representing state
        """
        return await self.read_value_from_offset(136, "bool")

    async def write_model_update_scheduled(self, state: bool):
        """
        Writes if this body should have their model resynced with it's position

        Args:
            state: The boolean to write
        """
        await self.write_value_to_offset(136, state, "bool")


class CurrentActorBody(ActorBody):
    """
    Actor body tied to the player hook
    """

    async def read_base_address(self) -> int:
        return await self.hook_handler.read_current_player_base()
