# Decisions

## 2026-10-07 — Module 3A visual anchors are pending event-review windows

### Decision

Separately authorize offline Deployment Event GT preparation, stopping at the
Human Review Bundle. Use existing accepted visual evidence as manual location
references, not automatic card-play truth. This supersedes the prior checkpoint's
blanket "Module3 not authorized" only for3A preparation;3B remains unauthorized.

### Context and Reason

Milestone2 has83 confirmed boxes/9 visual classes but0 confirmed card-play events.
Persistent/reappearing entities and grouped/spawned units make box counts and
first-observation times insufficient to establish unique opponent deployments.
An explicit context review must precede any event lock or automatic event engine.

### Consequences

Keep candidate hints pending/uncertain/non-evaluable. Provide video context,
exact source-PTS images, old visual references and manual corrections/merges.
Duplicate-review windows do not increase deployment count. If spawn is outside
the supplied window, preserve uncertainty and request wider context, not a guess.
Own objects, unknown owner, null source-card mapping and spawned Skeleton cannot
become opponent plays. Unknown/reject/omissions are not Negative. New exclusive
review outputs do not overwrite existing locks/results; no Event GT Lock before
human return and explicit user attestation. ChatGPT suggestions are not human
reviewer identity. Model/runtime, App and live online-game safety gates unchanged.

## 2026-10-07 — User-attested multiclass visual GT, annotation-only freeze

### Decision

Import the user's explicit confirmation of ChatGPT visual-review suggestions as
reviewer=user, with actual_human_confirmation and human_review_attested true.
Record review_basis=chatgpt_visual_review and
confirmation_source=user_attestation_based_on_chatgpt_visual_review in separate
SHA-bound attestation metadata; do not rename ChatGPT a human reviewer or extend
the strict legacy return schema merely to carry those extra facts.

### Context and Reason

The first fixed24-frame batch receives exact user decisions:44 accepted boxes,
2 rejected proposals,480 left pending,6 visual classes,5 non-null canonical
mappings. User-confirmed visual class/bbox does not confirm a source card, card
play, cross-frame entity, provenance clearance or training qualification.

### Consequences

Create a new exclusive annotation-only GT snapshot/lock without altering source
predictions, packets or old locks. Cannon stays canonical_mapping=null; accepted
form/origin stay unknown. Preserve only user-supported continuity; unsupported
identity tokens name observations only and cannot be counted as independent
entities, appearances or deployments. Missing boxes, uncertain/rejected areas
and unlisted classes stay unresolved, never Negative. This batch has0 negatives
and0 card plays. No primary/spawned role is inferred merely from a mapping.
training_qualified and ordinary_training_export_allowed remain false. Freezing
file consistency is not legal clearance or authenticity certification. No
training, Module3, game HUD, push/main merge or new milestone is authorized.

## 2026-10-07 — Proposal-only KataCR and mock-only Capacitor prototype

### Decision

Use retained KataCR predictions only to accelerate local human annotation.
Keep raw predictions immutable and human corrections separate, explicitly
pending until an actual reviewer acts. Support accept/reject/relabel/bbox edit
and missing objects, with class-specific exhaustive coverage and preserved
appearance identity. Unknown/rejected/unmarked areas never automatically become
Negative. Expand recordings in original order; match02 remains truncated and
training-ineligible. 10–20 classes is an aspiration, not a mandatory quota.

Build a React/TypeScript/Vite/Capacitor mock App in parallel. A decoupled typed
event consumer accepts mock Witch/Balloon events; a small App-internal HUD shows
discovered 2/8. No persistent user data exists in this prototype, so in-memory
state is sufficient; do not add SQLite or localStorage without a real need.

### Context

Attempt02 is valid but data limited, not a usable detector. The fixed KataCR
benchmark produces many noisy proposals and does not justify final App adoption.
Existing predictions can reduce manual drawing effort without treating teacher
output as ground truth, while mock events make the product boundary visible.

### Alternatives and Reason

Do not run Attempt03, adopt KataCR as the production detector, or wait for full
recognition before prototyping UI. The additive tools and mock-only UI test the
desired interaction without changing old experiment results or game behavior.

### Consequences

At that original tool-only checkpoint no training or new lock was authorized;
the later bounded annotation-only user-confirmed freeze is recorded above.
Third-party code/weights/game rights are
not cleared by this research use. Do not redistribute private assets or weights.
Capacitor is the prototype UI choice, not a constraint on future native inference.
No MediaProjection, detector bridge, SYSTEM_ALERT_WINDOW, Accessibility/input
control, cycle/evolution/elixir logic, push or main merge. Live game HUD still
requires the original explicit applicable Supercell permission gate.

## 2026-10-07 — Accept data-limited Attempt02; pause fine-tuning for existing-detector benchmark

### Decision

The user relays `ATTEMPT02_VALID_BUT_DATA_LIMITED` and pauses self-trained
fine-tuning. Preserve both fixed experiments and their data, locks, metadata and
results; no Attempt03, confidence/step changes or additional Skeleton labeling.
Separately authorize the Existing Multiclass Detector Local Benchmark, with
explicit upstream-source/provenance and an independent runtime qualification.
The one fixed confidence0.1 dual CUDA run is now executed on240 PTS frames from
the original first retained match01 (12..72s exclusive,4FPS), not blind. Preserve
all outputs and stop for ChatGPT manual visual review; no tuning/repeat or
automatic model adoption. Proposal labels are not verified card/classes.

### Context and Reason

ChatGPT's ZIP extraction environment failed. The acceptance uses statistics,
not a completed independent per-image or source-code review. The fixed run is
valid but does not establish a usable two-class detector. ROI, data, input size
and budget changed simultaneously; no single factor's causal effect is proven.
Checking an existing multiclass detector is a new bounded local benchmark, not
a result-guided retry of the completed fine-tuning experiment.

### Consequences

Weight provenance/rights remain unverified where not independently established;
local research permission is not legal clearance, redistribution or release
permission. Do not upload private source media or turn benchmark output into
confirmed events. Primary/secondary describe future visual semantic duties:
Witch observations require separate deployment/event confirmation before
`OpponentCardPlayed`; spawned Skeleton does not imply a Skeleton card play.
Root MIT does not override modified Ultralytics AGPL obligations or rights in
weights/game assets. The detector1 public v0.7.13 filename/internal v0.7.12 name
mismatch and CUBIC-wrapper versus actual LINEAR-upstream preprocessing are
disclosed limitations, not grounds for silent modification/rerunning outputs.
Do not claim a byte-identical upstream reproduction or independently confirmed
accuracy. See [actual benchmark verification](VERIFICATION_EXISTING_MULTICLASS_BENCHMARK.md).
Old locks and specialist validators retain historical meaning. No Module3,
production Model Lock, Android/live capability, push or main integration.

## 2026-10-06 — Accept Attempt01 insufficiency; authorize bounded Attempt02

### Decision

The user's explicit relay of ChatGPT's independent visual review accepts
Attempt01 as valid but insufficient. Preserve its exact predictions/checkpoint
and no threshold-based repair claim. Attempt02 keeps Nano, uses match01-only
TRAIN expansion and a TRAIN-defined fixed battlefield crop, increases input to
640 and fixes 300 optimizer steps before any new training. Match04 is now
DEV_TUNE, not a blind/independent test; old immutable split fields remain history.

### Reason

One very-low-score Witch match and no Skeleton matches do not establish a usable
detector. Data/UI/small-target issues are hypotheses, not proven causal facts.
Adding representative positives and explicitly reviewed negatives may improve
the development experiment, but fresh drafts cannot masquerade as human GT.

### Consequences

New objects, appearance continuity and zero-label frames require exact human
review. Unknown is never background. Keep the continuous Witch identity and
spawned Skeleton relationships; do not count new frames as new deployments.
Freeze expanded confirmed data separately from v1, then one fixed run and one
DEV_TUNE evaluation, even if it fails. Changing ROI/data/input/budget together
does not isolate their individual effects. No model change, extra recording,
automatic Attempt03, Blind Test, Module3, push or merge.

## 2026-10-06 — Preserve the first fixed-budget real smoke result

### Decision

Retain the one 100-step Nano checkpoint and its first DEV_VAL predictions without
tuning, retries or retroactive success. The real training chain and numerical
learning are verified, but 1/5 matched GT at IoU 0.5 with a very low-score Witch
response is not reliable two-class detection. No Model Lock or next module.

### Reason

Two TRAIN images cannot justify accuracy or generalization claims. The fixed low
confidence output includes many false detections in the complete frame. Partial
DEV_VAL unmatched predictions remain unjudged Unknown, never negative evidence.
The review ZIP is created locally only; no automatic upload or redistribution.

### Consequences

Freeze the first result for independent review. Further experiments need new
authorization. The unmodified old locks, 2B-1 FAIL and historical validators
remain valid history; no restored specialist Minions quota.

## 2026-10-06 — Authorize one fixed-budget two-class smoke training run

### Decision

The user's explicit Phase C instruction authorizes official COCO YOLOX-Nano
transfer learning using only the locked Witch/Skeleton TRAIN split, 416 input,
batch 1, FP32, fixed seed and exactly 100 optimizer steps. Commit a clean local
historical-data/environment baseline first; no push or main integration.
The experiment may fail visually without being invalid; do not tune or retry
based on DEV_VAL. Record separate current run authority instead of altering
immutable locks' older authorization flags.

### Reason

Exercise the first real GT-to-detector chain while preserving match isolation,
the original 11 accepted boxes and the actual limits of two training frames.
Owner/form/origin remain metadata; spawned Skeleton is not a card-play event.
Local training-use qualification is not legal clearance.

### Consequences

Public docs may now record the exact GT/data-lock SHA-256 identities. Media,
annotations, weights, checkpoints, predictions and exports stay private and
ignored. Use only the official Nano release asset with recorded code license,
COCO provenance and unverified dataset/asset rights caveat. Train only complete
TRAIN frames; the partial DEV_VAL frame yields positive matches and Unknown
unmatched detections, not full-frame negatives/FP. One post-training evaluation,
fixed confidence/NMS/IoU settings before training, and no quality PASS threshold.
No Tiny, extra data, Blind Test, production Model Lock or later module.


This document records durable product and architecture decisions. New entries
must describe accepted reality rather than speculative preferences.

## 2026-09-26 — Start With Offline Recorded Video

### Decision

The first executable stages will analyze user-provided recordings and test
footage. Live online-match capture and overlays are not authorized current scope.

### Context

The intended product may eventually analyze an Android screen, but the user has
made account safety a highest-priority constraint. The technical feasibility of
reliable deployment recognition is also unproven.

### Alternatives

- Begin directly with live Android MediaProjection capture.
- Build a complete Android interface before validating recognition.
- Validate the difficult recognition path using recorded input.

### Reason

Recorded input isolates the main technical risk without introducing live-match
policy exposure, overlay complexity, or device-capture variability.

### Consequences

- Modules 1 through 6 operate offline.
- Module 7 requires explicit Supercell permission covering specific live tool
  behavior, version, and usage context, plus project approval.
- Module 8 cannot begin before Module 7 is approved and verified.

## 2026-09-26 — Prohibit Game Interaction and Automation

### Decision

The project will not modify or control Clash Royale. APK modification, hooking,
injection, memory access, traffic interception, protocol emulation,
AccessibilityService control, synthetic input, bots, and automatic card placement
are permanently outside the project boundary.

### Context

These capabilities are unnecessary for visual match analysis and conflict with
the project's safety requirements.

### Alternatives

- Reuse automation capabilities from reference projects.
- Restrict the system to passive visual input and analysis.

### Reason

Passive analysis is the smallest architecture that addresses the intended
problem while reducing technical, privacy, and account risk.

### Consequences

- Reference-project automation code must not be imported.
- Android permissions and services must remain limited to approved passive needs.

## 2026-09-26 — Separate Detection From Confirmed Game Events

### Decision

The visual detector will emit observations. A separate deployment tracker will
use temporal and spatial evidence to emit confirmed `OpponentCardPlayed` events.
Only confirmed events may update history, cycle, or elixir state.

### Context

One deployed unit remains visible across many frames. Treating every detection
as a card play would repeatedly count the same deployment.

### Alternatives

- Let the model update game-state trackers directly.
- Confirm and deduplicate observations in a dedicated domain component.

### Reason

The dedicated event boundary makes false positives, repeated detections, and
uncertainty testable without coupling them to game-state calculations.

### Consequences

- Module 2 proves limited detection only.
- Module 3 owns confirmation and deduplication.
- Cycle and elixir work cannot consume raw detections.

## 2026-09-26 — Defer the Model Runtime Choice

### Decision

YOLO, ONNX Runtime, TensorFlow Lite, and other candidates remain unselected until
offline experiments provide accuracy, performance, model-size, and Android
deployment evidence.

### Context

No representative recording, trained model, benchmark, or Android performance
measurement currently exists.

### Alternatives

- Select a framework during project bootstrap.
- Allow the proof of concept to establish requirements first.

### Reason

Early lock-in would add dependencies without reducing the current uncertainty.

### Consequences

- Module 1 adds no machine-learning runtime.
- A later decision must record measured tradeoffs before standardizing a runtime.

## 2026-09-26 — Use Local-First Core Processing

### Decision

Core video analysis and future supported device analysis will run locally. A
server, account, or cloud database is not a default dependency.

### Context

The initial product serves one user, processes local media, and has no confirmed
collaboration or multi-device requirement.

### Alternatives

- Upload video to a hosted inference service.
- Keep the core pipeline local and add online capabilities only when necessary.

### Reason

Local processing reduces privacy exposure, latency, operating cost, and failure
dependencies while satisfying the current use case.

### Consequences

- Offline operation is an acceptance condition for core modules.
- Any future online capability must be optional and justified independently.

## 2026-09-26 — Treat External Code and Data as Provenance-Gated

### Decision

No external source, model, dataset, recording, or game asset enters the project
until its origin, license, and intended use have been reviewed. Source from an
unlicensed repository must not be copied.

### Context

The reference repositories differ in licensing, and code licenses do not
automatically grant redistribution rights for game assets or datasets.

### Alternatives

- Copy useful implementations first and resolve licensing later.
- Reimplement concepts cleanly and import only verified compatible material.

### Reason

Up-front provenance prevents the proof of concept from accumulating legal and
maintenance debt that would block later distribution.

### Consequences

- CR Vision is an algorithmic reference only while it lacks a declared license.
- Every external artifact requires an evidence-backed review before inclusion.

## 2026-10-03 — Require Specific Official Permission for Live Features

### Decision

Live online-match analysis and HUD remain Gated and disabled unless explicit
Supercell permission covers the exact behavior, version, and usage context.
Passive capture, local execution, alternate accounts, training-ground tests,
and user risk acceptance cannot substitute for permission. Even with permission,
reassess scope and never promise zero ban risk.

### Context

The Module 0 review found that risk acceptance could bypass the intended
account-safety constraint. This entry supersedes that weaker gate. No official
permission has been obtained or asserted.

### Alternatives

- Allow a user to accept remaining risk.
- Require explicit, applicable official permission for live features.

### Reason

The user's requirement places account safety above live functionality.

### Consequences

Offline-file modules may continue. This module never accesses a running game.
Live functionality remains closed; project approval is still necessary but
cannot replace official permission.

## 2026-10-03 — Python/PyAV Offline Experiment and Presentation-Time Contract

### Decision

Use a small Python 3.12 CLI with PyAV, Pillow, and pytest for Module 1. Select
frames by actual PTS/time_base normalized to the first display frame. Use exact
fraction arithmetic and choose the first frame at or after a target within an
inclusive 100ms window. Scan sequentially with bounded frame memory.

### Context

The user specifically authorized this Windows experiment. Variable frame rates
and nonzero starting PTS make frame-index/average-FPS calculation unreliable.

### Alternatives

- Estimate frame times from frame indices and average FPS.
- Use actual decoded display timestamps.
- Build an Android application before verifying recorded-video behavior.

### Reason

The selected approach makes temporal correctness reproducible using synthetic
media while remaining independent of Android, game control, and model choices.

### Consequences

Python is an explicitly authorized experiment, not a replacement for a future
app stack. Core app business logic/storage are not implemented here. No database
or inference framework is added. Keep original videos untouched and generated
media ignored. Missing timestamps fail explicitly; partial misses return nonzero.
Runtime versions are pinned in the tool configuration and test requirements.
Representative user-recording acceptance remains required after synthetic tests.

## 2026-10-03 — Evidence Preparation Before Single-Card Detection

Status: retained for stage/event separation and historical 2A1 behavior.
Its first-experiment data thresholds are superseded by the 2026-10-04 Module 2A2
decision below; do not reuse the old 4/6/2 experiment gate for new 2A2 work.

### Decision

The user explicitly split Module 2 into 2A (manual evidence/annotations/sufficiency)
and 2B (one-card visual Observations). Only Module 3 emits OpponentCardPlayed.
Target selection requires four distinct reviewed opponent deployments in current
footage; Hog Rider is not predefined. Before 2B require two independent complete
matches, six total verified plays, a whole held-out match with two plays, reviewed
non-match negatives and a locked split. Same underlying match/re-recording frames
cannot cross development and test. These minima do not certify reliability.

### Context

Module 1 has been accepted. A single real recording proves extraction, not model
generalization. Random frame splits would leak nearly identical match evidence.
The current task authorizes planning only, plus the accepted branch's main merge.

### Alternatives

- Train immediately on frames randomly split from one recording.
- Establish evidence and independent whole-match boundaries before an experiment.

### Reason

Manual evidence and pre-registered isolation make the next experiment verifiable
without adding a model, GUI or live-game risk prematurely.

### Consequences

Module 2A implementation remains subject to separate user approval. Proposed
target/tool/evaluation details in the design are recommendations, not decisions
accepted by this entry. Real footage, hashes and labels remain local and ignored.
External datasets/models remain separately provenance-gated; no download approved.

## 2026-10-03 — Lightweight Key Evidence Before Independent Split Infrastructure

Historical scope: its 2A1 constraints remain valid. Its deferral of 2A2 until
a second recording is superseded by the separately approved 2026-10-04 design.

### Decision

The user's review directs 2A1 to prepare current-recording evidence only, with
prepare/validate/review commands, full manual deployment/visibility/negative
interval review and 3–5 distinct original key-frame boxes per verified play.
No dense 5FPS manual annotation inventory. Independence allocation, Evaluation
Protocol, canonical digest, split lock and freeze are deferred to 2A2 after at
least a second independent complete recording and separate design/approval.

### Context

The prior draft required every 5FPS held-out/non-match frame to be reviewed and
planned freeze infrastructure despite having only one observed match. Neither
implementation nor final annotations exist; this task authorizes document revision.

### Alternatives

- Build the original dense-label/freeze system immediately.
- Complete a lightweight current-recording stage, then approve independent-data
  preparation when a second match exists.

### Reason

The smaller stage matches an individual PoC's workload without lowering the
independent full-match isolation, data/provenance or live-safety gates.

### Consequences

2A1 is not implemented; 2A2 is unapproved. Inferno Dragon stays a pending-review
candidate, and one match remains insufficient for 2B. Future box metrics cover
only the disclosed key-frame subset; temporal coverage/FP metrics use complete
reviewed intervals, not implicitly negative unlabeled frames.
Ordinary intervals stay half-open, with a closed end only for terminal negatives
ending at the exact last actual frame. Public documents allow anonymous candidate/
count/gate aggregates; actual timestamps, paths, hashes, boxes, media and labels
stay local. Prior commits are not rewritten. Proposed model/protocol details are
not made accepted technical decisions by this entry.

## 2026-10-04 — Independent Experiment Locks and Prospective Blind Testing

### Decision

The user approved Module 2A2 implementation: a new natural development replay,
human target selection, at least two clear independent deployments of one known
card/form, immutable versioned Development Data Lock, later Model Lock, and a
separate-session Test Ground Truth Lock before any test inference. The first
qualifying independent natural test match needs at least one locked-form play.
The old Inferno Dragon recording is historical regression evidence only.

### Context

The accepted 2A1 tools establish evidence consistency, not model readiness.
Freezing the model before test exposure prevents test-driven target/parameter
selection. The user explicitly approved building infrastructure before supplying
new development footage. Real Module 2A2 execution stops at DEV_LOCKED; absent
that footage it stops WAITING_FOR_DEVELOPMENT_MATCH, without fabricated locks.

### Alternatives

- Require all development and test labels before developing a model.
- Prospectively freeze development, then model, then independent blind labels.

### Reason

The second flow preserves a small one-development/one-test PoC while protecting
independence and avoiding parameter tuning on test pixels or ground truth.

### Consequences

- Supersedes the old first-experiment 4/6/2 thresholds and pre-2B test-label
  requirement only; existing 2A1 four-play candidate/review behavior stays intact.
- Add a separate Python experiment layer; no database or new dependency.
- normal/evolved/unknown are separate. Other/unknown forms and timeline gaps
  are not negatives. Evolution is manual ground truth, not an automatic counter.
- Split identity is the underlying match, not the recording file or its hash.
- Digests and exclusive creation detect inconsistencies, not dishonest human
  attestations, coherent forgery or source-video authenticity.
- Module 2B still requires separate acceptance, planning and explicit approval.
  No training, inference, Android or live feature is authorized by this decision.

## 2026-10-04 — User-Confirmed Completeness and Actual File-End Boundary

### Decision

The user explicitly replaces the result-screen requirement: a complete replay is
one the user confirms covers the full natural match. Its last actual decoded
frame is the valid evaluable end. Record completion_attestation=user_confirmed
and terminal_result_screen_present separately; false screen presence is not
incompleteness or a Development Data Freeze veto.

### Context

The user reconfirms all four supplied recordings and authorizes continuing in
their original intake order, starting with the first usable input and reusing its
existing human rough review. This supersedes the visible-result-based exclusions
in the earlier boundary-check documents, not their factual image observations.
Historical exclusions, files and reviews are retained rather than rewritten.

### Alternatives

- Require a visible victory/defeat/result screen before any development evidence.
- Use explicit human whole-match coverage plus technical integrity and actual PTS.

### Reason

Missing ending UI does not establish missing battle content. Human confirmation
is an auditable declaration, not software-certified source authenticity.

### Consequences

- Still reject damaged or undecodable files, obvious mid-match truncation, missing
  key battle intervals or explicit human incompleteness. Do not hide such conflicts
  behind an attestation; absence of result UI alone is not one.
- Preserve strict report/index/PNG/PTS checks, whole-file human review, one shared
  complete segment and >=2 independent clear verified deployments of one known form.
- Ordinary intervals remain half-open; retain explicit terminal uncertainty when
  needed. The file end or missing result screen is never an automatic negative.
- Retain the existing v1 evidence/extractor and prior immutable records. Additive
  development identity metadata can be bound by the existing digest without a
  new database, dependency or lock format.
- No result-screen-driven re-recording is required for these four inputs. Do not
  filter or reorder them by card/difficulty/quality. Stop at a truthful Development
  Data Lock or unresolved evidence blocker; Module 2B remains separately gated.

## 2026-10-05 — Development-only Reference Template Baseline

### Decision

The user separately authorizes Module 2B-1: fixed multiscale OpenCV template
matching on the existing two ordinary Minions deployments. ORB is diagnostic,
never a ranking/gate weight. Both held-out deployment folds must meet the fixed
Top5/2s temporal search criterion before a real detector artifact/Model Lock may
be created. Failure is a valid result and stops, not automatic training or tuning.

### Context

Two independent plays and six group-box frames are too little evidence to claim
generalization. A simple reference baseline tests feasibility before a separately
planned neural route. The full approved protocol and a priori settings are in
[MODULE_2B1_PROTOCOL.md](MODULE_2B1_PROTOCOL.md).

### Alternatives

- Train a detector immediately on the six images.
- Search for each deployment using only the other deployment's references.

### Reason

The second approach is transparent, preserves frozen evidence, exposes self-match
failure and leaves independent-match testing untouched.

### Consequences

- Scanner/ranker do not receive hidden GT. Freeze both rankings before evaluation.
- First support and highest peak are different fields. Continuous support uses
  transitive event grouping; >2s gaps can still split one play, a disclosed limit.
- Unknown intervals/forms never tune thresholds or establish false-positive rates.
- A temporal match is a development proxy, not verified card identity/ownership,
  OpponentCardPlayed, cross-match reliability or permission for live use.
- Add only optional pinned headless OpenCV plus its NumPy dependency; no neural
  weights/framework, database, cloud runtime or Android dependency.
- An additive closed Model Lock artifact variant preserves legacy v1 contracts.
  Detector JSON hashes are actual canonical file hashes, not imaginary model files.
- Freeze code/settings before the first real scan. Preserve all original evidence.
  No independent test, 2B-2, Module 3, push or main integration is implied.

## 2026-10-05 — Pause Fixed-Minions Expansion; Audit Multiclass Taxonomy

### Decision

The user explicitly pauses ordinary-Minions four-match/eight-deployment training
data expansion. The product must recognize multiple visual types dynamically
present in natural matches; Minions remains historical evidence and one later
class, not a fixed standard. Retain existing dataset contracts, annotation/lock
infrastructure, private data, 2A2 Development Lock and accepted 2B-1 failure.
Authorize Module 2B-2A research/design only and reopen model selection rather
than inheriting the Faster R-CNN preference as a binding constraint.

### Context

The prior data slice ended with working tools but unreviewed per-unit data and
an unresolved recording completeness conflict. More specialist samples do not
define a general card/unit taxonomy. Public repositories mix units, UI, spells,
evolution variants and generated assets with different provenance obligations.

### Alternatives

- Continue supplementing a fixed ordinary-Minions dataset before any multiclass work.
- Preserve that work and audit multiclass data/schema/model assumptions first.

### Reason

The second approach follows the clarified product objective without deleting
useful infrastructure, mutating old evidence or treating visual units as cards.

### Consequences

- Old four/eight validator behavior is retained as historical code, not the new
  data objective. No threshold patch, old-lock migration or data editing in this stage.
- Research must separate code, data, third-party game assets and weight licenses;
  unclear public material remains reference_only, with no training download.
- Proposed taxonomy, 3-5-class PoC and Nano/Tiny/Faster comparison are DRAFT
  recommendations in the new spec, not accepted implementation/model/gate decisions.
- Unknown and other forms never become ordinary-target negatives; image/box counts
  never replace independent matches/groups or certified absence-time coverage.
- Preserve underlying-match isolation, immutable versions and separate GT/predictions.
  Old exposed recordings are development/reference, not prospective blind tests.
- Stop for ChatGPT independent review. New implementation planning/execution,
  model installation, weights, training, inference, Model Lock, Module 3 and
  Android/live functionality require later authority. No push/main integration.

## 2026-10-05 — Accept Multiclass Design with Development Scale Coverage

### Decision

Record the user's reported independent ChatGPT verdict at
`cec8abc35fce2438d149fe4b68b203650cb835e4`:
MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT. Close the design stage after adding
the Scale Coverage Gate and documentation checks; write, but do not execute,
the Module 2B-2B data/training-infrastructure plan. This supersedes only the
preceding decision's pending-review/planning stop, not its paused specialist route.

### Context

An easy-large-only 3-5-class baseline would not test a material risk for real
gameplay: small moving targets. Class names or subjective impressions cannot
substitute for original-image bbox measurements. Data and environment gates
must remain separate to avoid moving straight from design to training.

### Alternatives

- Preselect named small/large cards or adjust categories after seeing test results.
- Fix a Development-only relative-size policy before final class selection,
  measure the full qualified mobile candidate pool, and retain insufficiency.

### Reason

The second approach keeps dynamic target choice, avoids test leakage and reports
actual scale support without claiming a universal absolute small-object threshold.
The exact fixed policy, grouped weighting and tie fallback are in the
[amended spec](superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md).

### Consequences

- Choose at least one relative-small and one medium/large mobile class among
  the 3-5 targets; both remain subject to independent group and own/opponent
  train/validation support. No preset card priority or specialist Minions gate.
- Report pixel dimensions and normalized-area distributions for all candidates
  and chosen classes. Clear boxes define scale; occluded/pending data stays
  preserved, not negative. Missing scale support yields SIZE_COVERAGE_INSUFFICIENT.
- Freeze the rule, candidate universe/statistics, cutpoints and whole-match split
  before final selection; bind them and selection rationale into the dataset digest.
  A revision needs a new version, never future-test-driven regrouping/overwriting.
- Relative scale is not COCO absolute-small coverage, training success or proof
  of cross-match generalization. Model/environment performance is still unmeasured.
- New multiclass contracts are additive; old locks/tools/FAIL stay unchanged.
  Reference-only assets remain forbidden training inputs.
- Phase A data infrastructure/preparation and Phase B isolated model-environment
  qualification each need separate approval/acceptance. No weights/training,
  Model Lock, Test GT, blind test, later modules, push or main integration now.

## 2026-10-05 — Authorize Phase A with Opponent-first Owner Support

### Decision

The user reports ChatGPT verdict PHASE_A_AUTHORIZED_WITH_SIMPLIFICATION and
authorizes Module 2B-2B Tasks 1–6 only. Every selected visual class requires
confirmed independent opponent support in both TRAIN and DEV_VAL. At least one
selected class additionally requires own support in both splits. Other classes'
unsupported own subgroups are not_qualified / not_evaluated, not a blocker to
opponent detection and not evidence of validated bidirectional owner distinction.

### Context

The initial product prioritizes opponent visual units. Requiring full own support
for every class overconstrains the first dataset; one supported owner-control
class retains a meaningful owner-discrimination check.

### Alternatives

Require both owners for every class; or opponent support for every class with
one fully supported own control. The user explicitly chooses the second.

### Reason

Simplify support without changing unknown handling, exhaustive frame annotation,
whole-match isolation or Scale Coverage Gate. The full basic moving candidate
pool uses opponent support rather than requiring own support for every class.

### Consequences

- Unknown owner is never opponent or Negative. Missing own qualification does
  not excuse omitting own objects from exported complete-frame Ground Truth.
- Keep 3–5 classes, at least two moving types, relative-small and medium/large
  moving representatives, provenance gates and immutable dataset versions.
- Preserve old locks, fixed-Minions tools and accepted 2B-1 failure byte-for-byte.
- No Phase B, model installation, weights, training, blind-test work, Module 3,
  push or main integration. Stop on data insufficiency or Dataset Lock for review.

## 2026-10-06 — Separate Smoke GT Freeze from Training Qualification

### Decision

The user authorizes a separate two-class learned-detector smoke milestone:
`unit.witch` and `unit.skeleton`, match 01 / TRAIN and match 04 / DEV_VAL.
The existing 3–5-class schema, validators and locks remain unchanged. The
normal-Minions specialist route is not resumed. Owner is annotation metadata,
not a detector class; missing own support does not block this smoke scope and
does not establish owner discrimination. Witch visual identity can be confirmed
with form unknown. Spawned Skeletons retain their proposed source relationship,
without becoming Skeleton-card deployment evidence.

### Context

High-level returned human review identifies these two visual candidates across
the two Development matches, but precise boxes, continuity and sources still
need independent confirmation. Provenance facts alone are not a training-use
legal authorization or a passed readiness gate.

### Alternatives

Relax the existing general-purpose training lock; conflate GT freeze with training
qualification; or keep an additive smoke GT boundary separate from training
eligibility. The user explicitly chooses the third.

### Reason

Freeze reproducible human annotation without falsely representing pending
training provenance as qualified. Preserve the general-purpose contract and
historical experiments instead of rewriting their results.

### Consequences

- A future **2-Class Smoke GT Lock** requires confirmed visual class, bbox,
  appearance/deployment semantics and owner/form/origin metadata. Training
  qualification may still be pending; the lock must not imply ready for training.
- A **Training Dataset Lock** requires frozen GT and passed training-use
  provenance/readiness. It is forbidden when `training_qualified=false`.
- This turn prepares private, non-exhaustive `draft / pending_human_review`
  proposals only. No precise ChatGPT confirmation, independent deployment count,
  causal root, negative background or exhaustive frame coverage is fabricated.
- This decision does not implement new production schemas/locks, change old
  2A2 locks or 2B-1 FAIL, or authorize Phase B, installation, weights or training.
- Stop with the minimal Human Review Bundle for final human correction. Do not
  request more recordings merely to satisfy the superseded first-milestone
  3–5-class target; its existing validator remains intact for its original scope.

## 2026-10-06 — Freeze Confirmed Development GT without Training Qualification

### Decision

The user explicitly relays TWO_CLASS_SMOKE_HUMAN_REVIEW_CONFIRMED: objects 01–11
confirmed, 12 rejected, original bboxes accepted unchanged. Four groups are
accepted; each match's Witch group represents one confirmed independent
deployment, while both spawned Skeleton groups remain non-card deployments.
Only the Development **2-Class Smoke GT Lock** is authorized.

### Context

The exact four-frame packet has now been reviewed. Three frames are declared
exhaustive for Witch/Skeleton only; match 04 at 72s retains an ambiguous small
unit and is not exhaustive. Unknown form is allowed. The user permits recording
moderate/low visibility metadata locally without changing confirmation decisions.

### Reason

Freeze the supplied human conclusions and their original media coordinates,
without requiring or falsely granting training provenance. Keep a rejected
visual hypothesis distinct from a negative and retain sampled-frame coverage.

### Consequences

- The private dedicated `two_class_smoke_gt_lock` v1 uses canonical digests,
  strict source binding and exclusive versioned creation. One-off validation
  supports this reviewed snapshot; it does not relax old training/scale schemas,
  impersonate a Model-linked blind Test GT Lock or certify video authenticity.
- Owner/form/origin and confirmed spawned-from relationships are frozen; no
  per-frame deployment multiplication, entity tracking, source-card ID or
  exact spawn timestamp is inferred from these selected frame times.
- Preserve the original ZIP/draft. Append a confirmed return and an explicit
  final presentation; historical candidate fields are marked draft-only.
- Partial 72s GT retains its Witch box, not complete-supervision background.
  Unknown/rejected objects are not Negative; sampled images are not FP/min time.
- `training_qualified=false`; Training Dataset Lock and Phase B remain closed.
  Rights provenance is factual only. Stop after verification and reporting.

## 2026-10-06 — Separately Qualify YOLOX CUDA Environment without Real Training

### Decision

The user's explicit Phase B authorization permits a separate model environment,
compatible dependency installation, then Nano and Tiny synthetic CUDA probes.
It supersedes the earlier Task 7 no-optimizer/checkpoint and Nano-only restrictions
for this environment test. `training_qualified=false` remains unchanged.

### Context

GT is frozen but training provenance/readiness is not qualified. Hardware is GTX
1050 Ti 4GB, capability 6.1, Windows 11 / Python 3.12.4. Driver-reported maximum
CUDA version is not proof that a chosen wheel supports Pascal or executes kernels.

### Alternatives

Pollute the established offline environment or install all optional legacy YOLOX
export/trainer dependencies; instead use an isolated, pinned minimum model-operation
closure and unmodified official source integration, then verify actual operations.

### Reason

Separate environment feasibility from data/weight rights and detection quality.
Match official Torch 2.7.1 and Vision 0.22.1 CUDA 11.8 Windows wheels; their actual
GTX 1050 Ti execution is the acceptance evidence, not a theoretical compatibility
claim. Preserve all old datasets, locks and accepted failures.

### Consequences

- The environment qualifies Nano 416 / FP32 / batch 1, followed by Tiny batch 1
  and optional Nano batch 2. Verify real GPU loss/gradients, nonzero parameter
  updates, strict model/optimizer checkpoint recovery, inference and CUDA NMS;
  CPU assignment fallback cannot qualify the required CUDA chain.
- YOLOX source version 0.3.0 is pinned to official commit
  `6ddff4824372906469a7fae2dc3206c7aa4bbaee` with Apache-2.0 license retained.
  Do not alter dependency metadata to fake `pip check` success. Installed
  distributions and source import closure are audited separately. Full official
  Trainer, real COCO pipeline and ONNX/ncnn/mobile paths remain unqualified.
- Only anonymous in-memory random tensors/toy annotations may exercise this
  chain. Synthetic checkpoints are local probe artifacts, not Model Locks or
  downloaded pretrained weights. Python audit guards are not OS sandbox proof.
- Official future weight identifiers `YOLOX/0.1.1rc0/yolox_nano.pth` and
  `YOLOX/0.1.1rc0/yolox_tiny.pth` are recorded only; no weights are downloaded.
  Code license does not qualify weights or gameplay training provenance.
- Neither Training Dataset Lock nor real training is authorized. Environment
  qualification is not detector success, owner discrimination, training permission,
  full-epoch stability or mobile feasibility. Stop for review; no commit/push/merge.

## 2026-10-06 — Authorize Private Local Smoke Training Qualification Separately

### Decision

The user explicitly authorizes training-use qualification and a separate
**2-Class Training Dataset Lock v1** (`two_class_training_dataset_lock`)
for the existing Smoke GT Lock v1's
11 confirmed boxes only: `unit.witch` / `unit.skeleton`, match 01 / TRAIN and
match 04 / DEV_VAL. Intended use is `private_local_research_poc`. This supersedes
the earlier smoke-stage prohibition on creating a training snapshot within
this exact scope, without changing the immutable GT-only lock or old schemas.

### Context

GT and synthetic model-environment qualification have separate retained evidence.
The ordinary-Minions four-match/eight-play target-recheck is a preserved historical
route, not the current product direction or a prerequisite for this smoke dataset.
User authorization for a private local research PoC is now explicit, while
third-party game-asset rights remain unverified.

### Alternatives

Keep waiting for the historical specialist quota; treat user authorization as
general legal clearance; or record the bounded private local authorization and
verify a separate smoke training snapshot. The user chooses the third scope.

### Reason

Make the authorized local research step reproducible while distinguishing the
project's internal readiness decision from rights clearance, detector quality
and permission to perform the later training stage.

### Consequences

- Record `source_type=user_recorded_gameplay`,
  `intended_use=private_local_research_poc`, `user_training_authorized=true`,
  `external_upload=false`, `redistribution=false`, and
  `rights_clearance=unverified`. `training_qualified` is only the internal
  private local PoC gate; it is not legal clearance, official Supercell permission,
  commercial-use approval or external upload/redistribution rights.
- New qualification must be checked and bound to a separate immutable version;
  never set the old GT-only v1's `training_qualified=false` to true in place.
  Preserve original bboxes, owner/form/origin, spawned-from relations, underlying
  matches/splits, rejection and Unknown coverage. Freeze 11 boxes/four frames,
  with default complete selected-class supervision limited to three frames/10
  boxes. The 72s Witch positive is
  `positive_only_requires_unknown_safe_consumer`; standard full-frame
  loss/metrics are prohibited by default and Unknown regions never become
  background. Sampled images do not certify FP/min time.
- Existing target-recheck files remain superseded / historical without deletion,
  overwrite or retrospective success. No specialist supplementation is requested.
  Old 2A2/2B-1 and 3–5-class schemas, validators, gates and locks stay unchanged;
  their insufficiency is not rewritten as a qualified multiclass dataset.
- This authorization covers data-lock preparation and verification only. It
  does not permit actual training, pretrained-weight download, Phase C, real
  detector inference, threshold tuning, Model/Test GT Lock, later modules,
  Android/live use, staging, commit, push or merge.
- Fresh checked freeze evidence records **TWO_CLASS_TRAINING_DATASET_LOCKED**:
  exclusive v1 creation, dedicated readiness and lock validation/readback exit 0,
  new internal `training_qualified=true`, old GT-only snapshot unchanged and
  1,462 protected files unchanged. Private hashes stay in ignored local receipts.
  Fresh joint private lock tests pass 65 (40 new + 25 original GT); full
  maintained regression passes 908 / 3 existing Windows permission skips,
  exit 0. The data-lock stage stops here. Full production training pipeline
  remains unqualified; Phase C and actual training still require separate authority.
