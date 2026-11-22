# Audio Fixes

Fixes startup, video and positional audio. Uses the existing FX slider.

Version 0.2.0 ships the game's original behaviour: all three fixes are off by
default, so adding the module alone changes nothing. The "UCP3 Fixes" plugin
turns all three on; you can also switch each one on yourself under Bugfixes.
Values you saved in a configuration stay as they are. If you added an earlier
version on its own and update it, switch the fixes you want back on (or use the
"UCP3 Fixes" plugin). Module text supports all nine UCP launcher languages.

| Option | URL | Default |
|---|---|---|
| FX volume at startup | `audio-fixes.startup-sfx-volume` | off |
| Video FX volume | `audio-fixes.video-fx-volume` | off |
| Positional audio | `audio-fixes.positional-audio` | off |

Install Audio Fixes through the UCP 3.0.7 launcher's Content tab; it installs
the signed module for the regular framework build. Include modules in the filter
if needed. Find the options and their expandable explanations under Bugfixes.
See the [store release](https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/releases/tag/v3.0.7).
See [startup](VALIDATION.md), [video](VALIDATION-R012.md) and
[positional audio validation](VALIDATION-R011.md)
for tested behavior and compatibility limits.
