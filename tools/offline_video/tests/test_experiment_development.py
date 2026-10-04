"""Real v1 adapters and manual-development gates, using anonymous evidence."""
from copy import deepcopy
from importlib import import_module

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from experiment_fixtures import development_fixture, split_forms


def api():
    # Missing behavior is reported as an assertion during the initial RED run.
    try:
        return import_module("clash_tracker_video.experiment_development")
    except ModuleNotFoundError:
        pytest.fail("Development validator has not been implemented")


def test_two_clear_normal_plays_are_eligible_without_changing_inputs():
    draft, indexes = development_fixture()
    before = deepcopy((draft, indexes))
    report = api().validate_development(draft, indexes)
    assert report["status"] == "DEV_VALIDATED"
    assert report["candidates"][0]["clear_verified_plays"] == 2
    assert report["candidates"][0]["eligible"] is True
    assert report["coverage_gaps"] == []
    frozen = api().require_development(draft, indexes)
    assert frozen["draft"] == draft
    assert frozen["derived"] == report
    frozen["draft"]["identity"]["recording_id"] = "changed"
    assert (draft, indexes) == before


def test_normal_and_evolved_cannot_aggregate_into_two_plays():
    draft, indexes = development_fixture()
    split_forms(draft)
    report = api().validate_development(draft, indexes)
    assert report["status"] == "NOT_READY"
    assert [c["clear_verified_plays"] for c in report["candidates"]] == [1, 1]
    assert all(c["eligible"] is False for c in report["candidates"])
    assert report["coverage_gaps"]


def test_three_key_frames_of_one_play_do_not_count_as_three_plays():
    draft, indexes = development_fixture()
    split_forms(draft)
    draft["candidates"] = draft["candidates"][:1]
    assert api().validate_development(draft, indexes)["candidates"][0]["clear_verified_plays"] == 1


@pytest.mark.parametrize("selection", [None, {"candidate_id": "absent", "card_id": "absent",
    "form": "normal", "method": "manual", "reason": "Manual selection"}])
def test_selection_must_reference_actual_candidate_evidence(selection):
    draft, indexes = development_fixture()
    draft["selection"] = selection
    assert api().validate_development(draft, indexes)["status"] == "NOT_READY"
    with pytest.raises(EvidenceError):
        api().require_development(draft, indexes)


def test_unknown_form_is_retained_but_cannot_be_selected():
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    candidate["form"] = "unknown"
    candidate["evidence"]["target_card"]["variant"] = "unknown"
    for play, deployment in zip(candidate["evidence"]["occurrences"], candidate["deployments"]):
        play["manual_verification_status"] = "ambiguous"
        deployment["form"] = "unknown"
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    draft["selection"]["form"] = "unknown"
    report = api().validate_development(draft, indexes)
    assert report["status"] == "NOT_READY"
    assert report["candidates"][0]["clear_verified_plays"] == 0


def test_reused_occurrence_reference_is_rejected():
    draft, indexes = development_fixture()
    draft["candidates"][0]["deployments"][1]["play_id"] = "play0"
    assert api().validate_development(draft, indexes)["valid"] is False


def test_renamed_identical_deployment_cannot_inflate_count():
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    original = candidate["evidence"]["occurrences"][0]
    duplicate = deepcopy(original)
    duplicate["play_id"] = "renamed_play"
    duplicate["evidence_annotation_ids"] = []
    boxes = []
    for box in candidate["evidence"]["frame_annotations"][:3]:
        new = deepcopy(box)
        new["annotation_id"] = "renamed_" + box["annotation_id"]
        new["play_id"] = "renamed_play"
        duplicate["evidence_annotation_ids"].append(new["annotation_id"])
        boxes.append(new)
    candidate["evidence"]["occurrences"][1] = duplicate
    candidate["evidence"]["frame_annotations"] = candidate["evidence"]["frame_annotations"][:3] + boxes
    candidate["deployments"][1]["play_id"] = "renamed_play"
    assert api().validate_development(draft, indexes)["valid"] is False


@pytest.mark.parametrize("unknown", [False, True])
def test_other_or_unknown_form_cannot_overlap_confirmed_negative(unknown):
    draft, indexes = development_fixture()
    split_forms(draft)
    candidate = draft["candidates"][0]
    candidate["evidence"]["negative_intervals"] = [{
        "negative_id": "contradictory", "recording_id": "synthetic", "start_seconds": 5,
        "end_seconds": 6, "reason": "target_absent", "match_segment_id": "match",
        "non_match": False, "review_status": "verified"}]
    if unknown:
        other = draft["candidates"][1]
        other["form"] = "unknown"
        other["evidence"]["target_card"]["variant"] = "unknown"
        other["evidence"]["occurrences"][0]["manual_verification_status"] = "ambiguous"
        other["deployments"][0]["form"] = "unknown"
    assert api().validate_development(draft, indexes)["valid"] is False


def test_explicit_unknown_interval_rejects_overlap_with_negative():
    draft, indexes = development_fixture()
    draft["unknown_intervals"] = [{"unknown_id": "uncertain", "recording_id": "synthetic",
        "start_seconds": 3, "end_seconds": 4, "reason": "Possible missed deployment"}]
    assert api().validate_development(draft, indexes)["valid"] is False


@pytest.mark.parametrize("cause", ["equipment", "rules", "missed", "unknown_interval", "gap"])
def test_uncertainty_forbids_claimed_evolution_precision(cause):
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    if cause == "equipment":
        candidate["evolution"]["equipped"] = "unknown"
    elif cause == "rules":
        candidate["evolution"]["rules_version"] = None
    elif cause == "missed":
        candidate["deployments"][0]["possible_missed_play"] = True
    else:
        candidate["evidence"]["negative_intervals"] = []
        if cause == "unknown_interval":
            draft["unknown_intervals"] = [{"unknown_id": "uncertain", "recording_id": "synthetic",
                "start_seconds": 3, "end_seconds": 4, "reason": "Unreviewed visibility"}]
    assert api().validate_development(draft, indexes)["valid"] is False
    for deployment in candidate["deployments"]:
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    assert api().validate_development(draft, indexes)["valid"] is True


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(freeze_version=True),
    lambda d: d.update(created_at="2026-10-04T01:00:00+08:00"),
    lambda d: d["identity"].update(provenance="historical"),
    lambda d: d["identity"].update(full_human_review=False),
    lambda d: d["candidates"][0].update(notes=[]),
    lambda d: d["candidates"][0]["evolution"].update(charge_requirement=True),
    lambda d: d["candidates"][0]["evolution"].update(equipped=[]),
    lambda d: d["candidates"][0]["deployments"][0].update(form={}),
    lambda d: d["candidates"][0]["deployments"][0]["evolution"].update(remaining_count=float("nan")),
    lambda d: d["selection"].update(extra="C:/private/account"),
    lambda d: d["candidates"][0]["evidence"]["frame_annotations"][0].update(normalized_bbox=[]),
])
def test_nested_malformed_inputs_have_sanitized_predictable_errors(mutation):
    draft, indexes = development_fixture()
    mutation(draft)
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    with pytest.raises(EvidenceError) as error:
        api().require_development(draft, indexes)
    assert "private" not in str(error.value)
    assert "account" not in str(error.value)


def test_existing_v1_export_validation_remains_mandatory():
    draft, indexes = development_fixture()
    indexes["synthetic"]["frames"][0]["raw_pts"] += 1
    assert api().validate_development(draft, indexes)["valid"] is False


def test_same_recording_metadata_must_match_across_candidate_bundles():
    draft, indexes = development_fixture()
    split_forms(draft)
    draft["candidates"][1]["evidence"]["recordings"][0]["perspective"] = "unknown"
    assert api().validate_development(draft, indexes)["valid"] is False


def test_frozen_payload_binds_verified_pixel_hash_and_only_used_frames():
    draft, indexes = development_fixture()
    indexes["synthetic"]["frames"][0]["_content_hash"] = "a" * 64
    indexes["synthetic"]["frames"].append({"frame_id": "unused", "status": "success"})
    frozen = api().require_development(draft, indexes)
    snapshot = frozen["index_snapshot"]["synthetic"]
    assert len(snapshot["frames"]) == 6
    assert snapshot["frames"][0]["_content_hash"] == "a" * 64
    indexes["synthetic"]["frames"][0]["_content_hash"] = "b" * 64
    changed = api().require_development(draft, indexes)
    assert frozen["index_snapshot"] != changed["index_snapshot"]


def test_terminal_unknown_point_conflicts_with_closed_terminal_negative():
    draft, indexes = development_fixture()
    draft["unknown_intervals"] = [{"unknown_id": "terminal", "recording_id": "synthetic",
        "start_seconds": 20, "end_seconds": 20, "reason": "Exact terminal uncertainty"}]
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    assert "overlaps" in report["reasons"][0]
    draft["candidates"][0]["evidence"]["negative_intervals"].pop()
    for deployment in draft["candidates"][0]["deployments"]:
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    report = api().validate_development(draft, indexes)
    assert report["valid"] is True
    assert report["unknown_intervals"][0]["start_seconds"] == 20
    assert report["coverage_gaps"][-1]["start_seconds"] == 19


@pytest.mark.parametrize("field,value", [("_content_hash", "private malformed hash"),
    ("requested_seconds", float("inf")), ("_aliases", ["../private.png"])])
def test_invalid_bound_export_metadata_is_invalid_at_readiness_boundary(field, value):
    draft, indexes = development_fixture()
    indexes["synthetic"]["frames"][0][field] = value
    assert api().validate_development(draft, indexes)["valid"] is False


def test_known_evolved_form_requires_evolution_capability():
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    candidate["form"] = "evolved"
    candidate["evidence"]["target_card"]["variant"] = "known_evolution"
    candidate["evolution"] = {"capable": False, "equipped": "not_equipped", "charge_requirement": None,
                              "rules_version": None}
    draft["selection"]["form"] = "evolved"
    for deployment in candidate["deployments"]:
        deployment["form"] = "evolved"
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    assert api().validate_development(draft, indexes)["valid"] is False


def test_independent_units_can_share_original_frame_with_distinct_boxes():
    draft, indexes = development_fixture()
    evidence = draft["candidates"][0]["evidence"]
    evidence["occurrences"][0]["visible_end_seconds"] = 6
    evidence["negative_intervals"] = [n for n in evidence["negative_intervals"] if n["negative_id"] != "negative1"]
    first_box, second_box = evidence["frame_annotations"][0], evidence["frame_annotations"][3]
    for field in ("frame_id", "timestamp_seconds", "raw_pts", "time_base", "image_path"):
        first_box[field] = deepcopy(second_box[field])
    first_box["normalized_bbox"] = {"x": .6, "y": .6, "width": .3, "height": .3}
    report = api().validate_development(draft, indexes)
    assert report["status"] == "DEV_VALIDATED"
    assert report["candidates"][0]["clear_verified_plays"] == 2
