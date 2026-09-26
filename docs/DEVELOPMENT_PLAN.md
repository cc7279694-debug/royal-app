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

Status: Planned

Goal: read one user-provided MP4 without performing card recognition.

Acceptance criteria:

- report duration, FPS, width, and height;
- retrieve a frame at a requested timestamp with defined seeking tolerance;
- export selected frames to a disposable, Git-ignored output location;
- return clear errors for missing, unreadable, or unsupported input;
- keep user recordings and exported frames out of version control.

Verification:

- automated tests for metadata and timestamp validation where practical;
- run against a small non-sensitive fixture and a representative user recording;
- verify exported frames visually and confirm Git remains clean of media.

## Module 2 — Single Card Detection Proof of Concept

Status: Planned

Goal: detect a deliberately small set of opponent-card candidates in recorded
footage, beginning with Hog Rider and only adding classes supported by evidence.

Acceptance criteria:

- produce timestamped observations with card identifier and confidence;
- measure false positives and missed detections on labeled validation clips;
- keep observations distinct from confirmed deployment events;
- record model, dataset, and asset provenance.

Verification:

- reproducible evaluation on held-out clips;
- documented accuracy and known failure cases;
- no claim of full card coverage.

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
- current Supercell rules are reviewed for the exact proposed behavior;
- the user explicitly approves proceeding despite any remaining account risk;
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
- live presentation is explicitly approved for the intended test context.

Potential acceptance criteria, to be finalized only after the gates pass:

- touch-through behavior;
- no overlap with critical battlefield or system controls;
- minimal information, safe-area handling, and automatic dismissal;
- no interaction required during play.
