"""Closed local unit-dataset v1, with human-attested independent evidence.

This validates declared snapshots, not the external files or human authenticity.
No observation in this module is a runtime OpponentCardPlayed event.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import PureWindowsPath

from .evidence_contract import EvidenceError, rational, seconds, valid_type
from .experiment_contract import utc_time


ROOT_FIELDS = {
    "schema_version", "dataset_id", "freeze_version", "created_at",
    "development_lock_sha256", "target", "visual_class", "coordinate_policy",
    "intake", "matches", "recordings", "deployments", "frames", "unit_annotations",
    "unknown_intervals", "confirmed_absent_intervals", "annotation_sources",
}
OWNER = {"opponent", "own", "unknown"}
FORM = {"normal", "evolved", "unknown"}
STATUS = {"included", "pending", "excluded"}
VISIBILITY = {"none", "partial", "unknown"}
RECORDING_SCHEMA = {
    "recording_id": "id", "underlying_match_id": "id", "source_sha256": "hash", "source_path": "id",
    "width": "positive_int", "height": "positive_int", "rotation_degrees": {0, 90, 180, 270},
    "time_base": "rational", "origin_pts": "int", "origin_time_base": "rational",
    "last_frame_seconds": "seconds", "technical_valid": "bool", "complete_recording": "bool",
    "unedited_recording": "bool", "full_human_review": "bool",
    "completion_attestation": {"user_confirmed", "pending"},
    "terminal_result_screen_present": "bool",
}
DEPLOYMENT_SCHEMA = {
    "deployment_id": "id", "underlying_match_id": "id", "recording_id": "id",
    "owner": OWNER, "source_card": "id", "form": FORM,
    "verification_status": {"confirmed", "ambiguous", "unreviewed", "rejected"},
    "independence_attestation": {"human_confirmed", "pending"},
    "onset_lower_seconds": "seconds", "onset_seconds": "seconds", "onset_upper_seconds": "seconds",
    "visible_start_seconds": "seconds", "visible_end_seconds": "seconds",
    "occlusion": VISIBILITY, "truncation": VISIBILITY,
}
FRAME_SCHEMA = {
    "frame_id": "id", "recording_id": "id", "export_ids": "ids",
    "timestamp_seconds": "seconds", "raw_pts": "int", "time_base": "rational",
    "image_path": "png", "image_width": "positive_int", "image_height": "positive_int",
    "image_sha256": "hash", "review_status": {"complete", "pending", "excluded"},
    "minion_presence": {"positive", "absent", "unknown"}, "all_identifiable_units_labelled": "bool",
}
ANNOTATION_SCHEMA = {
    "annotation_id": "id", "annotation_source_id": "id", "recording_id": "id", "frame_id": "id",
    "deployment_id": "nullable_id", "owner": OWNER, "source_card": "id", "form": FORM,
    "visual_class": {"minion_unit"}, "normalized_bbox": "box", "occlusion": VISIBILITY,
    "truncation": VISIBILITY, "review_status": {"verified", "pending"},
}
MEDIA_FIELDS = {"width", "height", "rotation_degrees", "time_base", "origin_pts",
                "origin_time_base", "last_frame_seconds"}


def _object(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise EvidenceError("Invalid dataset object fields.")


def _typed(value, schema, extra=()):
    _object(value, set(schema) | set(extra))
    if any(not valid_type(value[field], kind) for field, kind in schema.items()):
        raise EvidenceError("Invalid dataset field type or value.")


def _array(value):
    if type(value) is not list:
        raise EvidenceError("Dataset collection must be an array.")
    return value


def _unique(rows, key):
    result = {}
    for row in rows:
        identity = key(row)
        if identity in result:
            raise EvidenceError("Duplicate dataset identity.")
        result[identity] = row
    return result


def _review(value, *, complete=False):
    _typed(value, {"method": {"manual", "pending"}, "reviewed_by": "nullable_id", "notes": "id"})
    if complete and (value["method"] != "manual" or value["reviewed_by"] is None):
        raise EvidenceError("Explicit manual review provenance required.")


def _relative_path(value):
    return (type(value) is str and bool(value.strip()) and "\\" not in value
            and ":" not in value and not value.startswith("/") and not PureWindowsPath(value).drive
            and all(part not in {"", ".", ".."} for part in value.split("/")))


def _range(row, last):
    start, end = seconds(row["start_seconds"]), seconds(row["end_seconds"])
    if not 0 <= start < end <= seconds(last):
        raise EvidenceError("Dataset interval outside recording.")
    return start, end


def _overlaps(left, right):
    return left[0] < right[1] and right[0] < left[1]


def _at(timestamp, interval, last):
    return interval[0] <= timestamp and (timestamp < interval[1]
                                        or timestamp == interval[1] == seconds(last))


def _maps(draft):
    recordings = {r["recording_id"]: r for r in draft["recordings"]}
    frames = {(f["recording_id"], f["frame_id"]): f for f in draft["frames"]}
    deployments = {(d["underlying_match_id"], d["deployment_id"]): d for d in draft["deployments"]}
    included = {i["recording_id"] for i in draft["intake"] if i["status"] == "included"}
    return recordings, frames, deployments, included


def validate_dataset_shape(draft: dict) -> None:
    """Raise path-free EvidenceError for malformed/contradictory declared evidence."""
    _object(draft, ROOT_FIELDS)
    _typed({key: draft[key] for key in ("schema_version", "dataset_id", "freeze_version",
                                      "development_lock_sha256", "visual_class")}, {
        "schema_version": {1}, "dataset_id": "id", "freeze_version": "positive_int",
        "development_lock_sha256": "hash", "visual_class": {"minion_unit"},
    })
    utc_time(draft["created_at"])
    _typed(draft["target"], {"card_id": {"minions"}, "owner": {"opponent"}, "form": {"normal"}})
    _typed(draft["coordinate_policy"], {"space": {"normalized_full_image"}, "box_extent": {"visible"},
                                         "image_basis": {"original_rotated"}})
    for name in ROOT_FIELDS - {"schema_version", "dataset_id", "freeze_version", "created_at",
                               "development_lock_sha256", "target", "visual_class", "coordinate_policy"}:
        _array(draft[name])
    for item in draft["intake"]:
        _typed(item, {"intake_id": "id", "recording_id": "id", "status": STATUS, "reason": "id"}, {"history"})
        for history in _array(item["history"]):
            _typed(history, {"status": STATUS, "reason": "id"})
    _unique(draft["intake"], lambda i: i["intake_id"])
    intake = _unique(draft["intake"], lambda i: i["recording_id"])
    for match in draft["matches"]:
        _typed(match, {"underlying_match_id": "id", "provenance": {"natural", "unknown"},
                       "identity_attestation": {"human_confirmed", "pending"}, "notes": "id"})
    matches = _unique(draft["matches"], lambda m: m["underlying_match_id"])
    for record in draft["recordings"]:
        # Undecodable retained inputs may explicitly lack technical metadata.
        schema = dict(RECORDING_SCHEMA)
        if type(record) is dict and record.get("technical_valid") is False:
            schema = {key: kind for key, kind in schema.items() if key not in MEDIA_FIELDS}
        _typed(record, schema, {"exports", "complete_segment", "review_provenance"} | MEDIA_FIELDS)
        if not _relative_path(record["source_path"]):
            raise EvidenceError("Invalid root-relative source path.")
        for field in MEDIA_FIELDS:
            if record[field] is not None and not valid_type(record[field], RECORDING_SCHEMA[field]):
                raise EvidenceError("Invalid dataset media metadata.")
        export_rows = _array(record["exports"])
        for export in export_rows:
            _typed(export, {"export_id": "id", "report_sha256": "hash", "index_sha256": "hash",
                            "report_path": "id", "index_path": "id"})
            if any(not _relative_path(export[key]) or not export[key].endswith(".json")
                   for key in ("report_path", "index_path")):
                raise EvidenceError("Invalid root-relative export JSON path.")
        _unique(export_rows, lambda e: e["export_id"])
        if record["complete_segment"] is not None:
            _typed(record["complete_segment"], {"start_seconds": "seconds", "end_seconds": "seconds"})
            if record["last_frame_seconds"] is None:
                raise EvidenceError("Segment needs actual recording boundary.")
            _range(record["complete_segment"], record["last_frame_seconds"])
        if record["underlying_match_id"] not in matches or record["recording_id"] not in intake:
            raise EvidenceError("Recording lacks match or original intake identity.")
        is_included = intake[record["recording_id"]]["status"] == "included"
        _review(record["review_provenance"], complete=is_included)
        if is_included:
            match = matches[record["underlying_match_id"]]
            segment = record["complete_segment"]
            if (not all(record[field] for field in ("technical_valid", "complete_recording",
                                                    "unedited_recording", "full_human_review"))
                    or record["completion_attestation"] != "user_confirmed"
                    or match["provenance"] != "natural" or match["identity_attestation"] != "human_confirmed"
                    or not export_rows or segment is None or segment["start_seconds"] != 0
                    or seconds(segment["end_seconds"]) != seconds(record["last_frame_seconds"])):
                raise EvidenceError("Included source needs a valid full-file natural-match review.")
    recordings = _unique(draft["recordings"], lambda r: r["recording_id"])
    if set(recordings) != set(intake) or set(matches) != {r["underlying_match_id"] for r in recordings.values()}:
        raise EvidenceError("Intake, recording and match inventory conflict.")
    source_matches = {}
    for record in recordings.values():
        prior = source_matches.setdefault(record["source_sha256"], record["underlying_match_id"])
        if prior != record["underlying_match_id"]:
            raise EvidenceError("Identical source cannot claim separate underlying matches.")
    for source in draft["annotation_sources"]:
        _typed(source, {"annotation_source_id": "id", "path": "id", "sha256": "hash"})
        if not _relative_path(source["path"]) or not source["path"].endswith(".json"):
            raise EvidenceError("Invalid relative annotation JSON path.")
    sources = _unique(draft["annotation_sources"], lambda a: a["annotation_source_id"])
    _unique(draft["annotation_sources"], lambda a: a["path"])
    for deployment in draft["deployments"]:
        _typed(deployment, DEPLOYMENT_SCHEMA, {"review_provenance"})
        _review(deployment["review_provenance"], complete=deployment["verification_status"] == "confirmed")
        record = recordings.get(deployment["recording_id"])
        if record is None or record["underlying_match_id"] != deployment["underlying_match_id"] or record["last_frame_seconds"] is None:
            raise EvidenceError("Deployment recording/match reference conflict.")
        ordered = [0, *(deployment[key] for key in ("onset_lower_seconds", "onset_seconds", "onset_upper_seconds",
                                                    "visible_start_seconds", "visible_end_seconds")), record["last_frame_seconds"]]
        if any(seconds(a) > seconds(b) for a, b in zip(ordered, ordered[1:])) or deployment["visible_start_seconds"] >= deployment["visible_end_seconds"]:
            raise EvidenceError("Invalid deployment onset/visibility ordering.")
    deployments = _unique(draft["deployments"], lambda d: (d["underlying_match_id"], d["deployment_id"]))
    _unique(draft["deployments"], lambda d: (d["underlying_match_id"], d["owner"], d["source_card"], d["form"],
                                           *(seconds(d[k]) for k in ("onset_lower_seconds", "onset_seconds", "onset_upper_seconds"))))
    for frame in draft["frames"]:
        _typed(frame, FRAME_SCHEMA, {"review_provenance"})
        _review(frame["review_provenance"], complete=frame["review_status"] == "complete")
        record = recordings.get(frame["recording_id"])
        if record is None or any(record[field] is None for field in MEDIA_FIELDS):
            raise EvidenceError("Frame lacks actual recording metadata.")
        if not frame["export_ids"] or not set(frame["export_ids"]) <= {e["export_id"] for e in record["exports"]}:
            raise EvidenceError("Frame lacks declared export binding.")
        actual = frame["raw_pts"] * rational(frame["time_base"]) - record["origin_pts"] * rational(record["origin_time_base"])
        if not 0 <= actual <= seconds(record["last_frame_seconds"]) or abs(actual - seconds(frame["timestamp_seconds"])) > Fraction(1, 1000000):
            raise EvidenceError("Frame PTS/time mismatch.")
        dimensions = (record["width"], record["height"])
        if record["rotation_degrees"] in {90, 270}:
            dimensions = dimensions[::-1]
        if (frame["image_width"], frame["image_height"]) != dimensions:
            raise EvidenceError("Frame original rotated dimensions conflict.")
    frames = _unique(draft["frames"], lambda f: (f["recording_id"], f["frame_id"]))
    _unique(draft["frames"], lambda f: (f["recording_id"], f["raw_pts"] * rational(f["time_base"])))
    annotations_by_frame = {key: [] for key in frames}
    for annotation in draft["unit_annotations"]:
        _typed(annotation, ANNOTATION_SCHEMA)
        key = annotation["recording_id"], annotation["frame_id"]
        if key not in frames or annotation["annotation_source_id"] not in sources:
            raise EvidenceError("Unit annotation lacks frame/revision binding.")
        record = recordings[annotation["recording_id"]]
        if annotation["deployment_id"] is not None:
            deployment = deployments.get((record["underlying_match_id"], annotation["deployment_id"]))
            if deployment is None or any(annotation[k] != deployment[k] for k in ("owner", "source_card", "form")):
                raise EvidenceError("Unit deployment identity/semantics conflict.")
            timestamp = seconds(frames[key]["timestamp_seconds"])
            if (annotation["recording_id"] == deployment["recording_id"]
                    and not seconds(deployment["visible_start_seconds"]) <= timestamp < seconds(deployment["visible_end_seconds"])):
                raise EvidenceError("Unit frame outside deployment visibility.")
        elif annotation["owner"] == "opponent" and annotation["source_card"] == "minions" and annotation["form"] == "normal":
            raise EvidenceError("Ordinary opponent target unit requires deployment evidence.")
        annotations_by_frame[key].append(annotation)
    _unique(draft["unit_annotations"], lambda a: a["annotation_id"])
    _unique(draft["unit_annotations"], lambda a: (a["recording_id"], a["frame_id"],
                                                tuple(seconds(a["normalized_bbox"][k]) for k in ("x", "y", "width", "height"))))
    intervals = {"unknown_intervals": {}, "confirmed_absent_intervals": {}}
    for name in intervals:
        for interval in draft[name]:
            _typed(interval, {"interval_id": "id", "recording_id": "id", "start_seconds": "seconds", "end_seconds": "seconds"},
                   {"reason"} if name == "unknown_intervals" else {"review_provenance"})
            if name == "unknown_intervals":
                if not valid_type(interval["reason"], "id"):
                    raise EvidenceError("Unknown interval needs retained reason.")
            else:
                _review(interval["review_provenance"], complete=True)
            record = recordings.get(interval["recording_id"])
            if record is None or record["last_frame_seconds"] is None:
                raise EvidenceError("Interval lacks recording boundary.")
            interval_range = _range(interval, record["last_frame_seconds"])
            intervals[name].setdefault(interval["recording_id"], []).append(interval_range)
        _unique(draft[name], lambda i: i["interval_id"])
    for rid, absent_ranges in intervals["confirmed_absent_intervals"].items():
        possible = [(seconds(d["visible_start_seconds"]), seconds(d["visible_end_seconds"]))
                    for d in deployments.values() if d["recording_id"] == rid]
        possible += intervals["unknown_intervals"].get(rid, [])
        if any(_overlaps(absent, uncertain) for absent in absent_ranges for uncertain in possible):
            raise EvidenceError("Certified absence overlaps possible minion-like/unknown content.")
    for key, frame in frames.items():
        annotations = annotations_by_frame[key]
        rid = frame["recording_id"]
        actual = seconds(frame["timestamp_seconds"])
        last = recordings[rid]["last_frame_seconds"]
        unknown = any(_at(actual, interval, last) for interval in intervals["unknown_intervals"].get(rid, []))
        possible = any(d["recording_id"] == rid and seconds(d["visible_start_seconds"]) <= actual < seconds(d["visible_end_seconds"])
                       for d in deployments.values())
        if annotations and (frame["minion_presence"] == "absent" or any(_at(actual, interval, last)
                                          for interval in intervals["confirmed_absent_intervals"].get(rid, []))):
            raise EvidenceError("Annotated visual units cannot be absent/background.")
        if frame["review_status"] == "complete":
            if (not frame["all_identifiable_units_labelled"] or frame["minion_presence"] == "unknown" or unknown
                    or any(a["review_status"] != "verified" for a in annotations)
                    or (frame["minion_presence"] == "positive" and not annotations)
                    or (frame["minion_presence"] == "absent" and possible)):
                raise EvidenceError("Complete frame needs consistent exhaustive unit review.")


def _eligible(draft):
    recordings, frames, deployments, included = _maps(draft)
    training_frames = {key: frame for key, frame in frames.items()
                       if key[0] in included and frame["review_status"] == "complete"}
    supported = set()
    for annotation in draft["unit_annotations"]:
        key = recordings[annotation["recording_id"]]["underlying_match_id"], annotation["deployment_id"]
        if (key in deployments and annotation["recording_id"] == deployments[key]["recording_id"]
                and (annotation["recording_id"], annotation["frame_id"]) in training_frames):
            supported.add(key)
    eligible = {key for key, d in deployments.items() if d["recording_id"] in included
                and d["owner"] == "opponent" and d["source_card"] == "minions" and d["form"] == "normal"
                and d["verification_status"] == "confirmed" and d["independence_attestation"] == "human_confirmed"
                and key in supported}
    match_ids = []
    for item in draft["intake"]:
        mid = recordings[item["recording_id"]]["underlying_match_id"]
        if item["status"] == "included" and any(key[0] == mid for key in eligible) and mid not in match_ids:
            match_ids.append(mid)
    return recordings, training_frames, eligible, match_ids


def _union_duration(intervals):
    end, duration = Fraction(0), Fraction(0)
    for start, stop in sorted(intervals):
        duration += max(Fraction(0), stop - max(start, end))
        end = max(end, stop)
    return duration


def dataset_readiness(draft: dict) -> dict:
    """Derive independent data gates; sparse negatives never certify time."""
    counts = dict.fromkeys(("matches", "recordings", "deployments", "images", "unit_boxes",
                           "target_positive_matches", "confirmed_target_deployments", "training_images",
                           "positive_training_images", "negative_training_images", "training_unit_boxes",
                           "pending_frames", "unknown_intervals"), 0)
    report = {"valid": False, "training_data_ready": False, "evaluation_ready": False,
              "counts": counts, "reasons": [], "evaluation_reasons": [],
              "confirmed_absent_seconds": 0, "per_match": [], "per_recording": [],
              "coverage_scope": "reviewed_absent_intervals_only"}
    try:
        validate_dataset_shape(draft)
    except EvidenceError:
        report["reasons"] = ["invalid_dataset_shape"]
        report["evaluation_reasons"] = ["invalid_dataset_shape"]
        return report
    recordings, training_frames, eligible, match_ids = _eligible(draft)
    counts.update(matches=len(draft["matches"]), recordings=len(recordings), deployments=len(draft["deployments"]),
                  images=len(draft["frames"]), unit_boxes=len(draft["unit_annotations"]),
                  target_positive_matches=len(match_ids), confirmed_target_deployments=len(eligible),
                  training_images=len(training_frames),
                  positive_training_images=sum(f["minion_presence"] == "positive" for f in training_frames.values()),
                  negative_training_images=sum(f["minion_presence"] == "absent" for f in training_frames.values()),
                  training_unit_boxes=sum((a["recording_id"], a["frame_id"]) in training_frames for a in draft["unit_annotations"]),
                  pending_frames=sum(f["review_status"] == "pending" for f in draft["frames"]),
                  unknown_intervals=len(draft["unknown_intervals"]))
    included = {i["recording_id"] for i in draft["intake"] if i["status"] == "included"}
    coverage = {}
    for intake in draft["intake"]:
        rid = intake["recording_id"]
        ranges = [(seconds(i["start_seconds"]), seconds(i["end_seconds"]))
                  for i in draft["confirmed_absent_intervals"] if i["recording_id"] == rid]
        duration = float(_union_duration(ranges))
        coverage[rid] = duration
        report["per_recording"].append({"recording_id": rid,
                                        "underlying_match_id": recordings[rid]["underlying_match_id"],
                                        "included": rid in included, "confirmed_absent_seconds": duration})
    for mid in match_ids:
        # No guessed alignment or longest/easiest post-hoc denominator selection.
        rid = next(i["recording_id"] for i in draft["intake"] if i["recording_id"] in included
                   and recordings[i["recording_id"]]["underlying_match_id"] == mid)
        report["per_match"].append({"underlying_match_id": mid,
                                    "confirmed_target_deployments": sum(key[0] == mid for key in eligible),
                                    "evaluation_recording_id": rid,
                                    "confirmed_absent_seconds": coverage[rid],
                                    "has_certified_absent_coverage": coverage[rid] > 0})
    report["confirmed_absent_seconds"] = sum(m["confirmed_absent_seconds"] for m in report["per_match"])
    report["valid"] = True
    if len(match_ids) < 4:
        report["reasons"].append("need_four_target_positive_matches")
    if len(eligible) < 8:
        report["reasons"].append("need_eight_confirmed_target_deployments")
    report["training_data_ready"] = not report["reasons"]
    if not report["training_data_ready"]:
        report["evaluation_reasons"].append("training_data_not_ready")
    if not match_ids or any(m["confirmed_absent_seconds"] <= 0 for m in report["per_match"]):
        report["evaluation_reasons"].append("missing_absent_coverage")
    report["evaluation_ready"] = not report["evaluation_reasons"]
    return report


def grouped_folds(draft: dict) -> list[dict]:
    """Deterministic LOMO ownership; assignment is not a frame eligibility claim."""
    validate_dataset_shape(draft)
    recordings, _, _, match_ids = _eligible(draft)
    if len(match_ids) < 2:
        return []
    folds = []
    for held_out in match_ids:
        fold = {"fold_id": f"lomo_{len(folds) + 1}", "train_match_ids": [mid for mid in match_ids if mid != held_out],
                "validation_match_ids": [held_out]}
        for split in ("train", "validation"):
            mids = set(fold[split + "_match_ids"])
            rids = [i["recording_id"] for i in draft["intake"]
                    if recordings[i["recording_id"]]["underlying_match_id"] in mids]
            fold[split + "_recording_ids"] = rids
            fold[split + "_frames"] = [{"recording_id": rid, "frame_id": f["frame_id"]}
                                       for rid in rids for f in draft["frames"] if f["recording_id"] == rid]
        folds.append(fold)
    return folds
