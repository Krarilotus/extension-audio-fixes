# Audio Fixes test download

Copy **audio-fixes-0.1.0.zip** into `<game>\ucp\modules\` without extracting it.
Use a separate UCP 3.0.7 Developer installation: this test module is unsigned.
Reopen the launcher, add Audio Fixes in Extensions, apply and restart the game.
All three fixes default on. Previously saved off settings remain off: enable
those switches manually when updating an existing configuration.
In Content, turn off the globe filter to show installed/local content; ensure the
funnel filter includes modules. Move any previously extracted audio-fixes-0.1.0
folder outside modules first, since Developer mode prefers folders over ZIPs.

The ZIP is the official packager output for source
669390229a0ea765acffd988b65cfb15f2569961. Of the 24 runtime/localization files,
only options.yml changed to enable the three defaults; Lua and translations are
byte-identical to the tested candidate. SHA256:
246f8ddf9355a2e0e71683ab3b20c95f795f4e30ce126c36ebd4532fbfcafa2c

The older `audio-fixes-0.1.0-test-809c374.zip` is superseded: its filename and
wrapper folder are unsuitable for direct ZIP installation.

Feedback and testing guidance: https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/pull/29

Test download only. The store PR remains held from merge/publication.
