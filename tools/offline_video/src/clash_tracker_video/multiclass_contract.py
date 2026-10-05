"""Closed, data-only multiclass declarations, not media checks or game events.

Human identity, independence and review are declarations. The checked disk
binding and independently computed readiness belong to separate modules.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from pathlib import Path, PureWindowsPath
from types import UnionType
from typing import Annotated, Literal, Protocol, TypedDict, Union, get_args, get_origin, get_type_hints, is_typeddict

from .evidence_contract import EvidenceError, number, rational, seconds, valid_type
from .evidence_prepare import frame_id
from .experiment_contract import utc_time


Id = Annotated[str, "id"]
ClassId = Annotated[str, "class_id"]
Sha256 = Annotated[str, "hash"]
RelativePath = Annotated[str, "relative_path"]
UtcTime = Annotated[str, "utc_time"]
Number = int | float
Seconds = Annotated[Number, "seconds"]
PositiveInt = Annotated[int, "positive_int"]
NonnegativeInt = Annotated[int, "nonnegative_int"]
Owner = Literal["own", "opponent", "neutral", "unknown"]
Form = Literal["normal", "evolved", "unknown"]
Kind = Literal["unit", "building", "spell_effect", "projectile", "battlefield_object", "ui"]
Mobility = Literal["moving", "static", "unknown"]
OriginKind = Literal["direct", "summoned", "transformed", "unknown"]
Split = Literal["train", "development_validation", "prospective_test"]
DevelopmentSplit = Literal["train", "development_validation"]
Visibility = Literal["none", "partial", "unknown"]
IntakeStatus = Literal["included", "pending", "excluded"]
ScaleGroup = Literal["relative_small", "medium", "large"]
ScalePolicyId = Literal["dev_moving_area_quantiles_v1"]


class Rational(TypedDict):
    numerator: PositiveInt
    denominator: PositiveInt


class ExactRatio(TypedDict):
    numerator: NonnegativeInt
    denominator: PositiveInt


class Box(TypedDict):
    x: Number
    y: Number
    width: Number
    height: Number


NormalizedBox = Annotated[Box, "box"]


class ReviewProvenance(TypedDict):
    method: Literal["manual", "pending"]
    reviewed_by: Id | None
    notes: Id


class VisualClass(TypedDict):
    visual_class_id: ClassId
    kind: Kind
    mobility: Mobility
    definition: Id


class AliasMapping(TypedDict):
    alias: Id
    visual_class_id: ClassId


class Taxonomy(TypedDict):
    taxonomy_id: Id
    version: PositiveInt
    classes: list[VisualClass]
    alias_mapping: list[AliasMapping]


class CoordinatePolicy(TypedDict):
    space: Literal["normalized_full_image"]
    box_extent: Literal["visible"]
    image_basis: Literal["original_rotated"]


class IntakeHistory(TypedDict):
    status: IntakeStatus
    reason: Id


class IntakeRow(TypedDict):
    intake_id: Id
    recording_id: Id
    status: IntakeStatus
    reason: Id
    history: list[IntakeHistory]


class MatchRow(TypedDict):
    underlying_match_id: Id
    provenance: Literal["natural", "unknown"]
    identity_attestation: Literal["human_confirmed", "pending"]
    notes: Id


class MatchSegment(TypedDict):
    start_seconds: Seconds
    end_seconds: Seconds
    complete_match: bool


class ExportReference(TypedDict):
    export_id: Id
    report_path: RelativePath
    index_path: RelativePath
    report_sha256: Sha256
    index_sha256: Sha256


class RecordingRow(TypedDict):
    recording_id: Id
    underlying_match_id: Id
    split: Split
    source_id: Id
    source_sha256: Sha256
    source_path: RelativePath
    perspective_ref: Id
    width: PositiveInt | None
    height: PositiveInt | None
    rotation_degrees: Literal[0, 90, 180, 270] | None
    time_base: Rational | None
    origin_pts: int | None
    origin_time_base: Rational | None
    last_frame_seconds: Seconds | None
    technical_valid: bool
    complete_recording: bool
    unedited_recording: bool
    full_human_review: bool
    completion_attestation: Literal["user_confirmed", "pending"]
    terminal_result_screen_present: bool
    match_segment: MatchSegment | None
    exports: list[ExportReference]
    review_provenance: ReviewProvenance


class GroupRow(TypedDict):
    appearance_group_id: Id
    underlying_match_id: Id
    recording_id: Id
    visual_class_id: ClassId
    owner: Owner
    observed_form: Form
    origin_kind: OriginKind
    causal_root_id: Id
    parent_group_id: Id | None
    entity_occurrence_id: Id | None
    human_deployment_id: Id | None
    independence_attestation: Literal["human_confirmed", "pending"]
    verification_state: Literal["confirmed", "ambiguous", "unreviewed", "rejected"]
    start_seconds: Seconds
    end_seconds: Seconds
    review_provenance: ReviewProvenance


class FrameOrigin(TypedDict):
    raw_pts: int
    time_base: Rational


class FrameRow(TypedDict):
    frame_id: Id
    recording_id: Id
    export_ids: list[Id]
    timestamp_seconds: Seconds
    raw_pts: int
    time_base: Rational
    origin: FrameOrigin
    image_path: RelativePath
    image_width: PositiveInt
    image_height: PositiveInt
    image_sha256: Sha256
    perspective_ref: Id
    perspective_change_reason: Id | None
    review_state: Literal["complete", "pending", "excluded"]
    review_provenance: ReviewProvenance


class AnnotationRow(TypedDict):
    annotation_id: Id
    annotation_source_id: Id
    recording_id: Id
    frame_id: Id
    appearance_group_id: Id | None
    entity_occurrence_id: Id | None
    visual_class_id: ClassId
    owner: Owner
    perspective_ref: Id
    observed_form: Form
    visual_stage: Id | None
    box: NormalizedBox
    source_card_id: Id | None
    source_card_candidates: list[Id]
    mapping_basis: Literal["manual", "external_reference", "unknown"]
    mapping_verification: Literal["verified", "pending"]
    occlusion: Visibility
    truncation: Visibility
    review_state: Literal["verified", "pending"]
    review_provenance: ReviewProvenance


class AnnotationSource(TypedDict):
    annotation_source_id: Id
    path: RelativePath
    sha256: Sha256


class UnknownInterval(TypedDict):
    start_seconds: Seconds
    end_seconds: Seconds
    visual_class_ids: list[ClassId]
    reason: Id


class IgnoreRegion(TypedDict):
    box: NormalizedBox
    visual_class_ids: list[ClassId]
    reason: Id


class CoverageRow(TypedDict):
    coverage_id: Id
    recording_id: Id
    frame_id: Id
    exhaustive_for_classes: list[ClassId]
    exhaustive_state: Literal["complete", "pending"]
    reviewed_regions: list[NormalizedBox]
    unknown_intervals: list[UnknownInterval]
    ignore_regions: list[IgnoreRegion]
    ignore_reasons: list[Id]
    review_provenance: ReviewProvenance


class ProvenanceRow(TypedDict):
    source_id: Id
    creator: Id
    source_url: Id | None
    artifact_kind: Literal["code", "dataset", "game_asset", "model_weight", "recording", "annotation", "synthetic_test"]
    license_evidence: Id | None
    allowed_scope: Literal["reference_only", "development_training", "test_evaluation", "manual_evidence"]


class SplitAssignment(TypedDict):
    underlying_match_id: Id
    split: Split


class ClassDecision(TypedDict):
    visual_class_id: ClassId
    selected: bool
    reason: Id


class Selection(TypedDict):
    selected_class_ids: list[ClassId]
    class_decisions: list[ClassDecision]
    scale_snapshot_digest: Sha256
    policy_id: ScalePolicyId


class BackendLabelMaps(TypedDict):
    yolox: dict[str, int]
    torchvision: dict[str, int]


class EmptyMaps(TypedDict):
    pass


class MulticlassDraft(TypedDict):
    kind: Literal["multiclass_visual_dataset"]
    schema_version: Literal[1]
    dataset_id: Id
    freeze_version: PositiveInt
    created_at: UtcTime
    taxonomy: Taxonomy
    coordinate_policy: CoordinatePolicy
    intake: list[IntakeRow]
    matches: list[MatchRow]
    recordings: list[RecordingRow]
    groups: list[GroupRow]
    frames: list[FrameRow]
    annotations: list[AnnotationRow]
    annotation_sources: list[AnnotationSource]
    coverage: list[CoverageRow]
    provenance: list[ProvenanceRow]
    split_assignment: list[SplitAssignment]
    selection: Selection | None
    backend_label_maps: BackendLabelMaps | EmptyMaps


# Closed output interfaces for the following separately tested tasks. Their
# construction/readiness/digest/disk semantics are not implemented here.
class SupportCounts(TypedDict):
    matches: NonnegativeInt
    groups: NonnegativeInt
    entities: NonnegativeInt
    frames: NonnegativeInt
    boxes: NonnegativeInt


class OwnerSplitSupport(TypedDict):
    owner: Owner
    split: DevelopmentSplit
    underlying_match_ids: list[Id]
    causal_root_ids: list[Id]
    appearance_group_ids: list[Id]
    frame_ids: list[Id]
    annotation_ids: list[Id]
    counts: SupportCounts
    qualification: Literal["qualified", "not_qualified"]
    evaluation: Literal["not_evaluated"]
    reasons: list[Id]


class CandidateClassReport(TypedDict):
    visual_class_id: ClassId
    kind: Kind
    mobility: Mobility
    basic_qualified: bool
    reasons: list[Id]
    support: list[OwnerSplitSupport]


class CandidateReport(TypedDict):
    qualified_class_ids: list[ClassId]
    class_reports: list[CandidateClassReport]
    development_match_ids: list[Id]
    primary_recording_ids: list[Id]
    reasons: list[Id]


class QuantileStatistics(TypedDict):
    count: NonnegativeInt
    min: ExactRatio | None
    p10: ExactRatio | None
    p50: ExactRatio | None
    p90: ExactRatio | None
    max: ExactRatio | None


class BoxStatistics(TypedDict):
    width_px: QuantileStatistics
    height_px: QuantileStatistics
    short_side_px: QuantileStatistics
    area_norm: QuantileStatistics


class ResolutionCount(TypedDict):
    width: PositiveInt
    height: PositiveInt
    frames: NonnegativeInt


class ReasonCount(TypedDict):
    reason: Id
    count: NonnegativeInt


class ScaleGroupSupport(TypedDict):
    underlying_match_id: Id
    appearance_group_id: Id
    causal_root_id: Id
    owner: Owner
    clean_frame_ids: list[Id]
    clean_annotation_ids: list[Id]
    score: ExactRatio | None


class ScaleClassReport(TypedDict):
    visual_class_id: ClassId
    basic_qualified: bool
    scale_support_pending: bool
    score: ExactRatio | None
    scale_group: ScaleGroup | None
    all_reviewed: BoxStatistics
    clean_representatives: BoxStatistics
    resolution_distribution: list[ResolutionCount]
    excluded_reasons: list[ReasonCount]
    support: list[ScaleGroupSupport]


class ScaleCutpoints(TypedDict):
    q25: ExactRatio | None
    q75: ExactRatio | None


class ScaleReport(TypedDict):
    policy_id: ScalePolicyId
    candidate_class_ids: list[ClassId]
    candidate_semantic_sha256: Sha256
    split_semantic_sha256: Sha256
    class_reports: list[ScaleClassReport]
    cutpoints: ScaleCutpoints
    tie_fallback_used: bool
    size_coverage_status: Literal["SIZE_COVERAGE_SUFFICIENT", "SIZE_COVERAGE_INSUFFICIENT"]
    blocking_reasons: list[Id]


class JointExportSupport(TypedDict):
    joint_label: Id
    visual_class_id: ClassId
    owner: Literal["own", "opponent"]
    support: list[OwnerSplitSupport]


class ReadinessReport(TypedDict):
    status: Literal["MULTICLASS_DATASET_READY", "DATA_INSUFFICIENT", "SIZE_COVERAGE_INSUFFICIENT", "PROVENANCE_INSUFFICIENT", "INVALID_DATASET"]
    ready: bool
    blocking_reasons: list[Id]
    candidate_report: CandidateReport
    scale_report: ScaleReport
    export_support: list[JointExportSupport]


class CheckedMediaSnapshot(TypedDict):
    recording: RecordingRow
    frames: list[FrameRow]


class CheckedLabelSnapshot(TypedDict):
    annotation_source: AnnotationSource
    annotations: list[AnnotationRow]


class BoundMulticlass(Protocol):
    """Typing-only interface; Task 3 must supply an opaque checked factory."""
    draft: MulticlassDraft
    media_snapshot: list[CheckedMediaSnapshot]
    label_snapshot: list[CheckedLabelSnapshot]
    file_hashes: dict[str, str]
    semantic_sha256: str
    data_root: Path


class ScaleSnapshotPayload(TypedDict):
    draft: MulticlassDraft
    draft_semantic_sha256: Sha256
    candidate_report: CandidateReport
    scale_report: ScaleReport


class ScaleSnapshot(TypedDict):
    kind: Literal["multiclass_scale_snapshot"]
    version: Literal[1]
    id: Id
    created_at: UtcTime
    payload: ScaleSnapshotPayload
    digest: Sha256


class MulticlassLockPayload(TypedDict):
    draft: MulticlassDraft
    draft_semantic_sha256: Sha256
    scale_snapshot: ScaleSnapshot
    readiness: ReadinessReport
    media_snapshot: list[CheckedMediaSnapshot]
    label_snapshot: list[CheckedLabelSnapshot]


class MulticlassLock(TypedDict):
    kind: Literal["multiclass_dataset_lock"]
    version: Literal[1]
    id: Id
    created_at: UtcTime
    payload: MulticlassLockPayload
    digest: Sha256


class FrameTransform(TypedDict):
    original_width: PositiveInt
    original_height: PositiveInt
    offset_x: Number
    offset_y: Number
    scale_x: Number
    scale_y: Number
    output_width: PositiveInt
    output_height: PositiveInt
    rotation_degrees: Literal[0, 90, 180, 270]


class ExportFrame(TypedDict):
    frame_id: Id
    recording_id: Id
    split: DevelopmentSplit
    status: Literal["exported", "pending", "excluded"]
    reasons: list[Id]
    original_sha256: Sha256
    image_path: RelativePath | None
    label_path: RelativePath | None
    label_sha256: Sha256 | None
    transform: FrameTransform | None


class ExportManifest(TypedDict):
    dataset_digest: Sha256
    backend: Literal["yolox", "torchvision"]
    joint_label_map: dict[str, int]
    frames: list[ExportFrame]
    reasons: list[ReasonCount]
    counts: SupportCounts


def _fail(message="Invalid multiclass field type, value or closed object."):
    raise EvidenceError(message)


def _relative_path(value):
    return (type(value) is str and bool(value.strip()) and "\\" not in value
            and ":" not in value and not value.startswith("/") and not PureWindowsPath(value).drive
            and all(part not in {"", ".", ".."} for part in value.split("/")))


@lru_cache(maxsize=None)
def _fields(schema):
    return get_type_hints(schema, include_extras=True)


def _validate_types(value, schema):
    """Check closed runtime JSON types; bool is never an int/number/literal 1."""
    origin, args = get_origin(schema), get_args(schema)
    if origin is Annotated:
        _validate_types(value, args[0])
        tag = args[1]
        valid = {
            "id": lambda: bool(value.strip()),
            "class_id": lambda: bool(value) and "::" not in value and not any(c.isspace() for c in value),
            "hash": lambda: valid_type(value, "hash"),
            "relative_path": lambda: _relative_path(value),
            "positive_int": lambda: value > 0,
            "nonnegative_int": lambda: value >= 0,
            "seconds": lambda: value >= 0,
            "box": lambda: valid_type(value, "box"),
        }
        if tag == "utc_time":
            utc_time(value)
        elif not valid[tag]():
            _fail()
    elif origin in (Union, UnionType):
        for option in args:
            try:
                _validate_types(value, option)
                return
            except EvidenceError:
                pass
        _fail()
    elif origin is Literal:
        if not any(type(value) is type(option) and value == option for option in args):
            _fail()
    elif is_typeddict(schema):
        fields = _fields(schema)
        if type(value) is not dict or set(value) != set(fields):
            _fail()
        for key, item_schema in fields.items():
            _validate_types(value[key], item_schema)
    elif origin is list:
        if type(value) is not list:
            _fail()
        for item in value:
            _validate_types(item, args[0])
    elif origin is dict:
        if type(value) is not dict:
            _fail()
        for key, item in value.items():
            _validate_types(key, args[0])
            _validate_types(item, args[1])
    elif schema is type(None):
        if value is not None:
            _fail()
    elif type(value) is not schema or (schema in (int, float) and not number(value)):
        _fail()


def _unique(rows, key):
    indexed = {}
    for row in rows:
        identity = key(row)
        if identity in indexed:
            _fail("Duplicate multiclass identity or declared observation.")
        indexed[identity] = row
    return indexed


def _ids(values):
    if len(set(values)) != len(values):
        _fail("Duplicate multiclass identity in an array.")


def _review(review, required):
    if required and (review["method"] != "manual" or review["reviewed_by"] is None):
        _fail("Explicit manual review declaration required.")


def _range(start, end, last):
    if last is None or not 0 <= seconds(start) < seconds(end) <= seconds(last):
        _fail("Declared interval outside actual recording boundary.")


def _split_relations(draft):
    matches = _unique(draft["matches"], lambda r: r["underlying_match_id"])
    assignments = _unique(draft["split_assignment"], lambda r: r["underlying_match_id"])
    records = _unique(draft["recordings"], lambda r: r["recording_id"])
    if set(assignments) != set(matches):
        _fail("Whole-match split assignment must cover the match inventory exactly.")
    for record in records.values():
        match_id = record["underlying_match_id"]
        if match_id not in assignments or record["split"] != assignments[match_id]["split"]:
            _fail("All recordings and derivatives of one match must inherit one split.")


def validate_match_splits(draft: MulticlassDraft) -> None:
    """Validate declared whole-match ownership, never infer match identity."""
    _validate_types(draft, MulticlassDraft)
    _split_relations(draft)


def backend_label_maps(selected_class_ids: list[str]) -> dict[str, dict[str, int]]:
    """Stable (class, owner) labels; TorchVision reserves 0 for background."""
    _validate_types(selected_class_ids, list[ClassId])
    _ids(selected_class_ids)
    if not selected_class_ids:
        _fail("Joint maps require a nonempty selected class set.")
    labels = [f"{cid}::{owner}" for cid in sorted(selected_class_ids) for owner in ("opponent", "own")]
    return {"yolox": {label: index for index, label in enumerate(labels)},
            "torchvision": {label: index + 1 for index, label in enumerate(labels)}}


def validate_multiclass_shape(draft: MulticlassDraft) -> None:
    """Pure closed shape/relation validation; valid drafts may be unready."""
    _validate_types(draft, MulticlassDraft)
    _split_relations(draft)
    classes = _unique(draft["taxonomy"]["classes"], lambda r: r["visual_class_id"])
    if not classes:
        _fail("Taxonomy must declare at least one visual class.")
    aliases = _unique(draft["taxonomy"]["alias_mapping"], lambda r: r["alias"])
    if any(row["visual_class_id"] not in classes for row in aliases.values()):
        _fail("Taxonomy alias lacks a canonical class reference.")
    _unique(draft["intake"], lambda r: r["intake_id"])
    intake = _unique(draft["intake"], lambda r: r["recording_id"])
    matches = {r["underlying_match_id"]: r for r in draft["matches"]}
    recordings = {r["recording_id"]: r for r in draft["recordings"]}
    provenance = _unique(draft["provenance"], lambda r: r["source_id"])
    if set(recordings) != set(intake) or set(matches) != {r["underlying_match_id"] for r in recordings.values()}:
        _fail("Match, recording and original intake inventories conflict.")
    media_fields = ("width", "height", "rotation_degrees", "time_base", "origin_pts", "origin_time_base", "last_frame_seconds")
    source_matches = {}
    for rid, record in recordings.items():
        if record["source_id"] not in provenance or not record["source_path"].endswith(".mp4"):
            _fail("Recording lacks source provenance or local MP4 declaration.")
        mid = record["underlying_match_id"]
        prior = source_matches.setdefault(record["source_sha256"], mid)
        if prior != mid:
            _fail("Identical source bytes cannot establish two independent matches.")
        if record["technical_valid"] and any(record[key] is None for key in media_fields):
            _fail("Technically valid recording needs complete actual metadata.")
        exports = _unique(record["exports"], lambda r: r["export_id"])
        for export in exports.values():
            if any(not export[key].endswith(".json") for key in ("report_path", "index_path")):
                _fail("Export references must name relative JSON files.")
        segment = record["match_segment"]
        if segment is not None:
            _range(segment["start_seconds"], segment["end_seconds"], record["last_frame_seconds"])
            if record["completion_attestation"] == "user_confirmed" and segment["complete_match"]:
                if segment["start_seconds"] != 0 or seconds(segment["end_seconds"]) != seconds(record["last_frame_seconds"]):
                    _fail("User-confirmed complete match must use the entire actual file boundary.")
        included = intake[rid]["status"] == "included"
        _review(record["review_provenance"], included)
        if included and (record["split"] == "prospective_test"
                         or not all(record[key] for key in ("technical_valid", "complete_recording", "unedited_recording", "full_human_review"))
                         or record["completion_attestation"] != "user_confirmed" or segment is None
                         or not segment["complete_match"] or not exports
                         or matches[mid]["provenance"] != "natural" or matches[mid]["identity_attestation"] != "human_confirmed"):
            _fail("Included development source needs an attested full natural match.")
    sources = _unique(draft["annotation_sources"], lambda r: r["annotation_source_id"])
    _unique(draft["annotation_sources"], lambda r: r["path"])
    if any(not row["path"].endswith(".json") for row in sources.values()):
        _fail("Annotation sources must name relative JSON files.")
    groups = _validate_groups(draft, recordings, classes)
    frames = _validate_frames(draft, recordings)
    annotations_by_frame = _validate_annotations(draft, recordings, classes, sources, groups, frames)
    _validate_coverage(draft, recordings, classes, frames, annotations_by_frame)
    _validate_selection(draft, classes)


def _validate_groups(draft, recordings, classes):
    groups = _unique(draft["groups"], lambda r: r["appearance_group_id"])
    roots = []
    for gid, group in groups.items():
        record = recordings.get(group["recording_id"])
        if record is None or group["underlying_match_id"] != record["underlying_match_id"] or group["visual_class_id"] not in classes:
            _fail("Appearance group has conflicting match, recording or class reference.")
        _range(group["start_seconds"], group["end_seconds"], record["last_frame_seconds"])
        _review(group["review_provenance"], group["verification_state"] == "confirmed"
                or group["independence_attestation"] == "human_confirmed")
        root = groups.get(group["causal_root_id"])
        if root is None or root["parent_group_id"] is not None or root["causal_root_id"] != root["appearance_group_id"]:
            _fail("Causal root must name an actual root appearance group.")
        if root["underlying_match_id"] != group["underlying_match_id"]:
            _fail("A causal chain cannot cross underlying matches.")
        parent_id = group["parent_group_id"]
        if parent_id is None:
            if group["causal_root_id"] != gid:
                _fail("A root group must retain its own causal identity.")
            roots.append(group)
        else:
            parent = groups.get(parent_id)
            if parent is None or parent["underlying_match_id"] != group["underlying_match_id"] or parent["causal_root_id"] != group["causal_root_id"]:
                _fail("Derived appearance must inherit the same match and cause.")
            if group["origin_kind"] == "direct":
                _fail("Direct appearance cannot declare a causal parent.")
        visited = {gid}
        current = group
        while current["parent_group_id"] is not None:
            parent_id = current["parent_group_id"]
            if parent_id in visited:
                _fail("Appearance parent links must be acyclic.")
            visited.add(parent_id)
            parent = groups.get(parent_id)
            if parent is None:
                _fail("Appearance ancestor lacks an existing group reference.")
            current = parent
    _unique([r for r in roots if r["human_deployment_id"] is not None],
            lambda r: (r["underlying_match_id"], r["human_deployment_id"]))
    _unique([r for r in roots if r["entity_occurrence_id"] is not None],
            lambda r: (r["underlying_match_id"], r["entity_occurrence_id"]))
    _unique(roots, lambda r: (r["underlying_match_id"], r["visual_class_id"], r["owner"], r["observed_form"],
                            r["origin_kind"], seconds(r["start_seconds"]), seconds(r["end_seconds"])))
    return groups


def _validate_frames(draft, recordings):
    frames = _unique(draft["frames"], lambda r: r["frame_id"])
    _unique(draft["frames"], lambda r: (r["recording_id"], r["raw_pts"] * rational(r["time_base"])))
    for frame in frames.values():
        record = recordings.get(frame["recording_id"])
        if record is None or not record["technical_valid"]:
            _fail("Frame lacks technically valid recording metadata.")
        origin = frame["origin"]
        if origin["raw_pts"] != record["origin_pts"] or rational(origin["time_base"]) != rational(record["origin_time_base"]):
            _fail("Frame origin differs from the recording origin.")
        actual = frame["raw_pts"] * rational(frame["time_base"]) - origin["raw_pts"] * rational(origin["time_base"])
        if actual < 0 or abs(actual - seconds(frame["timestamp_seconds"])) > Fraction(1, 1000000) or float(actual) > record["last_frame_seconds"]:
            _fail("Frame timestamp disagrees with actual PTS or recording boundary.")
        if frame["frame_id"] != frame_id(frame["recording_id"], frame["raw_pts"], rational(frame["time_base"])):
            _fail("Frame identity must use the canonical actual recording PTS.")
        dimensions = (record["width"], record["height"])
        if record["rotation_degrees"] in (90, 270):
            dimensions = dimensions[::-1]
        if (frame["image_width"], frame["image_height"]) != dimensions or not frame["image_path"].endswith(".png"):
            _fail("Frame must declare the rotated full original PNG dimensions.")
        _ids(frame["export_ids"])
        if not frame["export_ids"] or not set(frame["export_ids"]) <= {r["export_id"] for r in record["exports"]}:
            _fail("Frame lacks an existing export declaration.")
        if frame["perspective_ref"] != record["perspective_ref"] and frame["perspective_change_reason"] is None:
            _fail("Changed owner perspective requires an explicit declaration.")
        _review(frame["review_provenance"], frame["review_state"] == "complete")
    return frames


def _validate_annotations(draft, recordings, classes, sources, groups, frames):
    _unique(draft["annotations"], lambda r: r["annotation_id"])
    _unique(draft["annotations"], lambda r: (r["frame_id"], tuple(seconds(r["box"][key]) for key in ("x", "y", "width", "height"))))
    _unique([r for r in draft["annotations"] if r["entity_occurrence_id"] is not None],
            lambda r: (r["frame_id"], r["entity_occurrence_id"]))
    result = {fid: [] for fid in frames}
    entity_causes = {}
    for annotation in draft["annotations"]:
        frame = frames.get(annotation["frame_id"])
        if (frame is None or frame["recording_id"] != annotation["recording_id"]
                or annotation["visual_class_id"] not in classes or annotation["annotation_source_id"] not in sources
                or annotation["perspective_ref"] != frame["perspective_ref"]):
            _fail("Observation lacks consistent frame, source, class or perspective reference.")
        _ids(annotation["source_card_candidates"])
        if (annotation["source_card_id"] is not None and annotation["source_card_id"] not in annotation["source_card_candidates"]):
            _fail("Verified or tentative source card must remain in its declared candidates.")
        if annotation["mapping_verification"] == "verified" and (annotation["source_card_id"] is None or annotation["mapping_basis"] == "unknown"):
            _fail("Verified card mapping requires known identity and evidence basis.")
        _review(annotation["review_provenance"], annotation["review_state"] == "verified")
        group_id = annotation["appearance_group_id"]
        if group_id is not None:
            group = groups.get(group_id)
            record = recordings[annotation["recording_id"]]
            if (group is None or group["underlying_match_id"] != record["underlying_match_id"]
                    or any(group[key] != annotation[key] for key in ("visual_class_id", "owner", "observed_form"))):
                _fail("Observation conflicts with its appearance-group declaration.")
            if group["recording_id"] == annotation["recording_id"]:
                actual = (frame["raw_pts"] * rational(frame["time_base"])
                          - record["origin_pts"] * rational(record["origin_time_base"]))
                instant = seconds(float(actual))
                start, end = seconds(group["start_seconds"]), seconds(group["end_seconds"])
                terminal = (float(actual) == record["last_frame_seconds"]
                            and end == seconds(record["last_frame_seconds"]))
                if not (start <= instant < end or terminal):
                    _fail("Observation lies outside its declared appearance interval.")
            entity = annotation["entity_occurrence_id"]
            if entity is not None:
                key = (record["underlying_match_id"], entity)
                prior = entity_causes.setdefault(key, group["causal_root_id"])
                if prior != group["causal_root_id"]:
                    _fail("Known entity cannot be renamed into another independent cause.")
                if group["entity_occurrence_id"] is not None and group["entity_occurrence_id"] != entity:
                    _fail("Observation entity differs from its singleton appearance group.")
        result[annotation["frame_id"]].append(annotation)
    return result


def _validate_coverage(draft, recordings, classes, frames, annotations_by_frame):
    _unique(draft["coverage"], lambda r: r["coverage_id"])
    coverage = _unique(draft["coverage"], lambda r: r["frame_id"])
    for fid, row in coverage.items():
        frame = frames.get(fid)
        if frame is None or frame["recording_id"] != row["recording_id"]:
            _fail("Coverage lacks consistent frame and recording identity.")
        _ids(row["exhaustive_for_classes"])
        if not set(row["exhaustive_for_classes"]) <= set(classes):
            _fail("Coverage names an unknown visual class.")
        _review(row["review_provenance"], row["exhaustive_state"] == "complete")
        if row["exhaustive_state"] == "complete" and (not row["reviewed_regions"]
                or any(r["review_state"] != "verified" for r in annotations_by_frame[fid]
                       if r["visual_class_id"] in row["exhaustive_for_classes"])):
            _fail("Exhaustive class coverage requires reviewed regions and verified observations.")
        for interval in row["unknown_intervals"]:
            _range(interval["start_seconds"], interval["end_seconds"], recordings[row["recording_id"]]["last_frame_seconds"])
            _ids(interval["visual_class_ids"])
            if not set(interval["visual_class_ids"]) <= set(classes):
                _fail("Unknown interval names an unknown visual class.")
        for region in row["ignore_regions"]:
            _ids(region["visual_class_ids"])
            if not set(region["visual_class_ids"]) <= set(classes):
                _fail("Ignore region names an unknown visual class.")
        _ids(row["ignore_reasons"])
    if any(frame["review_state"] == "complete" and (fid not in coverage or coverage[fid]["exhaustive_state"] != "complete")
           for fid, frame in frames.items()):
        _fail("Complete frames require an explicit exhaustive class-coverage declaration.")


def _validate_selection(draft, classes):
    selection = draft["selection"]
    if selection is None:
        if draft["backend_label_maps"]:
            _fail("Unselected draft cannot lock backend labels.")
        return
    selected = selection["selected_class_ids"]
    _ids(selected)
    decisions = _unique(selection["class_decisions"], lambda r: r["visual_class_id"])
    if (not set(selected) <= set(classes) or set(decisions) != set(classes)
            or set(selected) != {cid for cid, row in decisions.items() if row["selected"]}):
        _fail("Selection must declare consistent decisions for every taxonomy class.")
    if draft["backend_label_maps"] != backend_label_maps(selected):
        _fail("Selected joint labels must match both locked backend maps.")
