"""Versioned offline lock contracts, not inference or proof of human attestations.

Pure validators bind metadata snapshots. Disk consumers must independently load
recordings/indexes before freezing; these hashes do not certify media authenticity.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

from .evidence_contract import (EvidenceError, SCHEMAS, interval_contains,
                                load_evidence, number, rational, seconds, valid_type)
from .experiment_contract import FORMS, utc_time
from .experiment_development import _index_snapshot, require_development
from .evidence_prepare import safe_path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
MAX_LOCK_BYTES = 16 * 1024 * 1024
LOCK_TYPES = {"development", "model", "test_gt"}
COMMON = {"schema_version", "experiment_id", "freeze_version", "created_at"}
MODEL_FIELDS = COMMON | {"development_lock_sha256", "target", "git_commit", "model_sha256",
    "development_session_id", "test_pixels_unseen", "precise_test_gt_unseen", "input",
    "sampling", "confidence_threshold", "nms", "postprocess", "evaluation_protocol_version"}
GT_FIELDS = COMMON | {"development_lock_sha256", "model_lock_sha256", "target", "identity",
    "annotation_session", "selection_history", "recording", "match_segments", "evolution",
    "deployments", "negative_intervals", "unknown_intervals", "index_snapshot",
    "evaluation_protocol_version"}


def _object(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise EvidenceError("Invalid closed lock object fields.")


def _text(value):
    if type(value) is not str or not value.strip():
        raise EvidenceError("Nonempty lock text required.")


def _choice(value, choices):
    if type(value) is not str or value not in choices:
        raise EvidenceError("Unsupported lock value.")


def _integer(value, minimum=1):
    if type(value) is not int or value < minimum:
        raise EvidenceError("Invalid lock integer.")


def _true(value):
    if value is not True:
        raise EvidenceError("Required manual lock attestation absent.")


def _bool(value):
    if type(value) is not bool:
        raise EvidenceError("Invalid lock boolean.")


def _hash(value, length=64):
    if type(value) is not str or not re.fullmatch(f"[0-9a-f]{{{length}}}", value):
        raise EvidenceError("Invalid lock hash.")


def _version(value):
    if type(value) is not int or value != 1:
        raise EvidenceError("Unsupported lock schema or protocol version.")


def _common(value):
    _version(value["schema_version"])
    _integer(value["freeze_version"])
    identifier = value["experiment_id"]
    if (type(identifier) is not str or not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", identifier)
            or identifier.upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)],
                                      *[f"LPT{i}" for i in range(1, 10)]}):
        raise EvidenceError("Unsafe experiment identifier.")
    utc_time(value["created_at"])


def canonical_bytes(value):
    """Compact sorted-key UTF-8 JSON; array order and numeric types are retained."""
    def check(item):
        if type(item) is dict:
            if any(type(k) is not str for k in item):
                raise EvidenceError("JSON object keys must be strings.")
            for nested in item.values():
                check(nested)
        elif type(item) is list:
            for nested in item:
                check(nested)
        elif item is None or type(item) in (str, bool):
            return
        elif type(item) in (int, float) and number(item):
            return
        else:
            raise EvidenceError("Strict finite JSON required.")
    try:
        check(value)
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("Cannot serialize strict lock JSON.") from exc


def _digest(envelope):
    return sha256(canonical_bytes({k: v for k, v in envelope.items() if k != "sha256"})).hexdigest()


def _envelope(kind, source, payload):
    if type(source) is not dict or not COMMON <= set(source):
        raise EvidenceError("Missing lock identity/version/time fields.")
    envelope = {k: deepcopy(source[k]) for k in COMMON}
    envelope.update(lock_type=kind, payload=deepcopy(payload))
    envelope["sha256"] = _digest(envelope)
    return envelope


def _base(envelope):
    _object(envelope, COMMON | {"lock_type", "payload", "sha256"})
    _common(envelope)
    _choice(envelope["lock_type"], LOCK_TYPES)
    _hash(envelope["sha256"])
    if envelope["sha256"] != _digest(envelope):
        raise EvidenceError("Lock digest does not match complete envelope.")


def _bound_common(envelope, source):
    if canonical_bytes({k: envelope[k] for k in COMMON}) != canonical_bytes({k: source[k] for k in COMMON}):
        raise EvidenceError("Lock envelope is not bound to payload identity/version/time.")


def _target(target):
    _object(target, {"card_id", "form"})
    _text(target["card_id"])
    _choice(target["form"], {"normal", "evolved"})


def _dev_target(development):
    selection = development["payload"]["draft"]["selection"]
    return {k: selection[k] for k in ("card_id", "form")}


def _after(envelope, prior):
    if utc_time(envelope["created_at"]) <= utc_time(prior["created_at"]):
        raise EvidenceError("Lock creation must follow its prerequisite strictly.")
    if envelope["experiment_id"] != prior["experiment_id"]:
        raise EvidenceError("Lock experiment reference conflicts.")


def _ratio(value):
    if not number(value) or not 0 <= value <= 1:
        raise EvidenceError("Invalid locked threshold.")


def _model(envelope, development):
    contract = envelope["payload"]
    reference = set(contract) == MODEL_FIELDS | {"artifact_type", "baseline"}
    _object(contract, MODEL_FIELDS | {"artifact_type", "baseline"} if reference else MODEL_FIELDS)
    _bound_common(envelope, contract)
    _version(contract["evaluation_protocol_version"])
    _after(envelope, development)
    if contract["development_lock_sha256"] != development["sha256"]:
        raise EvidenceError("Model development digest reference conflicts.")
    _target(contract["target"])
    if canonical_bytes(contract["target"]) != canonical_bytes(_dev_target(development)):
        raise EvidenceError("Model target must equal the locked development target.")
    _hash(contract["git_commit"], 40)
    _hash(contract["model_sha256"])
    _text(contract["development_session_id"])
    _true(contract["test_pixels_unseen"])
    _true(contract["precise_test_gt_unseen"])
    geometry = contract["input"]
    _object(geometry, {"width", "height", "crop", "resize", "interpolation", "preprocess"})
    _integer(geometry["width"])
    _integer(geometry["height"])
    if geometry["crop"] is not None and not valid_type(geometry["crop"], "box"):
        raise EvidenceError("Invalid normalized full-image crop.")
    _choice(geometry["resize"], {"stretch", "letterbox"})
    _choice(geometry["interpolation"], {"nearest", "bilinear", "bicubic"})
    preprocess = geometry["preprocess"]
    _object(preprocess, {"color_order", "dtype", "scale", "mean", "std"})
    _choice(preprocess["color_order"], {"RGB", "BGR"})
    _choice(preprocess["dtype"], {"float32", "uint8"})
    if not number(preprocess["scale"]) or preprocess["scale"] <= 0:
        raise EvidenceError("Invalid preprocessing scale.")
    for name in ("mean", "std"):
        items = preprocess[name]
        if type(items) is not list or len(items) != 3 or not all(number(x) for x in items):
            raise EvidenceError("Three finite preprocessing channel values required.")
    if any(x <= 0 for x in preprocess["std"]):
        raise EvidenceError("Preprocessing standard deviation must be positive.")
    _object(contract["sampling"], {"fps", "start_seconds"})
    if not number(contract["sampling"]["fps"]) or contract["sampling"]["fps"] <= 0:
        raise EvidenceError("Positive locked sampling rate required.")
    if seconds(contract["sampling"]["start_seconds"]) != 0:
        raise EvidenceError("Protocol v1 sampling must start at the recording origin.")
    _ratio(contract["confidence_threshold"])
    _object(contract["nms"], {"enabled", "iou_threshold"})
    _bool(contract["nms"]["enabled"])
    _ratio(contract["nms"]["iou_threshold"])
    _object(contract["postprocess"], {"version", "class_agnostic_nms", "max_detections"})
    _text(contract["postprocess"]["version"])
    _bool(contract["postprocess"]["class_agnostic_nms"])
    _integer(contract["postprocess"]["max_detections"])
    if reference:
        _reference_baseline(contract, development)


def _reference_baseline(contract, development):
    """Additive closed detector-artifact variant; legacy v1 contracts unchanged."""
    from .baseline import Config, reference_model_parameters
    _choice(contract['artifact_type'], {'reference_template_matcher'})
    baseline = contract['baseline']
    _object(baseline, {'artifact_sha256','config','templates','score_method','event_merge',
                      'threshold_derivation','opencv_version','evaluation_protocol_version'})
    if baseline['artifact_sha256'] != contract['model_sha256']:
        raise EvidenceError('Reference artifact hash conflicts with Model Lock.')
    _choice(baseline['score_method'], {'RGB_TM_CCOEFF_NORMED'})
    _choice(baseline['event_merge'], {'transitive_adjacent_support_gap'})
    _choice(baseline['threshold_derivation'], {'min_two_held_out_true_event_peak_scores'})
    _version(baseline['evaluation_protocol_version'])
    _text(baseline['opencv_version'])
    config = baseline['config']
    _object(config, {'roi','scales','fps','fine_seconds','merge_seconds','working_scale',
                     'proposal_floor','coarse_seeds','top_k'})
    if type(config['roi']) is not list or len(config['roi']) != 4 or type(config['scales']) is not list:
        raise EvidenceError('Invalid fixed reference geometry/scales.')
    parsed = Config(**{**config,'roi':tuple(config['roi']),'scales':tuple(config['scales'])})
    rid = development['payload']['draft']['identity']['recording_id']
    recording = development['payload']['index_snapshot'][rid]['recording']
    expected = reference_model_parameters(recording, parsed)
    if any(contract[k] != value for k,value in expected.items()):
        raise EvidenceError('Reference configuration conflicts with actual scanner parameters.')
    templates = baseline['templates']
    if type(templates) is not list or not templates:
        raise EvidenceError('Reference template identities required.')
    seen = set()
    for template in templates:
        _object(template, {'template_id','play_id','frame_id','width','height','crop_rgb_sha256'})
        for field in ('template_id','play_id','frame_id'):
            _text(template[field])
        _integer(template['width']); _integer(template['height']); _hash(template['crop_rgb_sha256'])
        if template['template_id'] in seen:
            raise EvidenceError('Duplicate reference template identity.')
        seen.add(template['template_id'])


def _record(value, schema):
    _object(value, schema)
    if any(not valid_type(value[k], kind) for k, kind in schema.items()):
        raise EvidenceError("Invalid ground-truth evidence metadata.")


def _array(value):
    if type(value) is not list:
        raise EvidenceError("Ground-truth collections must be arrays.")


def _unique(values):
    if len(set(values)) != len(values):
        raise EvidenceError("Duplicate ground-truth evidence identity.")


def _overlap(a, b, c, d):
    return seconds(a) < seconds(d) and seconds(c) < seconds(b)


def _evolution(value):
    _object(value, {"capable", "equipped", "charge_requirement", "rules_version"})
    _bool(value["capable"])
    _choice(value["equipped"], {"verified", "not_equipped", "unknown"})
    if value["charge_requirement"] is not None:
        _integer(value["charge_requirement"])
    if value["rules_version"] is not None:
        _text(value["rules_version"])
    if not value["capable"] and (value["equipped"] == "verified" or value["charge_requirement"] is not None):
        raise EvidenceError("Conflicting ground-truth evolution capability.")


def _gt(envelope, development, model):
    gt = envelope["payload"]
    _object(gt, GT_FIELDS)
    _bound_common(envelope, gt)
    _version(gt["evaluation_protocol_version"])
    _after(envelope, model)
    if (gt["development_lock_sha256"] != development["sha256"] or gt["model_lock_sha256"] != model["sha256"]):
        raise EvidenceError("Ground-truth lock chain digest conflicts.")
    _target(gt["target"])
    if canonical_bytes(gt["target"]) != canonical_bytes(model["payload"]["target"]):
        raise EvidenceError("Ground truth target conflicts with Model Lock.")
    identity = gt["identity"]
    _object(identity, {"underlying_match_id", "recording_id", "split", "provenance", "complete_recording",
                      "unedited_recording", "full_human_review", "first_qualifying_match", "all_deployments_reviewed"})
    _text(identity["underlying_match_id"])
    _text(identity["recording_id"])
    _choice(identity["split"], {"test"})
    _choice(identity["provenance"], {"new_natural"})
    for key in ("complete_recording", "unedited_recording", "full_human_review", "first_qualifying_match", "all_deployments_reviewed"):
        _true(identity[key])
    dev_identity = development["payload"]["draft"]["identity"]
    if (identity["underlying_match_id"] == dev_identity["underlying_match_id"]
            or identity["recording_id"] == dev_identity["recording_id"]):
        raise EvidenceError("Test must be a declared independent match and recording.")
    session = gt["annotation_session"]
    _object(session, {"session_id", "independent_session", "predictions_unseen"})
    _text(session["session_id"])
    _true(session["independent_session"])
    _true(session["predictions_unseen"])
    if session["session_id"] == model["payload"]["development_session_id"]:
        raise EvidenceError("Fresh annotation session required.")
    _array(gt["selection_history"])
    for item in gt["selection_history"]:
        _object(item, {"underlying_match_id", "reason"})
        _text(item["underlying_match_id"])
        _choice(item["reason"], {"missing_replay", "damaged_replay", "interrupted_recording", "undecodable"})
        if item["underlying_match_id"] == identity["underlying_match_id"]:
            raise EvidenceError("Selected test cannot also be excluded material.")
    _unique([i["underlying_match_id"] for i in gt["selection_history"]])
    recording = gt["recording"]
    _record(recording, SCHEMAS["recordings"])
    if recording["recording_id"] != identity["recording_id"]:
        raise EvidenceError("Ground-truth recording identity conflicts.")
    dev_recording = development["payload"]["index_snapshot"][dev_identity["recording_id"]]["recording"]
    if recording["source_sha256"] == dev_recording["source_sha256"]:
        raise EvidenceError("Test source recording duplicates development.")
    rid = recording["recording_id"]
    last = seconds(recording["last_frame_seconds"])
    w, h = recording["width"], recording["height"]
    if recording["rotation_degrees"] in (90, 270):
        w, h = h, w
    orientation = "portrait" if h > w else "landscape" if w > h else "square"
    if recording["orientation"] != orientation:
        raise EvidenceError("Ground-truth orientation conflicts with dimensions.")
    _array(gt["match_segments"])
    segments = {}
    for segment in gt["match_segments"]:
        _record(segment, SCHEMAS["match_segments"])
        if (segment["recording_id"] != rid or segment["perspective"] != recording["perspective"]
                or not 0 <= seconds(segment["start_seconds"]) < seconds(segment["end_seconds"]) <= last
                or segment["validation_status"] != "verified" or segment["capture_complete"] is not True
                or segment["perspective"] == "unknown"):
            raise EvidenceError("Reviewed complete ground-truth match segment required.")
        segments[segment["segment_id"]] = segment
    _unique([s["segment_id"] for s in gt["match_segments"]])
    if len(segments) != 1:
        raise EvidenceError("Exactly one complete test match segment required.")
    _evolution(gt["evolution"])
    _array(gt["deployments"])
    _array(gt["negative_intervals"])
    _array(gt["unknown_intervals"])
    frames = []
    plays = gt["deployments"]
    ordered_fields = ("last_absent_seconds", "deployment_lower_seconds", "deployment_time_seconds",
                      "deployment_upper_seconds", "visible_start_seconds", "visible_end_seconds")
    play_fields = {"play_id", "recording_id", "card_id", "owner", *ordered_fields, "match_segment_id", "notes",
                   "form", "evaluation_status", "non_evaluable_reason", "possible_missed_play", "evolution", "key_frames"}
    for play in plays:
        _object(play, play_fields)
        for name in ("play_id", "notes"):
            _text(play[name])
        _choice(play["owner"], {"opponent"})
        _choice(play["form"], FORMS)
        _choice(play["evaluation_status"], {"evaluable", "non_evaluable"})
        _bool(play["possible_missed_play"])
        if play["evaluation_status"] == "non_evaluable":
            _text(play["non_evaluable_reason"])
        elif play["non_evaluable_reason"] is not None:
            raise EvidenceError("Evaluable play cannot carry an exclusion reason.")
        segment = segments.get(play["match_segment_id"])
        if segment is None or play["recording_id"] != rid or play["card_id"] != gt["target"]["card_id"]:
            raise EvidenceError("Ground-truth deployment identity/reference conflicts.")
        bounds = [segment["start_seconds"], *[play[k] for k in ordered_fields], segment["end_seconds"]]
        if (any(seconds(a) > seconds(b) for a, b in zip(bounds, bounds[1:]))
                or seconds(play["visible_start_seconds"]) >= seconds(play["visible_end_seconds"])):
            raise EvidenceError("Invalid ground-truth onset or visibility bounds.")
        if play["form"] == "evolved" and (not gt["evolution"]["capable"] or gt["evolution"]["equipped"] == "not_equipped"):
            raise EvidenceError("Ground-truth evolved form conflicts with capability.")
        progress = play["evolution"]
        _object(progress, {"progress", "remaining_count", "source"})
        _choice(progress["progress"], {"known", "unknown"})
        _choice(progress["source"], {"manual"})
        if progress["remaining_count"] is not None:
            _integer(progress["remaining_count"], 0)
        if (progress["progress"] == "unknown") != (progress["remaining_count"] is None):
            raise EvidenceError("Unknown evolution requires null remaining count.")
        _array(play["key_frames"])
        # Non-evaluable and unresolved-form deployments may legitimately have no boxes.
        for frame in play["key_frames"]:
            _record(frame, SCHEMAS["frame_annotations"])
            if (frame["recording_id"] != rid or frame["play_id"] != play["play_id"]
                    or frame["review_status"] != "verified"
                    or (frame["image_width"], frame["image_height"]) != (w, h)):
                raise EvidenceError("Ground-truth box identity, dimensions or review conflicts.")
            actual = frame["raw_pts"] * rational(frame["time_base"]) - recording["origin_pts"] * rational(recording["origin_time_base"])
            if (abs(actual - seconds(frame["timestamp_seconds"])) > seconds(.000001)
                    or not interval_contains(actual, seconds(play["visible_start_seconds"]),
                        seconds(play["visible_end_seconds"]), last_frame=last)):
                raise EvidenceError("Ground-truth box timestamp conflicts.")
            frames.append(frame)
    _unique([p["play_id"] for p in plays])
    _unique([f["annotation_id"] for f in frames])
    if not any(p["form"] == gt["target"]["form"] for p in plays):
        raise EvidenceError("Test requires at least one locked-form deployment.")
    for i, play in enumerate(plays):
        own_boxes = {(f["frame_id"], canonical_bytes(f["normalized_bbox"])) for f in play["key_frames"]}
        for other in plays[:i]:
            other_boxes = {(f["frame_id"], canonical_bytes(f["normalized_bbox"])) for f in other["key_frames"]}
            if (seconds(play["deployment_time_seconds"]) == seconds(other["deployment_time_seconds"])
                    or _overlap(play["deployment_lower_seconds"], play["deployment_upper_seconds"],
                                other["deployment_lower_seconds"], other["deployment_upper_seconds"])
                    or own_boxes & other_boxes):
                raise EvidenceError("Reused ground-truth deployment evidence.")
    pseudo_draft = {"identity": {"recording_id": rid}, "candidates": [{"evidence": {"frame_annotations": frames}}]}
    snapshot = _index_snapshot(pseudo_draft, gt["index_snapshot"])
    if canonical_bytes(snapshot) != canonical_bytes(gt["index_snapshot"]):
        raise EvidenceError("Ground-truth snapshot is not canonical or contains unbound metadata.")
    if canonical_bytes(snapshot[rid]["recording"]) != canonical_bytes(recording):
        # Existing index loading may retain unknown perspective; all other metadata bind exactly.
        bound = deepcopy(snapshot[rid]["recording"])
        if bound["perspective"] != "unknown":
            raise EvidenceError("Ground-truth recording snapshot conflicts.")
        bound["perspective"] = recording["perspective"]
        if canonical_bytes(bound) != canonical_bytes(recording):
            raise EvidenceError("Ground-truth recording snapshot conflicts.")
    indexed = {f["frame_id"]: f for f in snapshot[rid]["frames"]}
    for frame in frames:
        entry = indexed.get(frame["frame_id"])
        fields = ("raw_pts", "time_base", "image_width", "image_height", "timestamp_seconds")
        if (entry is None or canonical_bytes({k: frame[k] for k in fields}) != canonical_bytes({k: entry[k] for k in fields})
                or frame["image_path"] not in entry.get("_aliases", [entry["image_path"]])):
            raise EvidenceError("Ground-truth frame snapshot reference conflicts.")
    unknowns = gt["unknown_intervals"]
    for unknown in unknowns:
        _object(unknown, {"unknown_id", "recording_id", "start_seconds", "end_seconds", "reason"})
        _text(unknown["unknown_id"])
        _text(unknown["reason"])
        if (unknown["recording_id"] != rid or not 0 <= seconds(unknown["start_seconds"]) <= seconds(unknown["end_seconds"]) <= last
                or (unknown["start_seconds"] == unknown["end_seconds"] and seconds(unknown["end_seconds"]) != last)):
            raise EvidenceError("Invalid ground-truth unknown bounds.")
    _unique([u["unknown_id"] for u in unknowns])
    for negative in gt["negative_intervals"]:
        _record(negative, SCHEMAS["negative_intervals"])
        start, end = seconds(negative["start_seconds"]), seconds(negative["end_seconds"])
        if negative["recording_id"] != rid or negative["review_status"] != "verified" or not 0 <= start < end <= last:
            raise EvidenceError("Reviewed ground-truth negatives required.")
        segment = segments.get(negative["match_segment_id"])
        if negative["non_match"]:
            if negative["match_segment_id"] is not None or negative["reason"] == "target_absent" or any(
                _overlap(negative["start_seconds"], negative["end_seconds"], s["start_seconds"], s["end_seconds"])
                    for s in segments.values()):
                raise EvidenceError("Ground-truth non-match negative conflicts.")
        elif (segment is None or negative["reason"] != "target_absent"
              or not seconds(segment["start_seconds"]) <= start < end <= seconds(segment["end_seconds"])):
            raise EvidenceError("Ground-truth match negative conflicts.")
        for interval in [*plays, *unknowns]:
            left = interval.get("visible_start_seconds", interval.get("start_seconds"))
            right = interval.get("visible_end_seconds", interval.get("end_seconds"))
            if (_overlap(negative["start_seconds"], negative["end_seconds"], left, right)
                    or (seconds(left) == seconds(right)
                    and interval_contains(seconds(left), start, end, last_frame=last, terminal_negative=True))):
                raise EvidenceError("Negative overlaps target/other/unknown form or uncertainty.")
    _unique([n["negative_id"] for n in gt["negative_intervals"]])
    evolution = gt["evolution"]
    uncertain = (bool(unknowns) or any(p["form"] == "unknown" or p["possible_missed_play"] for p in plays)
                 or not evolution["capable"] or evolution["equipped"] != "verified"
                 or evolution["charge_requirement"] is None or evolution["rules_version"] is None)
    for play in plays:
        progress = play["evolution"]
        if (uncertain and progress["progress"] != "unknown") or (progress["remaining_count"] is not None
                and progress["remaining_count"] > evolution["charge_requirement"]):
            raise EvidenceError("Uncertainty forbids precise evolution progress.")
    # Every unreviewed interval must be explicit; absence of labels is never negative.
    intervals = [(seconds(p["visible_start_seconds"]), seconds(p["visible_end_seconds"])) for p in plays]
    intervals.extend((seconds(n["start_seconds"]), seconds(n["end_seconds"])) for n in [*gt["negative_intervals"], *unknowns])
    cursor = seconds(0)
    for start, end in sorted(intervals):
        if start > cursor:
            raise EvidenceError("Unregistered ground-truth timeline gap.")
        cursor = max(cursor, end)
    if cursor < last or not (any(seconds(n["end_seconds"]) == last for n in gt["negative_intervals"])
                            or any(seconds(u["end_seconds"]) == last for u in unknowns)):
        raise EvidenceError("Ground-truth coverage must include explicit terminal state.")


def validate_lock(envelope, development_lock=None, model_lock=None):
    """Recompute digest, closed payload, prerequisite chain and strict UTC order.

    Returns an isolated envelope or raises a path-free EvidenceError. Passing an
    already validated object never skips prerequisite revalidation.
    """
    try:
        _base(envelope)
        kind = envelope["lock_type"]
        payload = envelope["payload"]
        if kind == "development":
            _object(payload, {"draft", "derived", "index_snapshot"})
            recomputed = require_development(payload["draft"], payload["index_snapshot"])
            if canonical_bytes(recomputed) != canonical_bytes(payload):
                raise EvidenceError("Development report/snapshot is not bound to recomputed evidence.")
            _bound_common(envelope, payload["draft"])
        else:
            development = validate_lock(development_lock)
            if development["lock_type"] != "development":
                raise EvidenceError("Development prerequisite has wrong lock type.")
            if kind == "model":
                _model(envelope, development)
            else:
                model = validate_lock(model_lock, development)
                if model["lock_type"] != "model":
                    raise EvidenceError("Model prerequisite has wrong lock type.")
                _gt(envelope, development, model)
        return deepcopy(envelope)
    except (TypeError, KeyError, AttributeError, ValueError, OverflowError, RecursionError) as exc:
        raise EvidenceError("Invalid lock metadata or missing prerequisite.") from exc


def make_development_lock(draft, indexes):
    """Pure constructor used after the caller's disk/index verification boundary."""
    return validate_lock(_envelope("development", draft, require_development(draft, indexes)))


def load_lock(path, development_lock=None, model_lock=None):
    """Load strict UTF-8 JSON and recompute complete lock/reference contracts."""
    return validate_lock(load_evidence(_directory(path)), development_lock, model_lock)


def lock_filename(envelope):
    _base(envelope)
    return f"{envelope['experiment_id']}.{envelope['lock_type']}.v{envelope['freeze_version']}.json"


def _directory(value):
    try:
        root = PROJECT_ROOT.absolute()
        # Guard textual traversal, UNC/URL and every link/junction ancestor before
        # any normalization; resolving first would conceal the unsafe input.
        path = safe_path(value)
        if not any(path.is_relative_to(root / folder) for folder in ("outputs", "local_data")):
            raise EvidenceError("Locks must stay in ignored project outputs or local_data.")
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        raise EvidenceError("Invalid local lock directory.") from exc


def _freeze(envelope, directory):
    raw = canonical_bytes(envelope) + b"\n"
    if len(raw) > MAX_LOCK_BYTES:
        raise EvidenceError("Lock exceeds strict loader size limit.")
    path = _directory(directory)
    try:
        path.mkdir(parents=True, exist_ok=True)
        # Inspect all names, not just canonical names: renaming is not a version escape.
        for existing in path.iterdir():
            if existing.is_symlink() or existing.is_junction() or not existing.is_file():
                raise EvidenceError("Lock directory must contain regular lock files only.")
            prior = load_evidence(existing)
            _base(prior)
            if all(prior[k] == envelope[k] for k in ("experiment_id", "lock_type", "freeze_version")):
                raise EvidenceError("This experiment/type/freeze version already exists.")
        destination = path / lock_filename(envelope)
        # Canonical names + exclusive creation also reject simultaneous same-version writers.
        with destination.open("xb") as handle:
            handle.write(raw)
        return deepcopy(envelope)
    except OSError as exc:
        raise EvidenceError("Cannot exclusively create immutable local lock.") from exc


def freeze_development(draft, indexes, directory):
    return _freeze(make_development_lock(draft, indexes), directory)


def freeze_model(contract, development_lock, directory):
    """Future contract reuse only; does not load/train/run a model artifact."""
    return _freeze(validate_lock(_envelope("model", contract, contract), development_lock), directory)


def freeze_test_gt(gt, development_lock, model_lock, directory):
    """Metadata-only GT freeze; callers must first verify disk/index bindings."""
    return _freeze(validate_lock(_envelope("test_gt", gt, gt), development_lock, model_lock), directory)


def evaluation_references(development_lock, model_lock, test_gt_lock):
    """Future Evaluation Result reference fields only; no predictions or metrics."""
    development = validate_lock(development_lock)
    model = validate_lock(model_lock, development)
    gt = validate_lock(test_gt_lock, development, model)
    if (development["lock_type"], model["lock_type"], gt["lock_type"]) != ("development", "model", "test_gt"):
        raise EvidenceError("Future evaluation requires all three exact lock types.")
    return {"schema_version": 1, "experiment_id": development["experiment_id"],
            "development_lock_sha256": development["sha256"], "model_lock_sha256": model["sha256"],
            "test_gt_sha256": gt["sha256"], "evaluation_protocol_version": 1}
