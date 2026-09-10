"""Exercise emitted focus/viewport hooks without touching rendering or mixer state."""
from pathlib import Path
import re
import struct

from keystone import Ks, KS_ARCH_X86, KS_MODE_32
from lupa import LuaRuntime
import pytest
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *

ROOT=Path(__file__).resolve().parents[1]
POSITION,FULL,PROJECT,PAN,RENDER=0x401000,0x402000,0x401046,0x403000,0x404000
VIEW,STATE,ORIENTATION,CAVE,STACK=0x600000,0x800000,0x900000,0xA00000,0xB00000


class Harness:
    def __init__(self, bad_layout=False):
        self.uc=Uc(UC_ARCH_X86,UC_MODE_32)
        for address,size in [(0x400000,0x10000),(VIEW,0x1a0000),(STATE,0x1000),
                             (ORIENTATION,0x1000),(CAVE,0x4000),(STACK,0x2000)]:
            self.uc.mem_map(address,size)
        self.write(VIEW+0x9c,160)
        self.write(VIEW+0xa0,170)
        self.uc.mem_write(RENDER,bytes.fromhex('89 93 9c 00 00 00 89 b3 a0 00 00 00'))
        self.sites={}
        self.sizes=[]
        self.next_cave=CAVE
        lua=LuaRuntime(unpack_returned_tuples=True)
        def scan(pattern):
            return next(value for prefix,value in [('8B 44 24 10',POSITION),
                ('8B 44 24 0C',FULL),('8D 5A',PROJECT),('2B C6',PAN),('89 93',RENDER)]
                if pattern.startswith(prefix))
        layout={POSITION+16:VIEW+0x9c,POSITION+22:VIEW+0xa0,
                FULL+16:VIEW+0x9c,FULL+22:VIEW+0xa0,
                POSITION+10:ORIENTATION,FULL+10:ORIENTATION}
        if bad_layout: layout[FULL+22]+=4
        def read(address): return layout[address] if address in layout else self.read(address)
        def assemble(source,values):
            for name,value in values.items():
                source=re.sub(r'\b'+name+r'\b',hex(value),source)
            source=source.replace('dword [','dword ptr [').replace('word [','word ptr [')
            code,_=Ks(KS_ARCH_X86,KS_MODE_32).asm(source)
            return lua.table_from(code)
        def insert(site,size,code,return_to=None,original=None):
            body=bytes(code.values())
            if original=='before': body=bytes(self.uc.mem_read(site,size))+body
            dest=self.next_cave
            self.next_cave+=0x1000
            self.uc.mem_write(site,b'\xe9'+struct.pack('<i',dest-site-5))
            self.uc.mem_write(dest,body+b'\xe9'+struct.pack('<i',site+size-dest-len(body)-5))
            self.sites[site]=size
            self.sizes.append(len(body)+5)
        def write_data(address,value):
            assert address >= VIEW, 'writeInteger requires writable data memory'
            self.write(address,value)
        lua.globals().core=lua.table_from(dict(AOBScan=scan,readInteger=read,
            writeInteger=write_data,writeCode=lambda address,code:self.write(address,code[1][1]),
            allocate=lambda n,zero:STATE,assemble=assemble,insertCode=insert))
        lua.execute((ROOT/'positional-audio.lua').read_text()).enable()
        self.uc.reg_write(UC_X86_REG_ESP,STACK+0x1000)

    def write(self,address,value):
        self.uc.mem_write(address,struct.pack('<I',value&0xffffffff))

    def read(self,address): return struct.unpack('<i',self.uc.mem_read(address,4))[0]

    def run(self,site,**regs):
        for name,value in regs.items(): self.uc.reg_write(globals()['UC_X86_REG_'+name],value)
        self.uc.emu_start(site,site+self.sites[site],count=1000)

    def reg(self,name):
        value=self.uc.reg_read(globals()['UC_X86_REG_'+name])
        return value if value<2**31 else value-2**32

    def camera(self,width=1024,height=640,zoom=0,orientation=0,origin=(2688,1760),anchor=(19,48)):
        for offset,value in [(0x78,origin[0]),(0x7c,origin[1]),(0xac,anchor[0]),
                             (0xb0,anchor[1]),(0x18b730,width),(0x18b734,height),(0x90,zoom)]:
            self.write(VIEW+offset,value)
        self.write(ORIENTATION,orientation)
        row=(origin[1]+height*(zoom+1)//2-8*zoom)//8
        col=(origin[0]+width*(zoom+1)//2+256+160*zoom)//32
        index=row//2*401+(row%2)*200+col+{0:0,6:80400,4:160800,2:241200}.get(orientation,0)
        if not 0 <= index < 321602: index=0
        self.write(VIEW+0x4e600+index*4,51537)
        self.uc.mem_write(VIEW+0x271c0+51537*2,struct.pack('<h',230))
        self.write(VIEW+0x188728+230*12,51300)
        self.run(RENDER,EBX=VIEW,EDX=246,ESI=242,EAX=0x12345,ECX=0x23456,EDI=0x34567,EBP=0x45678,EFLAGS=0x247)


@pytest.mark.parametrize('orientation',[0,2,4,6])
def test_screen_center_uses_rotated_lookup_and_only_private_focus_changes(orientation):
    h=Harness()
    for zoom,origin,anchor in [(0,(2688,1760),(19,48)),(1,(1984,1504),(41,80))]:
        h.camera(1280,592,zoom,orientation,origin,anchor)
        assert [h.read(STATE+i*4) for i in range(4)]==[237,230,1280*(zoom+1),592*(zoom+1)]
        assert h.read(VIEW+0x9c)==246 and h.read(VIEW+0xa0)==242
        for name,value in dict(EBX=VIEW,EDX=246,ESI=242,EAX=0x12345,ECX=0x23456,
                               EDI=0x34567,EBP=0x45678,ESP=STACK+0x1000,EFLAGS=0x247).items():
            assert h.reg(name)==value


@pytest.mark.parametrize('width,height,zoom',[(1024,640,0),(1280,592,0),(1920,952,0),
    (1024,640,1),(1280,592,1),(1920,952,1),(1920,1080,1)])
@pytest.mark.parametrize('x,y',[(0,0),(10,-1),(-10,1),(100,-50),(-100,50),(35,36)])
def test_projection_scales_screen_coordinates_preserving_world_distance(width,height,zoom,x,y):
    h=Harness()
    h.camera(width,height,zoom)
    h.run(PROJECT,EAX=x,ECX=y,EDX=x-y,EDI=x+y,ESI=0x12345,EBP=0x34567)
    expected_h=int((x-y)*1024/(width*(zoom+1)))
    expected_v=int(((x+y)//2)*640/(height*(zoom+1)))
    assert h.reg('EDX')==expected_h
    assert h.reg('EDI')==expected_v
    assert h.reg('EBX')==expected_h+45
    assert (h.reg('EAX'),h.reg('ECX'))==(x,y)
    assert h.reg('ESP')==STACK+0x1000
    assert h.reg('ESI')==0x12345 and h.reg('EBP')==0x34567
    h.run(PAN,EAX=x,ESI=y,EDX=123,ECX=456)
    assert h.reg('ESI')==2*expected_h+62
    assert h.reg('EDX')==123 and h.reg('ECX')==456
    assert h.reg('ESP')==STACK+0x1000


@pytest.mark.parametrize('orientation,origin',[(1,(2688,1760)),(8,(2688,1760)),
    (0,(-10000,1760)),(0,(2688,-10000)),(0,(100000,1760)),(0,(2688,100000))])
def test_invalid_lookup_falls_back_without_out_of_bounds_reads(orientation,origin):
    h=Harness()
    h.camera(1280,592,1,orientation,origin)
    assert [h.read(STATE+i*4) for i in range(4)]==[246,242,2560,1184]


def test_reject_mismatched_native_readers_before_patching():
    with pytest.raises(Exception,match='unsupported positional sound layout'):
        Harness(bad_layout=True)


def test_both_positional_readers_use_private_focus_with_protected_code_writes():
    h=Harness()
    for site in (POSITION,FULL):
        assert h.read(site+16)==STATE
        assert h.read(site+22)==STATE+4


@pytest.mark.parametrize('width,height',[(0,640),(1024,0),(-1,640),(1024,-1),(8193,640),(1024,8193)])
def test_invalid_viewport_size_keeps_safe_nonzero_divisors(width,height):
    h=Harness()
    h.camera(width,height)
    assert [h.read(STATE+i*4) for i in range(4)]==[246,242,1024,640]
