import pathlib
import struct
import zlib
from collections import namedtuple

from .utils import get_wiz_install

wad_file_info = namedtuple("wad_file_info", "offset, size, is_zip, crc, unzipped_size")


class Wad:
    def __init__(self, name: str):
        if not name.endswith(".wad"):
            name += ".wad"

        self.name = name
        self.file_path = (
            pathlib.Path(get_wiz_install()) / "Data" / "GameData" / self.name
        )
        if not self.file_path.exists():
            raise RuntimeError(f"{self.name} not found.")

        self.journal = {}
        self.refresh_journal()

    def __repr__(self):
        return f"<Wad {self.name=} {self.total_size=}>"

    @property
    def total_size(self):
        """Total size of the files in this wad"""
        total = 0
        for file_info in self.journal.values():
            total += file_info.size

        return total

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
                offset=offset, size=size, is_zip=is_zip, crc=crc, unzipped_size=zsize,
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

        fp.close()
        del fp

        return data

    def get_file_info(self, name: str) -> wad_file_info:
        """
        Gets a wad_file_info for a file
        this is the same as journal[name]
        """
        try:
            file_info = self.journal[name]
        except KeyError:
            raise RuntimeError(f"File {name} not found")
        else:
            return file_info
