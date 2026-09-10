# Positional audio validation

R011 belongs to Audio Fixes; see [module issue 4](https://github.com/Krarilotus/extension-audio-fixes/issues/4)
and the matching [UCP2 report 1023](https://github.com/UnofficialCrusaderPatch/UnofficialCrusaderPatch2/issues/1023).
No OpenSHC reconstruction or generated headers are changed.

The native positional sound functions read a listener written by renderMap using
resolution-specific offsets. At 1280x720, zooming out moved a visible woodcutter
outside the fixed horizontal cutoff: source (247,229), listener (208,237), h=47
with the original limit of 45. Replaying the captured inputs through the original
instructions confirms rejection. Widening that limit alone leaves the listener
and stereo pan incorrect.

The option derives a private listener from the flat-ground viewport center using
the existing rotated tile lookup. Horizontal pan and both cutoff coordinates are
scaled by the actual viewport dimensions and native zoom. The original world
distance attenuation, variation scheduling, sound pool and FX mixer remain in use.
The renderer's listener stores are replayed unchanged; only the two audio readers
use private state. Unsupported lookup inputs retain the original listener; invalid
dimensions use nonzero 1024x640 scale defaults.

Automated: 133 combined tests, including 60 positional tests, execute emitted x86
for all four orientations, normal/zoomed views, viewport sizes, signed projection,
unchanged distance inputs, register/stack preservation, invalid inputs and protected
code writes. A separate local oracle runs the original screen-to-tile transform
against captured native lookup tables: the emitted center matches within one tile
in 128 combinations of four sizes, four camera origins, two zoom levels and four
orientations. The one-tile difference is flat diamond quantization, not terrain
height picking. Licensed executable bytes and lookup data are not distributed.

All five signatures are unique in SHC1.41 and Extreme1.41. Native testing uses
SHC SHA256 `3bb0a8c1e72331b3a30a5aa93ed94beca0081b476b04c1960e26d5b45387ac5a`,
UCP3.0.7 developer build `77c6accf14`, graphicsApiReplacer1.3.0 and
winProcHandler0.2.0 in an isolated installation. All three Audio Fixes options are
enabled. The existing audio.sav fixture has SHA256
`93a99e7de8d8bc1d0c14a779fb3f9c93ea919aacc3e31d001d5b44302a36f659`.
The latest user-selected settings are 1920x1080, music10, FX10, speech30;
normal exit and restart preserve them without touching sliders.

Native natural wood-delivery events (SFX41) pass the original cutoff after the
new projection in the following observed placements. Coordinates below are the
normalized h/v inputs to the existing sound code; FX master remained10.

| View | Keep placement | h,v |
| --- | --- | --- |
| Normal, orientation0 | Upper left | -19,-5 |
| Zoomed out, orientation0 | Lower right | 8,10 |
| Zoomed out, orientation0 | Upper right | 19,-1 |
| Zoomed out, orientation0 | Lower left | -19,18 |
| Zoomed out, orientation6 | Left edge | -37,-10 |

Natural wood chopping also passes in normal and zoomed/rotated views. This is
native call/cutoff observation with screenshots of actual camera placement;
it does not claim loopback waveform measurement. Earlier startup/video and
save/load acceptance remain recorded in their respective validation files.

Cost: 16 bytes of private state; installed FASM trampolines are 327/46/23 bytes
(396 total). The frame hook performs bounded integer arithmetic and table reads;
the sound hooks add two integer divisions for normal positional sound or one for
the full-volume variant. No runtime Lua callback, allocation, timer or dependency
is added. A task-only native microbenchmark copies these installed bodies and
runs five batches of two million calls after warmup, subtracting an empty loop
with identical setup. On a Ryzen5 3600X, median added times were about 9.5ns for
focus, 6ns for projection and 2.5ns for full-volume pan. These are warm-cache
microbenchmarks with millisecond timer resolution, not whole-frame measurements.
The unchanged finite sound pool can still drop sounds in a saturated scene;
this change admits visible sounds that were wrongly excluded, so crowded-scene
contention can increase. No larger pool or new sound assets are introduced.

The UCP3.0.7 ReleaseSecure packager includes 24 production/localization files,
13,859 uncompressed bytes and 17,541 ZIP bytes. All nine launcher locales resolve
through its actual translation function. Tests, diagnostics and documentation are
excluded by files.xml. No release has been published.

Native Extreme, multiplayer/replay, terrain-height acoustics and crowded-scene
stress are not claimed. Multiplayer simulation code and save formats are not
modified, but that is a scope statement, not native compatibility acceptance.
