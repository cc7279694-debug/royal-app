# Module 3C-1 — Detector baseline ready for review

## Goal

Actual retained KataCR output → standard observations → frozen Module3B engine →
independent existing Event GT score. Baseline main:
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.

## Verified completed

Full-file4FPS match01 then match04,1523 actual PTS samples;33337 observations,
2339 candidates,14 emitted engine events. Prediction/replay sealed before GT
evaluation. Actual valid experiment **FAIL**:2/5 positives,1 Royal Hogs duplicate,
three sampled no-new-play windows each0 emissions.12 unscored retain the duplicate
as a failure; four unresolved stay non-negative, full-match FP/min unavailable.

## Changes and inherited decisions

New isolated adapter/replay/post-score diagnostics and37 synthetic tests. Existing
engine/Episode/rules/score/GT/old experiments/App unchanged; no new dependency,
database/schema/native permission. All media, predictions, GT and model weights
remain private/ignored. No training, download, live-game or Android modification.

Model owner is unvalidated; origin/form unknown, no human continuity identity.
Existing STRONG is not human-confirmed deployment or calibrated confidence.
Inherited Oracle-format schema names do not mean Human-GT input in this run.

## Known limitations

Three fixed-window misses have earlier same-class outputs(-1/-0.25/-0.25s), not
zero visual support. No GT or scoring adjustment. Royal Hogs duplicate mechanics
trace to extra same-frame observations becoming new tracks/episode after old
track assignments; physical causes remain uncertain. Candidate12 has zero Witch
predictions, so its formal zero-output PASS does not prove continuity. About3.2FPS
steady GTX1050Ti inference is not real-time/phone qualification or blind validation.

## Verification and handoff

Fresh1439 Python passes/4 existing Windows permission skips; App102/Node8 pass;
offline and retained detector pip checks pass.2165 old material files and144 frozen
non-document sources byte-identical; diff/privacy/manifest checks pass. No Android
build/emulator/phone retest: unchanged App and outside scope.
See [full evidence](../VERIFICATION_MODULE3C1.md).

Local branch `codex/module3c1-detector-event-baseline`; implementation SHA is the
commit containing this checkpoint and the packet manifest's review commit.
No push/main merge. Next action: independent ChatGPT baseline-packet review,
not automatic repair, training, App hookup or next-module work.
