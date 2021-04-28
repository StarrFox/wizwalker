import asyncio

import wizwalker
from wizwalker.hotkey import Hotkey, Listener


class Quester:
    def __init__(self):
        self.walker = wizwalker.WizWalker()
        self.walker.get_clients()

    async def activate_hooks(self):
        for client in self.walker.clients:
            await client.activate_hooks("quest_struct", "player_struct")

    async def handle_e_pressed(self):
        for client in self.walker.clients:
            quest_xyz = await client.quest_xyz()
            await client.teleport(quest_xyz.x, quest_xyz.y, quest_xyz.z)

    async def run(self):
        await self.activate_hooks()

        quest_hotkey = Hotkey(wizwalker.Keycode.E, self.handle_e_pressed)
        quest_listener = Listener([quest_hotkey])

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
