# Existing Multiclass Detector Local Benchmark

Date: 2026-10-07. Branch: `codex/existing-multiclass-local-benchmark`.
Start baseline: `9600236f18a8bae6861ceb905bff38d510d11d48`.
Status: **EXISTING_MULTICLASS_BENCHMARK_COMPLETE — fixed local inference executed;
ChatGPT visual review pending, recognition accuracy not accepted**.

## Authorized scope

The user accepts `ATTEMPT02_VALID_BUT_DATA_LIMITED` from the reported statistics,
not an independent image/code review (ChatGPT could not extract the ZIP).
Preserve both experiments; no Attempt03, threshold/step tuning or added Skeleton
labels. This is a new inference-only feasibility probe, not another training run.

Use only the original detector sources linked by KataCR's own README, in a new
isolated venv. No dataset, training, game connection, policy agent, OCR, production
Model Lock, Module3, Android, HUD, push or main integration. Existing YOLOX and
offline environments must stay unchanged.

## Official source and provenance

Pinned upstream commit: `36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8` (current
master rechecked with GitHub API). [Official README](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/README.md)
links the dual v0.7.13 detectors, not a GitHub release asset:

- [detector1 original Drive file](https://drive.google.com/file/d/1DMD-EYXa1qn8lN4JjPQ7UIuOMwaqS5w_/view?usp=drive_link):
  87,793,385 bytes, downloaded SHA-256
  `72707f7af25a6b95e9dc8c3dbbf317cc727dbc5d7b457dae64b5c32e9a7024f2`.
- [detector2 original Drive file](https://drive.google.com/file/d/1yEq-6liLhs_pUfipJM1E-tMj6l4FSbxD/view?usp=drive_link):
  87,788,969 bytes, downloaded SHA-256
  `613062634618679418ef238acb6077c7357dfafde32b4f6078dde346f73d865a`.

Both original-host downloads succeeded, with no mirror or reupload. Source and
intended use were recorded before download. Upstream did not provide SHA-256;
these local digests identify downloaded bytes, not independent authentication.
Checkpoints reference the expected custom CRDetectionModel/standard Torch and
Ultralytics classes; static pickle inspection is not a safety proof.
The published detector1 filename is `detector1_v0.7.13.pt`, while its embedded
training name is `detector1_v0.7.12`. Detector2's embedded name is v0.7.13.
Preserve this discrepancy: filename versions do not establish exact training
identity. The downloaded byte digests above, not an inferred version, bind this run.

Root software [LICENSE](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/LICENSE)
is MIT. Modified YOLOv8 files and Ultralytics 8.1.24 carry AGPL-3.0 obligations;
root MIT does not override them or license game assets. Separate weight license,
complete training provenance and game-asset rights are not established.
`rights_clearance=unverified`; explicit user authority permits only this internal
private-local research benchmark, not a legal-clearance conclusion or
distribution/product integration. No third-party training material was imported.
A venv isolates dependencies, not security; Torch pickle loads still require
trust in the pinned official publisher and its dependencies.

## Frozen probe

Use the first retained natural recording, match01, without quality-based match
selection. Fixed file-relative PTS window **12..72s exclusive**, 4 samples/s,
240 samples selected before predictions. This already-used development match is
not a blind or independent test.

Source UI was inspected before inference. It has the live-layout card bar;
offline recording does not imply the alternate replay layout. Reproduce the
official 2.22 live-layout crop from [constant.py](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/build_dataset/constant.py):
432x960 original, ROI `[8,67,422,729]`, integer-truncated proportional crop,
Explicit INTER_CUBIC resize to 576x896. All boxes map back to original coordinates.
This is not byte-identical reproduction of upstream preprocessing: the upstream
`extract_bbox` puts `cv2.INTER_CUBIC` in the third positional `dst` argument,
which defaults to LINEAR interpolation in the Python binding. A synthetic-only
OpenCV4.9.0 check confirmed literal-upstream output equals explicit LINEAR and
differs from explicit CUBIC. The fixed wrapper used explicit CUBIC, matching the
apparent author intent, but no claim of exact upstream resize behavior is made.
This was discovered after the single run; neither configuration nor results
were changed, and no second inference was run to improve the outcome.
Display-only black masks hide the fixed header/card UI; inference input is not
changed by this visualization mask.

- dual original detectors; input longest-side896, batch1, FP32, CUDA0;
- fixed proposal confidence0.1, per-detector IoU0.7/max300;
- confidence0.1 is a permissive benchmark proposal cutoff sourced from the
  active upstream tracked entry point, **not** the tracker-free default0.7;
- tracker disabled; no continuous-unit or card/deployment identities inferred;
- preserve original class-agnostic cross-detector NMS IoU0.6 and fixed UI filter;
- retain raw per-detector rows plus pre/post merge/filter diagnostics;
- local class IDs map via checkpoint names to the common upstream label registry;
- padding/unmapped proposals retained as diagnostics, not promoted to units;
- last belong channel0/1 maps to predicted own/opponent for the bottom-player
  view. This is a prediction, not validated ownership or form/card semantics;
- deterministic keyframes every5s, not selected for good-looking predictions.

The wrapper imports only CRDetectionModel, CRDetectionPredictor and labels; it
does not import upstream train/predict/combo entry points, which pull dataset,
JAX, tracking or interaction paths. It independently draws overlays. Runtime
socket denial precedes library imports; YOLO autoinstall, telemetry/settings and
callbacks are disabled. This is a process-level privacy safeguard, not an OS
sandbox or universal security guarantee.

## Actual environment and result

Independent Python3.12.4 venv: Torch2.2.2+cu118, TorchVision0.17.2+cu118,
Ultralytics8.1.24, NumPy1.26.4, OpenCV4.9.0.80 (runtime4.9.0), CUDA11.8.
GPU: NVIDIA GeForce GTX1050Ti4GB, capability6.1, driver582.28.
Package sources/versions/license metadata were recorded before and after install.
Both installation dependency checks returned0. The old offline/YOLOX envs were
not upgraded or reused for this model; their package inventories remain equal.

Exactly one fixed real inference completed, exit0:

| Item | Observed result |
|---|---|
| Sample frames / actual PTS | 240 / 12.00..71.75s |
| Visualization | 60s silent video, 4FPS; 12 preselected screenshots |
| Per-detector post-NMS proposals | 9,287 |
| After cross-detector NMS | 5,404 |
| UI-filtered proposals | 86 |
| Final per-frame proposal rows | 5,318 |
| Distinct proposal labels | 84, including towers/UI/effects/noisy false candidates |
| Dual prediction time | median310.05ms, P95332.99ms, mean344.72ms |
| Whole run wall time | 97.88s |
| Torch peak allocated / reserved | 553.83MiB / 596.00MiB |
| Driver-reported system-wide GPU memory / utilization peak | 1,644MiB / 95% |
| Process CPU peak | 105.7%, psutil multicore semantics |

CUDA model parameters and input execution were checked. Dual timings include
pre/postprocessing and CPU merge; the first sample includes warmup. Wall time
includes decoding/resize/overlays/writing, but excludes installs and model load.
System-wide telemetry does not isolate this process's GPU use.

Witch, Minion, Skeleton and Golden Knight names occur among proposals; this is
not an exhaustive verified inventory of true battlefield units. Many low-score
wrong-class candidates are retained. **84 output labels are not 84 correctly
recognized classes/cards.** Confidence is uncalibrated, ownership only predicted,
and repeated per-frame rows are not independent units or deployments. No GT
accuracy, mAP, recall, FP/min, owner discrimination, card-play events, production
readiness or phone performance was evaluated. Only two fixed screenshots were
visually spot-checked locally; this is not independent or exhaustive visual
acceptance. All raw outputs and all preselected views remain available to review.

Three runtime socket calls were denied before library imports; destination
arguments were not captured. This is not an OS-level network audit. Forbidden
training/dataset/interaction modules were absent from loaded modules. No model
training, weight edits, event/card integration or result-guided second run occurred.

## Fresh verification and protection

The exact historical-helper regression command was:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tools/smoke_training/tests tools/smoke_training_attempt02/tests --tb=short --junitxml=outputs/existing-multiclass-benchmark/katacr-20261007-01/historical-helper-regression.xml
```

Actual result: **200 passed**, 0 failed, exit0,316.18s. The historical maintained
908-test suite was **Not Run in this turn**: public application/legacy training
code is unchanged and this is an isolated one-off inference probe. Its older
908/3skip receipt is not substituted for fresh verification.

The final before/after protection audit returned0 and confirmed:

- 32,217 existing files unchanged, including the four original recordings,
  historical Evidence/locks, Attempt01/02 configs, datasets, predictions and
  checkpoints; no re-extraction/relabeling or Attempt03;
- all 160 existing YOLOX source files unchanged;
- both old environment inventories unchanged and both `pip check` exits0;
- zero tracked private media; historical private files and this new probe remain
  Git ignored; no private source paths/profile names enter public documentation;
- the two new weight digests unchanged and pinned upstream checkout clean;
- all 240 timestamps/class-owner fields/bbox inverse transforms checked;
- visualization re-decodes to exactly240 frames; all12 keyframe PNGs readable;
- raw stage counts recomputed, fixed wrapper/config SHA binding checked;
- archive CRC, member byte readback and privacy exclusions checked.

One-off scripts, env, source checkout, weights, results and receipts are local
ignored artifacts, not a new application subsystem. Only six public status/
verification documents are changed; no public production/train code, dependencies,
database, schemas, CLI or previous lock was modified.

## Handoff and stop boundary

Local run root: `outputs/existing-multiclass-benchmark/katacr-20261007-01/`.
`detections.json` / `observations.csv` contain actual timestamps, raw per-model
rows, stage diagnostics and final class/confidence/original-coordinate boxes.
`evaluation-summary.md` is descriptive, not an accuracy acceptance report.
`detections-12-72s.mp4`, the 12 fixed `keyframes/` and `contact-sheet.png`
show the complete sampled clip, including noisy predictions.

`KataCR_Local_Benchmark_Review.zip` is preserved unchanged. The supplemented
`KataCR_Local_Benchmark_Review_v2.zip` adds identity/preprocessing caveats and
bounded public context without changing any original inference result/member.
The handoff is manual: no upload occurs automatically. It contains only derived,
UI-masked visualization and approved result metadata, not raw recordings,
GT/private labels, source crops, weights, environments or datasets.

ChatGPT independent visual review remains **pending**. Completion proves that
the pinned official detector pair runs on this fixed local footage, not that it
is accurate, distributable, commercially cleared or suitable for the final App.
No adoption decision or next module is authorized by this result. Main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`; no push/merge, training, production
Model Lock, Module3, Android/HUD or live game behavior. Stop after delivery.
