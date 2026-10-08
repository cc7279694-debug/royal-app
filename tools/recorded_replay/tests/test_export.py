"""Synthetic artifact tests: no private GT, footage, or Oracle replay is run."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


CARDS = ["witch", "royal_hogs", "flying_machine", "golden_knight", "minions"]


def exporter():
    try:
        return importlib.import_module("tools.recorded_replay.export")
    except ModuleNotFoundError:
        pytest.fail("recorded replay exporter is not implemented")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_artifacts(directory, members):
    directory.mkdir(exist_ok=True)
    for name, value in members.items():
        (directory / name).write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    (directory / "manifest.json").write_text(json.dumps({
        "schema": "oracle_artifact_manifest_v1",
        "files": {name: sha(directory / name) for name in members},
    }, sort_keys=True), encoding="utf-8")


def fixture(tmp_path, mutate=None):
    events = [
        {"event_id": f"event-engine-{card}", "card_id": card,
         "match_id": "synthetic_match", "timestamp": timestamp,
         "confirmed_at": confirmed_at, "evidence_level": "STRONG",
         "form": "unknown", "rule_version": "oracle-card-rules-v1",
         "source_observation_ids": ["PRIVATE_VISUAL_OBSERVATION"],
         "source_appearance_groups": ["PRIVATE_APPEARANCE_GROUP"]}
        for card, timestamp, confirmed_at in [
            ("witch", 32.0, 34.5), ("royal_hogs", 77.0, 77.0),
            ("flying_machine", 79.5, 79.5), ("golden_knight", 104.5, 104.5),
            ("minions", 117.0, 117.0),
        ]
    ]
    unresolved = [
        {**deepcopy(events[4]), "event_id": "event-unscored-minions", "timestamp": 14.5, "confirmed_at": 14.5},
        {**deepcopy(events[3]), "event_id": "event-unscored-knight", "timestamp": 44.5, "confirmed_at": 52.0},
        {**deepcopy(events[0]), "event_id": "event-unscored-witch", "timestamp": 163.0, "confirmed_at": 163.0},
        {**deepcopy(events[0]), "event_id": "event-unscored-other-match", "match_id": "other_match",
         "timestamp": 68.0, "confirmed_at": 68.0},
    ]
    replay = {"schema": "oracle_event_replay_v1", "events": [*unresolved, *reversed(events)]}
    evaluation = {
        "schema": "oracle_event_evaluation_v1", "passed": True,
        "positive_hits": 5, "positive_total": 5, "positive_duplicates": 0,
        "explicit_dedupe_failures": 0,
        "positives": [{"hit": True, "matching_count": 1,
                       "matched_event_id": row["event_id"], "card_id": row["card_id"],
                       "event_gt_id": f"PRIVATE_GT_{index}", "gt_timestamp": 9000 + index}
                      for index, row in enumerate(events)],
        "unscored_events": [{key: row[key] for key in ("event_id", "card_id", "match_id", "timestamp")}
                            for row in unresolved],
        "dedupe_outcomes": [{"candidate_id": f"private_dedupe_{index}",
                              "new_event_count": 0, "event_ids": []} for index in range(3)],
        "unresolved_is_negative": False, "real_time_latency_validated": False,
        "cross_match_positive_validation": False, "detector_performance": False,
        "full_timeline_false_positive_rate": None,
    }
    if mutate:
        mutate(replay, evaluation)
    replay_dir, evaluation_dir = tmp_path / "replay", tmp_path / "evaluation"
    write_artifacts(replay_dir, {"replay.json": replay})
    evaluation["replay_manifest_sha256"] = sha(replay_dir / "manifest.json")
    write_artifacts(evaluation_dir, {"evaluation.json": evaluation})
    return replay_dir, evaluation_dir


def load_packet(output):
    return json.loads((output / "recorded-oracle-demo.json").read_text("utf-8"))


def test_selects_engine_ids_after_scoring_and_preserves_original_times(tmp_path):
    replay, evaluation = fixture(tmp_path)
    snapshots = {path: path.read_bytes() for directory in (replay, evaluation) for path in directory.iterdir()}
    output = tmp_path / "demo"
    exporter().export_demo(replay, evaluation, output)
    packet = load_packet(output)
    assert packet == {
        "schema": "recorded_oracle_demo_v1", "selection": "verified_scored_only",
        "timeline": "engine_first_seen_seconds",
        "source": {"replaySha256": sha(replay / "replay.json"),
                   "evaluationSha256": sha(evaluation / "evaluation.json")},
        "excludedUnscoredEventCount": 4,
        "events": [
            {"eventId": "event-engine-witch", "cardId": "witch", "timestamp": 32.0,
             "confidence": None, "source": "recorded_oracle"},
            {"eventId": "event-engine-royal_hogs", "cardId": "royal_hogs", "timestamp": 77.0,
             "confidence": None, "source": "recorded_oracle"},
            {"eventId": "event-engine-flying_machine", "cardId": "flying_machine", "timestamp": 79.5,
             "confidence": None, "source": "recorded_oracle"},
            {"eventId": "event-engine-golden_knight", "cardId": "golden_knight", "timestamp": 104.5,
             "confidence": None, "source": "recorded_oracle"},
            {"eventId": "event-engine-minions", "cardId": "minions", "timestamp": 117.0,
             "confidence": None, "source": "recorded_oracle"},
        ],
    }
    sidecar = json.loads((output / "manifest.json").read_text("utf-8"))
    assert sidecar["files"]["recorded-oracle-demo.json"] == sha(output / "recorded-oracle-demo.json")
    assert sidecar["selectedEvents"][0] == {"eventId": "event-engine-witch", "time": 32.0, "confirmedAt": 34.5}
    assert snapshots == {path: path.read_bytes() for path in snapshots}
    for private_text in ("PRIVATE_GT", "9000", "PRIVATE_VISUAL", "PRIVATE_APPEARANCE", str(tmp_path)):
        assert private_text not in (output / "recorded-oracle-demo.json").read_text("utf-8")


def test_repeated_exports_are_byte_identical(tmp_path):
    replay, evaluation = fixture(tmp_path)
    exporter().export_demo(replay, evaluation, tmp_path / "one")
    exporter().export_demo(replay, evaluation, tmp_path / "two")
    for name in ("recorded-oracle-demo.json", "manifest.json"):
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes()


@pytest.mark.parametrize("member", ["replay.json", "evaluation.json"])
def test_changed_input_bytes_fail_manifest_validation(tmp_path, member):
    replay, evaluation = fixture(tmp_path)
    directory = replay if member == "replay.json" else evaluation
    (directory / member).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, tmp_path / "demo")
    assert not (tmp_path / "demo").exists()


def test_wrong_replay_manifest_binding_is_rejected(tmp_path):
    replay, evaluation = fixture(tmp_path)
    report = json.loads((evaluation / "evaluation.json").read_text("utf-8"))
    report["replay_manifest_sha256"] = "0" * 64
    write_artifacts(evaluation, {"evaluation.json": report})
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, tmp_path / "demo")


@pytest.mark.parametrize("mutation", [
    "missing-id", "duplicate-engine-id", "duplicate-positive-id", "unscored-overlap",
    "wrong-card", "bad-positive-count", "not-hit", "multiple-matches", "evaluation-fail",
    "unpartitioned-event", "duplicate-unscored-id", "dedupe-failure", "unsupported-card",
    "bad-time", "non-finite-time", "confirmation-before-first-seen", "non-strong-event",
])
def test_inconsistent_sealed_evidence_is_rejected_before_output_creation(tmp_path, mutation):
    def mutate(replay, evaluation):
        events, positives = replay["events"], evaluation["positives"]
        selected = events[-1]
        if mutation == "missing-id": positives[0]["matched_event_id"] = "missing-engine-id"
        elif mutation == "duplicate-engine-id": events.append(deepcopy(selected))
        elif mutation == "duplicate-positive-id": positives[1]["matched_event_id"] = positives[0]["matched_event_id"]
        elif mutation == "unscored-overlap": evaluation["unscored_events"][0]["event_id"] = positives[0]["matched_event_id"]
        elif mutation == "wrong-card": positives[0]["card_id"] = "minions"
        elif mutation == "bad-positive-count": evaluation["positive_hits"] = 4
        elif mutation == "not-hit": positives[0]["hit"] = False
        elif mutation == "multiple-matches": positives[0]["matching_count"] = 2
        elif mutation == "evaluation-fail": evaluation["passed"] = False
        elif mutation == "unpartitioned-event": events.append({**deepcopy(selected), "event_id": "extra-event"})
        elif mutation == "duplicate-unscored-id": evaluation["unscored_events"][1]["event_id"] = evaluation["unscored_events"][0]["event_id"]
        elif mutation == "dedupe-failure": evaluation["dedupe_outcomes"][0]["new_event_count"] = 1
        elif mutation == "unsupported-card": selected["card_id"] = positives[0]["card_id"] = "skeletons"
        elif mutation == "bad-time": selected["timestamp"] = -1
        elif mutation == "non-finite-time": selected["timestamp"] = float("inf")
        elif mutation == "confirmation-before-first-seen": selected["confirmed_at"] = 31
        elif mutation == "non-strong-event": selected["evidence_level"] = "MEDIUM"
    replay, evaluation = fixture(tmp_path, mutate)
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, tmp_path / "demo")
    assert not (tmp_path / "demo").exists()


def test_missing_matched_id_cannot_fall_back_to_card_name(tmp_path):
    def mutate(_replay, evaluation):
        del evaluation["positives"][0]["matched_event_id"]
    replay, evaluation = fixture(tmp_path, mutate)
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, tmp_path / "demo")


@pytest.mark.parametrize("field,value", [("card_id", []), ("timestamp", 2 ** 1024)])
def test_malformed_engine_scalar_is_rejected_as_evidence_error(tmp_path, field, value):
    def mutate(replay, _evaluation):
        replay["events"][-1][field] = value
    replay, evaluation = fixture(tmp_path, mutate)
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, tmp_path / "demo")
    assert not (tmp_path / "demo").exists()


def test_existing_output_is_never_overwritten(tmp_path):
    replay, evaluation = fixture(tmp_path)
    output = tmp_path / "demo"
    output.mkdir()
    keep = output / "keep.txt"
    keep.write_text("existing evidence", encoding="utf-8")
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, output)
    assert keep.read_text("utf-8") == "existing evidence"
    assert list(output.iterdir()) == [keep]


@pytest.mark.parametrize("overlap", ["inside-input", "input-parent"])
def test_output_cannot_overlap_frozen_inputs(tmp_path, overlap):
    replay, evaluation = fixture(tmp_path)
    output = replay / "demo" if overlap == "inside-input" else tmp_path
    with pytest.raises(ValueError):
        exporter().export_demo(replay, evaluation, output)
    assert not (replay / "demo").exists()


def test_cli_exports_without_printing_private_paths(tmp_path, capsys):
    replay, evaluation = fixture(tmp_path)
    code = exporter().main(["--replay-directory", str(replay), "--evaluation-directory", str(evaluation),
                            "--output", str(tmp_path / "demo")])
    assert code == 0
    report = json.loads(capsys.readouterr().out)
    assert report["eventCount"] == 5
    assert report["excludedUnscoredEventCount"] == 4
    assert str(tmp_path) not in json.dumps(report)


def test_cli_rejects_private_input_without_path_disclosure(tmp_path, capsys):
    code = exporter().main(["--replay-directory", str(tmp_path / "PRIVATE_ACCOUNT"),
                            "--evaluation-directory", str(tmp_path / "PRIVATE_GT"),
                            "--output", str(tmp_path / "demo")])
    assert code == 2
    assert "PRIVATE" not in capsys.readouterr().out
    assert not (tmp_path / "demo").exists()


def test_module_entrypoint_exports_frozen_artifacts(tmp_path):
    exporter()  # Make the RED failure an explicit missing-feature assertion.
    replay, evaluation = fixture(tmp_path)
    process = subprocess.run([sys.executable, "-m", "tools.recorded_replay",
                              "--replay-directory", str(replay), "--evaluation-directory", str(evaluation),
                              "--output", str(tmp_path / "demo")], capture_output=True, text=True)
    assert process.returncode == 0, process.stdout + process.stderr
    assert len(load_packet(tmp_path / "demo")["events"]) == 5


def test_deeply_nested_private_metadata_is_rejected_without_traceback_or_output(tmp_path, capsys):
    replay, evaluation = fixture(tmp_path)
    (replay / "manifest.json").write_text(
        '{"files":' + '[' * 5000 + '0' + ']' * 5000 + '}', encoding="utf-8")
    code = exporter().main(["--replay-directory", str(replay),
                            "--evaluation-directory", str(evaluation),
                            "--output", str(tmp_path / "demo")])
    assert code == 2
    output = capsys.readouterr()
    assert str(tmp_path) not in output.out + output.err
    assert "Traceback" not in output.out + output.err
    assert not (tmp_path / "demo").exists()
