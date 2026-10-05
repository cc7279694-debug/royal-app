"""Behavioral contract checks using synthetic records, without a model runtime."""
from copy import deepcopy

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.training_dataset_contract import (
    dataset_readiness, grouped_folds, validate_dataset_shape,
)
from training_dataset_fixtures import add_reencoded_recording, dataset_fixture


@pytest.mark.parametrize("plays,matches,events,ready", [
    ((2, 2, 2, 2), 4, 8, True), ((3, 3, 2), 3, 8, False),
    ((2, 2, 2, 1), 4, 7, False), ((1, 2, 2, 3), 4, 8, True),
])
def test_readiness_counts_independent_matches_and_plays(plays, matches, events, ready):
    report = dataset_readiness(dataset_fixture(plays))
    assert report["valid"] is True
    assert report["training_data_ready"] is ready
    assert report["evaluation_ready"] is False
    assert report["counts"]["target_positive_matches"] == matches
    assert report["counts"]["confirmed_target_deployments"] == events


def test_twelve_boxes_in_four_frames_supply_only_one_play():
    report = dataset_readiness(dataset_fixture((1,)))
    assert report["counts"]["confirmed_target_deployments"] == 1
    assert report["counts"]["training_images"] == 4
    assert report["counts"]["training_unit_boxes"] == 12
    assert grouped_folds(dataset_fixture((1,))) == []


def test_reencoded_recording_cannot_manufacture_a_match_or_play():
    draft = add_reencoded_recording(dataset_fixture())
    report = dataset_readiness(draft)
    assert report["counts"]["target_positive_matches"] == 4
    assert report["counts"]["confirmed_target_deployments"] == 8
    assert report["counts"]["recordings"] == 5


def test_sparse_empty_frame_does_not_certify_evaluation_time():
    draft = dataset_fixture()
    frame = deepcopy(draft["frames"][0])
    frame.update(frame_id="empty_frame", timestamp_seconds=1, raw_pts=2000,
                 image_path="synthetic/empty.png", minion_presence="absent")
    draft["frames"].append(frame)
    report = dataset_readiness(draft)
    assert report["counts"]["negative_training_images"] == 1
    assert report["confirmed_absent_seconds"] == 0
    assert report["evaluation_ready"] is False


def test_absent_intervals_are_unioned_and_needed_in_each_included_match():
    draft = dataset_fixture(absent=True)
    report = dataset_readiness(draft)
    assert report["confirmed_absent_seconds"] == 32
    assert report["evaluation_ready"] is True
    draft["confirmed_absent_intervals"] = [i for i in draft["confirmed_absent_intervals"]
                                            if i["recording_id"] != "recording_4"]
    report = dataset_readiness(draft)
    assert report["training_data_ready"] is True
    assert report["evaluation_ready"] is False
    assert "missing_absent_coverage" in report["evaluation_reasons"]


@pytest.mark.parametrize("field,value", [
    ("form", "unknown"), ("form", "evolved"), ("source_card", "minion_horde"),
    ("source_card", "unknown"), ("owner", "own"), ("verification_status", "unreviewed"),
])
def test_other_semantics_remain_visual_records_but_never_target_plays(field, value):
    draft = dataset_fixture()
    draft["deployments"][0][field] = value
    for annotation in draft["unit_annotations"]:
        if annotation["recording_id"] == "recording_1" and annotation["deployment_id"] == "play_1":
            if field in annotation:
                annotation[field] = value
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["confirmed_target_deployments"] == 7
    assert report["counts"]["training_unit_boxes"] == 96
    assert report["counts"]["negative_training_images"] == 0


def test_unreviewed_frame_is_retained_but_cannot_qualify_a_play():
    draft = dataset_fixture((1, 2, 2, 3))
    for frame in draft["frames"]:
        if frame["recording_id"] == "recording_1":
            frame["review_status"] = "pending"
            frame["all_identifiable_units_labelled"] = False
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["target_positive_matches"] == 3
    assert report["counts"]["confirmed_target_deployments"] == 7


def test_complete_positive_frame_cannot_omit_its_unit_boxes():
    draft = dataset_fixture()
    draft["unit_annotations"] = [a for a in draft["unit_annotations"]
                                 if not (a["recording_id"] == "recording_1"
                                         and a["frame_id"] == "play_1_frame_1")]
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("change", ["annotation_id", "frame_box", "renamed_event"])
def test_renamed_or_duplicate_evidence_is_rejected(change):
    draft = dataset_fixture()
    if change == "renamed_event":
        event = deepcopy(draft["deployments"][0])
        event["deployment_id"] = "manufactured_event"
        draft["deployments"].append(event)
    else:
        annotation = deepcopy(draft["unit_annotations"][0])
        if change == "frame_box":
            annotation["annotation_id"] = "manufactured_box"
        draft["unit_annotations"].append(annotation)
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)
    assert dataset_readiness(draft)["valid"] is False


@pytest.mark.parametrize("field,value", [
    ("x", -0.1), ("x", 0.99), ("width", 0), ("height", float("nan")), ("y", True),
])
def test_invalid_normalized_visible_boxes_reject(field, value):
    draft = dataset_fixture()
    draft["unit_annotations"][0]["normalized_bbox"][field] = value
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("location,field,value", [
    ("frames", "timestamp_seconds", float("nan")), ("frames", "raw_pts", True),
    ("recordings", "last_frame_seconds", float("inf")), ("recordings", "width", True),
    ("deployments", "onset_seconds", True),
])
def test_nonfinite_and_boolean_numbers_reject(location, field, value):
    draft = dataset_fixture()
    draft[location][0][field] = value
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("change", ["unknown", "other_form", "own", "unreviewed"])
def test_uncertain_or_other_visual_content_cannot_be_certified_absent(change):
    draft = dataset_fixture()
    if change == "unknown":
        draft["unknown_intervals"].append({"interval_id": "gap", "recording_id": "recording_1",
                                          "start_seconds": 1, "end_seconds": 3,
                                          "reason": "Unreviewed content"})
        start, end = 0, 4
    else:
        start, end = 10, 12
        field, value = {"other_form": ("form", "evolved"), "own": ("owner", "own"),
                        "unreviewed": ("verification_status", "unreviewed")}[change]
        draft["deployments"][0][field] = value
        for annotation in draft["unit_annotations"]:
            if annotation["recording_id"] == "recording_1" and annotation["deployment_id"] == "play_1" and field in annotation:
                annotation[field] = value
    draft["confirmed_absent_intervals"].append({
        "interval_id": "unsafe_absence", "recording_id": "recording_1",
        "start_seconds": start, "end_seconds": end,
        "review_provenance": {"method": "manual", "reviewed_by": "synthetic", "notes": "Reviewed range"},
    })
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


def test_complete_whole_file_accepts_without_result_ui():
    assert validate_dataset_shape(dataset_fixture()) is None


@pytest.mark.parametrize("change", ["start", "end", "incomplete", "technical", "edited", "unreviewed"])
def test_included_source_requires_actual_whole_file_and_valid_human_review(change):
    draft = dataset_fixture()
    recording = draft["recordings"][0]
    if change in {"start", "end"}:
        recording["complete_segment"][change + "_seconds"] = 1 if change == "start" else 99
    else:
        field = {"incomplete": "complete_recording", "technical": "technical_valid",
                 "edited": "unedited_recording", "unreviewed": "full_human_review"}[change]
        recording[field] = False
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


def test_invalid_excluded_source_is_retained_with_history():
    draft = dataset_fixture()
    draft["intake"][0].update(status="excluded", reason="Human-declared incomplete")
    draft["recordings"][0]["complete_recording"] = False
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["target_positive_matches"] == 3


@pytest.mark.parametrize("count", [4, 5])
def test_lomo_keeps_every_recording_and_frame_of_one_match_together(count):
    draft = add_reencoded_recording(dataset_fixture((2,) * count))
    folds = grouped_folds(draft)
    assert folds == grouped_folds(deepcopy(draft))
    assert len(folds) == count
    assert [fold["validation_match_ids"] for fold in folds] == [[f"match_{i}"] for i in range(1, count + 1)]
    for fold in folds:
        assert len(fold["train_match_ids"]) == count - 1
        assert not set(fold["train_recording_ids"]) & set(fold["validation_recording_ids"])
        train_frames = {(f["recording_id"], f["frame_id"]) for f in fold["train_frames"]}
        valid_frames = {(f["recording_id"], f["frame_id"]) for f in fold["validation_frames"]}
        assert not train_frames & valid_frames
        assert len(train_frames | valid_frames) == len(draft["frames"])
        assert ("recording_1" in fold["validation_recording_ids"]) == ("recording_1_reencoded" in fold["validation_recording_ids"])


def test_intake_order_drives_folds_without_mutating_input():
    draft = dataset_fixture()
    draft["intake"] = list(reversed(draft["intake"]))
    original = deepcopy(draft)
    assert [f["validation_match_ids"] for f in grouped_folds(draft)] == [
        ["match_4"], ["match_3"], ["match_2"], ["match_1"]]
    assert draft == original


@pytest.mark.parametrize("change", ["root", "nested", "dangling", "pts", "dimension", "target"])
def test_closed_types_references_and_frame_bindings_reject_conflicts(change):
    draft = dataset_fixture()
    if change == "root": draft["prediction"] = 0.9
    if change == "nested": draft["frames"][0]["prediction"] = 0.9
    if change == "dangling": draft["unit_annotations"][0]["deployment_id"] = "missing"
    if change == "pts": draft["frames"][0]["raw_pts"] += 10
    if change == "dimension": draft["frames"][0]["image_width"] = 480
    if change == "target": draft["target"]["form"] = "evolved"
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("path", ["../outside.mp4", "/absolute.mp4", "C:/absolute.mp4",
                                  "synthetic\\escape.mp4", "synthetic//empty.mp4"])
def test_recording_paths_are_safe_root_relative_declarations(path):
    draft = dataset_fixture()
    draft["recordings"][0]["source_path"] = path
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("field", ["index_path", "report_path"])
def test_export_bindings_reject_traversal(field):
    draft = dataset_fixture()
    draft["recordings"][0]["exports"][0][field] = "../outside.json"
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


def test_multiple_existing_exports_share_a_recording_without_regeneration():
    draft = dataset_fixture()
    export = deepcopy(draft["recordings"][0]["exports"][0])
    export.update(export_id="export_2", index_path="synthetic/extra/index.json",
                  report_path="synthetic/extra/report.json", index_sha256="9" * 64)
    draft["recordings"][0]["exports"].append(export)
    draft["frames"][0]["export_ids"].append("export_2")
    assert dataset_readiness(draft)["training_data_ready"] is True


def test_unassigned_unknown_visual_unit_does_not_manufacture_a_play():
    draft = dataset_fixture()
    annotation = deepcopy(draft["unit_annotations"][0])
    annotation.update(annotation_id="unassigned_unit", deployment_id=None,
                      owner="unknown", source_card="unknown", form="unknown")
    annotation["normalized_bbox"]["y"] = 0.5
    draft["unit_annotations"].append(annotation)
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["confirmed_target_deployments"] == 8
    assert report["counts"]["training_unit_boxes"] == 97


def test_undecodable_source_can_remain_excluded_without_invented_metadata():
    draft = dataset_fixture()
    draft["intake"][0].update(status="excluded", reason="Undecodable source retained")
    record = draft["recordings"][0]
    record.update(technical_valid=False, exports=[], complete_segment=None)
    for field in ("width", "height", "rotation_degrees", "time_base", "origin_pts",
                  "origin_time_base", "last_frame_seconds"):
        record[field] = None
    for field in ("frames", "deployments", "unit_annotations"):
        draft[field] = [row for row in draft[field] if row["recording_id"] != "recording_1"]
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["recordings"] == 4
    assert report["counts"]["target_positive_matches"] == 3


def test_renaming_a_frame_cannot_duplicate_its_pts_evidence():
    draft = dataset_fixture()
    frame = deepcopy(draft["frames"][0])
    frame["frame_id"] = "renamed_frame"
    draft["frames"].append(frame)
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


def test_unknown_interval_forces_a_potentially_unlabelled_frame_to_remain_pending():
    draft = dataset_fixture()
    draft["unknown_intervals"].append({"interval_id": "unknown_content", "recording_id": "recording_1",
                                      "start_seconds": 10, "end_seconds": 15, "reason": "Potential extra unit"})
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)
    for frame in draft["frames"]:
        if frame["recording_id"] == "recording_1" and frame["timestamp_seconds"] < 15:
            frame["review_status"] = "pending"
            frame["all_identifiable_units_labelled"] = False
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["confirmed_target_deployments"] == 7


def test_other_recording_absence_cannot_replace_first_intake_evaluation_source():
    draft = add_reencoded_recording(dataset_fixture(absent=True))
    draft["confirmed_absent_intervals"] = [i for i in draft["confirmed_absent_intervals"]
                                            if i["recording_id"] != "recording_1"]
    draft["confirmed_absent_intervals"].append({
        "interval_id": "alternate_absence", "recording_id": "recording_1_reencoded",
        "start_seconds": 0, "end_seconds": 8,
        "review_provenance": {"method": "manual", "reviewed_by": "synthetic", "notes": "Alternate review"},
    })
    report = dataset_readiness(draft)
    assert report["evaluation_ready"] is False
    assert report["confirmed_absent_seconds"] == 24
    assert report["per_match"][0]["evaluation_recording_id"] == "recording_1"
    assert report["per_match"][0]["confirmed_absent_seconds"] == 0
    assert report["per_recording"][-1]["confirmed_absent_seconds"] == 8


def test_same_match_recordings_with_different_origins_keep_separate_timelines():
    draft = add_reencoded_recording(dataset_fixture())
    record = draft["recordings"][-1]
    record["origin_pts"] = 2000
    for frame in draft["frames"]:
        if frame["recording_id"] == "recording_1_reencoded":
            frame["raw_pts"] += 6000
            frame["timestamp_seconds"] += 5
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["confirmed_target_deployments"] == 8
    assert report["counts"]["target_positive_matches"] == 4


def test_alternate_recording_boxes_cannot_supply_missing_primary_deployment_support():
    draft = add_reencoded_recording(dataset_fixture())
    draft["unit_annotations"] = [a for a in draft["unit_annotations"]
                                 if not (a["recording_id"] == "recording_1" and a["deployment_id"] == "play_1")]
    for frame in draft["frames"]:
        if frame["recording_id"] == "recording_1" and frame["frame_id"].startswith("play_1_"):
            frame.update(review_status="pending", all_identifiable_units_labelled=False)
    report = dataset_readiness(draft)
    assert report["valid"] is True
    assert report["counts"]["confirmed_target_deployments"] == 7
    assert report["training_data_ready"] is False


def test_renamed_identical_source_cannot_claim_an_independent_match():
    draft = dataset_fixture()
    draft["recordings"][1]["source_sha256"] = draft["recordings"][0]["source_sha256"]
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)


@pytest.mark.parametrize("presence", ["positive", "unknown"])
def test_certified_absence_rejects_pending_unboxed_non_absent_frame(presence):
    draft = dataset_fixture(absent=True)
    frame = deepcopy(draft["frames"][0])
    frame.update(frame_id="pending_unboxed_frame", timestamp_seconds=1, raw_pts=2000,
                 image_path="synthetic/pending_unboxed.png", review_status="pending",
                 minion_presence=presence, all_identifiable_units_labelled=False)
    draft["frames"].append(frame)
    with pytest.raises(EvidenceError):
        validate_dataset_shape(draft)
    report = dataset_readiness(draft)
    assert report["valid"] is False
    assert report["evaluation_ready"] is False
