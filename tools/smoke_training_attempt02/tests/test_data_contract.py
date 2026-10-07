"""Anonymous synthetic contract cases; no footage, model, or training imports."""

from copy import deepcopy
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def api():
    name = "tools.smoke_training_attempt02.data_contract"
    assert importlib.util.find_spec(name) is not None, "Attempt02 contract implementation missing"
    return importlib.import_module(name)


def binding_digest(frame, objects):
    value = {"frame": frame, "objects": sorted(objects, key=lambda item: item["object_id"])}
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


@pytest.fixture
def evidence():
    frame = {"frame_id": "synthetic_frame", "underlying_match_id": "natural_match_01",
             "split": "TRAIN", "image_size": [100, 200], "image_sha256": "a" * 64,
             "positive_object_ids": ["synthetic_object"], "review_state": "confirmed"}
    objects = [{"object_id": "synthetic_object", "frame_id": "synthetic_frame",
                "underlying_match_id": "natural_match_01", "visual_class": "unit.skeleton",
                "class_id": 0, "bbox_xywh_pixels": [10, 50, 8, 16],
                "review_state": "confirmed", "appearance_group_id": "synthetic_group",
                "owner": "opponent", "form": "unknown", "origin_kind": "spawned",
                "source_relationship": "spawned_from:synthetic_witch_group",
                "spawned_from_appearance_group_id": "synthetic_witch_group"}]
    review = {"review_id": "synthetic_human_review", "reviewer": "synthetic reviewer",
              "review_kind": "human", "review_state": "confirmed",
              "frame_id": "synthetic_frame", "image_sha256": "a" * 64,
              "annotation_sha256": binding_digest(frame, objects),
              "selected_classes_exhaustive": ["unit.skeleton", "unit.witch"],
              "material_unknown": False, "negative_confirmed": False,
              "roi_xyxy": [0, 25, 100, 155]}
    return frame, objects, review


@pytest.mark.parametrize(("size", "expected"), [
    ([432, 960], [0, 120, 432, 744]),
    ([1080, 2400], [0, 300, 1080, 1860]),
    ([433, 2003], [0, 250, 433, 1552]),
])
def test_fixed_roi_scales_train_rule_without_dev_adaptation(size, expected):
    assert api().fixed_roi(size) == expected


@pytest.mark.parametrize("size", [[0, 960], [432, -1], [True, 960], [432.0, 960],
                                   [432, 1], [432], [432, 960, 3]])
def test_invalid_or_empty_image_geometry_is_rejected(size):
    with pytest.raises(ValueError):
        api().fixed_roi(size)


def test_roi_translation_retains_extent_and_round_trips_without_clipping():
    module = api()
    assert module.bbox_to_roi([20, 200, 30, 40], [432, 960]) == [20, 80, 30, 40]
    assert module.bbox_from_roi([20, 80, 30, 40], [432, 960]) == [20, 200, 30, 40]
    assert module.bbox_to_roi([0, 120, 432, 624], [432, 960]) == [0, 0, 432, 624]


@pytest.mark.parametrize("box", [[-1, 200, 5, 6], [431, 200, 2, 6], [10, 119, 5, 6],
                                  [10, 740, 5, 5], [10, 200, 0, 5],
                                  [10, 200, 5, float("nan")], [True, 200, 5, 6]])
def test_gt_crossing_roi_or_invalid_geometry_never_silently_clips(box):
    with pytest.raises(ValueError):
        api().bbox_to_roi(box, [432, 960])


def test_restoring_an_invalid_roi_gt_box_is_rejected():
    with pytest.raises(ValueError):
        api().bbox_from_roi([10, 623, 20, 2], [432, 960])


def test_prediction_back_transform_applies_ratio_then_roi_offset():
    result = api().prediction_from_letterbox(
        [800 / 39, 3200 / 39, 2000 / 39, 4800 / 39], [432, 960])
    assert result["bbox_xyxy_original"] == pytest.approx([20, 200, 50, 240])
    assert result["valid_in_roi"] is True
    assert result["invalid_reason"] is None


def test_prediction_entirely_in_resized_roi_can_touch_exact_valid_pixel_edge():
    result = api().prediction_from_letterbox([0, 0, 443, 640], [432, 960])
    assert result["valid_in_roi"] is True
    assert result["bbox_xyxy_original"] == pytest.approx([0, 120, 431.925, 744])


@pytest.mark.parametrize("box", [[440, 50, 450, 60], [445, 50, 455, 60],
                                  [-1, 50, 10, 60], [20, 639, 30, 641]])
def test_padding_and_crossing_predictions_are_retained_invalid_without_clipping(box):
    result = api().prediction_from_letterbox(box, [432, 960])
    assert result["valid_in_roi"] is False
    assert result["invalid_reason"] == "padding_or_roi_boundary"
    expected = [box[0] * 39 / 40, box[1] * 39 / 40 + 120,
                box[2] * 39 / 40, box[3] * 39 / 40 + 120]
    assert result["bbox_xyxy_original"] == pytest.approx(expected)


@pytest.mark.parametrize("box", [[10, 20, 10, 30], [10, 20, 5, 30],
                                  [10, float("inf"), 20, 30], [10, 20, 30]])
def test_malformed_prediction_is_rejected(box):
    with pytest.raises(ValueError):
        api().prediction_from_letterbox(box, [432, 960])


@pytest.mark.parametrize("schema", [{"unit.skeleton": 1, "unit.witch": 0},
                                     {"unit.skeleton": False, "unit.witch": 1},
                                     {"unit.skeleton": 0, "unit.witch": 1, "other": 2}])
def test_swapped_boolean_or_expanded_class_indices_are_rejected(schema):
    with pytest.raises(ValueError):
        api().validate_class_schema(schema)


def test_reviewed_complete_training_frame_qualifies_with_metadata_retained(evidence):
    frame, objects, review = evidence
    original = deepcopy(evidence)
    result = api().qualify_frame(frame, objects, review)
    assert result["training_qualified"] is True
    assert result["qualification_scope"] == "selected_class_supervision_only"
    assert result["roi_xyxy"] == [0, 25, 100, 155]
    assert result["labels"][0]["category_id"] == 0
    assert result["labels"][0]["bbox_xywh_roi"] == [10, 25, 8, 16]
    assert result["labels"][0]["metadata"] == objects[0]
    assert evidence == original


@pytest.mark.parametrize(("field", "value"), [
    ("review_state", "draft"), ("review_state", "pending_human_review"),
    ("review_kind", "automated"), ("reviewer", ""), ("review_id", ""),
    ("material_unknown", True), ("material_unknown", 0),
    ("selected_classes_exhaustive", ["unit.witch"]),
    ("selected_classes_exhaustive", ["unit.skeleton", "unit.witch", "unit.witch"]),
    ("negative_confirmed", "false"), ("frame_id", "another_frame"),
    ("image_sha256", "b" * 64), ("annotation_sha256", "b" * 64),
    ("roi_xyxy", [0, 0, 100, 200]), ("roi_xyxy", None),
    ("selected_classes_exhaustive", [{"unit.skeleton": 0}, "unit.witch"]),
])
def test_unbound_incomplete_unknown_or_automatic_review_cannot_qualify(evidence, field, value):
    frame, objects, review = evidence
    review[field] = value
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


@pytest.mark.parametrize("target", ["frame", "object"])
def test_pending_frame_or_object_cannot_be_promoted_by_an_unrelated_confirmed_review(evidence, target):
    frame, objects, review = evidence
    (frame if target == "frame" else objects[0])["review_state"] = "pending_human_review"
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


@pytest.mark.parametrize(("field", "value"), [("class_id", 1), ("class_id", False),
                                                 ("visual_class", "unknown"),
                                                 ("frame_id", "another_frame"),
                                                 ("underlying_match_id", "natural_match_04"),
                                                 ("bbox_xywh_pixels", [10, 24, 8, 16])])
def test_bound_review_cannot_override_class_source_or_roi_conflicts(evidence, field, value):
    frame, objects, review = evidence
    objects[0][field] = value
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


@pytest.mark.parametrize(("field", "value"), [
    ("owner", "guessed_opponent"), ("form", "guessed_evolved"),
    ("origin_kind", "guessed_direct_card"), ("appearance_group_id", ""),
    ("source_relationship", ""), ("source_relationship", "spawned_from:"),
    ("source_relationship", "unknown"), ("is_skeleton_card_deployment", True),
    ("bbox_xywh_pixels", [10.0, 50, 8, 16]),
])
def test_human_review_cannot_override_invalid_grouping_metadata(evidence, field, value):
    frame, objects, review = evidence
    objects[0][field] = value
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


@pytest.mark.parametrize("field", ["owner", "form", "origin_kind", "appearance_group_id", "source_relationship"])
def test_human_gt_cannot_drop_required_grouping_metadata(evidence, field):
    frame, objects, review = evidence
    del objects[0][field]
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


def test_spawn_relationship_does_not_require_duplicate_source_identity(evidence):
    frame, objects, review = evidence
    del objects[0]["spawned_from_appearance_group_id"]
    review["annotation_sha256"] = binding_digest(frame, objects)
    assert api().qualify_frame(frame, objects, review)["labels"][0]["metadata"]["source_relationship"] == "spawned_from:synthetic_witch_group"


def test_unknown_witch_origin_and_unknown_owner_form_are_retained_without_inference(evidence):
    frame, objects, review = evidence
    objects[0].update(visual_class="unit.witch", class_id=1, owner="unknown",
                      origin_kind="unknown", source_relationship=None,
                      spawned_from_appearance_group_id=None)
    review["annotation_sha256"] = binding_digest(frame, objects)
    result = api().qualify_frame(frame, objects, review)
    assert result["labels"][0]["metadata"]["origin_kind"] == "unknown"
    assert result["labels"][0]["metadata"]["form"] == "unknown"
    assert result["labels"][0]["metadata"]["owner"] == "unknown"


def test_duplicate_or_missing_frame_object_references_are_rejected(evidence):
    frame, objects, review = evidence
    for ids in ([], ["synthetic_object", "synthetic_object"], ["missing_object"]):
        frame["positive_object_ids"] = ids
        review["annotation_sha256"] = binding_digest(frame, objects)
        with pytest.raises(ValueError):
            api().qualify_frame(frame, objects, review)


def test_dev_tune_frame_cannot_enter_training_even_with_confirmed_gt(evidence):
    frame, objects, review = evidence
    frame.update(underlying_match_id="natural_match_04", split="DEV_TUNE")
    objects[0]["underlying_match_id"] = "natural_match_04"
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)
    result = api().qualify_frame(frame, objects, review, purpose="DEV_TUNE")
    assert result["training_qualified"] is False
    assert result["purpose"] == "DEV_TUNE"


def test_relabeling_underlying_dev_match_as_train_is_rejected(evidence):
    frame, objects, review = evidence
    frame["underlying_match_id"] = "natural_match_04"
    objects[0]["underlying_match_id"] = "natural_match_04"
    review["annotation_sha256"] = binding_digest(frame, objects)
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


def test_zero_gt_requires_explicit_reviewed_negative_confirmation(evidence):
    frame, _, review = evidence
    frame["positive_object_ids"] = []
    review["annotation_sha256"] = binding_digest(frame, [])
    with pytest.raises(ValueError):
        api().qualify_frame(frame, [], review)
    review["negative_confirmed"] = True
    result = api().qualify_frame(frame, [], review)
    assert result["labels"] == []
    assert result["negative_confirmed"] is True


def test_positive_boxes_cannot_be_called_a_negative_frame(evidence):
    frame, objects, review = evidence
    review["negative_confirmed"] = True
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects, review)


def test_annotation_digest_is_order_stable_and_binds_every_annotation_field(evidence):
    frame, objects, _ = evidence
    module = api()
    assert module.annotation_digest(frame, objects) == binding_digest(frame, objects)
    second = deepcopy(objects[0]); second["object_id"] = "second_object"
    assert module.annotation_digest(frame, objects + [second]) == module.annotation_digest(frame, [second] + objects)
    before = module.annotation_digest(frame, objects)
    objects[0]["owner"] = "unknown"
    assert module.annotation_digest(frame, objects) != before


def test_human_confirmation_relayed_from_chatgpt_is_an_explicit_supported_review(evidence):
    frame, objects, review = evidence
    review["review_kind"] = "human_relayed_chatgpt"
    assert api().qualify_frame(frame, objects, review)["training_qualified"] is True


def test_duplicate_objects_cannot_reuse_one_identity_and_review_binding(evidence):
    frame, objects, review = evidence
    with pytest.raises(ValueError):
        api().qualify_frame(frame, objects + deepcopy(objects), review)


def test_nonfinite_semantics_cannot_be_hashed_into_review_evidence(evidence):
    frame, objects, _ = evidence
    objects[0]["confidence"] = float("nan")
    with pytest.raises(ValueError):
        api().annotation_digest(frame, objects)


def test_many_boxes_frames_or_appearance_groups_do_not_multiply_one_confirmed_deployment():
    group = {"appearance_group_id": "synthetic_witch_1", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.witch", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "direct_card", "spawned_from_appearance_group_id": None}
    repeated = dict(group, appearance_group_id="synthetic_witch_2", frame_count=30, bbox_count=90)
    spawned = dict(group, appearance_group_id="synthetic_skeleton", visual_class="unit.skeleton",
                   independent_deployment_confirmed=False, deployment_id=None,
                   origin_kind="spawned", spawned_from_appearance_group_id="synthetic_witch_1")
    assert api().count_confirmed_deployments([group, repeated, spawned]) == {"unit.skeleton": 0, "unit.witch": 1}


@pytest.mark.parametrize("change", [{"review_state": "pending_human_review"},
                                      {"deployment_id": None}, {"origin_kind": "spawned"},
                                      {"spawned_from_appearance_group_id": "synthetic_parent"}])
def test_unsupported_independent_deployment_claim_is_rejected(change):
    group = {"appearance_group_id": "synthetic_group", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.skeleton", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "direct_card", "spawned_from_appearance_group_id": None}
    group.update(change)
    with pytest.raises(ValueError):
        api().count_confirmed_deployments([group])


def test_one_confirmed_deployment_cannot_be_counted_as_two_visual_classes():
    group = {"appearance_group_id": "synthetic_witch", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.witch", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "direct_card", "spawned_from_appearance_group_id": None}
    conflict = dict(group, appearance_group_id="synthetic_skeleton", visual_class="unit.skeleton")
    with pytest.raises(ValueError):
        api().count_confirmed_deployments([group, conflict])


def test_explicit_independent_witch_review_does_not_invent_direct_card_origin():
    group = {"appearance_group_id": "synthetic_witch", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.witch", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "unknown", "spawned_from_appearance_group_id": None}
    assert api().count_confirmed_deployments([group]) == {"unit.skeleton": 0, "unit.witch": 1}
    assert group["origin_kind"] == "unknown"


def test_one_appearance_group_cannot_claim_two_deployment_identities():
    group = {"appearance_group_id": "synthetic_witch", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.witch", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "unknown", "spawned_from_appearance_group_id": None}
    with pytest.raises(ValueError):
        api().count_confirmed_deployments([group, dict(group, deployment_id="another_play")])


def test_spawned_from_relationship_cannot_be_counted_as_an_independent_witch():
    group = {"appearance_group_id": "synthetic_witch", "underlying_match_id": "natural_match_01",
             "visual_class": "unit.witch", "review_state": "confirmed",
             "independent_deployment_confirmed": True, "deployment_id": "synthetic_play",
             "origin_kind": "unknown", "source_relationship": "spawned_from:synthetic_parent"}
    with pytest.raises(ValueError):
        api().count_confirmed_deployments([group])
