# Module 3D-Offline — user accepted Android replay checkpoint

Date:2026-10-08. Implementation commit:
`cf9d2995ac6d206ad57c40ce24b72538e3584af4`.
Accepted user conclusion: **`MODULE_3D_REAL_DEVICE_ACCEPTED`**.

## Goal and accepted behavior

Frozen Oracle engine outputs→RecordedEventSource→Android App opponent-deck demo.
The user personally confirms local offline JSON import, automatic0/8→5/8,
start/pause/continue/restart and1×/4×, preserved Mock, and the four unscored outputs
not entering the confirmed deck. User confirmation is the physical-device evidence;
Codex did not independently repeat that test. Phone model/OS, performance/device-side
APK SHA and supported-device matrix are unreported.

## Inherited implementation and data boundaries

Only actual five scored ENGINE event IDs/times are projected by separate offline
preparation. No GT-generated events, new engine run or source/parameter change.
Private real-event JSON remains Git ignored and external to the APK. Four unscored
outputs, original OracleFAIL/PASS results, all visual/Event GT locks and attempts
remain immutable. Unknown/unscored are not Negative. Source metadata is not a
signature authenticating arbitrary edited JSON.

Replay is retrospective first-seen time, not new detector/real-time/cross-match
validation. Witch's actual confirmation delay remains3s. Same-card repeat plays
increase history without slots; Mock and Recorded stay separate. Imports/history
are deliberately in memory, reset on cold restart. No database/schema/migration,
new permission/dependency, capture, accessibility, live game or cross-App overlay.

## Traceable private delivery

- APK:`outputs/module3d-offline/clash-tracker-recorded-event-debug.apk`.
  SHA256:`52450eda8b0cbd6ff7dd27fb003fd6668e4d038366386ca4ec336f6c14052dc0`.
- Demo:`outputs/module3d-offline/verified-oracle-demo-v1/recorded-oracle-demo.json`.
  SHA256:`bdefd0876d7b6b61d7aa63dc309eaaa6399e56435696929fa4e301348372b029`.
- Original checks/screenshots/receipts:`outputs/module3d-offline/`.
- Fresh closeout commands/logs/protection/ref receipts:`outputs/module3d-closeout/`.

Paths are local repository-relative references, not public downloadable artifacts;
no private material is tracked or redistributed. See
[full verification](../VERIFICATION_MODULE3D_OFFLINE.md) for actual fresh counts,
commands/build checks, retained original evidence and publication boundaries.

## Publication and next step

Fresh final regression:1402 Python passed/4 retained Windows permission skips;
102 App tests and8 Node review tests passed. Pip check, TypeScript/Vite/Capacitor,
Debug build/signature/permission, diff/privacy/link checks pass.2107 historical
material files and144 non-document sources remain unchanged. Initial full-run
native-child180s timeout is retained; the same single test and then complete911-test
rerun passed without changing code, timeouts or skips. See verification for exact
commands/counts and the separately traced rebuilt APK; accepted APK is unchanged.

User authorizes documentation-only closeout, fresh checks, **ff-only** merge and
main push. Retain `codex/module3d-offline-recorded-replay`. The commit containing
this accepted checkpoint defines the publication SHA, independently read back from
local main/origin/main/remote after push; private receipts contain exact ref values.
No release-signing, GitHub Release, history rewrite or branch deletion.

Stop after `MODULE_3D_RELEASED`. No automatic next phase, detector mode, Module4,
card-cycle/evolution/elixir or actual-game integration. Await separate authorization.
