import winim
import strformat
import deques
import os
import posix

{.experimental: "caseStmtMacros".}
import fusion/matching

proc read[T](address: ByteAddress, t: typedesc[T]): T = cast[ptr T](address)[]
proc write[T](address: ByteAddress, v: T) = cast[ptr T](address)[] = v

#proc write(address: ByteAddress, v: Iterable[byte]) =
#  var offset = 0
#  for b in v:
#    cast[ptr byte](address + offset)[] = b
#    inc offset

#proc readBytes(address: ByteAddress, length: uint): seq[byte] =
#  for i in 0 ..< length:
#    let cur_c = read(address + i.int, byte)
#    result.add(cur_c)

proc getModuleSize(module: HMODULE): int32 =
  var modinfo: MODULEINFO
  GetModuleInformation(GetCurrentProcess(), module, modinfo, sizeof(MODULEINFO).int32)
  result = modinfo.SizeOfImage

const ww_mem_size: int32 = 0xFFFF
var
  ww_mem_handle: HANDLE = 0
  ww_mem_pointer: pointer = nil

proc cleanup_shared_memory() =
  if ww_mem_pointer != nil:
    UnmapViewOfFile(ww_mem_pointer)
    ww_mem_pointer = nil

  if ww_mem_handle != 0:
    CloseHandle(ww_mem_handle)
    ww_mem_handle = 0

proc init_shared_memory(name: string): bool = 
  result = true
  if ww_mem_handle == 0:
    ww_mem_handle = CreateFileMapping(
      INVALID_HANDLE_VALUE,
      nil,
      PAGE_READWRITE,
      0,
      ww_mem_size,
      name
    )

    if ww_mem_handle == 0:
      echo "Could not create file mapping object"
      echo GetLastError()
      sleep(5000)
      return false

    echo &"Created a shared memory segment with the name {name}"

  if ww_mem_pointer == nil:
    ww_mem_pointer = MapViewOfFile(
      ww_mem_handle,
      FILE_MAP_ALL_ACCESS,
      0,
      0,
      ww_mem_size
    )

    if ww_mem_pointer == nil:
      cleanup_shared_memory()
      echo "Could not map view into shared memory"
      sleep(5000)
      return false

const
  guard_status_client = 'c'
  guard_status_server = 's'
  guard_status_locked = '*'
  guard_status_value_ready = 'r'

  memory_operation_read = 'r'
  memory_operation_write = 'w'

template writeWWGuard(c: char) = cast[ptr char](ww_mem_pointer)[] = c
template readWWGuard(): char = cast[ptr char](ww_mem_pointer)[]

template readWWMemOperation(): char = cast[ptr char](cast[ByteAddress](ww_mem_pointer) + 1)[]

template readWWMemOpAddr(): ByteAddress = cast[ptr ByteAddress](cast[ByteAddress](ww_mem_pointer) + 2)[]
template readWWMemOpSize(): uint32 = cast[ptr uint32](cast[ByteAddress](ww_mem_pointer) + 10)[]

template with_ww_guard(body) =
  writeWWGuard(guard_status_locked)
  body
  writeWWGuard(guard_status_value_ready)

template with_protect(address, size, body: untyped) =
  var oldprotect: uint32
  if VirtualProtect(cast[LPVOID](address), size_t(size), 4.DWORD, cast[PDWORD](addr oldprotect)) == 0:
    echo "VirtualProtect failed"
  else:
    copyMem(
      cast[pointer](address),
      cast[pointer]((cast[ByteAddress](ww_mem_pointer) + 14)),
      size
    )
    body
  discard VirtualProtect(cast[LPVOID](address), size_t(size), oldprotect.DWORD, cast[PDWORD](addr oldprotect))  

proc mainThread() =
  AllocConsole()
  discard stdout.reopen("CONOUT$", fmWrite)
  echo "Nimland entered"

  let base_addr = GetModuleHandle("WizardGraphicalClient.exe")
  echo "WizardGraphicalClient.exe: 0x" & baseAddr.toHex() & "\n"
  echo "Module size: " & $getModuleSize(base_addr)

  let mapping_name = &"Local\\WizWalker{GetCurrentProcessId()}"

  if not init_shared_memory(mapping_name):
    return

  echo &"Buffer view can be found at {cast[ByteAddress](ww_mem_pointer).toHex()}"

  cast[ptr char](ww_mem_pointer)[] = guard_status_client
  while true:
    #echo read_ww_guard()
    let guard = readWWGuard()
    if guard == guard_status_server:
      #echo "LOCKED"
      let mem_op = readWWMemOperation()
      case mem_op
      of memory_operation_read:
        withWWGuard:
          let
            address = readWWMemOpAddr()
            size = readWWMemOpSize()
          echo &"r {address.toHex()} {size}"
          withProtect(address, size):
            copyMem(
              cast[pointer]((cast[ByteAddress](ww_mem_pointer) + 1)),
              cast[pointer](address),
              size
            )
      of memory_operation_write:
        withWWGuard:
          let
            address = readWWMemOpAddr()
            size = readWWMemOpSize()
          echo &"w {address.toHex()} {size}"

          withProtect(address, size):
            copyMem(
              cast[pointer](address),
              cast[pointer]((cast[ByteAddress](ww_mem_pointer) + 14)),
              size
            )
      else:
        echo &"Invalid memory operation: {mem_op}"
    else:
      #echo guard
      #sleep(0)
      discard usleep(50)
      #discard

  cleanup_shared_memory()
  echo "Cleaned up shared memory"

proc NimMain() {.cdecl, importc.}

proc DllMain(h_module: HINSTANCE, reason_for_call: DWORD, lp_reserved: LPVOID): WINBOOL {.exportc, dynlib, stdcall.} =
  case reason_for_call:
    of DLL_PROCESS_ATTACH:
      NimMain()
      CloseHandle(
        CreateThread(
          cast[LPSECURITY_ATTRIBUTES](nil),
          0.SIZE_T,
          cast[LPTHREAD_START_ROUTINE](mainThread),
          cast[LPVOID](nil),
          0.DWORD,
          cast[LPDWORD](nil)
        )
      )
    of DLL_PROCESS_DETACH:
      cleanup_shared_memory()
    else:
      discard

  return TRUE
