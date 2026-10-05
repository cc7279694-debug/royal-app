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
These are typed interfaces, not implemented readiness/freeze/export behavior.
Scale statistics carry exact `{numerator, denominator}` values and both all-reviewed
and clean-representative distributions. All lock envelopes have exactly
`kind/version/id/created_at/payload/digest`. No prediction fields are present.
BoundMulticlass is only a typing Protocol in Task 1: Task 3 must implement the
opaque, checked disk factory and reject ordinary caller-created dictionaries.

The accepted design and task boundaries remain in the
[amended spec](superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md) and
[Phase A plan](superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md).
