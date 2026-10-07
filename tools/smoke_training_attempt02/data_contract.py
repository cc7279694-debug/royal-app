"""Pure Attempt02 geometry and human-review gates; no model or file I/O.

The fixed ROI rule was selected from TRAIN geometry, before DEV_TUNE inspection.
Only a bound, explicit human confirmation can qualify selected-class background.
Digests detect semantic changes; they do not authenticate a human or verify pixels.
This helper does not authorize a run, create a lock, or emit game events.
"""

from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
import json
import math

CLASS_SCHEMA = {"unit.skeleton": 0, "unit.witch": 1}
MATCH_SPLITS = {"natural_match_01": "TRAIN", "natural_match_04": "DEV_TUNE"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value)


def _vector(value, length):
    _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes))
             and len(value) == length, f"Expected {length} numeric coordinates")
    _require(all(type(item) in (int, float) and math.isfinite(item) for item in value),
             "Coordinates must be finite numbers, not booleans")
    return list(value)


def fixed_roi(image_size):
    """Return exclusive pixel bounds [0, floor(h/8), width, floor(31*h/40)].

    Image dimensions are [width, height]. Integer arithmetic avoids boundary
    drift: a 432x960 source always yields [0, 120, 432, 744]. The full width
    conservatively retains both playable lanes while excluding top/bottom UI.
    """
    _require(isinstance(image_size, Sequence) and len(image_size) == 2,
             "Image size must contain width and height")
    width, height = image_size
    _require(type(width) is int and type(height) is int and width > 0 and height > 0,
             "Image dimensions must be positive integers")
    top, bottom = height // 8, height * 31 // 40
    _require(bottom > top, "Fixed ROI is empty")
    return [0, top, width, bottom]


def _xywh_in_bounds(bbox, width, height):
    x, y, box_width, box_height = _vector(bbox, 4)
    _require(x >= 0 and y >= 0 and box_width > 0 and box_height > 0
             and x + box_width <= width and y + box_height <= height,
             "BBox must be wholly inside bounds; clipping is forbidden")
    return [x, y, box_width, box_height]


def bbox_to_roi(bbox_xywh, image_size):
    """Translate an original-image xywh GT box; reject crossing, never clip."""
    left, top, right, bottom = fixed_roi(image_size)
    x, y, width, height = _xywh_in_bounds(bbox_xywh, *image_size)
    return _xywh_in_bounds([x - left, y - top, width, height], right - left, bottom - top)


def bbox_from_roi(bbox_xywh, image_size):
    """Restore a wholly contained ROI xywh GT box to the original image."""
    left, top, right, bottom = fixed_roi(image_size)
    x, y, width, height = _xywh_in_bounds(bbox_xywh, right - left, bottom - top)
    return [x + left, y + top, width, height]


def prediction_from_letterbox(bbox_xyxy, image_size, input_size=640):
    """Restore YOLOX top-left letterbox coordinates without clipping.

    The crop is scaled by input_size/max(ROI width, ROI height). Integer resize
    bounds match the existing top-left letterbox convention, so even predictions
    only partly in its padding remain invalid. Invalid boxes are retained for
    audit and must be excluded from ordinary ROI box metrics.
    """
    _require(type(input_size) is int and input_size > 0, "Input size must be a positive integer")
    left, top, right, bottom = fixed_roi(image_size)
    x1, y1, x2, y2 = _vector(bbox_xyxy, 4)
    _require(x2 > x1 and y2 > y1, "Prediction extent must be positive")
    width, height = right - left, bottom - top
    ratio = input_size / max(width, height)
    resized_width, resized_height = int(width * ratio), int(height * ratio)
    _require(resized_width > 0 and resized_height > 0, "Resized ROI is empty")
    original = [x1 / ratio + left, y1 / ratio + top, x2 / ratio + left, y2 / ratio + top]
    valid = 0 <= x1 < x2 <= resized_width and 0 <= y1 < y2 <= resized_height
    return {"bbox_xyxy_original": original, "valid_in_roi": valid,
            "invalid_reason": None if valid else "padding_or_roi_boundary",
            "roi_xyxy": [left, top, right, bottom], "resize_ratio": ratio,
            "resized_roi_size": [resized_width, resized_height]}


def validate_class_schema(schema):
    """Reject swaps, implicit boolean indices, additional or missing classes."""
    expected = {"unit.skeleton": 0, "unit.witch": 1}
    _require(isinstance(schema, Mapping) and set(schema) == set(expected)
             and all(type(schema[name]) is int and schema[name] == index
                     for name, index in expected.items()), "Attempt02 class schema differs")


def annotation_digest(frame, objects):
    """Bind the complete frame and complete objects, independent of object order.

    Hash the original annotations before geometry conversion. Review metadata
    belongs in the separate human return, avoiding a self-referential digest.
    """
    _require(isinstance(frame, Mapping) and isinstance(objects, Sequence), "Invalid annotations")
    _require(all(isinstance(item, Mapping) and _text(item.get("object_id")) for item in objects),
             "Every object needs an explicit identity")
    _require(len({item["object_id"] for item in objects}) == len(objects), "Duplicate object identity")
    value = {"frame": dict(frame), "objects": sorted(objects, key=lambda item: item["object_id"])}
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError("Annotations must be finite JSON data") from error
    return sha256(encoded).hexdigest()


def qualify_frame(frame, objects, review, purpose="TRAIN", class_schema=None):
    """Qualify one original frame against a separate exact human review binding.

    Required frame fields: frame_id, underlying_match_id, split, image_size,
    image_sha256, positive_object_ids and review_state='confirmed'. Every object
    binds object_id/frame_id/underlying_match_id, visual_class, integer class_id,
    integer original bbox_xywh_pixels and review_state='confirmed'. Metadata must
    include appearance_group_id, owner (opponent/own/unknown), form
    (normal/evolved/unknown), and origin_kind (direct_card/spawned/unknown).
    Spawned Skeleton requires source_relationship='spawned_from:<group_id>' and
    cannot claim a Skeleton card deployment. A duplicate source ID is optional.
    All metadata is preserved verbatim; an unknown Witch origin stays unknown.

    Required review fields: review_id, reviewer, review_kind ('human' or
    'human_relayed_chatgpt'), review_state='confirmed', frame_id, image_sha256,
    annotation_sha256, selected_classes_exhaustive, material_unknown=False and
    roi_xyxy matching the fixed rule, and boolean negative_confirmed. Zero GT
    requires negative_confirmed=True.
    Exhaustiveness applies only to these two visual classes in the fixed ROI;
    it never certifies a whole-match absence or false-positive time denominator.

    TRAIN accepts only natural_match_01; DEV_TUNE accepts only natural_match_04
    and never returns training_qualified=True. Here training_qualified means
    only selected-class supervision qualification; it is not provenance,
    Training Dataset Lock readiness, rights clearance, or permission to train.
    A draft or partial frame cannot pass this standard full-ROI supervision gate.
    """
    validate_class_schema(CLASS_SCHEMA if class_schema is None else class_schema)
    _require(isinstance(frame, Mapping) and isinstance(review, Mapping), "Frame/review must be objects")
    _require(purpose in ("TRAIN", "DEV_TUNE"), "Unsupported supervision purpose")
    _require(_text(frame.get("frame_id")) and _sha(frame.get("image_sha256")), "Invalid frame binding")
    expected_split = MATCH_SPLITS.get(frame.get("underlying_match_id"))
    _require(expected_split is not None and frame.get("split") == expected_split == purpose,
             "Underlying match cannot cross Attempt02 split or training purpose")
    _require(frame.get("review_state") == "confirmed", "Draft/pending frame cannot qualify")
    roi = fixed_roi(frame.get("image_size"))
    digest = annotation_digest(frame, objects)
    _require(review.get("review_state") == "confirmed"
             and review.get("review_kind") in ("human", "human_relayed_chatgpt")
             and _text(review.get("review_id")) and _text(review.get("reviewer")),
             "Explicit attributed human confirmation is required")
    _require(review.get("frame_id") == frame["frame_id"]
             and review.get("image_sha256") == frame["image_sha256"]
             and review.get("annotation_sha256") == digest, "Human review is not bound to these exact annotations")
    _require(_vector(review.get("roi_xyxy"), 4) == roi, "Human review ROI differs from the fixed rule")
    classes = review.get("selected_classes_exhaustive")
    _require(isinstance(classes, list) and len(classes) == 2
             and all(_text(item) for item in classes) and set(classes) == set(CLASS_SCHEMA),
             "Both selected classes require exhaustive fixed-ROI review")
    _require(review.get("material_unknown") is False, "Material Unknown cannot become background")
    _require(type(review.get("negative_confirmed")) is bool, "Negative confirmation must be an explicit boolean")
    references = frame.get("positive_object_ids")
    _require(isinstance(references, list) and all(_text(item) for item in references)
             and len(set(references)) == len(references)
             and set(references) == {item["object_id"] for item in objects}, "Frame/object identities differ")
    _require(review["negative_confirmed"] == (not bool(objects)),
             "Zero GT needs explicit negative confirmation; positives cannot be negative")
    labels = []
    for item in sorted(objects, key=lambda item: item["object_id"]):
        visual_class = item.get("visual_class")
        _require(item.get("review_state") == "confirmed" and visual_class in CLASS_SCHEMA,
                 "Unconfirmed or unknown-class objects cannot qualify")
        _require(type(item.get("class_id")) is int and item["class_id"] == CLASS_SCHEMA[visual_class],
                 "Object class index differs from frozen schema")
        _require(item.get("frame_id") == frame["frame_id"]
                 and item.get("underlying_match_id") == frame["underlying_match_id"], "Object source differs")
        _require(item.get("owner") in ("opponent", "own", "unknown")
                 and item.get("form") in ("normal", "evolved", "unknown")
                 and item.get("origin_kind") in ("direct_card", "spawned", "unknown")
                 and _text(item.get("appearance_group_id")), "Required grouping metadata is missing or invalid")
        bbox = _vector(item.get("bbox_xywh_pixels"), 4)
        _require(all(type(coordinate) is int for coordinate in bbox), "Human GT must use integer original pixels")
        if visual_class == "unit.skeleton" and item["origin_kind"] == "spawned":
            relationship = item.get("source_relationship")
            _require(isinstance(relationship, str) and relationship.startswith("spawned_from:")
                     and _text(relationship.removeprefix("spawned_from:")), "Spawned Skeleton source relationship is required")
            if "spawned_from_appearance_group_id" in item:
                _require(item["spawned_from_appearance_group_id"] == relationship.removeprefix("spawned_from:"),
                         "Duplicate spawned-from identity conflicts")
            _require(item.get("is_skeleton_card_deployment", False) is False,
                     "Spawned Skeleton cannot be a Skeleton card deployment")
        labels.append({"object_id": item["object_id"], "category_id": item["class_id"],
                       "bbox_xywh_roi": bbox_to_roi(bbox, frame["image_size"]),
                       "metadata": deepcopy(dict(item))})
    return {"frame_id": frame["frame_id"], "purpose": purpose,
            "training_qualified": purpose == "TRAIN", "roi_xyxy": roi, "labels": labels,
            "qualification_scope": "selected_class_supervision_only",
            "negative_confirmed": review["negative_confirmed"], "review_id": review["review_id"],
            "annotation_sha256": digest, "fp_time_denominator_seconds": None}


def count_confirmed_deployments(groups):
    """Count explicit confirmed deployment identities, never frames or boxes.

    Independent claims require a confirmed group, a deployment_id and no
    spawned-from parent. Skeleton additionally requires direct_card origin;
    an explicitly confirmed independent Witch may retain unknown origin.
    Duplicate appearance groups sharing the same
    underlying match/deployment count once. This is an annotation summary, not
    an automatic tracker or an OpponentCardPlayed event emitter.
    """
    _require(isinstance(groups, Sequence) and not isinstance(groups, (str, bytes)), "Groups must be a sequence")
    deployments = {}
    appearances = {}
    counts = {"unit.skeleton": 0, "unit.witch": 0}
    for group in groups:
        _require(isinstance(group, Mapping) and group.get("visual_class") in CLASS_SCHEMA
                 and _text(group.get("appearance_group_id"))
                 and group.get("underlying_match_id") in MATCH_SPLITS, "Invalid appearance group identity")
        independent = group.get("independent_deployment_confirmed")
        _require(type(independent) is bool, "Deployment confirmation must be explicit")
        if not independent:
            continue
        _require(group.get("review_state") == "confirmed" and _text(group.get("deployment_id"))
                 and (group.get("origin_kind") == "direct_card"
                      or group["visual_class"] == "unit.witch" and group.get("origin_kind") == "unknown")
                 and group.get("spawned_from_appearance_group_id") is None
                 and not (isinstance(group.get("source_relationship"), str)
                          and group["source_relationship"].startswith("spawned_from:")),
                 "Unsupported independent deployment claim")
        identity = (group["underlying_match_id"], group["deployment_id"])
        appearance = (group["underlying_match_id"], group["appearance_group_id"])
        _require(appearance not in appearances or appearances[appearance] == identity,
                 "One appearance group cannot claim two deployment identities")
        appearances[appearance] = identity
        visual_class = group["visual_class"]
        _require(identity not in deployments or deployments[identity] == visual_class,
                 "One deployment identity cannot change visual class")
        if identity not in deployments:
            deployments[identity] = visual_class
            counts[visual_class] += 1
    return counts
