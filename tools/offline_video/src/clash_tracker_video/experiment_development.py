"""Pure development eligibility, never automatic card selection or inference."""
from copy import deepcopy
from collections.abc import Mapping

from .evidence_contract import EvidenceError, SCHEMAS, validate_evidence, seconds, valid_type, interval_contains
from .evidence_review import review_evidence
from .experiment_contract import FORM_TO_V1, validate_draft_shape


def _unique(values):
    if len(values) != len(set(values)):
        raise EvidenceError("Duplicate development identity or reference.")


def _overlaps(start, end, left, right):
    return seconds(start) < seconds(right) and seconds(left) < seconds(end)


def _checked_report(draft, indexes):
    validate_draft_shape(draft)
    if not isinstance(indexes, Mapping):
        raise EvidenceError("Recording indexes required.")
    candidates = draft["candidates"]
    identity = draft["identity"]
    _unique([c["candidate_id"] for c in candidates])
    _unique([(c["card_id"], c["form"]) for c in candidates])
    _unique([u["unknown_id"] for u in draft["unknown_intervals"]])
    recording = None
    all_plays = []
    all_refs = []
    gaps = []
    for candidate in candidates:
        evidence = candidate["evidence"]
        # v1 diagnostics contain schema names only; suppress malformed index
        # exceptions and return one stable, path-free adapter diagnostic.
        try:
            errors = validate_evidence(evidence, indexes)
        except (TypeError, KeyError, AttributeError, ValueError, OverflowError) as exc:
            raise EvidenceError("Invalid v1 evidence or index metadata.") from exc
        if errors:
            raise EvidenceError("Development v1 evidence validation failed.")
        if len(evidence["recordings"]) != 1 or evidence["recordings"][0]["recording_id"] != identity["recording_id"]:
            raise EvidenceError("Development identity must match every evidence recording.")
        current = evidence["recordings"][0]
        if recording is not None and recording != current:
            raise EvidenceError("Conflicting candidate recording metadata.")
        recording = current
        target = evidence["target_card"]
        if (target is None or target["card_id"] != candidate["card_id"]
                or target["variant"] != FORM_TO_V1[candidate["form"]]):
            raise EvidenceError("Candidate card/form must match v1 evidence target.")
        if not any(s["validation_status"] == "verified" and s["capture_complete"]
                   and s["perspective"] != "unknown" for s in evidence["match_segments"]):
            raise EvidenceError("Reviewed complete development match segment required.")
        play_ids = [p["play_id"] for p in evidence["occurrences"]]
        deployment_ids = [d["play_id"] for d in candidate["deployments"]]
        _unique(deployment_ids)
        if set(play_ids) != set(deployment_ids):
            raise EvidenceError("Deployment annotations must cover exactly the v1 occurrences.")
        all_refs.extend(play_ids)
        if any(d["form"] != candidate["form"] for d in candidate["deployments"]):
            raise EvidenceError("One logical form per evidence bundle required.")
        all_plays.extend((candidate, p) for p in evidence["occurrences"])
        for gap in review_evidence(evidence, indexes)["coverage_gaps"]:
            gaps.append({"candidate_id": candidate["candidate_id"], **gap})
    _unique(all_refs)
    if candidates:
        _index_snapshot(draft, indexes)
    # Renaming a play or annotation cannot manufacture an independent spawn.
    for i, (candidate, play) in enumerate(all_plays):
        if play["manual_verification_status"] == "rejected":
            continue
        key_evidence = {(a["frame_id"], tuple(a["normalized_bbox"][field] for field in ("x", "y", "width", "height")))
                        for a in candidate["evidence"]["frame_annotations"] if a["play_id"] == play["play_id"]}
        for other_candidate, other in all_plays[:i]:
            if (other["manual_verification_status"] == "rejected"
                    or candidate["card_id"] != other_candidate["card_id"]):
                continue
            other_evidence = {(a["frame_id"], tuple(a["normalized_bbox"][field] for field in ("x", "y", "width", "height")))
                              for a in other_candidate["evidence"]["frame_annotations"] if a["play_id"] == other["play_id"]}
            if (key_evidence & other_evidence
                    or seconds(play["deployment_time_seconds"]) == seconds(other["deployment_time_seconds"])
                    or _overlaps(play["deployment_lower_seconds"], play["deployment_upper_seconds"],
                                 other["deployment_lower_seconds"], other["deployment_upper_seconds"])):
                raise EvidenceError("Reused or overlapping deployment evidence is not independent.")
    for unknown in draft["unknown_intervals"]:
        if (recording is None or unknown["recording_id"] != identity["recording_id"]
                or seconds(unknown["end_seconds"]) > seconds(recording["last_frame_seconds"])
                or (unknown["start_seconds"] == unknown["end_seconds"]
                    and seconds(unknown["end_seconds"]) != seconds(recording["last_frame_seconds"]))):
            raise EvidenceError("Unknown interval conflicts with development recording.")
    for candidate in candidates:
        for negative in candidate["evidence"]["negative_intervals"]:
            if negative["review_status"] != "verified":
                continue
            for unknown in draft["unknown_intervals"]:
                if (_overlaps(negative["start_seconds"], negative["end_seconds"],
                              unknown["start_seconds"], unknown["end_seconds"])
                        or (unknown["start_seconds"] == unknown["end_seconds"]
                            and interval_contains(seconds(unknown["start_seconds"]),
                                seconds(negative["start_seconds"]), seconds(negative["end_seconds"]),
                                last_frame=seconds(recording["last_frame_seconds"]), terminal_negative=True))):
                    raise EvidenceError("Confirmed negative overlaps explicit uncertainty.")
            for other_candidate, play in all_plays:
                if (other_candidate["card_id"] == candidate["card_id"]
                        and play["manual_verification_status"] != "rejected"
                        and _overlaps(negative["start_seconds"], negative["end_seconds"],
                                      play["visible_start_seconds"], play["visible_end_seconds"])):
                    raise EvidenceError("Confirmed negative overlaps possible card/form visibility.")
    uncertainty = bool(draft["unknown_intervals"] or gaps
                       or any(c["form"] == "unknown" for c in candidates)
                       or any(d["possible_missed_play"] for c in candidates for d in c["deployments"]))
    derived = []
    for candidate in candidates:
        evolution = candidate["evolution"]
        progress_unknown = (uncertainty or not evolution["capable"] or evolution["equipped"] != "verified"
                            or evolution["rules_version"] is None or evolution["charge_requirement"] is None)
        plays = {p["play_id"]: p for p in candidate["evidence"]["occurrences"]}
        count = 0
        for deployment in candidate["deployments"]:
            progress = deployment["evolution"]
            if progress_unknown and (progress["progress"] != "unknown" or progress["remaining_count"] is not None):
                raise EvidenceError("Uncertain evidence forbids precise evolution progress.")
            if progress["remaining_count"] is not None and progress["remaining_count"] > evolution["charge_requirement"]:
                raise EvidenceError("Manual evolution remaining count exceeds charge requirement.")
            if (deployment["clear"] and plays[deployment["play_id"]]["manual_verification_status"] == "verified"
                    and candidate["form"] != "unknown"):
                count += 1
        reasons = []
        if candidate["form"] == "unknown":
            reasons.append("Unknown form cannot qualify.")
        if count < 2:
            reasons.append("Fewer than two independent clear verified plays of this exact form.")
        derived.append({"candidate_id": candidate["candidate_id"], "card_id": candidate["card_id"],
                        "form": candidate["form"], "clear_verified_plays": count,
                        "eligible": count >= 2 and candidate["form"] != "unknown", "reasons": reasons,
                        "evolution_progress": "unknown" if progress_unknown else "manual"})
    selection = draft["selection"]
    reasons = []
    selected = None if selection is None else next((c for c in derived if all(
        c[field] == selection[field] for field in ("candidate_id", "card_id", "form"))), None)
    if selected is None:
        reasons.append("Manual target selection must reference actual candidate evidence.")
    elif not selected["eligible"]:
        reasons.append("Selected known-form target lacks two independent clear verified plays.")
    return {"status": "NOT_READY" if reasons else "DEV_VALIDATED", "valid": True,
            "reasons": reasons, "candidates": derived, "coverage_gaps": gaps,
            "unknown_intervals": deepcopy(draft["unknown_intervals"]),
            "provenance_assurance": "declared_human_review_only"}


def validate_development(draft, indexes):
    """Report invalid/insufficient inputs without exposing private strings."""
    try:
        return _checked_report(draft, indexes)
    except EvidenceError as exc:
        return {"status": "NOT_READY", "valid": False, "reasons": [str(exc)],
                "candidates": [], "coverage_gaps": [], "unknown_intervals": [],
                "provenance_assurance": "declared_human_review_only"}


def _index_snapshot(draft, indexes):
    """Bind used export metadata/pixel hashes, without persisting filesystem roots."""
    rid = draft["identity"]["recording_id"]
    index = indexes.get(rid)
    if type(index) is not dict or set(index) != {"recording", "frames"}:
        raise EvidenceError("Invalid bound recording index fields.")
    recording = index["recording"]
    recording_schema = SCHEMAS["recordings"]
    if (type(recording) is not dict or set(recording) != set(recording_schema)
            or any(not valid_type(recording[field], kind) for field, kind in recording_schema.items())):
        raise EvidenceError("Invalid bound recording metadata.")
    if type(index["frames"]) is not list:
        raise EvidenceError("Bound export frames must be an array.")
    used = {a["frame_id"] for c in draft["candidates"] for a in c["evidence"]["frame_annotations"]}
    frame_schema = dict(frame_id="id", requested_seconds="seconds", timestamp_seconds="seconds",
                        raw_pts="int", time_base="rational", image_path="png",
                        image_width="positive_int", image_height="positive_int", status={"success"})
    fields = (*frame_schema, "reason")
    entries = {}
    for source in index["frames"]:
        if type(source) is not dict:
            raise EvidenceError("Invalid bound export frame object.")
        if source.get("status") != "success":
            continue
        if not valid_type(source.get("frame_id"), "id"):
            raise EvidenceError("Invalid bound export frame identity.")
        if source["frame_id"] not in used:
            continue
        if (not set(fields) <= set(source) or set(source) - set(fields) - {"_content_hash", "_aliases"}
                or any(not valid_type(source[field], kind) for field, kind in frame_schema.items())
                or source["reason"] is not None):
            raise EvidenceError("Invalid bound export metadata.")
        # Check each retained occurrence before merging: True == 1 must never
        # allow an invalid duplicate to replace a valid original entry.
        if "_content_hash" in source and not valid_type(source["_content_hash"], "hash"):
            raise EvidenceError("Invalid bound export pixel hash.")
        if "_aliases" in source and (type(source["_aliases"]) is not list
                or not all(valid_type(alias, "png") for alias in source["_aliases"])):
            raise EvidenceError("Invalid bound export aliases.")
        entries[source["frame_id"]] = source
    frames = []
    for fid in sorted(entries):
        source = entries[fid]
        frame = {field: deepcopy(source[field]) for field in fields}
        if "_content_hash" in source:
            frame["_content_hash"] = source["_content_hash"]
        if "_aliases" in source:
            frame["_aliases"] = sorted(set(source["_aliases"]))
        frames.append(frame)
    return {rid: {"recording": deepcopy(recording), "frames": frames}}


def require_development(draft, indexes):
    """Return an isolated freeze payload; disk verification is the loader's job."""
    report = validate_development(draft, indexes)
    if report["status"] != "DEV_VALIDATED":
        raise EvidenceError("Development evidence is invalid or not ready.")
    return {"draft": deepcopy(draft), "derived": report, "index_snapshot": _index_snapshot(draft, indexes)}
