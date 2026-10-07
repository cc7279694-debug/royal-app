# Attempt02 — confirmed expanded TRAIN and fixed Nano640 experiment

Date: 2026-10-07. Current boundary: **one fixed training and DEV_TUNE run
completed; independent visual acceptance pending**. User-relayed human verdict:
`ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED`.
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
binding. Fresh maintained regression, working directory `tools/offline_video`:
`../../.venv/Scripts/python.exe -m pytest -q --tb=short`, with private JUnit:
**908 passed / 3 existing Windows symlink-permission skips**, exit0,2079.70s.
Both suites have zero failures/errors. The temporary awake guard released
normally; no interrupted-run or historical count is substituted.

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

## Actual one-run result

Clean local public baseline at model execution:
`361a2e4c074195ebc3c42e1b5a1e951884cd82b8`. The exact run-freeze records this
commit, environment and all code/data/config/weight hashes before any update.
No implementation changes were made after the actual run started. Maintained
legacy regression was allowed to continue concurrently because it uses neither
the independent model environment nor GPU; all 200 new/historical smoke-helper
tests and the before-run data/protection checks had already passed.

Actual qualified-model command invokes `tools/smoke_training_attempt02/train_attempt02.py`
with the repository root, new expanded lock and new ignored run directory,
using the unchanged Phase B model interpreter. An ephemeral per-process awake
guard (not a Windows power-settings change) releases normally; command exit0.

- Exactly **300 CUDA FP32 optimizer steps**; 174 explicit negative steps,
  126 positive steps/126 GPU assignments, **zero CPU fallback**. Each step logs
  finite losses, nonzero CUDA gradients and its TRAIN frame identity.
- All 14 CPU-cached inputs were used the frozen number of times, never match04.
  320 parameter tensors changed; absolute summed parameter change19720.159182.
- Actual training184.20s; first/last14-step mean losses11.571084/1.910648.
  Numerical learning is verified, not generalized detection accuracy.
- Torch peak training allocated322.22MiB/reserved670MiB; telemetry285 samples,
  GPU utilization peak61%. Driver-wide memory peak2373MiB includes the desktop
  and other processes, not only this model's tensors.
- Checkpoint save, byte hash and strict model/optimizer reload equality passed.
  Final checkpoint SHA:
  `8423fbe8be74302b65b163ec6701d69bde865df950b20eb469597e6de7b67811`.
- Exactly **one DEV_TUNE run / two forwards**, only after training/checkpoint
  reload. All raw8400x7 outputs per frame, fixed post-NMS detections, full GT
  matches and two original-coordinate visualizations retained.

| GT | Attempt01 best IoU | Attempt02 best IoU | Attempt02 confidence | Fixed-IoU match |
| --- | --- | --- | --- | --- |
| 68s Witch | 0.644608 | 0.842899 | 0.001086 | yes |
| 68s Skeleton object08 | 0 | 0 | 0.130002 at an unrelated location | no |
| 68s Skeleton object09 | 0 | 0.288067 | 0.001503 | no |
| 68s Skeleton object10 | 0 | 0.048542 | 0.005230 | no |
| 72s Witch | 0.008379 | 0.656132 | 0.004371 | yes |

Fixed diagnostic GT matches: **Attempt01 1/5 → Attempt02 2/5**, Witch2/2,
Skeleton0/3. The Witch scores remain extremely low: this is weak localization
response, **not a usable two-class detector or accuracy acceptance**. Complete
68s:16 retained detections,15 sampled-frame FP (Attempt01 had77). Partial72s:
5 retained detections,4 unmatched **unjudged**, no confirmed-FP claim (Attempt01
had30 unjudged plus1 padding candidate). No FP/min, mAP, owner-discrimination
or independent generalization claim. Data/ROI/input/budget changed together,
so the comparison does not isolate the reason for any difference.

TRAIN GT overlays and DEV_TUNE visualizations were inspected as diagnostics;
this does not replace the independent human-review provenance. Loss history,
GPU telemetry, both predictions/raw outputs, evaluation JSON/Markdown,
Attempt01-vs-Attempt02 comparison and Completion Report stay private/ignored.
The local small results ZIP contains the two visualizations and numerical
summary/comparison, not original MP4, dataset, GT files or model checkpoint.
No automatic upload. The official cached Nano weight/provenance was reused,
no installation/download/retuning/retry/Attempt03 occurred. No production Model
Lock, Blind Test, Module3, Android/live feature, push or main integration.

## Final protection and handoff

Fresh after-run protection command exits0: **32,217 protected historical file
hashes unchanged**, **32,143 private paths remain ignored**, zero tracked private
media. The original recordings, 2A2 lock, 2B-1 failure, v1 GT/Dataset Lock,
Attempt01 data/config/checkpoint/predictions and legacy code are unchanged.
Expanded GT v2, its deterministic export and fixed training config also match
their before-run hashes and validate again. No frame extraction or GT editing.

Both environment `pip check` commands again exit0, `No broken requirements
found.` Package inventories match the prior snapshots (only the approved
editable local checkout commit reference is normalized). All160 pinned YOLOX
source files and the original official cached weight/provenance remain unchanged.
Process-bound system-awake requests were released normally; power settings
and installed environments were not modified.

Read-only post-run artifact audit confirms every loss row, actual frozen sample
order/count, source-code hash, checkpoint hash, result receipt and single
DEV_TUNE run. Public diff/link/privacy/secret checks pass. The actual full
regression JUnit contains911 tests, zero errors/failures, exactly three existing
Windows symlink-creation privilege skips;908passed. Helper JUnit confirms200
tests, zero failures/errors/skips. These are two actual suites, not one combined
run and not historical results reused as evidence.

Results ZIP: `Module_2B2B_Attempt02_DEV_TUNE_Results.zip`,931274bytes,8 unique
members; CRC, archived bytes and all manifest member hashes verified. SHA-256:
`818bd2ecc928916ee35673a80e34beaf671c0072757669d85b151736e0271c20`.
Includes two visualizations, fixed evaluation JSON/Markdown, Attempt01 vs02
comparison, GPU summary and scoped execution Completion Report; no source
video, GT/dataset files or checkpoint. No automatic upload.

Public run code is frozen at361a2e4 above; only the four current README/state/
roadmap/verification documents changed after execution to record real results.
Local feature-branch commits only; main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`. No push, merge or Model Lock.
Independent ChatGPT visual result acceptance remains pending. Stop here;
no Attempt03, Blind Test, Module3, Android or live-game development.
