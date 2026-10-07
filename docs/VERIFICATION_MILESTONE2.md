# Milestone 2 — Debug APK and first multiclass review batch

Verified locally on2026-10-07. TaskB1 is complete; TaskA1's review packet is
prepared, but its actual human-GT confirmation/import is **pending**. This is not
detector accuracy, finished multiclass GT, training readiness or real-game HUD
acceptance. User selected independent ChatGPT review followed by returned
decisions; no human identity or confirmation has been invented.

## Scope and baseline

- Branch: `codex/milestone2-apk-and-first-gt`.
- Start: `97d87d875e97b847e79fd00433a79d779e9abd1c`, accepted Milestone1.
- Mock App behavior, App source, npm pins, Android wrapper, preannotation code
  and schema are unchanged. Only public documentation is changed this stage.
- No main merge/push, training, inference rerun, weights download, new game
  ability, product feature, SQLite schema/migration or business data change.
- All generated artifacts/toolchain/media/GT/signing material stay Git-ignored.
  Match02 remains mid-match truncated and training-ineligible.

## TaskB1 — actual Android build and startup

APK: `outputs/milestone2/clash-tracker-simulated-debug.apk`,3,977,891 bytes.

SHA256: `774ed13e2ac69690330cf126084aee15b19ecf676e579a1872eaa7e37ea6bb0d`.

Package `com.clashtracker.simulated`, version0.1.0/code1, minimumAPI24,
compile/targetAPI36. `apksigner verify --verbose --print-certs` passes with
Android Debug certificate / APK Signature Schemev2. This is not release signing.

| Component | Actual installed/used version |
|---|---|
| Host | Windows11 Home Chinese, x64, build26200 |
| Portable JDK | Eclipse Temurin21.0.12.1+1, HotSpot x64 |
| SDK command-line tools |22.0|
| SDK platform |Android36, revision2|
| Build tools |35.0.0, AGP8.13 default|
| Platform tools |37.0.1|
| Existing Gradle wrapper |8.14.3|
| Existing Android Gradle Plugin |8.13.0|
| Existing Capacitor Android |8.4.3|
| Startup target |Existing Android17/API37 x86_64 emulator|

Only official Adoptium/Google/Gradle components were downloaded. JDK and
command-line archive SHA256 and the wrapper-pinned Gradle distribution checksum
were checked. Portable tooling/Gradle cache are under
`outputs/milestone2/android-build/`; task-process environment variables select
them. No global PATH/JDK/SDK change, Android Studio, new system image/emulator,
npm upgrade or model-environment installation was performed.
Actual download/version/license records are in ignored
`outputs/milestone2/android-build/task-b1-report.md` and installation logs.

Actual commands, with the isolated task environment selected:

```powershell
# app/
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
npm.cmd run android:sync
# app/android/
.\gradlew.bat --no-daemon --console=plain --max-workers=2 assembleDebug
```

The local `outputs/milestone2/android-build/setup-toolchain.ps1 -Step gradle`
selects the isolated tools and runs the above wrapper command.
`gradle-build.log`: **BUILD SUCCESSFUL in3m54s**,93 tasks executed.

### Actual merged APK permission inspection

The APK declares and requests exactly:
`com.clashtracker.simulated.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`
with `protectionLevel=signature`, supplied by AndroidX. Zero dangerous runtime,
Internet, SYSTEM_ALERT_WINDOW, MediaProjection/capture or Accessibility-service
permissions are requested. Do not shorten this to "zero permissions": the
dependency signature permission exists. Dependency initialization/provider and
profile receiver entries are not game integration. No game/capture/input service
was added. Sources: APK `aapt` permissions/badging, merged manifest and merger
report in the same ignored log directory.

### Real startup, not just a Web preview

The APK was installed and its own Android Activity launched on the existing
API37 emulator. The actual WebView at `https://localhost/` rendered bundled
local assets; viewport411×914,DPR2.625. Device checks exercised:
`0/8→1/8(Witch)→2/8(Witch+Balloon)→Reset0/8→replay1/8`.
Mock-only boundary/footer, history/button states and no horizontal overflow were
checked. Saved screenshots include `android-device-screen.png`,
`android-second-event.png` and `android-reset.png`; the parent inspected the
actual2/8 image. There is no real recording/detector/game connection.

The first local verification assertion incorrectly expected English HUD names
while existing `card-display.ts` intentionally renders Chinese. Only the ignored
verification script assertion was corrected; its original failed log is retained
as `device-check-first-assertion-mismatch.log`. No App behavior was changed.
The completed rerun passes all five states. This is not a hidden product failure.

Pre-existing debug signing key bytes were checked unchanged. The emulator's
unrelated App package/data metadata and service snapshots were checked unchanged,
and its exact original foreground Activity restored. Only the mock package was
installed/used; it was stopped and the task WebView forwarding removed afterward.
No unrelated uninstall, data reset, settings change or game interaction.

Known non-blocking logs: generator flatDir/SDK XML/unchecked warnings and
emulator graphics/optional Bluetooth/skipped-frame messages. No own-App fatal
exception; this establishes minimal startup, **not mobile performance**.
Physical-phone installation and offline-on-device network-disconnection testing
are Not Run. Minimum/older Android version compatibility is not runtime-tested.

## TaskA1 — chronological review handoff, not confirmed GT

Existing CLI selected first24 fixed-stride source frames of natural_match_01,
at12.0..69.5s every2.5s, from preserved240-frame/4FPS benchmark `[12,72)`.
No card/confidence/ease-based selection and no other recording's pixels were used.
This is not a full-match exhaustive audit or a new model inference.

-24 full-resolution review PNGs,526 **pending** proposals,39 **UNVERIFIED** raw
  teacher labels. Four contact sheets / six frames per sheet.
- Existing reviewer, frame/source/PTS metadata, pending boxes, human-return
  template, chronological index, review instructions and count summary.
- Accept/reject/relabel/bbox-correction/missing-box and per-selected-class
  exhaustive review remain available without code/schema modifications.
- Predictions are separate and unchanged. Unknown/rejected/unmarked areas do not
  become Negative. Appearance continuity is not independent deployment;
  spawned/secondary units are not automatically card-play events.
- **Reviewed frames0; confirmed boxes0; confirmed classes0; primary classes0;
  spawned/secondary classes0; rejected0; relabelled0; corrected bbox0; added
  missing boxes0.** These values require real returned review, not teacher counts.
- No real human-return import, new revision/lock, training export or training.

Private final ZIP:
`outputs/milestone2/first-gt-batch/match01-first24-independent-review-v2.zip`,
16,452,557 bytes/46 members; SHA256
`bb6c4297a76c732b60a8907a589854420ec7d8d7d2922ee5d65c1a06cc1c99be`.
Detailed checks are in `outputs/milestone2/first-gt-batch/task-a1-report.md`.
The count-summary sidecar explicitly includes confirmed/primary/spawned-secondary
class arrays, all empty and pending actual confirmation, separate from the
strict human-return schema. Original v1 ZIP is preserved; only presentation
instructions/summary/packet manifest differ in v2, not image/proposal/return
bytes. Existing allowed note/origin/appearance fields can retain evidence-based
source relationships without inventing new strict fields.
It contains review images
which may show player UI; no video, weights or secrets. It is for the user's
explicit private review handoff, **not public redistribution**. No upload has
been performed. Archive checks do not establish rights clearance or image
authenticity. The strict CLI retains its legacy `outputs/milestone1/` output
namespace for the new batch; changing that restriction was unnecessary.

ChatGPT should return proposed decisions and actual uncertainty. The user's
confirmed relay can then supply truthful final review attestation; do not invent
a human reviewer to satisfy the strict importer. Validate the exact batch and
import into a fresh exclusive revision only after confirmation.
Review may be returned as a table for transcription; the strict template uses
the exact decision key `bbox_xyxy`, not a new `bbox` key. Generic "bbox" in
presentation instructions does not change that schema.

## Fresh checks and protected evidence

| Actual check | Result |
|---|---|
| App Vitest |43 passed,0 failed|
| App TypeScript / production build / Capacitor sync |exit0 each|
| Debug build / APK signature / merged manifest |PASS|
| Actual Android WebView five-state flow |PASS|
| Focused preannotation Python tests |51 passed,0 failed|
| Focused reviewer/UI Node tests |8 passed,0 failed/skipped|
| Strict batch and extracted-bundle CLI validate |exit0|
| ZIP CRC/member SHA / frame bounds/order/raw proposal checks |PASS|
| Existing offline environment `pip check` |No broken requirements found|
| Four batch inputs and193 prior Milestone1 files |unchanged|
| Fresh historical inventory32,217 files, both passes |all unchanged|
| Prior YOLOX source160 files, Attempt02 and benchmark outputs |unchanged|
| Offline/YOLOX/benchmark package inventories |unchanged|
| Private artifacts tracked / ignored output/toolchain checks |0 / PASS|
| Relative document links / credential pattern scan / diff check |85 valid / PASS / PASS|

The parent reran the existing protection helper against the original historical
SHA inventory and completed both local `protection-before.json` and
`protection-after.json` under `outputs/milestone2/`, exit0 each. All32,217 original
paths/bytes and160 YOLOX source hashes matched; Attempt02 files and benchmark
output files matched across passes. Benchmark output hashing excludes its
source/venv directories; the three existing Python environments were compared by
package inventory, not exhaustive venv byte hashing. These are this turn's actual
receipts, not the earlier Milestone1 test/receipt cited as fresh execution.
No historical true GT/lock/result was rewritten.

The parent also freshly repeated the51-test Python suite (6.09s) and8-test Node
suite, exit0, retaining output in `outputs/milestone2/preannotation-python.log`
and `preannotation-node.log`. APK/ZIP SHA256 and extracted-v2 strict validation
were independently checked. A read-only internal artifact/docs reviewer checked
scope, hashes, permissions, screenshots and all45 manifest-bound ZIP members;
no unresolved Critical/Important issue. This is **not ChatGPT's independent
visual GT review**. Generic bbox wording is clarified by the strict template
key above; no source/schema or original ZIP was changed to address it.

Not Run: full908-test historical offline suite (no offline source/package change;
fresh focused tests used), ESLint (no script configured), real GT confirmation/
import, model training/inference, physical phone, live game, real HUD, Release
build/signing, main integration or external upload. Prior test totals are not
presented as fresh execution.

## Stop and Git

Public changes are documentation only. The local feature branch remains pending
user stage acceptance, with no push/main merge. Old feature branches/results are
preserved. TaskB1: `CLASH_TRACKER_FIRST_APK_READY`; TaskA1: packet ready, actual GT
pending. Next authorized action is independent review and returned confirmation,
not automatic training or a new milestone.
