import asyncio
import contextlib
from typing import List

from loguru import logger

import wizwalker
from wizwalker import Keycode
from wizwalker.combat import CombatHandler


class WizWalkerScriptCombatHandler(CombatHandler):
    def __init__(
        self,
        client: "wizwalker.Client",
        combat_actions: List["wizwalker.cli.wizwalker_script.CombatAction"],
    ):
        super().__init__(client)
        self.combat_actions = combat_actions

        self.action_position = 0

    async def handle_round(self):
        if len(self.combat_actions) - 1 > self.action_position:
            self.action_position = 0

        action = self.combat_actions[self.action_position]

        # TODO: python 3.10 replace with match-case
        if action.action_type == "enemy":
            await self.enemy_action(action)

        elif action.action_type == "ally":
            await self.ally_action(action)

        elif action.action_type == "card":
            await self.card_action(action)

        else:
            await self.notarget_action(action)

    async def enemy_action(self, action):
        card = action.source
        if action.enchant:
            res = await self.try_cast(action.enchant, on_card=card)

            # couldn't enchant
            if not action.maybe_enchant and res is False:
                await self.pass_button()
                return False

        target_param = action.param
        mobs = await self.get_all_monster_members()

        target = await self.get_target(mobs, target_param)

        # this should never happen
        if target == "self":
            raise RuntimeError("Cannot use self as enemy target")

        await self.try_cast(card, on_mob=target, check_enchanted=bool(action.enchant))

    async def ally_action(self, action):
        card = action.source
        if action.enchant:
            res = await self.try_cast(action.enchant, on_card=card)

            # couldn't enchant
            if not action.maybe_enchant and res is False:
                await self.pass_button()
                return

        target_param = action.param
        mobs = await self.get_all_player_members()

        target = await self.get_target(mobs, target_param)

        if target == "self":
            target = await self.get_client_member()

        await self.try_cast(card, on_mob=target, check_enchanted=bool(action.enchant))

    async def card_action(self, action):
        await self.try_cast(action.source, on_card=action.param)

    async def notarget_action(self, action):
        card = action.source
        if action.enchant:
            res = await self.try_cast(action.enchant, on_card=card)

            # couldn't enchant
            if not action.maybe_enchant and res is False:
                await self.pass_button()
                return

        await self.try_cast(card, check_enchanted=bool(action.enchant))

    @staticmethod
    async def get_target(members: list, target_param):
        target = None

        # TODO: python3.10 replace with match-case
        if target_param == "first":
            target = members[0]

        elif target_param == "second":
            target = members[1]

        elif target_param == "third":
            target = members[2]

        elif target_param == "forth":
            target = members[3]

        elif target_param == "self":
            target = "self"

        elif target_param.isnumeric():
            for member in members:
                if await member.template_id() == int(target_param):
                    target = member

            if target is None:
                raise RuntimeError(f"No member with id {target_param}")

        else:
            for member in members:
                if await member.name() == target_param:
                    target = member

            if target is None:
                raise RuntimeError(f"No mobs with name {target_param}")

        return target

    async def try_cast(
        self,
        name: str,
        *,
        on_mob: str = None,
        on_card: str = None,
        on_client: bool = False,
        check_enchanted: bool = False,
    ):
        try:
            if check_enchanted:
                card = await self.get_enchanted_card_named(name)
            else:
                card = await self.get_card_named(name)

            if on_mob:
                target = await self.get_member_named(on_mob)
                await card.cast(target)

            elif on_card:
                target = await self.get_card_named(on_card)
                await card.cast(target)

            elif on_client:
                target = await self.get_client_member()
                await card.cast(target)

            else:
                await card.cast(None)

            return True

        except ValueError:
            return False

    async def get_enchanted_card_named(self, name: str):
        cards = await self.get_cards()

        for card in cards:
            if (
                name.lower() == (await card.name()).lower()
                and await card.is_enchanted()
            ):
                return card

        raise ValueError(f"Couldn't find a card named {name}")


async def do_dialog_forever(client: "wizwalker.Client", sleep_time: float = None):
    with contextlib.suppress(asyncio.CancelledError):
        while True:
            if await client.is_in_dialog():
                await client.send_key(Keycode.SPACEBAR)

            await asyncio.sleep(sleep_time)


async def do_commands(
    script: "wizwalker.cli.WizWalkerScript", client: "wizwalker.Client"
) -> bool:
    for command in script.loop.commands:
        command_type = command.command_type

        # TODO: python 3.10 replace with match-case
        if command_type == "move":
            steps_name = command.param

            steps = None
            for move_steps in script.move_steps:
                if move_steps.name == steps_name:
                    steps = move_steps

            if steps is None:
                raise RuntimeError(f"Move with undefined steps {steps_name}.")

            for step in steps.steps:
                current_zone = await client.zone_name()
                await client.goto(*step)
                await asyncio.sleep(1)

                if await client.is_loading():
                    await client.wait_for_zone_change(current_zone)

                if await client.in_battle():
                    await WizWalkerScriptCombatHandler(
                        client, script.battle
                    ).handle_combat()

        elif command_type == "npc":
            if await client.is_in_npc_range():
                await client.send_key(Keycode.X)

            else:
                raise RuntimeError("No npc in range.")

        elif command_type == "stop":
            return False


async def do_loop(script: "wizwalker.cli.WizWalkerScript", client: "wizwalker.Client"):
    loop = script.loop

    dialog_task = asyncio.create_task(do_dialog_forever(client, 1))

    if loop.iterations:
        for _ in range(loop.iterations):
            res = await do_commands(script, client)

            if res is False:
                raise RuntimeError("Cannot use stop command with iteration loop")

    else:
        while True:
            res = await do_commands(script, client)

            if res is False:
                break

    dialog_task.cancel()
    await dialog_task


async def run_script(
    walker: "wizwalker.WizWalker", script: "wizwalker.cli.WizWalkerScript"
):
    clients = walker.get_new_clients()

    try:
        hook_tasks = []

        for client in clients:
            hook_tasks.append(asyncio.create_task(client.activate_hooks()))
            hook_tasks.append(
                asyncio.create_task(client.mouse_handler.activate_mouseless())
            )

        await asyncio.gather(*hook_tasks)

        client_tasks = []

        # we want them all to be hooked before starting the loop
        for client in clients:
            client_tasks.append(asyncio.create_task(do_loop(script, client)))

        await asyncio.gather(*client_tasks)

    finally:
        await walker.close()
