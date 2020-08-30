import asyncio
import re

ZONE_REGEX = re.compile(rb"\r\xf0..\x00\x00\x00\x00\x05l....([a-zA-Z/_]+)")


class PacketHookWatcher:
    def __init__(self, client, *, delay: float = 0.3):
        self.client = client
        self.memory_handler = client.memory
        self.delay = delay
        self.watching = False

        # self.packet_processer = PacketProcesser()

    def start(self):
        self.watching = True
        asyncio.create_task(self.read_task())

    def stop(self):
        self.watching = False

    async def read_task(self):
        """
        Continusly reads the packet buffer every <self.delay> seconds
        """
        # don't drop packets on cancel
        while self.watching:
            buffer = await self.memory_handler.read_packet_buffer()
            await self.process_buffer(buffer)
            await asyncio.sleep(self.delay)

    async def process_buffer(self, buffer: bytes):
        """
        Splits packets and hands them to the processer
        """
        # Todo: make this work
        # packets = buffer.split(b"\x0D\xF0")
        # for packet in packets:
        #     packet = b"\x0D\xF0" + packet
        #     try:
        #         message_name, description, parsed_params = self.packet_processer.process_packet_data(packet)
        #     except:
        #         pass
        #     else:
        #         if "zone" in message_name.lower():
        #             print(f"Zone found, {parsed_params}")

        # I can't be bothered to parse the messages
        current_zone = ZONE_REGEX.search(buffer)
        if current_zone:
            self.client.current_zone = current_zone.group(1).decode("utf-8")
