# Module 2B-2B Multiclass Contract v1

Task 1 implements a separate, data-only `multiclass_visual_dataset` contract.
It does not change the historical Minions schema, accepted Development Lock,
old annotation tools or 2B-1 failure. Visual GT remains an observation; no row
is a runtime `OpponentCardPlayed` event. No model, training, media download,
on-device or live behavior is introduced.

## Implemented APIs and limits

`validate_multiclass_shape(draft: MulticlassDraft) -> None` validates closed JSON
types and declared relations. `validate_match_splits(draft: MulticlassDraft) ->
None` checks whole-match split declarations after the same strict type checks.
Both raise path-free `EvidenceError`, perform no file reads, and never mutate
the input. A valid empty or pending draft is not a ready dataset. They do not
verify actual files, whether humans reviewed exhaustively, match authenticity,
independence or asset rights. Those are separate checked binding/readiness gates.

`backend_label_maps(selected_class_ids: list[str]) -> dict[str, dict[str, int]]`
requires distinct, nonempty IDs. Labels sort by `(visual_class_id, owner)` using
owners `opponent`, `own`. Keys are `visual_class_id::owner`; visual class IDs
must not contain `::` or whitespace. YOLOX foreground starts at 0; TorchVision
foreground starts at 1, reserving background 0. Both owners are encoded for every
selected class; an encoded label does not establish training or evaluation support.

## Closed primitive and root types

Every object requires exactly its TypedDict fields; every nullable field must be
present with an explicit `null` when unknown. Arrays are JSON arrays; identifiers
and notes are nonempty strings. Integers are actual JSON integers, never bools.
Numbers must be finite; seconds are nonnegative. Hashes are lowercase 64-digit
SHA-256. UTC times use `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`. Rational time bases have
exactly positive-integer `numerator`, `denominator`.

Paths are forward-slash relative paths without drives, colons, absolute roots,
backslashes, empty segments, `.` or `..`. Source paths end `.mp4`, original image
paths `.png`, annotation/report/index paths `.json`. Syntax does not prove disk
containment, ignore state or safety; checked binding must enforce those later.

Root fields are exactly:

`kind`, `schema_version`, `dataset_id`, `freeze_version`, `created_at`, `taxonomy`,
`coordinate_policy`, `intake`, `matches`, `recordings`, `groups`, `frames`,
`annotations`, `annotation_sources`, `coverage`, `provenance`, `split_assignment`,
`selection`, `backend_label_maps`.

`kind=multiclass_visual_dataset`, `schema_version=1`; freeze version is a positive
integer. Coordinate policy is exactly `{space: normalized_full_image,
box_extent: visible, image_basis: original_rotated}`. The root is not an old-lock
conversion and does not use an old lock digest as evidence of qualification.

## Taxonomy, inventory and sources

| Type | Exact fields |
| --- | --- |
| Taxonomy | `taxonomy_id`, positive `version`, `classes`, `alias_mapping` |
| VisualClass | `visual_class_id`, `kind`, `mobility`, `definition` |
| AliasMapping | `alias`, `visual_class_id` |
| IntakeRow | `intake_id`, `recording_id`, `status`, `reason`, `history` |
| IntakeHistory | `status`, `reason` |
| MatchRow | `underlying_match_id`, `provenance`, `identity_attestation`, `notes` |
| ProvenanceRow | `source_id`, `creator`, nullable `source_url`, `artifact_kind`, nullable `license_evidence`, `allowed_scope` |
| AnnotationSource | `annotation_source_id`, `path`, `sha256` |
| ReviewProvenance | `method`, nullable `reviewed_by`, `notes` |
| SplitAssignment | `underlying_match_id`, `split` |

Kind is `unit/building/spell_effect/projectile/battlefield_object/ui`; mobility is
`moving/static/unknown`. No card list is hardcoded. Aliases resolve to declared
canonical classes and cannot repeat. Match provenance is `natural/unknown`,
identity attestation `human_confirmed/pending`. Intake status is
`included/pending/excluded`; history preserves declared order. Review method is
`manual/pending`. Confirmed/verified/complete declarations require a named manual
reviewer. Provenance artifact kind is `code/dataset/game_asset/model_weight/
recording/annotation/synthetic_test`; allowed scope is `reference_only/
development_training/test_evaluation/manual_evidence`. Training rights are not
inferred from those strings; readiness must inspect the evidence.

Recording, intake and match inventories agree exactly. Identical source hashes
cannot claim independent underlying matches. IDs are unique in their collection;
export IDs are unique within their recording. Annotation source paths are unique.

## Recording and original-frame binding

RecordingRow fields are `recording_id`, `underlying_match_id`, `split`, `source_id`,
`source_sha256`, `source_path`, `perspective_ref`, `width`, `height`,
`rotation_degrees`, `time_base`, `origin_pts`, `origin_time_base`,
`last_frame_seconds`, `technical_valid`, `complete_recording`, `unedited_recording`,
`full_human_review`, `completion_attestation`, `terminal_result_screen_present`,
`match_segment`, `exports`, `review_provenance`.

Technical metadata fields from width through last-frame seconds may be null in
undecodable retained pending sources; technically valid recordings require all
of them. Dimensions are positive integers, rotation `0/90/180/270`, raw PTS actual
integers. MatchSegment is nullable or exactly `{start_seconds, end_seconds,
complete_match}` with positive-duration bounds within the actual recording.
Completion attestation is `user_confirmed/pending`. User-confirmed complete-match
bounds must equal `0..last_frame_seconds`. Included development sources additionally
require all technical/completeness/unedited/full-review booleans, a complete segment,
natural confirmed match identity and exports. A missing terminal result screen is
legal and has no completeness-gate role.

ExportReference is `{export_id, report_path, index_path, report_sha256,
index_sha256}`. FrameRow is `{frame_id, recording_id, export_ids,
timestamp_seconds, raw_pts, time_base, origin, image_path, image_width,
image_height, image_sha256, perspective_ref, perspective_change_reason,
review_state, review_provenance}`. FrameOrigin is `{raw_pts, time_base}` and must
match the recording's first displayed frame. Frame state is `complete/pending/excluded`.
Perspective-change reason is explicitly nullable; a changed reference requires a reason.

Frame IDs use the existing canonical `frame_id(recording_id, raw_pts, time_base)`.
Duplicate actual `(recording, PTS)` cannot acquire a new identity. Display seconds
must agree with actual PTS minus origin within 1 microsecond. The last-frame
comparison uses the producer's `float(actual_pts_seconds)` representation, so
a legal rounded final-frame value (for example 1/3 seconds) remains inclusive;
no extra boundary epsilon is added. Dimensions match the complete original after rotation, never a model
resize or crop. Exports must resolve to declarations in that recording. Actual PNG,
PTS index and report integrity are checked only by later disk binding.

## Appearance, causality and observation GT

GroupRow is `{appearance_group_id, underlying_match_id, recording_id,
visual_class_id, owner, observed_form, origin_kind, causal_root_id,
parent_group_id, entity_occurrence_id, human_deployment_id,
independence_attestation, verification_state, start_seconds, end_seconds,
review_provenance}`. Parent/entity/human-deployment IDs are explicitly nullable.
Verification is `confirmed/ambiguous/unreviewed/rejected`; independence is
`human_confirmed/pending`. Origin is `direct/summoned/transformed/unknown`.

Causal roots reference actual root groups with `causal_root_id=appearance_group_id`
and null parents. Derived groups preserve the same underlying match and root;
parents are acyclic, existing references. Direct groups cannot declare parents.
Declared root human-deployment and singleton entity IDs cannot establish multiple
roots within one match. Renaming root/group/event IDs with identical declared
class/owner/form/origin/appearance bounds is rejected as a duplicate declaration.
One group may contain multiple visible units and span multiple frames. A derived
group is never evidence of an additional independent cause merely because it has
a separate group ID. No validator invents missing human causality.

AnnotationRow is `{annotation_id, annotation_source_id, recording_id, frame_id,
appearance_group_id, entity_occurrence_id, visual_class_id, owner,
perspective_ref, observed_form, visual_stage, box, source_card_id,
source_card_candidates, mapping_basis, mapping_verification, occlusion,
truncation, review_state, review_provenance}`. Group/entity/stage/source-card IDs
are explicitly nullable. Owner is `own/opponent/neutral/unknown`; form is
`normal/evolved/unknown`; visibility is `none/partial/unknown`. Observation state
is `verified/pending`. The annotation perspective matches its frame. A referenced
group agrees on match, visual class, owner and form; its own-recording frames lie
inside its appearance bounds using the producer-represented actual PTS instant.
Appearance intervals normally exclude their end. Only a group ending at the
recording's last-frame boundary may include a frame whose actual PTS is that
terminal boundary, including rounded non-terminating values such as 1/3 seconds.
A rounded declared timestamp cannot impersonate that actual terminal instant.
Known entities retain one cause across frames.

Box is exactly normalized original-image `{x,y,width,height}`, with finite
nonnegative coordinates, positive dimensions and right/bottom at most 1. One
known entity has at most one annotation in a frame; renaming an entity or annotation
cannot duplicate an identical frame/box. GT rejects prediction fields such as
`score/model_id`. Unknown owner/form remains unknown, never ordinary/opponent/negative.

Source-card mapping is orthogonal and many-to-many, not an elixir or deployment
inference. Candidates are distinct; a declared source-card ID occurs in that set.
Mapping basis is `manual/external_reference/unknown`, verification `verified/pending`.
Verified mapping requires a known source ID and known basis; NULL and ambiguous
candidates remain valid pending mappings. Different classes can share a card,
and one visual class can list several source cards.

## Coverage, split isolation and selection

CoverageRow is `{coverage_id, recording_id, frame_id, exhaustive_for_classes,
exhaustive_state, reviewed_regions, unknown_intervals, ignore_regions,
ignore_reasons, review_provenance}`. Exhaustive state is `complete/pending`;
class sets contain distinct declared IDs. Reviewed regions are normalized boxes.
UnknownInterval is `{start_seconds, end_seconds, visual_class_ids, reason}`;
IgnoreRegion is `{box, visual_class_ids, reason}`. Intervals remain inside the
actual recording; region/interval class IDs exist. Complete frames require one
explicit complete coverage row. Complete class coverage requires reviewed regions
and verified annotations for those classes. Empty boxes without such review do
not certify absence or time-based FP/min.

Split is `train/development_validation/prospective_test`. Assignment covers each
underlying match exactly once; all recordings, crops and derivatives inherit that
match's split. Prospective-test identities may remain pending/excluded inventory,
but cannot be included development material or supply development qualification.

For later support/scale statistics, choose the first included available recording
of each underlying match in original intake order. Re-encodes cannot add groups,
real-frame counts, boxes or statistical weight. Shared match/cause/group/entity
identities and known image hashes preserve explicit duplication evidence. There is
no inferred cross-recording alignment; conservative exclusion of later re-recorded
support is preferable to counting it as independent. This is a documented
consumer rule; Task 1 itself does not compute support or scale statistics.

Selection is null with empty backend maps, or exactly `{selected_class_ids,
class_decisions, scale_snapshot_digest, policy_id}`. ClassDecision is
`{visual_class_id, selected, reason}` and covers every taxonomy class once, including
unselected reasons. Selected IDs and decisions agree; both maps equal the stable
joint maps. Policy is `dev_moving_area_quantiles_v1`; its digest is syntactically
checked here, not proof of an existing frozen scale snapshot.

The later readiness gate remains opponent-first: each selected class needs
independent opponent support in TRAIN and DEV_VAL; at least one selected class
also needs own support in both. Unsupported own subgroups are
`not_qualified/not_evaluated`. Encoded own labels or valid shape do not certify
bidirectional owner recognition. Exhaustive own-frame annotation is still required.

## Interfaces reserved for Tasks 2–5

The module defines closed TypedDicts for CandidateReport, ScaleReport,
ReadinessReport, ScaleSnapshot, MulticlassLock and ExportManifest, with explicit
support counts/IDs, rational statistics, reasons, media/label snapshots and transforms.
Task 2 implements candidate, scale and prospective readiness reports below;
Task 3 implements checked disk binding and separate freezes below. Annotation
editing and actual exports remain separate consumer tasks.
Scale statistics carry exact `{numerator, denominator}` values and both all-reviewed
and clean-representative distributions. All lock envelopes have exactly
`kind/version/id/created_at/payload/digest`. No prediction fields are present.
BoundMulticlass remains a typing Protocol in the contract module; Task 3 supplies
the private checked disk factory and rejects ordinary caller-created dictionaries.

## Task 2: pure qualification and fixed Development scale policy

`multiclass_readiness.py` implements exactly:

- `candidate_eligibility(draft: MulticlassDraft) -> CandidateReport`
- `development_scale_report(draft: MulticlassDraft) -> ScaleReport`
- `multiclass_readiness(draft: MulticlassDraft, scale_snapshot: ScaleSnapshot | None = None) -> ReadinessReport`

These functions validate declarations and do not open files, create any lock,
change GT, evaluate a detector or authorize training. `ready=true` means only
prospective data qualification. A missing optional snapshot is not a data
readiness blocker; Task 3 must require a valid checked snapshot when freezing.
The old experiment/review gates are unchanged.

Original intake order selects the first included Development recording of each
underlying match. Pending/excluded intake and prospective-test recordings do not
supply support. Later re-recordings and repeated export references add no counts
or scale weight. A support annotation must be verified, normal, own/opponent and
refer to a confirmed group declared in that same primary recording. Its actual
causal root must be confirmed with `human_confirmed` independence. A confirmed
derived group with an explicit parent/root may retain pending independence:
it shares the root's single support, never creates an independent event. A
pending/unconfirmed root cannot be repaired by a confirmed derived ID. Explicit
`frame.review_state=excluded` supplies neither basic support nor scale statistics;
a pending frame's class-verified observations may still supply pre-selection
support, but cannot supply final export support.

All normal support is aggregated once per
`(underlying_match_id, causal_root_id, visual_class_id, owner)`. `counts.groups`
counts those independent supports, not group rows, units, boxes or frames.
`counts.matches/entities/frames/boxes` remain separate. Actual group/frame/annotation
IDs are retained; entity counts use match-scoped known entity identities. Basic
candidate qualification requires opponent support in both TRAIN and DEV_VAL,
known mobility and first-PoC unit/building kind. Every taxonomy class is reported,
including unqualified classes and reasons. Candidate owner/split cells describe
local support, not final owner-joint qualification or measured recognition.

The scale pool is **all** basically qualified normal moving-unit classes before
selection and final whole-frame export filtering. Missing clean support is
`scale_support_pending`, retained in that pool and blocks size coverage. Each
independent support needs a verified, known-owner normal annotation with neither
occlusion nor truncation. Unlike owner-split support cells, scale weighting groups
all owners together by `(underlying_match_id, causal_root_id, visual_class_id)`.
Median unit area per true frame is followed by median clean frames per unique
cause, then median cause scores per match, then median match scores per class.
An owner change cannot give the same cause another scale weight. A cause is
scale-support-pending only if none of its owner branches has a clean observation;
an unclear sibling branch does not invalidate another clean branch. Matches and
classes have equal weight. An existing group with earliest `(start_seconds, appearance_group_id)`
is only a report representative; that ID never changes weights or eligibility.
`ScaleGroupSupport` retains descriptive owner-branch scores and true clean member
IDs; these owner branches are not independently weighted cause scores. Candidate
support retains all actual appearance-group members.

Decimal values use exact `Fraction(str(value))`. Pixels use the original rotated
image dimensions: width=`box.width*W`, height=`box.height*H`, short side their
minimum, area=`box.width*box.height`. All reviewed and clean-representative
distributions report exact count/min/P10/P50/P90/max. Type 7 quantiles use
`h=(n-1)*p` with exact linear interpolation; no epsilon, rounding or ID-based rank
breaks. Q25/Q75 use one class score per full-pool class. If Q25<Q75, <=Q25 is
`relative_small`, >=Q75 is `large`, the interior is `medium`. If cutpoints collapse
but min<max, min is small, max large and the rest medium. All equal scores, fewer
than two clean moving candidates or any pending moving candidate yield
`SIZE_COVERAGE_INSUFFICIENT`; no scale group is invented to satisfy the gate.
Buildings retain descriptive statistics without contributing scale cutpoints.

Final export support is recomputed independently. A whole frame must be complete,
have complete exhaustive coverage for every selected class and exact union of
reviewed rectangles covering the entire normalized image. An explicit full-image
rectangle or overlapping/tiled exact coverage is accepted; even a tiny gap is not.
Selected pending/unknown-owner/neutral/other-form observations, relevant unknown
intervals and selected ignore regions block the entire frame because there is no
reliable ignore-loss mask. Generic ignore reasons and class-unspecified ignore
regions/intervals are conservatively relevant to all selected classes. Unknown
intervals are half-open except that an interval ending at the recording boundary
includes the actual terminal frame. Clearing annotations does not manufacture
coverage or certify an empty negative. Non-export reasons are retained in final
owner/split support; `frame_export_reasons(draft, frame_id) -> list[str]` exposes
the same whole-frame gate to Task 5, including empty frames.

Final readiness requires 3–5 selected classes, at least two moving units, a
selected qualified relative-small moving class and a selected medium/large one.
Each selected class needs independent **exportable** opponent support in both
splits. At least one selected class needs exportable own support in both. Other
own joint subgroups have both cells `not_qualified/not_evaluated` with
`own_control_incomplete`, preserving any real partial counts and IDs. Even complete
own controls remain `not_evaluated`: no model evaluation occurred. Used primary
recording sources require non-null license evidence and `development_training`
scope; unrelated unused reference-only rows do not block. This validates explicit
provenance declarations, not the truth of a legal rights assertion.

All blockers are reported together. Status precedence is INVALID_DATASET, then
PROVENANCE_INSUFFICIENT, then SIZE_COVERAGE_INSUFFICIENT, then DATA_INSUFFICIENT;
only no blockers yields MULTICLASS_DATASET_READY. Malformed input produces
`candidate_report=null`, `scale_report=null`, `export_support=[]` and no fabricated
digests. Null reports are allowed only with INVALID_DATASET. Direct candidate and
scale APIs raise sanitized EvidenceError for invalid shape/canonical serialization.
Readiness catches those EvidenceErrors during report construction, returning the
same null-report INVALID_DATASET boundary even for non-UTF-8-serializable Unicode
declarations; unrelated programming errors are not swallowed.

The shared consumer helpers `scale_basis(draft) -> MulticlassDraft` and
`scale_basis_sha256(draft) -> str` validate and copy the closed draft, remove only
selection/backend maps and canonicalize set-like collection order. All remaining
GT, inventory, metadata, split and provenance fields are committed, including
retained pending/prospective-test inventory; none of that inventory supplies scale
support. Original intake and its history order remain significant. The split hash
commits the canonical whole-match assignment separately. A supplied ScaleSnapshot
must satisfy closed types, canonical envelope SHA excluding `digest`, unselected
payload draft/basis hash and exact recomputed candidate/scale reports. Its basis
must equal the current full pre-selection basis, and any current selection digest
must refer to it. Re-signing fabricated statistics or changing GT/splits does not
make a snapshot current. Backend maps/selection never change that statistical
basis. These shared helpers do not replace Task 3's checked disk binding.

The accepted design and task boundaries remain in the
[amended spec](superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md) and
[Phase A plan](superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md).

## Task 3: checked artifacts and separate immutable freezes

`multiclass_dataset.py` exposes:

- `bind_multiclass(draft: MulticlassDraft, data_root: Path) -> BoundMulticlass`
- `freeze_scale_snapshot(bound: BoundMulticlass, directory: Path) -> ScaleSnapshot`
- `load_scale_snapshot(path: Path, data_root: Path) -> ScaleSnapshot`
- `freeze_multiclass_dataset(bound: BoundMulticlass, scale_snapshot: ScaleSnapshot, directory: Path) -> MulticlassLock`
- `load_multiclass_dataset_lock(path: Path, data_root: Path) -> MulticlassLock`

The explicit absolute `data_root` is a repository-local container (the repository
itself may be used). Every container-relative source, report, index, image and
label artifact must stay inside that container and ignored, untracked repository
`outputs/` or `local_data/`. Lock output/read paths are explicit absolute private
paths. URLs, UNC, drives in relative paths, traversal, symlinks and junctions
(including ancestors) are rejected before resolving references. Public legacy
`dataset_artifact_path`/`private_artifact_path` are reused without changing old
contracts or lock factories. The legacy private `_disk_operation` decorator is
reused only for identical-path Git privacy checks within a single top-level disk
operation: no content/hash/containment caching or cross-operation authority.

A new multiclass label sidecar has exactly `{schema_version: 1,
annotation_source_id, annotations}`. `annotations` contains the full closed
AnnotationRow set for that source, including retained pending and non-target
metadata. Its source ID agrees with every row. Sidecar raw SHA is declared in
the draft; no self-hash is embedded in the sidecar. Set ordering is semantically
canonical, but the raw byte SHA is still exact. This is not the old
`unit_annotations` sidecar schema and uses no old deployment defaults.

Binding loads each declared export through unchanged strict `load_indexes`,
with its own report/image/contact-page path base, then merges all exports to
reject conflicting duplicate pixels. A declared frame must occur with its
actual PTS/time base/timestamp/dimensions in every listed export and its image
path must be a real alias. Source SHA, original rotated geometry, origin, terminal
metadata and report/index pairing must agree. At bind, all declared source bytes, raw
JSON, successful export images and contact pages are hashed and rechecked;
sidecars must correspond exactly to the full draft labels. No caller-provided
snapshot replaces these disk reads. Binding may retain valid pending inventory;
binding alone establishes neither readiness nor a lock.

This does **not** decode original MP4s again. Source hash plus producer reports
and indexes bind existing metadata; they cannot independently certify source
first/last PTS, completeness, natural match identity, human exhaustive review or
rights assertions. Digests are consistency checks, not signatures, authenticity
proof or protection against a caller with write access. No extra epsilon changes
the original 100ms export tolerance or producer-compatible terminal boundary.

The closed draft persists hashes for MP4s, indexes, reports, declared frames and
label sidecars. Reload checks those historical declared hashes. Additional
successful export PNGs and contact pages not listed as draft frames are re-read
through the current strict loader and safe reference checks, but have no
persisted historical-byte hash in this schema. Bind-to-freeze compares their
in-memory hashes too; later lock reload cannot certify their historical bytes.
They supply no GT, scale or export support. This is not a requirement to turn
every locator export into a reviewed draft frame. The separate phase protection
inventory safeguards all pre-existing private bytes without changing this schema.

The bound implementation is private and freeze requires its checked context.
Each freeze rebinds all dependencies and rejects changes since bind, including
raw-byte changes with unchanged JSON meaning. A frozen/loaded ScaleSnapshot is
a checked dict subclass carrying its path/container/raw file SHA **only in
memory**; these are not extra envelope fields. `dict(snapshot)` is the closed
JSON value for pure readiness/serialization consumers. Ordinary dictionaries,
including re-signed valid-looking snapshots, cannot authorize dataset freeze.
The prior checked snapshot is reloaded and its file bytes compared at freeze.

Scale freeze requires a complete qualifying full moving-candidate scale pool
and qualified used-source provenance, before selection. The public freeze API
rejects an input with non-null selection, even if its statistics are valid; it
does not erase a final selection to manufacture prior scale evidence. Its draft is the shared
`scale_basis`: no selection, empty backend maps, all retained inventory/GT/splits
committed. It is not MULTICLASS_DATASET_LOCKED or training permission. Dataset
freeze separately requires checked prior scale evidence plus selected-data
readiness. Only selection and deterministic backend maps may differ from the
prior basis; changing GT, inventory, split, metadata, policy, created time or
freeze version needs a new snapshot/version, never an edited old lock.

Both envelopes retain exactly the Task 1 fields. Their `id`/`created_at` equal
the payload draft's dataset ID/time; envelope `version=1` is format version,
while `draft.freeze_version` is immutable data revision. Dataset load validates
and rederives its embedded full scale evidence and all current external data.
The closed dataset JSON embeds the scale value, not its original disk path;
reload checks that embedded evidence rather than claiming independent proof of
the historical existence/chronology of the external scale file.

Set-like collections sort deterministically; intake and its history remain in
original order. Raw file hashes and semantic draft/envelope digests are distinct.
New files use a SHA-256 ID namespace plus kind/revision, never arbitrary IDs as
paths. The directory rejects an existing same-kind/ID/revision even after rename;
exclusive creation also ensures one winner for concurrent same-version writers.
Failed partial writes remove only the regular file inode created by that
operation, not an existing lock or another writer's replacement. Locks, old
sources and old single-card behavior are never overwritten or migrated.
