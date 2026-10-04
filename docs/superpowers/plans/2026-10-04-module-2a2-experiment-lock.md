# Module 2A2 infrastructure implementation

Authority: the user-approved Module 2A2 Independent Evidence & Experiment Lock
design, supplied on 2026-10-04. This plan implements that design, not a new
model experiment. Baseline: 3ad657f2c9190f4e389ccd035682becd12d0c51c.

## Global constraints

- Work on feat/module-2a2-experiment-lock in the user's existing checkout.
- Existing Module 1 and 2A1 production files and their command semantics stay
  unchanged. The old review always has experiment_gate=false.
- No new dependencies, database, model, inference, Android, network runtime,
  game interaction, automatic target selection or evolution calculation.
- New real development evidence requires a new natural complete unedited replay,
  human whole-match review and two clear independent plays of one known form.
- The old Inferno Dragon match remains a historical regression sample only.
- No actual Model Lock or Test GT is fabricated. Synthetic fixtures are tests.
- Private identities, labels, times, hashes and media remain in ignored folders.
- Missing new development footage means WAITING_FOR_DEVELOPMENT_MATCH, not
  DEV_LOCKED or READY_FOR_ACCEPTANCE. No merge, push, PR or next module.

## Task 1: experiment schema and development validation

Create experiment_contract.py, experiment_development.py and focused tests in
tools/offline_video. TDD: add tests and observe expected failures before behavior;
record focused RED/GREEN commands in the ignored task report. Use strict closed
JSON schemas and path-free EvidenceError. Reuse existing strict JSON loader and
validate_evidence; never relax v1 or bypass index/image checks at the disk boundary.

Public pure interface:

- validate_development(draft, indexes) -> a report with status DEV_VALIDATED or
  NOT_READY, reasons, derived candidate counts/eligibility, and conservative gaps.
- require_development(draft, indexes) -> the validated frozen payload or raises
  EvidenceError. It must not mutate callers. Additional helpers may be private.
- indexes is the same recording-keyed mapping produced by load_indexes.

Use one versioned development draft holding exactly one development identity,
candidate list, manual selected target/reason, v1 evidence bundles (one logical
card/form per bundle), deployment form/clear/evolution annotations, explicit
unknown intervals, creation time, freeze version and protocol/policy versions.
Define the exact fields in the implementation and anonymous test fixture; the
controller and later lock/CLI task consume these APIs, not unvalidated counts.
Candidate evidence must be validated with existing v1 validators; translate only
evolved <-> known_evolution at this adapter boundary. Unknown forms are retained
but cannot qualify. Candidate notes must capture distinctness, visibility,
occlusion and owner/form clarity; record eligibility/rejection reasons derived
from actual verified clear plays, never a caller-supplied count.

Match identity separates underlying_match_id and recording_id; requires split
development, new-natural (not historical) provenance, complete/unedited/full
human review attestations. recording_id must match every v1 evidence recording.
Target must be a candidate actually present in evidence. Selection is manual,
one known form, with a nonempty reason. At least two independent clear verified
plays of that exact card/form. normal+evolved cannot aggregate. Duplicate IDs,
reused occurrence references or duplicate deployment evidence cannot inflate
counts; annotations/frames are not plays. Identity is declared human provenance,
not cryptographic certification of an underlying real game.

Unknown intervals and other/unknown forms cannot overlap any proposed confirmed
negative interval. Compute/preserve uncovered gaps from the v1 evidence rather
than trusting advisory reports. Evolution metadata includes capable,
equipped verified/not_equipped/unknown, charge requirement and rules version;
per-play remaining count is nullable/manual only. Unknown interval, possible
missed play, unknown form/equipment/rules forces unknown progress/null remaining.
Validate types strictly (booleans are not ints, finite bounds, closed nested
objects, supported versions); do not leak arbitrary private strings in errors.

Tests cover normal twice eligible, normal+evolved not eligible, frames cannot
inflate independent count, unknown target, missing target, duplicate play refs,
other-form/unknown negative overlap, evolution unknown with claimed precision,
malformed nested fields, unchanged input and existing v1 validation failures.
Do not edit any existing tracked production/test file. Do not commit or push;
the controller runs full regression and commits after review. Report exact files,
interfaces, RED/GREEN results and concerns to the ignored task report.

## Task 2: immutable lock chain

Consume Task 1 pure APIs; add experiment_lock.py and tests. Canonical SHA-256
uses deterministic UTF-8 sorted-key compact JSON, disallows nonfinite numbers;
normalize serialized newline to a single LF. Hash the complete payload excluding
only its own digest, including identity, all evidence snapshots, candidate order,
selection, deployment/box/unknown/evolution data, split and protocol/version.
Use exclusive versioned files in outputs/local_data, reject existing destination
and duplicate freeze version for the same experiment/type in its lock directory.
Load and recompute hashes instead of trusting caller digests. Validate lock type,
version, nested payload schema and UTC ordering: development < model < test GT.

Model Lock is a contract, not a trainer: references development digest, exact
target, git commit and model hashes, input geometry/crop/resize/preprocess,
sampling rate, confidence, NMS/IoU, postprocess and evaluation protocol version.
No real model artifacts or fake real hashes are created in this task. Synthetic
contract construction is tested. Model time must be after development and
attest no earlier exposure to test pixels/precise GT.

Test GT must reference valid development and Model Locks; declared independent
underlying match and recording identity; first qualifying natural complete
unedited replay attestation; all target-form deployments (including non_evaluable
with reason), other/unknown forms, reviewed negatives and unknown intervals;
new independent annotation session and no prediction exposure attestation.
Reject prediction fields recursively by closed schemas, wrong lock hashes,
same match despite different recording/source hashes, unknown/other-form negative
overlaps and missing Model Lock. Whole-match completeness remains manual
attestation, not software proof. Record permissible invalid-material exclusions
only (damaged/missing replay, interrupted recording, undecodable), never difficulty.
Define Evaluation Result's references as a future contract; don't implement
metrics/inference. Tests prove stability/change/overwrite/version/order/linkage.

## Task 3: CLI, protocol and staged handoff

Add independent experiment_cli.py and tests. CLI loads strict local draft and
all explicit indexes through existing load_indexes; readiness returns 0 when
validated, 3 when insufficient and 2 when invalid/I/O. Freeze refuses non-ready
development. Safe local path handling and exclusive immutable outputs, sanitized
errors. Add lock contract validation/test GT freeze for later authorized reuse,
with gates enforced. No actual model/test artifacts this round.

Document exact JSON/contracts and commands, blind-test protocol and limits.
Update README, CURRENT_STATE, DECISIONS, DEVELOPMENT_PLAN, VERIFICATION_M2A2.
Record new thresholds explicitly superseding old 2A experiment gates only;
historical 2A1 four-play behavior remains unchanged. New flow: dev >=2 known-form
plays -> DEV_LOCKED -> separately approved 2B -> model lock -> independent test
>=1 target-form play -> separate-session GT lock before any inference.

Run full pytest, pip check, wheel build and diff check. Revalidate old four
reports/533 requests/402 unique success frames, validate=0/review=3, four plays/
12 boxes/eight gaps and original 591 hashes unchanged; prove old production
blobs unchanged, private data ignored, no real locks produced. End infrastructure
at WAITING_FOR_DEVELOPMENT_MATCH with one exact future prepare command, recommended
local recording filename and whole-replay instructions. Do not mark module done.
