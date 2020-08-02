# Based on algorithms written by amBro

"""
Generates json data for item ids
{"id": "template.xml", ...}
"""

import io
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT_DIR = Path(__file__).parent


def read_bind(filename: str):
    with open(filename, "rb") as fp:
        data = fp.read()

    if not data.startswith(b"BINd"):
        raise Exception("Bruh moment")

    return zlib.decompress(data[0xD:])


def parse_template_list(data):
    total_size = len(data)
    data = io.BytesIO(data)

    data.seek(0x24)

    out = {}
    while data.tell() < total_size:
        size = ord(data.read(1)) // 2

        string = data.read(size).decode()
        data.read(8)  # unknown bytes

        # Little endian int
        entry_id = struct.unpack("<i", data.read(4))[0]

        data.read(0x10)  # next entry

        out[entry_id] = string

    return out


def main():
    raw_xml = ROOT_DIR / "TemplateManifest.xml"

    if not raw_xml.exists():
        print("TemplateManifest not found")
        sys.exit(1)

    uncompressed = read_bind(raw_xml)
    out_data = parse_template_list(uncompressed)

    with open("template_ids.json", "w+") as fp:
        json.dump(out_data, fp, indent=4)


if __name__ == "__main__":
    main()
