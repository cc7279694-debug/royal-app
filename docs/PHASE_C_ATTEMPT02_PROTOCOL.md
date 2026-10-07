# Phase C — Attempt02 two-class smoke protocol

Authorized by the user's explicit Attempt02 instruction, 2026-10-06.
Attempt01 was accepted as `TWO_CLASS_SMOKE_ATTEMPT01_VALID_BUT_INSUFFICIENT`.
Its original result, checkpoint, exported labels, config and code stay unchanged.
No confidence-threshold repair claim is allowed.

## Scope and prerequisites

TRAIN remains only `natural_match_01`; `natural_match_04` is now `DEV_TUNE`,
not a blind or independent test. Historical locked `DEV_VAL` fields remain
unchanged; new artifacts record this current role separately.

Check the two old TRAIN exports against all six original human-confirmed boxes
and exact source PNG hashes before any new training. Classes are fixed:
`unit.skeleton=0`, `unit.witch=1`. Export mismatch blocks training.

Prepare 6–10 representative positive and 6–10 candidate negative TRAIN frames,
12–20 total, from match 01 only. Newly drawn boxes are
`draft/pending_human_review`, never confirmed GT. Existing approved objects
retain their review provenance. Every actual training frame needs explicit
selected-class exhaustive review, including both own and opponent Witch and
Skeleton visible in the training ROI. A candidate zero-label frame needs
explicit absence confirmation; no unresolved relevant Unknown region may enter
standard YOLOX background loss. Exclude an unqualified frame rather than infer
missing annotations. Rejection of an uncertain object is not Negative evidence.

Continuous Witch/Skeleton sightings retain appearance identity. Separate
skeleton single-unit identities may be pending if continuity is not provable.
Spawned Skeleton is a visual class, not a Skeleton-card deployment. The number
of frames or single-unit boxes never increases independent deployment counts.
Expanded annotations require a new immutable snapshot; do not append to or
overwrite GT v1 or Training Dataset Lock v1.

## Fixed ROI and model settings

ROI rule is chosen from match 01 geometry only before any Attempt02 prediction:
half-open pixel rectangle `[0, floor(H*0.125), W, floor(H*0.775)]`, using exact
rational integer arithmetic. For 432×960 it is `[0,120,432,744]`, 432×624.
It excludes the top HUD/name/timer band and bottom cards/elixir/peripheral
decorations, retaining full horizontal width to avoid cropping playable outer
lanes. This rectangular ROI still contains some side decoration; it is not an
automatic battlefield segmentation or enemy-half mask. TRAIN and DEV_TUNE use
the identical rule. Do not adjust it from DEV detections. Boxes must be fully
inside the ROI; crossings are explicitly unqualified, never silently dropped.
Keep original-image GT and audit the translated ROI boxes and reverse mapping.
The old partial 72s frame remains partial even after cropping.

- YOLOX-Nano only, input 640, batch 1, FP32, GTX 1050 Ti CUDA.
- Seed 20261006. Exactly **300 optimizer steps**; no early stop or DEV feedback.
- SGD lr 0.001, momentum 0.9, Nesterov true, non-BN weight decay 0.0005;
  no scheduler. CPU-cache images, transfer only one input per step to GPU.
- No augmentation (including Mosaic, MixUp, random crop, flip or scale), a
  conservative allowed choice. No additional model/environment installation.
- Reuse the existing official COCO Nano release 0.1.1rc0 weight, SHA
  `cd28f55fbbc1829f99d9ac9b38a16d259a22889739c8728ea877610201feff7b`;
  preserve original provenance. No Clash Royale third-party data or weights.
- Freeze confirmed TRAIN frame order, image/annotation hashes, class map,
  expanded data snapshot, code/config/ROI/weight identity before first step.
  Fixed order cycles through frames; record actual per-frame step counts.
- BGR 0..255, FP32 CHW, left/top linear letterbox, padding 114. Labels shift by
  the crop offset then scale. Predictions inverse-scale then add the offset;
  distinguish letterbox padding from visible ROI before original-image mapping.
- Retain failed-start receipts; no implicit OOM resolution, CPU fallback,
  budget reduction, changed seed or retry to seek a PASS.

## One development evaluation

After the fixed budget, save/hash/reload checkpoint; run exactly one forward
per original DEV_TUNE image (68s,72s). Fixed confidence 0.001, class-aware NMS
IoU 0.65, GT match IoU 0.5, display at most top 30. Save all raw proposals and
retained detections with coordinate metadata; these are diagnostics, not an
optimized operating threshold. Preserve the five accepted DEV boxes, rejected
object12 and the old coverage declarations. Unmatched proposals in partial
72s remain unjudged, not confirmed false positives. No FP/min or mAP claims.

Compare Attempt01 and Attempt02 GT IoU/confidence/matches, sampled-frame false
detections, loss and time/memory. Input, ROI, data and budget change together;
do not attribute improvements to just one factor. Poor evaluation remains a
valid experiment. No Attempt03, Blind Test, production Model Lock, Module3,
Android, HUD, live match use, push or main integration.

## Confirmed review return and run boundary — 2026-10-07

The user relayed `ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED`: 11 new objects
confirmed, four rejected, original bboxes accepted. Six prior objects inherit
the unchanged v1 GT. The new expanded snapshot retains 16 TRAIN frames and 17
confirmed objects; only **14 standard TRAIN frames / 15 boxes** enter loss:
eight explicit exhaustive negatives and six exhaustive positives (Witch 6,
Skeleton 9). Confirmed Witch boxes at 162s/165s remain archived but their partial
frames never enter standard loss. Rejected regions are not Negative.

The old Witch episode stays one independent deployment. Left Skeleton 160s/161s
has confirmed continuity with origin/source unknown, not an independent card
deployment; 162s is unresolved. The 166s Skeleton wave keeps its confirmed
spawned-from Witch relationship; rejected 165s proposals do not establish it.
Freeze a new exclusive expanded GT v2, with the exact human return bound to the
original reviewed ZIP. Validate exact source/ROI pixels and box round-trips
before the only authorized run. Keep all old v1 locks immutable.

No new parameter choice or training budget is introduced by this return.
Local public code/document baseline commits inherit the Phase C requirement for
a clean reproducible run; push and main integration remain prohibited. After
one 300-step training and one two-frame DEV_TUNE evaluation, preserve the actual
result and stop, even if localization is insufficient.
