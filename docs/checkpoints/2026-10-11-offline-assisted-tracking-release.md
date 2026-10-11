# Offline Assisted Card Tracking MVP — acceptance and release checkpoint

Date: 2026-10-11. Status: accepted delivery; release-only verification complete.
Accepted development commit:
`2fbb23db5536628e315a8e3d272692c89af5c3ff`.
Preceding main: `602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.
Feature branch: `codex/offline-assisted-tracking-mvp`; retain it after publication.
The release documentation commit containing this checkpoint identifies the release;
its exact local/remote SHA and publication receipts belong in the private completion
report, avoiding a self-referential commit hash in its own content.

## Formal acceptance and its scope

`OFFLINE_ASSISTED_TRACKING_REAL_DEVICE_ACCEPTED`.
Basis: `user_real_device_attestation`; reviewer=user. The user reports successful
installation/launch, real candidate JSON import, candidate cards/evidence images,
confirm/exclude/correct/manual addition, deck 0/8→5/8, and duplicate-card handling.
This is acceptance of the offline assisted App workflow, not Codex independent
native automation, pixel-level Human GT, detector accuracy or confirmed play counts.

The original API37 system interruption and API36 WebView timeout remain recorded
as failures/unverified outcomes. The native picker displayed the real JSON, but
the original automatic test did not establish file delivery/Assisted confirmation.
Those records were not rewritten to PASS. No new emulator/physical-phone automated
test is claimed during this release task; no device-side APK checksum was supplied.
The separate local attestation record is
`outputs/offline-assisted-tracking-release/user-real-device-attestation.v1.json`,
SHA-256 `d2d271e65554479d2ba9b3c22739aaba0d5b2be3299d4f7efbcbeb4401dbcc78`.

## Accepted capability and retained scientific results

- Recorded/Mock remain available. Assisted imports source-bound pending hypotheses;
  confirmation/exclusion/correction/manual entries are separate from raw predictions.
  Only confirmed opponent rows affect the deduplicated eight-slot deck; repeated
  card records do not occupy additional slots. Manual choice is not model support.
- Real first-match detector export: 18 candidates, 47 actual PTS-bound evidence
  JPEGs. Assistant visual review supports 14 hypotheses, rejects one false target
  mapping, and leaves three unresolved. These are not 14 independent card plays.
- The frozen detector-to-engine scientific score remains 2/5, with one Royal Hogs
  duplicate. Four unresolved GT windows remain non-negative. Whole-match misses,
  FP/min and independent cross-match performance are not established.
- Separate 3C-3/3C-4 Shadow/ByteTrack experiment history is retained in the branch
  ancestry, including failures; neither strategy is promoted into the formal
  Module 3B engine or default App workflow. Its formal engine tree remains
  `028d60e093c5eb7b40439c198b0215dd0dc29761`, identical to preceding main.
- Geometry closure remains assistant-provisional, not human pixel verification.
  It creates no new qualified training labels, Negative or card-play GT.

## Debug APK traceability

Original local delivery file:
`outputs/offline-assisted-tracking/android/clash-tracker-assisted-debug.apk`.
Size: 4,070,269 bytes. SHA-256:
`7d278add5ea903d652249604a39d22abf5ae653682cc5db3779cbaa1a4a146e2`.

Fresh build is additive at
`outputs/offline-assisted-tracking-release/android/clash-tracker-assisted-debug-fresh.apk`;
its byte hash equals the original delivery hash. The original APK/logs/failure
receipts are retained, not overwritten. The App Web assets match the fresh dist.

Commands: `npm.cmd run android:sync`, then
`gradlew.bat --offline --no-daemon --console=plain --max-workers=2 assembleDebug`.
Fresh sync includes TypeScript and Vite build. Both Debug builds exit 0: the first
BUILD SUCCESSFUL in 2m 58s and the final additive verified run in 36s, each with
93 tasks (24 executed, 69 up-to-date). No install/upgrade or Release signing.
Retained environment: Node 24.18.1, npm 11.16.0, TypeScript 5.9.3, Vite 8.3.3,
Capacitor 8.4.3, Temurin JDK 21.0.12.1+1, Gradle 8.14.3,
Android platform 36 rev2 and build-tools 35.0.0.

Source Manifest has zero uses-permission entries. Merged APK uses only its own
AndroidX signature permission
`com.clashtracker.simulated.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`.
No Internet, screen capture, cross-app overlay, Accessibility or game-input control.
No private candidate JSON, gameplay images/video, GT or model weights are bundled.

## Fresh release checks

Logs and command/exit/SHA receipts are additive and ignored under
`outputs/offline-assisted-tracking-release/`; original reports remain unchanged.

- App: `npm.cmd test -- --reporter=dot`: 145 passed, nine files, exit 0.
  This includes 43 Assisted tests and the existing Mock/Recorded regression.
- Other Python tools: 586 passed / one existing Windows symlink permission skip,
  exit 0. Covers Assisted exporter, detector adapter, formal engine, event GT,
  preannotation, recorded replay and separate dormant experimental utilities.
  Invocation: offline-video Python, repo cwd, `-B -m pytest`
  `tools/assisted_tracking/tests tools/detector_events/tests tools/event_engine/tests`
  `tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests`
  `tools/deployment_shadow/tests tools/smoke_training/tests tools/smoke_training_attempt02/tests`
  `-q --import-mode=importlib --tb=short -rs`.
- Isolated existing ByteTrack environment: `-B -m pytest tools/visual_evidence/tests`
  `-q --import-mode=importlib --tb=short -rs`: 75 passed, exit 0.
- Private geometry regression: `-B -m pytest`
  `outputs/offline-assisted-tracking/test_geometry_closure.py -q --tb=short`:
  three passed, exit 0.
- Offline-video full regression, cwd `tools/offline_video`, existing offline-video
  Python `-B -m pytest -q --tb=short -rs`: 908 passed / three existing Windows
  symlink privilege skips, exit 0, 1239.17s. The native Tk cases ran, not skipped.
  Log SHA-256 `7b474d3b4032484b3f8bb97e79be73e43eb5b213f7e5335d00d5d00bc2150545`.
  Across the three public Python suites: 1,569 passed / four permission skips;
  the three private geometry tests are additional, not included in that total.
- Both existing Python environments: `python -m pip check`, exit 0, no broken
  requirements. App `npm.cmd ls --depth=0`, exit 0; 13 direct pins match.
- Local npm lock/installed-package license metadata audit: 194 lock locations,
  148 installed packages, 46 absent optional platform packages; zero missing
  mandatory packages/version mismatches/missing license metadata. Direct packages
  are 12 MIT and TypeScript Apache-2.0; transitive/bundled notices include other
  licenses and must not be described as all MIT. Python dependency license files
  and installed versions are recorded. No fresh network vulnerability scan,
  package installation, weight download or blanket legal/security clearance.
- Local pinned ByteTrack sources and LICENSE/NOTICE hashes match; no source,
  game asset or model rights are newly cleared by this check. Private research
  boundaries and unverified rights remain unchanged.
- No configured ESLint script exists in the retained App; no linter/dependency was
  added for release. TypeScript/build and existing tests supply the actual checks.

An initial root-wide `pytest tools --import-mode=importlib` invocation exited 2
with 18 collection import errors: legacy offline-video fixtures require their
normal prepend imports and working directory. It did not run failing assertions.
The failed log is retained as `python-full-regression.log/json`; suites were
rerun in their existing working directories/environments, without changing tests,
code, timeouts or skips. Fresh successful suite receipts are separate.

The first build helper completed its checks but stalled serializing extended
PowerShell string properties into its final receipt. Its exact task-owned process
was stopped; successful logs/APK were retained. Only the ignored helper was fixed
and rerun with existing PowerShell 7.6.5 and separate `verified-` logs. Its final
`android/build-receipt.json` is PASS; 28 original Android artifacts and 54 tracked
App files remain unchanged. No original native failure report was overwritten.

The ignored audit helpers also retain initial classification failures: exact
public-source mirrors were not private media; older commits predate the later
materials ignore rule; the two extra Cordova stub assets are exactly empty.
Corrected v2 audits document those exact classifications, not suppressed findings.

## Privacy and historical protection

Fresh byte hashes verify all 5,726 saved files unchanged (5,692 historical plus
34 precise-review files), and capture 133 further stable MVP files: 5,859 total.
Zero missing/hash mismatches/nonignored files; the final stat guard additionally
checks preserved size/mtime. Mutable unused emulator disk images are not rehashed.
Original source recordings, snapshots, GT locks, Oracle/FAIL results, exported
packet members, screenshots, APK and five native failure records remain protected.

Key private artifact SHA-256 values:

- Candidate JSON: `99c3337e6f4e5d35fcaffdf4ed1360629aeda1af3c44a944beef2439c0e41af0`.
- Assistant hypothesis review: `ed09e32704176f5c521229f461a744bbbadbcefd0bcfc29bb96cd474faf8b5e2`.
- Provisional geometry closure: `02367a06abcc4b6ffc1e2dfd58a51d5b48d1ef189627539ad170b478165ebf56`.
- Saved source recording: `3125314ea1b431d360baf8e8e4a79e66a830a50cf67cd8face2fb174228f6549`.
- Fresh preservation receipt: `b11e64edc4293c1b51f04108ae00dd84ffd93dcab7bca052a6f3b455f59ab4e0`.

All to-be-published commit trees, not just the latest diff, are checked for
private paths/hash copies, new media/binaries/weights, secret patterns, ignore
rules and unwanted default Shadow integration. The initial development range is
13 commits / 64 final changed paths; the final range also includes this docs-only
acceptance commit. Public code/docs/tests only; outputs/local_data/materials,
personal images/account information/JSON/labels/weights/Debug signing artifacts
remain ignored and untracked. Final full-history/guard receipts and Git status
are recorded before publication.

## File/data changes and release boundary

This closeout changes only README, CURRENT_STATE, DEVELOPMENT_PLAN and this new
checkpoint. The historical implementation checkpoint remains an honest account
of its earlier pending acceptance. No production/test/Schema/SQLite/Migration,
dependencies, native permissions, formal engine parameters, historical GT or
scientific results changed. Local build/verification outputs are ignored.

Release uses a checked documentation commit, safe fast-forward main, normal
push and post-fetch local/remote verification. No force push, branch deletion,
PR, GitHub Release, model training or next-stage implementation.

Known remaining limitations:

1. Review decisions are session-only; reset, mode switch/reimport and reopen clear
   them. No persistence/recovery or new data storage is implemented.
2. Detector retains false positives, misses and unknown candidates. User-confirmed
   deck results do not establish automatic tracking accuracy.
3. No independent cross-match performance validation; no whole-match FP/min claim.
4. Real-game analysis and cross-app HUD remain Gated; no capture or game connection.
5. Exporter/App limits are not identical for arbitrary packets; only their valid
   intersection and the actual delivery packet are verified.

Stop after this release. Suggested separately authorized next work is session
review persistence/recovery; no new feature, training or real-game work starts here.
