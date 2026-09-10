local M = {}

function M.enable()
  -- readUserConfig mirrors speech into stream 4, then incorrectly into samples.
  local site = core.AOBScan("A1 ? ? ? ? 56 55 6A 10 68 ? ? ? ? A3 ? ? ? ? A3 ? ? ? ? E8")
  local speechVolume = core.readInteger(site + 1)
  local speechMirror = core.readInteger(site + 15)
  local sampleVolume = core.readInteger(site + 20)
  if speechMirror ~= speechVolume + 4 or sampleVolume ~= speechVolume + 0x30F4 then
    error("Audio Fixes: unsupported saved-volume layout")
  end
  local fxVolume = speechVolume - 8

  -- First launch takes a separate defaults path: FX=80 but samples=100.
  local defaults = core.AOBScan("B8 50 00 00 00 A3 ? ? ? ? A3 ? ? ? ? B8 55 00 00 00 C7 05 ? ? ? ? 5A 00 00 00 A3 ? ? ? ? A3 ? ? ? ? C7 05 ? ? ? ? 64 00 00 00")
  if core.readInteger(defaults + 11) ~= fxVolume
      or core.readInteger(defaults + 42) ~= sampleVolume then
    error("Audio Fixes: unsupported default-volume layout")
  end

  local copyFX = {
    0x50,                         -- push eax
    0xA1, {fxVolume},             -- mov eax, [saved FX volume]
    0xA3, {sampleVolume},         -- mov [sample volume], eax
    0x58,                         -- pop eax
  }
  core.insertCode(site + 19, 5, copyFX)
  core.insertCode(defaults + 40, 10, copyFX)
end

return M
