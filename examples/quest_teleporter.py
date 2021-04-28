import asyncio

import wizwalker
from wizwalker.hotkey import Hotkey, Listener, ModifierKeys


class Quester:
    def __init__(self):
        self.walker = wizwalker.WizWalker()
        self.walker.get_new_clients()

    async def activate_hooks(self):
        for client in self.walker.clients:
            await client.hook_handler.activate_quest_hook()
            await client.hook_handler.activate_player_hook()

    async def handle_e_pressed(self):
        for client in self.walker.clients:
            await client.teleport(await client.player_quest_position.position())

    async def run(self):
        await self.activate_hooks()

        quest_hotkey = Hotkey(
            wizwalker.Keycode.Q, self.handle_e_pressed, modifiers=ModifierKeys.SHIFT
        )
        quest_listener = Listener(quest_hotkey)

        while True:
            await quest_listener.listen()

    async def close(self):
        await self.walker.close()


if __name__ == "__main__":
    quester = Quester()
    try:
        asyncio.run(quester.run())
    except KeyboardInterrupt:
        print("Exiting")
        asyncio.run(quester.close())
