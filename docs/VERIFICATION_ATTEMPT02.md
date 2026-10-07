# Attempt02 — confirmed expanded TRAIN and fixed Nano640 experiment

Date: 2026-10-07. Current boundary: **confirmed data validated; real run not yet
started**. User-relayed human verdict: `ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED`.
Follow the unchanged [fixed protocol](PHASE_C_ATTEMPT02_PROTOCOL.md).

## Immutable confirmed data

The actual user-relayed return binds the reviewed ZIP file SHA
`7e7a1d9d50d9ec4de1d7b5dbe6a5049ca041cd64737265f966b7e8446ba51972`.
ZIP/local manifest bytes, unique member inventory and all member hashes match.
Eleven new objects are confirmed, four rejected with the exact review reasons;
six original confirmed objects inherit all old v1 fields. No bbox was changed.

New exclusive `expanded_gt_snapshot.v2.json` file SHA-256:
`f25c54e6dfc578a6d9edd69c2adfa712fb79fa5c924b25a7ad6999951707c1c2`.
The dedicated expanded snapshot validates and deterministic export readback
exits 0. Old v1 GT and Training Dataset Lock are unchanged.

- Snapshot TRAIN: 16 frames, 17 accepted objects, four rejected proposals.
- Standard TRAIN: **14 frames / 15 boxes**, 8 exhaustive negative frames and
  6 exhaustive positive frames, Witch 6 / Skeleton 9.
- Standard times: 5,10,15,75,90,95,100,105,158,160,161,163,164,166 seconds.
- Partial 162s/165s frames retain two confirmed Witch boxes and material Unknown,
  but are not exported into the standard dataset/loss. Rejected proposals are
  not Negative. No unresolved region is silently supervised as background.
- Classes: `unit.skeleton=0`, `unit.witch=1`. Every ROI box maps back exactly to
  the original accepted integer bbox, no class swap, clipping or bbox editing.
- ROI `[0,120,432,744]` yields 432x624 crops. All 16 exported PNGs (14 TRAIN,
  2 DEV_TUNE) are pixel-identical to their deterministic original-image crops.
  TRAIN GT overlays/contact sheets were generated and visually inspected.
- TRAIN is only `natural_match_01`; DEV_TUNE is only `natural_match_04` (68s,
  72s; five accepted boxes). Historical DEV_VAL lock fields are not modified.
  DEV_TUNE images never enter training; 72s remains partial.
- Original Witch episode identity stays one independent deployment. Skeleton
  continuity at 160s/161s has unknown source; the 166s wave is spawned from the
  same Witch episode. Neither Skeleton group represents a Skeleton card play.

Eight existing source report/index sets were reloaded by the unchanged strict
Module2A1 loader: 195 original requests, no new frame extraction. Digests are
consistency bindings, not authentication of a human or legal rights clearance.
Training qualification is only the authorized private local research PoC scope:
user-recorded gameplay, local authorization true, external upload false,
redistribution false, rights clearance unverified.

## Fresh verification before the real run

Helper command from repository root:
`./.venv/Scripts/python.exe -m pytest -q tools/smoke_training/tests tools/smoke_training_attempt02/tests --tb=short`
with a private JUnit receipt: **200 passed**, exit 0, 90.78s. The suite includes
26 unchanged historical smoke tests and 174 Attempt02 contract/preparation/
snapshot/runtime tests. Focused tests demonstrated RED before implementation
and GREEN afterward, including exact export/lock binding and reviewed ZIP
binding. The maintained offline_video full regression is still running; do not
substitute historical pass counts for the current result.

Fresh before-run protection: **32,217 historical file hashes unchanged**,
**32,143 private paths still ignored**, original recordings/old locks/Attempt01
results and 160 official YOLOX source files unchanged. Both environment pip
checks exit 0 (`No broken requirements found.`); installed inventories match the
Attempt01 baseline, allowing only an approved editable checkout Git reference.
No package installation, new weight download or model execution in preparation.
Public link/privacy/secret checks pass; no tracked private media.

Two read-only local reviews found no remaining Important/Critical data/runtime
issues. They are implementation checks, not a substitute for ChatGPT's later
independent experiment/result acceptance. Actual expanded data/export metadata
was also independently compared to the snapshot without editing files.

## Run contract

The already-fixed settings are Nano640, batch1, FP32, seed20261006, SGD0.001,
exactly300 optimizer steps, no augmentations/scheduler. Chronological 14-frame
cycling gives 174 negative steps and 126 positive steps. Zero-GT images use
the native `(1,0,5)` target shape, not fabricated labels. Only one current frame
is transferred to CUDA; the image cache remains CPU-resident.
Reuse the same official COCO Nano weight/provenance. Freeze committed public
code identity, exact expanded data/config/weight hashes and sample counts before
the first update. Retain all start/failure receipts; no implicit retry/tuning.
After training, checkpoint round-trip and only one two-frame DEV_TUNE run, using
the pre-fixed confidence0.001 / class-aware NMS0.65 / matchIoU0.5 diagnostic
rules. Padding/outside-ROI boxes are retained but excluded from valid matches;
72s unmatched proposals are unjudged, never confirmed FP. No mAP/FP-per-minute,
owner-discrimination, production Model Lock, Blind Test or Module3 claim.

Actual receipts/raw logs/JUnit and all media remain in the ignored Attempt02
run directory. No push or main integration. Training/checkpoint/evaluation
results will be recorded only after the single actual run completes.
