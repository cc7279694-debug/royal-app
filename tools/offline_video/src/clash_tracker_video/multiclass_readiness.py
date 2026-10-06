"""Pure Development qualification, exact scale statistics and export support.

Nothing here opens media, writes a lock, runs a detector or certifies legal rights.
Manual identity/causality/provenance declarations remain human attestations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256

from .evidence_contract import EvidenceError, rational, seconds
from .experiment_lock import canonical_bytes
from .multiclass_contract import (
    CandidateReport, MulticlassDraft, ReadinessReport, ScaleReport, ScaleSnapshot,
    _validate_types, validate_multiclass_shape,
)

POLICY = "dev_moving_area_quantiles_v1"
SPLITS = ("train", "development_validation")
OWNERS = ("opponent", "own", "neutral", "unknown")


def _canonical_collections(value, key=None):
    if isinstance(value, dict):
        return {k: _canonical_collections(v, k) for k, v in value.items()}
    if isinstance(value, list):
        rows = [_canonical_collections(v) for v in value]
        # These two arrays are histories, not sets. Intake chooses the primary.
        return rows if key in ("intake", "history") else sorted(rows, key=canonical_bytes)
    return value


def scale_basis(draft: MulticlassDraft) -> MulticlassDraft:
    """Validated canonical pre-selection draft; shared with the freeze consumer."""
    validate_multiclass_shape(draft)
    result = deepcopy(draft)
    result["selection"], result["backend_label_maps"] = None, {}
    return _canonical_collections(result)


def scale_basis_sha256(draft: MulticlassDraft) -> str:
    return sha256(canonical_bytes(scale_basis(draft))).hexdigest()


def _context(draft):
    records = {r["recording_id"]: r for r in draft["recordings"]}
    primary = {}
    for row in draft["intake"]:
        record = records[row["recording_id"]]
        if row["status"] == "included" and record["split"] in SPLITS:
            primary.setdefault(record["underlying_match_id"], record["recording_id"])
    annotations = defaultdict(list)
    for row in draft["annotations"]:
        annotations[row["frame_id"]].append(row)
    return {"records": records, "primary": primary,
            "groups": {r["appearance_group_id"]: r for r in draft["groups"]},
            "frames": {r["frame_id"]: r for r in draft["frames"]},
            "coverage": {r["frame_id"]: r for r in draft["coverage"]}, "annotations": annotations}


def _support_reasons(row, context):
    record = context["records"][row["recording_id"]]
    reasons = []
    if record["split"] not in SPLITS:
        reasons.append("not_development")
    if context["primary"].get(record["underlying_match_id"]) != record["recording_id"]:
        reasons.append("not_primary_recording")
    if row["review_state"] != "verified":
        reasons.append("observation_pending")
    if context["frames"][row["frame_id"]]["review_state"] == "excluded":
        reasons.append("frame_excluded")
    if row["owner"] not in ("own", "opponent"):
        reasons.append("owner_not_qualified")
    if row["observed_form"] != "normal":
        reasons.append("form_not_normal")
    group = context["groups"].get(row["appearance_group_id"])
    if group is None:
        reasons.append("missing_causal_group")
    else:
        root = context["groups"][group["causal_root_id"]]
        if group["recording_id"] != row["recording_id"]:
            reasons.append("alternate_recording_group")
        if (group["verification_state"] != "confirmed" or root["verification_state"] != "confirmed"
                or root["independence_attestation"] != "human_confirmed"):
            reasons.append("causal_independence_unconfirmed")
    return reasons


def _cause(row, context):
    record = context["records"][row["recording_id"]]
    group = context["groups"][row["appearance_group_id"]]
    return (record["underlying_match_id"], group["causal_root_id"], row["visual_class_id"], row["owner"])


def _support(rows, cid, owner, split, context, exclusions=()):
    rows = [r for r in rows if r["visual_class_id"] == cid and r["owner"] == owner
            and context["records"][r["recording_id"]]["split"] == split]
    causes = {_cause(r, context) for r in rows}
    mids = sorted({key[0] for key in causes})
    gids = sorted({r["appearance_group_id"] for r in rows})
    fids = sorted({r["frame_id"] for r in rows})
    entities = {(context["records"][r["recording_id"]]["underlying_match_id"], r["entity_occurrence_id"])
                for r in rows if r["entity_occurrence_id"] is not None}
    qualified = bool(causes) and owner in ("opponent", "own")
    return {"owner": owner, "split": split, "underlying_match_ids": mids,
            "causal_root_ids": sorted({key[1] for key in causes}), "appearance_group_ids": gids,
            "frame_ids": fids, "annotation_ids": sorted(r["annotation_id"] for r in rows),
            "counts": {"matches": len(mids), "groups": len(causes), "entities": len(entities),
                       "frames": len(fids), "boxes": len(rows)},
            "qualification": "qualified" if qualified else "not_qualified", "evaluation": "not_evaluated",
            "reasons": sorted(set(exclusions) | (set() if qualified else {"no_qualified_independent_support"}))}


def candidate_eligibility(draft: MulticlassDraft) -> CandidateReport:
    """Opponent-first candidates, independent of selection/export-frame filters."""
    validate_multiclass_shape(draft)
    context = _context(draft)
    rows = [r for r in draft["annotations"] if not _support_reasons(r, context)]
    reports = []
    for cls in sorted(draft["taxonomy"]["classes"], key=lambda r: r["visual_class_id"]):
        cid = cls["visual_class_id"]
        cells = [_support(rows, cid, owner, split, context) for owner in OWNERS for split in SPLITS]
        reasons = []
        if cls["kind"] not in ("unit", "building"):
            reasons.append("kind_not_first_poc")
        if cls["mobility"] == "unknown":
            reasons.append("mobility_unknown")
        for split in SPLITS:
            if not any(r["owner"] == "opponent" and r["split"] == split and r["counts"]["groups"] for r in cells):
                reasons.append(f"missing_opponent:{split}")
        reports.append({"visual_class_id": cid, "kind": cls["kind"], "mobility": cls["mobility"],
                        "basic_qualified": not reasons, "reasons": reasons, "support": cells})
    return {"qualified_class_ids": [r["visual_class_id"] for r in reports if r["basic_qualified"]],
            "class_reports": reports, "development_match_ids": sorted(context["primary"]),
            "primary_recording_ids": sorted(context["primary"].values()),
            "reasons": [] if len(context["primary"]) >= 2 else ["need_two_development_matches"]}


def _ratio(value):
    return None if value is None else {"numerator": value.numerator, "denominator": value.denominator}


def _quantile(values, p):
    if not values:
        return None
    values = sorted(values)
    offset = (len(values) - 1) * p
    lower = offset.numerator // offset.denominator
    fraction = offset - lower
    return values[lower] if not fraction else values[lower] + fraction * (values[lower + 1] - values[lower])


def _statistics(values):
    return {"count": len(values), "min": _ratio(min(values)) if values else None,
            "p10": _ratio(_quantile(values, Fraction(1, 10))),
            "p50": _ratio(_quantile(values, Fraction(1, 2))),
            "p90": _ratio(_quantile(values, Fraction(9, 10))),
            "max": _ratio(max(values)) if values else None}


def _area(row):
    return seconds(row["box"]["width"]) * seconds(row["box"]["height"])


def _box_statistics(rows, context):
    metrics = {key: [] for key in ("width_px", "height_px", "short_side_px", "area_norm")}
    for row in rows:
        frame = context["frames"][row["frame_id"]]
        w = seconds(row["box"]["width"]) * frame["image_width"]
        h = seconds(row["box"]["height"]) * frame["image_height"]
        for key, value in zip(metrics, (w, h, min(w, h), _area(row))):
            metrics[key].append(value)
    return {key: _statistics(values) for key, values in metrics.items()}


def development_scale_report(draft: MulticlassDraft) -> ScaleReport:
    """Equal-weight frame→cause→match→class medians, before class selection."""
    candidates = candidate_eligibility(draft)
    context = _context(draft)
    candidate_ids = [r["visual_class_id"] for r in candidates["class_reports"]
                     if r["basic_qualified"] and r["kind"] == "unit" and r["mobility"] == "moving"]
    reports, scores = [], {}
    for cls in candidates["class_reports"]:
        cid = cls["visual_class_id"]
        all_rows = [r for r in draft["annotations"] if r["visual_class_id"] == cid]
        reviewed = [r for r in all_rows if r["review_state"] == "verified" and
                    context["frames"][r["frame_id"]]["review_state"] != "excluded" and
                    context["primary"].get(context["records"][r["recording_id"]]["underlying_match_id"]) == r["recording_id"]]
        causes = defaultdict(list)
        excluded = Counter()
        for row in all_rows:
            reasons = _support_reasons(row, context)
            if row["occlusion"] != "none":
                reasons.append("occlusion_not_clean")
            if row["truncation"] != "none":
                reasons.append("truncation_not_clean")
            excluded.update(reasons)
            if not _support_reasons(row, context):
                causes[_cause(row, context)].append(row)
        group_support, clean_rows, match_scores = [], [], defaultdict(list)
        # Owner cells are descriptive support; a true cause has one scale weight.
        root_frames = {key[:3]: defaultdict(list) for key in causes}
        pending = False
        for key, rows in sorted(causes.items()):
            clean = [r for r in rows if r["occlusion"] == "none" and r["truncation"] == "none"]
            clean_rows.extend(clean)
            frames = defaultdict(list)
            for row in clean:
                frames[row["frame_id"]].append(_area(row))
                root_frames[key[:3]][row["frame_id"]].append(_area(row))
            score = _quantile([_quantile(v, Fraction(1, 2)) for v in frames.values()], Fraction(1, 2))
            # This actual group is a display representative, not a weighting key.
            groups = [context["groups"][gid] for gid in {r["appearance_group_id"] for r in rows}]
            representative = min(groups, key=lambda g: (seconds(g["start_seconds"]), g["appearance_group_id"]))
            group_support.append({"underlying_match_id": key[0], "appearance_group_id": representative["appearance_group_id"],
                                  "causal_root_id": key[1], "owner": key[3],
                                  "clean_frame_ids": sorted(frames),
                                  "clean_annotation_ids": sorted(r["annotation_id"] for r in clean), "score": _ratio(score)})
        for key, frames in sorted(root_frames.items()):
            score = _quantile([_quantile(v, Fraction(1, 2)) for v in frames.values()], Fraction(1, 2))
            if score is None:
                pending = True
            else:
                match_scores[key[0]].append(score)
        score = None
        if cls["basic_qualified"] and not pending:
            score = _quantile([_quantile(values, Fraction(1, 2)) for values in match_scores.values()], Fraction(1, 2))
        if cid in candidate_ids and score is not None:
            scores[cid] = score
        resolution = Counter((context["frames"][fid]["image_width"], context["frames"][fid]["image_height"])
                             for fid in {r["frame_id"] for r in reviewed})
        reports.append({"visual_class_id": cid, "basic_qualified": cls["basic_qualified"],
                        "scale_support_pending": cls["basic_qualified"] and pending, "score": _ratio(score), "scale_group": None,
                        "all_reviewed": _box_statistics(reviewed, context), "clean_representatives": _box_statistics(clean_rows, context),
                        "resolution_distribution": [{"width": w, "height": h, "frames": n} for (w, h), n in sorted(resolution.items())],
                        "excluded_reasons": [{"reason": reason, "count": n} for reason, n in sorted(excluded.items())],
                        "support": group_support})
    values = list(scores.values())
    q25, q75 = _quantile(values, Fraction(1, 4)), _quantile(values, Fraction(3, 4))
    reasons = []
    if any(r["scale_support_pending"] for r in reports if r["visual_class_id"] in candidate_ids):
        reasons.append("scale_support_pending")
    if len(values) < 2:
        reasons.append("need_two_clean_moving_candidates")
    if values and min(values) == max(values):
        reasons.append("all_moving_scores_equal")
    fallback = bool(not reasons and q25 == q75)
    if not reasons:
        for row in reports:
            value = scores.get(row["visual_class_id"])
            if value is None:
                continue
            lower, upper = (min(values), max(values)) if fallback else (q25, q75)
            row["scale_group"] = "relative_small" if value <= lower else "large" if value >= upper else "medium"
    return {"policy_id": POLICY, "candidate_class_ids": candidate_ids,
            "candidate_semantic_sha256": scale_basis_sha256(draft),
            "split_semantic_sha256": sha256(canonical_bytes(_canonical_collections(draft["split_assignment"]))).hexdigest(),
            "class_reports": reports, "cutpoints": {"q25": _ratio(q25), "q75": _ratio(q75)},
            "tie_fallback_used": fallback,
            "size_coverage_status": "SIZE_COVERAGE_INSUFFICIENT" if reasons else "SIZE_COVERAGE_SUFFICIENT",
            "blocking_reasons": reasons}


def _full_image_review(regions):
    """Exact rectangle union covers [0,1]²; neither epsilon nor clipping."""
    rectangles = [(seconds(r["x"]), seconds(r["y"]), seconds(r["x"]) + seconds(r["width"]),
                   seconds(r["y"]) + seconds(r["height"])) for r in regions]
    edges = sorted({Fraction(0), Fraction(1)} | {x for r in rectangles for x in (r[0], r[2])})
    for left, right in zip(edges, edges[1:]):
        intervals = sorted((top, bottom) for x0, top, x1, bottom in rectangles if x0 <= left and x1 >= right)
        covered = Fraction(0)
        for top, bottom in intervals:
            if top > covered:
                return False
            covered = max(covered, bottom)
        if covered < 1:
            return False
    return True


def frame_export_reasons(draft: MulticlassDraft, frame_id: str) -> list[str]:
    """Shared whole-frame export gate, including empty-frame review evidence."""
    validate_multiclass_shape(draft)
    context = _context(draft)
    if frame_id not in context["frames"]:
        raise EvidenceError("Unknown multiclass frame identity.")
    return _frame_export_reasons(draft, context["frames"][frame_id], context)


def _frame_export_reasons(draft, frame, context):
    reasons = []
    selected = set(draft["selection"]["selected_class_ids"]) if draft["selection"] else set()
    record = context["records"][frame["recording_id"]]
    if context["primary"].get(record["underlying_match_id"]) != frame["recording_id"]:
        reasons.append("not_primary_development_recording")
    if not selected:
        reasons.append("selection_missing")
    if frame["review_state"] != "complete":
        reasons.append("frame_review_not_complete")
    coverage = context["coverage"].get(frame["frame_id"])
    if coverage is None or coverage["exhaustive_state"] != "complete":
        reasons.append("coverage_not_complete")
    else:
        if not selected <= set(coverage["exhaustive_for_classes"]):
            reasons.append("selected_class_coverage_missing")
        if not _full_image_review(coverage["reviewed_regions"]):
            reasons.append("full_image_review_missing")
        if coverage["ignore_reasons"] or any(not r["visual_class_ids"] or selected.intersection(r["visual_class_ids"])
                                            for r in coverage["ignore_regions"]):
            reasons.append("selected_ignore_without_loss_mask")
        actual = frame["raw_pts"] * rational(frame["time_base"]) - record["origin_pts"] * rational(record["origin_time_base"])
        instant = seconds(float(actual))
        if any((not r["visual_class_ids"] or selected.intersection(r["visual_class_ids"]))
               and seconds(r["start_seconds"]) <= instant
               and (instant < seconds(r["end_seconds"]) or
                    (instant == seconds(r["end_seconds"]) == seconds(record["last_frame_seconds"])))
               for r in coverage["unknown_intervals"]):
            reasons.append("selected_unknown_interval")
    for row in context["annotations"][frame["frame_id"]]:
        if row["visual_class_id"] in selected and (
                row["review_state"] != "verified" or row["owner"] not in ("own", "opponent") or row["observed_form"] != "normal"):
            reasons.append("selected_observation_not_exportable")
    return sorted(set(reasons))


def _snapshot_matches(snapshot, draft, candidate, scale):
    _validate_types(snapshot, ScaleSnapshot)
    envelope = {k: v for k, v in snapshot.items() if k != "digest"}
    payload = snapshot["payload"]
    if sha256(canonical_bytes(envelope)).hexdigest() != snapshot["digest"]:
        return False
    validate_multiclass_shape(payload["draft"])
    if (payload["draft"]["selection"] is not None or payload["draft"]["backend_label_maps"]
            or payload["draft_semantic_sha256"] != scale_basis_sha256(payload["draft"])
            or payload["draft_semantic_sha256"] != scale_basis_sha256(draft)
            or payload["candidate_report"] != candidate or payload["scale_report"] != scale):
        return False
    return draft["selection"] is None or draft["selection"]["scale_snapshot_digest"] == snapshot["digest"]


def multiclass_readiness(draft: MulticlassDraft, scale_snapshot: ScaleSnapshot | None = None) -> ReadinessReport:
    """Prospective data eligibility, NOT a checked lock or training permission."""
    invalid = {"status": "INVALID_DATASET", "ready": False, "blocking_reasons": ["invalid_multiclass_shape"],
               "candidate_report": None, "scale_report": None, "export_support": []}
    try:
        validate_multiclass_shape(draft)
        candidate, scale = candidate_eligibility(draft), development_scale_report(draft)
    except EvidenceError:
        return invalid
    if scale_snapshot is not None:
        try:
            if not _snapshot_matches(scale_snapshot, draft, candidate, scale):
                raise EvidenceError("Scale snapshot differs from current full candidate evidence.")
        except EvidenceError:
            return {**invalid, "blocking_reasons": ["invalid_or_stale_scale_snapshot"]}
    context = _context(draft)
    reasons = list(candidate["reasons"])
    size_reasons = list(scale["blocking_reasons"])
    selection = draft["selection"]
    selected = sorted(selection["selected_class_ids"]) if selection else []
    if not 3 <= len(selected) <= 5:
        reasons.append("select_three_to_five_classes")
    classes = {r["visual_class_id"]: r for r in draft["taxonomy"]["classes"]}
    moving = [cid for cid in selected if classes[cid]["kind"] == "unit" and classes[cid]["mobility"] == "moving"]
    if len(moving) < 2:
        reasons.append("need_two_selected_moving_classes")
    selected_scales = {r["scale_group"] for r in scale["class_reports"] if r["visual_class_id"] in moving}
    if "relative_small" not in selected_scales:
        size_reasons.append("need_selected_relative_small")
    if not selected_scales.intersection({"medium", "large"}):
        size_reasons.append("need_selected_medium_or_large")
    eligible_frames = {fid for fid, frame in context["frames"].items() if not _frame_export_reasons(draft, frame, context)}
    rows = [r for r in draft["annotations"] if r["frame_id"] in eligible_frames and not _support_reasons(r, context)]
    export = []
    for cid in selected:
        if cid not in candidate["qualified_class_ids"]:
            reasons.append(f"selected_class_not_basic_qualified:{cid}")
        for owner in ("opponent", "own"):
            cells = []
            for split in SPLITS:
                exclusions = set()
                for row in draft["annotations"]:
                    if row["visual_class_id"] == cid and row["owner"] == owner and context["records"][row["recording_id"]]["split"] == split:
                        exclusions.update(_support_reasons(row, context))
                        exclusions.update(_frame_export_reasons(draft, context["frames"][row["frame_id"]], context))
                cell = _support(rows, cid, owner, split, context, exclusions)
                cells.append(cell)
                if owner == "opponent" and cell["qualification"] != "qualified":
                    reasons.append(f"missing_export_opponent:{cid}:{split}")
            if owner == "own" and any(c["qualification"] != "qualified" for c in cells):
                for cell in cells:
                    cell["qualification"] = "not_qualified"
                    cell["reasons"] = sorted(set(cell["reasons"]) | {"own_control_incomplete"})
            export.append({"joint_label": f"{cid}::{owner}", "visual_class_id": cid, "owner": owner, "support": cells})
    if not any(r["owner"] == "own" and all(c["qualification"] == "qualified" for c in r["support"]) for r in export):
        reasons.append("need_own_control_in_both_splits")
    sources = {r["source_id"]: r for r in draft["provenance"]}
    provenance_reasons = []
    for sid in sorted({context["records"][rid]["source_id"] for rid in context["primary"].values()}):
        source = sources[sid]
        if source["allowed_scope"] != "development_training" or source["license_evidence"] is None:
            provenance_reasons.append(f"source_not_training_qualified:{sid}")
    blocking = sorted(set(reasons + size_reasons + provenance_reasons))
    status = ("PROVENANCE_INSUFFICIENT" if provenance_reasons else "SIZE_COVERAGE_INSUFFICIENT" if size_reasons
              else "DATA_INSUFFICIENT" if reasons else "MULTICLASS_DATASET_READY")
    return {"status": status, "ready": not blocking, "blocking_reasons": blocking,
            "candidate_report": candidate, "scale_report": scale, "export_support": export}
