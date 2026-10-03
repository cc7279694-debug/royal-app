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

Status: Planned — design and implementation plan prepared for user review;
implementation has not started.

Goal: manually identify usable match ranges, inventory opponent cards, choose a
defensible first target, prepare local annotations and assess data sufficiency.
No model, automatic boundary detector or custom annotation GUI.

Acceptance criteria:

- exact PTS-normalized local evidence and manually reviewed boundaries;
- at least four distinct manually confirmed deployments in current recording
  before selecting a troop/building target; no predefined Hog Rider;
- versioned annotations, full-image normalized boxes, reviewed negative ranges;
- whole-match/source isolation and a clear sufficient/insufficient report;
- no private media, labels, source paths or hashes in public Git.

Verification:

- synthetic validation, timestamp, coordinates, file safety and split-leakage tests;
- reviewed real recording with honest uncertainty and data limitations;
- no model accuracy claim in this stage.

Planning documents:
[design](superpowers/specs/2026-10-03-module-2a-evidence-preparation-design.md),
[implementation plan](superpowers/plans/2026-10-03-module-2a-evidence-preparation.md).
Current recommendation: Inferno Dragon, at least four reviewed episodes;
one observed match alone is insufficient for Module 2B.

## Module 2B — Single Card Detection Proof of Concept

Status: Gated — accepted Module 2A, independent data and separate approval required.

Goal: detect exactly one evidence-selected card as timestamped visual Observations.
No OpponentCardPlayed, card cycle or elixir updates.

Entry gates:

- at least two independent complete matches and six verified target plays total;
- at least one whole held-out match with two target plays;
- reviewed non-match negatives, valid annotations and a locked pre-training split;
- all same-match/re-recording/adjacent occurrence frames remain in one split;
- independently reviewed code/model/data provenance, not merely a repository license.

Verification:

- complete held-out matches; deployment-window coverage TP/FN and box TP/FP/FN;
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
