# Module3C5 — Detector Improvement Sprint A: data admission checkpoint

## Goal and stopping point

Improve Royal Hogs / Minions visual evidence, not formal tracking/event rules.
Authorized from local `d699877ecc83cfa4cc26945879dc1b7466995922`;
branch `codex/module3c5-detector-improvement-a`. The conditional training gate is
not met. This checkpoint records inventory and a pending review supplement,
**not detector improvement or a failed new training run**. No production source,
test, dependency, environment, engine/rule/scorer or Android change.

## Verified inventory (real data only, versions deduplicated)

| Existing source | Accepted bbox records | Qualification / coverage |
|---|---:|---|
| Multiclass first/second batches |44+39=83|Human accepted original bbox; annotation-only locks, training_qualified=false|
| Witch/Skeleton v1 plus Attempt02 latest union |22|17 TRAIN boxes (15 standard,2 partial) and5 DEV_TUNE; only old two-class scope|
| Field-Level Review Snapshot v1 |0 complete bbox|49 unverified boxes/40 nonexhaustive frames; only supported fields/links confirmed|
| Older Phase A provisional |0 frozen accepted bbox|8 pending single-unit boxes;6 reported Minion accepts explicitly not imported GT|
| Historical2A2 |6 combination boxes|2 confirmed Minions deployments; not6 unit labels|

105 accepted bbox records are not105 qualified supervision records. Original
11 Witch/Skeleton boxes are contained in the22-record union, not added again.
Its14 standard TRAIN frames include8 negatives exhaustive only for Witch/Skeleton;
two further partial TRAIN frames and partial DEV_TUNE material stay excluded
from ordinary complete-background loss. Those negatives cannot become new-target
Negative or a full-match FP/min time denominator.

Target accepted records:28 Minion boxes/12 frames and5 Royal Hog boxes/3 frames,
all opponent match01 with form/origin unknown. The geometry is finite/in-bounds;
user confirmation and lock member bindings validate. Observation-only identity
tokens are not distinct physical units/deployments. Minion has8 class-exhaustive
positive frames (14.5,19.5,22,24.5,27,117,119.5,122s); four are nonexhaustive.
Royal77/79.5/82s frames all unresolved/nonexhaustive with possible missing boxes.
**Joint two-target exhaustive frames proven0; eligible target Negative0;
qualified target standard training frames0.** First/second batches retain932
pending and2 rejected proposal regions; none automatically become background.

All49 field snapshot boxes remain unverified, including12 Minion and6 Royal
class/owner-only records. Supported fields are not pixel-exact box validation.
Snapshot byte SHA remains:
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.

## Source isolation gate

Royal has one known confirmed deployment source; Minion has two historical
human-confirmed deployment sources in match01. Counting adjacent frames or
observation tokens cannot produce independent sources. No source assignments
are frozen:TRAIN/DEV/RETAINED_EVAL remain unassigned. Same source must stay in
one role, including duplicates identified by recording SHA+exact PTS rather
than different frame-ID spelling. Source roles/config must freeze before the
one permitted experiment; no deployment/event GT is used to tune model output.

Existing03/04 review material has159/107 frames but no finalized target unit GT
or pre-existing teacher localization proposals in that review bundle. This
does **not** prove target absence in their videos. The old third-match0–20s
matchmaking prefix has no battlefield target support; it is not an evaluation
set. The52–57s combat clip is real but previously reviewed and only confirms
other class/presence fields. Third/fourth have prior development exposure, not
blind status. Match02 remains mid-match truncated/excluded, not deleted/Negative.

Minimal next remedy:finish this bbox/region review, then locate and human-confirm
independent Royal/Minion source support in existing03/04 combat if present. Only
if absent is minimal new natural footage needed. If three source-isolated roles
each need both classes, the current known source inventory lacks two Royal
sources and one Minion source; this is a conditional split-support count, not a
new4-match/8-play quota. Deployment-isolated evaluation within match01 would not
justify cross-match generalization. No current split, dataset, or metric is
training/evaluation-ready.

## Private review supplement

Folder:`outputs/module3c5/review-v1/`.
ZIP:`outputs/module3c5/Module_3C5_Minimal_BBox_Review_v1.zip` (6,258,452 bytes).
ZIP byte SHA:
`f785a7b1000beb42ef359835d5bc8dad392f980b6edf789a0278ca3a7600232a`.

Eight existing source PNGs:14.5,24.5,77,79.5,82,117,119.5,122s; no extraction
or new model proposal run. Includes two JPG contact sheets, original PNGs,
annotated JPGs/crops, exact PTS/frame/source metadata, inventory and unassigned
split facts, object/coverage/missing-box CSVs, explicit human-return template.
28 reference rows=19 immutable prior accepted bbox references plus9 unverified
drafts; overlapping same-PTS sources are not28 new objects. Original pixels match
byte/RGB hash; alias frame namespaces are checked at the same recording+PTS.

Prior bbox confirmation remains intact; a correction creates a future new
revision, never edits old locks. All new decisions pending;16 two-class region
review rows pending. Fixed review ROI [0,120,432,744] inherits Attempt02 and is
not a new frozen training preprocessing config. Human must correct/merge overlap
or add missed boxes and identify unresolved regions; no automatic Negative.
Unknown identity/owner/form/origin stays unknown, no new card plays. reviewer
empty/attestation false until user confirms; ChatGPT is a review basis, not a
human reviewer. Full PNGs contain game UI/nicknames:private user-chosen review,
**not anonymized/public redistribution**, no automatic external upload.

## Existing model prerequisites

Current installed metadata:Python3.12.4,Torch2.7.1+cu118,TorchVision0.22.1+cu118,
NumPy1.26.4,OpenCV-headless4.11.0.86,pycocotools2.0.10. Existing isolated YOLOX
source0.3.0 commit `6ddff4824372906469a7fae2dc3206c7aa4bbaee` is retained.
GTX1050Ti CUDA qualification is historical; no new CUDA/model step run here.
Both current offline and model-environment pip checks pass without installation.

Existing Nano COCO weight hash/provenance matches:
`cd28f55fbbc1829f99d9ac9b38a16d259a22889739c8728ea877610201feff7b`.
Original recorded source is the official Megvii-BaseDetection/YOLOX release
`0.1.1rc0/yolox_nano.pth`; code Apache-2.0, rights_clearance=unverified. Code
license is not legal clearance for COCO/learned weights/game assets. Private local
scope and no redistribution remain; no new download/third-party game weight.

## Fresh verification

Read-only first/second preannotation validation exits0; actual frozen members8/9
and source bindings validate. Existing scaled training data is not silently
requalified. Four fresh scoped suites, separately to avoid duplicate test module
names:

```text
.venv/Scripts/python.exe -m pytest tools/preannotation/tests -q --tb=short
51 passed
.venv/Scripts/python.exe -m pytest tools/event_engine/tests -q --tb=short
84 passed
.venv/Scripts/python.exe -m pytest tools/smoke_training/tests -q --tb=short
26 passed
.venv/Scripts/python.exe -m pytest tools/smoke_training_attempt02/tests -q --tb=short
174 passed
```

Combined335 distinct tests pass/0 skipped. Initial combined-directory invocation
had2 collection errors from same-named test_cli/test_contract modules before
assertions; preserved `regression.xml`. Separate fresh runs all pass without
editing tests, removing caches or production changes; individual JUnit files
preserve complete suite evidence. Both pip checks exit0, No broken requirements.

Final private readback verifier exits0:198 artifact/link/CLI checks,3210 protected material
files and224 tracked non-status source files unchanged (3434 hash checks).
Includes four original videos, all old locks, frozen predictions, Oracle
FAIL/PASS and3C experiments, Field Snapshot/members and original weight.
ZIP CRC/exact56 members/SHA,8 PNG/PTS/RGB bindings,9 alias pixel bindings, pending
flags and16 coverage requests pass.86 public document links resolve; two real
preannotation CLI validations exit0. All enumerated new private files ignored;
no outputs/local_data tracked. Full suite, Android/JS/build/GPU/model inference/
training/event scoring Not Run, because this stage stops at data admission.
No new detector P/R/IoU/owner/speed or after-engine metrics:Not Run, not0/FAIL.
Old2/5 detector and4/5 tracking history remain, not a like-for-like sprint result.

## Public delta and handoff

Only CURRENT_STATE, DEVELOPMENT_PLAN and this checkpoint are changed. Private
audit/presentation helpers, receipts, images/CSV/ZIP stay ignored. No SQLite,
migration, repository layer, backup, manifest, App or dependency changes.
Local commit only; no push/main merge. No training config budget/checkpoint or
model/data lock is created prematurely. Finish at the required reporting marker
`MODULE_3C_5_DETECTOR_IMPROVEMENT_READY` with **human/data gate blocked** clearly
reported. Next action is pixel/coverage and independent source confirmation,
not another event-rule patch or automatic training.
