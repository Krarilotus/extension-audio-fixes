# Audio Fixes test download

Copy **audio-fixes-0.1.0.zip** into `<game>\ucp\modules\` without extracting it.
Use a separate UCP 3.0.7 Developer installation: this test module is unsigned.
Reopen the launcher, add Audio Fixes in Extensions, enable its three fixes and apply.
In Content, turn off the globe filter to show installed/local content; ensure the
funnel filter includes modules. Move any previously extracted audio-fixes-0.1.0
folder outside modules first, since Developer mode prefers folders over ZIPs.

The ZIP is the official packager output for source
809c37428232c6ed25776cd9dd44abb15bf992c2, with all 24 tested runtime/localization
files unchanged. SHA256:
242fa6035e11bf1416df80a2d5d5b1aaa37f91b25a972cbe100bda48e6b3197c

The older `audio-fixes-0.1.0-test-809c374.zip` is superseded: its filename and
wrapper folder are unsuitable for direct ZIP installation.

Feedback and testing guidance: https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/pull/29

Test download only. The store PR remains held from merge/publication.
