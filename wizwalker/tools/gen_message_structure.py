"""
Generates structured json data from wizard101 message xmls

parsing functions are split for easy modification

Top level = {
    int<ServiceID>: {
        type: int<ProtocolType>,
        description: str<ProtocolDescription>,
        messages: {
            int<MessageID>: {Message obj}
        }
    }
}

Message obj = {
    name: str<_MsgName>,
    description: Optional[str]<_MsgDescription>,
    params: [{
        name: <Non _ key>,
        type: str<TYPE>
    }]
}
"""

import json
import sys
import xml.etree.ElementTree as ET

from pathlib import Path


def parse_messages_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    service_data = root.find("_ProtocolInfo").find("RECORD")
    s_id, s_data = parse_service_info(service_data)

    messages = root[1:]

    def msg_sorter(m):
        # Function to sort messages by
        return m[0].find("_MsgName").text

    parsed_msgs = {}
    for index, msg in enumerate(sorted(messages, key=msg_sorter), 1):
        # msg[0] is the RECORD element
        parsed_msgs[index] = parse_message(msg[0])

    s_data["messages"] = parsed_msgs

    return s_id, s_data


def parse_service_info(data):
    service_id = int(data.find("ServiceID").text)
    service_type = data.find("ProtocolType").text
    service_description = data.find("ProtocolDescription").text

    res = {
        "type": service_type,
        "description": service_description
    }

    return service_id, res


def parse_message(data):
    msg_name = data.find("_MsgName").text
    msg_description = data.find("_MsgDescription").text

    params = []

    for child in data:
        # Message meta info starts with _
        if not child.tag.startswith("_"):
            params.append(
                {
                    "name": child.tag,
                    "type": child.get("TYPE")
                }
            )

    res = {
        "name": msg_name,
        "description": msg_description,
        "params": params
    }

    return res


def main():
    target_dir = Path(input("Path to messages dir: "))

    if not target_dir.exists():
        print("Messages dir does not exist")
        sys.exit(1)

    parsed = {}

    for message_file in target_dir.iterdir():
        print(f"Parsing {message_file}")
        s_id, data = parse_messages_file(message_file)
        parsed[s_id] = data

    with open("../data/packet_message_structure.json", "w+") as fp:
        json.dump(parsed, fp, indent=4)


if __name__ == "__main__":
    main()
