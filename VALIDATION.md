# R013 validation

Original SHC 1.41 Latin executable SHA256:
`3bb0a8c1e72331b3a30a5aa93ed94beca0081b476b04c1960e26d5b45387ac5a`.
Extreme executable SHA256:
`55648e6b05d67d37a5773fe699bbb17a2d6ad4de1bb9dbded9a21caef82bd7fb`.

The saved-settings signature occurs once in each executable, at 0x00496075 /
0x004961DE; the default-settings signature at 0x0049637B / 0x004964E6.
Original assembly and existing OpenSHC `readUserConfig` agree: speech is loaded,
mirrored to stream 4, then incorrectly stored as sample volume. The original
FX slider sets streams 1/2 and samples; speech sets streams 3/4.

Native SHC baseline, saved music/FX/speech 37/0/83: device ready,
streams [37,0,0,83,83], sample volume 83. Patched startup through released UCP
3.0.7 Developer (`77c6accf14`) gives sample volume 0 with identical streams.
The first sample setup (main-menu click) was instrumented in the test installation:
master=0, per-file=100, effective=0. The diagnostic is outside the module.
Loaded Castle Builder `A Mighty Oasis.map` (SHA256
`f6d54c03b019026b40c41b9def0e9467188353f1490efef505922b6d0f2733c2`).
The original FX slider subsequently changed streams 1/2 and sample volume to
12, then 24, leaving music=37 and speech=83 unchanged.
Additional fresh native launches passed: FX=50/speech=83 produced first-sample
master/effective volume 50; FX=100/speech=0 produced 100. Music remained 37.
Those saved-setting matrix checks used runtime commit 8ae3f7a.

Further end-to-end testing found the separate no-config path sets FX=80 but
sample master=100. Original assembly and native startup both confirmed it. This
revision also redirects that default store to the FX value, preserving the game's
default stream values. Native fixed-default acceptance is pending.

The user then set music=10, FX=11, speech=30 in the native UI and requested a
restart without touching the sliders. With this revision and the video correction,
fresh startup produced streams [10,11,11,30,30], sample master11, first-sample
effective11. The config SHA256 stayed
`c00783a5c2398ec44daaef89dc19e4f402f90e978940b8e86d3c47679233f511`.
No slider was touched after restart. The user reported the audible result working.

Test setup: isolated copied game and configpath/userdata; no replay installation
changes. DirectDraw native state was checked; visual checks used existing
Graphics API Replacer 1.3.0 and winProcHandler 0.2.0. No UI controls are added.
An obsolete Windows missing-DLL dialog overlaps part of the captured window;
the sound options and all three existing sliders remained inspectable.

Automated: `python -m pytest -q` executes 40 tests. Emitted x86 is executed with
Unicorn for independent FX/speech combinations (including mute/full), checking
all general registers, ESP, flags, and unrelated channel values. Invalid layout,
unrecognized code, disabled option and repeat activation are covered. These are
emulated tests, not native game compatibility claims.

Cost: the saved/default stores use two 17-byte trampolines, verified by reading
native installed code. Only one path runs per config load. The additional executed
startup instructions are two jumps, push/pop EAX and one memory load;
there is no per-sound/per-frame overhead, new persistent state or dependency.
Allocation/page overhead comes from the existing UCP core allocator. Native
wall-clock startup deltas are not yet measured; modal acknowledgement and capture
timing must not be presented as patch overhead.

Package measurement will be refreshed for this default-path revision. The prior
saved-only candidate contained four runtime files, 1,549 bytes / 1,275 ZIP bytes.
No assets, diagnostics, tests or test-only
Python dependencies are packaged. This is a local candidate, not a release.

Still pending: fixed-default native launch, save/load acceptance, native Extreme
and independent review. User-driven slider persistence and the requested audible
restart comparison have passed as described above.
No multiplayer/replay compatibility claim is made from these tests.
