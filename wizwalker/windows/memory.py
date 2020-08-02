import logging
import struct
import threading

import pymem
import pymem.pattern

logger = logging.getLogger(__name__)


class CordReaderThread(threading.Thread):
    def __init__(self, memory_handler):
        super().__init__()
        self.memory_handler = memory_handler

    def run(self) -> None:
        process = self.memory_handler.process
        cord_struct = self.memory_handler.cord_struct_addr
        while True:
            self.memory_handler.x = process.read_float(cord_struct)
            self.memory_handler.y = process.read_float(cord_struct + 0x4)
            self.memory_handler.z = process.read_float(cord_struct + 0x8)

class MemoryHandler:
    MODULE_NAME = "WizardGraphicalClient.exe"
    TARGET_SIGNATURE = b"\x8B\x48\x2C\x8B\x50\x30\x8B\x40\x34\xEB\x2A"

    def __init__(self, pid: int):
        self.process = pymem.Pymem()
        self.process.open_process_from_id(pid)
        self.process.check_wow64()

        self.cord_thread = None
        self.cord_struct_addr = None
        self.x = None
        self.y = None
        self.z = None

    def start_cord_thread(self):
        self.cord_struct_addr = self.inject_cord_reader()
        self.cord_thread = CordReaderThread(self)
        self.cord_thread.start()

    def inject_cord_reader(self):
        """
        Injects bytecode to construct a structre for player cords and returns it
        """
        module = pymem.process.module_from_name(self.process.process_handle, self.MODULE_NAME)
        logger.debug(f"module={module}")

        target_func = pymem.pattern.pattern_scan_module(
            self.process.process_handle,
            module,
            self.TARGET_SIGNATURE,
            "x" * len(self.TARGET_SIGNATURE)
        )
        logger.debug(f"target_func={target_func} ({hex(target_func)})")

        jump_mem = self.process.allocate(1000)
        logger.debug(f"jump_mem={jump_mem} ({hex(jump_mem)})")

        player_cords_struct = self.process.allocate(12)  # 3 4 byte long cords
        logger.debug(f"player_cords_struct={player_cords_struct} ({hex(player_cords_struct)})")

        jumper_byte_code = self.get_jumper_bytecode(target_func, jump_mem)
        logger.debug(f"jumper_byte_code={jumper_byte_code}")

        return_jump_addr = target_func + len(jumper_byte_code)
        logger.debug(f"return_jump_addr={return_jump_addr} ({hex(return_jump_addr)})")

        bytecode = self.construct_byte_code(player_cords_struct, return_jump_addr, jump_mem)
        logger.debug(f"bytecode={bytecode}")

        pymem.memory.write_bytes(
            self.process.process_handle,
            jump_mem,
            bytecode,
            len(bytecode)
        )

        pymem.memory.write_bytes(
            self.process.process_handle,
            target_func,
            jumper_byte_code,
            len(jumper_byte_code)
        )

        return player_cords_struct

    @staticmethod
    def construct_byte_code(player_cords: int, return_addr: int, inject_point: int) -> bytes:
        """
        Converts an address into bytecode for us to inject

        ---
        314B0000 - 8B C8                 - mov ecx,eax
        314B0002 - 81 C1 2C030000        - add ecx,0000032C { 812 }
        314B0008 - 8B 11                 - mov edx,[ecx]
        314B000A - 83 FA 08              - cmp edx,08 { 8 }
        314B000D - 0F85 23000000         - jne 314B0036
        314B0013 - 8B C8                 - mov ecx,eax
        314B0015 - 83 C1 2C              - add ecx,2C { 44 }
        314B0018 - 8B 11                 - mov edx,[ecx]
        314B001A - 89 15 00084B31        - mov [player_cords],edx { (790.40) }
        314B0020 - 83 C1 04              - add ecx,04 { 4 }
        314B0023 - 8B 11                 - mov edx,[ecx]
        314B0025 - 89 15 04084B31        - mov [314B0804],edx { (-15.88) }
        314B002B - 83 C1 04              - add ecx,04 { 4 }
        314B002E - 8B 11                 - mov edx,[ecx]
        314B0030 - 89 15 08084B31        - mov [314B0808],edx { (-28.79) }
        314B0036 - 8B 48 2C              - mov ecx,[eax+2C]
        314B0039 - 8B 50 30              - mov edx,[eax+30]
        314B003C - E9 ACBA99CF           - jmp WizardGraphicalClient.exe+A4BAED
        """
        packed_addr = struct.pack("<i", player_cords)  # litte-endian int
        packed_addr_4 = struct.pack("<i", player_cords + 0x4)
        packed_addr_8 = struct.pack("<i", player_cords + 0x8)

        bytecode_lines = [
            b"\x8B\xC8",  # mov ecx,eax
            b"\x81\xC1\x2C\x03\x00\x00",  # add ecx,0000032C { 812 }
            b"\x8B\x11",  # mov edx,[ecx]
            # check if player
            b"\x83\xFA\x08",  # cmp edx,08 { 8 }
            b"\x0F\x85\x23\x00\x00\x00",  # jne 314B0036 (relitive jump 23 down)
            b"\x8B\xC8",  # mov ecx,eax
            b"\x83\xC1\x2C",  # add ecx,2C { 44 }
            b"\x8B\x11",  # mov edx,[ecx]
            # X
            b"\x89\x15" + packed_addr,  # mov [player_cords],edx { (790.40) }
            b"\x83\xC1\x04",  # add ecx,04 { 4 }
            b"\x8B\x11",  # mov edx,[ecx]
            # Y
            b"\x89\x15" + packed_addr_4,  # mov [314B0804],edx { (-15.88) }
            b"\x83\xC1\x04",  # add ecx,04 { 4 }
            b"\x8B\x11",  # mov edx,[ecx]
            # Z
            b"\x89\x15" + packed_addr_8,  # mov [314B0808],edx { (-28.79) }
            # origional code
            b"\x8B\x48\x2C",  # mov ecx,[eax+2C]
            b"\x8B\x50\x30",  # mov edx,[eax+30]
        ]

        bytecode = b"".join(bytecode_lines)

        relitive_return_jump = return_addr - (inject_point + len(bytecode)) - 5
        packed_relitive_return_jump = struct.pack("<i", relitive_return_jump)

        bytecode += b"\xE9" + packed_relitive_return_jump  # jmp WizardGraphicalClient.exe+A4BAED

        return bytecode

    @staticmethod
    def get_jumper_bytecode(start_jump: int, end_jump: int) -> bytes:
        """
        INJECT                           - E9 14458E01           - jmp 02730000
        WizardGraphicalClient.exe+A4BAEC - 90                    - nop
        """
        distance = end_jump - start_jump
        relitive_jump = distance - 5  # size of this line
        packed_relitive_jump = struct.pack("<i", relitive_jump)
        return b"\xE9" + packed_relitive_jump + b"\x90"
