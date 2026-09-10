"""Execute the module's emitted x86 patch; fixtures contain no game assets."""
from pathlib import Path
import re
import struct

import pytest
from lupa import LuaRuntime
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
    UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP,
    UC_X86_REG_ESP, UC_X86_REG_EFLAGS)

ROOT = Path(__file__).resolve().parents[1]
SITE, DATA, CAVE, STACK = 0x401000, 0x600000, 0x700000, 0x800000


def fixture():
    # Settings-loader instruction sequence with relocated, synthetic globals.
    return (b'\xa1' + struct.pack('<I', DATA + 0x7c)
        + bytes.fromhex('56 55 6a 10 68') + struct.pack('<I', DATA + 0x4000)
        + b'\xa3' + struct.pack('<I', DATA + 0x80)
        + b'\xa3' + struct.pack('<I', DATA + 0x3170) + b'\xe8'
        + bytes.fromhex('b8 50 00 00 00 a3') + struct.pack('<I', DATA+0x78)
        + b'\xa3' + struct.pack('<I', DATA+0x74) + bytes.fromhex('b8 55 00 00 00 c7 05')
        + struct.pack('<I', DATA+0x70) + bytes.fromhex('5a 00 00 00 a3')
        + struct.pack('<I', DATA+0x7c) + b'\xa3' + struct.pack('<I', DATA+0x80)
        + bytes.fromhex('c7 05') + struct.pack('<I',DATA+0x3170) + bytes.fromhex('64 00 00 00'))


def install(code=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    blob = code if code is not None else fixture()
    patches = []
    def scan(pattern):
        regex = b''.join(b'.' if p == '?' else re.escape(bytes([int(p, 16)]))
                         for p in pattern.split())
        match = re.search(regex, blob, re.DOTALL)
        if not match:
            raise ValueError('AOB not found')
        return SITE + match.start()
    def insert(address, size, table):
        def flatten(t):
            for v in t.values():
                if isinstance(v, int):
                    yield from bytes([v]) if 0 <= v <= 255 else struct.pack('<I', v)
                else:
                    yield from flatten(v)
        patches.append((address, size, bytes(flatten(table))))
    lua.globals().core = lua.table_from({
        'AOBScan': scan,
        'readInteger': lambda a: struct.unpack_from('<I', blob, a-SITE)[0],
        'insertCode': insert,
    })
    module = lua.execute((ROOT / 'startup-sfx-volume.lua').read_text())
    module.enable()
    return patches


@pytest.mark.parametrize('fx', [0, 1, 50, 80, 99, 100])
@pytest.mark.parametrize('speech', [0, 37, 100])
@pytest.mark.parametrize('path', [0, 1])
def test_fx_not_speech_and_preserves_machine_state(fx, speech, path):
    address, size, emitted = install()[path]
    assert (address, size) == ((SITE+19,5) if path == 0 else (SITE+65,10))
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    for base, length in [(SITE, 0x1000), (DATA, 0x5000), (CAVE, 0x1000), (STACK, 0x2000)]:
        uc.mem_map(base, length)
    uc.mem_write(SITE, fixture())
    uc.mem_write(DATA + 0x70, struct.pack('<5i', 23, fx, fx, speech, speech))
    uc.mem_write(DATA + 0x3170, struct.pack('<i', speech))
    uc.mem_write(address, b'\xe9' + struct.pack('<i', CAVE-address-5))
    uc.mem_write(CAVE, emitted + b'\xe9' + struct.pack('<i', address+size-CAVE-len(emitted)-5))
    registers = [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX,
                 UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]
    for index, register in enumerate(registers):
        uc.reg_write(register, 0x123400 + index)
    uc.reg_write(UC_X86_REG_ESP, STACK+0x1000)
    uc.reg_write(UC_X86_REG_EFLAGS, 0x246)
    tracked = registers + [UC_X86_REG_ESP, UC_X86_REG_EFLAGS]
    before = [uc.reg_read(r) for r in tracked]
    uc.emu_start(address, address+size, count=20)
    assert [uc.reg_read(r) for r in tracked] == before
    assert struct.unpack('<i', uc.mem_read(DATA+0x3170, 4))[0] == fx
    assert struct.unpack('<5i', uc.mem_read(DATA+0x70, 20)) == (23, fx, fx, speech, speech)
    assert len(emitted) == 12  # 17 executable bytes including return jump.


def test_unsupported_layout_fails_before_writing():
    blob = bytearray(fixture())
    struct.pack_into('<I', blob, 15, DATA + 0x84)
    with pytest.raises(Exception, match='unsupported saved-volume layout'):
        install(bytes(blob))


def test_unrecognized_code_fails_before_writing():
    with pytest.raises(ValueError, match='AOB not found'):
        install(b'\x90' * 32)


def test_unsupported_default_layout_fails_before_writing():
    blob = bytearray(fixture())
    struct.pack_into('<I', blob, 25+42, DATA+0x3174)
    with pytest.raises(Exception, match='unsupported default-volume layout'):
        install(bytes(blob))


def test_disabled_option_and_repeated_enable():
    lua = LuaRuntime()
    lua.execute('calls = 0; require = function() return {enable=function() calls=calls+1 end} end')
    init = lua.execute((ROOT / 'init.lua').read_text())
    init.enable(init, lua.table_from({'startup-sfx-volume': False}))
    assert lua.globals().calls == 0
    init = lua.execute((ROOT / 'init.lua').read_text())
    init.enable(init, lua.table_from({'startup-sfx-volume': True}))
    init.enable(init, lua.table_from({'startup-sfx-volume': True}))
    assert lua.globals().calls == 1
