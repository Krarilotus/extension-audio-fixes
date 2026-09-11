# Audio Fixes test download

Copy **audio-fixes-0.1.1.zip** into `<game>\ucp\modules\` without extracting it.
Use a separate UCP 3.0.7 Developer installation: this test module is unsigned.
Reopen the launcher, select Audio Fixes 0.1.1, apply and restart the game.
All three fixes default on; saved off choices remain off. Find the options under
Bugfixes and expand each for its localized explanation.

The proposed tag system recognizes `sounds` and `bugfixes`, translated in all nine
locale catalogs. Tags appear with the proposed GUI/store discovery update.
Keep older ZIP versions if existing profiles use them; no automatic migration.
A loose audio-fixes-0.1.1 folder takes precedence over this ZIP in Developer mode.

Official packager output for source c17ff7d06499f581ac1cff73ddca7916333956b4.
All Lua, options and description Markdown bytes match the accepted 0.1.0 package;
only version/tag metadata and the appended locale tag labels change.
SHA256: 4c43c490992f233646f50fd305eddf8289e0a5c5e7146b9a2a06c7ff69526b63

Feedback and testing guidance: https://github.com/UnofficialCrusaderPatch/UCP3-extensions-store/pull/29

Test download only. The store PR remains held from merge/publication.
