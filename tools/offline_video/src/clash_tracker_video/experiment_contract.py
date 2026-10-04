"""Closed development-draft v1 schema; provenance is a human declaration."""
from datetime import datetime
import re

from .evidence_contract import EvidenceError, SCHEMAS, valid_type


FORMS = {"normal", "evolved", "unknown"}
FORM_TO_V1 = {"normal": "normal", "evolved": "known_evolution", "unknown": "unknown"}


def _object(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise EvidenceError("Invalid development object fields.")


def _text(value):
    if not valid_type(value, "id"):
        raise EvidenceError("Nonempty development text required.")


def _enum(value, choices):
    if type(value) is not str or value not in choices:
        raise EvidenceError("Unsupported development value.")


def _integer(value, minimum=1):
    if type(value) is not int or value < minimum:
        raise EvidenceError("Invalid development integer.")


def _boolean(value):
    if type(value) is not bool:
        raise EvidenceError("Invalid development boolean.")


def utc_time(value):
    """Accept explicit UTC only, without local timezone interpretation."""
    if type(value) is not str or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
        raise EvidenceError("Explicit UTC creation time required.")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError("Invalid UTC creation time.") from exc


def _v1_shape(evidence):
    required = {"schema_version", *SCHEMAS}
    if type(evidence) is not dict or not required <= set(evidence) or set(evidence) - required - {"preparation_report"}:
        raise EvidenceError("Invalid v1 evidence bundle fields.")
    # Reuse v1 validation for semantics below, but require all optional advisory
    # objects to be closed too: they cannot smuggle predictions into a snapshot.
    if "preparation_report" in evidence:
        report = evidence["preparation_report"]
        _object(report, {"status", "candidate_gate", "experiment_gate", "counts", "reasons", "coverage_gaps"})
        _object(report["counts"], {"recordings", "reviewed_complete_segments", "verified_plays", "annotated_key_frames"})
        if type(report["coverage_gaps"]) is not list:
            raise EvidenceError("Invalid advisory coverage gaps.")
        for gap in report["coverage_gaps"]:
            _object(gap, {"recording_id", "match_segment_id", "start_seconds", "end_seconds"})
            if (not valid_type(gap["recording_id"], "id")
                    or not valid_type(gap["match_segment_id"], "nullable_id")
                    or not valid_type(gap["start_seconds"], "seconds")
                    or not valid_type(gap["end_seconds"], "seconds")
                    or gap["start_seconds"] > gap["end_seconds"]):
                raise EvidenceError("Invalid advisory coverage gap.")


def validate_draft_shape(draft):
    """Validate all new nested fields before any semantic indexing or hashing."""
    _object(draft, {"schema_version", "experiment_id", "freeze_version", "created_at",
                    "protocol_version", "policy_version", "identity", "candidates",
                    "selection", "unknown_intervals"})
    for field in ("schema_version", "protocol_version", "policy_version"):
        if type(draft[field]) is not int or draft[field] != 1:
            raise EvidenceError("Unsupported development schema or policy version.")
    _integer(draft["freeze_version"])
    _text(draft["experiment_id"])
    utc_time(draft["created_at"])
    identity = draft["identity"]
    identity_fields = {"underlying_match_id", "recording_id", "split", "provenance",
                       "complete_recording", "unedited_recording", "full_human_review"}
    completion_fields = {"completion_attestation", "terminal_result_screen_present"}
    # Old drafts stay valid; new paired metadata records provenance, not a UI gate.
    if type(identity) is dict and set(identity) & completion_fields:
        _object(identity, identity_fields | completion_fields)
        _enum(identity["completion_attestation"], {"user_confirmed"})
        _boolean(identity["terminal_result_screen_present"])
    else:
        _object(identity, identity_fields)
    for field in ("underlying_match_id", "recording_id"):
        _text(identity[field])
    _enum(identity["split"], {"development"})
    _enum(identity["provenance"], {"new_natural"})
    for field in ("complete_recording", "unedited_recording", "full_human_review"):
        _boolean(identity[field])
        if not identity[field]:
            raise EvidenceError("Complete unedited whole-match human review required.")
    if type(draft["candidates"]) is not list or type(draft["unknown_intervals"]) is not list:
        raise EvidenceError("Development collections must be arrays.")
    for candidate in draft["candidates"]:
        _object(candidate, {"candidate_id", "card_id", "form", "notes", "evidence", "deployments", "evolution"})
        _text(candidate["candidate_id"])
        _text(candidate["card_id"])
        _enum(candidate["form"], FORMS)
        _object(candidate["notes"], {"distinctness", "visibility", "occlusion", "owner_clarity", "form_clarity"})
        for note in candidate["notes"].values():
            _text(note)
        _v1_shape(candidate["evidence"])
        evolution = candidate["evolution"]
        _object(evolution, {"capable", "equipped", "charge_requirement", "rules_version"})
        _boolean(evolution["capable"])
        _enum(evolution["equipped"], {"verified", "not_equipped", "unknown"})
        if evolution["charge_requirement"] is not None:
            _integer(evolution["charge_requirement"])
        if evolution["rules_version"] is not None:
            _text(evolution["rules_version"])
        if not evolution["capable"] and (evolution["equipped"] == "verified" or evolution["charge_requirement"] is not None):
            raise EvidenceError("Conflicting evolution capability metadata.")
        if candidate["form"] == "evolved" and not evolution["capable"]:
            raise EvidenceError("Known evolved form requires evolution capability.")
        if candidate["form"] == "evolved" and evolution["equipped"] == "not_equipped":
            raise EvidenceError("Known evolved form conflicts with unequipped evolution.")
        if type(candidate["deployments"]) is not list:
            raise EvidenceError("Deployment annotations must be an array.")
        for deployment in candidate["deployments"]:
            _object(deployment, {"play_id", "clear", "form", "possible_missed_play", "evolution"})
            _text(deployment["play_id"])
            _boolean(deployment["clear"])
            _boolean(deployment["possible_missed_play"])
            _enum(deployment["form"], FORMS)
            progress = deployment["evolution"]
            _object(progress, {"progress", "remaining_count", "source"})
            _enum(progress["progress"], {"known", "unknown"})
            _enum(progress["source"], {"manual"})
            if progress["remaining_count"] is not None:
                _integer(progress["remaining_count"], 0)
            if (progress["progress"] == "unknown") != (progress["remaining_count"] is None):
                raise EvidenceError("Unknown evolution progress requires null remaining count.")
    selection = draft["selection"]
    if selection is not None:
        _object(selection, {"candidate_id", "card_id", "form", "method", "reason"})
        for field in ("candidate_id", "card_id", "reason"):
            _text(selection[field])
        _enum(selection["form"], FORMS)
        _enum(selection["method"], {"manual"})
    for interval in draft["unknown_intervals"]:
        _object(interval, {"unknown_id", "recording_id", "start_seconds", "end_seconds", "reason"})
        for field in ("unknown_id", "recording_id", "reason"):
            _text(interval[field])
        if (not valid_type(interval["start_seconds"], "seconds")
                or not valid_type(interval["end_seconds"], "seconds")
                or interval["start_seconds"] > interval["end_seconds"]):
            raise EvidenceError("Invalid unknown interval bounds.")
