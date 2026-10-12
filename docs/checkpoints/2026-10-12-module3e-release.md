# Module 3E — real-device acceptance and release checkpoint

Date: 2026-10-12. Status: user accepted; release regression/build verification complete.
Accepted development: `8b5029e01ba58093ce69a48177f06506ce418307`.
Preceding main: `7269a02c9ba418796afeabbd0091036a0b72f3d5`.
Feature branch: `codex/module3e-assisted-review-persistence`; retain it.
The documentation commit containing this checkpoint identifies the release;
exact final local/remote SHA belongs in the ignored completion report, not in
self-referential content. No next module, PR or GitHub Release is authorized.

## Formal acceptance and evidence source

`MODULE_3E_REAL_DEVICE_ACCEPTED`, basis `user_real_device_attestation`, reviewer=user.
The user personally reports covering install/start, saved Assisted review results,
exit/reopen recovery, phone reboot retaining5/8, screenshots and confirmation/
exclusion/correction/manual additions restored, and no startup fault or data loss
affecting this acceptance. This is not Codex independent automatic phone testing.

Prior-review preservation after covering install/reopen/reboot is user-attested;
no independent phone database export, phone model/OS or device-side checksum was
supplied. The local delivered APK is hash-verified, not advertised as a measured
device-side file. The new private attestation is
`outputs/module3e-release/user-real-device-attestation.v1.json`, SHA-256
`3f312a1a8307927e7393d73a3c093384529505bc6ac04727813c316b5f54d920`.

## Acceptance matrix

| Criterion | Accepted evidence | Automated evidence boundary |
| --- | --- | --- |
| Covering install and start | User phone PASS | Original emulator install/recovery qualified by OS ANRs |
| Save and reopen review | User phone PASS | Original browser/process-death QA and session tests |
| Phone reboot retains5/8 | User phone PASS | Original actual emulator reboot functional PASS after timeout |
| Evidence images restore | User phone PASS | Original47 image SHA/dimension matches across recovery |
| Confirm/exclude/correct/manual restore | User phone PASS | Shared model/repository/controller tests and original UI QA |
| Deck dedup, pending and raw prediction separation | Retained accepted implementation | Fresh App201 passed; review is not training GT |
| Invalid import/restart/corruption protection | Retained accepted implementation | Fresh App tests; native30 tests remain original evidence |
| Native console and OS health | No phone startup problem reported in acceptance | Original aggregate FAIL remains FAIL, not rewritten |
| Publication and historical protection | Fresh regression/build/hash verification complete | Final scope/guards, ff-only and remote SHA equality recorded in private publication receipts |

## Inherited local storage and safety

One current session only. Android built-in SQLite schema1 stores metadata and
review rows; immutable packet/JPEG bytes stay in App-private noBackupFilesDir.
Web preview uses IndexedDB through the same Repository; `formatVersion=1`.
No cloud/accounts/localStorage business store or new dependency/permission.
Raw detector packet/predictions and editable review rows remain separate.

Serialized writes use session/revision checks. UI publishes committed results only;
packet files are synced/published before the transactional DB pointer. Replacement
and restart require confirmation. Missing/corrupt packet, malformed rows, stale
writes, unsupported versions or I/O failures preserve files/last reliable state
and block unsafe mutation; retry reloads the last commit, never silently clears.
No storage/Migration change is part of release; future versions remain blocked
until explicitly supported. Covering install is not a schema-upgrade test.

## APK traceability and retained failure records

Accepted delivery:
`outputs/module3e/android/clash-tracker-assisted-persistence-debug.apk`.
4,078,411 bytes. SHA-256:
`b95ab9d1362e0eab8e4bb0c7012f8e42991a2d8abc08ab4561ccd1e42b9896b6`.
Retain this original file unchanged. Fresh additive rebuilt artifact:
`outputs/module3e-release/android/clash-tracker-assisted-persistence-debug-rebuilt.apk`,
SHA-256 `2beb0bfab70734e8201ceb3d6325e73a4b38fea2d92574a8796f7704f8286294`,
also4,078,411 bytes. It is **not byte-identical** to the phone-accepted artifact
and is not substituted for that accepted delivery.

Full ZIP-entry audit:412 entries each,410 same-named,409 byte-identical;
only index.html changes its JS/CSS references. Renamed JS bytes match exactly;
CSS only adds the21-byte `.table{display:table}` utility, unused in App source.
Current Tailwind auto-discovery picks up `String table` in the existing native
instrumentation fixture. This establishes current generation cause, not the
historical build-time filesystem. All non-Web/native entries, six DEX files and
resources.arsc match exactly; common ZIP metadata match. Signing-block hashes
change with signed payloads, so this is not a claim that every container difference
is only CSS. Both signatures verify against the same accepted Debug certificate.
Both APKs pass privacy/permissions audits; no new code/config/dependency fix.

Accepted assets: `index-C4jfCsph.js` / `index-Yg1HcDny.css`.
Fresh assets: `index-CZqL3_MK.js` / `index-wNeWulYc.css`.
Entry-audit receipt:
`outputs/module3e-release/protection/all-apk-entry-byte-delta.v1.json`, SHA-256
`6d7bcd0f362dfc9fbf8513be6d21b94d8b7b18a2e42917ac3866461b28ad5f63`.

Original native30 tests passed; Android Gradle AndroidTest failed on offline Maven
cache, and existing SDK tools ran dependency-free platform instrumentation instead.
No new native or physical-phone automated tests are claimed in this docs-only
release. Original boot/socket watchdog failures and process/system UI ANRs remain.

Original additive Android report:
`outputs/module3e/android-app-qa/run-2026-10-11T15-26-55-065Z/android-app-qualified-report.json`,
SHA-256 `2e3a438983411e5f6ccbc9b2087b657e7b84efa89780eb81b085a0bc8ae7c328`.
It remains `functional_pass=true`, `passed=false`, `consoleHealthPassed=false`.
The two existing Capacitor8.4.3 SystemBars startup injection errors and all original
failed receipts/screenshots/logs are retained. No SDK workaround or dependency
upgrade is included. User phone acceptance does not retroactively turn them green.

## Release checks

Fresh logs/receipts are additive and ignored under `outputs/module3e-release/`.
- App: `npm.cmd test -- --run`,201 passed /12 files, exit0.
- `npm.cmd run typecheck`, exit0; `npm.cmd run android:sync`, exit0, including
  TypeScript/Vite build and Capacitor sync.
- Android: `gradlew.bat --offline --no-daemon --console=plain --max-workers=2 :app:assembleDebug`,
  exit0,1m45s,71tasks (21 executed/50 up-to-date). No installation or Release signing.
- Existing offline-video environment from repo cwd: `-B -m pytest`
  `tools/assisted_tracking/tests tools/detector_events/tests tools/event_engine/tests`
  `tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests`
  `tools/deployment_shadow/tests tools/smoke_training/tests tools/smoke_training_attempt02/tests`
  `-q --import-mode=importlib --tb=short -rs`:586 passed/one existing Windows
  symlink-permission skip, exit0. No model training occurred.
- Existing isolated tracker environment: `-B -m pytest tools/visual_evidence/tests`
  `-q --import-mode=importlib --tb=short -rs`:75 passed, exit0.
- Private geometry: `-B -m pytest outputs/offline-assisted-tracking/test_geometry_closure.py`
  `-q --tb=short`:3 passed, exit0, additional to public suite totals.
- Both existing Python environments' `pip check` exit0. Npm local metadata:
  194 lock locations/148 installed packages/13 direct pins/46 optional absent;
  no required/version/license-metadata mismatch. This is not a network vulnerability
  scan, publisher authentication or blanket rights clearance. No dependency change.
- Retained Node24.18.1/npm11.16.0, TypeScript5.9.3/Vite8.3.3/Capacitor8.4.3,
  Temurin21.0.12.1+1, Gradle8.14.3, SDK36 revision2/build-tools35.0.0.
- Full offline-video regression, existing offline-video environment, cwd
  `tools/offline_video`: `-B -m pytest -q --tb=short -rs`,908 passed/three existing
  Windows symlink-permission skips, exit0,1361.71s. Native Tk cases ran, not skipped.
  Log SHA-256 `43ef273dba16c56c70259623a3ed3848a196c57c7a8581d9707cf16909661d2b`.
  The three public suites total1,569 passed/four permission skips; private geometry3
  is additional, not counted twice. No timeout, test or skip workaround was added.
- Not rerun: native30/emulator full UI and physical-phone automation; user phone
  acceptance and preserved original evidence define those bounds. No configured
  ESLint script exists; none installed solely for release.

Fresh SHA preservation of all5,859 accepted historical files passed: zero missing,
hash mismatches, changed-during-read or nonignored files. Receipt:
`outputs/module3e-release/protection/historical-sha-recheck.v1.json`, SHA-256
`c2f6a48f0de5be7ee71bcf8b9379c18ab880fe0e689fc1f72d2da33bdff7fdac`.
An additional160 pre-existing Module3E/checkpoint files are byte-hashed/protected,
including the original APK, aggregate failures, qualified report and completion
report; mutable browser-profile/emulator disks excluded. Final size/mtime guards
complement these hashes, not a second full rehash. A tracked old checkpoint may
be recreated by Git checkout; only its metadata change may be classified after
a fresh one-file SHA matches. No private artifact is allowed that exception.

The new ignored audit helper initially created one bytecode cache in the old
protection folder. Only that verified newly generated cache was removed by exact
canonical path, with no recursive removal; bytecode generation was disabled and
a new corrected v2 capture recorded. Original receipts/reports and all160
pre-existing files stayed unchanged. This failure history is not overwritten.

Final scope/secrets/link/full-range privacy/APK/signature checks and end guards gate
publication. Logs and final receipts are retained in the private completion report.
No old aggregate FAIL is counted as a green fresh test.

## Change and publication boundaries

Closeout changes only README, CURRENT_STATE, DEVELOPMENT_PLAN and this new
checkpoint. Original implementation checkpoint and all historical data/results
remain immutable. No production/test/SQLite/Migration/Schema/Manifest/Gradle,
detector/formal-engine/GT/scoring/dependency change; no training or new inference.
Private recordings, packet/review JSON, screenshots, Human GT, weights, debug
signing files, APKs and reports remain ignored, never published with source.

Verify both old-to-development and development-to-release ranges; do not publish
binary/private assets from intermediate commits. If the remote moved/diverged or
checks fail, stop. Use only safe fast-forward and normal push, never force/rebase,
branch deletion, PR or a GitHub Release. Exact final publication receipts belong
in the private completion report.

## Remaining limitations and next boundary

1. Only one current session; retained old packet files can grow storage.
2. Not backup/export/sync; uninstall, clear-data, device loss or browser-site-data
   removal can destroy the only copy. No power-loss or arbitrary future migration claim.
3. Does not detect external complete logical deletion of an otherwise valid DB.
4. Detector errors/unknowns and the frozen2/5 plus one Royal Hogs duplicate remain;
   confirmed deck results are not automatic event accuracy or cross-match validation.
5. Original emulator console/OS failures are not resolved by phone acceptance.
6. No live game, capture, cross-app HUD, cycle, evolution or elixir implementation.

Stop after release and wait for separate next-stage authorization.
