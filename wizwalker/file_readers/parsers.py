import io
import struct
import zlib

from wizwalker import XYZ


def parse_template_id_file(file_data: bytes) -> dict:
    """
    Pharse a template id file's data
    """
    if not file_data.startswith(b"BINd"):
        raise RuntimeError("No BINd id string")

    data = zlib.decompress(file_data[0xD:])

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


def parse_node_data(file_data: bytes) -> dict:
    """
    Converts data into a dict of node nums to points
    """
    entry_start = b"\xFE\xDB\xAE\x04"

    node_data = {}
    # no nodes
    if len(file_data) == 20:
        return node_data

    # header
    file_data = file_data[20:]

    last_start = 0
    while file_data:
        start = file_data.find(entry_start, last_start)
        if start == -1:
            break

        # fmt: off
        entry = file_data[start: start + 48 + 2]

        cords_data = entry[16: 16 + (4 * 3)]
        x = struct.unpack("<f", cords_data[0:4])[0]
        y = struct.unpack("<f", cords_data[4:8])[0]
        z = struct.unpack("<f", cords_data[8:12])[0]

        node_num = entry[48: 48 + 2]
        unpacked_num = struct.unpack("<H", node_num)[0]
        # fmt: on

        node_data[unpacked_num] = (x, y, z)

    return node_data


# implemented from https://github.com/PeechezNCreem/navwiz/
# this licence covers the below function
# Boost Software License - Version 1.0 - August 17th, 2003
#
# Permission is hereby granted, free of charge, to any person or organization
# obtaining a copy of the software and accompanying documentation covered by
# this license (the "Software") to use, reproduce, display, distribute,
# execute, and transmit the Software, and to prepare derivative works of the
# Software, and to permit third-parties to whom the Software is furnished to
# do so, all subject to the following:
#
# The copyright notices in the Software and this entire statement, including
# the above license grant, this restriction and the following disclaimer,
# must be included in all copies of the Software, in whole or in part, and
# all derivative works of the Software, unless such copies or derivative
# works are solely in the form of machine-executable object code generated by
# a source language processor.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
# SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
# FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
def parse_nav_data(file_data: bytes):
    file_data = file_data[2:]

    vertex_count_bytes = file_data[:4]
    file_data = file_data[4:]

    vertex_count = struct.unpack("<i", vertex_count_bytes)[0]

    vertices = []
    for idx in range(vertex_count):
        position_bytes = file_data[:12]
        file_data = file_data[12:]

        x, y, z = struct.unpack("<fff", position_bytes)
        vertices.append(XYZ(x, y, z))

        vertex_index_bytes = file_data[:2]
        file_data = file_data[2:]

        vertex_index = struct.unpack("<h", vertex_index_bytes)[0]

        if vertex_index != idx:
            raise RuntimeError(
                f"vertex index doesnt match expected: {idx} got: {vertex_index}"
            )

    edge_count_bytes = file_data[:4]
    file_data = file_data[4:]

    edge_count = struct.unpack("<i", edge_count_bytes)[0]

    edges = []
    for idx in range(edge_count):
        start_stop_bytes = file_data[:4]
        file_data = file_data[4:]

        start, stop = struct.unpack("<hh", start_stop_bytes)

        edges.append((start, stop))

    return vertices, edges