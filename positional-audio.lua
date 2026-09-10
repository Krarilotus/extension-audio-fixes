local M = {}

function M.enable()
  local position = core.AOBScan("8B 44 24 10 8B 4C 24 14 8B 15 ? ? ? ? 2B 05 ? ? ? ? 2B 0D ? ? ? ? 83 FA 02")
  local fullVolume = core.AOBScan("8B 44 24 0C 8B 74 24 10 8B 3D ? ? ? ? 2B 05 ? ? ? ? 2B 35 ? ? ? ? 83 FF 02")
  local projection = core.AOBScan("8D 5A 2D D1 FF 83 FB 5A 0F 87 ? ? ? ? 83 C7 24 83 FF 48")
  local fullPan = core.AOBScan("2B C6 8D 74 00 3E 85 F6 7D 04 33 F6 EB 0A 83 FE 7F")
  local render = core.AOBScan("89 93 9C 00 00 00 89 B3 A0 00 00 00 A3 ? ? ? ? A1")
  local listener = core.readInteger(position+16)
  local orientation = core.readInteger(position+10)
  if core.readInteger(position+22) ~= listener+4
      or core.readInteger(fullVolume+16) ~= listener
      or core.readInteger(fullVolume+22) ~= listener+4
      or core.readInteger(fullVolume+10) ~= orientation
      or projection ~= position+70 then
    error("Audio Fixes: unsupported positional sound layout")
  end

  -- Private audio focus and viewport scales; renderer state stays unchanged.
  local state = core.allocate(16, true)
  local values = {focusX=state, focusY=state+4, width=state+8,
    height=state+12, orientation=orientation}
  core.writeInteger(state, core.readInteger(listener))
  core.writeInteger(state+4, core.readInteger(listener+4))
  core.writeInteger(state+8, 1024)
  core.writeInteger(state+12, 640)

  -- Resolve the flat-ground viewport center through the native rotated tile
  -- table. The screen transform has an eight-column gutter, plus a zoom offset.
  local focus = core.assemble([[
    pushfd
    pushad
    mov dword [focusX], edx
    mov dword [focusY], esi
    mov dword [width], 1024
    mov dword [height], 640
    mov eax, dword [ebx + 0x18B730]
    mov ecx, dword [ebx + 0x18B734]
    cmp eax, 1
    jl finished
    cmp ecx, 1
    jl finished
    cmp eax, 8192
    ja finished
    cmp ecx, 8192
    ja finished
    cmp dword [ebx + 0x90], 0
    je scales
    add eax, eax
    add ecx, ecx
scales:
    mov dword [width], eax
    mov dword [height], ecx
    mov eax, ecx
    sar eax, 1
    cmp dword [ebx + 0x90], 0
    je row
    sub eax, 8
row:
    add eax, dword [ebx + 0x7C]
    sar eax, 3
    cmp eax, 399
    ja finished
    mov edx, eax
    and edx, 1
    imul edx, edx, 200
    sar eax, 1
    imul eax, eax, 401
    add edx, eax
    mov eax, dword [width]
    sar eax, 1
    add eax, 256
    cmp dword [ebx + 0x90], 0
    je column
    add eax, 160
column:
    add eax, dword [ebx + 0x78]
    sar eax, 5
    cmp eax, 200
    ja finished
    add edx, eax
    cmp edx, 80400
    jae finished
    mov eax, dword [orientation]
    test eax, eax
    jz lookup
    cmp eax, 6
    ja finished
    test eax, 1
    jnz finished
    mov ecx, 8
    sub ecx, eax
    imul ecx, ecx, 40200
    add edx, ecx
lookup:
    mov eax, dword [ebx + edx*4 + 0x4E600]
    cmp eax, 80400
    jae finished
    movsx ecx, word [ebx + eax*2 + 0x271C0]
    cmp ecx, 399
    ja finished
    lea edx, [ecx + ecx*2]
    sub eax, dword [ebx + edx*4 + 0x188728]
    cmp eax, 399
    ja finished
    mov dword [focusX], eax
    mov dword [focusY], ecx
finished:
    popad
    popfd
  ]], values)
  local project = core.assemble([[
    push eax
    push ecx
    push edx
    mov eax, edx
    shl eax, 10
    cdq
    idiv dword [width]
    mov dword [esp], eax
    sar edi, 1
    imul eax, edi, 640
    cdq
    idiv dword [height]
    mov edi, eax
    pop edx
    pop ecx
    pop eax
    lea ebx, [edx + 45]
  ]], values)
  local pan = core.assemble([[
    sub eax, esi
    push edx
    shl eax, 10
    cdq
    idiv dword [width]
    pop edx
    lea esi, [eax + eax + 62]
  ]], values)

  core.insertCode(render, 12, focus, nil, "before")
  core.writeCode(position+16, {{state}})
  core.writeCode(position+22, {{state+4}})
  core.writeCode(fullVolume+16, {{state}})
  core.writeCode(fullVolume+22, {{state+4}})
  core.insertCode(projection, 5, project)
  core.insertCode(fullPan, 6, pan)
end

return M
