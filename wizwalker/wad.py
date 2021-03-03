import struct
import zlib
from collections import namedtuple
from typing import Union
from pathlib import Path

import aiofiles

from .utils import executor_function, get_wiz_install

wad_file_info = namedtuple("wad_file_info", "offset, size, is_zip, crc, unzipped_size")


class WadFileInfo:
    def __init__(self, *, name, offset, size, is_zip, crc, unzipped_size):
        self.name = name
        self.offset = offset
        self.size = size
        self.is_zip = is_zip
        self.crc = crc
        self.unzipped_size = unzipped_size


# TODO: allow specifying wads not in game dir
class Wad:
    def __init__(self, name: str):
        if not name.endswith(".wad"):
            name += ".wad"

        self.name = name
        self.file_path = get_wiz_install() / "Data" / "GameData" / self.name
        if not self.file_path.exists():
            raise ValueError(f"{self.name} not found.")

        self._file_list = []
        self._refreshed_once = False
        self._open = False
        self._file_pointer = None

    def __repr__(self):
        return f"<Wad {self.name=}>"

    async def size(self) -> int:
        """
        Total size of this wad
        """
        if not self._open:
            await self.open()

        return sum(file.size for file in self._file_list)

    async def names(self):
        """
        List of all file names in this wad
        """
        if not self._open:
            await self.open()

        return [file.name for file in self._file_list]

    async def open(self):
        # noinspection PyTypeChecker
        self._file_pointer = open(self.file_path, "rb")
        await self._refresh_journal()
        self._open = True

    def close(self):
        self._file_pointer.close()
        self._open = False

    # This method runs in a thread bc it is very slow
    @executor_function
    def _refresh_journal(self):
        if self._refreshed_once:
            return

        self._refreshed_once = True

        fp = self._file_pointer

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
            name = (fp.read(name_length)).decode("utf-8")[:-1]

            self._file_list.append(
                WadFileInfo(
                    name=name,
                    offset=offset,
                    size=size,
                    is_zip=is_zip,
                    crc=crc,
                    unzipped_size=zsize,
                )
            )

    async def get_file(self, name: str) -> bytes:
        """
        Get the data contents of the named file
        """
        if not self._open:
            await self.open()

        target_file = None
        for file in self._file_list:
            if file.name == name:
                target_file = file

        if not target_file:
            raise ValueError(f"File {name} not found.")

        async with aiofiles.open(self.file_path, "rb") as fp:
            await fp.seek(target_file.offset)
            raw_data = await fp.read(target_file.size)

            if target_file.is_zip:
                try:
                    data = zlib.decompress(raw_data)
                except zlib.error:
                    data = raw_data

            else:
                data = raw_data

        return data

    async def get_file_info(self, name: str) -> wad_file_info:
        """
        Gets a WadFileInfo for a named file
        """
        if not self._open:
            await self.open()

        target_file = None
        for file in self._file_list:
            if file.name == name:
                target_file = file

        if not target_file:
            raise ValueError(f"File {name} not found.")

        return target_file

    async def unarchive(self, path: Union[Path, str]):
        if not path.exists():
            raise ValueError(f"{path} does not exist.")

        if not path.is_dir():
            raise ValueError(f"{path} is not a directory.")

        for file in self._file_list:
            dirs = file.name.split("/")
            # not a base level file
            if len(dirs) != 1:
                current = path
                for next_dir in dirs[:-1]:
                    current = current / next_dir
                    if not current.exists():
                        current.mkdir()

            file_path = path / file.name
            file_data = await self.get_file(file.name)

            async with aiofiles.open(file_path, "wb") as fp:
                await fp.write(file_data)

    @classmethod
    async def from_directory(self, path):
        """
        Create a Wad object from a directory

        Args:
            path: Path to directory to archive
        """
