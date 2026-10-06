# Phase C — First real two-class learned-detector smoke experiment

Date: 2026-10-06. Execution completed; pending ChatGPT independent acceptance.
This is a valid fixed-budget experiment with insufficient detection performance,
not a claim of accurate card recognition, generalization or a production model.

## Local baselines and unchanged data

- Historical Phase A/B/GT/data checkpoint:
  `b75819db3bc2c542eede1b28ac854049f7ba3acc`.
- Tested runner initial commit: `9fd65d9e0555580ed46c2b40bfdeb13931abfc3f`.
- Exact clean code commit frozen before the real run:
  `bfc834dfc197d21528cf410591a41f53ab844fc3`.
- Branch: `codex/module-2b2b-multiclass-infrastructure`.
- `main` unchanged: `8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.
- GT file SHA: `f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1`.
- Dataset Lock file SHA: `582dc30d3e418aebf09adfed931742627c29a1f3da1a19ae24c165621cc58e39`.

Original readiness/validate-lock exit 0; run preflight also checks pinned lock,
parent snapshot, source PNG/index/report bindings and every accepted bbox.
Deterministic export: TRAIN match 01, two frames, Witch 2 / Skeleton 4;
DEV_VAL match 04, two frames, Witch 2 / Skeleton 3. Eleven accepted objects only;
rejected object 12 is never a label or Negative. Skeleton=0, Witch=1.
No original GT, lock, appearance identity, owner/form/origin or split was edited.
Form unknown is allowed; spawned Skeleton is not a Skeleton-card deployment.
The two TRAIN frames are complete for selected classes. Partial 72s DEV_VAL is
positive-only and never enters training loss or full-frame precision/FP metrics.

## Fixed protocol and official weight

See [the pre-run protocol](PHASE_C_SMOKE_PROTOCOL.md). Nano only, input 416,
batch 1, FP32, seed 20261006, exactly 100 SGD steps, lr 0.001, momentum 0.9,
Nesterov true, non-BN weight decay 0.0005, no scheduler/augmentation/early stop.
The two TRAIN images alternate and are each used 50 times. No DEV_VAL data
enters optimization. Full-image BGR/114 left-top letterbox retains every box.
The isolated environment lacked full Trainer UI/logging extras; the minimal
runner uses unmodified upstream model/loss/assignment/SGD components without
installing additional packages. Six 80-to-2 classification predictor parameters
are initialized freshly; every other pretrained key and shape must match.

Only [official YOLOX release 0.1.1rc0](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0)
asset `yolox_nano.pth` was downloaded after its provenance record was written.
Size 7,694,953 bytes; local SHA:
`cd28f55fbbc1829f99d9ac9b38a16d259a22889739c8728ea877610201feff7b`.
The official API advertises no asset digest; this local hash pins bytes, not an
independently supplied authenticity checksum. Source revision
`6ddff4824372906469a7fae2dc3206c7aa4bbaee`, code Apache-2.0, pretrained dataset
COCO. Code license does not clear COCO photographs, weight or game-asset rights.
Private local research only, no automatic upload/redistribution, rights unverified.
The separate current Phase C receipt does not edit historical lock permissions.

## Actual training evidence

Torch 2.7.1+cu118, TorchVision 0.22.1+cu118, YOLOX 0.3.0, CUDA 11.8;
GTX 1050 Ti 4GB, driver 582.28. Deterministic algorithms enabled, TF32 disabled.

- Exactly 100 optimizer steps; 100 GPU assignment calls; zero CPU fallback.
- Forward, finite loss/gradients, backward and optimizer update run on CUDA.
- 320 parameter tensors changed; absolute parameter change sum 12134.146071.
- First ten-step mean loss **11.925852**, last ten-step mean **2.136085**.
- First step loss 20.517359; last step 1.961264. No stop chosen from these values.
- Training wall time **40.20238s**; complete runner 92.797s including preflight
  and final evaluation. No second actual training run.
- Peak allocated CUDA memory **123,324,928 bytes / 117.61 MiB**; reserved
  **140,509,184 bytes / 134 MiB**. This is allocator usage, not total system VRAM.
- `nvidia-smi` is sampled during execution in a private CSV; a separate summary
  records utilization and whole-GPU memory, including other desktop processes.
  Actual 70 samples, maximum utilization 59%, whole-GPU peak 1,456 MiB.
- Checkpoint SHA:
  `bc62d86f4bdbefbfc353c0260ba4fb57e300437d2468e61ce5d4fbdaddd1820c`.
- All saved/reloaded model, optimizer, config and step fields compare exactly;
  model strict reload passes. No extra validation forward used for round-trip.

The original upstream autocast deprecation warning remains informational; no
upstream files were edited to suppress it.

## One DEV_VAL evaluation — first result preserved

Exactly two post-training inference forwards, one per held-out match 04 image.
Each saves all 3,549 decoded raw rows, fixed confidence 0.001 / class-aware NMS
0.65 predictions, original-image bboxes and per-GT best same-class IoU.
One-to-one matching IoU is fixed at 0.5. No thresholds or budgets changed.

| Frame | Accepted GT | Fixed-IoU hits | Best same-class response |
| --- | --- | --- | --- |
| 68s | Witch 1 | 1 | IoU 0.644608, confidence 0.001066 |
| 68s | Skeleton 3 | 0 | Each best IoU 0; no localized retained Skeleton response |
| 72s partial | Witch 1 | 0 | Best IoU 0.008379, confidence 0.001804 |

Overall **1/5** matched positives. Complete 68s has 78 retained candidates,
including **77 sampled-frame false detections** at the intentionally low score
gate. Partial 72s has 31 retained candidates: **30 unjudged Unknown**, one
padding-only/outside-image candidate, and no FP/precision claim. Padding-only
boxes remain auditable but never count as image-level false detections.
Visuals show green GT and the fixed top 30 valid-image candidates, orange
Skeleton/cyan Witch. A very-low-ranked best match need not appear in top30;
the complete prediction/IoU JSON retains it. No presentation threshold was tuned.

Numerical learning is evident; the one very-low-score Witch overlap is a weak
spatial response, not evidence of a reliable detector. Skeleton detection failed
on these retained outputs. No mAP pass gate, full-match FP/min, owner distinction,
blind-test result, production Model Lock or card-play inference is claimed.

## Verification and resolved preflight issues

- Before new real training: fresh GT/dataset-lock private tests **65 passed**;
  original dataset validate exit 0 and offline pip check exit 0.
- Full maintained regression, from `tools/offline_video`, existing process-bound
  awake wrapper invoking `python -m pytest -q --tb=short --junitxml=...`:
  **908 passed / 3 existing Windows symlink-permission skips**, exit 0,
  1146.78s. JUnit/stdout/exit receipt retained privately; zero failures/errors.
- New standalone smoke behavioral tests: pre-run **25 passed**, post-run
  **26 passed** (14.12s), including original-image padding, one-to-one matching,
  Unknown coverage, immutable export/attempts, exact transfer keys, config/source
  gates, UTF-8 metadata, monitoring errors and protection checks. Actual command:
  `.venv/Scripts/python.exe -m pytest tools/smoke_training/tests -q --tb=short --junitxml=...`.
  These are separate suites, not a fabricated single 934-test invocation.
- Both offline/model `pip check` pass; no package installation or upgrade.
- Fresh post-run official source check: all 160 regular-file hashes in the
  Phase B source inventory match. Local reviewer independently compares all
  91 Python files plus LICENSE to the original official source archive.
  Downloaded pretrained weight SHA remains unchanged.
- Hash protection before/after checks all **1,462** historical files: four
  recordings, 1,405 ignored evidence/media files and 53 tracked legacy
  source/tests/config files. Parent GT and Dataset Lock SHA unchanged; export
  images/labels/config unchanged. Private outputs remain ignored/untracked.
- Full diff, links and privacy checks accompany the final local commit; no push
  or merge. Module 1 and old prepare/validate/review/readiness semantics unchanged.

Resolved without a second model experiment: Windows default GBK could not decode
UTF-8 official API metadata; parsing was fixed before downloading/training,
reusing existing immutable export. Initial protection checker incorrectly treated
the historical tracked source entries as private and launched per-file Git
checks; corrected tracked/ignored grouping preserves all hashes with batched Git
checks. Padding and GPU-monitor evidence issues were caught by read-only local
review and synthetic RED/GREEN tests before the first real run.

After training, raw pip-freeze comparison differed only because editable
`clash-tracker-video` embeds checkout HEAD (9fd65d9 to bfc834d). The new verifier
permits only approved local commit refs in that exact editable line; every other
line, package version and isolated model environment still matches. Original
53 legacy source/config hashes confirm unchanged installed code. The original
comparison failure is retained in the diagnostic note/tool trace; a new
successful protection receipt explains
the distinction. Only checker/test code changed afterward, not the frozen
training/export/evaluation implementation, config, weights or predictions.

## Outputs and stopping boundary

Ignored local run directory: `outputs/module2b2b/phase-c/nano-smoke-20261006-attempt01/`.
Includes configuration, current authorization, official pretrained provenance,
deterministic dataset/manifest, frozen code/data/config hashes, loss history,
GPU telemetry, checkpoint, raw outputs, predictions, annotated images,
evaluation summary, protection/test receipts and Completion Report.
`Two_Class_Smoke_DEV_VAL_Review.zip` contains only two annotated DEV_VAL images
and evaluation/telemetry summaries; no video, original images, crops or weights.
Actual size 957,992 bytes (about 0.96 MB); SHA-256
`9e73723ecdd52a72d4a610b7fdff9e6588f8c2268494d700ab22b419c9848da7`.
The ZIP stays local until the user chooses to submit it for independent review.

No new recording/GT, DEV_VAL training, Tiny experiment, Clash Royale third-party
weights/data, blind testing, Model Lock, Module 3, Android/live feature, push or
main integration. Stop at execution completion and await independent acceptance.
