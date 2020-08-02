import sys
import time
from functools import cached_property

from wizwalker import Client, packets, utils


class WizWalker:
    """
    Represents the main program
    and handles all windows
    """
    def __init__(self):
        self.window_handles = None
        self.clients = None
        self.socket_listener = None

    @cached_property
    def install_location(self):
        return utils.get_wiz_install()

    def close(self):
        for client in self.clients:
            client.close()

    def run(self):
        # Todo: remove debugging
        import logging
        logging.getLogger("wizwalker").setLevel(logging.DEBUG)

        print("Starting wizwalker")
        print(f'Found install under "{self.install_location}"')

        self.get_handles()
        print(f"Found {len(self.window_handles)} client(s), loading")

        self.clients = [Client(handle) for handle in self.window_handles]

        for client in self.clients:
            client.memory.start_cord_thread()

        # temp stuff for demo
        old_cords = {}
        while True:
            for idx, client in enumerate(self.clients, 1):
                xyz = client.xyz
                try:
                    old = old_cords[idx]
                except KeyError:
                    old = (999, 999, 999)

                if xyz != old:
                    print(
                        f"client-{idx}: x={client.memory.x} y={client.memory.y} z={client.memory.z}"
                    )
                    old_cords[idx] = xyz

    @staticmethod
    def listen_packets():
        socket_listener = packets.SocketListener()
        packet_processer = packets.PacketProcesser()

        for packet in socket_listener.listen():
            try:
                name, description, params = packet_processer.process_packet_data(packet)
                if name in ["MSG_CLIENTMOVE", "MSG_SENDINTERACTOPTIONS", "MSG_MOVECORRECTION"]:
                    continue

                print(f"{name}: {params}")
            except TypeError:
                print("Bad packet")
            except:
                # print_exc()
                print("Ignoring exception")

    def get_handles(self):
        current_handles = utils.get_all_wizard_handles()

        if not current_handles:
            if input("No wizard101 clients running, start one? [y/n]: ").lower() == "y":
                utils.start_wiz(self.install_location)
                print("Sleeping 10 seconds then rescanning")
                time.sleep(10)

                current_handles = utils.get_all_wizard_handles()
                if not current_handles:
                    print("Critical error starting client")
                    sys.exit(1)

            else:
                print("Exiting...")
                sys.exit(0)

        self.window_handles = current_handles









