import asyncio
import functools
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
from mmap import mmap, ACCESS_READ

from wizwalker.utils import get_wiz_install, run_in_executor


@dataclass
class WadFileInfo:
    name: str
    offset: int
    size: int
    zipped_size: int
    is_zip: int
    crc: int


# TODO: implement context manager (should it and .close be async?)
class Wad:
    def __init__(self, path: Union[Path, str]):
        self.name = path.stem
        self.file_path = Path(path)

        self._file_map = {}
        self._file_pointer = None
        self._mmap = None
        self._read_lock = asyncio.Lock()

        self._refreshed_once = False

        self._size = None

    @classmethod
    def from_game_data(cls, name: str):
        """
        Get a Wad file from game installation dir

        Args:
            name: name of the wad
        """
        file_path = get_wiz_install() / "Data" / "GameData" / name
        return cls(file_path.with_suffix(".wad"))

    def __repr__(self):
        return f"<Wad {self.name=}>"

    async def size(self) -> int:
        """
        Total size of this wad
        """
        if not self._file_pointer:
            await self.open()

        if self._size:
            return self._size

        self._size = sum(file.size for file in self._file_map.values())
        return self._size

    async def names(self) -> list[str]:
        """
        List of all file names in this wad
        """
        if not self._file_pointer:
            await self.open()

        return list(self._file_map.keys())

    async def open(self):
        if self._file_pointer:
            raise RuntimeError("This Wad is already opened")

        # noinspection PyTypeChecker
        self._file_pointer = open(self.file_path, "rb")
        self._mmap = mmap(self._file_pointer.fileno(), 0, access=ACCESS_READ)
        await run_in_executor(self._refresh_journal)

    def close(self):
        self._file_pointer.close()
        self._file_pointer = None

    async def _read(self, start: int, size: int) -> bytes:
        # fmt: off
        return self._mmap[start: start + size]
        # fmt: on

    def _refresh_journal(self):
        if self._refreshed_once:
            return

        self._refreshed_once = True

        # KIWAD id string
        file_offset = 5

        # fmt: off
        version, file_num = struct.unpack(
            "<ll", self._mmap[file_offset: file_offset + 8]
        )

        file_offset += 8

        if version >= 2:
            file_offset += 1

        for _ in range(file_num):
            # no reason to use struct.calcsize
            offset, size, zipped_size, is_zip, crc, name_length = struct.unpack(
                "<lll?ll", self._mmap[file_offset: file_offset + 21]
            )

            # 21 is the size of all the data we just read
            file_offset += 21

            name: str = self._mmap[file_offset: file_offset + name_length].decode(
                "utf-8"
            )
            name = name.rstrip("\x00")

            # fmt: on

            file_offset += name_length

            self._file_map[name] = WadFileInfo(
                name, offset, size, zipped_size, is_zip, crc
            )

    async def get_file(self, name: str) -> Optional[bytes]:
        """
        Get the data contents of the named file

        Args:
            name: name of the file to get

        Returns:
            Bytes of the file or None for "unpatched" dummy files
        """
        if not self._file_pointer:
            await self.open()

        target_file = await self.get_file_info(name)

        if target_file.is_zip:
            data = await self._read(target_file.offset, target_file.zipped_size)

        else:
            data = await self._read(target_file.offset, target_file.size)

        # unpatched file
        if data[:4] == b"\x00\x00\x00\x00":
            return None

        if target_file.is_zip:
            data = await run_in_executor(zlib.decompress, data)

        return data

    async def get_file_info(self, name: str) -> WadFileInfo:
        """
        Gets a WadFileInfo for a named file

        Args:
            name: name of the file to get info on
        """
        if not self._file_pointer:
            await self.open()

        try:
            target_file = self._file_map[name]
        except KeyError:
            raise ValueError(f"File {name} not found.")

        return target_file

    async def unarchive(self, path: Union[Path, str]):
        """
        Unarchive a wad file into a directory

        Args:
            path: path to the directory to unpack the wad
        """
        path = Path(path)

        if not self._file_pointer:
            await self.open()

        await run_in_executor(self._unarchive, path)

    def _unarchive(self, path):
        with open(self.file_path, "rb") as fp:
            with mmap(fp.fileno(), 0, access=ACCESS_READ) as mm:
                for file in self._file_map.values():
                    file_path = path / file.name
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    if file.is_zip:
                        data = mm[file.offset: file.offset + file.zipped_size]

                    else:
                        data = mm[file.offset: file.offset + file.size]

                    # unpatched file
                    if data[:4] == b"\x00\x00\x00\x00":
                        file_path.touch()
                        continue

                    if file.is_zip:
                        data = zlib.decompress(data)

                    file_path.write_bytes(data)

    @classmethod
    async def from_directory(cls, path: Union[Path, str]):
        """
        Create a Wad object from a directory

        Args:
            path: Path to directory to archive
        """
        path = Path(path)

        if not path.exists():
            raise ValueError(f"{path} does not exist.")

        if not path.is_dir():
            raise ValueError(f"{path} is not a directory.")

        raise NotImplemented()
