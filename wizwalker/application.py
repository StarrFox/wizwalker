import json
from collections import defaultdict
from functools import cached_property

from loguru import logger

from wizwalker import packets, utils
from .client import Client
from .wad import Wad


class WizWalker:
    """
    Represents the main program
    and handles all windows
    """

    def __init__(self):
        self.window_handles = []
        self.clients = []
        self.socket_listener = None

    def __repr__(self):
        return f"WizWalker {self.window_handles=} {self.clients=}"

    @cached_property
    def install_location(self):
        return utils.get_wiz_install()

    @cached_property
    def wad_cache(self):
        try:
            with open("wad_cache.data", "r+") as fp:
                data = fp.read()
        except OSError:
            data = None

        wad_cache = defaultdict(lambda: defaultdict(lambda: -1))

        if data:
            wad_cache_data = json.loads(data)
            wad_cache.update(wad_cache_data)

        return wad_cache

    def write_wad_cache(self):
        with open("wad_cache.data", "w+") as fp:
            json.dump(self.wad_cache, fp)

    def get_clients(self):
        self.get_handles()
        self.clients = [Client(handle) for handle in self.window_handles]

    def close(self):
        for client in self.clients:
            client.close()

    def cache_data(self):
        """Caches various file data we will need later"""
        root_wad = Wad("Root")
        message_files = {
            k: v
            for k, v in root_wad.journal.items()
            if "Messages" in k and k.endswith(".xml")
        }

        message_files = self.check_updated(root_wad, message_files)

        if message_files:
            pharsed_messages = {}
            for message_file in message_files:
                file_data = root_wad.get_file(message_file)
                logger.debug(f"pharsing {message_file}")

                # They messed up one of their xml files so I have to fix it for them
                if message_file == "WizardMessages2.xml":
                    temp = file_data.decode()
                    temp = temp.replace(
                        '<LastMatchStatus TYPE="INT"><LastMatchStatus>',
                        '<LastMatchStatus TYPE="INT"></LastMatchStatus>',
                    )
                    file_data = temp.encode()
                    del temp

                pharsed_messages.update(utils.pharse_message_file(file_data))
                del file_data

            with open("wizard_messages.json", "w+") as fp:
                json.dump(pharsed_messages, fp)

        template_file = {
            "TemplateManifest.xml": root_wad.get_file_info("TemplateManifest.xml")
        }

        template_file = self.check_updated(root_wad, template_file)

        if template_file:
            file_data = root_wad.get_file("TemplateManifest.xml")
            pharsed_template_ids = utils.pharse_template_id_file(file_data)
            del file_data

            with open("template_ids.json", "w+") as fp:
                json.dump(pharsed_template_ids, fp)

        self.write_wad_cache()

    def check_updated(self, wad_file: Wad, files: dict):
        """Checks if some wad files have changed since we last accessed them"""
        res = []

        for file_name, file_info in files.items():
            if self.wad_cache[wad_file.name][file_name] != file_info.size:
                logger.debug(
                    f"{file_name} has updated. old: {self.wad_cache[wad_file.name][file_name]} new: {file_info.size}"
                )
                res.append(file_name)
                self.wad_cache[wad_file.name][file_name] = file_info.size

            else:
                logger.debug(f"{file_name} has not updated from {file_info.size}")

        return res

    def run(self):
        # Todo: remove debugging
        import logging

        logging.getLogger("wizwalker").setLevel(logging.DEBUG)

        print("Starting wizwalker")
        print(f'Found install under "{self.install_location}"')

        self.get_clients()
        self.cache_data()

    @staticmethod
    def listen_packets():
        socket_listener = packets.SocketListener()
        packet_processer = packets.PacketProcesser()

        for packet in socket_listener.listen():
            try:
                name, description, params = packet_processer.process_packet_data(packet)
                if name in [
                    "MSG_CLIENTMOVE",
                    "MSG_SENDINTERACTOPTIONS",
                    "MSG_MOVECORRECTION",
                ]:
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
            raise RuntimeError("No handles found")

        self.window_handles = current_handles
