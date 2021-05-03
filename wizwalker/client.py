from functools import cached_property
from typing import List

import pymem

from . import (
    CacheHandler,
    Keycode,
    MemoryReadError,
    NotInCombat,
    ReadingEnumFailed,
    utils,
)
from .memory import (
    DuelPhase,
    HookHandler,
    CurrentGameStats,
    CurrentActorBody,
    CurrentDuel,
    CurrentQuestPosition,
    CurrentClientObject,
    CurrentRootWindow,
)

from .constants import WIZARD_SPEED
from .utils import XYZ, check_if_process_running
from .combat import Card
from .mouse_handler import MouseHandler


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
        self.hook_handler = HookHandler(self._pymem)

        # TODO: somehow reference the WizWalker's handler
        self.cache_handler = CacheHandler()

        self.mouse_handler = MouseHandler(self)

        self._template_ids = None

    def __repr__(self):
        return f"<Client {self.window_handle=} {self.process_id=}>"

    def is_running(self):
        return check_if_process_running(self._pymem.process_handle)

    async def close(self):
        """
        Closes this client; unhooking all active hooks
        """
        # if the client isn't running there isn't anything to unhook
        if not self.is_running():
            return

        await self.hook_handler.close()

    @cached_property
    def process_id(self) -> int:
        """
        Client's process id
        """
        return utils.get_pid_from_handle(self.window_handle)

    @cached_property
    def stats(self) -> CurrentGameStats:
        """
        Client's game stats struct
        """
        return CurrentGameStats(self.hook_handler)

    @cached_property
    def body(self) -> CurrentActorBody:
        """
        Client's actor body struct
        """
        return CurrentActorBody(self.hook_handler)

    @cached_property
    def duel(self) -> CurrentDuel:
        """
        Client's duel struct
        """
        return CurrentDuel(self.hook_handler)

    @cached_property
    def quest_position(self) -> CurrentQuestPosition:
        """
        Client's quest position struct
        """
        return CurrentQuestPosition(self.hook_handler)

    @cached_property
    def client_object(self) -> CurrentClientObject:
        """
        Client's current client object; name is pretty confusing
        """
        return CurrentClientObject(self.hook_handler)

    @cached_property
    def root_window(self) -> CurrentRootWindow:
        """
        Client's current root window
        """
        return CurrentRootWindow(self.hook_handler)

    async def get_template_ids(self) -> dict:
        """
        Get a dict of template ids mapped to their value
        ids are str
        """
        if self._template_ids:
            return self._template_ids

        self._template_ids = await self.cache_handler.get_template_ids()
        return self._template_ids

    async def get_cards(self) -> List[Card]:
        """
        Get the client's current cards
        """
        if not await self.in_battle():
            raise NotInCombat("Must be in combat to get cards")

        character_id = await self.client_object.character_id()

        client_participant = None
        for partipant in await self.duel.participant_list():
            # owner id is 2 more than character id for some reason
            if await partipant.owner_id_full() == character_id + 2:
                client_participant = partipant
                break

        if client_participant is None:
            raise RuntimeError("Somehow the client is not a member of the current duel")

        client_hand = await client_participant.hand()
        client_spells = await client_hand.spell_list()

        # TODO: position is incorrect
        cards = []
        hand_position = 0
        for spell in client_spells:
            spell_template_id = await spell.template_id()
            spell_name = await self.get_filename_from_template_id(spell_template_id)
            cards.append(Card(spell_name, hand_position, spell))
            hand_position += 1

        return cards

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

    async def activate_hooks(self):
        """
        Activate all memory hooks but mouseless
        """
        await self.hook_handler.activate_all_hooks()

    def login(self, username: str, password: str):
        """
        Login to a client that is at the login screen

        Args:
            username: The username to login with
            password: The password to login with
        """
        utils.instance_login(self.window_handle, username, password)

    async def send_key(self, key: Keycode, seconds: float = 0.5):
        await utils.timed_send_key(self.window_handle, key, seconds)

    async def goto(
        self, x: float, y: float, *, speed_multiplier: float = 1.0,
    ):
        """
        Moves the player to a specific x and y

        Args:
            x: X to move to
            y: Y to move to
            speed_multiplier: Multiplier for speed (for mounts) i.e. 1.4 for 40%
        """
        current_xyz = await self.body.position()
        target_xyz = utils.XYZ(x, y, current_xyz.z)
        distance = current_xyz - target_xyz
        move_seconds = distance / (WIZARD_SPEED * speed_multiplier)
        yaw = utils.calculate_perfect_yaw(current_xyz, target_xyz)

        await self.body.write_yaw(yaw)
        await utils.timed_send_key(self.window_handle, Keycode.W, move_seconds)

    async def teleport(self, xyz: XYZ, yaw: int = None):
        """
        Teleport the client

        Args:
            xyz: xyz to teleport to
            yaw: yaw to set or None to not change

        Raises:
            RuntimeError: player hook not active
        """
        await self.body.write_position(xyz)

        if yaw is not None:
            await self.body.write_yaw(yaw)
