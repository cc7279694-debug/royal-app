"""Synthetic lock contracts; hashes do not represent real model artifacts."""
from copy import deepcopy

from evidence_fixtures import synthetic_evidence, synthetic_indexes


def model_fixture(development):
    return {
        "schema_version": 1, "experiment_id": development["experiment_id"],
        "freeze_version": 1, "created_at": "2026-10-04T02:00:00Z",
        "development_lock_sha256": development["sha256"],
        "target": {"card_id": "synthetic_card", "form": "normal"},
        "git_commit": "a" * 40, "model_sha256": "b" * 64,
        "development_session_id": "synthetic_development_session",
        "test_pixels_unseen": True, "precise_test_gt_unseen": True,
        "input": {"width": 64, "height": 48, "crop": None,
                  "resize": "letterbox", "interpolation": "bilinear",
                  "preprocess": {"color_order": "RGB", "dtype": "float32",
                                 "scale": 1 / 255, "mean": [0, 0, 0], "std": [1, 1, 1]}},
        "sampling": {"fps": 5, "start_seconds": 0}, "confidence_threshold": 0.5,
        "nms": {"enabled": True, "iou_threshold": 0.5},
        "postprocess": {"version": "synthetic_v1", "class_agnostic_nms": False,
                        "max_detections": 10},
        "evaluation_protocol_version": 1,
    }


def gt_fixture(development, model):
    evidence = synthetic_evidence(1)
    for entity in (evidence["recordings"], evidence["match_segments"], evidence["occurrences"],
                   evidence["frame_annotations"], evidence["negative_intervals"]):
        for item in entity:
            item["recording_id"] = "synthetic_test"
    evidence["recordings"][0]["source_sha256"] = "c" * 64
    play = evidence["occurrences"][0]
    gt = {
        "schema_version": 1, "experiment_id": development["experiment_id"],
        "freeze_version": 1, "created_at": "2026-10-04T03:00:00Z",
        "development_lock_sha256": development["sha256"], "model_lock_sha256": model["sha256"],
        "target": {"card_id": "synthetic_card", "form": "normal"},
        "identity": {"underlying_match_id": "synthetic_independent_match",
                     "recording_id": "synthetic_test", "split": "test",
                     "provenance": "new_natural", "complete_recording": True,
                     "unedited_recording": True, "full_human_review": True,
                     "first_qualifying_match": True, "all_deployments_reviewed": True},
        "annotation_session": {"session_id": "synthetic_fresh_annotator",
                               "independent_session": True, "predictions_unseen": True},
        "selection_history": [], "recording": deepcopy(evidence["recordings"][0]),
        "match_segments": deepcopy(evidence["match_segments"]),
        "evolution": {"capable": True, "equipped": "unknown",
                      "charge_requirement": None, "rules_version": None},
        "deployments": [{
            **{k: deepcopy(play[k]) for k in (
                "play_id", "recording_id", "card_id", "owner", "last_absent_seconds",
                "deployment_lower_seconds", "deployment_time_seconds", "deployment_upper_seconds",
                "visible_start_seconds", "visible_end_seconds", "match_segment_id", "notes")},
            "form": "normal", "evaluation_status": "evaluable", "non_evaluable_reason": None,
            "possible_missed_play": False,
            "evolution": {"progress": "unknown", "remaining_count": None, "source": "manual"},
            "key_frames": deepcopy(evidence["frame_annotations"]),
        }],
        "negative_intervals": deepcopy(evidence["negative_intervals"]), "unknown_intervals": [],
        "index_snapshot": synthetic_indexes(evidence),
        "evaluation_protocol_version": 1,
    }
    return gt
