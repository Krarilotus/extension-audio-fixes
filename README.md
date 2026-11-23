# Audio Fixes

Fixes startup, video and positional audio. Uses the existing FX slider.

Add Audio Fixes to your configuration, switch on the fixes you want under
Bugfixes, apply and restart the game. All three are off by default; the
"UCP3 Fixes" plugin turns them on. Values explicitly saved in a configuration stay
as they are; if you relied on the earlier defaults, check the switches after
updating. Module text supports all nine UCP launcher languages.

| Option | URL |
|---|---|
| FX volume at startup | `audio-fixes.startup-sfx-volume` |
| Video FX volume | `audio-fixes.video-fx-volume` |
| Positional audio | `audio-fixes.positional-audio` |

Install Audio Fixes through the UCP 3.0.7 launcher's Content tab; it installs
the signed module for the regular framework build. Include modules in the filter
if needed. Find the options and their expandable explanations under Bugfixes.
See the [store release](https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/releases/tag/v3.0.7).
See [startup](VALIDATION.md), [video](VALIDATION-R012.md) and
[positional audio validation](VALIDATION-R011.md)
for tested behavior and compatibility limits.
