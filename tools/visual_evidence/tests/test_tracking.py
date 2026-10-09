"""Synthetic geometric contracts; no recordings, GT, models or event scoring."""
from copy import deepcopy
import importlib
import importlib.util
from pathlib import Path
import shutil

import pytest


SOURCE_ROOT = Path(__file__).resolve().parents[3] / "outputs/module3c4/bytetrack_source"


def module():
    # An absent implementation is a readable assertion failure, not collection failure.
    assert importlib.util.find_spec("tools.visual_evidence.tracking") is not None, \
        "visual tracking sidecar is not implemented"
    if not SOURCE_ROOT.is_dir() or any(importlib.util.find_spec(name) is None for name in ("numpy", "scipy", "lap")):
        pytest.skip("private ByteTrack source and isolated NumPy/SciPy/LAP environment required")
    return importlib.import_module("tools.visual_evidence.tracking")


def row(oid, timestamp, x=10, *, match="m", visual="visual.unit.royal_hog", owner="opponent", score=.8):
    return {"observation_id": oid, "match_id": match, "timestamp": timestamp,
            "visual_class": visual, "bbox": [x, 10, x + 20, 30], "owner": owner,
            "confidence": score, "form": "unknown", "origin_kind": "unknown", "source": "synthetic"}


def frames(end=1, match="m"):
    return [{"match_id": match, "timestamp": i / 4, "raw_pts": i, "time_base": "1/4"}
            for i in range(int(end * 4) + 1)]


def replay(rows, metadata=None):
    return module().track_stream(rows, frames() if metadata is None else metadata, SOURCE_ROOT)


def assigned(result):
    return {r["observation_id"]: r for r in result["observations"]}


def test_movement_and_short_missing_interval_keep_track_identity():
    data = [row("a", 0), row("b", .25, 11), row("c", .5, 12), row("d", 1, 14)]
    out = replay(data)
    assert len({r["track_id"] for r in out["observations"]}) == 1
    assert out["tracks"][0]["observation_ids"] == ["a", "b", "c", "d"]
    assert any(x["state"] == "lost" for x in out["tracks"][0]["lifecycle"])
    assert [r["bbox"] for r in out["observations"]] == [r["bbox"] for r in data]


def test_owner_flip_preserves_raw_owner_without_splitting():
    data = [row("a", 0, owner="own"), row("b", .25, owner="opponent")]
    out = replay(data)
    assert out["observations"][0]["track_id"] == out["observations"][1]["track_id"]
    assert [r["owner"] for r in out["observations"]] == ["own", "opponent"]
    assert out["tracks"][0]["owner_history"] == [
        {"observation_id": "a", "owner": "own"}, {"observation_id": "b", "owner": "opponent"}]


def test_concurrent_members_and_later_separate_members_have_distinct_ids():
    data = [row("a", 0, 10), row("b", 0, 80), row("c", .25, 11), row("d", .25, 81),
            row("e", 1, 200), row("f", 1, 270)]
    out = assigned(replay(data))
    assert out["a"]["track_id"] == out["c"]["track_id"]
    assert out["b"]["track_id"] == out["d"]["track_id"]
    assert len({out[k]["track_id"] for k in ("a", "b", "e", "f")}) == 4


def test_reset_and_reordered_input_produce_identical_sidecars():
    data = [row("b", .25), row("a", 0), row("x", 0, 200)]
    first = replay(data)
    assert first == replay(list(reversed(data)))


def test_empty_frames_expire_tracks_and_later_detection_starts_new_identity():
    out = replay([row("a", 0), row("b", .25), row("c", 3)], frames(3))
    rows = assigned(out)
    assert rows["a"]["track_id"] == rows["b"]["track_id"]
    assert rows["c"]["track_id"] != rows["a"]["track_id"]
    old = next(t for t in out["tracks"] if t["track_id"] == rows["a"]["track_id"])
    assert old["lifecycle"][-1]["state"] == "removed"
    assert len(out["frames"]) == 13


def test_removed_track_does_not_resurrect_on_the_immediately_following_frame():
    out = replay([row("a", 0), row("b", .25), row("c", 2.75)], frames(2.75))
    rows = assigned(out)
    assert rows["c"]["track_id"] != rows["a"]["track_id"]


def test_visual_classes_and_matches_have_independent_identity_spaces():
    metadata = frames(.25, "m") + frames(.25, "other")
    data = [row("a", 0), row("b", .25),
            row("c", 0, visual="visual.unit.minion"), row("d", .25, visual="visual.unit.minion"),
            row("e", 0, match="other"), row("f", .25, match="other")]
    out = assigned(replay(data, metadata))
    assert out["a"]["track_id"] == out["b"]["track_id"]
    assert out["c"]["track_id"] == out["d"]["track_id"]
    assert out["e"]["track_id"] == out["f"]["track_id"]
    assert len({out[k]["track_id"] for k in ("a", "c", "e")}) == 3


def test_low_confidence_can_extend_existing_track_but_cannot_create_one():
    out = assigned(replay([row("a", 0), row("b", .25, score=.2), row("c", .5, 200, score=.2)]))
    assert out["b"]["track_id"] == out["a"]["track_id"]
    assert out["b"]["low_confidence"] is True
    assert out["c"]["track_id"] is None
    assert out["c"]["state"] == "unassigned"


def test_new_track_after_first_frame_stays_unconfirmed_until_next_support():
    out = assigned(replay([row("a", .25), row("b", .5)]))
    assert out["a"]["state"] == "unconfirmed"
    assert out["b"]["state"] == "tracked"
    assert out["a"]["track_id"] == out["b"]["track_id"]


def test_competing_geometric_candidates_are_explicit_ambiguity():
    out = assigned(replay([row("a", 0, 10), row("b", 0, 20), row("c", .25, 15)]))
    assert out["c"]["association_ambiguity"] is True
    assert len(out["c"]["competing_track_ids"]) == 2
    assert out["c"]["track_id"] in out["c"]["competing_track_ids"]


def test_numpy_iou_preserves_pixel_inclusive_boundary():
    backend = module().load_backend(SOURCE_ROOT)
    assert backend.matching.ious([[0, 0, 1, 1]], [[1, 0, 2, 1]])[0, 0] == pytest.approx(1 / 3)


def test_lap_cost_limit_preserves_optional_assignment_boundary():
    import numpy as np
    backend = module().load_backend(SOURCE_ROOT)
    pairs, ua, ub = backend.matching.linear_assignment(np.asarray([[.4, .6], [.6, 100.]]), .5)
    assert pairs.tolist() == [[0, 0]]
    assert list(ua) == [1] and list(ub) == [1]


@pytest.mark.parametrize("score", [None, float("nan"), -.1, 1.1, True])
def test_invalid_confidence_is_rejected_without_guessing(score):
    bad = row("a", 0)
    bad["confidence"] = score
    with pytest.raises(ValueError, match="confidence"):
        replay([bad])


def test_missing_confidence_is_rejected_without_guessing():
    bad = row("a", 0)
    del bad["confidence"]
    with pytest.raises(ValueError, match="confidence"):
        replay([bad])


def test_tracking_does_not_mutate_original_observations_or_frames():
    data, metadata = [row("a", 0), row("b", .25)], frames()
    original = deepcopy((data, metadata))
    out = replay(data, metadata)
    assert (data, metadata) == original
    assert len(out["observations"]) == 2
    assert out["event_gt_used_as_input"] is False
    assert out["human_identity_used"] is False
    assert out["track_ids_are_identity_hypotheses"] is True


def test_hash_mismatch_rejects_modified_source_before_execution(tmp_path):
    tracker = module()
    copied = tmp_path / "source"
    shutil.copytree(SOURCE_ROOT, copied)
    with (copied / "basetrack.py").open("ab") as target:
        target.write(b"\nraise RuntimeError('unverified source executed')\n")
    with pytest.raises(ValueError, match="source hash mismatch"):
        tracker.load_backend(copied)


def test_missing_observation_frame_is_rejected():
    with pytest.raises(ValueError, match="observation frame missing"):
        replay([row("a", .125)])


@pytest.mark.parametrize("delta", [.5, 20., .2501])
def test_sparse_or_wrong_cadence_frames_are_rejected(delta):
    metadata = [{"match_id": "m", "timestamp": 0}, {"match_id": "m", "timestamp": delta}]
    with pytest.raises(ValueError, match="4FPS cadence"):
        replay([row("a", 0), row("b", delta)], metadata)


def test_serialization_roundoff_does_not_break_fixed_sampler_cadence():
    metadata = [{"match_id": "m", "timestamp": 0}, {"match_id": "m", "timestamp": .2500001}]
    out = replay([row("a", 0), row("b", .2500001)], metadata)
    assert out["observations"][0]["track_id"] == out["observations"][1]["track_id"]


def test_human_appearance_identity_is_rejected_at_standalone_boundary():
    data = row("a", 0)
    data["appearance_group_id"] = "human-assigned"
    with pytest.raises(ValueError, match="human|appearance"):
        replay([data])


@pytest.mark.parametrize("source", ["human_gt", "oracle_visual_stream", "event_gt"])
def test_human_or_oracle_sources_cannot_enter_standalone_tracker(source):
    data = row("a", 0)
    data["source"] = source
    with pytest.raises(ValueError, match="source"):
        replay([data])


def test_duplicate_ids_are_rejected_even_across_matches():
    with pytest.raises(ValueError, match="duplicate observation_id"):
        replay([row("a", 0), row("a", 0, match="other")], frames(0) + frames(0, "other"))


def test_empty_detection_frames_remain_present_without_synthesized_rows():
    out = replay([])
    assert out["observations"] == [] and out["associations"] == [] and out["tracks"] == []
    assert len(out["frames"]) == 5


def test_every_row_has_exact_association_including_below_low_threshold():
    data = [row("a", 0), row("b", .25, score=.1), row("c", .5, 200, score=.05)]
    out = replay(data)
    assert {r["observation_id"] for r in out["associations"]} == {"a", "b", "c"}
    lookup = {r["observation_id"]: r for r in out["associations"]}
    assert lookup["b"] == {"observation_id": "b", "track_id": None, "association_ambiguous": False}
    assert lookup["c"] == {"observation_id": "c", "track_id": None, "association_ambiguous": False}


def test_lifecycle_records_disappearance_due_to_duplicate_suppression():
    # Two initial overlapping hypotheses: one loses its evidence and is dropped
    # by ByteTrack's tracked-vs-lost duplicate suppression at the next frame.
    data = [row("a", 0), row("b", 0, 11), row("c", .25)]
    out = replay(data)
    rows = assigned(out)
    dropped = next(t for t in out["tracks"] if t["track_id"] == rows["b"]["track_id"])
    assert dropped["lifecycle"][-1] == {"timestamp": .25, "state": "suppressed"}
    assert rows["c"]["association_ambiguity"] is True
    assert set(rows["c"]["competing_track_ids"]) == {rows["a"]["track_id"], rows["b"]["track_id"]}
