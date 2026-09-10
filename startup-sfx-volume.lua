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

  core.insertCode(site + 19, 5, {
    0x50,                         -- push eax
    0xA1, {fxVolume},             -- mov eax, [saved FX volume]
    0xA3, {sampleVolume},         -- mov [sample volume], eax
    0x58,                         -- pop eax
  })
end

return M
