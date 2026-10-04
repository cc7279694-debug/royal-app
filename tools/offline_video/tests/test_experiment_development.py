"""Real v1 adapters and manual-development gates, using anonymous evidence."""
from copy import deepcopy
from importlib import import_module

import pytest

from clash_tracker_video.evidence_contract import EvidenceError, validate_evidence
from clash_tracker_video.experiment_lock import make_development_lock
from evidence_fixtures import synthetic_evidence, synthetic_indexes
from experiment_fixtures import development_fixture, split_forms, user_confirmed_development_fixture


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


@pytest.mark.parametrize("equipment,expected_valid", [("not_equipped", False), ("unknown", True)])
def test_evolved_form_rejects_explicit_unequipped_but_preserves_unknown(equipment, expected_valid):
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    candidate["form"] = "evolved"
    candidate["evidence"]["target_card"]["variant"] = "known_evolution"
    candidate["evolution"]["equipped"] = equipment
    draft["selection"]["form"] = "evolved"
    for deployment in candidate["deployments"]:
        deployment["form"] = "evolved"
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    report = api().validate_development(draft, indexes)
    assert report["valid"] is expected_valid
    if expected_valid:
        assert report["status"] == "DEV_VALIDATED"
        assert report["candidates"][0]["clear_verified_plays"] == 2
        assert api().require_development(draft, indexes)["draft"]["candidates"][0]["evolution"]["equipped"] == "unknown"
    else:
        with pytest.raises(EvidenceError):
            api().require_development(draft, indexes)


@pytest.mark.parametrize("container,field,value", [
    ("recording", "time_base", {"numerator": True, "denominator": 1000}),
    ("recording", "origin_time_base", {"numerator": True, "denominator": 1000}),
    ("recording", "width", 64.0),
    ("recording", "height", 48.0),
    ("recording", "origin_pts", 5000.0),
    ("recording", "rotation_degrees", 0.0),
    ("frame", "time_base", {"numerator": True, "denominator": 1000}),
    ("frame", "raw_pts", 6000.0),
    ("frame", "timestamp_seconds", True),
    ("frame", "image_width", 64.0),
    ("frame", "image_height", 48.0),
])
def test_numerically_equal_invalid_snapshot_types_cannot_freeze(container, field, value):
    draft, indexes = development_fixture()
    target = indexes["synthetic"]["recording"] if container == "recording" else indexes["synthetic"]["frames"][0]
    target[field] = value
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    with pytest.raises(EvidenceError):
        api().require_development(draft, indexes)


@pytest.mark.parametrize("mutation", [
    lambda i: i["synthetic"].update(extra="C:/private/account"),
    lambda i: i["synthetic"].update(frames={"private": "C:/private/account"}),
    lambda i: i["synthetic"]["frames"].__setitem__(0, "C:/private/account"),
    lambda i: i["synthetic"]["frames"][0].update(time_base={"numerator": [], "denominator": 1000}),
    lambda i: i["synthetic"]["frames"].append({**deepcopy(i["synthetic"]["frames"][0]),
                                            "time_base": {"numerator": True, "denominator": 1000}}),
])
def test_malformed_index_snapshot_is_sanitized_without_traceback(mutation):
    draft, indexes = development_fixture()
    mutation(indexes)
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    assert "private" not in " ".join(report["reasons"])
    with pytest.raises(EvidenceError) as error:
        api().require_development(draft, indexes)
    assert "private" not in str(error.value)


def _assert_development_refused(draft, indexes):
    for candidate in draft["candidates"]:
        assert validate_evidence(candidate["evidence"], indexes) == []
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    assert report["status"] == "NOT_READY"
    with pytest.raises(EvidenceError):
        api().require_development(draft, indexes)
    with pytest.raises(EvidenceError):
        make_development_lock(draft, indexes)


@pytest.mark.parametrize("first_complete", [True, False])
def test_development_cannot_accumulate_plays_across_match_segments(first_complete):
    draft, indexes = development_fixture()
    candidate = draft["candidates"][0]
    evidence = candidate["evidence"]
    first = deepcopy(evidence["match_segments"][0])
    first.update(end_seconds=3, capture_complete=first_complete)
    second = deepcopy(evidence["match_segments"][0])
    second.update(segment_id="second_match", start_seconds=4)
    evidence["match_segments"] = [first, second]
    evidence["occurrences"][1]["match_segment_id"] = "second_match"
    # Remove only the old negative crossing both matches; keep legal reviewed
    # absences inside their assigned match and the result screen outside both.
    evidence["negative_intervals"] = [n for n in evidence["negative_intervals"]
                                      if n["negative_id"] != "negative1"]
    evidence["negative_intervals"][1]["match_segment_id"] = "second_match"
    for deployment in candidate["deployments"]:
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    _assert_development_refused(draft, indexes)


def _two_candidate_shared_match():
    draft, _ = development_fixture()
    full = synthetic_evidence(3)
    indexes = synthetic_indexes(full)
    normal = draft["candidates"][0]
    normal["evidence"] = deepcopy(full)
    normal["evidence"]["occurrences"] = normal["evidence"]["occurrences"][:2]
    normal["evidence"]["frame_annotations"] = normal["evidence"]["frame_annotations"][:6]
    normal["evidence"]["negative_intervals"] = []
    other = deepcopy(normal)
    other["candidate_id"] = "candidate_other"
    other["card_id"] = "other_synthetic_card"
    other["evidence"] = deepcopy(full)
    other["evidence"]["target_card"]["card_id"] = "other_synthetic_card"
    other["evidence"]["occurrences"] = other["evidence"]["occurrences"][2:]
    other["evidence"]["occurrences"][0]["card_id"] = "other_synthetic_card"
    other["evidence"]["frame_annotations"] = other["evidence"]["frame_annotations"][6:]
    other["evidence"]["negative_intervals"] = []
    other["deployments"] = [deepcopy(normal["deployments"][0])]
    other["deployments"][0]["play_id"] = "play2"
    draft["candidates"] = [normal, other]
    for candidate in draft["candidates"]:
        for deployment in candidate["deployments"]:
            deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    return draft, indexes


@pytest.mark.parametrize("field,value", [
    ("segment_id", "inconsistent_match"), ("start_seconds", .5),
    ("end_seconds", 18), ("boundary_uncertainty_seconds", .25),
    ("notes", "Different whole-match metadata"),
])
def test_candidate_bundles_must_share_identical_complete_match_metadata(field, value):
    draft, indexes = _two_candidate_shared_match()
    other = draft["candidates"][1]["evidence"]
    other["match_segments"][0][field] = value
    if field == "segment_id":
        other["occurrences"][0]["match_segment_id"] = value
    _assert_development_refused(draft, indexes)


def test_one_shared_complete_match_remains_valid_for_all_candidates():
    draft, indexes = _two_candidate_shared_match()
    for candidate in draft["candidates"]:
        assert validate_evidence(candidate["evidence"], indexes) == []
    report = api().validate_development(draft, indexes)
    assert report["status"] == "DEV_VALIDATED"
    assert [c["clear_verified_plays"] for c in report["candidates"]] == [2, 1]
    assert make_development_lock(draft, indexes)["lock_type"] == "development"


def test_empty_candidates_remain_valid_but_not_ready():
    draft, indexes = development_fixture()
    draft["candidates"] = []
    draft["selection"] = None
    report = api().validate_development(draft, indexes)
    assert report["valid"] is True
    assert report["status"] == "NOT_READY"
    assert report["candidates"] == []
    with pytest.raises(EvidenceError):
        make_development_lock(draft, indexes)


@pytest.mark.parametrize("screen_present", [False, True])
def test_user_confirmed_completion_does_not_require_result_screen(screen_present):
    draft, indexes = user_confirmed_development_fixture()
    draft["identity"]["terminal_result_screen_present"] = screen_present
    report = api().validate_development(draft, indexes)
    assert report["status"] == "DEV_VALIDATED"
    assert report["valid"] is True
    assert report["candidates"][0]["clear_verified_plays"] == 2
    frozen = api().require_development(draft, indexes)
    assert frozen["draft"]["identity"]["completion_attestation"] == "user_confirmed"
    assert frozen["draft"]["identity"]["terminal_result_screen_present"] is screen_present
    assert frozen["draft"]["candidates"][0]["evidence"]["match_segments"][0]["end_seconds"] == 20
    assert frozen["derived"]["unknown_intervals"][0]["end_seconds"] == 20
    assert not any(n["reason"] == "result" for n in frozen["draft"]["candidates"][0]["evidence"]["negative_intervals"])


@pytest.mark.parametrize("field,value", [
    ("completion_attestation", None), ("completion_attestation", True),
    ("completion_attestation", "machine_confirmed"), ("completion_attestation", "C:/private/account"),
    ("terminal_result_screen_present", 0), ("terminal_result_screen_present", 1),
    ("terminal_result_screen_present", "false"), ("terminal_result_screen_present", None),
    ("extra", "C:/private/account"),
])
def test_completion_metadata_is_closed_and_strictly_typed(field, value):
    draft, indexes = user_confirmed_development_fixture()
    draft["identity"][field] = value
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    with pytest.raises(EvidenceError) as error:
        api().require_development(draft, indexes)
    assert "private" not in str(error.value)


@pytest.mark.parametrize("missing", ["completion_attestation", "terminal_result_screen_present"])
def test_completion_metadata_must_be_paired(missing):
    draft, indexes = user_confirmed_development_fixture()
    del draft["identity"][missing]
    assert api().validate_development(draft, indexes)["valid"] is False


@pytest.mark.parametrize("field", ["complete_recording", "unedited_recording", "full_human_review"])
def test_user_confirmation_does_not_override_false_review_attestations(field):
    draft, indexes = user_confirmed_development_fixture()
    draft["identity"][field] = False
    assert api().validate_development(draft, indexes)["valid"] is False
    with pytest.raises(EvidenceError):
        make_development_lock(draft, indexes)


def test_user_confirmation_does_not_override_incomplete_segment():
    draft, indexes = user_confirmed_development_fixture()
    draft["candidates"][0]["evidence"]["match_segments"][0]["capture_complete"] = False
    assert api().validate_development(draft, indexes)["valid"] is False
    with pytest.raises(EvidenceError):
        make_development_lock(draft, indexes)


@pytest.mark.parametrize("start,end", [(0, 19), (.25, 20)])
def test_user_confirmed_segment_must_cover_entire_recording(start, end):
    draft, indexes = user_confirmed_development_fixture()
    evidence = draft["candidates"][0]["evidence"]
    # Keep the shortened segment valid under v1; only the new completion
    # attestation binds it to the full file. Terminal 19..20 stays unknown.
    evidence["negative_intervals"] = []
    evidence["match_segments"][0].update(start_seconds=start, end_seconds=end)
    assert validate_evidence(evidence, indexes) == []
    report = api().validate_development(draft, indexes)
    assert report["valid"] is False
    assert report["status"] == "NOT_READY"
    with pytest.raises(EvidenceError):
        api().require_development(draft, indexes)
    with pytest.raises(EvidenceError):
        make_development_lock(draft, indexes)


def test_user_confirmed_full_segment_without_result_screen_can_lock():
    draft, indexes = user_confirmed_development_fixture()
    assert draft["identity"]["terminal_result_screen_present"] is False
    evidence = draft["candidates"][0]["evidence"]
    segment = evidence["match_segments"][0]
    assert segment["start_seconds"] == 0
    assert segment["end_seconds"] == evidence["recordings"][0]["last_frame_seconds"]
    assert api().validate_development(draft, indexes)["status"] == "DEV_VALIDATED"
    assert make_development_lock(draft, indexes)["lock_type"] == "development"
