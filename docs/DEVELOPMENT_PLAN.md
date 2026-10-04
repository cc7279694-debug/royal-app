# Development Plan

The project advances one independently verifiable module at a time. A module may
start only after the previous module has been reviewed and accepted. Statuses are
`Completed`, `In Progress`, `Planned`, or `Gated`.

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

Status: In Progress — 2A1 formally accepted on 2026-10-04 at `98037ceba81683ad1a2c214bada30a10f2f3f69e`.
2A2 was separately approved on 2026-10-04 and is in progress. Its prospective
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

Status: In Progress — implementation separately authorized on 2026-10-04.
Infrastructure implemented; full synthetic/regression tests passed. No new
natural development replay supplied: WAITING_FOR_DEVELOPMENT_MATCH, not DEV_LOCKED.

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

Real execution of this module stops at DEV_LOCKED for independent acceptance.
Building future contracts does not authorize actual model/test execution or 2B.
See [implementation plan](superpowers/plans/2026-10-04-module-2a2-experiment-lock.md)
and [blind-test protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md).

## Module 2B — Single Card Detection Proof of Concept

Status: Gated — accepted Module 2A1, accepted 2A2 DEV_LOCKED and separate
planning/authorization required. No training or inference has started.

Goal: detect exactly one evidence-selected card as timestamped visual Observations.
No OpponentCardPlayed, card cycle or elixir updates.

Entry gates:

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
