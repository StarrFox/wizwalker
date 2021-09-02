import asyncio
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from mmap import mmap, ACCESS_READ

from wizwalker.utils import get_wiz_install, run_in_executor


def calculate_wad_crc(data) -> int:
    return zlib.crc32(data)


@dataclass
class WadFileInfo:
    name: str
    offset: int
    size: int
    zipped_size: int
    is_zip: bool
    crc: int


class Wad:
    def __init__(self, path: Path | str):
        self.file_path = Path(path)
        self.name = self.file_path.stem

        self._file_map = {}
        self._file_pointer = None
        self._mmap = None
        self._read_lock = asyncio.Lock()

        self._data_blocks = None

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

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

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

    # fmt: off
    async def _read(self, start: int, size: int) -> bytes:
        return self._mmap[start: start + size]
    # fmt: on

    # fmt: off
    def _refresh_journal(self):
        if self._refreshed_once:
            return

        self._refreshed_once = True

        # KIWAD id string
        file_offset = 5

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

            name = self._mmap[file_offset: file_offset + name_length].decode()
            name = name.rstrip("\x00")

            file_offset += name_length

            self._file_map[name] = WadFileInfo(
                name, offset, size, zipped_size, is_zip, crc
            )
    # fmt: on

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

    async def write_file(self):
        raise NotImplementedError()

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

    async def unarchive(self, path: Path | str):
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
                        data = mm[file.offset : file.offset + file.zipped_size]

                    else:
                        data = mm[file.offset : file.offset + file.size]

                    # unpatched file
                    if data[:4] == b"\x00\x00\x00\x00":
                        file_path.touch()
                        continue

                    if file.is_zip:
                        data = zlib.decompress(data)

                    file_path.write_bytes(data)

    async def archive(self):
        raise NotImplementedError()

    def _archive(self):
        pass

    @classmethod
    async def from_directory(cls, path: Path | str, wad_name: str):
        """
        Create a Wad object from a directory

        Args:
            path: Path to directory to archive
            wad_name: Name of the wad
        """
        path = Path(path)

        if not path.is_dir():
            if not path.exists():
                raise FileNotFoundError(path)

            raise ValueError(f"{path} is not a directory.")

        # TODO: move to a different function when implemented
        journal = {}
        blocks = []
        for file in path.glob("**/*"):  # probably safe from race condition
            # sub_path = f"{file.relative_to(path)}\x00".encode("utf-8")
            sub_path = file.relative_to(path)
            is_zip = sub_path.suffix not in (
                ".mp3",
                ".ogg",
            )  # this check is probably not complete
            offset = 0  # impossible to get at this point
            data = file.read_bytes()
            size = len(data)
            if is_zip:
                data = zlib.compress(data)
                zsize = len(data)
            else:
                zsize = -1

            crc = calculate_wad_crc(data)

            journal[sub_path] = WadFileInfo(
                sub_path.name, offset, size, zsize, is_zip, crc
            )

            blocks.append(data)

        wad = cls(path)

        raise NotImplemented()


def _debug_create_wad(
    path: Path | str,
    output_path: Path | str,
    *,
    overwrite: bool = False,
    calculate_crcs: bool = True,
):
    path = Path(path)
    output_path = Path(output_path)

    # TODO: remove this debug import
    import time

    if not path.is_dir():
        if not path.exists():
            raise FileNotFoundError(path)

        raise ValueError(f"{path} is not a directory.")

    if not overwrite and output_path.exists():
        raise FileExistsError(f"{output_path} already exists.")

    journal = {}
    blocks = []

    # KIWAD + version + file_num + version 2 0x01
    journal_size = 14
    file_num = 0

    # TODO remove this
    debug_crc_total_time = 0
    for file in path.glob("**/*"):  # probably safe from race condition
        if not file.is_file():
            continue

        # sub_path = f"{file.relative_to(path)}\x00".encode("utf-8")
        sub_path = file.relative_to(path)
        # is_zip = sub_path.suffix not in (
        #     # ".mp3",
        #     ".ogg",
        # )  # this check is probably not complete

        is_zip = True
        offset = 0  # impossible to get at this point
        data = file.read_bytes()

        if calculate_crcs:
            start = time.perf_counter()
            crc = calculate_wad_crc(data)
            end = time.perf_counter()

            total_time = end - start
            debug_crc_total_time += total_time

            print(
                f"crc time = {total_time} seconds; total = {debug_crc_total_time}, {crc=} {crc.bit_length()=}"
            )

            assert crc.bit_length() <= 32

        else:
            crc = 0

        size = len(data)
        if is_zip:
            compressed_data = zlib.compress(data)

            # they still write the zipped size for optimized files
            zsize = len(compressed_data)

            # they optimize in these cases
            if zsize >= len(data):
                is_zip = False

            else:
                data = compressed_data
        else:
            zsize = -1

        journal[sub_path] = WadFileInfo(sub_path.name, offset, size, zsize, is_zip, crc)

        blocks.append(data)

        print(f"Added {sub_path} to journal")

        # size of info + size of name + null terminator
        journal_size += 21 + len(str(sub_path)) + 1
        file_num += 1

    with open(output_path, "wb+") as fp:
        fp.write(b"KIWAD")

        fp.write(struct.pack("<ll", 2, file_num))

        # version 2 thing
        fp.write(b"\x01")

        current_offset = journal_size

        for name, info in journal.items():
            print(f"Writing {name} with info {info}")
            fp.write(
                struct.pack(
                    "<lll?Ll",
                    current_offset,
                    info.size,
                    info.zipped_size,
                    info.is_zip,
                    info.crc,
                    len(str(name)) + 1,
                )
            )
            # only / paths are allowed
            fp.write(str(name).replace("\\", "/").encode() + b"\x00")

            if info.is_zip:
                current_offset += info.zipped_size

            else:
                current_offset += info.size

        for data in blocks:
            fp.write(data)
