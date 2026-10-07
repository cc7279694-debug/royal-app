"""Versioned, conservative visual-review contract independent of old GT locks."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from fractions import Fraction


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def bundle_digest(bundle: dict) -> str:
    return digest({k: v for k, v in bundle.items() if k != "bundle_sha256"})


def frame_id(recording: str, pts: int, time_base: str) -> str:
    return "f-" + digest([recording, str(Fraction(pts) * Fraction(time_base))])[:24]


def proposal_id(prediction_sha: str, recording: str, pts: int, time_base: str, row: int) -> str:
    return "p-" + digest([prediction_sha, recording, str(Fraction(pts) * Fraction(time_base)), row])[:24]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def visual_class(value: object) -> None:
    require(isinstance(value, str) and re.fullmatch(
        r"visual\.(unit|structure|effect|ui|other)\.[a-z0-9]+(?:[._-][a-z0-9]+)*", value) is not None,
        "visual_class must be an explicit visual.unit/structure/effect/ui/other label")


def bbox(value: object, width: int, height: int) -> None:
    require(isinstance(value, list) and len(value) == 4, "bbox must contain four xyxy coordinates")
    require(all(type(v) in (int, float) and math.isfinite(v) for v in value), "bbox coordinates must be finite")
    x1, y1, x2, y2 = value
    require(0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height, "bbox is outside source bounds or empty")


def validate_bundle(bundle: dict) -> None:
    require(bundle.get("schema") == "preannotation_bundle_v1", "unsupported bundle schema")
    inventory = bundle.get("inventory", [])
    require([x.get("recording_id") for x in inventory] == [f"natural_match_0{i}" for i in range(1, 5)],
            "retained recording inventory must preserve 01,02,03,04 order")
    require([x.get("intake_order") for x in inventory] == [1, 2, 3, 4], "invalid intake order")
    require(inventory[1].get("truncated") is True and inventory[1].get("training_excluded") is True,
            "truncated match02 must remain excluded from training")
    require(bundle.get("recording_id") in [x["recording_id"] for x in inventory], "recording absent from inventory")
    require(isinstance(bundle.get("prediction_sha256"), str) and
            re.fullmatch(r"[a-f0-9]{64}", bundle["prediction_sha256"]) is not None, "invalid prediction SHA256")
    require(isinstance(bundle.get("frames"), list) and bool(bundle["frames"]), "bundle has no frames")
    frames_seen, proposals_seen = set(), set()
    for frame in bundle["frames"]:
        fid = frame.get("frame_id")
        require(isinstance(fid, str) and fid not in frames_seen, "duplicate or missing frame identity")
        frames_seen.add(fid)
        require(type(frame.get("raw_pts")) is int, "exact raw PTS required")
        try:
            require(Fraction(frame["time_base"]) > 0, "time_base must be positive")
        except (KeyError, TypeError, ZeroDivisionError):
            raise ValueError("invalid exact time_base") from None
        require(type(frame.get("width")) is int and frame["width"] > 0 and
                type(frame.get("height")) is int and frame["height"] > 0, "invalid source dimensions")
        for proposal in frame.get("proposals", []):
            pid = proposal.get("proposal_id")
            require(isinstance(pid, str) and pid not in proposals_seen, "duplicate proposal identity")
            proposals_seen.add(pid)
            require(proposal.get("status") == "pending", "immutable proposals must stay pending")
            bbox(proposal.get("bbox_xyxy"), frame["width"], frame["height"])
            require(isinstance(proposal.get("raw_teacher"), dict), "raw teacher fields must be preserved")
    if "bundle_sha256" in bundle:
        require(bundle["bundle_sha256"] == bundle_digest(bundle), "bundle digest mismatch")


def return_template(bundle: dict) -> dict:
    validate_bundle(bundle)
    return {
        "schema": "preannotation_human_return_v1", "bundle_sha256": bundle_digest(bundle),
        "provenance": {"kind": "human", "reviewer": "", "human_review_attested": False, "synthetic": False},
        "frames": [{"frame_id": f["frame_id"], "coverage": [], "decisions": []} for f in bundle["frames"]],
    }


def validate_return(bundle: dict, returned: dict, *, allow_synthetic: bool = False) -> dict:
    validate_bundle(bundle)
    require(set(returned) == {"schema", "bundle_sha256", "provenance", "frames"}, "unexpected return fields")
    require(returned.get("schema") == "preannotation_human_return_v1", "unsupported return schema")
    require(returned.get("bundle_sha256") == bundle_digest(bundle), "return is bound to another bundle")
    provenance = returned.get("provenance", {})
    require(set(provenance) <= {"kind", "reviewer", "human_review_attested", "synthetic", "reviewed_at"},
            "unexpected reviewer provenance")
    require(isinstance(provenance.get("reviewer"), str) and bool(provenance["reviewer"].strip()), "actual reviewer required")
    synthetic = provenance.get("kind") == "synthetic"
    if synthetic:
        require(allow_synthetic and provenance.get("synthetic") is True and
                provenance.get("human_review_attested") is False, "synthetic correction cannot be imported as human GT")
    else:
        require(provenance.get("kind") == "human" and provenance.get("synthetic") is False and
                provenance.get("human_review_attested") is True, "explicit actual human review attestation required")
        require(bundle.get("synthetic", False) is False, "synthetic bundle cannot become real human GT")
    returned_frames = returned.get("frames")
    require(isinstance(returned_frames, list), "return frames must be an array")
    require([f.get("frame_id") for f in returned_frames] == [f["frame_id"] for f in bundle["frames"]],
            "return must preserve every frame exactly once and in bundle order")
    excluded = next(x for x in bundle["inventory"] if x["recording_id"] == bundle["recording_id"])["training_excluded"]
    positives, unresolved, negatives, groups, group_labels, group_metadata, coverage_export = [], [], [], {}, {}, {}, []
    decision_keys = {"proposal_id", "manual_id", "action", "decision", "visual_class", "canonical_mapping",
                     "bbox_xyxy", "owner", "form", "origin", "appearance_id", "visibility", "uncertainty", "note"}
    for frame, reviewed in zip(bundle["frames"], returned_frames, strict=True):
        require(set(reviewed) == {"frame_id", "coverage", "decisions"}, "unexpected review frame fields")
        require(isinstance(reviewed["decisions"], list) and isinstance(reviewed["coverage"], list), "review arrays required")
        proposals = {p["proposal_id"]: p for p in frame["proposals"]}
        seen, manual_seen = set(), set()
        frame_unresolved, frame_positives = [], []
        for decision in reviewed["decisions"]:
            require(set(decision) <= decision_keys, "unexpected human decision fields")
            action, state = decision.get("action"), decision.get("decision")
            require(action in {"accept", "reject", "relabel", "bbox-correct", "missing-box"}, "unsupported edit action")
            require(state in {"accepted", "rejected", "unknown", "pending"}, "invalid human decision")
            pid = decision.get("proposal_id")
            if action == "missing-box":
                mid = decision.get("manual_id")
                require(pid is None and isinstance(mid, str) and bool(mid.strip()) and mid not in manual_seen,
                        "missing-box requires a unique manual identity, not a teacher proposal")
                manual_seen.add(mid)
                oid, raw = f"manual:{frame['frame_id']}:{mid}", None
            else:
                require(pid in proposals and pid not in seen, "unknown or duplicated proposal decision")
                seen.add(pid)
                oid, raw = pid, proposals[pid]["raw_teacher"]
            require((action != "reject" or state == "rejected") and
                    (state != "rejected" or action == "reject"), "reject action and decision disagree")
            if decision.get("visual_class") is not None or state == "accepted":
                visual_class(decision.get("visual_class"))
            mapping = decision.get("canonical_mapping")
            require(mapping is None or (isinstance(mapping, str) and
                    re.fullmatch(r"(unit|building|spell|effect|structure|ui)\.[a-z0-9]+(?:[._-][a-z0-9]+)*", mapping)),
                    "invalid explicit canonical mapping")
            bbox(decision.get("bbox_xyxy"), frame["width"], frame["height"])
            if action in {"accept", "relabel"} and state == "accepted":
                require(decision["bbox_xyxy"] == proposals[pid]["bbox_xyxy"], "changed box requires bbox-correct action")
            require(decision.get("owner") in {"own", "opponent", "neutral", "unknown"}, "invalid human owner")
            require(decision.get("form") in {"normal", "evolved", "other", "unknown"}, "invalid human form")
            require(decision.get("origin") in {"independent", "spawned", "clone", "transformed", "unknown"}, "invalid visual origin")
            if decision.get("appearance_id") is not None or state == "accepted":
                require(isinstance(decision.get("appearance_id"), str) and
                        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}", decision["appearance_id"]), "appearance identity required")
            require(decision.get("visibility") in {"visible", "occluded", "unknown"}, "invalid visibility")
            require(decision.get("uncertainty") in {"none", "uncertain", "unknown"}, "invalid uncertainty")
            require(isinstance(decision.get("note", ""), str), "note must be text")
            confirmed = state == "accepted" and decision["uncertainty"] == "none" and decision["visibility"] != "unknown"
            box = {**copy.deepcopy(decision), "object_id": oid, "frame_id": frame["frame_id"],
                   "recording_id": bundle["recording_id"], "raw_teacher": copy.deepcopy(raw),
                   "human_confirmed": confirmed and not synthetic}
            if not confirmed:
                frame_unresolved.append(box)
            else:
                aid = decision["appearance_id"]
                label = (decision["visual_class"], mapping)
                require(aid not in group_labels or group_labels[aid] == label, "appearance group changed visual identity")
                group_labels[aid] = label
                known = group_metadata.setdefault(aid, {})
                for field in ("owner", "form", "origin"):
                    value = decision[field]
                    if value != "unknown":
                        require(field not in known or known[field] == value, "appearance group has conflicting known metadata")
                        known[field] = value
                groups.setdefault(aid, []).append(oid)
                frame_positives.append(box)
        for pid, proposal in proposals.items():
            if pid not in seen:
                frame_unresolved.append({"object_id": pid, "frame_id": frame["frame_id"], "decision": "pending",
                                         "visual_class": None, "bbox_xyxy": proposal["bbox_xyxy"],
                                         "raw_teacher": copy.deepcopy(proposal["raw_teacher"]), "human_confirmed": False})
        classes_seen = set()
        for coverage in reviewed["coverage"]:
            require(set(coverage) == {"visual_class", "exhaustive", "scope", "unresolved"}, "invalid coverage fields")
            visual_class(coverage["visual_class"])
            cls = coverage["visual_class"]
            require(cls not in classes_seen, "duplicate class coverage")
            classes_seen.add(cls)
            require(type(coverage["exhaustive"]) is bool and type(coverage["unresolved"]) is bool and
                    coverage["scope"] == "full_frame", "coverage requires explicit full-frame booleans")
            coverage_export.append({"frame_id": frame["frame_id"], **copy.deepcopy(coverage)})
            if (not synthetic and not excluded and coverage["exhaustive"] and not coverage["unresolved"] and
                    not any(b["visual_class"] == cls for b in frame_positives) and
                    not frame_unresolved):
                negatives.append({"frame_id": frame["frame_id"], "visual_class": cls})
        positives.extend(frame_positives)
        unresolved.extend(frame_unresolved)
    return {"schema": "preannotation_review_revision_v1", "bundle_sha256": bundle_digest(bundle),
            "status": "synthetic_not_gt" if synthetic else "human_reviewed_visual_annotations",
            "provenance": copy.deepcopy(provenance), "positive_boxes": positives, "unresolved_regions": unresolved,
            "coverage": coverage_export, "negative_evidence": negatives, "appearance_groups": groups,
            "training_excluded": excluded, "training_qualified": False,
            "ordinary_training_export_allowed": False, "card_events": [], "independent_deployments": 0,
            "supervision_policy": "positive_only_requires_unknown_safe_consumer; unreviewed frame is not background"}
