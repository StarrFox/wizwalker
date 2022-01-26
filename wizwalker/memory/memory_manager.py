import asyncio
import mmap
import struct
import os
from pathlib import Path

import pymem

from wizwalker import utils

# There should only be one manager per client
class MemoryManager:
    def __init__(self):
        print("Created a new memory manager") # TODO: Remove/replace this debug output

    async def read(self, addr, size):
        pass

    async def write(self, addr, size):
        pass

_GUARD_STATUS_CLIENT = ord("c")
_GUARD_STATUS_SERVER = ord("s")
_GUARD_STATUS_LOCKED = ord("*")
_GUARD_STATUS_VALUE_READY = ord("r")

_MEMORY_OPERATION_READ = ord("r")
_MEMORY_OPERATION_WRITE = ord("w")

_pack_uint32 = struct.Struct('<I').pack
_pack_uint64 = struct.Struct('<Q').pack

class SharedMemoryManager(MemoryManager):
    def __init__(self, window_handle, process):
        super().__init__()
        self._mem_path = f"Local\\WizWalker{utils.get_pid_from_handle(window_handle)}"
        self._shm = None
        self._buff_size = 0xFFFE # real size minus one to make space for guard
        self._process = process
        self._open_shm()

    def _inject_adapter(self):
        # Taken from pymem and modified to work
        path = str(Path(os.path.realpath(__file__)).parent.absolute()) + "/wizwalker_adapter.dll" # TODO: Don't do this
        filepath = os.path.abspath(path).replace("\\", "/").encode("ascii")
        filepath_address = pymem.ressources.kernel32.VirtualAllocEx(
            self._process.process_handle,
            0,
            len(filepath),
            pymem.ressources.structure.MEMORY_STATE.MEM_COMMIT.value | pymem.ressources.structure.MEMORY_STATE.MEM_RESERVE.value,
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READWRITE.value
        )
        pymem.ressources.kernel32.WriteProcessMemory(self._process.process_handle, filepath_address, filepath, len(filepath), None)
        kernel32_handle = pymem.ressources.kernel32.GetModuleHandleW("kernel32.dll")
        load_library_a_address = pymem.ressources.kernel32.GetProcAddress(kernel32_handle, b"LoadLibraryA")
        thread_h = pymem.ressources.kernel32.CreateRemoteThread(
            self._process.process_handle, None, 0, load_library_a_address, filepath_address, 0, None
        )
        pymem.ressources.kernel32.WaitForSingleObject(thread_h, -1)
        pymem.ressources.kernel32.VirtualFreeEx(
            self._process.process_handle, filepath_address, len(filepath), pymem.ressources.structure.MEMORY_STATE.MEM_RELEASE.value
        )

    def _open_shm(self):
        if not self._shm:
            self._inject_adapter()
            self._shm = mmap.mmap(0, self._buff_size + 1, self._mem_path) # re-add the guard byte

    async def _wait_for_guard(self, g: int):
        while self._shm[0] != g:
            #await asyncio.sleep(0)
            pass

    async def _acquire_lock(self):
        await self._wait_for_guard(_GUARD_STATUS_CLIENT)
        self._shm[0] = _GUARD_STATUS_LOCKED

    async def read(self, addr, size):
        res = bytearray()
        
        while size > 0:
            await self._acquire_lock()

            self._shm[1] = _MEMORY_OPERATION_READ
            self._shm[2:10] = _pack_uint64(addr)
            self._shm[10:14] = _pack_uint32(min(self._buff_size - 14, size))

            self._shm[0] = _GUARD_STATUS_SERVER
            await self._wait_for_guard(_GUARD_STATUS_VALUE_READY)

            self._shm[0] = _GUARD_STATUS_LOCKED
            res += self._shm[1:1+size]
            self._shm[0] = _GUARD_STATUS_CLIENT

            size -= self._buff_size - 14

        return res

    async def write(self, addr, data):
        size = len(data)
        offset = 0
        while size > 0:
            await self._acquire_lock()

            chunk_size = min(self._buff_size - 14, size)
            size -= chunk_size

            self._shm[1] = _MEMORY_OPERATION_WRITE
            self._shm[2:10] = _pack_uint64(addr + offset)
            self._shm[10:14] = _pack_uint32(chunk_size)
            self._shm[14:14+chunk_size] = data[offset:offset+chunk_size]

            self._shm[0] = _GUARD_STATUS_SERVER
            await self._wait_for_guard(_GUARD_STATUS_VALUE_READY)

            self._shm[0] = _GUARD_STATUS_CLIENT

            offset += chunk_size
