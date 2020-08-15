import json
import logging
import struct
from io import BytesIO

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
logger = logging.getLogger(__name__)


TYPE_TABLE = {
    "BYT": "b",
    "UBYT": "B",
    "SHRT": "<h",
    "USHRT": "<H",
    "INT": "<i",
    "UINT": "<I",
    "STR": "",
    "WSTR": "",
    "FLT": "<f",
    "DBL": "<d",
    "GID": "<Q",
}


class PacketProcesser:
    def __init__(self):
        self.message_structure = self.load_message_structure()

    @staticmethod
    def load_message_structure():
        json_data = ROOT_DIR / "data" / "packet_message_structure.json"

        return json.load(json_data.open())

    # Todo: comment what this does
    def process_packet_data(self, data):
        """
        Based on https://github.com/Joshsora/libki/wiki/Message-Structure
        """

        logger.debug(f"Parsing {data}")

        data_len = len(data)
        data = BytesIO(data)

        data.read(2)  # F00D header

        try:
            msg_length = struct.unpack(TYPE_TABLE["USHRT"], data.read(2))[0]
        except struct.error:
            print(f"Message len couldnt be read from: {data.read()}")
            return

        if msg_length != data_len - 2 - 2:
            logger.debug("Message inside message")
            pos = data.tell()
            real = data.read()
            next_msg_pos = real.find(b"\x0D\xF0")

            if next_msg_pos == 0:
                logger.debug(f"Message length issue {real=}")
                return

            self.process_packet_data(real[next_msg_pos:])
            data.seek(pos)

        is_control = struct.unpack(TYPE_TABLE["UBYT"], data.read(1))[0]

        if is_control:
            logger.debug("Ignoring control message")
            return

        op_code = struct.unpack(TYPE_TABLE["UBYT"], data.read(1))[0]
        data.read(2)  # undefined bytes
        service_id = struct.unpack(TYPE_TABLE["UBYT"], data.read(1))[0]

        # if service_id != 51:
        #     return

        message_id = struct.unpack(TYPE_TABLE["UBYT"], data.read(1))[0]

        logger.debug(
            f"message_len={msg_length} "
            f"service_id={service_id} "
            f"message_id={message_id} "
            f"is_control={is_control} "
            f"op_code={op_code}"
        )

        service_name, message_name, description, params = self.lookup_message_data(
            service_id, message_id
        )

        logger.debug(f"Got packet data: {service_name}: {message_name} ({description})")

        parsed_params = self.parse_params(data, params)

        return message_name, description, parsed_params

    def lookup_message_data(self, service_id: int, message_id: int):
        service_data = self.message_structure[str(service_id)]
        service_name = service_data["type"]

        message_data = service_data["messages"][str(message_id)]
        message_name = message_data["name"]
        message_description = message_data["description"]
        message_params = message_data["params"]

        return service_name, message_name, message_description, message_params

    @staticmethod
    def parse_params(data: BytesIO, params: list):
        parsed = {}
        for param in params:
            p_type = param["type"]
            p_name = param["name"]

            if p_type == "STR":
                # logger.debug("String type skipped")
                str_len = struct.unpack(TYPE_TABLE["USHRT"], data.read(2))[0]
                str_value = data.read(str_len)
                logger.debug(f"Got string param {str_len=} {str_value=}")
                parsed[p_name] = str_value
                continue

            p_format = TYPE_TABLE[p_type]
            p_size = struct.calcsize(p_format)

            logger.debug(f"{p_type=} {p_name=} {p_format=} {p_size=}")

            p_data = data.read(p_size)
            logger.debug(f"{p_data=}")

            try:
                p_value = struct.unpack(p_format, p_data)[0]

                logger.debug(f"{p_value=}")

                parsed[p_name] = p_value
            except Exception as e:
                logger.debug(f"Failed reading {p_name}")
                parsed[p_name] = "error"

        return parsed
