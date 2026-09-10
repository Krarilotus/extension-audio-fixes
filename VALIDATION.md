# R013 validation

Original SHC 1.41 Latin executable SHA256:
`3bb0a8c1e72331b3a30a5aa93ed94beca0081b476b04c1960e26d5b45387ac5a`.
Extreme executable SHA256:
`55648e6b05d67d37a5773fe699bbb17a2d6ad4de1bb9dbded9a21caef82bd7fb`.

The signature occurs once in each executable, at 0x00496075 / 0x004961DE.
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

Test setup: isolated copied game and configpath/userdata; no replay installation
changes. DirectDraw native state was checked; visual checks used existing
Graphics API Replacer 1.3.0 and winProcHandler 0.2.0. No UI controls are added.
An obsolete Windows missing-DLL dialog overlaps part of the captured window;
the sound options and all three existing sliders remained inspectable.

Automated: `python -m pytest -q` executes 18 tests. Emitted x86 is executed with
Unicorn for independent FX/speech combinations (including mute/full), checking
all general registers, ESP, flags, and unrelated channel values. Invalid layout,
unrecognized code, disabled option and repeat activation are covered. These are
emulated tests, not native game compatibility claims.

Cost: one existing 5-byte store is redirected to a 17-byte trampoline. The
additional startup instructions are two jumps, push/pop EAX and one memory load;
there is no per-sound/per-frame overhead, new persistent state or dependency.
Allocation/page overhead comes from the existing UCP core allocator. Native
wall-clock startup deltas are not yet measured; modal acknowledgement and capture
timing must not be presented as patch overhead.

Still pending: fresh native FX=50/100 and missing-config launches; restart after
native slider persistence; save/load acceptance; native Extreme; direct audible
output comparison, final package-size measurement and independent review.
No multiplayer/replay compatibility claim is made from these tests.
