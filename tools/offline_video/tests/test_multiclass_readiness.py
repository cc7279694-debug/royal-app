"""Synthetic independent supports and exact Development-only scale statistics."""
from copy import deepcopy
from fractions import Fraction
from importlib import import_module
from hashlib import sha256

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.evidence_prepare import frame_id
from clash_tracker_video.multiclass_contract import backend_label_maps, validate_multiclass_shape
from clash_tracker_video.experiment_lock import canonical_bytes
from multiclass_fixtures import add_rerecording, multiclass_fixture


def api():
    try:
        return import_module("clash_tracker_video.multiclass_readiness")
    except ModuleNotFoundError:
        pytest.fail("Multiclass candidate/scale/readiness APIs are not implemented")


def ratio(numerator, denominator=1):
    return {"numerator": numerator, "denominator": denominator}


def selected(draft, ids=None):
    ids = ids or [c["visual_class_id"] for c in draft["taxonomy"]["classes"]]
    draft["selection"] = {"selected_class_ids": ids,
        "class_decisions": [{"visual_class_id": c["visual_class_id"], "selected": c["visual_class_id"] in ids,
                             "reason": "Synthetic pre-model class decision"} for c in draft["taxonomy"]["classes"]],
        "scale_snapshot_digest": "a" * 64, "policy_id": "dev_moving_area_quantiles_v1"}
    draft["backend_label_maps"] = backend_label_maps(ids)
    return draft


def report_class(report, cid):
    return next(row for row in report["class_reports"] if row["visual_class_id"] == cid)


def support(report, cid, owner, split):
    return next(row for row in report_class(report, cid)["support"]
                if row["owner"] == owner and row["split"] == split)


def areas(draft, scores):
    for row in draft["annotations"]:
        row["box"].update(width=0.1, height=scores[row["visual_class_id"]] * 10)
    return draft


def test_three_units_and_many_frames_are_one_group():
    draft = multiclass_fixture(("unit.speck",), match_count=1, own_class_ids=())
    original, annotation, coverage = draft["frames"][0], draft["annotations"][0], draft["coverage"][0]
    draft["frames"], draft["annotations"], draft["coverage"] = [], [], []
    for index in range(5):
        frame = deepcopy(original)
        frame.update(raw_pts=11000 + index * 200, timestamp_seconds=10 + index / 5)
        frame["frame_id"] = frame_id(frame["recording_id"], frame["raw_pts"], Fraction(1, 1000))
        frame["image_sha256"] = f"{index + 100:064x}"
        draft["frames"].append(frame)
        row = deepcopy(coverage)
        row.update(coverage_id=f"coverage_{index}", frame_id=frame["frame_id"])
        draft["coverage"].append(row)
        for unit in range(3):
            box = deepcopy(annotation)
            box.update(annotation_id=f"annotation_{index}_{unit}", frame_id=frame["frame_id"],
                       entity_occurrence_id=f"entity_{unit}")
            box["box"]["x"] = 0.1 + unit / 5
            draft["annotations"].append(box)
    row = support(api().candidate_eligibility(draft), "unit.speck", "opponent", "train")
    assert row["counts"] == {"matches": 1, "groups": 1, "entities": 3, "frames": 5, "boxes": 15}
    assert report_class(api().candidate_eligibility(draft), "unit.speck")["basic_qualified"] is False


def test_small_missing_clean_support_is_insufficient():
    draft = selected(multiclass_fixture())
    for row in draft["annotations"]:
        if row["visual_class_id"] == "unit.speck":
            row["occlusion"] = "partial"
    report = api().multiclass_readiness(draft)
    assert report["status"] == "SIZE_COVERAGE_INSUFFICIENT"
    assert "unit.speck" in report["scale_report"]["candidate_class_ids"]
    assert report_class(report["scale_report"], "unit.speck")["scale_support_pending"] is True


def test_all_equal_scales_fail_coverage():
    draft = areas(multiclass_fixture(), {"unit.speck": 0.01, "unit.guard": 0.01, "building.anchor": 0.04})
    report = api().development_scale_report(draft)
    assert report["size_coverage_status"] == "SIZE_COVERAGE_INSUFFICIENT"
    assert report["cutpoints"] == {"q25": ratio(1, 100), "q75": ratio(1, 100)}
    assert all(report_class(report, cid)["scale_group"] is None for cid in ("unit.speck", "unit.guard"))


def test_collapsed_quantiles_use_fixed_tie_fallback():
    ids = tuple(f"unit.type_{i}" for i in range(5))
    draft = areas(multiclass_fixture(ids), dict(zip(ids, (0.01, 0.02, 0.02, 0.02, 0.02))))
    report = api().development_scale_report(draft)
    assert report["tie_fallback_used"] is True
    assert report["cutpoints"] == {"q25": ratio(1, 50), "q75": ratio(1, 50)}
    assert [report_class(report, cid)["scale_group"] for cid in ids] == ["relative_small", "large", "large", "large", "large"]


def test_original_resolution_changes_pixels_not_normalized_area():
    draft = multiclass_fixture()
    before = report_class(api().development_scale_report(draft), "unit.speck")["all_reviewed"]
    for record in draft["recordings"]:
        record["width"] *= 2
        record["height"] *= 2
    for frame in draft["frames"]:
        frame["image_width"] *= 2
        frame["image_height"] *= 2
    after = report_class(api().development_scale_report(draft), "unit.speck")["all_reviewed"]
    assert before["width_px"]["p50"] == ratio(96, 5)
    assert after["width_px"]["p50"] == ratio(192, 5)
    assert before["height_px"]["p50"] == ratio(144, 5)
    assert after["height_px"]["p50"] == ratio(288, 5)
    assert before["area_norm"] == after["area_norm"]
    assert before["area_norm"]["p50"] == ratio(9, 5000)


def test_selected_class_filter_cannot_change_scale_pool():
    ids = tuple(f"unit.type_{i}" for i in range(5))
    draft = areas(multiclass_fixture(ids), dict(zip(ids, (0.01, 0.02, 0.03, 0.04, 0.05))))
    before = api().development_scale_report(draft)
    selected(draft, list(ids[1:4]))
    assert api().development_scale_report(draft) == before
    assert before["candidate_class_ids"] == list(ids)


def test_opponent_majority_and_one_complete_own_control_are_data_ready_without_lock():
    draft = selected(multiclass_fixture())
    before = deepcopy(draft)
    report = api().multiclass_readiness(draft)
    assert report["ready"] is True
    assert report["status"] == "MULTICLASS_DATASET_READY"
    assert draft == before
    own_guard = next(row for row in report["export_support"] if row["joint_label"] == "unit.guard::own")
    assert all(row["qualification"] == "not_qualified" and row["evaluation"] == "not_evaluated"
               for row in own_guard["support"])


def test_without_any_complete_own_control_is_insufficient():
    report = api().multiclass_readiness(selected(multiclass_fixture(own_class_ids=())))
    assert report["ready"] is False
    assert "need_own_control_in_both_splits" in report["blocking_reasons"]


def test_pending_required_frame_cannot_use_scale_support_as_export_support():
    draft = selected(multiclass_fixture())
    fid = next(row["frame_id"] for row in draft["annotations"]
               if row["visual_class_id"] == "unit.guard" and row["recording_id"] == "recording_2")
    next(frame for frame in draft["frames"] if frame["frame_id"] == fid)["review_state"] = "pending"
    report = api().multiclass_readiness(draft)
    assert report["scale_report"]["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    assert report["ready"] is False
    assert "missing_export_opponent:unit.guard:development_validation" in report["blocking_reasons"]


def test_unknown_owner_never_supplies_opponent_or_empty_background():
    draft = selected(multiclass_fixture())
    for group in draft["groups"]:
        if group["visual_class_id"] == "unit.guard":
            group["owner"] = "unknown"
    for annotation in draft["annotations"]:
        if annotation["visual_class_id"] == "unit.guard":
            annotation["owner"] = "unknown"
    report = api().multiclass_readiness(draft)
    assert report["ready"] is False
    assert support(report["candidate_report"], "unit.guard", "opponent", "train")["counts"]["groups"] == 0
    assert draft["annotations"][2]["owner"] == "unknown"


def test_duplicate_exports_and_rerecording_add_no_support_or_scale_weight():
    draft = multiclass_fixture()
    before = api().candidate_eligibility(draft)
    scale_before = api().development_scale_report(draft)
    for record in draft["recordings"]:
        copy = deepcopy(record["exports"][0])
        copy["export_id"] = "export_2"
        record["exports"].append(copy)
    for frame in draft["frames"]:
        frame["export_ids"].append("export_2")
    add_rerecording(draft)
    assert api().candidate_eligibility(draft) == before
    after = api().development_scale_report(draft)
    assert after["cutpoints"] == scale_before["cutpoints"]
    assert [row["score"] for row in after["class_reports"]] == [row["score"] for row in scale_before["class_reports"]]


def test_semantic_collection_order_is_stable_except_original_intake():
    draft = multiclass_fixture()
    before = api().development_scale_report(draft)
    for key in ("matches", "recordings", "groups", "frames", "annotations", "coverage", "split_assignment"):
        draft[key].reverse()
    draft["taxonomy"]["classes"].reverse()
    assert api().development_scale_report(draft) == before
    draft["intake"].reverse()
    assert api().development_scale_report(draft)["candidate_semantic_sha256"] != before["candidate_semantic_sha256"]


def test_prospective_test_and_unknown_form_are_retained_but_not_scale_support():
    draft = multiclass_fixture()
    draft["split_assignment"][1]["split"] = "prospective_test"
    draft["recordings"][1]["split"] = "prospective_test"
    draft["intake"][1]["status"] = "pending"
    report = api().candidate_eligibility(draft)
    assert report["development_match_ids"] == ["match_1"]
    assert report["qualified_class_ids"] == []
    assert api().development_scale_report(draft)["candidate_class_ids"] == []
    assert len(draft["annotations"]) == 8


def test_source_and_data_shortages_are_reported_together():
    draft = selected(multiclass_fixture(own_class_ids=()))
    draft["provenance"][0]["allowed_scope"] = "reference_only"
    report = api().multiclass_readiness(draft)
    assert report["ready"] is False
    assert "need_own_control_in_both_splits" in report["blocking_reasons"]
    assert "source_not_training_qualified:synthetic_source" in report["blocking_reasons"]


def test_invalid_draft_has_no_fabricated_reports_or_digests():
    report = api().multiclass_readiness({"unexpected": "malformed"})
    assert report == {"status": "INVALID_DATASET", "ready": False,
                      "blocking_reasons": ["invalid_multiclass_shape"], "candidate_report": None,
                      "scale_report": None, "export_support": []}


def test_unknown_scale_policy_rejects_shape_not_reinterpreted_as_current_policy():
    draft = selected(multiclass_fixture())
    draft["selection"]["policy_id"] = "guessed_policy_v2"
    assert api().multiclass_readiness(draft)["status"] == "INVALID_DATASET"


def test_required_report_types_validate_without_new_fields():
    from clash_tracker_video.multiclass_contract import CandidateReport, ReadinessReport, ScaleReport, _validate_types
    draft = selected(multiclass_fixture())
    _validate_types(api().candidate_eligibility(draft), CandidateReport)
    _validate_types(api().development_scale_report(draft), ScaleReport)
    _validate_types(api().multiclass_readiness(draft), ReadinessReport)


def derived_observation(draft, original, suffix, *, width=0.2, height=0.2):
    group = deepcopy(next(g for g in draft["groups"] if g["appearance_group_id"] == original["appearance_group_id"]))
    group.update(appearance_group_id=group["appearance_group_id"] + suffix,
                 parent_group_id=original["appearance_group_id"], origin_kind="summoned",
                 human_deployment_id=None)
    row = deepcopy(original)
    row.update(annotation_id=row["annotation_id"] + suffix,
               appearance_group_id=group["appearance_group_id"], entity_occurrence_id=row["entity_occurrence_id"] + suffix)
    row["box"].update(x=0.6, width=width, height=height)
    draft["groups"].append(group)
    draft["annotations"].append(row)
    return group, row


def snapshot_for(draft):
    basis = api().scale_basis(draft)
    envelope = {"kind": "multiclass_scale_snapshot", "version": 1, "id": "synthetic_snapshot",
                "created_at": "2026-10-05T02:00:00Z", "payload": {
                    "draft": basis, "draft_semantic_sha256": api().scale_basis_sha256(basis),
                    "candidate_report": api().candidate_eligibility(basis),
                    "scale_report": api().development_scale_report(basis)}}
    return {**envelope, "digest": sha256(canonical_bytes(envelope)).hexdigest()}


def test_same_causal_chain_is_one_group_with_traceable_actual_members():
    draft = multiclass_fixture()
    original = draft["annotations"][0]
    child, row = derived_observation(draft, original, "_child")
    candidate = api().candidate_eligibility(draft)
    cell = support(candidate, "unit.speck", "opponent", "train")
    assert cell["counts"] == {"matches": 1, "groups": 1, "entities": 2, "frames": 1, "boxes": 2}
    assert cell["appearance_group_ids"] == sorted([original["appearance_group_id"], child["appearance_group_id"]])
    group = next(r for r in report_class(api().development_scale_report(draft), "unit.speck")["support"]
                 if r["underlying_match_id"] == "match_1" and r["owner"] == "opponent")
    assert group["clean_annotation_ids"] == sorted([original["annotation_id"], row["annotation_id"]])
    assert group["score"] == ratio(209, 10000)  # median(.0018, .04), not two causes


def test_derived_id_cannot_repair_unconfirmed_causal_root():
    draft = multiclass_fixture()
    original = draft["annotations"][0]
    derived_observation(draft, original, "_child")
    root = next(g for g in draft["groups"] if g["appearance_group_id"] == original["appearance_group_id"])
    root["independence_attestation"] = "pending"
    assert support(api().candidate_eligibility(draft), "unit.speck", "opponent", "train")["counts"]["groups"] == 0
    assert report_class(api().development_scale_report(draft), "unit.speck")["basic_qualified"] is False


def test_frame_then_cause_then_match_medians_have_equal_match_weight():
    draft = multiclass_fixture(("unit.speck", "unit.guard"), own_class_ids=())
    original = draft["annotations"][0]
    original["box"].update(width=0.1, height=0.1)
    # Two units in the same true frame; frame score = median(.01,.03) = .02.
    _, child = derived_observation(draft, original, "_child", width=0.1, height=0.3)
    frame = deepcopy(draft["frames"][0])
    frame.update(raw_pts=12000, timestamp_seconds=11, image_sha256="9" * 64)
    frame["frame_id"] = frame_id(frame["recording_id"], frame["raw_pts"], Fraction(1, 1000))
    draft["frames"].append(frame)
    cov = deepcopy(draft["coverage"][0])
    cov.update(frame_id=frame["frame_id"], coverage_id="later_coverage")
    draft["coverage"].append(cov)
    row = deepcopy(original)
    row.update(frame_id=frame["frame_id"], annotation_id="later_annotation")
    row["box"].update(width=0.1, height=0.4)
    draft["annotations"].append(row)  # cause score = median(.02,.04) = .03
    # A second independent cause in match 1 score .09 -> match median .06.
    group = deepcopy(draft["groups"][0])
    group.update(appearance_group_id="independent", causal_root_id="independent", human_deployment_id="second_event",
                 start_seconds=9, end_seconds=12)
    draft["groups"].append(group)
    row = deepcopy(original)
    row.update(annotation_id="independent_annotation", appearance_group_id="independent", entity_occurrence_id="second_entity")
    row["box"].update(x=0.3, y=0.05, width=0.1, height=0.9)
    draft["annotations"].append(row)
    next(r for r in draft["annotations"] if r["recording_id"] == "recording_2" and r["visual_class_id"] == "unit.speck")["box"].update(width=0.1, height=0.2)
    report = report_class(api().development_scale_report(draft), "unit.speck")
    assert report["score"] == ratio(1, 25)  # class median(.06,.02), not pooled median(.03,.09,.02)
    stats = report["all_reviewed"]["area_norm"]
    assert stats == {"count": 5, "min": ratio(1, 100), "p10": ratio(7, 500), "p50": ratio(3, 100),
                     "p90": ratio(7, 100), "max": ratio(9, 100)}


@pytest.mark.parametrize("form", ["unknown", "evolved"])
def test_non_normal_form_is_retained_not_qualified_or_exported(form):
    draft = selected(multiclass_fixture())
    for group in draft["groups"]:
        if group["visual_class_id"] == "unit.guard":
            group["observed_form"] = form
    for row in draft["annotations"]:
        if row["visual_class_id"] == "unit.guard":
            row["observed_form"] = form
    report = api().multiclass_readiness(draft)
    assert report["ready"] is False
    assert report_class(report["candidate_report"], "unit.guard")["basic_qualified"] is False
    assert all(row["observed_form"] == form for row in draft["annotations"] if row["visual_class_id"] == "unit.guard")


@pytest.mark.parametrize("uncertainty", ["unknown", "neutral", "evolved", "ignore", "interval", "half_review"])
def test_selected_uncertainty_blocks_entire_frame_without_filtering_scale_pool(uncertainty):
    draft = selected(multiclass_fixture())
    original = next(r for r in draft["annotations"] if r["visual_class_id"] == "unit.guard" and r["recording_id"] == "recording_2")
    if uncertainty in ("unknown", "neutral", "evolved"):
        row = deepcopy(original)
        row.update(annotation_id="uncertain_observation", appearance_group_id=None, entity_occurrence_id=None)
        row["box"]["x"] = 0.6
        row["owner"] = uncertainty if uncertainty != "evolved" else "own"
        row["observed_form"] = "evolved" if uncertainty == "evolved" else "normal"
        draft["annotations"].append(row)
    else:
        coverage = next(r for r in draft["coverage"] if r["frame_id"] == original["frame_id"])
        if uncertainty == "ignore":
            coverage["ignore_regions"] = [{"box": {"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.2},
                                            "visual_class_ids": ["unit.guard"], "reason": "Synthetic unresolved unit"}]
        elif uncertainty == "interval":
            coverage["unknown_intervals"] = [{"start_seconds": 19, "end_seconds": 21,
                                             "visual_class_ids": ["unit.guard"], "reason": "Synthetic uncertain moment"}]
        else:
            coverage["reviewed_regions"] = [{"x": 0, "y": 0, "width": 0.5, "height": 1}]
    report = api().multiclass_readiness(draft)
    assert report["scale_report"]["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    assert report["ready"] is False
    assert "missing_export_opponent:unit.guard:development_validation" in report["blocking_reasons"]
    export = next(r for r in report["export_support"] if r["joint_label"] == "unit.guard::opponent")
    assert export["support"][1]["counts"]["boxes"] == 0
    assert api().frame_export_reasons(draft, original["frame_id"])


def test_exact_union_full_frame_review_is_accepted_but_tiny_gap_is_not():
    draft = selected(multiclass_fixture())
    for row in draft["coverage"]:
        row["reviewed_regions"] = [{"x": 0, "y": 0, "width": 0.5, "height": 1},
                                   {"x": 0.5, "y": 0, "width": 0.5, "height": 1}]
    assert api().multiclass_readiness(draft)["ready"] is True
    draft["coverage"][0]["reviewed_regions"][0]["width"] = 0.499999999999
    assert "full_image_review_missing" in api().frame_export_reasons(draft, draft["frames"][0]["frame_id"])


def test_supplied_snapshot_is_recomputed_against_full_unselected_basis():
    draft = multiclass_fixture()
    snapshot = snapshot_for(draft)
    selected(draft)
    draft["selection"]["scale_snapshot_digest"] = snapshot["digest"]
    assert api().multiclass_readiness(draft, snapshot)["ready"] is True
    # Self-consistent outer digest cannot bless fabricated statistics.
    snapshot["payload"]["scale_report"]["cutpoints"]["q25"] = ratio(1, 999)
    snapshot["digest"] = sha256(canonical_bytes({k: v for k, v in snapshot.items() if k != "digest"})).hexdigest()
    draft["selection"]["scale_snapshot_digest"] = snapshot["digest"]
    assert api().multiclass_readiness(draft, snapshot)["status"] == "INVALID_DATASET"


def test_snapshot_rejects_changed_gt_splits_digest_or_closed_shape():
    draft = multiclass_fixture()
    snapshot = snapshot_for(draft)
    selected(draft)
    draft["selection"]["scale_snapshot_digest"] = snapshot["digest"]
    changed = deepcopy(draft)
    changed["annotations"][0]["box"]["width"] = 0.04
    assert api().multiclass_readiness(changed, snapshot)["status"] == "INVALID_DATASET"
    changed = deepcopy(draft)
    for record in changed["recordings"]:
        record["split"] = "development_validation" if record["split"] == "train" else "train"
    for assignment in changed["split_assignment"]:
        assignment["split"] = "development_validation" if assignment["split"] == "train" else "train"
    assert api().multiclass_readiness(changed, snapshot)["status"] == "INVALID_DATASET"
    snapshot["digest"] = "e" * 64
    assert api().multiclass_readiness(draft, snapshot)["status"] == "INVALID_DATASET"
    snapshot["extra"] = "not_a_schema_field"
    assert api().multiclass_readiness(draft, snapshot)["status"] == "INVALID_DATASET"


def test_first_included_recording_only_can_supply_its_declared_groups():
    draft = multiclass_fixture()
    rerun = add_rerecording(draft)
    first = draft["intake"].pop()
    draft["intake"].insert(0, first)
    report = api().candidate_eligibility(draft)
    assert rerun["recording_id"] in report["primary_recording_ids"]
    assert report["qualified_class_ids"] == []  # no guessed cross-recording alignment
    assert support(report, "unit.speck", "opponent", "train")["counts"]["boxes"] == 0


def test_unselected_reference_only_provenance_does_not_block_used_recordings():
    draft = selected(multiclass_fixture())
    draft["provenance"].append({"source_id": "unused_reference", "creator": "synthetic_author", "source_url": None,
                                "artifact_kind": "game_asset", "license_evidence": None, "allowed_scope": "reference_only"})
    assert api().multiclass_readiness(draft)["ready"] is True


def test_confirmed_derived_pending_independence_uses_confirmed_root_not_new_cause():
    draft = multiclass_fixture()
    original = draft["annotations"][0]
    original["review_state"] = "pending"
    draft["frames"][0]["review_state"] = "pending"
    draft["coverage"][0]["exhaustive_state"] = "pending"
    child, row = derived_observation(draft, original, "_child")
    child["independence_attestation"] = "pending"
    row["review_state"] = "verified"
    cell = support(api().candidate_eligibility(draft), "unit.speck", "opponent", "train")
    assert cell["counts"]["groups"] == 1
    assert cell["annotation_ids"] == [row["annotation_id"]]
    root = next(g for g in draft["groups"] if g["appearance_group_id"] == original["appearance_group_id"])
    root["independence_attestation"] = "pending"
    assert support(api().candidate_eligibility(draft), "unit.speck", "opponent", "train")["counts"]["groups"] == 0


def test_excluded_frame_is_not_basic_scale_or_reviewed_statistics_support():
    draft = multiclass_fixture()
    frame = draft["frames"][0]
    frame["review_state"] = "excluded"
    candidate = api().candidate_eligibility(draft)
    assert support(candidate, "unit.speck", "opponent", "train")["counts"]["groups"] == 0
    scale = report_class(api().development_scale_report(draft), "unit.speck")
    assert scale["basic_qualified"] is False
    assert scale["all_reviewed"]["area_norm"]["count"] == 2  # DEV opponent + own only
    assert scale["excluded_reasons"] == [{"reason": "frame_excluded", "count": 2}]


def test_partial_own_joint_subgroup_keeps_real_counts_but_neither_split_is_qualified():
    draft = selected(multiclass_fixture(own_class_ids=("unit.speck", "unit.guard")))
    draft["annotations"] = [r for r in draft["annotations"] if not (
        r["visual_class_id"] == "unit.speck" and r["owner"] == "own" and r["recording_id"] == "recording_2")]
    report = api().multiclass_readiness(draft)
    assert report["ready"] is True  # unit.guard remains the complete own control
    row = next(r for r in report["export_support"] if r["joint_label"] == "unit.speck::own")
    assert row["support"][0]["counts"]["groups"] == 1
    assert row["support"][1]["counts"]["groups"] == 0
    assert all(c["qualification"] == "not_qualified" and c["evaluation"] == "not_evaluated"
               and "own_control_incomplete" in c["reasons"] for c in row["support"])
    assert support(report["candidate_report"], "unit.speck", "own", "train")["qualification"] == "qualified"


def test_selected_medium_large_cannot_substitute_for_full_pool_small_candidate():
    ids = tuple(f"unit.type_{i}" for i in range(5))
    draft = selected(areas(multiclass_fixture(ids), dict(zip(ids, (0.01, 0.02, 0.03, 0.04, 0.05)))), list(ids[2:]))
    report = api().multiclass_readiness(draft)
    assert report["scale_report"]["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    assert report["status"] == "SIZE_COVERAGE_INSUFFICIENT"
    assert "need_selected_relative_small" in report["blocking_reasons"]


def test_rotated_original_image_dimensions_are_the_pixel_statistics_basis():
    draft = multiclass_fixture()
    for record in draft["recordings"]:
        record["rotation_degrees"] = 90
    for frame in draft["frames"]:
        frame["image_width"], frame["image_height"] = 480, 640
    row = report_class(api().development_scale_report(draft), "unit.speck")
    assert row["all_reviewed"]["width_px"]["p50"] == ratio(72, 5)
    assert row["all_reviewed"]["height_px"]["p50"] == ratio(192, 5)
    assert row["all_reviewed"]["area_norm"]["p50"] == ratio(9, 5000)


def test_unknown_interval_includes_actual_terminal_frame_not_background():
    draft = selected(multiclass_fixture())
    frame = draft["frames"][0]
    prior_id = frame["frame_id"]
    frame.update(raw_pts=101000, timestamp_seconds=100)
    frame["frame_id"] = frame_id(frame["recording_id"], frame["raw_pts"], Fraction(1, 1000))
    for row in draft["annotations"]:
        if row["frame_id"] == prior_id:
            row["frame_id"] = frame["frame_id"]
            group = next(g for g in draft["groups"] if g["appearance_group_id"] == row["appearance_group_id"])
            group.update(start_seconds=98, end_seconds=100)
    coverage = draft["coverage"][0]
    coverage["frame_id"] = frame["frame_id"]
    coverage["unknown_intervals"] = [{"start_seconds": 98, "end_seconds": 100,
                                      "visual_class_ids": ["unit.speck"], "reason": "Synthetic unresolved terminal moment"}]
    assert "selected_unknown_interval" in api().frame_export_reasons(draft, frame["frame_id"])


def shared_root_owner_branches():
    """One true cause changes declared view; owner branches are not new causes."""
    draft = multiclass_fixture(own_class_ids=())
    opponent = draft["annotations"][0]
    opponent["box"].update(width=0.1, height=0.1)
    root = next(g for g in draft["groups"] if g["appearance_group_id"] == opponent["appearance_group_id"])
    frame = deepcopy(draft["frames"][0])
    frame.update(raw_pts=12000, timestamp_seconds=11, image_sha256="9" * 64,
                 perspective_ref="synthetic_changed_view", perspective_change_reason="Explicit synthetic view change")
    frame["frame_id"] = frame_id(frame["recording_id"], frame["raw_pts"], Fraction(1, 1000))
    draft["frames"].append(frame)
    coverage = deepcopy(draft["coverage"][0])
    coverage.update(frame_id=frame["frame_id"], coverage_id="owner_branch_coverage")
    draft["coverage"].append(coverage)
    child = deepcopy(root)
    child.update(appearance_group_id="owner_branch", parent_group_id=root["appearance_group_id"],
                 owner="own", origin_kind="transformed", human_deployment_id=None,
                 independence_attestation="pending", start_seconds=11, end_seconds=13)
    draft["groups"].append(child)
    own = deepcopy(opponent)
    own.update(annotation_id="owner_branch_annotation", appearance_group_id="owner_branch",
               owner="own", entity_occurrence_id="owner_branch_entity", frame_id=frame["frame_id"],
               perspective_ref=frame["perspective_ref"])
    own["box"].update(y=0.05, width=0.1, height=0.9)
    draft["annotations"].append(own)
    independent = deepcopy(root)
    independent.update(appearance_group_id="second_cause", causal_root_id="second_cause",
                       human_deployment_id="second_independent_event", start_seconds=9, end_seconds=12)
    draft["groups"].append(independent)
    other = deepcopy(opponent)
    other.update(annotation_id="second_cause_annotation", appearance_group_id="second_cause", entity_occurrence_id="second_entity")
    other["box"].update(x=0.3, width=0.1, height=0.4)
    draft["annotations"].append(other)
    next(r for r in draft["annotations"] if r["visual_class_id"] == "unit.speck" and r["recording_id"] == "recording_2")["box"].update(width=0.1, height=0.2)
    validate_multiclass_shape(draft)
    return draft, own


def test_same_cause_across_owner_branches_has_one_scale_weight():
    draft, own = shared_root_owner_branches()
    report = report_class(api().development_scale_report(draft), "unit.speck")
    # Cause median(.01,.09)=.05; match1 median(.05,.04)=.045;
    # class median(.045,.02)=.0325. Owner-branch pooling yields the wrong .03.
    assert report["score"] == ratio(13, 400)
    assert support(api().candidate_eligibility(draft), "unit.speck", "own", "train")["counts"]["groups"] == 1
    assert any(own["annotation_id"] in r["clean_annotation_ids"] for r in report["support"])


def test_one_clean_owner_branch_prevents_false_root_scale_pending():
    draft, own = shared_root_owner_branches()
    own["occlusion"] = "partial"
    scale = api().development_scale_report(draft)
    row = report_class(scale, "unit.speck")
    assert row["scale_support_pending"] is False
    # Clean root=.01, match1 median(.01,.04)=.025; class median(.025,.02)=.0225.
    assert row["score"] == ratio(9, 400)
    assert scale["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    own_support = next(r for r in row["support"] if r["owner"] == "own")
    assert own_support["score"] is None and own_support["clean_annotation_ids"] == []


def test_nonserializable_unicode_draft_returns_invalid_without_fabricated_hashes():
    draft = selected(multiclass_fixture())
    draft["matches"][0]["notes"] = "\ud800"
    validate_multiclass_shape(draft)  # Valid closed fields, invalid canonical UTF-8.
    report = api().multiclass_readiness(draft)
    assert report == {"status": "INVALID_DATASET", "ready": False,
                      "blocking_reasons": ["invalid_multiclass_shape"], "candidate_report": None,
                      "scale_report": None, "export_support": []}


def test_readiness_does_not_swallow_programmer_error_from_report_builder(monkeypatch):
    def broken_candidate(_draft):
        raise RuntimeError("Synthetic programmer fault")
    monkeypatch.setattr(api(), "candidate_eligibility", broken_candidate)
    with pytest.raises(RuntimeError, match="Synthetic programmer fault"):
        api().multiclass_readiness(multiclass_fixture())
