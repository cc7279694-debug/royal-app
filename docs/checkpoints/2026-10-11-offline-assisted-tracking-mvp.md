# Offline Assisted Card Tracking MVP — local acceptance checkpoint

Date:2026-10-11. Start HEAD `1d0856217fed7a01384e5502c20826e52944e6c5`.
Branch `codex/offline-assisted-tracking-mvp`; main stays `602dd0f...`.
Local implementation handoff only, not independent acceptance or release. The local
commit containing this checkpoint is the delivery; no main merge or remote push.

## Delivered behavior

- Existing frozen real detector predictions/observations/formal candidates supply
  a separate private review export, not Human GT or invented automatic events.
- Fixed review filter exports18 opponent supported STRONG/MEDIUM candidates from
  1,188 first-match candidates:14 STRONG,4 MEDIUM. Exclusions903 owner-guard,
  267 unsupported mapping,0 insufficient evidence; no GT time-window filtering.
-47 native432x960 JPEGs are bound to exact source PTS/time-base/dimensions, source
  boxes and source hashes. First/middle/last actual observations per candidate,
  not interpolated imagery; max3 support references. Confidence is maximum source
  detector confidence, not calibrated event probability. Packet is5,565,445 bytes.
- Private packet SHA `99c3337e6f4e5d35fcaffdf4ed1360629aeda1af3c44a944beef2439c0e41af0`.
  Private assistant review SHA `ed09e32704176f5c521229f461a744bbbadbcefd0bcfc29bb96cd474faf8b5e2`.
- App Assisted mode validates/imports local JSON+embedded JPEGs. All items pending;
  explicit confirm/exclude/restore/correct/manual actions remain separate from raw
  predictions and formal events. Confirmed opponent cards deduplicate to8 slots;
  repeat records and visible overflow remain. Mock/Recorded contracts unchanged.
- Review state is memory-only. Mode switch/reset/reopen/reimport clears decisions,
  visibly disclosed; no persistence/backups/storage migration is claimed.
- Geometry closure SHA `02367a06abcc4b6ffc1e2dfd58a51d5b48d1ef189627539ad170b478165ebf56`:
  TO017 and GB07 6.018/6.676 assistant-provisional; four other display items unknown.
  All remain bbox_verified/training_qualified=false; old locks not edited.

## Real evidence and honest limits

Controller actually viewed all18 evidence sheets at original detail.14 support a
visual/card hypothesis,1 false Witch mapping,3 unresolved owner/class/occlusion cases.
Two pairs may concern the same cohort; do not count14 independent card plays.
This is assistant review under delegated routine authority, not Human GT or new
pixel/onset verification. Imported packet deliberately contains no confirmed rows.

The unchanged frozen event evaluation is still2/5 and1 Royal Hogs duplicate.
Three unmatched known windows have early same-class outputs, not demonstrated
total detection absence. Four unresolved windows remain non-negative. Full-match
FP/min, whole-match missed card counts and cross-match performance remain unknown.
The three current priorities Hog Rider/Goblin Barrel/Firecracker are not mapped
by the retained engine; App manual entries are labelled manual, never model support.

## Verification actually run

- `npm.cmd test -- --reporter=dot`:145 passed,9 files. Fresh TypeScript/Vite build
  and `npm.cmd run android:sync` exit0. `npm.cmd ls --depth=0` exit0.
- `python -B -m pytest tools/assisted_tracking/tests tools/detector_events/tests tools/event_engine/tests tools/deployment_review/tests tools/preannotation/tests -q --import-mode=importlib --tb=short`:
  315 passed,1 existing Windows permission skip. Includes16 exporter tests and
  existing formal engine/detector/deployment/preannotation regression.
- Private geometry tests separately:3 passed. A combined importlib invocation
  initially failed to collect the private helper; separate normal-mode run passed,
  without altering production or weakening tests.
- `python -m pip check`:no broken requirements.
- Actual rendered mobile workflow390x844 and320x568:real import0/8; five operator
  confirmations5/8; duplicate record count6, still5/8; exclude, correction to
  unknown, manual pending/explicit confirmation, bad import retaining state, reset,
  reimport and mode isolation passed. Native JPEG loaded; no page errors/external
  requests during successful QA. QA decisions are not user acceptance or Human GT.
- Local read-only code review:16 exporter tests and43 Assisted tests passed,
  no blocking findings. It is not ChatGPT independent acceptance.
- Fresh protection audit compares5,692 historical SHA values unchanged;34 precise
  closure files additionally captured; total5,726 files used in end-guard.
  Formal engine/adapter/offline/native/dependency selected115 files unchanged.
- No fresh full offline-video908-test run: extractor is unchanged and source
  protection plus directly affected regressions are used. No training/inference
  rerun or real device user acceptance in this task.

## Android artifact and bounded verification

- Private Debug APK: `outputs/offline-assisted-tracking/android/clash-tracker-assisted-debug.apk`.
  4,070,269 bytes; SHA-256
  `7d278add5ea903d652249604a39d22abf5ae653682cc5db3779cbaa1a4a146e2`.
- `gradlew.bat --offline --no-daemon --console=plain --max-workers=2 assembleDebug`:
  exit0, BUILD SUCCESSFUL in41s,93 tasks. Retained Temurin21.0.12.1+1,
  Android platform36 rev2,build-tools35.0.0,Gradle8.14.3; no installation/upgrade.
- Source Manifest has0 uses-permission; merged APK only AndroidX's own signature
  `com.clashtracker.simulated.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`. No Internet,
  capture, overlay, Accessibility or input-control permission. Bundled Web assets
  match the current dist; no private media, packet, GT or weights bundled.
- The initial isolated API37 clone installed/launched and Mock0/8→2/8 passed,
  but system ANR/crash dialogs blocked the document picker. A separate fresh API36
  instance installed/launched and native DocumentsUI displayed the real JSON.
  Later own-App WebView QA timed out; no receipt establishes whether it was during
  mode selection or after file delivery. Final screen was Mock0/8, cause unknown.
  It is not established as either an App defect or emulator-only instability.
  Native Assisted import/confirmation is **not verified**.
- Both task-owned emulators/forwards closed; old AVDs and all generated evidence
  retained. No user device/system settings were changed. Physical-phone test Not Run.
  Read-only code/browser/build checks do not substitute for native user acceptance.
- The first ignored build runner interpreted SDK XML stderr as terminating;
  only its output handling was corrected. Same native build command passed, with
  the interrupted warning log retained; no production/Gradle changes.

## Data, files and next boundary

New public code: `tools/assisted_tracking/`, `app/src/assisted/`, review UI/tests.
Minimal existing App/display/styles integration; current-state/decisions/plan/readmes
and this checkpoint. No SQLite, migration, dependency, manifest, Gradle or engine
change. Private outputs include candidate JSON/images, geometry closure, assistant
review, QA screenshots/logs and Debug APK; none is public Git content.

Known non-blocking contract limit: producer and App ID/array/dimension bounds are
not all identical; this verified real packet lies in their valid intersection.
Do not advertise arbitrary exporter-valid packets as universally importable.

Stop after local commit at independent acceptance. Preserve historical failures,
locks and all unknowns. No push/merge/release or automatic next milestone.
