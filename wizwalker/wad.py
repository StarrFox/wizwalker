import zlib
import struct
import pathlib
from collections import namedtuple

from .utils import get_wiz_install

wad_file_info = namedtuple("wad_file_info", "offset, size, is_zip, crc, unzipped_size")


class Wad:
    def __init__(self, name: str):
        self.name = name
        self.file_path = pathlib.Path(get_wiz_install()) / "Data" / "GameData" / self.name
        if not self.file_path.exists():
            raise RuntimeError(f"{self.name} not found.")

        self.journal = {}
        self.refresh_journal()

    def refresh_journal(self):
        fp = self.file_path.open("rb")
        # KIWAD id string
        fp.seek(5)
        version = struct.unpack("<l", fp.read(4))[0]
        file_num = struct.unpack("<l", fp.read(4))[0]

        if version >= 2:
            fp.read(1)

        for _ in range(file_num):
            offset = struct.unpack("<l", fp.read(4))[0]
            size = struct.unpack("<l", fp.read(4))[0]
            zsize = struct.unpack("<l", fp.read(4))[0]
            is_zip = struct.unpack("?", fp.read(1))[0]
            crc = struct.unpack("<l", fp.read(4))[0]
            name_length = struct.unpack("<l", fp.read(4))[0]
            name = fp.read(name_length).decode("utf-8")[:-1]

            self.journal[name] = wad_file_info(
                offset=offset,
                size=size,
                is_zip=is_zip,
                crc=crc,
                unzipped_size=zsize,
            )

        fp.close()
        del fp

    def get_file(self, name: str) -> bytes:
        """Get the data contents of the named file"""
        target_file = self.journal.get(name)

        if not target_file:
            raise RuntimeError(f"File {name} not found.")

        fp = self.file_path.open("rb")

        fp.seek(target_file.offset)
        raw_data = fp.read(target_file.size)

        if target_file.is_zip:
            data = zlib.decompress(raw_data)

        else:
            data = raw_data

        return data
