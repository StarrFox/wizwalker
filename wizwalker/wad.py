import pathlib
import struct
import zlib
from collections import namedtuple

import aiofiles

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
        self.refreshed_once = False

    def __repr__(self):
        return f"<Wad {self.name=}>"

    async def total_size(self):
        """Total size of the files in this wad"""
        total = 0
        for file_info in self.journal.values():
            total += file_info.size

        return total

    async def refresh_journal(self):
        self.refreshed_once = True

        async with aiofiles.open(self.file_path, "rb") as fp:
            # KIWAD id string
            await fp.seek(5)
            version = struct.unpack("<l", await fp.read(4))[0]
            file_num = struct.unpack("<l", await fp.read(4))[0]

            if version >= 2:
                await fp.read(1)

            for _ in range(file_num):
                offset = struct.unpack("<l", await fp.read(4))[0]
                size = struct.unpack("<l", await fp.read(4))[0]
                zsize = struct.unpack("<l", await fp.read(4))[0]
                is_zip = struct.unpack("?", await fp.read(1))[0]
                crc = struct.unpack("<l", await fp.read(4))[0]
                name_length = struct.unpack("<l", await fp.read(4))[0]
                name = (await fp.read(name_length)).decode("utf-8")[:-1]

                self.journal[name] = wad_file_info(
                    offset=offset, size=size, is_zip=is_zip, crc=crc, unzipped_size=zsize,
                )

    async def get_file(self, name: str) -> bytes:
        """Get the data contents of the named file"""
        if not self.refreshed_once:
            await self.refresh_journal()

        target_file = self.journal.get(name)

        if not target_file:
            raise RuntimeError(f"File {name} not found.")

        async with aiofiles.open(self.file_path, "rb") as fp:
            fp.seek(target_file.offset)
            raw_data = fp.read(target_file.size)

            if target_file.is_zip:
                data = zlib.decompress(raw_data)

            else:
                data = raw_data

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
