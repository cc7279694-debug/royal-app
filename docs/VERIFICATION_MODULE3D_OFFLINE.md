# Module 3D-Offline — Android Recorded Event Replay

Verified2026-10-08 from published main/origin/main
`293e26e00c2d2418fc78f2b2177f7780197d37f6`, feature branch
`codex/module3d-offline-recorded-replay`. This is an offline App demonstration,
not detector integration, live gameplay recognition or independent device acceptance.

## Implemented behavior and boundaries

- Reuse the existing `OpponentCardPlayed` contract, reducer, discovery slots,
  history and Mock Witch/Balloon interface. Only extend UI/source/replay support.
- Local JSON import through Android's native document picker, without a native
  storage plugin or broad filesystem permission. Strict envelope/event validation
  rejects wrong format, duplicate IDs, unknown cards, nonfinite/negative/over-one-day
  times and oversized files. Errors preserve the loaded state, paused.
- Start/pause/resume/restart,1×/4×, chronological history and0/8→5/8. Duplicate
  plays of one card add history, not slots. Mode switching resets/cancels the old
  source. Visibility loss pauses. State/import deliberately remain in memory;
  refresh/cold restart requires reimport. No SQLite/schema/migration/data-store change.
- UI says **离线 Oracle 回放** and real-game HUD remains closed. No recording,
  detector/model, game/network interaction, overlay/capture/accessibility/input
  control, card-cycle/evolution/elixir or later-module behavior.

## Frozen engine source and private offline selection

No real Oracle replay/evaluation was rerun. The exporter reads the frozen repair
replay/evaluation, validates manifest member hashes and evaluation→replay binding,
then selects each successful score's actual `matched_event_id`. The complete
five-matched/four-unscored partition is checked before writing an exclusive new
output directory. Engine IDs, card IDs and timestamps are copied from replay,
never from GT timestamps or fabricated from candidate answers. Event GT is not
loaded by this exporter or sent to the App. No event-engine production file changes.

| Selected engine card | Engine first-seen seconds | Engine confirmed_at seconds |
| --- | ---: | ---: |
| Witch | 32 | 34.5 |
| Royal Hogs | 77 | 77 |
| Flying Machine | 79.5 | 79.5 |
| Golden Knight | 104.5 | 104.5 |
| Minions | 117 | 117 |

All selected events are from match01. Four unresolved/unscored outputs remain in
the original results, excluded only during demo preparation. They are not Negative
or verified events. Playback uses retrospective first-seen time, **not confirmation
time**. Witch's actual confirmed_at34.5s minus approximate GT31.5s remains3s;
playing its32s first-seen position does not improve or certify real-time latency.

Source replay SHA256:
`9b5c1e626d62ba00d9762cb31075681444a0d9d36446694f6fca1bb36cd99d32`.
Source evaluation SHA256:
`67cdad941c073874b1bd9cf98593ca247093ac146fb35447f10e325ad7270c56`.

Private output:
`outputs/module3d-offline/verified-oracle-demo-v1/recorded-oracle-demo.json`.
SHA256:`bdefd0876d7b6b61d7aa63dc309eaaa6399e56435696929fa4e301348372b029`.
Its separate export manifest retains actual IDs, confirmation times, excluded IDs
and provenance/limitations; manifest SHA256:
`31b08eecf318c06d9c62b5d9f5ed99337e02dd501749a1e0246cce9e850a2beb`.
Neither private export is tracked or bundled into the APK. No media/GT/assets/weights
are included. Source SHA/selection labels are provenance metadata, **not digital
authentication** of arbitrary manually altered imports. The controlled exported
fixture has the verified partition; the App cannot certify an arbitrary source.
The old `recorded_oracle_events_v1` nine-event projection is explicitly not accepted
by the demo importer, rather than silently filtered inside the App.

Exporter command (existing fixed environment, no dependency added):

```powershell
.\.venv\Scripts\python.exe -B -m tools.recorded_replay `
  --replay-directory outputs/module3b-repair/replay-v2 `
  --evaluation-directory outputs/module3b-repair/evaluation-v2 `
  --output outputs/module3d-offline/verified-oracle-demo-v1
```

Exclusive output refuses overwrite; do not rerun against that directory. Synthetic
tests check deterministic bytes in separate temporary directories, not regeneration
of private evidence.

## Fresh tests and verification

All below actually ran during this module; no historical test count is substituted.
Full source logs/exit/JUnit receipts are private in `outputs/module3d-offline/`.

| Check | Result |
| --- | --- |
| Full offline_video pytest | 908 passed /3 skipped, exit0,1117.26s |
| Final event/deployment/preannotation/new-export pytest | 294 passed /1 skipped, exit0,10.75s |
| Both smoke-training contract suites, no model execution | 200 passed, exit0,32.03s |
| All owned Python suites combined | **1402 passed /4 skipped**,0 failures/errors |
| Full App Vitest | **102 passed**, exit0 |
| Existing Node review-tool tests | **8 passed**, exit0 |
| TypeScript and Vite build | exit0 |
| Fixed offline environment pip check | No broken requirements found, exit0 |
| Capacitor Android sync | exit0 |
| Final Debug Gradle build | BUILD SUCCESSFUL,1m19s,93 tasks |
| APK signature check | valid Android Debug RSA signer /v2 signature, exit0 |
| Historical protection | 2012 existing material hashes and11 event-engine source files unchanged |
| Privacy and delivery | private outputs ignored/untracked;4 dist assets match APK;166 native PNGs byte-identical to old Mock APK |
| Relative documentation links | 109 local links valid |

The four skips are existing Windows symlink-creation permission limitations:
offline evidence_prepare/multiclass_dataset/training_dataset and event_gt tests.
No unresolved assertion failure or interrupted regression remains.

Exact commands (offline first command runs from `tools/offline_video`):

```powershell
..\..\.venv\Scripts\python.exe -B -m pytest -q --tb=short -rs
.\.venv\Scripts\python.exe -B -m pytest tools/event_engine/tests tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests -q --import-mode=importlib --tb=short -rs
.\.venv\Scripts\python.exe -B -m pytest tools/smoke_training/tests tools/smoke_training_attempt02/tests -q --import-mode=importlib --tb=short -rs
node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs
.\.venv\Scripts\python.exe -B -m pip check
# From app:
npm.cmd test
npm.cmd run android:sync
# From app/android, with retained project-local JAVA_HOME/SDK/GRADLE_USER_HOME:
.\gradlew.bat --offline --no-daemon --console=plain --max-workers=2 assembleDebug
```

Receipts also include exact JUnit destination arguments and start/end times.
New parser/replay/SSR/export tests were run red before implementation, then green.
An additional small-tick boundary regression reproduced floating point rounding;
the clock now accumulates virtual milliseconds instead of repeatedly adding seconds.
Other checks cover invalid IDs/times/cards/paths/hashes/selection/overwrites, pause,
speed changes, repeat cards, source switching and chronological history.
Final read-only auxiliary code review found a deeply nested JSON CLI error path;
one new temporary-fixture regression reproduced `RecursionError` before a minimal
explicit exception handler was added. Final294-pass contract run includes this
32nd exporter test. This is not a new Oracle run or engine/parameter change, and
the auxiliary review is not claimed as ChatGPT independent acceptance.

## Rendered browser and Android emulator

Browser: existing cached Playwright1.62.1/Chromium, local127.0.0.1 preview only;
no install, external requests or game access. Mobile390×844 and desktop1280×900
checks pass17 checkpoints: Mock/reset, real prepared-file import, sequential1..5,
pause/no catch-up, continue/restart, duplicate JSON/raw-nine-event rejection while
retaining state, source switching and no horizontal overflow/runtime errors.
Browser uses a deterministic test clock, not performance evidence.

Android: task-owned `ClashTracker_Module3D_API37` AVD under ignored module outputs,
reused existing API37 google_apis x86_64 image/emulator37.1.11.0/WHPX, serial
`emulator-5582`. Existing unrelated AVDs are untouched. The native document picker
imports the local prepared JSON from Downloads. The App WebView then uses its
**actual Android performance clock**, not an override, for0→5/8/pause2s/continue/
restart/Mock/source-isolation checks. Own-App controls and own DocumentsUI only;
no game or other application automation. These are emulator smoke, not real-phone
performance, background-process resilience or supported-OS matrix certification.

QA-only initial issues were retained in private logs: a browser title helper
expected the old exact title; DocumentsUI initially showed empty Recent instead
of Downloads; a final reinstall launch helper raced force-stop/start. They were
corrected in QA helpers (awaited cold launch and explicit local Downloads), not
by bypassing App validation. Earlier WebView CDP full-page screenshots showed
duplicated compositor tiles; final delivery captures use actual device screencap.
No initial failed QA helper is represented as a passing final check.

## Delivery and environment

APK:`outputs/module3d-offline/clash-tracker-recorded-event-debug.apk`.
SHA256:`52450eda8b0cbd6ff7dd27fb003fd6668e4d038366386ca4ec336f6c14052dc0`.
App ID `com.clashtracker.simulated`, minSDK24/targetSDK36. Debug only; no Release
signing. Existing JDK Temurin21.0.12.1+1; buildSDK Android36rev2/ext17, build-tools
35.0.0, cmdline-tools22.0, platform-tools37.0.1, Gradle8.14.3, AGP8.13.0,
Capacitor8.4.3, Node24.18.1/npm11.16.0. Existing toolchains reused with process-only
environment variables; no install, global environment or model-environment change.
Existing flatDir/SDK-XML build warnings are retained, not hidden as new errors.

Merged APK has only
`com.clashtracker.simulated.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`.
No Internet, SYSTEM_ALERT_WINDOW, capture, Accessibility or input-control permission.
No new package/dependency/native/Gradle/manifest changes. Bundled assets are UI only.
Old visual/event GT locks, Oracle streams/results, attempts and private evidence
are protected by before/after hashes:2012 existing files unchanged plus all11
tracked event-engine files byte-identical. No tracked private artifact or new
nonignored output. Native AndroidX PNG resources are checked byte-for-byte against
the protected previous Mock APK, not misrepresented as private gameplay images.
Old outputs are not overwritten.

## Physical-phone handoff and stopping point

Transfer **both** the APK and prepared JSON to the phone using a user-selected
local method. Install the Debug APK, open App→Recorded mode→import the JSON from
Downloads→choose4×→start. It starts0/8, first card at about8 wall seconds, last at
about29.25 seconds excluding pauses. Check pause/continue/restart, then Mock→2/8
and Reset. Cold restart returns to Mock0/8 and needs JSON reimport.

The old Mock APK's user-reported phone PASS is preserved but does **not** test this
new APK. **New physical-phone acceptance: Not Run by Codex; pending user.**
No detector/cross-match/full-match FP/live-game/8-card inference/cycle/elixir claim.
No main merge or push. Stop at `MODULE_3D_OFFLINE_REPLAY_READY`; next action is the
user's new-APK offline smoke acceptance, not automatic next-module development.
