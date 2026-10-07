# Milestone 2 — Debug APK, multiclass review batches and phone-test boundary

Milestone2 closeout is recorded first; the original APK/pending-review checkpoints
and first-batch freeze below remain historical evidence. They are not detector
accuracy, training readiness or real-game HUD acceptance. ChatGPT is the visual-
review basis, not a human reviewer; the user supplied the human attestation.

## Final closeout — second user-attested GT and user-reported phone smoke

Verified2026-10-07; start `cbc6dd7872d05bef48e2a157c5a1a2e608564584`, branch
`codex/milestone2-apk-and-first-gt`. Authorized only: transcribe the user's exact
batch02 decisions through existing tooling, freeze a new annotation-only lock,
record the user's six phone checks, update public status and hand off. No public
implementation/schema/dependency/App change, decode, extraction, visual relabeling,
inference, training, device operation, environment installation, merge or push.

Private operation/evidence directory:
`outputs/milestone2/second-gt-confirmation-v1/`.
Source user-authorization attachment SHA256:
`93092a05b31a558aa1e058fb5453abbc354e8e6dac8b2065e3bb09a6f06dbed6`.
Structured decisions, strict return, identity/coverage supplement, command logs,
JUnit outputs, B2 attestation and Completion Report stay local/Git-ignored.

### Actual batch02 freeze and readback

Revision: `outputs/milestone1/milestone2-second-multiclass-human-gt-v1/`.
Lock: `second_multiclass_human_gt.snapshot_lock.v1.json`.
File SHA256: `4a2bf638855d18b6d00ddc35738c3b4f2cdc5a460837364989e552d169d986f8`.
Canonical lock digest:
`3d2434359155d7fc8ce35ffa530e4be8950250beb2f43bd6557b88c375868195`.
Nine SHA-bound members plus lock: original strict human-return, imported GT and
receipt, exact user attestation, identity/coverage supplement, first-lock reference,
review summary, object-review CSV and frame-review CSV. No copied original PNGs,
modified source proposals, frozen first-lock members or new training dataset.
First lock file SHA remains
`7d4a9a7fafd627f1fbf82f73db3d66232163e5aac14dbdc8f5996c2c0b3a9dae`.

| Confirmed batch02 visual class | Boxes | Owner | Canonical mapping |
|---|---:|---|---|
| `visual.unit.minion` |13|opponent|`unit.minion`|
| `visual.unit.flying_machine` |8|opponent|`unit.flying-machine`|
| `visual.unit.royal_hog` |5|opponent|`unit.royal-hog`|
| `visual.unit.golden_knight` |5|opponent|`unit.golden-knight`|
| `visual.structure.mortar` |4|own|`building.mortar`|
| `visual.structure.cannon` |3|opponent|null|
| `visual.effect.barbarian_barrel` |1|opponent|null|

24 inspected frames,39 accepted original boxes on21 frames,0 rejects,452 remaining
pending/unknown. New classes: Flying Machine, Royal Hog, Barbarian Barrel visual.
All form/origin fields unknown; no class/bbox change or missing box addition.
Four accepted objects override raw teacher owner=own to human owner=opponent;
raw teacher fields/file bytes remain unchanged. This is a metadata correction,
not teacher mutation. Exact source PTS/manifest/predictions/config/packet are bound.

Reviewer=user; actual_human_confirmation=true, human_review_attested=true,
review_basis=chatgpt_visual_review,
confirmation_source=user_attestation_based_on_chatgpt_visual_review.
Strict schema unchanged; additional facts live in separately SHA-bound files.
The five explicit appearance groups are retained.18 Minion/Royal Hog tokens are
observation-only, identity-unresolved, not18 new entities/independent deployments;
no cross-batch identity is inferred. Length of appearance_groups is not event count.
Primary/spawned roles are not newly inferred from labels or mappings.

Only9 explicit frame/class coverage rows are emitted: Minion117/119.5/122s
exhaustive positive; Royal Hog77/79.5/82s and Minion84.5/124.5/127s unresolved/
positive-only. Positive acceptance elsewhere is not an exhaustive absence claim.
No unlisted teacher proposal, reject, missing region or Unknown is background or
Negative. Class-specific negatives and independent card plays remain0.

Cumulative two separate snapshots:48 chronological inspected frames,83 accepted
boxes on44 frames,9 classes,7 unique non-null mappings,932 pending and2 historical
rejects, one underlying match only. Minion28, Mortar14, Flying Machine8, Cannon8,
Golden Knight7, Witch6, Skeleton Barrel6, Royal Hog5, Barbarian Barrel1.
This is not a merged Training Dataset or cross-match model-quality evidence.
training_qualified=false; ordinary_training_export_allowed=false; rights remain
unverified. Match02 remains mid-match truncated/training-excluded, not Negative.

### Actual commands and scoped checks

```powershell
.\.venv\Scripts\python.exe -B -m pytest tools/preannotation/tests outputs/milestone2/second-gt-confirmation-v1/test_transcription_contract.py -q --tb=short --junitxml=outputs/milestone2/second-gt-confirmation-v1/final-regression.xml
node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py prepare
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py validate-cli
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py import-cli
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py seal
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py refuse-overwrite
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-confirmation-v1/transcribe_and_seal.py verify
```

Actual final regression: **59 passed in8.68s** (51 existing preannotation tests +
8 private transcription/logging checks); Node **8 passed,0 failed/skipped**.
Existing strict CLI validate/import exit0; actual second import to the existing
revision exit2 and full10-file SHA set unchanged. New lock canonical/member,
return/GT/receipt/summary/first-reference/CSV readback passes.

The initial forbidden-overwrite log capture failed because the child emitted a
Chinese Windows file-exists error in CP936 while the private helper assumed
UTF-8. The already completed import/lock was not damaged. A real-child regression
reproduced the decoding failure; only the new ignored helper's output capture
was changed to preserve bytes. Fresh59-test run and byte-safe overwrite recheck
pass. Initial empty/failed logs and failing JUnit record remain, not replaced;
recheck files have new names. Public CLI, data and locks were not patched.
No training, inference, screenshot generation or failed-experiment rerun occurred.

Full historical offline-video suite, TypeScript/App tests/build, Capacitor sync,
APK rebuild and agent phone test are **Not Run this closeout**, because public
code/dependencies/App are unchanged. Prior passing totals above/below are historical,
not claimed as fresh results. The new private GT is verified by the actual existing
CLI plus scoped tests, exclusive-lock/CSV/source-hash readback and protection audit.

### Fresh closeout protection / dependency / privacy evidence

The before/after audit uses the same fixed1,360-file map: historical1,280-file
union plus all34 original second-bundle files and46 original second-stage files.
All hashes and directory memberships are unchanged, including first GT9 files,
complete Attempt01(43) and Attempt02(92),four MP4s,teacher/pinned source code,
weights/settings/review packets and existing APK. No old audit helper/receipt
was rerun or overwritten. Shared observed-map canonical SHA:
`7f22d48714646cf33e0e4db1823a580991b124eda36996e51379fe4f3c52ab87`.

New immutable private receipts under `second-gt-confirmation-v1/protection/`:
before SHA `8714bdbcb4cfa26614aa2fc7ab1c14da04bad8ff6cdc465f6ee9300fcdc90fcc`;
after SHA `00a93fd029a2394b25789b5c43e6c415c80ac7dc7a11e05d2182c7a3a286d788`.
Both PASS,errors0; raw three-environment inventories before→after equal at fixed
HEADcbc6dd:offline13,YOLOX22,benchmark41. Fresh `pip check` exit0 in all three,
"No broken requirements found." No environment change/install. The offline
editable checkout reference may advance only with the later docs-only commit;
that is Git metadata, not a package update. Pinned KataCR36ceb9f remains clean.

After audit checked1,397 protected/new/reserved private paths,all Git ignored;
tracked private/media0. New GT/return/CSV/logs/receipts remain ignored; public
diff is exactly four documentation files. No SQLite/config/dependency/App code,
private recording/PNG/index/report/weights/credential/signing material is staged.
The fixed audit is deliberately bounded, not a claim of hashing every venv/cache
file. Final checks:87 relative Markdown links exist;added public text secret/
private-path pattern scan PASS;all37 new private files ignored;tracked private/
media/weights/signing files0;`git diff --check` exit0. Public diff remains exactly
four documentation files. Only a local checkpoint follows;no push/main merge.

### TaskB2 — user-reported physical-phone result, not an agent retest

Status: `REAL_DEVICE_SMOKE_TEST_PASSED`, evidence_type=user_reported_physical_
android_device_smoke. User confirms APK install, App launch, Witch mock, Balloon
mock,2/8 and Reset0/8. Recorded in the new private
`b2-user-attestation.v1.json` and `B2_USER_REPORTED_SMOKE.md`; historical pending
reports remain unchanged. The unchanged local APK SHA is
`774ed13e2ac69690330cf126084aee15b19ecf676e579a1872eaa7e37ea6bb0d`.
Phone-installed checksum was not independently collected. No phone model/Android
version, detailed layout/gesture, cold-start/restart or performance report exists;
do not fill these as tested. No new ADB listing/install/launch/log collection,
App code change/rebuild or phone automation was performed this closeout.
The six reported passes establish mock-only smoke, not real-game integration,
live detector, true HUD, offline-network qualification or device performance.

The original permission inspection remains applicable to the same unchanged APK:
only AndroidX's own signature receiver permission, no Internet/capture/cross-app
overlay/Accessibility/game-input ability. No new permission or Module3 is enabled.

Stop with Milestone2 Completion Report. A future observation→confirmed card-play
bridge requires separate authorization; this closeout does not implement it.

## Historical original scope and baseline

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

## Follow-up — TaskA2 second pending batch and TaskB2 phone-test preparation

Authorized2026-10-07; startHEAD `fc0df2137e048640f200e5a412f9ddad81a42b90`,
same `codex/milestone2-apk-and-first-gt` branch. No new design, production source,
schema, dependency, App/Android build or training change. Only four public
state/verification documents are synchronized; preparation helpers/artifacts
remain private ignored files. No main merge or push.

### A2 actual chronology and one-shot proposals

First batch ends69.5s; old benchmark ends71.75s. The next24 fixed2.5s targets
are72..129.5s, all actual source PTS equal their requests. PTS6480000..11655000,
step225000,timebase1/90000,source432×960,origin0. No prior frame overlap;
only natural_match_01 pixels are used, no quality/class/confidence selection.
Four original recordings are protected by hashes, not newly reviewed.

New wrapper/config are exclusively created in
`outputs/milestone2/second-gt-and-real-device/a2-proposals/`. Full source audit
and read-only preflight precede generation and bind protected source/weights/
runtime/source commit plus config/script SHA. The helper does not import the
old wrapper (which changes old settings). New settings/cache/temp are local to
the new directory, bytecode/network disabled, training/val/track/control imports
blocked. These are process guards, not an OS sandbox or rights clearance.

Actual single generation command,exit0:

```powershell
.\outputs\existing-multiclass-benchmark\katacr-20261007-01\venv\Scripts\python.exe -B outputs/milestone2/second-gt-and-real-device/a2-proposals/generate_proposals.py
```

24 samples,878 per-detector boxes→502 merged→11 fixedUI removals→491 pending
proposals,48 raw teacher labels including UI/noise. CUDA1050Ti parameters used;
no weights training/modification or accuracy judgment. Preserve confidence0.1,
ROI[8,67,422,729],CUBIC canvas576×896,imgsz896,FP32,per-detectorNMS0.7,maxdet300,
dual class-agnosticNMS0.6 and original fixedUI rules. No parameter tuning/rerun.
New median376.34ms/P95608.22ms is offline preparation timing, not mobile/real-time
qualification. Three network attempts denied; old settings/environment preserved.
Prediction SHA256 `81d23490a9b045276af14122a338b9568aebe77d34ade6a893dc3a89fa643951`;
config SHA256 `6534c59ee9b48d8bc31cc09f54850725383ae85f603a18d85844c67a6e395b38`;
wrapper SHA256 `88bdca49a830053c5eb4f822cbc52473b943713e6120561cf41ae1714055ff68`.

Diagnostics retained: `NMS time limit 2.050s exceeded` once and a new local
Matplotlib font-cache notice. All24 frames complete, but no exhaustive teacher
coverage claim is made; manual missing-box/class-specific exhaustive review is
still necessary. Logs/summary/network denials are inside the review ZIP, not
silently discarded. No completed prediction run is retried for better candidates.

Actual existing prepare/validate and presentation-only pack commands,exit0 each:

```powershell
.\.venv\Scripts\python.exe -m tools.preannotation prepare --format generic --predictions outputs/milestone2/second-gt-and-real-device/a2-proposals/detections.json --config outputs/milestone2/second-gt-and-real-device/a2-proposals/proposal-config.json --inventory outputs/module2b2/data-preparation-20261005-9957a75d15744495935bb2fd67f07ac6/pending-dataset.v3.json --stride 1 --max-frames 24 --out outputs/milestone1/milestone2-second-review-batch02-v1
.\.venv\Scripts\python.exe -m tools.preannotation validate --bundle outputs/milestone1/milestone2-second-review-batch02-v1
.\.venv\Scripts\python.exe -B outputs/milestone2/second-gt-and-real-device/pack_second_batch.py pack
```

New source PNGs are decoded only for this next batch; no old frame is regenerated.
Bundle digest `e2e9e435ce8fc953d2e26ba295c1d1d7fd7bda537ce3e4a94da3adf293cf98ac`.
Package `outputs/milestone2/second-gt-and-real-device/Module_2_Milestone2_Second_Multiclass_Human_Review_Bundle_v1.zip`:
15,658,177 bytes,51 members,24original PNGs,4contact sheets,existing reviewer,
exact metadata/pending boxes/raw teacher/config,blank return,instructions and
original generation diagnostics. ZIP SHA256
`ab0e75f613bab96936f0c03434b9dabea1a92736ab6baf79c45f7851fae6ecaa`.
CRC,unique/safe member paths,manifest/each-member SHA,file-byte equality,exact
PTS/source bounds,counts and blank-attestation readback pass. Contact sheets are
new thumbnails only; parent visually checked first sheet layout, not object GT.
A separate read-only internal artifact audit also checks all50manifest-bound
members,51ZIP paths,35page resources,reviewer assets byte-equal to existing code,
zero prior frame overlap and blank confirmation; final readback exit0, no
blocking finding. This is not ChatGPT's visual/human review. The audit's initial
string-only JSON/LF assumptions were too strict for valid key order/WindowsCRLF;
semantic and original-byte checks establish validity, not an artifact rewrite.
Packet source images may contain player UI; private user-controlled review only,
no external upload or public Git/release,video/weights/APK/signing material in ZIP.

New batch inspected/confirmed/rejected/relabelled/corrected/missing-box counts
remain0;491 pending,confirmed classes/primary/spawned role arrays empty.
reviewer blank,actual_human_confirmation=false,human_review_attested=false;
old44 confirmed boxes/6 classes are separate historical reference only.
Unknown/reject/unmarked/teacher absence are never automatic Negative. Mapping
uncertain=null; no identity/deployment inference or card events;match02 remains
training-excluded. No human-return import,new GT lock,training export or training.

### B2 actual device check and install handoff

Fresh `adb devices -l`,exit0: physical0,emulator1. Parent independently repeats
the device listing,APK hash and aapt permission inspection. Emulator evidence
from B1 is history and is not rerun or counted as a real phone. Status
`REAL_DEVICE_TEST_PENDING_USER`; no install,launch,log collection,manual touch,
layout or cold-start check performed on a phone. Existing APK size3,977,891 bytes,
SHA unchanged `774ed13e2ac69690330cf126084aee15b19ecf676e579a1872eaa7e37ea6bb0d`.
Package `com.clashtracker.simulated`,.MainActivity,v0.1.0/code1,minAPI24,target36;
only own AndroidX signature receiver permission,not zero total permissions.
No Internet,capture,overlay,Accessibility,game/input control capability added.

Two installation paths and nine-step user checklist are in private
`b2/INSTALL_AND_CHECKLIST.md`: local USB file transfer/manual install,or existing
adb explicitly targeting the user's real phone serial. Do not bypass unauthorized
devices/signature failures or uninstall/clear data. Agent adb scope is install,
own-App launch and own-process logs only;no input/force-stop/screenshot/settings.
Manual Witch1/8→Balloon2/8→Reset0/8,replay,layout,background resume and true
process-cold-start checks remain Pending. Memory-only newJScontext expects0/8;
resume may retain state and is not evidence of cold restart. User must supply
actual device/Android version/install and touch results; no phone success claim.

### Fresh focused checks, protection and stop

Fresh Python `pytest tools/preannotation/tests -q --tb=short` with JUnit output:
51 passed,0failed/skipped,19.08s. Node reviewer/review-ui tests:8passed,0failed/
skipped. Commands/output evidence is in the new private `focused-test-evidence.md`
and `preannotation-regression.xml`, not an old test result reused as fresh.
No public implementation/schema change; proportional tests and exact artifact
readback used. Not Run: full historical offline suite,App unit/type/build,
Android rebuild,physical phone,training,new human-GT import,later modules/liveHUD.

Before/after main protection receipts both PASS:1,261 fixed existing paths,
including firstGT9files,all236 pre-existing Milestone1 files,confirmation19,
A1packet117,original4videos,Attempt02,selected pinnedKataCR67source files and
installedUltralytics189source files,old settings,weights and APK. Directory
membership and each byte hash remain unchanged. A separate append-only receipt
extends checks to fullAttempt01's43files and3 actual Development/GT/Training
locks; union1,280 unique protected old files all match historical/before hashes.
The original1,261-path receipts are not overwritten by this extension.

Fresh after `pip check` passes for offline/YOLOX/benchmark; their13/22/41package
inventories before→after are raw identical. No installations/upgrades or new
model environment; do not claim exhaustive venv byte preservation. Hygiene at
the final protection receipt checks1,280 old+78 new=1,358 unique private paths,
all Git-ignored,tracked private/media0. Paths added later for the stage report
receive a separate final ignore check. Protected selected-source/artifact audit
is not a new full32,217-file rehash. Historical908-test totals are not current.
Private protection logs/receipts are under the new task directory `protection/`.

Changed-document relative links87valid/0broken; credential-pattern scan0matches;
`git diff --check` exit0. Only README,CURRENT_STATE,DEVELOPMENT_PLAN and this
verification document change in Git. New source/prediction/image/return/ZIP,
checks and device handoff stay ignored; App/preannotation/model code unchanged.
A focused local docs checkpoint records the candidate/device-pending stage;
no push,main merge,new split/training or later module. Stop for ChatGPT suggestions
plus explicit user confirmation,and actual physical-device feedback.
