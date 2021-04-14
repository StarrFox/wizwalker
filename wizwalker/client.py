import asyncio
import ctypes.wintypes
from functools import cached_property
from typing import Optional

from . import Keycode, utils
from .windows import MemoryHandler

from .constants import user32


WIZARD_SPEED = 580


class Client:
    """
    Represents a connected wizard client

    Args:
        window_handle: A handle to the window this client connects to
    """

    def __init__(self, window_handle: int):
        self.window_handle = window_handle
        self._memory = MemoryHandler(self.process_id)

        self.click_lock = None

    def __repr__(self):
        return f"<Client {self.window_handle=} {self.process_id=}>"

    async def close(self):
        """
        Closes this client; unhooking all active hooks
        """
        await self._memory.close()

    @cached_property
    def process_id(self) -> int:
        """
        This client's PID

        Returns:
            The pid
        """
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(self.window_handle, ctypes.byref(pid))
        return pid.value

    async def send_key(self, key: Keycode, seconds: float):
        await utils.timed_send_key(self.window_handle, key, seconds)

    async def click(
        self,
        x: int,
        y: int,
        *,
        right_click: bool = False,
        sleep_duration: float = 0.0,
        use_post: bool = False,
    ):
        """
        Send a click to a certain x and y
        x and y positions are relative to the top left corner of the screen

        Args:
            x: x to click at
            y: y to click at
            right_click: If the click should be a right click
            sleep_duration: How long to sleep between messages
            use_post: If PostMessage should be used instead of SendMessage
        """
        # prevent multiple clicks from happening at the same time
        if right_click:
            button_down_message = 0x204
        else:
            button_down_message = 0x201

        if use_post:
            send_method = user32.PostMessageW
        else:
            send_method = user32.SendMessageW

        if self.click_lock is None:
            self.click_lock = asyncio.Lock()

        async with self.click_lock:
            await self.set_mouse_position(x, y)
            # mouse button down
            send_method(self.window_handle, button_down_message, 1, 0)
            if sleep_duration > 0:
                await asyncio.sleep(sleep_duration)
            # mouse button up
            send_method(self.window_handle, button_down_message + 1, 0, 0)

    def login(self, username: str, password: str):
        """
        Login to a client that is at the login screen

        Args:
            username: The username to login with
            password: The password to login with
        """
        utils.instance_login(self.window_handle, username, password)

    def get_hooks(self) -> list:
        """
        return a list of hook_names from the underlying MemoryHandler

        Returns:
            A list of avalible hooks
        """
        return self._memory.hook_functs().keys()

    async def activate_hooks(self, *hook_names: Optional[str]):
        """
        Activate a number of hooks or pass None/no args to activate all

        Args:
            hook_names: The hooks to activate

        Examples:
            .. code-block:: py

                # activates player_struct and player_stat_struct
                activate_hooks("player_struct", "player_stat_struct")

                # activates all hooks
                activate_hooks()

        """
        if not hook_names:
            await self._memory.hook_all()

        else:
            for hook_name in hook_names:
                hook = getattr(self._memory, "hook_" + hook_name, None)
                if not hook:
                    raise ValueError(f"{hook_name} is not a valid hook")

                await hook()

    async def goto(
        self,
        x: float,
        y: float,
        *,
        speed_multiplier: float = 1.0,
        use_nodes: bool = False,
    ):
        """
        Moves the player to a specific x and y

        Args:
            x: X to move to
            y: Y to move to
            speed_multiplier: Multiplier for speed (for mounts) i.e. 1.4 for 40%
            use_nodes: If node date should be used, currently WIP
        """
        if use_nodes is False:
            await self._to_point(x, y, speed_multiplier)
        else:
            raise NotImplemented("Node data not implemented")

    async def _to_point(self, x, y, speed_multiplier=1.0):
        current_xyz = await self.xyz()
        target_xyz = utils.XYZ(x, y, current_xyz.z)
        distance = current_xyz - target_xyz
        move_seconds = distance / (WIZARD_SPEED * speed_multiplier)
        yaw = current_xyz.yaw(target_xyz)

        await self.set_yaw(yaw)
        await utils.timed_send_key(self.window_handle, Keycode.W, move_seconds)

    async def set_mouse_position(
        self,
        x: int,
        y: int,
        *,
        convert_from_client: bool = True,
        use_post: bool = False,
    ):
        """
        Set's the mouse position to a certain x y relative to the
        top left corner of the client

        Args:
            x: x to set
            y: y to set
            convert_from_client: If the position should be converted from client to screen
            use_post: If PostMessage should be used instead of SendMessage
        """
        if use_post:
            send_method = user32.PostMessageW
        else:
            send_method = user32.SendMessageW

        if convert_from_client:
            point = ctypes.wintypes.tagPOINT(x, y)

            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-clienttoscreen
            if user32.ClientToScreen(self.window_handle, ctypes.byref(point)) == 0:
                raise RuntimeError("Client to screen conversion failed")

            # same point structure is overwritten by ClientToScreen; these are also ints and not
            # c_longs for some reason?
            x = point.x
            y = point.y

        res = await self._memory.write_mouse_position(x, y)
        # position doesn't matter here; sending mouse move
        # mouse move is here so that items are highlighted
        send_method(self.window_handle, 0x200, 0, 0)
        return res

    async def teleport(
        self, x: float = None, y: float = None, z: float = None, yaw: float = None
    ) -> bool:
        """
        Teleport the player to a set x, y, z

        Args:
            x: X to teleport to or None to not change
            y: Y to teleport to or None to not change
            z: Z to teleport to or None to not change
            yaw: yaw to set or None to not change

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            True if telelporting succseeded, False otherwise
        """
        res = await self.set_xyz(x=x, y=y, z=z)

        if yaw is not None:
            res = res and await self.set_yaw(yaw)

        return res

    async def xyz(self) -> Optional[utils.XYZ]:
        """
        Player xyz

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            XYZ namedtuple or None if hooked function hasn't run yet
        """
        return await self._memory.read_xyz()

    async def set_xyz(self, x: float, y: float, z: float):
        """
        Set the player xyz

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            XYZ namedtuple or None if hooked function hasn't run yet
        """
        return await self._memory.set_xyz(x=x, y=y, z=z)

    async def yaw(self) -> Optional[float]:
        """
        Player yaw

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            yaw float or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_yaw()

    async def set_yaw(self, yaw: float) -> bool:
        """
        Set the player yaw

        Raises:
            RuntimeError: player_struct hook not active

        Return:
            True if value was set, False otherwise
        """
        return await self._memory.set_player_yaw(yaw)

    async def roll(self) -> Optional[float]:
        """
        Player roll

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            roll float or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_roll()

    async def set_roll(self, roll: float) -> bool:
        """
        Set the player roll

        Raises:
            RuntimeError: player_struct hook not active

        Return:
            True if value was set, False otherwise
        """
        return await self._memory.set_player_roll(roll)

    async def pitch(self) -> Optional[float]:
        """
        Player pitch

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            pitch float or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_pitch()

    async def set_pitch(self, pitch: float) -> bool:
        """
        Set the player pitch

        Raises:
            RuntimeError: player_struct hook not active

        Return:
            True if value was set, False otherwise
        """
        return await self._memory.set_player_roll(pitch)

    async def scale(self) -> Optional[float]:
        """
        Player scale

        Raises:
            RuntimeError: player_struct hook not active

        Returns:
            scale float or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_scale()

    async def set_scale(self, scale: float) -> bool:
        """
        Set the player scale

        Raises:
            RuntimeError: player_struct hook not active

        Return:
            True if value was set, False otherwise
        """
        return await self._memory.set_player_scale(scale)

    async def quest_xyz(self) -> Optional[utils.XYZ]:
        """
        Quest xyz

        Raises:
            RuntimeError: quest_struct hook not active

        Return:
            XYZ namedtuple or None if hooked function hasn't run yet
        """
        return await self._memory.read_quest_xyz()

    async def move_lock(self) -> Optional[bool]:
        """
        Player move lock; weither or not the player is locked
        in combat/dialog

        Raises:
            RuntimeError: move_lock hook not active

        Return:
            move look bool or None if the function has not run yet
        """
        return await self._memory.read_move_lock()

    async def health(self) -> Optional[int]:
        """
        Player health

        Raises:
            RuntimeError: player_stat_struct hook not active

        Return:
            health int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_health()

    async def mana(self) -> Optional[int]:
        """
        Player mana

        Raises:
            RuntimeError: player_stat_struct hook not active

        Return:
            mana int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_mana()

    async def energy(self) -> Optional[int]:
        """
        Player energy

        Raises:
            RuntimeError: player_stat_struct hook not active

        Return:
            energy int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_energy()

    async def potions(self) -> Optional[int]:
        """
        Player full potions

        Raises:
            RuntimeError: player_stat_struct hook not active

        Return:
            # of potions int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_potions()

    async def potions_alt(self) -> Optional[int]:
        """
        Player full potions (alternative)

        Raises:
            RuntimeError: potion hook not active

        Return:
            # of potions int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_potions_alt()

    async def gold(self) -> Optional[int]:
        """
        Player gold

        Raises:
            RuntimeError: player_stat_struct hook not active

        Return:
            gold int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_gold()

    async def backpack_space_used(self) -> Optional[int]:
        """
        Player backpack used space

        Raises:
            RuntimeError: backpack_struct hook not active

        Return:
            used backpack space int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_backpack_used()

    async def backpack_space_total(self) -> Optional[int]:
        """
        Player backpack total space

        Raises:
            RuntimeError: backpack_struct hook not active

        Return:
            backpack total space int or None if hooked function hasn't run yet
        """
        return await self._memory.read_player_backpack_total()
