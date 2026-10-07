"""Annotation-only, user-attested Event GT snapshots; no automatic event engine.

The embedded source and supplied byte SHA are evidence bindings, not proof of
source authenticity. Timestamps remain approximate human-review annotations.
"""
from __future__ import annotations

import copy
import json
import math
import re
import stat
from pathlib import Path

from tools.preannotation.bundle import parse_json_bytes
from tools.preannotation.contract import digest

from .bundle import _path, validate_plan


MAX_LOCK_BYTES = 8 * 1024 * 1024
SCHEMA = "deployment_event_gt_lock_v1"
PLAN_FIELDS = {"schema", "inventory", "evidence_sources", "candidates", "baseline_commit",
               "confirmed_event_count", "independent_confirmed_card_play_count", "negative_evidence",
               "event_gt_lock_created", "omitted_visuals", "selection_method", "visual_gt_not_event_gt"}
RETURN_FIELDS = {"schema", "reviewer", "actual_human_confirmation", "human_review_attested",
                 "review_basis", "confirmation_source", "source_binding", "negative_evidence", "decisions"}
CANDIDATE_FIELDS = {"candidate_id", "underlying_match_id", "recording_id", "approximate_timestamp", "timestamp_kind",
                    "owner", "card_id", "form", "event_type", "evaluable", "confidence", "review_state",
                    "evidence_visual_classes", "evidence_frame_ids", "visual_refs", "candidate_reason", "notes",
                    "duplicate_hint", "context"}
ROW_FIELDS = {
    "confirm": {"candidate_id", "decision", "event_confirmation", "owner", "card_id", "form",
                "approximate_timestamp", "event_type", "evaluable", "confidence", "notes"},
    "uncertain": {"candidate_id", "decision", "event_confirmation", "evaluable", "uncertainty_reason", "notes"},
    "continuity": {"candidate_id", "decision", "no_new_card_play", "continuity_with", "notes"},
    "merge_duplicate": {"candidate_id", "decision", "no_new_card_play", "merge_duplicate_of", "notes"},
}
VISUAL_CARD = {"visual.unit.witch": "witch", "visual.unit.golden_knight": "golden_knight",
               "visual.unit.flying_machine": "flying_machine", "visual.unit.minion": "minions",
               "visual.unit.royal_hog": "royal_hogs", "visual.structure.mortar": "mortar",
               "visual.unit.skeleton_barrel": "skeleton_barrel"}
CARD_MAPPING = {"witch": "unit.witch", "golden_knight": "unit.golden-knight", "flying_machine": "unit.flying-machine",
                "minions": "unit.minion", "royal_hogs": "unit.royal-hog", "mortar": "building.mortar",
                "skeleton_barrel": "unit.skeleton-barrel"}
LIMITATIONS = {"annotation_only": True, "timestamps_are_approximate": True,
               "cross_match_validation": False, "detector_performance": False,
               "full_match_coverage": False, "eight_card_state": False, "cycle_state": False,
               "elixir_state": False, "source_authenticity_verified": False}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _fields(value: dict, expected: set[str], label: str) -> None:
    _require(isinstance(value, dict) and set(value) == expected, f"invalid {label} fields")


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _validate_inputs(plan: dict, returned: dict, freeze_version: int) -> None:
    _require(type(freeze_version) is int and freeze_version == 1, "only freeze version 1 is supported")
    _require(isinstance(plan, dict) and set(plan) <= PLAN_FIELDS, "unsupported source-plan claims")
    try:
        validate_plan(plan)
    except (KeyError, TypeError, AttributeError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("invalid source plan") from error
    for candidate in plan["candidates"]:
        _fields(candidate, CANDIDATE_FIELDS, "source candidate")
        for key in ("evidence_visual_classes", "evidence_frame_ids"):
            values = candidate[key]
            _require(isinstance(values, list) and bool(values)
                     and all(isinstance(value, str) and bool(value) for value in values)
                     and len(set(values)) == len(values), "source evidence references must be unique text lists")
    _fields(returned, RETURN_FIELDS, "human return")
    _require(returned["schema"] == "deployment_event_human_return_v1", "unsupported human return")
    _require(returned["reviewer"] == "user" and returned["actual_human_confirmation"] is True
             and returned["human_review_attested"] is True
             and returned["review_basis"] == "chatgpt_visual_review"
             and returned["confirmation_source"] == "user_attestation_based_on_chatgpt_visual_review",
             "explicit user attestation of ChatGPT visual review required")
    binding = returned["source_binding"]
    _fields(binding, {"source_plan_digest", "source_plan_file_sha256"}, "source binding")
    _require(_sha(binding["source_plan_file_sha256"]) and binding["source_plan_digest"] == digest(plan),
             "source snapshot differs from reviewed binding")
    _require(returned["negative_evidence"] == [], "uncertain or duplicate review cannot create Negative evidence")
    rows = returned["decisions"]
    _require(isinstance(rows, list), "candidate decisions required")
    candidates = {candidate["candidate_id"]: candidate for candidate in plan["candidates"]}
    seen = set()
    for row in rows:
        _require(isinstance(row, dict) and isinstance(row.get("decision"), str), "invalid candidate decision")
        kind = row["decision"]
        _require(kind in ROW_FIELDS, "pending or unsupported decision")
        _fields(row, ROW_FIELDS[kind], "candidate decision")
        cid = row["candidate_id"]
        _require(isinstance(cid, str) and cid in candidates and cid not in seen, "unknown or duplicate candidate decision")
        seen.add(cid)
        _require(isinstance(row["notes"], str), "candidate notes must be text")
        candidate = candidates[cid]
        if kind == "confirm":
            _require(row["owner"] == "opponent" and candidate["owner"] == "opponent"
                     and all(reference["owner"] == "opponent" for reference in candidate["visual_refs"]),
                     "only opponent evidence can confirm an opponent deployment")
            card = row["card_id"]
            _require(isinstance(card, str) and card in set(VISUAL_CARD.values())
                     and card == candidate["card_id"]
                     and all(VISUAL_CARD.get(visual) == card for visual in candidate["evidence_visual_classes"]),
                     "confirmation requires supported non-null visual/card mapping")
            _require(all(("canonical_mapping" not in reference or reference["canonical_mapping"] == CARD_MAPPING[card])
                         and reference.get("origin", "unknown") in {"independent", "unknown"}
                         for reference in candidate["visual_refs"]), "null-mapped or spawned visual reference cannot confirm a play")
            expected_type = "grouped" if card in {"minions", "royal_hogs"} else "direct"
            _require(row["event_type"] == expected_type and row["form"] in {"normal", "evolved", "unknown"}
                     and row["event_confirmation"] == "confirmed_new_deployment"
                     and row["evaluable"] is True and row["confidence"] == "human_confirmed",
                     "explicit confirmed new-deployment fields required")
            timestamp = row["approximate_timestamp"]
            _require(type(timestamp) in (int, float) and math.isfinite(timestamp)
                     and candidate["context"]["start_seconds"] <= timestamp <= candidate["context"]["end_seconds"],
                     "approximate confirmed timestamp must fall inside reviewed context")
        elif kind == "uncertain":
            _require(row["evaluable"] is False and row["event_confirmation"] == "uncertain"
                     and isinstance(row["uncertainty_reason"], str) and bool(row["uncertainty_reason"].strip()),
                     "unresolved candidate must retain explicit uncertainty")
        else:
            _require(row["no_new_card_play"] is True, "continuity/duplicate outcome must explicitly attest no new play")
    _require(seen == set(candidates), "every source candidate must receive exactly one decision")
    indices = {candidate["candidate_id"]: index for index, candidate in enumerate(plan["candidates"])}
    decisions = {row["candidate_id"]: row for row in rows}
    for row in rows:
        kind = row["decision"]
        if kind not in {"continuity", "merge_duplicate"}:
            continue
        key = "continuity_with" if kind == "continuity" else "merge_duplicate_of"
        target, cid = row[key], row["candidate_id"]
        _require(isinstance(target, str) and target in indices and indices[target] < indices[cid]
                 and candidates[target]["underlying_match_id"] == candidates[cid]["underlying_match_id"],
                 "continuity/duplicate target must be earlier in the same underlying match")
        if kind == "merge_duplicate":
            _require(decisions[target]["decision"] == "confirm", "duplicate target must resolve to a confirmed event")


def build_lock(plan: dict, human_return: dict, freeze_version: int = 1) -> dict:
    """Derive a deterministic v1 lock from a bound pending plan and human return."""
    plan, returned = copy.deepcopy(plan), copy.deepcopy(human_return)
    _validate_inputs(plan, returned, freeze_version)
    decisions = {row["candidate_id"]: row for row in returned["decisions"]}
    events, outcomes, unresolved = [], [], []
    for candidate in plan["candidates"]:
        cid = candidate["candidate_id"]
        row = decisions[cid]
        kind = row["decision"]
        if kind == "confirm":
            events.append({"event_gt_id": f"event-gt-{cid}", "candidate_id": cid,
                           "underlying_match_id": candidate["underlying_match_id"], "recording_id": candidate["recording_id"],
                           **{key: row[key] for key in ("approximate_timestamp", "owner", "card_id", "form", "event_type",
                                                       "evaluable", "confidence", "notes")},
                           "evidence_visual_classes": candidate["evidence_visual_classes"],
                           "evidence_frame_ids": candidate["evidence_frame_ids"], "source_visual_group": candidate["visual_refs"]})
        elif kind == "uncertain":
            unresolved.append({**row, "underlying_match_id": candidate["underlying_match_id"],
                               "recording_id": candidate["recording_id"]})
        else:
            key = "continuity_with" if kind == "continuity" else "merge_duplicate_of"
            target = row[key]
            outcomes.append({**row, "underlying_match_id": candidate["underlying_match_id"],
                             "recording_id": candidate["recording_id"],
                             "resolved_event_gt_id": f"event-gt-{target}" if decisions[target]["decision"] == "confirm" else None})
    summary = {"reviewed_candidate_count": len(plan["candidates"]), "confirmed_event_count": len(events),
               "continuity_dedupe_count": len(outcomes), "unresolved_candidate_count": len(unresolved), "negative_evidence_count": 0,
               "reviewed_underlying_matches": list(dict.fromkeys(c["underlying_match_id"] for c in plan["candidates"])),
               "confirmed_event_underlying_matches": list(dict.fromkeys(e["underlying_match_id"] for e in events))}
    lock = {"schema": SCHEMA, "freeze_version": freeze_version, "freeze_identity": "deployment-event-gt:" + digest(plan),
            "source_plan": plan, "human_return": returned, "confirmed_events": events,
            "continuity_dedupe_outcomes": outcomes, "unresolved_candidates": unresolved,
            "negative_evidence": [], "summary": summary, "limitations": copy.deepcopy(LIMITATIONS)}
    lock["lock_digest"] = digest(lock)
    return lock


def validate_lock(envelope: dict) -> None:
    """Check the entire digest and reconstruct derived semantics from source."""
    expected_fields = {"schema", "freeze_version", "freeze_identity", "source_plan", "human_return", "confirmed_events",
                       "continuity_dedupe_outcomes", "unresolved_candidates", "negative_evidence", "summary", "limitations", "lock_digest"}
    _fields(envelope, expected_fields, "lock")
    _require(envelope["schema"] == SCHEMA, "unsupported lock schema")
    _require(_sha(envelope["lock_digest"]) and envelope["lock_digest"] == digest({key: value for key, value in envelope.items()
                                                                               if key != "lock_digest"}), "lock digest mismatch")
    expected = build_lock(envelope["source_plan"], envelope["human_return"], envelope["freeze_version"])
    _require(envelope == expected, "derived lock payload differs from bound human/source semantics")


def _safe_path(path: Path) -> Path:
    _require(path.is_absolute() and ".." not in path.parts and path.name not in {"", ".", ".."},
             "explicit absolute lock path without traversal required")
    _path(path.parent, path.name)
    for ancestor in (path, *path.parents):
        if ancestor.exists() or ancestor.is_symlink():
            attributes = getattr(ancestor.lstat(), "st_file_attributes", 0)
            _require(not ancestor.is_symlink() and not attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0),
                     "symlink or junction lock path")
    return path


def _read_snapshot(path: Path) -> dict:
    with path.open("rb") as handle:
        snapshot = handle.read(MAX_LOCK_BYTES + 1)
    _require(len(snapshot) <= MAX_LOCK_BYTES, "lock exceeds byte size bound")
    return parse_json_bytes(snapshot)


def load_lock(path: Path) -> dict:
    """Read one bounded, strict JSON byte snapshot and validate it completely."""
    envelope = _read_snapshot(_safe_path(Path(path)))
    validate_lock(envelope)
    return envelope


def freeze_lock(envelope: dict, explicit_new_path: Path) -> Path:
    """Create a new lock exclusively; renamed sibling v1 history also blocks it."""
    envelope = copy.deepcopy(envelope)
    validate_lock(envelope)
    target = _safe_path(Path(explicit_new_path))
    _require(target.parent.is_dir(), "explicit lock parent must already exist")
    if target.exists():
        raise FileExistsError(target)
    for sibling in target.parent.iterdir():
        _safe_path(sibling)
        if not sibling.is_file():
            continue
        try:
            existing = _read_snapshot(sibling)
        except (ValueError, UnicodeError):
            continue
        if existing.get("schema") != SCHEMA:
            continue
        validate_lock(existing)
        if existing["freeze_identity"] == envelope["freeze_identity"] and existing["freeze_version"] == envelope["freeze_version"]:
            raise FileExistsError("source/freeze-version identity already exists in sibling lock")
    snapshot = (json.dumps(envelope, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    _require(len(snapshot) <= MAX_LOCK_BYTES, "lock exceeds byte size bound")
    with target.open("xb") as handle:
        handle.write(snapshot)
    return target
