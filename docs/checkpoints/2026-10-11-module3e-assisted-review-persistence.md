# Module 3E — Assisted Review Session Persistence

Date: 2026-10-11. Status: implementation ready for user real-device acceptance.
Baseline/main: `7269a02c9ba418796afeabbd0091036a0b72f3d5`.
Branch: `codex/module3e-assisted-review-persistence`.
This checkpoint's local commit identifies the implementation; its exact
SHA belongs in the private completion report, not in self-referential content.
No push, main merge, physical-phone acceptance or next module is authorized.

## Implemented behavior and storage

One current Assisted review automatically saves candidate confirmation,
exclusion, correction and manual additions. The original detector packet/source
and review rows are separate. A Repository/controller derives the deduplicated
deck from committed decisions; repeated plays do not occupy another slot.
Restore revalidates the packet, image hashes/dimensions and all review rows.
Pending stays pending. User review is not Human GT or training supervision.

Android uses a small built-in SQLite schema v1 for metadata and structured review
rows. The immutable original packet, including embedded JPEG evidence, lives in
an App-private file. DB, journals and packets are under `noBackupFilesDir`.
Web preview uses IndexedDB with the same version1 business envelope; neither
platform uses localStorage for core data. No dependencies or permissions added.
The new native plugin is limited to `AssistedSessionStore` load/save/replace.

Writes are serialized and session/revision checked; UI publishes only committed
results. Files are published before the SQLite pointer, with file/directory sync.
Save never changes the raw packet. Replacement and restart require confirmation;
cancel preserves progress. Restart retains evidence, resets decisions to pending
and removes manual additions. Successful replacement/restart creates a new UUID
so old unapplied input drafts cannot leak into the new review.

Corruption, missing packet, incompatible version, stale writes and I/O failures
preserve existing files/state and block unsafe writes. Retry reloads the last
commit rather than pretending the failed action was saved. No destructive schema
upgrade, delete-on-corruption handler, silent fallback or automatic clear exists.

## Verification

Fresh logs/receipts remain ignored under `outputs/module3e/`.

- App: `npm.cmd test -- --run`, 201 passed / 12 files, exit0.
  `npm.cmd run typecheck`, exit0. Existing Mock/Recorded tests remain green.
- `npm.cmd run android:sync`, exit0: TypeScript, Vite build and native sync.
  Current JS/CSS assets are `index-C4jfCsph.js` / `index-Yg1HcDny.css`.
- Real browser UI: 23 states, Chrome via already bundled Playwright. Real local
  packet imports 18 pending candidates/47 images; five unique confirmations reach
  5/8. Duplicate, exclude, correction, manual/Unknown, mode switching, canceled
  replace/restart and invalid import checks pass. Closing the entire browser and
  relaunching the same owned profile restores rows/deck/evidence. Mobile viewports
  390x844 and320x568 have no horizontal overflow or runtime/console errors.
- Disposable browser corruption checks preserve missing/corrupt reviews and a
  non-JSON value introduced during validation. RED failures are retained; the
  final successful checks do not overwrite their records.
- Scoped Python regression: 586 passed / one existing Windows symlink-permission
  skip, exit0; three additional private geometry tests passed. Both existing
  Python environments' `pip check` passes. Unchanged offline-video and isolated
  ByteTrack full suites were not rerun in3E; previous totals are not fresh results.
- Existing npm versions/license metadata: 194 lock locations,148 installed
  packages,13 direct pins,46 absent optional platform packages; no required
  package/version/license-metadata mismatch. No installation, weight download,
  network vulnerability scan or blanket rights-clearance claim.
- A fresh SHA check covers all5,859 accepted historical files: no missing,
  mismatched, changed-during-read or nonignored files. APK privacy checks below
  pass; end-of-task scope/link/stat receipts follow final documentation updates.

## Android native checks and Debug APK

Actual owned API36 emulator platform checks: 30 passed /0 failed, recorded in
`native/native-green30.log`. These cover exact packet/review restoration, stale
writes, transactional rollback, missing/tampered packets, unsupported versions,
corrupt DB/page preservation, row-count/hash/type integrity and restart.
The reviewer found and the runtime regressions reproduced five failures before
the narrow fixes: persisted fractional ordinal/count/revision, missing DB with
surviving packet, and replacement revision not1. The RED log retains25 passes/
5 failures; the original22 tests all passed. Fixed integer/TEXT type gates,
pristine-directory checks and revision-one guard close those defects. The test
fixture uses a fixed canonical synthetic child and rejects links/escaped cleanup.
Final local code review reports no remaining Important/Critical findings.

Final main-only command:
`gradlew.bat --offline --no-daemon --console=plain --max-workers=2 :app:assembleDebug`.
`native/native-green-build4.log`: exit0,39s,71 tasks (4 executed/67 up-to-date).
The copied delivery APK exactly matches the final native build and synced assets.
Path: `outputs/module3e/android/clash-tracker-assisted-persistence-debug.apk`.
Size:4,078,411 bytes. SHA-256:
`b95ab9d1362e0eab8e4bb0c7012f8e42991a2d8abc08ab4561ccd1e42b9896b6`.

Retained environment: App Node24.18.1/npm11.16.0, TypeScript5.9.3/Vite8.3.3,
Capacitor8.4.3, Temurin JDK21.0.12.1+1, Gradle8.14.3,
Android platform36 rev2/build-tools35.0.0. No installation or Release signing.
APK v2 signature verifies and Debug certificate matches the old accepted APK,
supporting covering-install rather than uninstalling/clearing existing data.
Source manifest has0 uses-permission entries; merged APK only uses the App's own
AndroidX signature permission. No private candidate/media/GT/model/database or
source-path data is bundled. APK stays ignored/untracked.

The original offline Gradle AndroidTest tasks failed on unavailable cached Maven
transitives; those failures remain. Instead, the already installed SDK's aapt2,
javac/d8/apksigner built the dependency-free platform instrumentation APK and ran
all30 checks on the actual emulator. This is not a successful Gradle AndroidTest
task. The first main Debug build failed on unsupported `OsConstants.O_DIRECTORY`;
directory open/type-check/fsync now uses supported SDK APIs. Android path-alias
and instrumentation-UID fixture failures are also retained, not rewritten.

Actual Android App behavioral QA uses the copied delivery APK on the owned API36
emulator, never a connected physical phone. The native picker delivered the actual
18-candidate/47-JPEG local JSON. The21 original UI states verify5/8 confirmations,
duplicate slots, exclusion, correction with raw prediction retained, manual/Unknown,
canceled replace/restart, invalid import and Mock/Recorded isolation.
Force-stop/relaunch, actual emulator reboot and `adb install -r` each restore the
same20 rows/5/8/revision12; every47 inline JPEG hash and432x960 size matches the
original. Confirmed restart returns18 pending/0/8, removes manual additions,
retains all47 images and persists after another force-stop/relaunch. No uninstall,
clear-data, test-state reimport or physical-device operation was used for recovery.

This is a **qualified behavioral result, not a blanket green Android QA run**.
An initial debugger-socket readiness failure, five-minute reboot watchdog timeout,
later Android process/system UI ANRs and their screenshots/receipts are retained.
The same original emulator eventually completed reboot without host restart or
data reset; low host free memory was observed, but is not proven the only cause.
The final aggregate's zero-console assertion failed on two
`Error injecting safe area CSS: TypeError: Cannot read properties of null (reading 'style')`
messages. Their exact source is unchanged Capacitor8.4.3
`SystemBars.java`'s `document.documentElement.style` injection; both occur before
the new AssistedSessionStore load. Dependency/configuration and upstream source
are unchanged. No App page exception, native FATAL or SQLite exception was found
in the inspected App-PID logs. The original aggregate FAIL is not rewritten;
an additive receipt separately reports the verified behavior and these limits.
No dependency workaround or unrelated system-bar change is included in3E.
Physical-phone final acceptance of this new APK remains pending user.

## Changed surface and retained boundaries

Changes are limited to App/session model, Repository/platform stores/controller,
Assisted UI, App mode restoration, related TypeScript/native tests, the local
native plugin registration, one platform instrumentation-runner configuration
line, and current documentation. No deletion, npm/Maven dependency change,
permission change, detector/adapter/formal-engine/GT/scoring change or training.
The formal event engine tree stays `028d60e093c5eb7b40439c198b0215dd0dc29761`.

This is not backup/export, a multi-session system or cross-device sync. Old
immutable packets are retained on replacement/restart; repeated imports can grow
private storage. Uninstall, clear-app-data, device loss or browser-site-data
removal can destroy the only copy. Device power-loss durability was not physically
tested. Hashes bind bytes, not authenticity, game permission or legal clearance.
The store detects corruption of surviving records, not external complete logical
deletion of an otherwise valid database's session/review rows.

The scientific detector baseline remains2/5 and one Royal Hogs duplicate; no
user-confirmed card list is advertised as automatic event accuracy. No real-game
connection, capture, cross-App HUD, cycle, evolution or elixir functionality.
Stop after local delivery and await the user's new APK phone acceptance.
