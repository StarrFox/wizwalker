import asyncio

import wizwalker
from wizwalker.hotkey import ModifierKeys, Keycode, HotkeyListener


class Quester(wizwalker.ClientHandler):
    def __init__(self):
        super().__init__()
        self.get_new_clients()

    async def activate_hooks(self):
        for client in self.clients:
            await client.hook_handler.activate_quest_hook()
            await client.hook_handler.activate_player_hook()
            await client.hook_handler.activate_movement_teleport_hook()

    async def handle_e_pressed(self):
        for client in self.clients:
            await client.teleport(await client.quest_position.position())

    async def run(self):
        await self.activate_hooks()

        listener = HotkeyListener()
        await listener.add_hotkey(
            Keycode.Q,
            self.handle_e_pressed,
            modifiers=ModifierKeys.SHIFT | ModifierKeys.NOREPEAT,
        )

        await listener.start()

        while True:
            await asyncio.sleep(1)


async def main():
    async with Quester() as quester:
        await quester.run()


if __name__ == "__main__":
    asyncio.run(main())
