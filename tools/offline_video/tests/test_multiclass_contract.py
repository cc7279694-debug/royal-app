"""Real boundary validation of synthetic declarations; no mocks or private data."""
from copy import deepcopy
from fractions import Fraction
from importlib import import_module

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.evidence_prepare import frame_id
from multiclass_fixtures import add_rerecording, multiclass_fixture


def api(name):
    try:
        module = import_module("clash_tracker_video.multiclass_contract")
    except ModuleNotFoundError as exc:
        if exc.name == "clash_tracker_video.multiclass_contract":
            pytest.fail("Multiclass contract interface is not implemented")
        raise
    return getattr(module, name)


def validate(draft):
    return api("validate_multiclass_shape")(draft)


def test_extensible_multiclass_draft_is_valid_without_selection_and_is_not_mutated():
    draft = multiclass_fixture(("unit.custom_small", "unit.custom_large", "building.custom"))
    before = deepcopy(draft)
    assert validate(draft) is None
    assert draft == before


def test_same_match_rerecording_cannot_cross_splits():
    draft = multiclass_fixture()
    record = add_rerecording(draft)
    record["split"] = "development_validation"
    with pytest.raises(EvidenceError):
        api("validate_match_splits")(draft)


def test_same_match_rerecording_can_keep_original_split():
    draft = multiclass_fixture()
    add_rerecording(draft)
    assert validate(draft) is None


@pytest.mark.parametrize("field,value", [("score", 0.9), ("model_id", "fake_model")])
def test_gt_rejects_prediction_fields(field, value):
    draft = multiclass_fixture()
    draft["annotations"][0][field] = value
    with pytest.raises(EvidenceError):
        validate(draft)


def test_unknown_form_does_not_become_normal():
    draft = multiclass_fixture()
    draft["annotations"][0]["observed_form"] = "unknown"
    draft["groups"][0]["observed_form"] = "unknown"
    assert validate(draft) is None
    assert draft["annotations"][0]["observed_form"] == "unknown"


def test_unknown_owner_and_cause_remain_unconfirmed():
    draft = multiclass_fixture()
    group = draft["groups"][0]
    group.update(owner="unknown", origin_kind="unknown", human_deployment_id=None,
                 independence_attestation="pending", verification_state="ambiguous")
    draft["annotations"][0]["owner"] = "unknown"
    assert validate(draft) is None
    assert group["owner"] == "unknown"


def test_user_confirmed_bounds_without_result_ui():
    draft = multiclass_fixture()
    assert validate(draft) is None
    assert draft["recordings"][0]["terminal_result_screen_present"] is False


@pytest.mark.parametrize("field,value", [("start_seconds", 1), ("end_seconds", 99)])
def test_user_confirmed_match_cannot_shorten_actual_file_boundary(field, value):
    draft = multiclass_fixture()
    draft["recordings"][0]["match_segment"][field] = value
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("field,value", [("x", -0.1), ("width", -0.1), ("width", 0),
                                        ("x", 0.99), ("height", float("nan")), ("y", True)])
def test_invalid_original_normalized_box_is_rejected(field, value):
    draft = multiclass_fixture()
    draft["annotations"][0]["box"][field] = value
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("collection,field,value", [
    ("recordings", "width", True), ("frames", "raw_pts", True),
    ("recordings", "last_frame_seconds", float("inf")),
    ("annotations", "owner", "enemy"), ("groups", "origin_kind", "guessed"),
])
def test_strict_scalar_and_enum_values(collection, field, value):
    draft = multiclass_fixture()
    draft[collection][0][field] = value
    with pytest.raises(EvidenceError):
        validate(draft)


def test_invalid_taxonomy_mobility_is_rejected():
    draft = multiclass_fixture()
    draft["taxonomy"]["classes"][0]["mobility"] = "fast"
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("target", ["root", "taxonomy", "class", "recording", "segment", "origin",
                                  "group", "frame", "coverage", "review", "provenance", "source"])
def test_nested_objects_are_closed(target):
    draft = multiclass_fixture()
    rows = {"root": draft, "taxonomy": draft["taxonomy"], "class": draft["taxonomy"]["classes"][0],
            "recording": draft["recordings"][0], "segment": draft["recordings"][0]["match_segment"],
            "origin": draft["frames"][0]["origin"], "group": draft["groups"][0],
            "frame": draft["frames"][0], "coverage": draft["coverage"][0],
            "review": draft["annotations"][0]["review_provenance"], "provenance": draft["provenance"][0],
            "source": draft["annotation_sources"][0]}
    rows[target]["extra_prediction"] = "forbidden"
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("collection,field", [("annotations", "visual_stage"),
                                             ("groups", "parent_group_id"),
                                             ("provenance", "source_url")])
def test_nullable_fields_are_required_not_silently_defaulted(collection, field):
    draft = multiclass_fixture()
    del draft[collection][0][field]
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("collection,key", [("annotations", "annotation_id"), ("groups", "appearance_group_id"),
                                            ("frames", "frame_id"), ("matches", "underlying_match_id")])
def test_duplicate_ids_are_rejected(collection, key):
    draft = multiclass_fixture()
    draft[collection].append(deepcopy(draft[collection][0]))
    with pytest.raises(EvidenceError):
        validate(draft)


def test_renamed_actual_pts_frame_is_rejected():
    draft = multiclass_fixture()
    frame = deepcopy(draft["frames"][0])
    frame["frame_id"] = "renamed_same_frame"
    draft["frames"].append(frame)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_same_frame_entity_cannot_get_two_gt_rows():
    draft = multiclass_fixture()
    anno = deepcopy(draft["annotations"][0])
    anno["annotation_id"] = "new_annotation_same_entity"
    anno["box"]["x"] = 0.2
    draft["annotations"].append(anno)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_same_box_cannot_be_renamed_into_another_entity():
    draft = multiclass_fixture()
    anno = deepcopy(draft["annotations"][0])
    anno.update(annotation_id="renamed_anno", entity_occurrence_id="renamed_entity")
    draft["annotations"].append(anno)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_same_confirmed_cause_cannot_get_new_root_id():
    draft = multiclass_fixture()
    group = deepcopy(draft["groups"][0])
    group.update(appearance_group_id="new_group", causal_root_id="new_group")
    draft["groups"].append(group)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_renaming_both_group_and_human_event_cannot_duplicate_declared_appearance():
    draft = multiclass_fixture()
    group = deepcopy(draft["groups"][0])
    group.update(appearance_group_id="new_group", causal_root_id="new_group", human_deployment_id="new_event")
    draft["groups"].append(group)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_parent_cycle_is_rejected():
    draft = multiclass_fixture()
    left, right = draft["groups"][:2]
    left["parent_group_id"] = right["appearance_group_id"]
    right["parent_group_id"] = left["appearance_group_id"]
    left["origin_kind"] = right["origin_kind"] = "transformed"
    with pytest.raises(EvidenceError):
        validate(draft)


def test_derived_group_keeps_same_match_and_causal_root():
    draft = multiclass_fixture()
    root = draft["groups"][0]
    child = deepcopy(root)
    child.update(appearance_group_id="summoned_child", parent_group_id=root["appearance_group_id"],
                 origin_kind="summoned", human_deployment_id=None, independence_attestation="pending",
                 start_seconds=11, end_seconds=12)
    draft["groups"].append(child)
    assert validate(draft) is None
    child["causal_root_id"] = child["appearance_group_id"]
    with pytest.raises(EvidenceError):
        validate(draft)


def test_known_entity_cannot_move_to_an_unrelated_causal_group():
    draft = multiclass_fixture()
    anno = deepcopy(draft["annotations"][0])
    anno.update(annotation_id="second_frame_entity", frame_id=draft["frames"][1]["frame_id"],
                appearance_group_id=draft["groups"][2]["appearance_group_id"],
                visual_class_id=draft["groups"][2]["visual_class_id"])
    draft["annotations"].append(anno)
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("collection,field,value", [
    ("recordings", "underlying_match_id", "missing_match"),
    ("annotations", "frame_id", "missing_frame"),
    ("annotations", "appearance_group_id", "missing_group"),
    ("annotations", "annotation_source_id", "missing_source"),
    ("coverage", "frame_id", "missing_frame"),
    ("groups", "causal_root_id", "missing_root"),
])
def test_dangling_references_are_rejected(collection, field, value):
    draft = multiclass_fixture()
    draft[collection][0][field] = value
    with pytest.raises(EvidenceError):
        validate(draft)


def test_same_source_bytes_cannot_claim_two_matches():
    draft = multiclass_fixture()
    draft["recordings"][1]["source_sha256"] = draft["recordings"][0]["source_sha256"]
    with pytest.raises(EvidenceError):
        validate(draft)


def test_prospective_test_identity_is_retained_but_not_included_for_development():
    draft = multiclass_fixture()
    draft["recordings"][0]["split"] = draft["split_assignment"][0]["split"] = "prospective_test"
    with pytest.raises(EvidenceError):
        validate(draft)
    draft["intake"][0]["status"] = "pending"
    assert validate(draft) is None
    assert draft["split_assignment"][0]["split"] == "prospective_test"


def test_nullable_source_card_supports_many_to_many_mapping():
    draft = multiclass_fixture()
    for anno in draft["annotations"]:
        anno.update(source_card_id="card.synthetic_shared", source_card_candidates=["card.synthetic_shared"],
                    mapping_basis="manual", mapping_verification="verified")
    assert validate(draft) is None
    draft["annotations"][0].update(source_card_id=None,
                                    source_card_candidates=["card.synthetic_shared", "card.synthetic_other"],
                                    mapping_verification="pending")
    assert validate(draft) is None


def test_joint_label_maps_are_stable_with_distinct_background_offsets():
    assert api("backend_label_maps")(["unit.z", "unit.a"]) == {
        "yolox": {"unit.a::opponent": 0, "unit.a::own": 1, "unit.z::opponent": 2, "unit.z::own": 3},
        "torchvision": {"unit.a::opponent": 1, "unit.a::own": 2, "unit.z::opponent": 3, "unit.z::own": 4},
    }


@pytest.mark.parametrize("ids", [["bad::class"], ["unit.a", "unit.a"], [True], "unit.a", []])
def test_joint_label_map_rejects_ambiguous_or_empty_classes(ids):
    with pytest.raises(EvidenceError):
        api("backend_label_maps")(ids)


def selected_draft():
    draft = multiclass_fixture()
    ids = [row["visual_class_id"] for row in draft["taxonomy"]["classes"]]
    draft["selection"] = {"selected_class_ids": ids,
                          "class_decisions": [{"visual_class_id": cid, "selected": True,
                                               "reason": "Synthetic selected representative"} for cid in ids],
                          "scale_snapshot_digest": "d" * 64, "policy_id": "dev_moving_area_quantiles_v1"}
    draft["backend_label_maps"] = api("backend_label_maps")(ids)
    return draft


def test_selected_draft_requires_consistent_locked_maps_and_complete_decisions():
    draft = selected_draft()
    assert validate(draft) is None
    draft["backend_label_maps"]["torchvision"]["unit.speck::opponent"] = 0
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("mutation", ["no_selection", "missing_map", "unknown_class", "wrong_decision",
                                     "missing_decision", "extra_selection_field"])
def test_selection_and_maps_cannot_disagree(mutation):
    draft = selected_draft()
    if mutation == "no_selection": draft["selection"] = None
    if mutation == "missing_map": draft["backend_label_maps"] = {}
    if mutation == "unknown_class": draft["selection"]["selected_class_ids"].append("unit.missing")
    if mutation == "wrong_decision": draft["selection"]["class_decisions"][0]["selected"] = False
    if mutation == "missing_decision": draft["selection"]["class_decisions"].pop()
    if mutation == "extra_selection_field": draft["selection"]["score"] = 0.9
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("change", ["pts", "origin", "dimensions", "perspective"])
def test_actual_pts_original_dimensions_and_owner_perspective_are_bound(change):
    draft = multiclass_fixture()
    if change == "pts": draft["frames"][0]["timestamp_seconds"] += 1
    if change == "origin": draft["frames"][0]["origin"]["raw_pts"] += 1
    if change == "dimensions": draft["frames"][0]["image_width"] = 320
    if change == "perspective": draft["annotations"][0]["perspective_ref"] = "guessed_view"
    with pytest.raises(EvidenceError):
        validate(draft)


def test_pending_undecodable_recording_can_retain_explicit_null_metadata():
    draft = multiclass_fixture()
    rid = "recording_1"
    draft["intake"][0]["status"] = "pending"
    record = draft["recordings"][0]
    for key in ("width", "height", "rotation_degrees", "time_base", "origin_pts",
                "origin_time_base", "last_frame_seconds", "match_segment"):
        record[key] = None
    record.update(technical_valid=False, complete_recording=False, full_human_review=False,
                  completion_attestation="pending", exports=[])
    for name in ("groups", "frames", "annotations", "coverage"):
        draft[name] = [row for row in draft[name] if row["recording_id"] != rid]
    assert validate(draft) is None


def test_exhaustive_class_coverage_cannot_silently_disappear():
    draft = multiclass_fixture()
    draft["coverage"].pop(0)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_dangling_ancestor_raises_evidence_error_not_internal_lookup_error():
    draft = multiclass_fixture()
    root = draft["groups"][0]
    for gid, parent in (("first_child", "second_child"), ("second_child", "missing_ancestor")):
        child = deepcopy(root)
        child.update(appearance_group_id=gid, parent_group_id=parent, origin_kind="summoned",
                     human_deployment_id=None, independence_attestation="pending")
        draft["groups"].append(child)
    with pytest.raises(EvidenceError):
        validate(draft)


def test_prospective_parent_cycle_with_actual_root_is_rejected():
    draft = multiclass_fixture()
    root = draft["groups"][0]
    for gid, parent in (("first_child", "second_child"), ("second_child", "first_child")):
        child = deepcopy(root)
        child.update(appearance_group_id=gid, parent_group_id=parent, origin_kind="summoned",
                     human_deployment_id=None, independence_attestation="pending")
        draft["groups"].append(child)
    with pytest.raises(EvidenceError):
        validate(draft)


@pytest.mark.parametrize("mutation", ["schema_bool", "rational_bool", "alias_missing_class",
                                     "alias_duplicate", "group_other_match", "unknown_coverage_class",
                                     "invalid_unknown_interval", "invalid_ignore_region", "absolute_path",
                                     "path_traversal", "unreviewed_confirmed"])
def test_declared_nested_metadata_cannot_escape_validation(mutation):
    draft = multiclass_fixture()
    if mutation == "schema_bool": draft["schema_version"] = True
    if mutation == "rational_bool": draft["frames"][0]["time_base"]["numerator"] = True
    if mutation == "alias_missing_class":
        draft["taxonomy"]["alias_mapping"] = [{"alias": "alias", "visual_class_id": "missing"}]
    if mutation == "alias_duplicate":
        draft["taxonomy"]["alias_mapping"] = [{"alias": "alias", "visual_class_id": "unit.speck"}] * 2
    if mutation == "group_other_match": draft["groups"][0]["underlying_match_id"] = "match_2"
    if mutation == "unknown_coverage_class": draft["coverage"][0]["exhaustive_for_classes"].append("missing")
    if mutation == "invalid_unknown_interval":
        draft["coverage"][0]["unknown_intervals"] = [{"start_seconds": 0, "end_seconds": 101,
                                                     "visual_class_ids": ["unit.speck"], "reason": "unknown"}]
    if mutation == "invalid_ignore_region":
        draft["coverage"][0]["ignore_regions"] = [{"box": {"x": 0, "y": 0, "width": 2, "height": 1},
                                                  "visual_class_ids": ["unit.speck"], "reason": "occluded"}]
    if mutation == "absolute_path": draft["recordings"][0]["source_path"] = "C:/private/source.mp4"
    if mutation == "path_traversal": draft["annotation_sources"][0]["path"] = "synthetic/../labels.json"
    if mutation == "unreviewed_confirmed": draft["groups"][0]["review_provenance"]["reviewed_by"] = None
    with pytest.raises(EvidenceError):
        validate(draft)


def test_pending_draft_with_empty_inventory_is_valid_but_makes_no_readiness_claim():
    draft = multiclass_fixture()
    for name in ("intake", "matches", "recordings", "groups", "frames", "annotations", "coverage", "split_assignment"):
        draft[name] = []
    assert validate(draft) is None


def rounded_final_frame_draft():
    draft = multiclass_fixture()
    record, frame = draft["recordings"][0], draft["frames"][0]
    old_fid, rid = frame["frame_id"], record["recording_id"]
    record.update(time_base={"numerator": 1, "denominator": 3}, origin_pts=3,
                  origin_time_base={"numerator": 1, "denominator": 3}, last_frame_seconds=1 / 3)
    record["match_segment"]["end_seconds"] = 1 / 3
    frame.update(frame_id=frame_id(rid, 4, Fraction(1, 3)), raw_pts=4,
                 time_base={"numerator": 1, "denominator": 3}, timestamp_seconds=1 / 3,
                 origin={"raw_pts": 3, "time_base": {"numerator": 1, "denominator": 3}})
    draft["groups"] = [row for row in draft["groups"] if row["recording_id"] != rid]
    for name in ("frames", "annotations", "coverage"):
        draft[name] = [row for row in draft[name] if row["recording_id"] != rid
                       or row["frame_id"] == old_fid or row is frame]
        for row in draft[name]:
            if row["recording_id"] == rid:
                row["frame_id"] = frame["frame_id"]
                if name == "annotations":
                    row["appearance_group_id"] = None
    return draft


def test_rounded_actual_final_pts_is_inside_its_declared_float_file_boundary():
    assert validate(rounded_final_frame_draft()) is None


def test_actual_frame_after_rounded_final_boundary_is_rejected():
    draft = rounded_final_frame_draft()
    frame = draft["frames"][0]
    new_fid = frame_id(frame["recording_id"], 5, Fraction(1, 3))
    frame.update(frame_id=new_fid, raw_pts=5, timestamp_seconds=2 / 3)
    for name in ("annotations", "coverage"):
        for row in draft[name]:
            if row["recording_id"] == frame["recording_id"]:
                row["frame_id"] = new_fid
    with pytest.raises(EvidenceError):
        validate(draft)


def final_frame_with_group_draft(*, integer_boundary=False):
    """Bind visible synthetic entities to groups ending at the actual last frame."""
    draft = rounded_final_frame_draft()
    record, frame = draft["recordings"][0], draft["frames"][0]
    if integer_boundary:
        old_fid = frame["frame_id"]
        frame.update(raw_pts=33, timestamp_seconds=10,
                     frame_id=frame_id(record["recording_id"], 33, Fraction(1, 3)))
        frame["image_path"] = frame["image_path"].replace(old_fid, frame["frame_id"])
        record["last_frame_seconds"] = record["match_segment"]["end_seconds"] = 10
        for name in ("annotations", "coverage"):
            for row in draft[name]:
                if row["recording_id"] == record["recording_id"]:
                    row["frame_id"] = frame["frame_id"]
    for group in multiclass_fixture()["groups"][:2]:
        group.update(start_seconds=0, end_seconds=record["last_frame_seconds"])
        draft["groups"].append(group)
        for annotation in draft["annotations"]:
            if annotation["recording_id"] == record["recording_id"] and annotation["owner"] == group["owner"]:
                annotation["appearance_group_id"] = group["appearance_group_id"]
    return draft


@pytest.mark.parametrize("integer_boundary", [True, False], ids=["integer_final_pts", "one_third_final_pts"])
def test_actual_final_frame_can_remain_associated_with_visible_group(integer_boundary):
    assert validate(final_frame_with_group_draft(integer_boundary=integer_boundary)) is None


@pytest.mark.parametrize("integer_boundary", [True, False], ids=["integer_regular_end", "one_third_regular_end"])
def test_group_ordinary_end_remains_exclusive(integer_boundary):
    draft = final_frame_with_group_draft(integer_boundary=integer_boundary)
    record = draft["recordings"][0]
    record["last_frame_seconds"] = record["match_segment"]["end_seconds"] = 100
    with pytest.raises(EvidenceError):
        validate(draft)


def test_rounded_timestamp_cannot_fake_actual_terminal_group_boundary():
    draft = final_frame_with_group_draft()
    frame = draft["frames"][0]
    old_fid = frame["frame_id"]
    frame.update(raw_pts=3_999_999, time_base={"numerator": 1, "denominator": 3_000_000},
                 frame_id=frame_id(frame["recording_id"], 3_999_999, Fraction(1, 3_000_000)))
    frame["image_path"] = frame["image_path"].replace(old_fid, frame["frame_id"])
    for name in ("annotations", "coverage"):
        for row in draft[name]:
            if row["recording_id"] == frame["recording_id"]:
                row["frame_id"] = frame["frame_id"]
    for group in draft["groups"]:
        if group["recording_id"] == frame["recording_id"]:
            group["start_seconds"] = 0.3333332
    with pytest.raises(EvidenceError):
        validate(draft)


def test_invalid_readiness_allows_null_reports_but_noninvalid_requires_reports():
    from clash_tracker_video.multiclass_contract import ReadinessReport, _validate_types
    report = {"status": "INVALID_DATASET", "ready": False, "blocking_reasons": ["invalid_multiclass_shape"],
              "candidate_report": None, "scale_report": None, "export_support": []}
    _validate_types(report, ReadinessReport)
    report["status"] = "DATA_INSUFFICIENT"
    with pytest.raises(EvidenceError):
        _validate_types(report, ReadinessReport)
