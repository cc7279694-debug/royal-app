# Module 2B-2 — Data Preparation Design

Status: user approved first implementation slice on 2026-10-05, with task-by-task
implementation and review. Based on the user's supplied **Learned Minion Visual
Detector** design. The remaining training/model/blind-test slices are not part of
this slice's execution approval; no model dependency or publication is authorized.

## Baseline and goal

Accepted main: `8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.
The accepted 2B-1 outcome concerns that fixed template baseline, not proof that
every possible template method fails. Do not tune or rerun it.

Build a local expansion intake, individually boxed `minion_unit` annotations,
verified counts, grouped folds, and an immutable Training Dataset Lock referencing
the existing 2A2 Development Lock. Do not edit or replace the old lock or its six
group boxes. Existing images may be referenced by new individual annotations;
group boxes must never be automatically split into three invented unit boxes.

## Why a separate contract

The existing v1 evidence contract requires 3–5 annotations at distinct times per
verified deployment. The 2A2 readiness layer deliberately owns a single match
with at least two plays. Neither contract is suitable for multiple boxes in one
frame or for adding a new match with just one confirmed target play. Reuse their
strict JSON/media/PTS and old-lock verification, not those eligibility rules.
Keep Module 1 and `prepare / validate / review` unchanged.

## Intake and completeness

- Preserve original natural recording order and all previous evidence/history.
- Already exposed retained recordings may become development expansion, not
  prospective blind tests. Mere knowledge that a file exists does not itself
  constitute pixel/label exposure; these four have recorded boundary exposure.
- Include valid target-positive matches in order, regardless of difficulty.
  No-target and invalid sources remain retained with reasons, not forced samples.
- A new match with one confirmed ordinary Minions play can qualify for expansion.
- `completion_attestation=user_confirmed` permits absent result UI. Its complete
  segment must cover exactly `0..last_frame_seconds` from actual normalized PTS.
  Corrupt, undecodable, clearly mid-battle truncated, key-content-missing or
  human-declared incomplete recordings still reject.
- Do not claim an unseen match has no target, full review, or precise deployment
  times on the basis of a sparse contact sheet. Missing facts remain pending.

## Independent units of evidence

The target card is opponent ordinary `minions/normal`; the visual class is
`minion_unit`. They are different concepts.

At least **4 distinct target-positive underlying matches** and **8 independently
confirmed target deployments** are required. Count matches by
`underlying_match_id`, deployments by their match-scoped event identity, not
recording hashes, frames, boxes or augmentations. Multiple recordings of one match
share one identity. The current accepted source supplies one match/two plays.
Identical spawn/annotation evidence under renamed event IDs cannot increase
counts. Honest provenance and independence still require human attestation.

Every deployment keeps onset bounds, owner, source card, form, verification and
occlusion/visibility provenance. Ambiguous or unreviewed plays remain in the
inventory but do not count toward the eight. An eligible play needs at least one
fully reviewed positive frame; roughly four spaced frames is the sampling goal,
not a reason to invent four frames or force three visible units in every frame.

## Unit annotation

- One rectangle per identifiable visual unit; use the tight **visible extent**,
  not an inferred hidden body, shadow or beam. Record occlusion and truncation.
- Use original rotated-image dimensions and normalized full-image coordinates.
  Store exact frame ID/PTS/time base and metadata/content binding.
- Each annotation has its own ID and inherits its source deployment identity.
  Multiple frames and boxes never become independent deployment counts.
- Label all identifiable minion-like visual units in a training image, including
  other sources or own-side units. Preserve owner/source/form independently.
  Visual positives of another source are not ordinary-card semantic positives.
- `normal / evolved / unknown` remain separate metadata; only manually confirmed
  opponent `minions/normal` plays contribute to target readiness.
- A frame with uncertain potentially unlabelled minion-like objects remains
  pending/excluded from the training view, not empty-box background. Retain hard
  matches and deployments; frame uncertainty is not permission to cherry-pick
  entire matches. No automatic ground-truth generation.
- Use the existing Pillow plus standard-library Tkinter for a minimal local
  image/drag-box/review/save/next tool. No web service or new dependency needed.
  Revision writes are additive in ignored directories; preserve original labels.

## Negative frames are not evaluation time

Two to four manually confirmed zero-minion frames per included match may supply
empty-box training examples. They do **not** certify the surrounding timeline.
Keep continuous `confirmed_absent_intervals` separately, with explicit review
provenance. Unknown intervals, unreviewed gaps and other/unknown forms never
become negatives or a false-evidence time denominator.

Later FP/min uses the union duration of reviewed absent intervals, without double
counting overlaps. Zero certified duration means **not evaluable**, not zero FP.
This slice reports `evaluation_ready=false` when that coverage is missing; it may
not advertise that the future development metric is ready.

## Dataset and split lock

A closed version-one dataset draft binds: dataset ID/version/explicit UTC time;
old Development Lock SHA; fixed target/visual class; original-order intake and
exclusion history; match/recording identities and completeness; deployments;
frames/unit boxes/review states; unknown and absent intervals; media/index/pixel
bindings; full-image coordinate and visible-box policy; grouped fold assignments.
Real paths, media hashes and labels remain private.

LOMO uses every included target-positive match. With N matches create N folds,
each with one held-out underlying match and all others training. All recordings,
frames and later augmentation derivatives of that match inherit its assignment.
No random frame split, renamed/reencoded same-match leakage or test data.
The later stability rule for N>4 must be fixed before training; it is not silently
inferred from the four-match example in the user's overall design.

Canonicalize deterministic derived collections using the bound intake/event/frame
order, preserve explicitly meaningful order, and serialize with the existing
`canonical_bytes` primitive. Digest covers all experiment semantics except itself.
Equivalent same-input preparation must reproduce bytes/digest; explicit version
or UTC changes legitimately change the digest.

Use a separate `training_dataset` envelope and exclusive versioned files, e.g.
`DATASET.training_dataset.vVERSION.json`, in a dedicated ignored lock directory.
Never extend old `LOCK_TYPES` or overwrite a freeze. Corrections/additions create
a new version. On disk freeze/load, reverify the declared existing media/index/
annotation bindings. Snapshot validation alone does not prove external integrity
or source authenticity.

## Stop states and later boundaries

Report distinct derived fields: valid draft, training-data readiness, evaluation
coverage readiness, independent match/play counts, image/box counts, unknowns,
and missing requirements. Insufficient data is a valid waiting outcome.

When all dataset requirements hold, freeze the training dataset and stop for
acceptance. This does not authorize installing a model runtime, downloading
weights, training, running a detector/aggregator, a Model Lock, blind testing,
Module 3, Android/HUD, publication or main integration.

Later training retains the user's Faster R-CNN/MobileNetV3-FPN direction,
license-before-download gate, fixed recipe, match-level CV, >=75% timely event
recall, <=0.5 false visual events/min, and model-before-GT-before-inference chain.
GPU/runtime compatibility, weight rights/hash provenance, threshold grid,
aggregation and matching rules must be fixed in that later plan, not improvised
after seeing validation results. Official TorchVision notes that pretrained
weights may have their own dataset-derived terms:
https://docs.pytorch.org/vision/stable/models.html

## Verification

Synthetic tests must cover independent counting, renamed duplicate evidence,
single-play expansion, multi-box frames, form/source separation, unknown/negative
conflicts, actual end boundaries without result UI, grouped leakage, digest
sensitivity/determinism, exclusive freeze, source tampering and path/JSON safety.
Run all maintained legacy tests without rewriting their expected semantics.
Snapshot and compare existing private evidence before/after any approved data work.
No private recordings, frames, labels, locks, hashes or weights enter Git.

## Read-only environment findings

On 2026-10-05: local/remote main match the baseline and working tree was clean;
the old real Development Lock passed `validate-lock`. NVIDIA reports GTX 1050 Ti,
4096 MiB VRAM; project environment has no torch/torchvision. Tkinter 8.6 imports.
These facts do not establish CUDA/PyTorch training compatibility or capacity.
