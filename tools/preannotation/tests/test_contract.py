"""Breaks caught: promotion without human evidence, unsafe negatives and mutation."""
import copy
import importlib
import json

import pytest


@pytest.fixture
def api():
    class ContractAccess:
        def __getattr__(self, name):
            try:
                return getattr(importlib.import_module("tools.preannotation.contract"), name)
            except ImportError:
                pytest.fail("preannotation contract is not implemented")
    return ContractAccess()


@pytest.fixture
def bundle():
    return {
        "schema": "preannotation_bundle_v1",
        "recording_id": "natural_match_01",
        "inventory": [
            {"recording_id": f"natural_match_0{i}", "intake_order": i,
             "truncated": i == 2, "training_excluded": i == 2}
            for i in range(1, 5)
        ],
        "prediction_sha256": "a" * 64,
        "frames": [{"frame_id": "frame-1", "raw_pts": 1, "time_base": "1/2",
                    "width": 100, "height": 200, "image": "images/frame-1.png",
                    "proposals": [
                        {"proposal_id": f"p{i}", "status": "pending",
                         "bbox_xyxy": [10, 20, 30, 40],
                         "raw_teacher": {"class": "witch", "confidence": .8,
                                         "owner_prediction": "opponent"}}
                        for i in range(1, 6)
                    ]}],
    }


def reviewed(api, bundle):
    result = api.return_template(bundle)
    result["provenance"] = {"kind": "human", "reviewer": "Test Reviewer",
                            "human_review_attested": True, "synthetic": False}
    return result


def accepted(proposal="p1", action="accept"):
    return {"proposal_id": proposal, "action": action, "decision": "accepted",
            "visual_class": "visual.unit.witch", "canonical_mapping": "unit.witch",
            "bbox_xyxy": [10, 20, 30, 40], "owner": "unknown", "form": "unknown",
            "origin": "unknown", "appearance_id": "witch-a", "visibility": "visible",
            "uncertainty": "none", "note": "visible identity confirmed"}


def test_ids_bind_prediction_bytes_recording_exact_time_and_row(api):
    a = api.proposal_id("a" * 64, "match", 1, "1/2", 0)
    assert a == api.proposal_id("a" * 64, "match", 2, "1/4", 0)
    assert a != api.proposal_id("b" * 64, "match", 1, "1/2", 0)
    assert a != api.proposal_id("a" * 64, "match", 1, "1/2", 1)
    assert a != api.proposal_id("a" * 64, "other", 1, "1/2", 0)


def test_templates_leave_every_proposal_and_whole_frame_unreviewed(api, bundle):
    result = api.return_template(bundle)
    assert result["provenance"]["human_review_attested"] is False
    assert result["frames"][0]["coverage"] == []
    assert result["frames"][0]["decisions"] == []


def test_five_actions_preserve_raw_teacher_and_never_create_events(api, bundle):
    result = reviewed(api, bundle)
    decisions = [accepted(), {**accepted("p2"), "action": "reject", "decision": "rejected"},
                 {**accepted("p3", "relabel"), "visual_class": "visual.unit.balloon",
                  "canonical_mapping": "unit.balloon", "appearance_id": "balloon-a"},
                 {**accepted("p4", "bbox-correct"), "bbox_xyxy": [11, 21, 31, 41]},
                 {**accepted(None, "missing-box"), "manual_id": "missing-1",
                  "appearance_id": "witch-b"}]
    result["frames"][0]["decisions"] = decisions
    original = copy.deepcopy(bundle)
    gt = api.validate_return(bundle, result)
    assert bundle == original
    assert len(gt["positive_boxes"]) == 4
    assert len(gt["unresolved_regions"]) == 2  # rejected p2, untouched p5
    assert gt["negative_evidence"] == []
    assert gt["card_events"] == []
    assert gt["independent_deployments"] == 0
    assert gt["training_qualified"] is False
    assert gt["ordinary_training_export_allowed"] is False
    assert gt["positive_boxes"][1]["raw_teacher"]["class"] == "witch"
    assert gt["positive_boxes"][1]["visual_class"] == "visual.unit.balloon"
    assert gt["positive_boxes"][2]["bbox_xyxy"] == [11, 21, 31, 41]
    assert gt["positive_boxes"][3]["raw_teacher"] is None


def test_exhaustiveness_is_class_specific_and_explicit(api, bundle):
    bundle["frames"][0]["proposals"] = []
    result = reviewed(api, bundle)
    assert api.validate_return(bundle, result)["negative_evidence"] == []
    result["frames"][0]["coverage"] = [{"visual_class": "visual.unit.witch",
        "exhaustive": True, "scope": "full_frame", "unresolved": False}]
    gt = api.validate_return(bundle, result)
    assert gt["negative_evidence"] == [{"frame_id": "frame-1", "visual_class": "visual.unit.witch"}]
    assert gt["ordinary_training_export_allowed"] is False


@pytest.mark.parametrize("decision", ["pending", "unknown", "rejected"])
def test_unresolved_regions_block_negative_even_with_exhaustive_claim(api, bundle, decision):
    result = reviewed(api, bundle)
    if decision != "pending":
        result["frames"][0]["decisions"] = [{**accepted(), "decision": decision,
                                            "action": "reject" if decision == "rejected" else "accept"}]
    result["frames"][0]["coverage"] = [{"visual_class": "visual.unit.witch",
        "exhaustive": True, "scope": "full_frame", "unresolved": False}]
    assert api.validate_return(bundle, result)["negative_evidence"] == []


@pytest.mark.parametrize("patch", [
    {"bbox_xyxy": [-1, 20, 30, 40]}, {"bbox_xyxy": [10, 20, 101, 40]},
    {"bbox_xyxy": [30, 20, 10, 40]}, {"bbox_xyxy": [10, 20, float("nan"), 40]},
    {"visual_class": "witch"}, {"owner": "model"}, {"origin": "card-play"},
    {"proposal_id": "unknown-proposal"}, {"appearance_id": ""},
    {"card_play_event": True}, {"action": "silent-promote"},
    {"visual_class": "visual.teacher.witch"},
])
def test_invalid_human_edits_are_rejected(api, bundle, patch):
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [{**accepted(), **patch}]
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)


def test_groups_link_repeated_appearance_without_implying_independence(api, bundle):
    other = copy.deepcopy(bundle["frames"][0])
    other.update(frame_id="frame-2", raw_pts=2)
    other["proposals"] = [{**other["proposals"][0], "proposal_id": "p6"}]
    bundle["frames"].append(other)
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [accepted()]
    result["frames"][1]["decisions"] = [accepted("p6")]
    gt = api.validate_return(bundle, result)
    assert gt["appearance_groups"] == {"witch-a": ["p1", "p6"]}
    assert gt["independent_deployments"] == 0
    result["frames"][1]["decisions"][0]["visual_class"] = "visual.unit.balloon"
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)


def test_synthetic_corrections_are_never_human_gt(api, bundle):
    result = reviewed(api, bundle)
    result["provenance"].update(kind="synthetic", synthetic=True, human_review_attested=False)
    result["frames"][0]["decisions"] = [accepted()]
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)
    gt = api.validate_return(bundle, result, allow_synthetic=True)
    assert gt["status"] == "synthetic_not_gt"
    assert gt["positive_boxes"][0]["human_confirmed"] is False


def test_unattested_or_wrong_bundle_returns_fail(api, bundle):
    with pytest.raises(ValueError):
        api.validate_return(bundle, api.return_template(bundle))
    result = reviewed(api, bundle)
    result["bundle_sha256"] = "b" * 64
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)


def test_inventory_order_and_truncated_training_exclusion_are_enforced(api, bundle):
    bundle["inventory"][1]["training_excluded"] = False
    with pytest.raises(ValueError):
        api.validate_bundle(bundle)
    bundle["inventory"][1]["training_excluded"] = True
    bundle["inventory"].reverse()
    with pytest.raises(ValueError):
        api.validate_bundle(bundle)


def test_truncated_match_never_produces_training_negative(api, bundle):
    bundle["recording_id"] = "natural_match_02"
    bundle["frames"][0]["proposals"] = []
    result = reviewed(api, bundle)
    result["frames"][0]["coverage"] = [{"visual_class": "visual.unit.witch",
        "exhaustive": True, "scope": "full_frame", "unresolved": False}]
    gt = api.validate_return(bundle, result)
    assert gt["negative_evidence"] == []
    assert gt["training_excluded"] is True


def test_duplicate_decisions_and_frame_ids_fail(api, bundle):
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [accepted(), accepted()]
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)
    result["frames"] = result["frames"] * 2
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)


def test_synthetic_bundle_cannot_be_falsely_attested_as_real_gt(api, bundle):
    bundle["synthetic"] = True
    with pytest.raises(ValueError):
        api.validate_return(bundle, reviewed(api, bundle))


def test_ambiguous_rejection_needs_no_invented_class_or_appearance(api, bundle):
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [{**accepted(), "action": "reject", "decision": "rejected",
        "visual_class": None, "canonical_mapping": None, "appearance_id": None}]
    gt = api.validate_return(bundle, result)
    assert gt["unresolved_regions"][0]["visual_class"] is None
    assert gt["unresolved_regions"][0]["human_confirmed"] is False


def test_uncertain_acceptance_does_not_claim_human_confirmation(api, bundle):
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [{**accepted(), "uncertainty": "unknown"}]
    gt = api.validate_return(bundle, result)
    assert gt["positive_boxes"] == []
    assert gt["unresolved_regions"][0]["human_confirmed"] is False


def test_rejected_class_hypothesis_cannot_exempt_region_from_other_class_negative(api, bundle):
    bundle["frames"][0]["proposals"] = bundle["frames"][0]["proposals"][:1]
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [{**accepted(), "action": "reject", "decision": "rejected",
        "visual_class": "visual.unit.balloon", "canonical_mapping": "unit.balloon"}]
    result["frames"][0]["coverage"] = [{"visual_class": "visual.unit.witch",
        "exhaustive": True, "scope": "full_frame", "unresolved": False}]
    assert api.validate_return(bundle, result)["negative_evidence"] == []


def test_appearance_continuity_rejects_conflicting_known_owner(api, bundle):
    other = copy.deepcopy(bundle["frames"][0])
    other.update(frame_id="frame-2", raw_pts=2)
    other["proposals"] = [{**other["proposals"][0], "proposal_id": "p6"}]
    bundle["frames"].append(other)
    result = reviewed(api, bundle)
    result["frames"][0]["decisions"] = [{**accepted(), "owner": "opponent"}]
    result["frames"][1]["decisions"] = [{**accepted("p6"), "owner": "own"}]
    with pytest.raises(ValueError):
        api.validate_return(bundle, result)
