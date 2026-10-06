# Development Plan

The project advances one independently verifiable module at a time. A module may
start only after the previous module has been reviewed and accepted. Statuses are
`Completed`, `In Progress`, `Planned`, `Paused`, or `Gated`.

## Current separately authorized Phase C smoke experiment

Status: In Progress — explicitly authorized 2026-10-06; no training performed
at the initial clean local checkpoint. The completed Phase A/B/GT/data-lock
records below retain their original historical boundaries. The obsolete
ordinary-Minions specialist quota is not reinstated.

Execute only [the fixed two-class smoke protocol](PHASE_C_SMOKE_PROTOCOL.md):
validate unchanged locks, official COCO Nano weight provenance, deterministic
two-TRAIN/two-DEV_VAL export, exactly 100 FP32 optimizer steps on Nano 416/b1,
checkpoint round-trip, then one fixed DEV_VAL evaluation and local review ZIP.
No DEV_VAL training or result-guided retries/tuning. Unknown remains unjudged,
especially the partial 72s frame. No push, main merge, Tiny run, Blind Test,
production Model Lock, new data, Module 3 or mobile/live development.

## Module 0 — Project Bootstrap

Status: Completed

Goal: establish project identity, operating constraints, durable decisions, and
the staged development plan without implementing product code.

Acceptance criteria:

- stable project purpose and non-goals are documented;
- account-safety boundaries are explicit;
- current facts and unknowns are separated;
- module order and gates are recorded;
- repository documentation contains no unsupported implementation claims.

Verification:

- inspect document responsibilities and cross-references;
- inspect Git status and diff;
- scan for secrets and unintended binary/data files.

## Module 1 — Offline Video Pipeline

Status: Completed — accepted by the user; fast-forwarded into main and pushed
at e30ca01 on 2026-10-03 after 47 tests and dependency checks were rerun.

Goal: read one user-provided MP4 without performing card recognition.

Acceptance criteria:

- report duration, FPS, width, and height;
- use PTS/time_base relative to the first display frame; choose first frame at or
  after each requested time with inclusive 100ms tolerance, recording misses;
- export selected frames to a disposable, Git-ignored output location;
- return clear errors for missing, unreadable, or unsupported input;
- keep user recordings and exported frames out of version control.

Verification:

- automated tests for metadata and timestamp validation where practical;
- run against a small non-sensitive fixture and a representative user recording;
- verify exported frames visually and confirm Git remains clean of media.

Evidence: [Module 1 verification](VERIFICATION_M1.md). The user-provided recording
has passed timestamp, image, output safety, and visual verification.

## Module 2A — Offline Evidence and Annotation Preparation

Status: Completed — 2A1 formally accepted on 2026-10-04 at `98037ceba81683ad1a2c214bada30a10f2f3f69e`.
2A2 was separately approved and formally user accepted on 2026-10-04 at
`69162023b87b71209f8dec9ebc9af69d4bfda944`, with DEV_LOCKED. Its prospective
experiment rules below supersede the original 2A first-experiment thresholds;
the following four-play rules remain historical 2A1 semantics only.

Goal: manually identify usable match ranges, inventory opponent cards, choose a
defensible first target, prepare local annotations and assess data sufficiency.
No model, automatic boundary detector or custom annotation GUI.

Acceptance criteria:

- exact PTS-normalized local evidence and manually reviewed boundaries;
- at least four distinct manually confirmed deployments in current recording
  before selecting a troop/building target; no predefined Hog Rider;
- versioned annotations, full-image normalized boxes, reviewed negative ranges;
- a clear candidate-gate/insufficiency report; split implementation deferred to 2A2;
- no private media, labels, source paths or hashes in public Git.

Verification:

- synthetic validation, timestamps, final-frame interval semantics, coordinates,
  file safety, unique-play counts and current-single-recording insufficiency tests;
- reviewed real recording with honest uncertainty and data limitations;
- no model accuracy claim in this stage.

Planning documents:
[design](superpowers/specs/2026-10-03-module-2a-evidence-preparation-design.md),
[implementation plan](superpowers/plans/2026-10-03-module-2a-evidence-preparation.md).
Current candidate: Inferno Dragon, four verified distinct opponent deployments
and 12 original key-frame boxes; candidate gate passes. Unknown coverage gaps
remain explicit; this is not detector accuracy or full negative certification.
One observed match alone is insufficient for Module 2B.

### Module 2A1 — Current Recording Evidence

Status: Completed — formally user accepted on 2026-10-04 at
`98037ceba81683ad1a2c214bada30a10f2f3f69e`.
Tasks 1–4 verified. User supplied whole-playback review; executor inspected
original frames and entered four deployments, onset/visibility evidence and
12 key boxes. Actual validate/review exit 0/3, candidate true, experiment false.
Eight unknown gaps remain disclosed, not implicit negatives; status insufficient
correctly closes the one-match stage without opening the experiment gate.
The user separately authorized only acceptance documentation, fresh full tests /
dependency checks, a documentation commit/push, ff-only main integration/push and
preserving the implementation branch. See verification record and Git for the
actual integration outcome. No next module, second recording, split freeze or
model experiment was authorized by that acceptance action itself. Module 2A2
was subsequently authorized separately, as recorded below; it does not authorize
Module 2B. Module 3, Android capture and HUD remain unstarted and unapproved.

Four tasks: simplified contract/tests; local index/contact pages/safe output;
deployment intervals/key boxes/sufficiency; current-video verification/docs/report.
Commands only prepare / validate / review. Each verified deployment requires
last-absence/onset/visibility intervals and 3–5 distinct original key-frame boxes.
Four surviving plays imply 12–20 boxes plus complete manual interval review, not
5FPS per-frame annotation. Reviewed positives/negatives cover the timeline or
report unknown gaps. Unknown gaps never become implicit negatives.

Ordinary intervals are start<=t<end. Only a terminal NegativeInterval whose end
equals the exact last actual frame permits start<=t<=end; boundary tests required.
Public reporting permits anonymous candidate/count/gate aggregates, not private
paths, hashes, screenshots, per-play times, boxes or actual annotation JSON.
Correct insufficient output may complete 2A1 without satisfying 2B readiness.

### Module 2A2 — Independent Evidence & Experiment Lock

Status: Completed — formally user accepted on 2026-10-04 at
`69162023b87b71209f8dec9ebc9af69d4bfda944` after the completion-boundary repair.
Infrastructure implemented; full synthetic/regression tests passed. Four new
recordings received. User explicitly reconfirms complete natural whole-match
coverage and replaces the result-screen requirement with user_confirmed completion
and the last actual decoded frame as evaluable end. Result-screen absence is not
incompleteness or a Freeze veto; damaged/undecodable/obviously truncated/key-battle-
missing/human-incomplete material still rejects. Old checks and exclusions remain
historical, all footage/evidence retained, not automatic negatives. Source
one was completed in the unchanged intake order, using its existing rough review; no card/
difficulty/quality filtering. Fresh first-source evidence reached DEV_LOCKED:
user-confirmed ordinary Minions, two independent verified plays and six original
key boxes; four candidate bundles retain other forms/doubts as unknown. Readiness,
freeze and lock validation all exit 0 with stable recomputed digest. Three explicit
unknown intervals and zero negatives remain; complete-file boundary is actual
first-to-last PTS, not game-clock/result UI. User-confirmed segments must cover
exactly 0..last_frame_seconds. The user authorizes only acceptance records,
ff-only main integration and push, retaining the feature branch. At that 2A2
acceptance boundary no Module 2B, Model Lock or Test GT operation was authorized;
the later scoped 2B-1 authorization is recorded below, not inherited from 2A2.
No model success is claimed by 2A2.

Owns a separate development readiness/freeze layer, declared underlying-match
identity, manual candidate/form selection, evolution ground truth, canonical
SHA-256, immutable freeze versions, Model Lock contract and later Test GT lock.
It does not change prepare/validate/review or the old experiment_gate=false.

First experiment: one NEW natural complete unedited development replay, manually
reviewed in full. Human target selection requires >=2 clear independent verified
deployments of the same logical card and one known form. No fixed card priority,
model-assisted selection or reuse of the historical Inferno Dragon sample.
No qualifying target means NOT_READY; missing footage means
WAITING_FOR_DEVELOPMENT_MATCH. No invented data or lowered standard.

Freeze development before Module 2B. After separate 2B approval, freeze the model
before test pixels/precise labels enter the development session. The first
qualifying independent natural test replay needs >=1 locked-form deployment;
do not skip difficult matches. A separate session labels all target deployments,
retains non-evaluable/other-form/unknown cases and locks GT before any inference.
Same underlying match cannot cross splits, regardless of recording/file hashes.
Unknown intervals and other/unknown forms are not negatives; no evolution estimate.

Real execution of this module has stopped at formally accepted DEV_LOCKED.
Building future contracts does not authorize actual model/test execution or 2B.
See [implementation plan](superpowers/plans/2026-10-04-module-2a2-experiment-lock.md)
and [blind-test protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md).

## Module 2B — Offline Visual Detection Proof of Concept

Status: In Progress — 2B-1 is formally completed and accepted as an insufficient
fixed lightweight template baseline, not successful single-card recognition.
The later Module 2B-2 specialist data slice is paused. Module 2B-2B Phase A Tasks
1–6 followed PHASE_A_AUTHORIZED_WITH_SIMPLIFICATION. The subsequent separate
Phase B authorization now qualifies isolated Nano/Tiny CUDA operations using
synthetic data only. Environment qualification passes; its stage did not authorize
real training. The new Phase C authority is recorded above; independent blind
testing and later modules remain Gated. Accepted 2A2
Development Data remains DEV_LOCKED.

Completed separately authorized data request (2026-10-06): prepare and verify a private
local **2-Class Training Dataset Lock v1** from the existing Smoke GT Lock v1
and its 11 confirmed Witch/Skeleton boxes, match 01 / TRAIN and match 04 / DEV_VAL.
Status: **TWO_CLASS_TRAINING_DATASET_LOCKED**; actual exclusive v1 creation and
dedicated readiness/readback exit 0. Internal private local PoC qualification
passes. Fresh joint private lock tests: 65 passed; full maintained regression:
908 passed / 3 existing Windows permission skips, exit 0. Data-lock preparation
and verification are completed; that stage stopped before Phase C. GT/data-lock
identities may now be published by explicit user request; source-media hashes
remain private. New Phase C authority is recorded above.
The ordinary-Minions four/eight target-recheck outputs are superseded / historical,
not the active route or a prerequisite. That completed data scope did not
authorize training/weights; the new smoke scope does. Model Lock, blind testing
and later modules remain unapproved.

### Module 2B-1 — Minions Visual Baseline

Status: Completed — on 2026-10-05 the user reports ChatGPT independent acceptance
at `585c3d95c832a1a86fce28ca822bc69d3646430f`, with
`MODULE_2B1_INSUFFICIENT_ACCEPTED`. Raw experiment status remains
2B1_BASELINE_INSUFFICIENT. Both folds fail; no PASS-only final detector or Model
Lock created. A-to-B retains zero candidates; B-to-A retains one 4.75s late.
Fresh closeout maintained-suite regression: 474 passed/1 skipped; dependencies
and diff/privacy/protection checks passed; 10376 protected files are unchanged.
That historical closeout authorized only acceptance documentation, full checks,
ff-only main integration/push and preserving the feature branch. It did not
authorize parameter changes, real inference reruns, new data, independent testing,
2B-2 or later modules. The subsequent data-only 2B-2 approval is recorded below.
Original failure evidence remains private and preserved. Acceptance does not
declare a working recognizer or unlock the still-failed Model Lock gate.

Two-fold same-match held-out deployment search using the frozen six crops;
both hidden deployments must enter Top5 within 2s of onset. No hidden-GT tuning,
unknown-as-negative, test footage, neural training or automatic next module.
PASS permits final six-reference detector/Model Lock; FAIL preserves evidence
and stops without a Model Lock. [Protocol](MODULE_2B1_PROTOCOL.md) fixes settings
and timing/merge semantics before any real experiment.

Historical 2B-1 goal: detect one evidence-selected card as timestamped visual Observations.
No OpponentCardPlayed, card cycle or elixir updates.

Historical single-card entry gates (not the proposed multiclass protocol):

- a new complete natural development match with >=2 clear independent known-form
  target plays and an accepted immutable Development Data Lock;
- manual candidate selection, reviewed negatives and explicit unknown intervals;
- prospective whole-match isolation and blind-test protocol fixed in advance;
- independently reviewed code/model/data provenance, not merely a repository license.

Required later sequence within a separately authorized Module 2B (not additional
preconditions for starting development on already locked development data):

- Model Lock after development, before accessing test pixels or precise GT;
- first qualifying independent complete test match with >=1 locked-form play,
  whole-match GT locked by a separate session before any test inference;
- same underlying match/re-recording/adjacent frames remain in one split;

Verification:

- full held-out inference can use 5FPS with reviewed visibility/negative intervals;
- occurrence coverage TP/FN, recall, earliest delay, whole-match FP/minute and non-match FP;
- box TP/FP/FN and IoU on explicitly boxed key-frame subset only, with actual
  frame/box counts and subset bias disclosed; not a full-frame accuracy claim;
- FP/minute, timing errors, confidence/IoU and non-match/similar-unit confusions;
- prospective go/revise/stop rule in the 2A design; no training-only score claim.

Minimum data permit an experiment only, not generalized reliability or live use.

### Module 2B-2 — Learned Minion Detector, data-preparation slice

Status: Paused by explicit user instruction on 2026-10-05. The earlier approved
[design](superpowers/specs/2026-10-05-module-2b2-data-preparation-design.md) and
[task plan](superpowers/plans/2026-10-05-module-2b2-data-preparation.md) are historical,
not current execution instructions. Tasks 1/2/3 and the Task 4 CLI are
verified and separately reviewed. The new-layer serialized-frame-boundary repair
is also reviewed. Final maintained regression: 680 passed / two known Windows
symlink permission skips; dependency check passed. Original-order intake is valid
but not ready (CLI exit 3). Historical target confirmation is one match/two plays;
new unit-supported training eligibility remains zero matches/zero plays.
The historical explicit user confirmation resolves the second source as mid-match
truncation with no later clip: excluded from Training Dataset use, but the file
and evidence remain preserved and never Negative. Missing result UI alone is
still legal. Source 03/04 existing sampled target review adds zero confirmed
ordinary deployments; it does not certify full-video absence. That request's
confirmation gap was three matches/six plays; native training eligibility was
zero/zero pending exhaustive unit GT. No Training Dataset Lock was made by this
route. Its target-recheck artifacts are retained as superseded / historical.

Retain schema/readiness, actual media bindings, per-unit annotation, grouped LOMO
ownership and exclusive Dataset Lock APIs. Their old four-match/eight-Minions-play
gate remains implemented for historical contracts, but is no longer a product
data objective or prerequisite for the new route. Do not continue specialist
supplementation. No frame/box-count substitution, unknown-as-negative or sparse-
negative-as-time substitution. Preserve old locks, sources and failure.

This slice has stopped without a Training Dataset Lock. No model install, weights,
training, inference, threshold choice, Model Lock,
blind-test data, Module 3, Android/HUD, push or main integration. GTX 1050 Ti 4GB
is future environment information. The subsequent research reopens the former
Faster R-CNN/MobileNetV3-FPN preference; no detector is implemented here.
See [data verification](VERIFICATION_M2B2_DATA.md) for actual outcomes and limits.

### Module 2B-2A — Multi-class Dataset & Taxonomy Audit

Status: Completed — user reports independent ChatGPT design acceptance on
2026-10-05 at `cec8abc35fce2438d149fe4b68b203650cb835e4`, with
MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT. Scale Coverage Gate is documented;
completion applies to the design phase, not implemented readiness or recognition.

Goal: support a versioned multi-visual-class vocabulary and a dynamic per-match
subset, not fixed ordinary Minions. Audit Dataset/KataCR classes, form/owner,
card-to-unit many-to-many, assets/weights and licenses; compare Faster R-CNN
MobileNetV3-FPN with YOLOX Nano/Tiny for small objects, 4GB and mobile export.

Deliverables: [pinned public-source audit](research/2026-10-05-multiclass-dataset-taxonomy-audit.md)
and [accepted amended design](superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md).
Public assets with unclear rights stay reference_only. No formal data download.

Accepted next-PoC design: 3-5 visual classes, at least two moving-unit types,
grouped development support and prospective unseen-natural-match box/owner evaluation.
Development-only bbox statistics over all basically qualified mobile candidates
precede final class selection. Require at least one relative-small mobile class
and one medium/large mobile class; freeze the rule before choosing classes.
SIZE_COVERAGE_INSUFFICIENT means add original-order Development material,
not lower standards. Nano-first qualification is still an unmeasured candidate
order, not a model decision. Sampled boxes cannot certify FP/min time.

Verification: pinned source/category counts, primary-source citations, document
consistency, diff/scope/privacy and read-only data protection. Model runtime,
training, performance and mobile evaluation are Not Run. Old 2A2 lock, 2B-1
failure, current data and all source/test/dependency files remain unchanged.

The design stage is closed; [fresh closeout checks](VERIFICATION_M2B2A.md)
record the user-supplied acceptance and documentation-only verification.
The user subsequently authorized Phase A Tasks 1–6; this historical design
acceptance does not authorize model execution or publication.

### Module 2B-2B — Multiclass PoC Data & Training Infrastructure

Completed smoke data work: **2-Class Training Dataset Lock v1**
(`two_class_training_dataset_lock`): **TWO_CLASS_TRAINING_DATASET_LOCKED;
data-stage verification completed**, separately authorized for the existing 11-box
**2-Class Smoke GT Lock v1**. Fixed scope: `unit.witch` / `unit.skeleton`,
match 01 / TRAIN and match 04 / DEV_VAL. Record
`source_type=user_recorded_gameplay`, `intended_use=private_local_research_poc`,
`user_training_authorized=true`, `external_upload=false`, `redistribution=false`,
and `rights_clearance=unverified`. The separate `training_qualified` result is
an internal private local PoC gate only, not legal clearance, Supercell permission,
commercial-use approval or redistribution rights. Exclusive v1 creation and
dedicated readiness/readback exit 0; new internal `training_qualified=true`
does not change the old GT-only v1's false. The actual freeze receipt confirms
1,462 protected files unchanged and no legacy source/test/dependency changes.
Fresh joint private tests pass **65** (40 new training-adapter + 25 original GT)
with no skips; full maintained regression passes **908 / 3 existing Windows
permission skips**, exit 0, 1052.47s, with zero failures/errors. Private hashes
are retained in local receipts. Full production training pipeline is not qualified.
Freeze all 11 boxes/four frames; default complete selected-class supervision
uses only three frames/10 boxes. The 72s Witch positive is
`positive_only_requires_unknown_safe_consumer`, with standard full-frame
loss/metrics prohibited by default and Unknown regions never treated as background.
No real training or weights download occurred in that data stage. The current
Phase C scope is above; it still forbids Model Lock and later modules.
The old GT lock and old 2A2/2B-1/3–5-class schemas and readiness remain unchanged;
the four/eight specialist route is superseded, not a prerequisite.

Preserved completed smoke checkpoint: **2-Class Smoke GT Lock v1 created** after
user-relayed ChatGPT final review of Witch/Skeleton, match 01 / TRAIN and
match 04 / DEV_VAL. Eleven positive boxes, one rejected ambiguous proposal,
four appearance groups; two independent Witch groups and zero Skeleton card
deployments. Unknown forms and the fourth frame's partial/Unknown coverage are
preserved. This private GT-only snapshot is not native training readiness:
`training_qualified=false` in that GT-only snapshot, no Training Dataset Lock or
real training at that stage. The completed Phase B qualified only the synthetic
model environment. Current private local training-use authorization is separate,
with its own checked snapshot. The original 3–5-class implementation/locks below
remain unchanged; that general-purpose insufficiency is not rewritten as a pass.

Historical 3–5-class status: Phase A infrastructure verified; consolidated data gaps.
Tasks 1–5 are locally verified/reviewed/committed. Final maintained regression:
908 passed / 3 Windows permission skips, exit 0. Task 6 read-only
checks of the original-order pending handoff return native exit 3: zero qualified
classes, PROVENANCE_INSUFFICIENT and SIZE_COVERAGE_INSUFFICIENT, with separate
whole-match/owner/GT gaps. No real Multiclass Dataset Lock is claimed. That Phase A
stage stopped at the consolidated insufficient-data boundary. Retain its unified
gap report; the later completed Phase B and current two-class smoke authorization
do not retroactively qualify the original 3–5-class dataset.
See [task-by-task plan](superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md).

Phase A: additive closed schema, independent readiness/Scale Coverage Gate,
checked manual per-unit data preparation and whole-match splits; freeze the
candidate/scale snapshot before selecting 3-5 classes, then create an exclusive
versioned Multiclass Dataset Lock only when all support/rights gates pass.
No old-lock conversion or ordinary-Minions four/eight requirement. Missing data
reports class/owner/group/scale gaps and stops; unknown is not negative.

Phase B: **MODEL_ENVIRONMENT_QUALIFIED**, separately authorized 2026-10-06 in
an isolated environment. Nano precedes Tiny. PyTorch 2.7.1+cu118 / TorchVision
0.22.1+cu118 / runtime CUDA 11.8 and pinned official YOLOX 0.3.0 source pass
actual GTX 1050 Ti CUDA forward/loss/backward/nonzero optimizer/checkpoint/
inference/NMS probes. Nano 416 FP32 batch 1 passes three steps; Tiny batch 1 and
optional Nano batch 2 also pass minimal steps. Only anonymous synthetic data,
no pretrained weights or real GT. The latest user authorization supersedes old
Task 7's no-optimizer/checkpoint and Nano-only limits; no other gate is relaxed.
Full Trainer, real data pipeline, long training and export/mobile suitability
remain untested. Original offline environment and all locks/results stay unchanged.

Each task receives corresponding tests/protection and independent code review;
the user authorized continuous Tasks 3–6 without per-task human pauses, with a
consolidated final full regression and gap/completion report. Stop at the phase
gate or consolidated real data gaps. Real training,
pretrained weights, threshold tuning, Model Lock, Test GT work, blind inference, Module 3,
Android/live use and push/main integration all remain separately Gated.

## Module 3 — Deployment Event Tracking

Status: Planned

Goal: promote repeated visual observations into one confirmed
`OpponentCardPlayed` event per real deployment.

Acceptance criteria:

- require configurable multi-frame confirmation;
- apply temporal and spatial deduplication;
- distinguish opponent-side evidence where the footage permits it;
- avoid recounting one moving unit as multiple deployments.

Verification:

- unit tests for confirmation and deduplication boundaries;
- annotated-video regression cases for repeated visibility and nearby deployments.

## Module 4 — Limited Card Set

Status: Planned

Goal: expand only to approximately 20 high-value cards after the initial event
pipeline is reliable.

Acceptance criteria:

- each added class meets an agreed validation threshold;
- class expansion does not materially regress existing classes;
- unsupported cards remain explicitly unknown rather than guessed.

Verification:

- per-class evaluation and confusion analysis on held-out footage.

## Module 5 — Card History and Cycle

Status: Planned

Goal: derive known opponent cards, recent confirmed plays, and cycle state from
`OpponentCardPlayed` events.

Acceptance criteria:

- deterministic updates from an event stream;
- duplicate or corrected events have defined behavior;
- unknown or missed plays preserve uncertainty.

Verification:

- unit tests using fixed event sequences and boundary cases.

## Module 6 — Elixir Estimation

Status: Planned

Goal: estimate a defensible opponent-elixir range using match timing and confirmed
card costs.

Acceptance criteria:

- model normal and accelerated elixir phases explicitly;
- widen or mark uncertainty when detection evidence is incomplete;
- display ranges such as `3–5`, not false precision such as `4.27`;
- keep calculations deterministic and independent of the vision runtime.

Verification:

- unit tests for timing, caps, card costs, phase changes, and missed-event cases;
- comparison with manually annotated recordings.

## Module 7 — Android Real-Time Capture

Status: Gated

Goal: evaluate passive on-device capture only after offline recognition is proven.

Entry gates:

- Modules 1 through 6 are accepted with measured reliability;
- explicit Supercell permission covers the tool behavior, version, and usage
  context before live online-match analysis or HUD can be enabled;
- passive capture, local execution, alternate accounts, training-ground tests,
  and user risk acceptance cannot substitute for permission;
- any permission is reassessed for scope; zero ban risk must never be promised;
- the implementation remains passive and does not control the game.

Potential acceptance criteria, to be finalized only after the gates pass:

- explicit MediaProjection consent and compliant foreground-service behavior;
- on-device processing without gameplay input or network interception;
- measured thermal, battery, latency, and dropped-frame behavior.

## Module 8 — Minimal HUD

Status: Gated

Goal: provide a minimal, non-interactive presentation only if Module 7 and a
separate policy review are accepted.

Entry gates:

- Module 7 is accepted;
- explicit Supercell permission covers the specific live HUD behavior, version,
  and usage context; project approval alone cannot substitute for it.

Potential acceptance criteria, to be finalized only after the gates pass:

- touch-through behavior;
- no overlap with critical battlefield or system controls;
- minimal information, safe-area handling, and automatic dismissal;
- no interaction required during play.
