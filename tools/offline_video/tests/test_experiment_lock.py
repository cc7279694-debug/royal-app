"""Lock-chain failures exercise real JSON, filesystem, and prerequisite validation."""
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
import json

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from experiment_fixtures import development_fixture, user_confirmed_development_fixture
from lock_fixtures import gt_fixture, model_fixture


def api():
    try:
        return import_module("clash_tracker_video.experiment_lock")
    except ModuleNotFoundError:
        pytest.fail("Immutable lock-chain API not implemented")


@pytest.fixture
def directory(tmp_path, monkeypatch):
    # The real path guard runs under an isolated project root.
    monkeypatch.setattr(api(), "PROJECT_ROOT", tmp_path)
    return tmp_path / "outputs" / "locks"


def chain(directory):
    draft, indexes = development_fixture()
    dev = api().freeze_development(draft, indexes, directory)
    model = api().freeze_model(model_fixture(dev), dev, directory)
    return dev, model, gt_fixture(dev, model)


def resign(value):
    value["sha256"] = sha256(json.dumps({k: v for k, v in value.items() if k != "sha256"},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    return value


def test_canonical_bytes_are_compact_utf8_sorted_and_finite():
    assert api().canonical_bytes({"z": [2, 1], "a": "中文"}) == b'{"a":"\xe4\xb8\xad\xe6\x96\x87","z":[2,1]}'
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(EvidenceError):
            api().canonical_bytes({"number": bad})
    with pytest.raises(EvidenceError):
        api().canonical_bytes({1: "non-json-key"})


def test_development_reordered_keys_are_stable_and_file_has_one_lf(directory):
    draft, indexes = development_fixture()
    lock = api().freeze_development(draft, indexes, directory)
    files = list(directory.glob("*.json"))
    assert len(files) == 1
    raw = files[0].read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n") and b"\r" not in raw
    assert api().load_lock(files[0])["sha256"] == lock["sha256"]
    other = api().make_development_lock(dict(reversed(list(draft.items()))), indexes)
    assert other["sha256"] == lock["sha256"]
    draft["candidates"][0]["notes"]["visibility"] = "A changed manual observation"
    assert api().make_development_lock(draft, indexes)["sha256"] != lock["sha256"]


def test_user_confirmed_completion_metadata_survives_disk_lock_and_changes_digest(directory):
    draft, indexes = user_confirmed_development_fixture()
    locked = api().freeze_development(draft, indexes, directory)
    loaded = api().load_lock(next(directory.glob("*.json")))
    assert loaded["payload"]["draft"]["identity"]["completion_attestation"] == "user_confirmed"
    assert loaded["payload"]["draft"]["identity"]["terminal_result_screen_present"] is False
    assert loaded["sha256"] == locked["sha256"]
    changed = deepcopy(draft)
    changed["identity"]["terminal_result_screen_present"] = True
    assert api().make_development_lock(changed, indexes)["sha256"] != locked["sha256"]
    tampered = deepcopy(locked)
    tampered["payload"]["draft"]["identity"]["terminal_result_screen_present"] = True
    with pytest.raises(EvidenceError):
        api().validate_lock(tampered)


def test_same_version_alternate_filename_is_rejected_without_overwrite(directory):
    draft, indexes = development_fixture()
    original = api().freeze_development(draft, indexes, directory)
    file = next(directory.glob("*.json"))
    bytes_before = file.read_bytes()
    file.rename(directory / "caller_alternate_name.json")
    with pytest.raises(EvidenceError):
        api().freeze_development(draft, indexes, directory)
    assert (directory / "caller_alternate_name.json").read_bytes() == bytes_before
    draft["freeze_version"] = 2
    assert api().freeze_development(draft, indexes, directory)["freeze_version"] == 2
    assert original["freeze_version"] == 1


@pytest.mark.parametrize("field,value", [("freeze_version", True), ("freeze_version", 0),
    ("experiment_id", "../escape"), ("experiment_id", "CON"), ("experiment_id", "trailing.")])
def test_unsafe_identity_and_nonpositive_version_cannot_create_files(directory, field, value):
    draft, indexes = development_fixture()
    draft[field] = value
    with pytest.raises(EvidenceError):
        api().freeze_development(draft, indexes, directory)
    assert not directory.exists()


def test_development_revalidates_report_snapshot_and_bool_int_corruption(directory):
    draft, indexes = development_fixture()
    lock = api().freeze_development(draft, indexes, directory)
    for route, value in [("derived", False), ("snapshot", True), ("version", 2)]:
        changed = deepcopy(lock)
        if route == "derived":
            changed["payload"]["derived"]["candidates"][0]["eligible"] = value
        elif route == "snapshot":
            changed["payload"]["index_snapshot"]["synthetic"]["recording"]["origin_pts"] = value
        else:
            changed["freeze_version"] = value
        with pytest.raises(EvidenceError):
            api().validate_lock(resign(changed))
    changed = deepcopy(lock)
    # Equality True == 1 must not certify a forged recomputed report.
    changed["payload"]["derived"]["candidates"][0]["clear_verified_plays"] = 2.0
    with pytest.raises(EvidenceError):
        api().validate_lock(resign(changed))


def test_complete_chain_freezes_gt_and_exposes_future_evaluation_references(directory):
    dev, model, gt = chain(directory)
    locked = api().freeze_test_gt(gt, dev, model, directory)
    assert api().validate_lock(locked, dev, model)["lock_type"] == "test_gt"
    refs = api().evaluation_references(dev, model, locked)
    assert refs == {"schema_version": 1, "experiment_id": "anonymous_experiment",
                   "development_lock_sha256": dev["sha256"], "model_lock_sha256": model["sha256"],
                   "test_gt_sha256": locked["sha256"], "evaluation_protocol_version": 1}


@pytest.mark.parametrize("field,value", [("created_at", "2026-10-04T01:00:00Z"),
    ("development_lock_sha256", "e" * 64), ("target", {"card_id": "different", "form": "normal"}),
    ("git_commit", "bad"), ("test_pixels_unseen", False), ("precise_test_gt_unseen", False)])
def test_model_rejects_missing_binding_temporal_leakage_or_invalid_hash(directory, field, value):
    draft, indexes = development_fixture()
    dev = api().freeze_development(draft, indexes, directory)
    contract = model_fixture(dev)
    contract[field] = value
    with pytest.raises(EvidenceError):
        api().freeze_model(contract, dev, directory)


@pytest.mark.parametrize("mutation", ["same_match", "same_recording", "same_source", "missing_model",
    "damaged_model", "wrong_dev", "wrong_model", "time", "session", "predictions_seen",
    "first", "all_plays", "non_evaluable_reason", "prediction_field", "difficulty"])
def test_gt_rejects_leaks_missing_prerequisites_and_difficulty_exclusion(directory, mutation):
    dev, model, gt = chain(directory)
    if mutation == "same_match": gt["identity"]["underlying_match_id"] = dev["payload"]["draft"]["identity"]["underlying_match_id"]
    elif mutation == "same_recording": gt["identity"]["recording_id"] = "synthetic"
    elif mutation == "same_source": gt["recording"]["source_sha256"] = "0" * 64
    elif mutation == "missing_model": model = None
    elif mutation == "damaged_model": model["payload"]["confidence_threshold"] = 0.9
    elif mutation == "wrong_dev": gt["development_lock_sha256"] = "d" * 64
    elif mutation == "wrong_model": gt["model_lock_sha256"] = "d" * 64
    elif mutation == "time": gt["created_at"] = model["created_at"]
    elif mutation == "session": gt["annotation_session"]["session_id"] = model["payload"]["development_session_id"]
    elif mutation == "predictions_seen": gt["annotation_session"]["predictions_unseen"] = False
    elif mutation == "first": gt["identity"]["first_qualifying_match"] = False
    elif mutation == "all_plays": gt["identity"]["all_deployments_reviewed"] = False
    elif mutation == "non_evaluable_reason": gt["deployments"][0].update(evaluation_status="non_evaluable", non_evaluable_reason=None)
    elif mutation == "prediction_field": gt["deployments"][0]["key_frames"][0]["confidence"] = .8
    elif mutation == "difficulty": gt["selection_history"] = [{"underlying_match_id": "earlier", "reason": "too_difficult"}]
    with pytest.raises(EvidenceError):
        api().freeze_test_gt(gt, dev, model, directory)


def test_fully_occluded_target_retained_with_reason_no_boxes_not_excluded(directory):
    dev, model, gt = chain(directory)
    gt["deployments"][0].update(evaluation_status="non_evaluable", non_evaluable_reason="Fully occluded", key_frames=[])
    gt["index_snapshot"]["synthetic_test"]["frames"] = []
    locked = api().freeze_test_gt(gt, dev, model, directory)
    assert locked["payload"]["deployments"][0]["evaluation_status"] == "non_evaluable"


@pytest.mark.parametrize("form", ["evolved", "unknown"])
def test_other_or_unknown_forms_cannot_qualify_or_be_negative(directory, form):
    dev, model, gt = chain(directory)
    other = deepcopy(gt["deployments"][0])
    other.update(play_id="other_form", form=form, key_frames=[])
    other.update(last_absent_seconds=8.9, deployment_lower_seconds=8.9,
                 deployment_time_seconds=9, deployment_upper_seconds=9,
                 visible_start_seconds=9, visible_end_seconds=10)
    gt["deployments"].append(other)
    with pytest.raises(EvidenceError):
        api().freeze_test_gt(gt, dev, model, directory)
    gt["negative_intervals"] = []
    gt["unknown_intervals"] = [{"unknown_id": "gap", "recording_id": "synthetic_test",
        "start_seconds": 0, "end_seconds": 20, "reason": "Remaining timeline unknown"}]
    assert api().freeze_test_gt(gt, dev, model, directory)["lock_type"] == "test_gt"


def test_unknown_overlap_and_unregistered_gaps_are_rejected(directory):
    dev, model, gt = chain(directory)
    gt["unknown_intervals"] = [{"unknown_id": "gap", "recording_id": "synthetic_test",
        "start_seconds": 0, "end_seconds": .5, "reason": "Unreviewed"}]
    with pytest.raises(EvidenceError):
        api().freeze_test_gt(gt, dev, model, directory)
    gt["unknown_intervals"] = []
    gt["negative_intervals"] = []
    with pytest.raises(EvidenceError):
        api().freeze_test_gt(gt, dev, model, directory)


def test_load_rejects_tampering_duplicate_json_keys_and_wrong_schema(directory):
    dev, _, _ = chain(directory)
    file = next(directory.glob("*development*.json"))
    for raw in [b'{"a":1,"a":2}', b'{"n":1e999}',
                json.dumps({**dev, "schema_version": 2}).encode()]:
        file.write_bytes(raw)
        with pytest.raises(EvidenceError): api().load_lock(file)


def test_directory_outside_ignored_roots_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(api(), "PROJECT_ROOT", tmp_path)
    draft, indexes = development_fixture()
    with pytest.raises(EvidenceError):
        api().freeze_development(draft, indexes, tmp_path / "tracked")


def test_traversal_into_private_root_is_rejected_before_normalization(directory):
    draft, indexes = development_fixture()
    with pytest.raises(EvidenceError):
        api().freeze_development(draft, indexes, directory / "unused" / ".." / "alternate")
    assert not directory.exists()


def test_windows_junction_into_private_root_is_rejected(directory):
    import subprocess
    target = directory.parent / "actual"
    target.mkdir(parents=True)
    link = directory.parent / "junction"
    created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                             capture_output=True, check=False)
    assert created.returncode == 0
    draft, indexes = development_fixture()
    try:
        with pytest.raises(EvidenceError):
            api().freeze_development(draft, indexes, link)
        assert list(target.iterdir()) == []
    finally:
        link.rmdir()


def test_lock_larger_than_loader_limit_never_creates_file(directory, monkeypatch):
    draft, indexes = development_fixture()
    monkeypatch.setattr(api(), "MAX_LOCK_BYTES", 10)
    with pytest.raises(EvidenceError):
        api().freeze_development(draft, indexes, directory)
    assert not directory.exists()


@pytest.mark.parametrize("field,value", [
    ("width", True), ("crop", {"x": 0, "y": 0, "width": 2, "height": 1}),
    ("preprocess", {"color_order": "RGB", "dtype": "float32", "scale": 1,
                    "mean": [0, 0, 0], "std": [1, 0, 1]}),
])
def test_invalid_model_preprocessing_is_rejected(directory, field, value):
    draft, indexes = development_fixture()
    dev = api().freeze_development(draft, indexes, directory)
    model = model_fixture(dev)
    model["input"][field] = value
    with pytest.raises(EvidenceError):
        api().freeze_model(model, dev, directory)


def test_two_real_candidate_payloads_keep_order_in_development_digest(directory):
    draft, indexes = development_fixture()
    other = deepcopy(draft["candidates"][0])
    other.update(candidate_id="second_candidate", card_id="second_synthetic_card")
    evidence = other["evidence"]
    evidence["target_card"]["card_id"] = "second_synthetic_card"
    for play in evidence["occurrences"]:
        play["play_id"] = "second_" + play["play_id"]
        play["card_id"] = "second_synthetic_card"
        play["evidence_annotation_ids"] = ["second_" + aid for aid in play["evidence_annotation_ids"]]
    for frame in evidence["frame_annotations"]:
        frame["play_id"] = "second_" + frame["play_id"]
        frame["annotation_id"] = "second_" + frame["annotation_id"]
    for play in other["deployments"]:
        play["play_id"] = "second_" + play["play_id"]
    draft["candidates"].append(other)
    first = api().make_development_lock(draft, indexes)
    draft["candidates"].reverse()
    second = api().make_development_lock(draft, indexes)
    assert first["sha256"] != second["sha256"]


def test_two_concurrent_freezes_never_overwrite_same_version(directory):
    from concurrent.futures import ThreadPoolExecutor
    draft, indexes = development_fixture()

    def attempt():
        try:
            return api().freeze_development(draft, indexes, directory)
        except EvidenceError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: attempt(), range(2)))
    assert sum(result is not None for result in outcomes) == 1
    assert len(list(directory.iterdir())) == 1
    assert api().load_lock(next(directory.iterdir()))["sha256"] == next(result for result in outcomes if result)["sha256"]


@pytest.mark.parametrize("mutation", ["only_other", "only_unknown", "unknown_precision",
    "terminal_unknown_negative", "frame_pts", "frame_hash", "nested_prediction", "empty_reason"])
def test_gt_form_uncertainty_frame_binding_and_nested_closed_schema(directory, mutation):
    dev, model, gt = chain(directory)
    if mutation == "only_other": gt["deployments"][0]["form"] = "evolved"
    elif mutation == "only_unknown": gt["deployments"][0]["form"] = "unknown"
    elif mutation == "unknown_precision": gt["deployments"][0]["evolution"].update(progress="known", remaining_count=1)
    elif mutation == "terminal_unknown_negative":
        gt["unknown_intervals"] = [{"unknown_id": "terminal", "recording_id": "synthetic_test",
            "start_seconds": 20, "end_seconds": 20, "reason": "Uncertain terminal frame"}]
    elif mutation == "frame_pts": gt["deployments"][0]["key_frames"][0]["raw_pts"] += 100
    elif mutation == "frame_hash": gt["index_snapshot"]["synthetic_test"]["frames"][0]["_content_hash"] = "invalid"
    elif mutation == "nested_prediction": gt["recording"]["model_predictions"] = []
    elif mutation == "empty_reason": gt["deployments"][0].update(evaluation_status="non_evaluable", non_evaluable_reason=" ")
    with pytest.raises(EvidenceError):
        api().freeze_test_gt(gt, dev, model, directory)


def test_new_creation_time_and_chain_binding_affect_complete_envelope_digest(directory):
    draft, indexes = development_fixture()
    first = api().make_development_lock(draft, indexes)
    draft["created_at"] = "2026-10-04T01:00:01Z"
    second = api().make_development_lock(draft, indexes)
    assert first["sha256"] != second["sha256"]
    model_a = model_fixture(first)
    model_b = model_fixture(second)
    locked_a = api().freeze_model(model_a, first, directory)
    model_b["freeze_version"] = 2
    locked_b = api().freeze_model(model_b, second, directory)
    assert locked_a["sha256"] != locked_b["sha256"]


def test_loaded_model_and_gt_require_revalidated_full_chain(directory):
    dev, model, gt = chain(directory)
    api().freeze_test_gt(gt, dev, model, directory)
    model_file = next(directory.glob("*.model.*.json"))
    gt_file = next(directory.glob("*.test_gt.*.json"))
    with pytest.raises(EvidenceError): api().load_lock(model_file)
    with pytest.raises(EvidenceError): api().load_lock(gt_file, dev)
    assert api().load_lock(model_file, dev)["sha256"] == model["sha256"]
    assert api().load_lock(gt_file, dev, model)["lock_type"] == "test_gt"
    bad_dev = deepcopy(dev)
    bad_dev["payload"]["derived"]["candidates"][0]["eligible"] = 1
    with pytest.raises(EvidenceError): api().load_lock(gt_file, resign(bad_dev), model)


@pytest.mark.parametrize("reason", ["missing_replay", "damaged_replay", "interrupted_recording", "undecodable"])
def test_only_permissible_material_exclusions_can_be_retained(directory, reason):
    dev, model, gt = chain(directory)
    gt["selection_history"] = [{"underlying_match_id": "excluded_synthetic_match", "reason": reason}]
    assert api().freeze_test_gt(gt, dev, model, directory)["payload"]["selection_history"][0]["reason"] == reason


@pytest.mark.parametrize("start_seconds", [1, 100])
def test_model_protocol_cannot_skip_recording_prefix(directory, start_seconds):
    draft, indexes = development_fixture()
    dev = api().freeze_development(draft, indexes, directory)
    model = model_fixture(dev)
    model["sampling"]["start_seconds"] = start_seconds
    with pytest.raises(EvidenceError):
        api().freeze_model(model, dev, directory)
