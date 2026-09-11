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
f71e48f0afe2f80fae8b489c586f3d11df62d8fb. Of the 24 runtime/localization files,
options.yml and locale YAML now expose one-sentence explanations in the existing
Bugfixes category; expand each switch to read them. Lua files are byte-identical
to the tested candidate. SHA256:
595f03a45f1fc5ab43922a8ba4c26b005257e6f6acdcd6709d9ac1bbe6cd71bb

The older `audio-fixes-0.1.0-test-809c374.zip` is superseded: its filename and
wrapper folder are unsuitable for direct ZIP installation.

Feedback and testing guidance: https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/pull/29

Test download only. The store PR remains held from merge/publication.
