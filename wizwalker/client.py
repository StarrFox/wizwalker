import asyncio
import struct
import warnings
from functools import cached_property
from typing import Callable, List, Optional

import pymem

from . import (
    CacheHandler,
    Keycode,
    MemoryReadError,
    ReadingEnumFailed,
    utils, ExceptionalTimeout,
)
from .constants import WIZARD_SPEED
from .memory import (
    CurrentActorBody,
    CurrentClientObject,
    CurrentDuel,
    CurrentGameStats,
    CurrentQuestPosition,
    CurrentRootWindow,
    CurrentGameClient,
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
    maybe_wait_for_any_value_with_timeout, maybe_wait_for_value_with_timeout,
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
        self.game_client = CurrentGameClient(self.hook_handler)

        self._teleport_helper = TeleportHelper(self.hook_handler)

        self._template_ids = None
        self._is_loading_addr = None
        self._world_view_window = None

        self._movement_update_address = None
        self._movement_update_original_bytes = None
        self._movement_update_patched = False

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

    # TODO: 2.0 remove the base_ here and in sub methods
    async def get_base_entity_list(self):
        """
        List of WizClientObjects currently loaded
        """
        root_client = await self.client_object.parent()
        return await root_client.children()

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

    async def get_base_entities_with_name(self, name: str):
        """
        Get entities with a name

        Args:
            name: The name to search for

        Returns:
            List of the matching entities
        """
        async def _pred(entity):
            object_template = await entity.object_template()
            return await object_template.object_name() == name

        return await self.get_base_entities_with_predicate(_pred)

    async def get_base_entities_with_display_name(self, display_name: str):
        """
        Get entities with a display name

        Args:
            display_name: The name to search for

        Returns:
            List of the matching entities
        """
        async def predicate(entity):
            mob_display_name = await entity.display_name()

            if mob_display_name is None:
                return False

            return display_name.lower() in mob_display_name.lower()

        return await self.get_base_entities_with_predicate(predicate)

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
        # if the client isn't running there isn't anything to unhook
        if not self.is_running():
            return

        await self._unpatch_movement_update()
        await self.hook_handler.close()

    async def get_template_ids(self) -> dict:
        """
        Get a dict of template ids mapped to their value
        ids are str
        """
        if self._template_ids:
            return self._template_ids

        self._template_ids = await self.cache_handler.get_template_ids()
        return self._template_ids

    async def quest_id(self) -> int:
        """
        Get the client's current quest id
        """
        registry = await self.game_client.character_registry()
        return await registry.active_quest_id()

    async def goal_id(self) -> int:
        """
        Get the client's current goal id
        """
        registry = await self.game_client.character_registry()
        return await registry.active_goal_id()

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
            move_after: bool = False,
            wait_on_inuse: bool = True,
            wait_on_inuse_timeout: float = 1.0,
            purge_on_after_unuser_fixer: bool = True,
            purge_on_after_unuser_fixer_timeout: float = 0.6,
    ):
        """
        Teleport the client

        Args:
            xyz: xyz to teleport to
            yaw: yaw to set or None to not change

        Keyword Args:
            move_after: depreciated
            wait_on_inuse: If we should wait for the update bool to be False
            wait_on_inuse_timeout: Time to wait for inuse flag to be setback
            purge_on_after_unuser_fixer: If should wait for inuse flag after and reset if not set
            purge_on_after_unuser_fixer_timeout: Time to wait for inuse flag to reset if not set
        """
        # we do this because the old teleport only required the body hook
        client_object = await self.body.parent_client_object()
        client_object_addr = await client_object.read_base_address()

        await self._teleport_object(
            client_object_addr,
            xyz,
            wait_on_inuse,
            wait_on_inuse_timeout,
            purge_on_after_unuser_fixer,
            purge_on_after_unuser_fixer_timeout,
        )

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
            wait_on_inuse: bool = True,
            wait_on_inuse_timeout: float = 1.0,
            purge_on_after_unuser_fixer: bool = True,
            purge_on_after_unuser_fixer_timeout: float = 0.6,
    ):
        """
        Teleport while playing as pet

        Args:
            xyz: xyz to teleport to
            yaw: yaw to set or None to not change

        Keyword Args:
            move_after: depreciated
            wait_on_inuse: If should wait for inuse flag to be setback
            wait_on_inuse_timeout: Time to wait for inuse flag to be setback
            purge_on_after_unuser_fixer: If should wait for inuse flag after and reset if not set
            purge_on_after_unuser_fixer_timeout: Time to wait for inuse flag to reset if not set
        """
        client_object_addr = await self.client_object.read_base_address()

        await self._teleport_object(
            client_object_addr,
            xyz,
            wait_on_inuse,
            wait_on_inuse_timeout,
            purge_on_after_unuser_fixer,
            purge_on_after_unuser_fixer_timeout,
        )

        if move_after:
            warnings.warn(DeprecationWarning("Move after will be removed in 2.0"))
            await self.send_key(Keycode.D, 0.1)

        if yaw is not None:
            await self.body.write_yaw(yaw)

    async def _teleport_object(
            self,
            object_address: int,
            xyz: XYZ,
            wait_on_inuse: bool = True,
            wait_on_inuse_timeout: float = 1.0,
            purge_on_after_unuser_fixer: bool = True,
            purge_on_after_unuser_fixer_timeout: float = 0.6,
    ):
        if not self.hook_handler._check_if_hook_active(MovementTeleportHook):
            raise RuntimeError("Movement teleport not active")

        if await self._teleport_helper.should_update():
            if not wait_on_inuse:
                raise ValueError("Tried to teleport while should update bool is set")

            await maybe_wait_for_value_with_timeout(
                self._teleport_helper.should_update,
                value=False,
                timeout=wait_on_inuse_timeout,
            )

        jes = await self._get_je_instruction_forward_backwards()

        await self._teleport_helper.write_target_object_address(object_address)
        await self._teleport_helper.write_position(xyz)
        await self._teleport_helper.write_should_update(True)

        for je in jes:
            await self.hook_handler.write_bytes(je, b"\x90" * 6)

        if purge_on_after_unuser_fixer:
            try:
                await maybe_wait_for_value_with_timeout(
                    self._teleport_helper.should_update,
                    value=False,
                    timeout=purge_on_after_unuser_fixer_timeout,
                )
            except ExceptionalTimeout:
                movement_teleport_hook = self.hook_handler._get_hook_by_type(MovementTeleportHook)
                for je, old_bytes in zip(jes, movement_teleport_hook._old_jes_bytes):
                    await self.hook_handler.write_bytes(je, old_bytes)

                await self._teleport_helper.write_should_update(False)

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

    async def camera_swap(self):
        """
        Swaps the current camera controller
        """
        if await self.game_client.is_freecam():
            await self.camera_elastic()

        else:
            await self.camera_freecam()

    async def camera_freecam(self):
        """
        Switches to the freecam camera controller
        """
        await self._patch_movement_update()

        await self.game_client.write_is_freecam(True)

        elastic = await self.game_client.elastic_camera_controller()
        free = await self.game_client.free_camera_controller()

        elastic_address = await elastic.read_base_address()
        free_address = await free.read_base_address()

        await self._switch_camera(free_address, elastic_address)

    async def camera_elastic(self):
        """
        Switches to the elastic camera controller
        """
        await self._unpatch_movement_update()

        await self.game_client.write_is_freecam(False)

        elastic = await self.game_client.elastic_camera_controller()
        free = await self.game_client.free_camera_controller()

        elastic_address = await elastic.read_base_address()
        free_address = await free.read_base_address()

        await self._switch_camera(elastic_address, free_address)

    async def _patch_movement_update(self):
        """
        Causes movement update to not run, means your character doesn't move
        """
        if self._movement_update_patched:
            return

        movement_update_address = await self._get_movement_update_address()
        self._movement_update_original_bytes = await self.hook_handler.read_bytes(movement_update_address, 3)
        # ret
        await self.hook_handler.write_bytes(movement_update_address, b"\xC3\x90\x90")

        self._movement_update_patched = True

    async def _unpatch_movement_update(self):
        if not self._movement_update_patched:
            return

        movement_update_address = await self._get_movement_update_address()
        await self.hook_handler.write_bytes(movement_update_address, self._movement_update_original_bytes)

        self._movement_update_patched = False

    async def _get_movement_update_address(self):
        if self._movement_update_address:
            return self._movement_update_address

        self._movement_update_address = await self.hook_handler.pattern_scan(
            rb"\x48\x8B\xC4\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48"
            rb"\x8D\xA8\xE8\xFD\xFF\xFF\x48\x81\xEC\xE0\x02\x00\x00\x48\xC7"
            rb"\x45\x28\xFE\xFF\xFF\xFF",
            module="WizardGraphicalClient.exe",
        )

        return self._movement_update_address

    async def _switch_camera(self, new_camera_address: int, old_camera_address: int):
        def _pack(address):
            return struct.pack("<Q", address)

        game_client_address = await self.game_client.read_base_address()
        packed_game_client_address = _pack(game_client_address)

        packed_new_camera_address = _pack(new_camera_address)
        packed_old_camera_address = _pack(old_camera_address)

        # fmt: off
        shellcode = (
                # setup
                b"\x50"  # push rax
                b"\x51"  # push rcx
                b"\x52"  # push rdx
                b"\x41\x50"  # push r8
                b"\x41\x51"  # push r9

                # call set_cam(client, new_cam, ?, cam_swap_fn)
                b"\x48\xB9" + packed_game_client_address +  # mov rcx, client_addr
                b"\x48\xBA" + packed_new_camera_address +  # mov rdx, new_cam_addr
                b"\x49\xC7\xC0\x01\x00\x00\x00"  # mov r8, 0x1
                b"\x48\x8B\x01"  # mov rax, [rcx]
                b"\x48\x8B\x80\x40\x04\x00\x00"  # mov rax, [rax+0x440]
                b"\x49\x89\xC1"  # mov r9, rax
                b"\xFF\xD0"  # call rax

                # call register_input_handlers(cam, active) [new_cam]
                b"\x48\xB9" + packed_game_client_address +  # mov rcx, client_addr
                b"\x48\xB8" + packed_new_camera_address +  # mov rax, new_cam_addr
                b"\x48\x89\xC1"  # mov rcx, rax
                b"\x48\x8B\x01"  # mov rax, [rcx]
                b"\x48\x8B\x40\x70"  # mov rax, [rax+0x70]
                b"\x48\xC7\xC2\x01\x00\x00\x00"  # mov rdx, 1
                b"\xFF\xD0"  # call rax

                # call register_input_handlers(cam, active) [old_cam]
                b"\x48\xB9" + packed_game_client_address +  # mov rcx, client_addr
                b"\x48\xB8" + packed_old_camera_address +  # mov rax, old_cam_addr
                b"\x48\x89\xC1"  # mov rcx, rax
                b"\x48\x8B\x01"  # mov rax, [rcx]
                b"\x48\x8B\x40\x70"  # mov rax, [rax+0x70]
                b"\x48\xC7\xC2\x00\x00\x00\x00"  # mov rdx, 0
                b"\xFF\xD0"  # call rax

                # cleanup
                b"\x41\x59"  # pop r9
                b"\x41\x58"  # pop r8
                b"\x5A"  # pop rdx
                b"\x59"  # pop rcx
                b"\x58"  # pop rax

                # end
                b"\xC3"  # ret
        )
        # fmt: on

        shell_ptr = await self.hook_handler.allocate(len(shellcode))
        await self.hook_handler.write_bytes(shell_ptr, shellcode)
        await self.hook_handler.start_thread(shell_ptr)
        # we can free here because start_thread waits for the thread to return
        await self.hook_handler.free(shell_ptr)
