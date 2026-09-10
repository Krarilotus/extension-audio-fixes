local M = {}

-- EAX is the original Bink gain; ECX is the existing FX slider value.
local scaleVolume = [[
  test ecx, ecx
  jns nonnegative
  xor ecx, ecx
nonnegative:
  cmp ecx, 100
  jle in_range
  mov ecx, 100
in_range:
  imul ecx
  mov ecx, 100
  idiv ecx
]]

function M.enable()
  local openSite = core.AOBScan("39 2D ? ? ? ? 74 26 39 2D ? ? ? ? 74 1E 8B 4C 24 18 51 B9")
  local gainSite = core.AOBScan("69 C0 FA 00 00 00 8B 54 BE 50 50 55 52 FF D3")
  local sliderSite = core.AOBScan("89 99 70 31 00 00 8D B1 90 01 00 00 BF 1F 00 00 00")
  if gainSite ~= openSite + 31 then
    error("Audio Fixes: unsupported Bink startup layout")
  end
  local soundSystem = core.readInteger(openSite + 10)
  if core.readInteger(openSite + 2) ~= soundSystem + 8 then
    error("Audio Fixes: unsupported Bink sound-device layout")
  end

  -- Controller, existing BinkSetVolume pointer, and native gain for each slot.
  local state = core.allocate(16, true)
  local values = {controller = state, setVolume = state + 4,
    gains = state + 8, savedFX = soundSystem + 0x74, soundActive = soundSystem}

  -- Both sound-enabled and muted opens pass here. Reset reused slot state.
  local opened = core.assemble([[
    mov dword [controller], esi
    mov dword [setVolume], ebx
    mov dword [gains + edi*4], 0
  ]], values)
  local started = core.assemble([[
    imul eax, eax, 250
    pushfd
    push ecx
    push edx
    mov dword [gains + edi*4], eax
    mov ecx, dword [savedFX]
  ]] .. scaleVolume .. [[
    pop edx
    pop ecx
    popfd
  ]], values)
  local changed = core.assemble([[
    pushfd
    pushad
    mov esi, dword [controller]
    test esi, esi
    jz finished
    add esi, 0x50
    mov edi, gains
    mov ebx, 2
next_slot:
    cmp dword [esi], 0
    je advance
    mov eax, dword [edi]
    mov ecx, dword [esp + 16]
    cmp dword [soundActive], 0
    jne apply_volume
    xor ecx, ecx
apply_volume:
  ]] .. scaleVolume .. [[
    push eax
    push 0
    push dword [esi]
    call dword [setVolume]
advance:
    add esi, 4
    add edi, 4
    dec ebx
    jnz next_slot
finished:
    popad
    popfd
  ]], values)

  core.insertCode(openSite, 6, opened, nil, "after")
  core.insertCode(gainSite, 6, started)
  core.insertCode(sliderSite, 6, changed, nil, "before")
end

return M
