# R012 video FX volume validation

Related report: [UCP2 #764](https://github.com/UnofficialCrusaderPatch/UnofficialCrusaderPatch2/issues/764).
This is a UCP3 opt-in implementation in the shared Audio Fixes module. It uses
the existing FX slider and Bink API; no new volume category is introduced.

The native `playBINK` path applies `fx_volume.txt` gain multiplied by 250 and
omits the user's FX value. It has two live slots. Native close clears the slot's
handle. The existing sample-volume setter is reached by the FX slider, alongside
its stream 1/2 updates. The patch scales initial Bink gain by FX/100, remembers
each slot's original gain, and updates live handles on that existing setter.
Muted opens reset cached gain, including handle reuse; closed handles are skipped.

SHC 1.41 SHA256:
`3bb0a8c1e72331b3a30a5aa93ed94beca0081b476b04c1960e26d5b45387ac5a`.
Extreme SHA256:
`55648e6b05d67d37a5773fe699bbb17a2d6ad4de1bb9dbded9a21caef82bd7fb`.
All three signatures are unique in both actual executables. SHC sites are
0x408F4C / 0x408F6B / 0x479E81; Extreme 0x408F5C / 0x408F7B / 0x47A051.
Existing OpenSHC reconstruction was used as a lead and checked against original
assembly. No reconstruction changes are required or bundled here.

Native SHC tests used isolated licensed game files, released UCP 3.0.7 Developer
77c6accf14, Graphics API Replacer 1.3.0 and winProcHandler 0.2.0. A test-only
diagnostic invokes the native Bink open/close and sound setter functions and logs
the real BinkSetVolume boundary. It does not ship in this module. These are native
function-harness checks, not claims of naturally triggered AI events or recorded
audible output. Both clips were also seen playing in the native window.

Fixtures: `wf_anger1.bik` (Wolf message), SHA256
`a6027f5a2149f88a4d1e5f9e1417a984bb9132ea924b955eb22b0e969d61d8f8`;
`st03_woodcutters_hut.bik` (building/workshop video), SHA256
`b9cb669e354db3bdf8cf0fb0ca615209894fe1689cfbdc19cd55c869be131631`.
The assets are not redistributed.

| Native check | Wolf gain | Woodcutter gain |
| --- | ---: | ---: |
| Option disabled, start at saved FX=0 | 7500 | 20000 |
| Option disabled, setter 0/50/100 | no update | no update |
| Option enabled, start at saved FX=0 | 0 | 0 |
| Option enabled, live setter FX=50 | 3750 | 10000 |
| Option enabled, live setter FX=100 | 7500 | 20000 |
| Option enabled, live setter FX=0 | 0 | 0 |
| Wolf closed, live setter FX=50 | skipped | 10000 |

The original UI FX slider was separately clicked through 12/24/36/48 while the
woodcutter slot played: gains 2400/4800/7200/9600. Music=37 and speech=83 remained
unchanged. The native sample path simultaneously used R013's saved FX correction.
No native error was logged. Video frame/synchronization timing was not benchmarked.

Automated: 33 video tests, 73 including the expanded R013 checks, pass under
Python/pytest. Lua's actual
assembly strings are assembled and executed in Unicorn with a stdcall API stub.
Checks include two live slots, startup/live mute/mid/full, per-file gain, closed
and reused handles, sound disabled, no video, corrupt FX values, preserved
registers/flags/stack. Keystone is a test-only assembler; native UCP uses FASM.

Cost: three event hooks, 16 bytes persistent state, no per-frame/per-sound polling,
no new runtime dependency. At most two extra BinkSetVolume calls per FX setter
event. Both emulation and a read-only inspection of the actual installed native
FASM code confirm 34/55/105-byte trampolines (194 total). The allocations share
the core allocator's code area; allocator page accounting is not yet measured.
Runtime files including all nine locales total 8,428 bytes; the candidate ZIP is
6,908 bytes before the shared startup-code cleanup is incorporated. All labels
resolve through the launcher's actual translation function. No tests, diagnostic
code, Python dependencies or assets are packaged. No release was published.

Remaining acceptance: native Extreme, natural AI/building trigger and timing,
sound-off/reused-slot native stress, save/load and persistence compatibility,
independent review. Multiplayer and replay have not been tested. Native test
access is serialized with the Interface and Visual threads; this PR remains draft.
