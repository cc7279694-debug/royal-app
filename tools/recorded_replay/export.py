"""Prepare an offline demo from sealed ENGINE outputs and post-replay scoring.

This module does not run or import the event engine, visual Oracle, or Event GT.
Scoring selects existing engine IDs only; it never supplies IDs or timestamps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_JS_SECONDS = 9007199254740991
CARDS = frozenset({"witch", "royal_hogs", "flying_machine", "golden_knight", "minions"})
EVENT_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PACKET_NAME = "recorded-oracle-demo.json"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _read_json(path):
    path = Path(path)
    _require(path.is_file() and path.stat().st_size <= MAX_JSON_BYTES,
             "Missing or oversized recorded replay metadata")
    raw = path.read_bytes()
    _require(len(raw) <= MAX_JSON_BYTES, "Oversized recorded replay metadata")

    def unique_keys(rows):
        result = {}
        for key, value in rows:
            _require(key not in result, "Duplicate recorded replay JSON key")
            result[key] = value
        return result

    def finite_decimal(text):
        value = float(text)
        _require(math.isfinite(value), "Non-finite recorded replay number")
        return value

    def reject_constant(_text):
        raise ValueError("Non-finite recorded replay number")

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys,
                       parse_float=finite_decimal, parse_constant=reject_constant)
    _require(isinstance(value, dict), "Recorded replay JSON object required")
    return value, hashlib.sha256(raw).hexdigest()


def _verify_directory(directory, required_member):
    root = Path(directory).resolve()
    manifest, manifest_sha = _read_json(root / "manifest.json")
    _require(manifest.get("schema") == "oracle_artifact_manifest_v1"
             and isinstance(manifest.get("files"), dict)
             and required_member in manifest["files"], "Invalid sealed artifact manifest")
    selected = None
    selected_sha = None
    for name, expected_sha in manifest["files"].items():
        _require(isinstance(name, str) and name.endswith(".json")
                 and name != "manifest.json" and not any(char in name for char in "/\\:")
                 and isinstance(expected_sha, str) and SHA256.fullmatch(expected_sha) is not None,
                 "Invalid sealed artifact member")
        path = root / name
        _require(path.resolve().is_relative_to(root), "Artifact member escaped its directory")
        value, actual_sha = _read_json(path)
        _require(actual_sha == expected_sha, "Sealed artifact SHA mismatch")
        if name == required_member:
            selected, selected_sha = value, actual_sha
    return selected, selected_sha, manifest_sha


def _seconds(value):
    return type(value) in (int, float) and 0 <= value <= MAX_JS_SECONDS and math.isfinite(value)


def _select_events(replay, evaluation):
    _require(replay.get("schema") == "oracle_event_replay_v1"
             and isinstance(replay.get("events"), list), "Invalid sealed ENGINE replay")
    _require(evaluation.get("schema") == "oracle_event_evaluation_v1"
             and evaluation.get("passed") is True, "A passing sealed evaluation is required")
    for key, expected in (("positive_hits", 5), ("positive_total", 5),
                          ("positive_duplicates", 0), ("explicit_dedupe_failures", 0)):
        _require(type(evaluation.get(key)) is int and evaluation[key] == expected,
                 "Evaluation count does not qualify for this demo")
    _require(evaluation.get("unresolved_is_negative") is False
             and evaluation.get("real_time_latency_validated") is False
             and evaluation.get("cross_match_positive_validation") is False
             and evaluation.get("detector_performance") is False
             and evaluation.get("full_timeline_false_positive_rate") is None,
             "Evaluation scope does not qualify for an offline Oracle demo")

    engine_by_id = {}
    for event in replay["events"]:
        _require(isinstance(event, dict), "Invalid ENGINE event")
        event_id = event.get("event_id")
        _require(isinstance(event_id, str) and EVENT_ID.fullmatch(event_id) is not None
                 and event_id not in engine_by_id, "Invalid or duplicate ENGINE ID")
        _require(isinstance(event.get("card_id"), str) and event["card_id"] in CARDS
                 and isinstance(event.get("match_id"), str)
                 and bool(event["match_id"]) and event.get("evidence_level") == "STRONG"
                 and event.get("rule_version") == "oracle-card-rules-v1"
                 and _seconds(event.get("timestamp")) and _seconds(event.get("confirmed_at"))
                 and event["confirmed_at"] >= event["timestamp"], "Invalid confirmed ENGINE event")
        engine_by_id[event_id] = event

    positives = evaluation.get("positives")
    unscored = evaluation.get("unscored_events")
    dedupe = evaluation.get("dedupe_outcomes")
    _require(isinstance(positives, list) and len(positives) == 5
             and isinstance(unscored, list) and len(unscored) == 4
             and isinstance(dedupe, list) and len(dedupe) == 3,
             "Expected five scored events, four unscored events, and three dedupe checks")
    for check in dedupe:
        _require(isinstance(check, dict) and type(check.get("new_event_count")) is int
                 and check["new_event_count"] == 0 and check.get("event_ids") == [],
                 "Explicit dedupe check failed")

    selected = []
    selected_ids = set()
    for positive in positives:
        _require(isinstance(positive, dict) and positive.get("hit") is True
                 and type(positive.get("matching_count")) is int
                 and positive["matching_count"] == 1, "Each scored positive must match once")
        event_id = positive.get("matched_event_id")
        _require(isinstance(event_id, str) and event_id in engine_by_id
                 and event_id not in selected_ids, "Scored positive lacks a unique ENGINE ID")
        event = engine_by_id[event_id]
        _require(positive.get("card_id") == event["card_id"], "Scored and ENGINE cards differ")
        selected_ids.add(event_id)
        selected.append(event)
    _require({event["card_id"] for event in selected} == CARDS
             and len({event["match_id"] for event in selected}) == 1,
             "Demo requires five original cards from one match")

    unscored_ids = set()
    for row in unscored:
        _require(isinstance(row, dict), "Invalid unscored event metadata")
        event_id = row.get("event_id")
        _require(isinstance(event_id, str) and event_id in engine_by_id
                 and event_id not in selected_ids and event_id not in unscored_ids,
                 "Unscored IDs overlap or lack an ENGINE event")
        event = engine_by_id[event_id]
        _require(all(row.get(key) == event[key] for key in ("card_id", "match_id", "timestamp")),
                 "Unscored metadata differs from ENGINE output")
        unscored_ids.add(event_id)
    _require(set(engine_by_id) == selected_ids | unscored_ids,
             "Scored and unscored IDs do not partition all ENGINE output")
    selected.sort(key=lambda event: (event["timestamp"], event["event_id"]))
    return selected, unscored_ids


def _encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def export_demo(replay_directory, evaluation_directory, output):
    """Exclusively write a deterministic demo; every source artifact stays read-only."""
    replay_root = Path(replay_directory).resolve()
    evaluation_root = Path(evaluation_directory).resolve()
    output = Path(output)
    resolved_output = output.resolve()
    for source_root in (replay_root, evaluation_root):
        _require(not resolved_output.is_relative_to(source_root)
                 and not source_root.is_relative_to(resolved_output),
                 "Demo output overlaps sealed input evidence")
    _require(not output.exists() and not output.is_symlink(), "Demo output already exists")
    replay, replay_sha, replay_manifest_sha = _verify_directory(replay_root, "replay.json")
    evaluation, evaluation_sha, evaluation_manifest_sha = _verify_directory(evaluation_root, "evaluation.json")
    _require(evaluation.get("replay_manifest_sha256") == replay_manifest_sha,
             "Evaluation belongs to another sealed replay")
    selected, unscored_ids = _select_events(replay, evaluation)
    source = {"replaySha256": replay_sha, "evaluationSha256": evaluation_sha}
    packet = {
        "schema": "recorded_oracle_demo_v1", "selection": "verified_scored_only",
        "timeline": "engine_first_seen_seconds", "source": source,
        "excludedUnscoredEventCount": len(unscored_ids),
        "events": [{"eventId": event["event_id"], "cardId": event["card_id"],
                    "timestamp": event["timestamp"], "confidence": None, "source": "recorded_oracle"}
                   for event in selected],
    }
    packet_bytes = _encode(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    manifest = {
        "schema": "recorded_oracle_demo_manifest_v1", "files": {PACKET_NAME: packet_sha},
        "source": {**source, "replayManifestSha256": replay_manifest_sha,
                   "evaluationManifestSha256": evaluation_manifest_sha},
        "selectedEvents": [{"eventId": event["event_id"], "time": event["timestamp"],
                            "confirmedAt": event["confirmed_at"]} for event in selected],
        "excludedUnscoredEventCount": len(unscored_ids),
        "excludedUnscoredEventIds": sorted(unscored_ids),
        "selectionUse": "post_replay_offline_demo_only",
        "eventGtUsedAsEngineInput": False,
        "limitations": {"offlineRetrospective": True, "realTimeLatencyValidated": False,
                        "detectorPerformance": False, "crossMatchValidation": False,
                        "fullMatchFalsePositiveRate": None, "unscoredIsNegative": False},
    }
    manifest_bytes = _encode(manifest)
    output.mkdir(parents=True, exist_ok=False)
    with (output / PACKET_NAME).open("xb") as handle:
        handle.write(packet_bytes)
    with (output / "manifest.json").open("xb") as handle:
        handle.write(manifest_bytes)
    return {"eventCount": len(selected), "excludedUnscoredEventCount": len(unscored_ids),
            "packetSha256": packet_sha, "source": source}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare five scored offline Oracle demo events; no engine rerun")
    parser.add_argument("--replay-directory", required=True)
    parser.add_argument("--evaluation-directory", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        report = export_demo(args.replay_directory, args.evaluation_directory, args.output)
        print(json.dumps(report, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError, RecursionError):
        print("Recorded replay evidence rejected; no private paths are disclosed.")
        return 2
