# Milestone 2 — Debug APK and first multiclass review batch

Original APK/review-packet checkpoint verified locally on2026-10-07; its record
below is retained with its original pending-GT boundary. The later user-attested
first-batch confirmation/import and annotation-only freeze are recorded in the
follow-up section below. Neither checkpoint is detector accuracy, training
readiness or real-game HUD acceptance. ChatGPT is the visual-review basis, not a
human reviewer; the user supplied the explicit human attestation.

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

## TaskA1 — original chronological handoff, before user confirmation

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

## Original checkpoint checks and protected evidence

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

## Original checkpoint stop and Git

Public changes are documentation only. The local feature branch remains pending
user stage acceptance, with no push/main merge. Old feature branches/results are
preserved. TaskB1: `CLASH_TRACKER_FIRST_APK_READY`; TaskA1: packet ready, actual GT
pending. Next authorized action is independent review and returned confirmation,
not automatic training or a new milestone.

## Follow-up — user-attested first multiclass visual GT frozen

On2026-10-07 the user explicitly confirms the ChatGPT visual-review suggestions
as their own human attestation. This follow-up uses local HEAD
`afd3701fdae2e0ea6087c240ee729c24913b10fb` on the same feature branch, with
unchanged public tool/App/model source, contracts, dependencies and environments.
It does not rerun image review or ask for a new confirmation. The machine audit
checks accurate transcription of the user's supplied decisions, not visual truth.

### Reviewer and evidence boundary

Record actual_human_confirmation=true, human_review_attested=true, reviewer=user,
review_basis=chatgpt_visual_review and
confirmation_source=user_attestation_based_on_chatgpt_visual_review. The strict
human-return provenance remains compatible; extra attestation facts, user
decisions and identity/coverage explanations are separate SHA-bound members.
ChatGPT is never labelled a human reviewer or a direct user visual inspection.

The original24-frame bundle, its526 teacher proposals, PNGs, return template and
both private review ZIPs remain byte-identical. Accepted bboxes are copied from
the exact original proposals without edits, relabel actions or new boxes.

| User-confirmed visual class | Accepted boxes | Canonical mapping | Owner |
|---|---:|---|---|
| visual.unit.minion |15|unit.minion|opponent|
| visual.unit.skeleton_barrel |6|unit.skeleton-barrel|own|
| visual.structure.mortar |10|building.mortar|own|
| visual.unit.witch |6|unit.witch|opponent|
| visual.unit.golden_knight |2|unit.golden-knight|opponent|
| visual.structure.cannon |5|null|opponent|

Totals:24 inspected frames,23 frames with accepted objects,44 accepted boxes,
6 classes,5 non-null unique mappings,2 explicit rejects and480 pending/unknown
proposals. Including rejects, unresolved_regions contains482 records. Skeleton/
Skeleton Evolution and all unlisted proposals remain pending, not class-confirmed,
automatically rejected or background. All accepted form/origin values stay unknown.
Cannon confirms visual structure only, never its source card.

Only the four explicit user appearance assignments are retained: Skeleton Barrel
12..22s and57s, Mortar29.5..52s and Cannon-like59.5..69.5s. The remaining23
observations use explicitly unresolved observation-only tokens to satisfy the
legacy identifier field; no cross-frame entity/deployment inference is made.
Golden Knight's two frames are not merged. Neither the identifier count nor the
appearance_groups dictionary length is an independent entity/appearance/play
count. Primary/spawned class roles were not attested and are not inferred from
canonical mappings; preserved historical spawned relationships remain unchanged.

Coverage has38 class-specific rows:32 user-exhaustive positive rows and6
unresolved/positive-only rows. Minion17s and Skeleton Barrel59.5s keep missing
objects unresolved without inventing bboxes; Witch44.5/47s keep crowd/occlusion
uncertainty; Golden Knight44.5/52s is positive-reviewed only. Every other frame/
class combination makes no absence claim. Actual derived negative_evidence=[],
card_events=[] and independent_deployments=0: eligible negatives/card plays are0.

### New private, annotation-only snapshot

Exclusive revision: `outputs/milestone1/milestone2-first-multiclass-human-gt-v1/`.
Lock: `first_multiclass_human_gt.snapshot_lock.v1.json`.

- Lock file SHA256:
  `7d4a9a7fafd627f1fbf82f73db3d66232163e5aac14dbdc8f5996c2c0b3a9dae`.
- Canonical lock digest:
  `82f27b0905d5a597a2564e37926470497b92b0a16cc353a02f2b1e01e192ad93`.
- Strict human-return file SHA256:
  `fc27ed028b0341816e1f6948b2380b2ca6574fa62ce9206a3b416935a0b8ae52`.
- Reviewed annotations file SHA256:
  `c00bcc6d7fedd25c1593c6e234c5a4ecd8b1edff88fd8ea88661ee25818d0ebf`.

Nine revision files: the seal plus eight SHA-bound members (strict return,
annotations, import receipt, user attestation, identity/coverage supplement,
summary, object CSV and frame/class-coverage CSV). Bind the existing source-bundle
manifest, bundle/prediction/config/packet identity and all24 exact PTS/frame
metadata; source recording and teacher files stay outside the new revision.
The46-row object CSV contains only44 accept and2 reject decisions; the38-row
coverage CSV is not falsely presented as24 fully exhaustive frames.

Status: USER_ATTESTED_VISUAL_GT_FROZEN. This is an annotation-only snapshot, not
a Training Dataset, Model or Test GT Lock. training_qualified=false and
ordinary_training_export_allowed=false. There is no new training/blind split.
Rights remain unverified. Exclusive create, content digests and readback guard
against accidental replacement, not OS write protection, legal clearance or
independent authenticity certification. Any later correction needs a new version.

### Fresh follow-up verification

Actual commands from the repository root:

```powershell
.\.venv\Scripts\python.exe outputs/milestone2/first-gt-confirmation-v1/transcribe_and_seal.py prepare
.\.venv\Scripts\python.exe -m tools.preannotation validate --bundle outputs/milestone1/milestone2-first-review-batch01-v1 --return outputs/milestone2/first-gt-confirmation-v1/user-confirmed-human-return.v1.json
.\.venv\Scripts\python.exe -m tools.preannotation import --bundle outputs/milestone1/milestone2-first-review-batch01-v1 --return outputs/milestone2/first-gt-confirmation-v1/user-confirmed-human-return.v1.json --revision outputs/milestone1/milestone2-first-multiclass-human-gt-v1
.\.venv\Scripts\python.exe outputs/milestone2/first-gt-confirmation-v1/transcribe_and_seal.py seal
.\.venv\Scripts\python.exe outputs/milestone2/first-gt-confirmation-v1/transcribe_and_seal.py verify
.\.venv\Scripts\python.exe -m pytest tools/preannotation/tests outputs/milestone2/first-gt-confirmation-v1/test_transcription_contract.py -q --tb=short
node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs
git diff --check
```

Prepare/validate/import/seal/readback all exit0. Focused Python regression:
53 passed,0 failures/skips (51 existing tool tests +2 private transcription
tests),19.50s; Node8 passed,0 failed/skipped. Repeating import into the existing
revision returns2; all9 files remain unchanged afterward and readback still
passes. A read-only internal artifact audit independently checked exact IDs,
bboxes, owners/mappings, pending complement, coverage, CSVs, eight member hashes,
lock digest and receipt-derived GT; no blocking finding. This is not another
ChatGPT visual review.

The preflight's initial temporary-script error used video_origin_seconds instead
of the existing bundle's source_origin_seconds_exact. Both private regression
tests reproduced the KeyError before repair; the one-field correction passed
both tests, then the53-test run. No return/import/GT write occurred before that
preflight repair. No producer, extraction algorithm or original evidence changed.

Fresh before/after protection rehashes874 fixed existing files, including old
locks/module JSON,4 original videos,227 previous Milestone1 files,92 Attempt02
files,65 benchmark outputs, A1 packets and inputs; groups overlap,874 is the
deduplicated total. All match historical expectations and each other. It is not
a fresh32,217-file audit or an exhaustive venv-byte comparison. The after receipt
checks898 private paths, including all9 new revision files, ignored; tracked
private/media=0. All three pip checks exit0, no broken requirements. Package
inventories before→after are identical (offline13, YOLOX22, benchmark41); an
older checkpoint's offline editable VCS reference differs solely with checkout
HEAD, not a dependency installation/upgrade.

Fresh relative-link checks:87 valid/0 broken; public credential-pattern scan0;
scoped diff check passes. Private logs/receipts and the final report are under
`outputs/milestone2/first-gt-confirmation-v1/`, excluded from Git. All original
evidence is retained; no new extraction, inference, annotation guesses, install,
training or App build/runtime change occurred.

Not Run this follow-up: historical908-test full offline suite, App/build/device
checks, ESLint, new visual review, training/inference or later module. Public
changes are only five state/verification documents; fresh focused regression and
artifact/protection checks match this data-only scope. APK runtime evidence above
is the preserved prior checkpoint, not re-executed now.

Stop with the first user-confirmed visual-GT batch frozen. A focused local docs
commit records the checkpoint on the feature branch; no push, main merge or
later milestone. Old feature branches, locks and experiments remain preserved.
