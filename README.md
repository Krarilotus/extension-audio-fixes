# Audio Fixes

Focused UCP3 audio corrections using the game's existing volume sliders and
audio facilities. This repository is the shared module home for startup SFX
volume (R013), Bink video volume (R012), and a bounded investigation of viewport
sound attenuation (R011). Each correction is reviewed separately.

Implementation and native acceptance are in progress. No release is available.
The `startup-sfx-volume` option makes sampled effects use the saved FX setting
immediately. It defaults to off; enabling it requires a restart. Copy the module
files into `ucp/modules/audio-fixes-0.1.0` in a UCP developer installation and
select the option through the usual configuration. See [validation](VALIDATION.md)
for actual checks and remaining acceptance.

Faithful original-game reconstruction belongs in
[OpenSHC](https://github.com/sourcehold/OpenSHC); intentional behavior changes
belong here.
