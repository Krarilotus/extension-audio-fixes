"""Execute assembled event hooks with a stdcall Bink API boundary stub."""
from pathlib import Path
import re
import struct

from keystone import Ks, KS_ARCH_X86, KS_MODE_32
from lupa import LuaRuntime
import pytest
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *

ROOT = Path(__file__).resolve().parents[1]
OPEN, GAIN, SLIDER = 0x401000, 0x40101F, 0x403000
STATE, SOUND, BINK, CAVE, STACK, API = 0x600000, 0x700000, 0x800000, 0xA00000, 0xB00000, 0xD00000


class Harness:
    def __init__(self):
        self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        for base, size in [(0x400000,0x10000),(STATE,0x1000),(SOUND,0x4000),
                           (BINK,0x1000),(CAVE,0x4000),(STACK,0x2000),(API,0x1000)]:
            self.uc.mem_map(base, size)
        self.uc.mem_write(OPEN, b'\x39\x2d'+struct.pack('<I', SOUND+8))
        self.uc.mem_write(SLIDER, bytes.fromhex('89 99 70 31 00 00'))
        self.uc.mem_write(API, bytes.fromhex('c2 0c 00'))
        self.calls = []
        self.uc.hook_add(UC_HOOK_CODE, self.api_call, begin=API, end=API)
        lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua = lua
        self.next_cave = CAVE
        self.sizes = []
        def scan(pattern):
            return OPEN if pattern.startswith('39 2D') else GAIN if pattern.startswith('69 C0') else SLIDER
        def read(address):
            return {OPEN+10:SOUND, OPEN+2:SOUND+8}[address]
        def assemble(source, values):
            for name, value in values.items():
                source = re.sub(r'\b'+name+r'\b', hex(value), source)
            source = source.replace('dword [', 'dword ptr [')
            code, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(source)
            return lua.table_from(code)
        def insert(site, size, code, return_to=None, original=None):
            body = bytes(code.values())
            copied = bytes(self.uc.mem_read(site,size))
            if original == 'before': body = copied + body
            if original == 'after': body += copied
            dest = self.next_cave
            self.next_cave += 0x1000
            self.uc.mem_write(site, b'\xe9'+struct.pack('<i',dest-site-5)+b'\x90'*(size-5))
            self.uc.mem_write(dest,body+b'\xe9'+struct.pack('<i',site+size-dest-len(body)-5))
            self.sizes.append(len(body)+5)
        lua.globals().core = lua.table_from({'AOBScan':scan, 'readInteger':read,
            'allocate':lambda size,zero:STATE, 'assemble':assemble, 'insertCode':insert})
        lua.execute((ROOT/'bink-volume.lua').read_text()).enable()
        self.write(SOUND,1)
        self.write(SOUND+8,1)
        self.uc.reg_write(UC_X86_REG_ESP,STACK+0x1000)

    def write(self, address, value):
        self.uc.mem_write(address,struct.pack('<I',value & 0xFFFFFFFF))

    def read(self,address):
        return struct.unpack('<I',self.uc.mem_read(address,4))[0]

    def api_call(self,uc,address,size,user):
        esp=uc.reg_read(UC_X86_REG_ESP)
        self.calls.append(struct.unpack('<3I',uc.mem_read(esp+4,12)))

    def execute(self,site,size,**registers):
        for name,value in registers.items():
            self.uc.reg_write(globals()['UC_X86_REG_'+name],value)
        self.uc.emu_start(site,site+size,count=500)

    def open(self,slot,handle):
        self.write(BINK+0x50+slot*4,handle)
        self.execute(OPEN,6,ESI=BINK,EDI=slot,EBX=API,EBP=0)

    def gain(self,slot,per_file,fx):
        self.write(SOUND+0x74,fx)
        self.execute(GAIN,6,EDI=slot,EAX=per_file,ECX=0x123456,EDX=0x789ABC)
        assert self.uc.reg_read(UC_X86_REG_ECX)==0x123456
        assert self.uc.reg_read(UC_X86_REG_EDX)==0x789ABC
        return self.uc.reg_read(UC_X86_REG_EAX)


@pytest.mark.parametrize('fx', [0,1,50,99,100])
@pytest.mark.parametrize('per_file', [0,37,100,131,10000])
def test_clip_start_preserves_native_gain_at_full_and_mutes_at_zero(fx,per_file):
    h=Harness()
    h.open(0,0x1234)
    assert h.gain(0,per_file,fx)==per_file*250*fx//100
    assert h.read(STATE+8)==per_file*250


@pytest.mark.parametrize('fx', [0,50,100])
def test_live_slider_updates_both_slots_and_preserves_registers(fx):
    h=Harness()
    h.open(0,0x1234)
    h.gain(0,100,75)
    h.open(1,0x5678)
    h.gain(1,37,75)
    regs={'EAX':0x111,'EBX':fx,'ECX':SOUND,'EDX':0x222,'ESI':0x333,'EDI':0x444,'EBP':0x555,'EFLAGS':0x246}
    h.execute(SLIDER,6,**regs)
    assert h.calls==[(0x1234,0,25000*fx//100),(0x5678,0,9250*fx//100)]
    assert h.read(SOUND+0x3170)==fx
    for name,value in regs.items():
        assert h.uc.reg_read(globals()['UC_X86_REG_'+name])==value
    assert h.uc.reg_read(UC_X86_REG_ESP)==STACK+0x1000


def test_closed_slot_is_not_called_and_muted_replacement_does_not_inherit_gain():
    h=Harness()
    h.open(0,0x1234)
    h.gain(0,100,100)
    h.write(BINK+0x50,0)  # Native close clears the pointer.
    h.execute(SLIDER,6,ECX=SOUND,EBX=50)
    assert h.calls==[]
    h.open(0,0x1234)  # Allocator reuses the same handle while sound is disabled.
    h.execute(SLIDER,6,ECX=SOUND,EBX=100)
    assert h.calls==[(0x1234,0,0)]


def test_no_video_yet_and_sound_off():
    h=Harness()
    h.execute(SLIDER,6,ECX=SOUND,EBX=100)
    assert h.calls==[]
    h.open(0,0x1234)
    h.gain(0,100,100)
    h.write(SOUND,0)
    h.execute(SLIDER,6,ECX=SOUND,EBX=100)
    assert h.calls==[(0x1234,0,0)]


@pytest.mark.parametrize('fx,expected',[(-1,0),(101,25000),(0x7FFFFFFF,25000)])
def test_corrupt_fx_value_cannot_overflow_the_division(fx,expected):
    h=Harness()
    h.open(0,0x1234)
    assert h.gain(0,100,fx)==expected
