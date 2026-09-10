local enabled = false

return {
  enable = function(self, config)
    if enabled then return end
    if config["startup-sfx-volume"] == true then
      require("startup-sfx-volume").enable()
    end
    if config["video-fx-volume"] == true then
      require("bink-volume").enable()
    end
    enabled = true
  end,
  disable = function()
    error("Audio Fixes requires a game restart to disable")
  end,
}
