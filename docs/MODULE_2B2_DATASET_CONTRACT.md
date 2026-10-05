# Module 2B-2 Unit Dataset Contract v1

This is the closed, separate **data-only** draft contract. It references the
accepted Development Lock without changing its schema, original group boxes,
Module 1, or existing prepare/validate/review behavior. There is no model runtime,
training, inference, detector success, test-set permission or live capability.

## APIs and boundary

`validate_dataset_shape(draft: dict) -> None` raises path-free `EvidenceError` for
an invalid shape or contradictory declared evidence. It does not access files.
`dataset_readiness(draft: dict) -> dict` reports valid/invalid and independently
derived training-data and evaluation-coverage gates, without mutating input.
`grouped_folds(draft: dict) -> list[dict]` validates and derives deterministic LOMO
ownership. Fewer than two eligible matches produces no folds, never an empty
training split. Insufficient data can remain a valid draft.

All objects below require **exactly** the listed fields. Arrays have meaningful
declared order; no consumer may silently reorder intake, history, deployments,
frames or boxes. Identifiers are nonempty strings. Numbers must be finite JSON
numbers; booleans are not numbers. Integers must be actual JSON integers.
`seconds` means a nonnegative finite number. SHA-256 values are lowercase 64-digit
hex strings. `time_base` is exactly `{numerator, denominator}`, both positive
integers. UTC is explicit ISO `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`.

All source, export, image and label paths use forward slashes and are relative to
**one explicitly selected absolute data container** supplied by the checked
disk-binding caller. The repository root may be that container so existing
`local_data/` recordings and `outputs/` exports can be referenced together without
duplicating media. Each resolved artifact must itself remain inside Git-ignored,
untracked `outputs/` or `local_data/`. The container grants no access to other
repository files and is not implicitly the current directory, each export
directory, or the lock directory. Links and junctions in any ancestor reject.
No absolute paths, drives, backslashes, empty path segments, `.` or `..` are
allowed. PNG paths end in `.png`; annotation/report/index paths end in `.json`.
Task 2 must resolve legacy index-relative PNG aliases to this root-relative form
and check the actual files, hashes, metadata and containment, including links.
Shape validation alone cannot certify on-disk integrity, source authenticity,
human independence or complete labelling.

Task 2 disk consumers use
`load_dataset_indexes(draft, data_root, *, development_lock_path: Path) -> dict`
with an explicit absolute Development Lock file. Its checked context carries
paths outside JSON. `bind_dataset`, `freeze_dataset` and `load_dataset_lock`
re-read the actual files; a plain snapshot dictionary is insufficient.
`dataset_artifact_path(data_root, relative) -> Path` and
`private_artifact_path(absolute_path) -> Path` check confinement and Git privacy
without creating files and are shared by the later additive annotation writer.

The separate closed annotation sidecar is exactly
`{schema_version: 1, annotation_source_id, unit_annotations}`. Its ordered array
contains full UnitAnnotation rows for that source only; no draft/sidecar digest
field creates a self-hash cycle. `validate_annotation_source(document) -> None`
checks this closed shape. Binding additionally requires exact semantic equality
with the corresponding draft rows, including order. The canonical draft binds
frame-review metadata. The separate `training_dataset` envelope binds `draft`,
recomputed `derived` and `folds`, checked `index_snapshot`, and
`development_lock_reference={path, file_sha256}`; the latter path is relative to
the explicit container, never absolute. Pure lock validation checks the digest
and declared contract; only checked disk consumers certify current file bindings.

## Root fields

| Field | Type / fixed meaning |
| --- | --- |
| `schema_version` | integer `1` |
| `dataset_id` | identifier |
| `freeze_version` | positive integer, explicit additive version |
| `created_at` | explicit UTC string |
| `development_lock_sha256` | accepted old Development Lock digest |
| `target` | exactly `{card_id: "minions", owner: "opponent", form: "normal"}` |
| `visual_class` | exactly `"minion_unit"` |
| `coordinate_policy` | exactly `{space: "normalized_full_image", box_extent: "visible", image_basis: "original_rotated"}` |
| `intake` | original-order array of Intake objects |
| `matches` | array of Match objects |
| `recordings` | array of Recording objects |
| `deployments` | array of Deployment objects |
| `frames` | array of Frame objects |
| `unit_annotations` | array of UnitAnnotation objects |
| `unknown_intervals` | array of UnknownInterval objects |
| `confirmed_absent_intervals` | array of AbsentInterval objects |
| `annotation_sources` | array of AnnotationSource objects |

Fold assignments are derived, not accepted as editable draft claims. Task 2
binds them into its separate canonical payload and `training_dataset` envelope;
the draft does not contain a self-digest, legacy lock type, model or predictions.

## Inventory, provenance and media

| Object | Exact fields and types |
| --- | --- |
| Intake | `intake_id`: identifier; `recording_id`: identifier; `status`: included/pending/excluded; `reason`: nonempty text; `history`: ordered array of History |
| History | `status`: included/pending/excluded; `reason`: nonempty text |
| Match | `underlying_match_id`: identifier; `provenance`: natural/unknown; `identity_attestation`: human_confirmed/pending; `notes`: nonempty text |
| ReviewProvenance | `method`: manual/pending; `reviewed_by`: identifier or null; `notes`: nonempty text |
| CompleteSegment | `start_seconds`, `end_seconds`: seconds, start < end |
| Export | `export_id`: identifier scoped to recording; `report_path`, `index_path`: root-relative JSON paths; `report_sha256`, `index_sha256`: SHA-256 |
| AnnotationSource | `annotation_source_id`: identifier; `path`: root-relative JSON path; `sha256`: SHA-256 |

Recording requires exactly these fields:

| Field | Type / meaning |
| --- | --- |
| `recording_id`, `underlying_match_id` | identifiers |
| `source_path`, `source_sha256` | root-relative source path and SHA-256 |
| `exports` | array of Export objects; multiple previous report/index pairs are legal |
| `width`, `height` | original unrotated positive integer dimensions |
| `rotation_degrees` | integer 0/90/180/270 |
| `time_base`, `origin_time_base` | rational objects |
| `origin_pts` | integer PTS of the first displayed frame |
| `last_frame_seconds` | seconds of actual last normalized decoded PTS |
| `technical_valid`, `complete_recording`, `unedited_recording`, `full_human_review` | booleans |
| `completion_attestation` | user_confirmed/pending |
| `terminal_result_screen_present` | boolean, independent of completeness |
| `complete_segment` | CompleteSegment or null |
| `review_provenance` | ReviewProvenance |

For `technical_valid=false` retained pending/excluded sources, technical fields
from `width` through `last_frame_seconds` may individually be null, exports may
be empty and complete_segment may be null. No frames, deployments or intervals
may reference unavailable required technical metadata. This retains undecodable
sources with honest reasons rather than inventing facts.

Every recording has exactly one Intake entry and one Match identity; every Match
has a recording. IDs are unique within their appropriate scope. Identical source
bytes cannot claim separate matches. Multiple reencoded recordings may belong to
one match; file hashes never establish independence. Included recordings require
all four validity/completeness/edit/full-review booleans true, natural human
confirmed match identity, manual review provenance, exports and user_confirmed
completion. Their segment must be exactly **0..last_frame_seconds**, even without
result UI. Pending/excluded sources and all history stay retained with reasons.

Annotation sources are separate additive label sidecars, not hashes of this draft
or of its containing lock; this avoids a self-hash cycle. Their IDs and paths are
unique. External annotation/image content validation belongs to Task 2.

## Deployment, frame and unit fields

Deployment requires exactly these fields:

| Field | Type / meaning |
| --- | --- |
| `deployment_id`, `underlying_match_id`, `recording_id` | identifiers; true play key is **(underlying_match_id, deployment_id)** |
| `owner` | opponent/own/unknown |
| `source_card` | nonempty card identifier, including explicit `unknown` |
| `form` | normal/evolved/unknown |
| `verification_status` | confirmed/ambiguous/unreviewed/rejected |
| `independence_attestation` | human_confirmed/pending |
| `onset_lower_seconds`, `onset_seconds`, `onset_upper_seconds` | ordered seconds, manually declared onset bounds |
| `visible_start_seconds`, `visible_end_seconds` | seconds, positive length reviewed visibility range |
| `occlusion`, `truncation` | none/partial/unknown |
| `review_provenance` | ReviewProvenance; confirmed requires manual/non-null reviewer |

On its declared recording, ordering is:
`0 <= onset_lower <= onset <= onset_upper <= visible_start < visible_end <= last_frame`.
The recording must belong to the same match. Renaming a play cannot duplicate its
match/owner/source/form/onset evidence. Different match IDs may reuse a local
deployment ID. This inventory is annotation ground truth, not runtime events.

Frame requires exactly these fields:

| Field | Type / meaning |
| --- | --- |
| `frame_id`, `recording_id` | identifiers; true frame key is **(recording_id, frame_id)** |
| `export_ids` | nonempty unique array of this recording's Export IDs |
| `timestamp_seconds`, `raw_pts`, `time_base` | normalized seconds, integer PTS and rational object |
| `image_path`, `image_sha256` | root-relative PNG path and actual file-content SHA-256 |
| `image_width`, `image_height` | positive integer original **rotated** image dimensions |
| `review_status` | complete/pending/excluded |
| `minion_presence` | positive/absent/unknown |
| `all_identifiable_units_labelled` | boolean human frame-wide attestation |
| `review_provenance` | ReviewProvenance; complete requires manual/non-null reviewer |

PTS normalization is `raw_pts * time_base - origin_pts * origin_time_base`,
within one microsecond of stored seconds and within the actual recording bounds.
The upper endpoint compares `float(normalized PTS)` to the producer's serialized
`last_frame_seconds`, matching the unchanged index loader for nonterminating
rational final timestamps. The lower endpoint remains exactly zero; this adds no
time epsilon and does not change export selection or its inclusive 100ms tolerance.
Rotated dimensions must match the recording. Renamed copies of the same recording
PTS cannot become extra frames. A complete frame has no uncertain potentially
unlabelled minion-like content, has all identifiable units labelled, and has only
verified unit annotations. Complete positive frames require at least one box.
Complete absent frames have no boxes or possible minion-like deployment at that
time. Pending/excluded frames are retained and excluded from the training view.

UnitAnnotation requires exactly these fields:

| Field | Type / meaning |
| --- | --- |
| `annotation_id`, `annotation_source_id`, `recording_id`, `frame_id` | identifiers with existing frame/sidecar references |
| `deployment_id` | match-scoped identifier or null |
| `owner`, `source_card`, `form` | same independent semantic types as Deployment |
| `visual_class` | exactly minion_unit |
| `normalized_bbox` | exactly `{x, y, width, height}` with finite numeric components |
| `occlusion`, `truncation` | none/partial/unknown, visible rather than inferred body |
| `review_status` | verified/pending |

Boxes require `0<=x,y<=1`, `0<width,height<=1`, `x+width<=1`, `y+height<=1`.
They describe tight visible unit extent in the full original rotated image;
occluded hidden body, shadow and beam are not boxed. Annotation IDs are globally
unique; identical frame/box evidence under new IDs rejects. Referenced deployments
must share the underlying match and exactly match owner/source/form. On the
deployment's own recording the frame lies in its visibility window. An ordinary
opponent minions/normal annotation must reference a real matching deployment.
Unknown/other-source/own-side units may have null deployment references and still
be valid visual positives; they neither create target plays nor become negatives.

There is **no automatic cross-recording time alignment**. Alternate recordings'
unit boxes may retain a human-assigned same-match deployment reference, but their
relative times are not compared against another recording and cannot provide
that deployment's eligibility support. All their frames still inherit the match
fold. Approximately four spaced frames per play is a sampling goal; one complete
positive frame can qualify a play, with any actual number of identifiable units.

## Unknown and absent coverage

| Object | Exact fields and types |
| --- | --- |
| UnknownInterval | `interval_id`, `recording_id`: identifiers; `start_seconds`, `end_seconds`: seconds; `reason`: nonempty text |
| AbsentInterval | `interval_id`, `recording_id`: identifiers; `start_seconds`, `end_seconds`: seconds; `review_provenance`: manual ReviewProvenance with non-null reviewer |

Intervals have positive length within actual recording bounds and unique IDs
within their respective collections. Ranges are half-open, with exact last-frame
membership permitted at the terminal recording end. Certified absence means no
minion-like units, including own/other-source/evolved/unknown units. It may overlap
neither unknown intervals, any possible deployment visibility, nor a boxed unit.
It also rejects any overlapping frame declaring positive or unknown minion
presence, even when that frame is pending/excluded, unboxed, or not linked to a
deployment. Removing boxes or excluding a frame cannot turn uncertain content
into certified absence.
Unknown intervals force affected frames to remain pending/excluded.

Sparse complete empty-box frames supply training examples only. They never
certify surrounding time. Absent intervals are unioned **per recording** so
overlaps do not double count. The **first included recording of each eligible
match in original intake order** is its `evaluation_recording_id`; only that
recording's union duration contributes to the evaluation denominator. Other
recordings' coverage is reported separately and cannot replace missing coverage
or be combined through guessed timeline alignment.

## Readiness report and folds

The report has `valid`, `training_data_ready`, `evaluation_ready`, `counts`,
`reasons`, `evaluation_reasons`, `confirmed_absent_seconds`, `per_match`,
`per_recording`, and fixed `coverage_scope="reviewed_absent_intervals_only"`.
An invalid report has false gates, zero counts/coverage, empty per-match/recording
arrays and reason `invalid_dataset_shape`; callers seeking detailed path-free
diagnostics may call validation directly.

Counts are derived integer fields: `matches`, `recordings`, `deployments`,
`images`, `unit_boxes` (all retained records); `target_positive_matches`,
`confirmed_target_deployments`; `training_images`, `positive_training_images`,
`negative_training_images`, `training_unit_boxes`; `pending_frames`, and
`unknown_intervals`. A training frame is complete and its recording is included.
These image/box counts are not independent deployment counts.

An eligible target deployment has opponent/minions/normal semantics, confirmed
manual verification, human-confirmed independence, an included source, and at
least one complete positive frame with a verified box on **its declared
recording**. A new match with just one such play is eligible. Training readiness
requires **>=4 distinct eligible underlying matches AND >=8 eligible deployments**.
Missing requirements are `need_four_target_positive_matches` and/or
`need_eight_confirmed_target_deployments`. No old per-match two-play or 3-5-group-box
threshold is inherited.

`per_match` lists eligible matches in intake order, each with underlying_match_id,
confirmed_target_deployments, evaluation_recording_id, confirmed_absent_seconds
and has_certified_absent_coverage. `per_recording` retains intake order and gives
recording_id, underlying_match_id, included and confirmed_absent_seconds.
Evaluation readiness additionally needs positive certified absent duration for
each selected evaluation recording; otherwise `missing_absent_coverage` is
reported (and `training_data_not_ready` if applicable). This describes readiness
of a reviewed subset, never full-timeline review, detector success, zero FP or
permission to train. A valid training-data-ready draft can later freeze with
evaluation_ready=false while clearly retaining that missing coverage.

LOMO produces one fold per eligible target-positive underlying match, in intake
order. Each fold has exactly `fold_id` (`lomo_1`, etc.), `train_match_ids`,
`validation_match_ids` (one item), `train_recording_ids`,
`validation_recording_ids`, `train_frames`, and `validation_frames`. Frame entries
are exactly `{recording_id, frame_id}`. Recording order follows intake; frame
order follows the bound frame array within each recording. All retained
recordings/frames of each eligible match, including alternate/pending/excluded
copies, receive one ownership assignment; assignment does not make them training
eligible. Later augmentations inherit this ownership. No frame-level random split
or renamed/reencoded same-match leakage is allowed. For >4 matches all N LOMO
folds are defined; later model stability/acceptance rules remain unapproved.

## Task 3 manual annotation interoperability

`canvas_box_to_normalized(box: tuple[float,float,float,float],
image_size: tuple[int,int], display_rect: tuple[float,float,float,float])
-> list[float]` takes canvas **endpoints** `(x0,y0,x1,y1)`, original rotated
`(width,height)`, and displayed-image `(left,top,width,height)` excluding any
letterbox. The display must preserve the original aspect ratio. Reverse dragging
is accepted; outside endpoints and zero-area boxes reject rather than clip. The
result is `[x,y,width,height]` in the original rotated full-image coordinate space,
not resized bitmap pixels. Decimal rounding at the right/bottom edge is kept
inside the normalized image; this is not clipping outside evidence.

`save_annotation_revision(document: dict, output: Path) -> Path` accepts an
**in-memory request**, exactly `{draft, data_root, annotation_source_id}`;
`data_root` is an explicit absolute `Path` for the data container described above.
This request is not the persisted sidecar schema. `output` is an absolute new
draft `.json` path; its sibling `<output.stem>.units.json` is a new full ordered
label snapshot with the closed sidecar fields described above. Both destinations
must be private artifacts and must not already exist. The writer clones the
draft, remaps only each row's `annotation_source_id` to the requested new identity,
and replaces `annotation_sources` with that one sidecar's relative path and actual
file SHA-256. All other row semantics, frame/deployment IDs, boxes, review states,
array order and retained records are preserved. Changes to `created_at` or
`freeze_version` must be explicit in the input; the writer never changes them.

The complete new draft and sidecar are validated before any file creation.
Exclusive binary writes use canonical JSON plus a newline, without overwriting
originals. A partial failure removes only this operation's newly created pair;
an inability to clean up is reported explicitly. This pure paired writer does not
certify external files or readiness. The saved pair must subsequently pass Task 2
checked loading/binding; a standalone sidecar check is insufficient.

`launch_annotator(draft_path: Path, indexes: dict, output_directory: Path) -> None`
requires the checked context from `load_dataset_indexes`, including its explicit
root and immutable Development Lock file reference. It rechecks disk bindings
before opening Tk and before saving, and checks the new pair after saving. Import
does not create a GUI. The local Pillow/Tk canvas only draws manually requested
visible unit boxes, edits selected per-unit metadata, deletes unsaved new boxes,
records explicit frame review, saves additively, and advances in declared frame
order. It never splits group boxes, guesses source/form, creates deployments, or
freezes a dataset lock. Choosing an existing deployment merely fills its declared
metadata for human review.

One invocation owns one application lifetime. Repeated launches in a shared
Python/Tcl interpreter are not validated. Automated Tk smoke uses a fresh child
process per real application lifetime, not a dummy GUI or human visible-window
review; initialization/callback errors, timeouts, nonzero exits and skipped GUI
cases fail that verification. This does not claim a native Tk runtime repair.

Editing a unit resets its frame to pending/non-exhaustive. Deleting boxes retains
declared presence; it cannot create a negative or an absent interval. A complete
positive frame requires explicit full-image review with all identifiable same-class
units labelled (including own/other-source units) and verified rows. Unknown
potentially unlabelled content remains pending. Semantic source/form uncertainty
may be retained in a verified visible unit without becoming a confirmed target
play. Complete review is a human attestation, not automatically proven by Tk.
Before advancing, the tool applies the explicit current review and validates the
whole updated draft. Contradictory review or invalid unit metadata keeps the same
frame and editable units visible with an error. A structurally valid pending frame
may advance; this check does not force completion or convert uncertainty to absence.
