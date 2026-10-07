# Local pre-annotation and simulated App — verification

Verified 2026-10-07. Scope: the user's Task A and Task B only. Implementation
baseline `17242b717de91a69b1a6d65511c10c0857337b1b`, branch
`codex/milestone1-data-and-simulated-app`. Main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`. No push or main merge.

## 1. Delivered behavior

Task A is an additive local proposal→explicit correction→separate revision
workflow. It reuses preserved KataCR predictions; it does not run inference or
adopt KataCR as the App detector. Original teacher bytes, score/class/owner
hypotheses and boxes stay separate from human fields. Source frames bind exact
PTS/time_base and hashes, not annotated benchmark screenshots.

The browser supports accept, reject, relabel, bbox correction and manual missing
boxes; owner/form/origin/visibility/uncertainty and appearance identity are
explicit human metadata. Class-specific exhaustive review is a separate
declaration. Unreviewed, rejected, uncertain and Unknown regions are not
automatic negatives. Even class-specific negative evidence is conservatively
blocked if any proposal region remains unresolved. Ordinary background training
exports remain disabled; every revision has `training_qualified=false` and no
card events or independent-deployment claim. Continuity metadata does not
prove a new card play. Source02 is explicitly truncated/training-excluded;
inventory order stays01,02,03,04. A target of10–20 classes is not a readiness gate.

Task B is a Vite/React/TypeScript/Tailwind/Capacitor mock-only App. A closed
`OpponentCardPlayed` interface carries eventId/cardId/timestamp/confidence/source.
Only `source=mock` is accepted now; detector/live/unsupported sources are rejected.
Duplicate events are idempotent, conflicting IDs are visible errors, and state
is copied/frozen rather than mutating accepted input. Discovery retains eight
slots and explicit overflow. Fixed Witch12s/Balloon28s events produce
0/8→1/8→2/8; reset permits replay. This is not visual recognition or card-cycle,
evolution or elixir inference.

The HUD is inside the App only. No game connection, MediaProjection,
SYSTEM_ALERT_WINDOW, capture service, Accessibility, synthetic input or detector
adapter exists. Future native plugins remain an option, not current behavior.
Live analysis/HUD remains subject to the unchanged Supercell permission gate;
no zero-ban-risk claim is made.

## 2. Changed files / storage

Added14 files under `tools/preannotation/`: contract, bundle I/O, local server/CLI,
HTML/CSS/JS reviewer, README, three Python test files and two Node test files.
Added41 files under `app/`: typed domain/mock/UI and tests, exact npm lock,
Capacitor configuration and Android source/wrapper. Added the bounded spec,
implementation plan and this verification document. Updated `.gitignore`,
`PROJECT.md`, `README.md`, `CURRENT_STATE.md`, `DECISIONS.md` and
`DEVELOPMENT_PLAN.md`. No pre-existing source, test, dependency or artifact deleted
or modified outside this explicit documentation/ignore scope.

No SQLite, migration or persistent App repository was added: the simulated App
contains only in-memory demo state. Human review edits are in page memory until
the user downloads a return. Import creates an exclusive new directory and
archives the validated byte snapshot; it never overwrites an old revision.
Private source PNGs, teacher copies, downloads, receipts, synthetic fixtures,
screenshots and preview/build outputs remain ignored/local. The only intentional
tracked binary is the43,764-byte official Gradle wrapper JAR, not game media or
weights. Its SHA and licenses are recorded in `app/android/NOTICE.md`.

## 3. Actual demonstrations

The real first-match bundle uses fixed stride20 of the existing first-match
benchmark:12 original source PNGs at12,17,...67 seconds,272 pending proposals.
No selection by class or prediction quality, no rerun of the detector, and no
false human confirmation. This is the first sparse workflow demonstration,
not an exhaustive review of all four recordings or a qualified multiclass dataset.

Current local presentation:
`outputs/milestone1/match01-review-presentation-v3/`.
Bundle SHA:
`a3801c0191aba1baf621fefaccfb8170f5d6f08bc41fcaf51c57ae6d67549f32`.
The new presentation copies identical data/PNG bytes; it does not re-decode or
replace the earlier bundles. Current read-only loopback preview: port8769.

The synthetic browser performed all five correction actions, real pointer-drag
for a missing bbox, class coverage retaining unresolved=true, and a download.
Post-fix CLI validate/import both exit0 into
`outputs/milestone1/browser-synthetic-revision-v2/`: four simulated positives,
four appearance groups, no negatives, no card events, independent deployments0,
`human_confirmed=false`, `training_qualified=false`. Synthetic downloads cannot
be imported as real reviewed GT. Human-return receipt SHA equals the exact
downloaded bytes; reviewed annotation readback also passes.

Actual browser delayed-image and deliberately failed404 checks show empty/
hidden canvas and disabled/guarded annotations until the current image loads.
Failure is visible; switching to a successful source recovers. The intentional
synthetic404 is one expected browser error, not an unhandled implementation
failure. The unmodified real review page has0 console errors/warnings.

App browser QA on installed Chrome: initial empty state, two successive mock
events, disabled completed playback, reset and replay. Final390×844 viewport
has scrollWidth390 and scrollHeight844; no horizontal overflow or clipped footer.
Desktop1440×900 also inspected; console0 errors/warnings. Actual final screenshots
were also checked against a320px-wide viewport: no horizontal overflow and both
control buttons at least48px high; the preview was restored to390×844. Screenshots
were saved outside Git in the task's local visualization folder:
`app-final-mobile.png`, `app-final-desktop.png` and
`real-proposal-review-final.png`. Browser connector initialization timed out;
installed-Chrome Playwright CLI was used as the bounded local QA fallback.

## 4. Checks actually run

- `.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short`
  → **908 passed / 3 skipped**, exit0,1311.23s. Existing Windows permission
  skips; no failures. Historical implementation/tests remain unchanged. This
  maintained suite is separate from historical helper200-test evidence, which
  was not rerun in this task.
- `.\.venv\Scripts\python.exe -m pytest tools/preannotation/tests -q --tb=short`
  → **51 passed**, exit0,4.14s after repairs.
- `node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs`
  → **8 passed / 0 failed**, exit0,216.01ms after repairs.
- `npm.cmd test` in `app/` → **43 passed**, exit0. Strict
  `npm.cmd run typecheck` and `npm.cmd run build` pass; production21 modules,
  CSS9.49kB / JS225.36kB. These are bundle sizes, not Android/inference speed.
- `npm.cmd run android:sync` → exit0, fresh TypeScript/build and Capacitor sync.
  Six Android/config XML files parsed; syntax validation is not resource linking.
- `npm.cmd audit --json` → exit0,0 reported vulnerabilities; exact installed
  versions match the npm lock. Audit is not a security guarantee.
- Existing offline, YOLOX and benchmark environment `pip check` pass; package
  inventories of all three are identical to before the task.
- Working/staged diff whitespace, relative-document links and scoped secret/
  accidental-media checks pass. New outputs/build assets/node_modules are ignored.

Test-driven implementation and scoped code reviews were used. Task A review
found two Important defects (return reread race; stale source image). Regression
tests first failed, repairs now pass, and scoped re-review approved both. Task B
review approved without findings. Final combined internal review approved after
correcting the App README npm-script invocation and adding the verified Gradle
wrapper checksum to its provenance notice; no functional changes were needed.
Test-first details and raw local outputs are
retained in ignored `outputs/milestone1/task-a-report.md`, `task-b-report.md`
and `verification-evidence.md`; no ChatGPT independent acceptance is invented.

## 5. Dependencies and Android status

Existing Python dependencies unchanged. App dependencies were version/source/
license checked, pinned and isolated to `app/`: React19.3.0 MIT,
Capacitor8.4.3 MIT, Tailwind4.3.3 MIT, TypeScript5.9.3 Apache-2.0,
Vite8.3.3 MIT, Vitest5.0.3 MIT. Official registry integrity values are in the npm
lock. The matched Capacitor8.4.3 set avoids the initial8.5.2 CLI transitive audit
finding; this was a scoped first-install selection, not an existing-stack upgrade.
Gradle8.14.3 wrapper and distribution hashes are pinned to official values.
No model framework, weights or data download was added.

**APK/device verification: Not Run.** Java/Javac/JDK21 are unavailable in PATH
and checked common locations. The existing Android SDK directory has emulator
templates but lacks platforms36/build-tools/platform-tools/cmdline-tools.
`assembleDebug` was not invoked and no APK exists. No automatic global SDK/JDK
installation, PATH mutation or emulator/device connection was performed.
**ESLint: Not Run**; the minimal App has no ESLint package/configuration.
Strict TypeScript,43 domain tests, production build and browser QA are verified.

## 6. Protection / limits / stop

Before-and-after protection confirms **32,217 historical files unchanged**,
including old locks, Attempt01/02, original recordings and the benchmark;
**160 original YOLOX source files unchanged**, unchanged benchmark file map and
unchanged three environment inventories. Tracked private gameplay/media count0;
old/new local evidence stays Git ignored. No old GT/lock was edited, no training,
inference rerun or model download occurred. Source02 exclusion does not delete
its file/evidence or convert it to Negative.

Hashes/attestations do not prove source authenticity or truthful human review.
KataCR code/weight/game-asset license and provenance caveats remain unresolved;
no private-use authority is described as legal clearance or redistribution rights.
The preannotation workflow intentionally has no training exporter, full-timeline
negative certification or FP/min claim. Teacher labels include noise/UI, not
verified classes/cards. A future detector still needs a confirmed event boundary
before it can drive `OpponentCardPlayed`.

UI reference fidelity: warm offwhite/green palette, compact header+mock badge,
small HUD,4×2 letter slots and event/history/control layout all matched the
generated concept and were checked against actual screenshots. Intentional
changes: corrected Chinese labels, honest empty/step/completed states and darker
secondary text for measured contrast. Generated concept is not an App screenshot
or shipped game art. Responsive footer spacing was checked in the final viewport.

Execution rulings: the user's direct design→implementation authority avoided a
new approval pause (possible cost: later visual preference adjustment); same
checkout/disjoint agents preserved fixed private environments (possible cost:
shared-path conflict, prevented by parent-owned Git/docs); all workers inherited
the current model as requested (possible cost: computation only).

Local public checkpoint only; preserve the feature branch, no push/main merge.
This task stops at usable tools/mock demo and truthful Android environment status.
Next is user acceptance and real human correction of the first pending bundle,
not automatic training, Module3, live game features or global toolchain setup.
