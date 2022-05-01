import asyncio
import struct
import warnings
from functools import cached_property
from typing import Callable, List, Optional

import pymem

from . import (
    CacheHandler,
    ClientClosedError,
    Keycode,
    MemoryReadError,
    ReadingEnumFailed,
    utils,
)
from .constants import WIZARD_SPEED, ntdll
from .memory import (
    CurrentActorBody,
    CurrentClientObject,
    CurrentDuel,
    CurrentGameStats,
    CurrentQuestPosition,
    CurrentRootWindow,
    DuelPhase,
    HookHandler,
    CurrentRenderContext,
    TeleportHelper,
    MovementTeleportHook,
)
from .mouse_handler import MouseHandler
from .utils import (
    XYZ,
    check_if_process_running,
    get_window_title,
    set_window_title,
    get_window_rectangle,
    wait_for_value,
)


class Client:
    """
    Represents a connected wizard client

    Args:
        window_handle: A handle to the window this client connects to
    """

    def __init__(self, window_handle: int):
        self.window_handle = window_handle

        self._pymem = pymem.Pymem()
        self._pymem.open_process_from_id(self.process_id)
        self.hook_handler = HookHandler(self._pymem, self)

        self.cache_handler = CacheHandler()
        self.mouse_handler = MouseHandler(self)

        self.stats = CurrentGameStats(self.hook_handler)
        self.body = CurrentActorBody(self.hook_handler)
        self.duel = CurrentDuel(self.hook_handler)
        self.quest_position = CurrentQuestPosition(self.hook_handler)
        self.client_object = CurrentClientObject(self.hook_handler)
        self.root_window = CurrentRootWindow(self.hook_handler)
        self.render_context = CurrentRenderContext(self.hook_handler)

        self._teleport_helper = TeleportHelper(self.hook_handler)

        self._template_ids = None
        self._is_loading_addr = None
        self._world_view_window = None

        # (pos_pointer_addr, hash_addr)
        self._position_holder_globals = None

        # for teleport
        self._je_instruction_forward_backwards = None

    def __repr__(self):
        return f"<Client {self.window_handle=} {self.process_id=}>"

    @property
    def title(self) -> str:
        """
        Get or set this window's title
        """
        return get_window_title(self.window_handle)

    @title.setter
    def title(self, window_title: str):
        set_window_title(self.window_handle, window_title)

    @property
    def is_foreground(self) -> bool:
        """
        If this client is the foreground window

        Set this to True to bring it to the foreground
        """
        return utils.get_foreground_window() == self.window_handle

    @is_foreground.setter
    def is_foreground(self, value: bool):
        if value is False:
            return

        utils.set_foreground_window(self.window_handle)

    @property
    def window_rectangle(self):
        """
        Get this client's window rectangle
        """
        return get_window_rectangle(self.window_handle)

    @cached_property
    def process_id(self) -> int:
        """
        Client's process id
        """
        return utils.get_pid_from_handle(self.window_handle)

    def is_running(self):
        """
        If this client is still running
        """
        return check_if_process_running(self._pymem.process_handle)

    async def zone_name(self) -> Optional[str]:
        """
        Client's current zone name
        """
        client_zone = await self.client_object.client_zone()

        if client_zone is not None:
            # noinspection PyBroadException
            try:
                return await client_zone.zone_name()
            except Exception:
                return None

        return None

    async def get_base_entity_list(self):
        """
        List of WizClientObjects currently loaded
        """
        root_client = await self.client_object.parent()
        return await root_client.children()

    async def get_base_entities_with_name(self, name: str):
        """
        Get entites with a name

        Args:
            name: The name to search for

        Returns:
            List of the matching entities
        """

        async def _pred(entity):
            object_template = await entity.object_template()
            return await object_template.object_name() == name

        return await self.get_base_entities_with_predicate(_pred)

    # TODO: add example
    async def get_base_entities_with_predicate(self, predicate: Callable):
        """
        Get entities with a predicate

        Args:
            predicate: Awaitable that returns True or False on if to add an entity

        Returns:
            The matching entities
        """
        entities = []

        for entity in await self.get_base_entity_list():
            if await predicate(entity):
                entities.append(entity)

        return entities

    async def get_world_view_window(self):
        """
        Get the world view window
        """
        if self._world_view_window:
            return self._world_view_window

        pos = await self.root_window.get_windows_with_name("WorldView")
        # TODO: test this claim on login screen
        # world view always exists
        self._world_view_window = pos[0]
        return self._world_view_window

    async def activate_hooks(
            self, *, wait_for_ready: bool = True, timeout: float = None
    ):
        """
        Activate all memory hooks but mouseless

        Keyword Args:
            wait_for_ready: If this should wait for hooks to be ready to use (duel exempt)
            timeout: How long to wait for hook values to be witten (None for no timeout)
        """
        await self.hook_handler.activate_all_hooks(
            wait_for_ready=wait_for_ready, timeout=timeout
        )

    async def close(self):
        """
        Closes this client; unhooking all active hooks
        """
        try:
            await self.hook_handler.close()
        except ClientClosedError:
            pass

    async def get_template_ids(self) -> dict:
        """
        Get a dict of template ids mapped to their value
        ids are str
        """
        if self._template_ids:
            return self._template_ids

        self._template_ids = await self.cache_handler.get_template_ids()
        return self._template_ids

    async def in_battle(self) -> bool:
        """
        If the client is in battle or not
        """
        try:
            duel_phase = await self.duel.duel_phase()
        except (ReadingEnumFailed, MemoryReadError):
            return False
        else:
            return duel_phase is not DuelPhase.ended

    async def is_loading(self) -> bool:
        """
        If the client is currently in a loading screen
        (does not apply to character load in)
        """
        if not self._is_loading_addr:
            mov_instruction_addr = await self.hook_handler.pattern_scan(
                b"\xC6\x05....\x00\xC6\x80.....\x48\x8B",
                module="WizardGraphicalClient.exe",
            )
            # first 2 bytes are the mov instruction and mov type (C6 05)
            rip_offset = await self.hook_handler.read_typed(
                mov_instruction_addr + 2, "int"
            )
            # 7 is the length of this instruction
            self._is_loading_addr = mov_instruction_addr + 7 + rip_offset

        # 1 -> can't move (loading) 0 -> can move (not loading)
        return await self.hook_handler.read_typed(self._is_loading_addr, "bool")

    async def is_in_dialog(self) -> bool:
        """
        If the client is in dialog
        """
        world_view = await self.get_world_view_window()
        for child in await world_view.children():
            # TODO: check if we also need to check for wndDialogMain child
            if (child_name := await child.name()) == "NPCServicesWin":
                return True

            elif child_name == "wndDialogMain":
                return True

        return False

    async def is_in_npc_range(self) -> bool:
        """
        If the client is within an npc interact range
        """
        world_view = await self.get_world_view_window()
        for child in await world_view.children():
            if await child.name() == "NPCRangeWin":
                return True

        return False

    async def backpack_space(self) -> tuple:
        """
        This client's backpack space used and max
        must be on inventory page to use
        """
        maybe_space_window = await self.root_window.get_windows_with_name(
            "inventorySpace"
        )

        if not maybe_space_window:
            # TODO: replace error
            raise ValueError("must open inventory screen to get")

        text = await maybe_space_window[0].maybe_text()
        text = text.replace("<center>", "")
        used, total = text.split("/")
        return int(used), int(total)

    async def wait_for_zone_change(
            self, name: Optional[str] = None, *, sleep_time: Optional[float] = 0.5
    ):
        """
        Wait for the client's zone to change

        Args:
            name: The name of the zone to wait to be changed from or None to read
            sleep_time: How long to sleep between reads or None to not
        """
        if name is None:
            name = await self.zone_name()

        while await self.zone_name() == name:
            await asyncio.sleep(sleep_time)

        while await self.is_loading():
            await asyncio.sleep(sleep_time)

    async def current_energy(self) -> int:
        """
        Client's current energy
        energy globe must be visible to use
        """
        maybe_energy_text = await self.root_window.get_windows_with_name("textEnergy")

        if not maybe_energy_text:
            # TODO: replace error
            raise ValueError("Energy globe not on screen")

        text = await maybe_energy_text[0].maybe_text()
        text = text.replace("<center>", "")
        text = text.replace("</center>", "")
        return int(text)

    def login(self, username: str, password: str):
        """
        Login this client

        Args:
            username: The username to login with
            password: The password to login with
        """
        utils.instance_login(self.window_handle, username, password)

    async def send_key(self, key: Keycode, seconds: float = 0):
        """
        Send a key

        Args:
            key: The Keycode to send
            seconds: How long to send it for
        """
        await utils.timed_send_key(self.window_handle, key, seconds)

    async def send_hotkey(self, modifers: List[Keycode], key: Keycode):
        """
        send a hotkey

        Args:
            modifers: The key modifers i.e CTRL, ALT
            key: The key being modified
        """
        await utils.send_hotkey(self.window_handle, modifers, key)

    async def goto(self, x: float, y: float):
        """
        Moves the player to a specific x and y

        Args:
            x: X to move to
            y: Y to move to
        """
        current_xyz = await self.body.position()
        # (40 / 100) + 1 = 1.4
        speed_multiplier = ((await self.client_object.speed_multiplier()) / 100) + 1
        target_xyz = utils.XYZ(x, y, current_xyz.z)
        distance = current_xyz - target_xyz
        move_seconds = distance / (WIZARD_SPEED * speed_multiplier)
        yaw = utils.calculate_perfect_yaw(current_xyz, target_xyz)

        await self.body.write_yaw(yaw)
        await utils.timed_send_key(self.window_handle, Keycode.W, move_seconds)

    # TODO: 2.0 remove move_after as it isn't needed anymore
    async def teleport(
            self,
            xyz: XYZ,
            yaw: float = None,
            *,
            move_after: bool = True,
            wait_on_inuse: bool = False,
    ):
        """
        Teleport the client

        Args:
            xyz: xyz to teleport to
            yaw: yaw to set or None to not change

        Keyword Args:
            move_after: depreciated
            wait_on_inuse: If we should wait for the update bool to be False
        """
        # we do this because the old teleport only required the body hook
        client_object = await self.body.parent_client_object()
        client_object_addr = await client_object.read_base_address()

        await self._teleport_object(client_object_addr, xyz, wait_on_inuse)

        if move_after:
            warnings.warn(DeprecationWarning("Move after will be removed in 2.0"))
            await self.send_key(Keycode.D, 0.1)

        if yaw is not None:
            await self.body.write_yaw(yaw)

    async def pet_teleport(
            self,
            xyz: XYZ,
            yaw: float = None,
            *,
            move_after: bool = True,
            wait_on_inuse: bool = False,
    ):
        """
        Teleport while playing as pet

        Args:
            xyz: xyz to teleport to
            yaw: yaw to set or None to not change

        Keyword Args:
            move_after: If the client's pet should rotate some to update the player model position
        """
        client_object_addr = await self.client_object.read_base_address()

        await self._teleport_object(client_object_addr, xyz, wait_on_inuse)

        if move_after:
            warnings.warn(DeprecationWarning("Move after will be removed in 2.0"))
            await self.send_key(Keycode.D, 0.1)

        if yaw is not None:
            await self.body.write_yaw(yaw)

    async def _teleport_object(self, object_address: int, xyz: XYZ, wait_on_inuse: bool = False):
        if await self._teleport_helper.should_update():
            if not wait_on_inuse:
                raise ValueError("Tried to teleport while should update bool is set")

            await wait_for_value(self._teleport_helper.should_update, True)

        jes = await self._get_je_instruction_forward_backwards()

        if not self.hook_handler._check_if_hook_active(MovementTeleportHook):
            raise RuntimeError("MOVEMENT TELEPORT NOT ACTIVE")

        await self._teleport_helper.write_target_object_address(object_address)
        await self._teleport_helper.write_position(xyz)
        await self._teleport_helper.write_should_update(True)

        for je in jes:
            await self.hook_handler.write_bytes(je, b"\x90" * 6)

    async def _get_je_instruction_forward_backwards(self):
        """
        this method returns the two je instruction addresses :)
        """
        if self._je_instruction_forward_backwards is not None:
            return self._je_instruction_forward_backwards

        movement_state_instruction_addr = await self.hook_handler.pattern_scan(
            rb"\x8B\x5F\x70\xF3",
            module="WizardGraphicalClient.exe"
        )

        self._je_instruction_forward_backwards = (
            movement_state_instruction_addr + 15,
            movement_state_instruction_addr + 24,
        )

        return self._je_instruction_forward_backwards

    async def _patch_position_holder(self, xyz: XYZ):
        """
        Patches position holder to a new xyz
        """
        position_pointer_addr, position_hash_addr = await self._get_position_holder_globals()

        packed_position_bytes = struct.pack("<fff", *xyz)
        position_hash = self._calculate_position_hash(packed_position_bytes)

        position_addr = await self.hook_handler.read_typed(position_pointer_addr, "unsigned long long")
        await self.hook_handler.write_bytes(position_addr, packed_position_bytes)
        await self.hook_handler.write_typed(position_hash_addr, position_hash, "unsigned int")

    @staticmethod
    def _calculate_position_hash(xyz_bytes: bytes):
        res = 0x811c9dc5

        for byte in xyz_bytes:
            res = (byte ^ res) * 0x1000193

        return res & 0xffffffff

    # TODO: remove
    async def _get_position_holder_globals(self):
        """
        returns: positional(pointer), hash
        """
        if self._position_holder_globals:
            return self._position_holder_globals

        player_position_func_pattern = rb"\x48\x83\xEC\x28\x48\x8D.....\x48\x8D.....\xE8....\x33\xC0\x48\x8D....." \
                                       rb"\x48\x89.....\x48\x89.....\x88.....\x89.....\xE8....\x89.....\x48\x83\xC4" \
                                       rb"\x28\xC3"

        player_position_func_addr = await self.hook_handler.pattern_scan(
            player_position_func_pattern,
            module="WizardGraphicalClient.exe"
        )

        position_pointer_offset_mov_addr = player_position_func_addr + 32
        position_pointer_offset_rip = await self.hook_handler.read_typed(
            position_pointer_offset_mov_addr + 3,
            "unsigned int"
        )
        position_pointer = position_pointer_offset_mov_addr + 7 + position_pointer_offset_rip

        self._position_holder_globals = (position_pointer, position_pointer + 12)
        return self._position_holder_globals
