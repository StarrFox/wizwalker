import json
import sys
from collections import defaultdict
from functools import cached_property
from pathlib import Path

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
        return f"<WizWalker {self.window_handles=} {self.clients=}>"

    @cached_property
    def cache_dir(self):
        if getattr(sys, "frozen", False):
            root = Path(sys.executable).parent
        else:
            root = Path(__file__).parent.parent

        return root / "cache"

    @cached_property
    def install_location(self):
        return utils.get_wiz_install()

    @cached_property
    def wizard_messages(self):
        try:
            with (self.cache_dir / "wizard_messages.json").open() as fp:
                message_data = fp.read()
        except OSError:
            raise RuntimeError("Messages not yet cached, please run .run or .cache_data")
        else:
            return json.loads(message_data)

    @cached_property
    def template_ids(self):
        try:
            with (self.cache_dir / "template_ids.json").open() as fp:
                message_data = fp.read()
        except OSError:
            raise RuntimeError("template_ids not yet cached, please run .run or .cache_data")
        else:
            return json.loads(message_data)

    @cached_property
    def wad_cache(self):
        try:
            with (self.cache_dir / "wad_cache.data").open() as fp:
                data = fp.read()
        except OSError:
            data = None

        wad_cache = defaultdict(lambda: defaultdict(lambda: -1))

        if data:
            wad_cache_data = json.loads(data)
            wad_cache.update(wad_cache_data)

        return wad_cache

    def write_wad_cache(self):
        with (self.cache_dir / "wad_cache.data").open("w+") as fp:
            json.dump(self.wad_cache, fp)

    @cached_property
    def node_cache(self):
        try:
            with (self.cache_dir / "node_cache.data").open() as fp:
                data = fp.read()
        except OSError:
            data = None

        wad_cache = defaultdict(lambda: 0)

        if data:
            wad_cache_data = json.loads(data)
            wad_cache.update(wad_cache_data)

        return wad_cache

    def write_node_cache(self):
        with (self.cache_dir / "node_cache.data").open("w+") as fp:
            json.dump(self.node_cache, fp)

    def get_clients(self):
        self.get_handles()
        self.clients = [Client(handle) for handle in self.window_handles]

    def close(self):
        for client in self.clients:
            client.close()

    def cache_data(self):
        """Caches various file data we will need later"""
        root_wad = Wad("Root")

        self._cache_messages(root_wad)
        self._cache_template(root_wad)
        self._cache_nodes()

        self.write_wad_cache()

    def _cache_messages(self, root_wad):
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

            with (self.cache_dir / "wizard_messages.json").open("w+") as fp:
                json.dump(pharsed_messages, fp)

    def _cache_template(self, root_wad):
        template_file = {
            "TemplateManifest.xml": root_wad.get_file_info("TemplateManifest.xml")
        }

        template_file = self.check_updated(root_wad, template_file)

        if template_file:
            file_data = root_wad.get_file("TemplateManifest.xml")
            pharsed_template_ids = utils.pharse_template_id_file(file_data)
            del file_data

            with (self.cache_dir / "template_ids.json").open("w+") as fp:
                json.dump(pharsed_template_ids, fp)

    def _cache_nodes(self):
        game_data = Path(self.install_location) / "Data" / "GameData"
        all_wads = game_data.glob("*.wad")

        new_node_data = {}
        for wad_name in all_wads:
            wad_name = wad_name.name
            if not self.node_cache[wad_name]:
                logger.debug(f"Checking {wad_name} for node data")
                wad = Wad(wad_name)
                self.node_cache[wad_name] = 1

                try:
                    file_info = wad.get_file_info("pathNodeData.bin")
                    if file_info.size == 20:
                        continue

                    node_data = wad.get_file("pathNodeData.bin")
                except RuntimeError:
                    continue
                else:
                    pharsed_node_data = utils.pharse_node_data(node_data)
                    new_node_data[wad_name] = pharsed_node_data

        if new_node_data:
            node_data_json = self.cache_dir / "node_data.json"
            if node_data_json.exists():
                with node_data_json.open() as fp:
                    old_node_data = json.load(fp)

            else:
                old_node_data = {}

            old_node_data.update(new_node_data)

            with node_data_json.open("w+") as fp:
                json.dump(old_node_data, fp)

        self.write_node_cache()

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
