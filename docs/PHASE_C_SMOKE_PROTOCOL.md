# Phase C — Fixed Two-Class Learned Detector Smoke Training

User-authorized 2026-10-06. This is a local development smoke experiment, not
blind testing, validated card-play recognition or a production Model Lock.

## Prerequisites and artifact identities

Commit the existing Phase A/B/GT/data-lock public state locally before new real
training code experiments. Validate the existing training lock with exit 0.
Keep original GT, images and exports ignored; do not change old lock contents.

| Artifact | File SHA-256 |
| --- | --- |
| Smoke GT v1 | `f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1` |
| Training Dataset v1 | `582dc30d3e418aebf09adfed931742627c29a1f3da1a19ae24c165621cc58e39` |

Classes are `unit.skeleton=0`, `unit.witch=1`; form may be unknown and owner is
metadata. TRAIN match 01 contains two frames, Witch 2 / Skeleton 4 boxes.
DEV_VAL match 04 contains two frames, Witch 2 / Skeleton 3 boxes. Export all
eleven accepted boxes and no rejected object 12. Match identity isolates splits.
Witch-spawned Skeleton remains a visual unit, not a Skeleton-card deployment.

## Fixed training and evaluation settings

- YOLOX-Nano only; official source commit
  `6ddff4824372906469a7fae2dc3206c7aa4bbaee`, version 0.3.0.
- Existing isolated Torch 2.7.1+cu118 / TorchVision 0.22.1+cu118 environment;
  GTX 1050 Ti, CUDA execution mandatory, FP32, input 416, batch 1.
- Seed `20261006`; deterministic sample order cycles the two TRAIN images;
  no workers, Mosaic, MixUp, flips, HSV, random scales or other augmentation.
- Exactly **100 optimizer steps**, SGD learning rate 0.001, momentum 0.9,
  Nesterov enabled, weight decay 0.0005 on non-BN weights only, no
  scheduler/early stopping/validation during training.
- Deterministic full-image BGR 0..255 float32 letterbox: left/top aligned,
  scale=min(416/H,416/W), linear resize, padding 114, CHW. Preserve every box.
- Transfer matching pretrained parameters; initialize the 80-to-2 class
  prediction layers freshly and document skipped keys. No silent missing backbone.
- Record every loss, gradients/parameter changes, wall time, peak allocator and
  sampled whole-GPU usage. Save model/optimizer/config, hash, strict reload.
- **One** post-training DEV_VAL forward per image. Fixed confidence 0.001,
  class-aware NMS IoU 0.65 and matching IoU 0.5. Save all decoded raw outputs
  as well as retained candidates; these values are not tuned on DEV_VAL.
- Visualizations show GT plus up to 30 highest-scoring retained detections,
  using a fixed display limit, not a newly selected presentation threshold.
  Padding-only boxes remain in the saved prediction audit, but zero-area boxes
  after original-image clipping are explicitly outside-image, not image FP.

## Unknown and evaluation boundaries

TRAIN's two frames are complete for the selected classes. DEV_VAL at 68s is
complete for them; 72s is partial and has one confirmed Witch positive.
Export coverage metadata explicitly; never add absent/rejected objects as
negative labels. The partial frame can report each accepted GT's best same-class
IoU, scores and coordinates, but unmatched predictions are **unjudged Unknown**,
not false detections. Full-frame negative loss/metrics are forbidden there.
For the complete DEV_VAL frame, fixed-IoU one-to-one same-class matching may
report unmatched retained predictions as sampled-frame false detections.
No mAP success gate, full-match FP/min, owner distinction or generalization claim.

## Weight provenance and privacy

Only [official YOLOX release 0.1.1rc0](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0)
asset `yolox_nano.pth`, exact URL:
https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth.
Record repository/tag/URL before download and local SHA-256 after it. Upstream
code is [Apache-2.0](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/LICENSE);
that does not clear COCO photographs, learned-weight rights or game assets.
No upstream asset digest is advertised; local digest pins the downloaded bytes,
not independent publisher authenticity. Intended use private_local_research_poc,
redistribution false, rights_clearance unverified. No external upload.

## Execution and stopping point

1. Validate/data protection and commit clean local historical checkpoint.
2. Test deterministic export, split/bbox/coverage checks and evaluation logic
   before implementation; commit tested training code/config before real run.
3. Record/download only authorized official weights. Freeze the run's exact
   code SHA/config/data/weight digests and exclusive attempt directory.
4. Train once to the fixed budget; save/reload checkpoint; evaluate DEV_VAL once.
5. Preserve all outputs even on failure. Full regression, pip/diff/privacy/data
   protection, completion report and a small DEV_VAL review ZIP; stop.

No result-driven retraining, additional steps/frames, extra classes, Tiny,
third-party Clash Royale material, Blind Test, production Model Lock, Module 3,
Android/Overlay, push or main merge. A crash is recorded, not permission to
silently start another real run. Data/media/checkpoint artifacts are never Git source.
