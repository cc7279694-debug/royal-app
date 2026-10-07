"""Manual Event GT freezes human decisions, never visual-only automatic plays."""
import copy
import hashlib
import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def api():
    class Access:
        def __getattr__(self, name):
            try:
                return getattr(importlib.import_module("tools.deployment_review.event_gt"), name)
            except ImportError:
                pytest.fail("manual Event GT lock feature is not implemented")
    return Access()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


@pytest.fixture
def reviewed():
    plan = {
        "schema": "deployment_event_review_plan_v1",
        "inventory": [{"intake_order": n, "underlying_match_id": f"match_{n}",
                       "recording_id": f"recording_{n}", "source_sha256": "b" * 64,
                       "disposition": "candidate_context" if n in (1, 4) else "not_selected",
                       "reason": "manual original-order evidence"} for n in range(1, 5)],
        "evidence_sources": [{"source_id": "visual_gt", "sha256": "a" * 64}],
        "candidates": [],
    }
    for number, match, timestamp, card in [(1, 1, 5, "witch"), (2, 1, 8, "minions"),
                                          (3, 1, 10, "minions"), (4, 1, 11, "witch"),
                                          (5, 4, 5, "witch"), (6, 4, 7, "witch")]:
        plan["candidates"].append({
            "candidate_id": f"candidate_{number:02}", "underlying_match_id": f"match_{match}",
            "recording_id": f"recording_{match}", "approximate_timestamp": timestamp,
            "timestamp_kind": "visual_anchor_not_confirmed_spawn", "owner": "opponent",
            "card_id": card, "form": "unknown", "event_type": "grouped" if card == "minions" else "direct",
            "evaluable": False, "confidence": "uncertain", "review_state": "pending_human_review",
            "evidence_visual_classes": ["visual.unit.minion" if card == "minions" else "visual.unit.witch"],
            "evidence_frame_ids": [f"old_frame_{number}"],
            "visual_refs": [{"source_id": "visual_gt", "object_id": f"old_object_{number}",
                             "appearance_id": f"old_group_{number}", "owner": "opponent"}],
            "candidate_reason": "Visual anchor only; onset requires human context review.",
            "notes": "No automatic deployment truth.", "duplicate_hint": None,
            "context": {"start_seconds": timestamp - 2, "end_seconds": timestamp + 2,
                        "clip": f"clips/candidate_{number:02}.mp4", "clip_presentation_only": True,
                        "source_sha256": "b" * 64,
                        "frames": [{"image": f"frames/frame_{number}.png", "frame_id": f"context_frame_{number}",
                                    "raw_pts": timestamp * 10, "time_base": "1/10",
                                    "origin_seconds_exact": "0", "timestamp_seconds": float(timestamp)}]},
        })
    decisions = [
        {"candidate_id": "candidate_01", "decision": "uncertain", "event_confirmation": "uncertain",
         "evaluable": False, "uncertainty_reason": "deployment_onset_outside_review_window", "notes": "Onset absent."},
        {"candidate_id": "candidate_02", "decision": "confirm", "event_confirmation": "confirmed_new_deployment",
         "owner": "opponent", "card_id": "minions", "form": "unknown", "approximate_timestamp": 7.5,
         "event_type": "grouped", "evaluable": True, "confidence": "human_confirmed", "notes": "One grouped play."},
        {"candidate_id": "candidate_03", "decision": "merge_duplicate", "no_new_card_play": True,
         "merge_duplicate_of": "candidate_02", "notes": "Same group continues."},
        {"candidate_id": "candidate_04", "decision": "continuity", "no_new_card_play": True,
         "continuity_with": "candidate_01", "notes": "Existing unresolved unit continues."},
        {"candidate_id": "candidate_05", "decision": "uncertain", "event_confirmation": "uncertain",
         "evaluable": False, "uncertainty_reason": "deployment_onset_outside_review_window", "notes": "Onset absent."},
        {"candidate_id": "candidate_06", "decision": "confirm", "event_confirmation": "confirmed_new_deployment",
         "owner": "opponent", "card_id": "witch", "form": "unknown", "approximate_timestamp": 7.0,
         "event_type": "direct", "evaluable": True, "confidence": "human_confirmed", "notes": "New visible deployment."},
    ]
    returned = {"schema": "deployment_event_human_return_v1", "reviewer": "user",
                "actual_human_confirmation": True, "human_review_attested": True,
                "review_basis": "chatgpt_visual_review",
                "confirmation_source": "user_attestation_based_on_chatgpt_visual_review",
                "source_binding": {"source_plan_digest": semantic_sha(plan), "source_plan_file_sha256": "c" * 64},
                "negative_evidence": [], "decisions": decisions}
    return plan, returned


def test_build_derives_one_event_per_confirmed_candidate_and_preserves_uncertainty(api, reviewed):
    plan, returned = reviewed
    lock = api.build_lock(plan, returned)
    assert lock["schema"] == "deployment_event_gt_lock_v1"
    assert lock["freeze_version"] == 1
    assert lock["source_plan"] == plan and lock["human_return"] == returned
    assert [e["candidate_id"] for e in lock["confirmed_events"]] == ["candidate_02", "candidate_06"]
    first = lock["confirmed_events"][0]
    assert first == {
        "event_gt_id": "event-gt-candidate_02", "candidate_id": "candidate_02", "underlying_match_id": "match_1",
        "recording_id": "recording_1", "approximate_timestamp": 7.5, "owner": "opponent", "card_id": "minions",
        "form": "unknown", "evidence_visual_classes": ["visual.unit.minion"], "evidence_frame_ids": ["old_frame_2"],
        "event_type": "grouped", "evaluable": True, "confidence": "human_confirmed", "notes": "One grouped play.",
        "source_visual_group": [{"source_id": "visual_gt", "object_id": "old_object_2", "appearance_id": "old_group_2", "owner": "opponent"}],
    }
    assert [u["candidate_id"] for u in lock["unresolved_candidates"]] == ["candidate_01", "candidate_05"]
    assert all(u["event_confirmation"] == "uncertain" and u["evaluable"] is False for u in lock["unresolved_candidates"])
    assert lock["continuity_dedupe_outcomes"][0]["resolved_event_gt_id"] == "event-gt-candidate_02"
    assert lock["continuity_dedupe_outcomes"][1]["resolved_event_gt_id"] is None
    assert lock["summary"] == {"reviewed_candidate_count": 6, "confirmed_event_count": 2,
                               "continuity_dedupe_count": 2, "unresolved_candidate_count": 2,
                               "negative_evidence_count": 0, "reviewed_underlying_matches": ["match_1", "match_4"],
                               "confirmed_event_underlying_matches": ["match_1", "match_4"]}
    assert lock["negative_evidence"] == []
    assert lock["limitations"]["annotation_only"] is True
    assert lock["limitations"]["timestamps_are_approximate"] is True
    assert all(lock["limitations"][key] is False for key in ["cross_match_validation", "detector_performance",
        "full_match_coverage", "eight_card_state", "cycle_state", "elixir_state", "source_authenticity_verified"])
    assert lock == api.build_lock(plan, returned)
    api.validate_lock(lock)
    plan["candidates"][0]["notes"] = "caller mutation"
    returned["decisions"][0]["notes"] = "caller mutation"
    assert lock["source_plan"]["candidates"][0]["notes"] == "No automatic deployment truth."
    assert lock["human_return"]["decisions"][0]["notes"] == "Onset absent."


@pytest.mark.parametrize("field,value", [("reviewer", "ChatGPT"), ("reviewer", ""),
    ("actual_human_confirmation", False), ("actual_human_confirmation", 1),
    ("human_review_attested", False), ("review_basis", "automatic_inference"),
    ("confirmation_source", "chatgpt_attestation")])
def test_requires_exact_explicit_human_attestation(api, reviewed, field, value):
    reviewed[1][field] = value
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unknown", "pending", "extra_top", "extra_row", "negative"])
def test_candidates_partition_exactly_once_without_extra_claims(api, reviewed, mutation):
    returned = reviewed[1]
    if mutation == "missing":
        returned["decisions"].pop()
    elif mutation == "duplicate":
        returned["decisions"].append(copy.deepcopy(returned["decisions"][0]))
    elif mutation == "unknown":
        returned["decisions"][0]["candidate_id"] = "candidate_fake"
    elif mutation == "pending":
        returned["decisions"][0]["decision"] = "pending"
    elif mutation == "extra_top":
        returned["detector_accuracy"] = 1.0
    elif mutation == "extra_row":
        returned["decisions"][1]["last_absent_seconds"] = 6.5
    else:
        returned["negative_evidence"] = [{"candidate_id": "candidate_01", "absent": True}]
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("field,value", [("owner", "own"), ("owner", "unknown"), ("card_id", None),
    ("card_id", "cannon"), ("card_id", "skeletons"), ("card_id", "barbarian_barrel"), ("card_id", "witch"),
    ("form", "invalid"), ("event_type", "spawned"), ("event_type", "direct"),
    ("evaluable", False), ("confidence", "uncertain"), ("event_confirmation", "visual_only"),
    ("approximate_timestamp", float("nan")), ("approximate_timestamp", float("inf")),
    ("approximate_timestamp", True), ("approximate_timestamp", 5.9), ("approximate_timestamp", 10.1)])
def test_confirm_rejects_wrong_identity_owner_or_unsupported_timing(api, reviewed, field, value):
    reviewed[1]["decisions"][1][field] = value
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("field", ["owner", "card_id", "form", "event_confirmation", "evaluable", "confidence", "approximate_timestamp", "event_type"])
def test_confirmation_never_fills_missing_explicit_fields_from_visual_hints(api, reviewed, field):
    del reviewed[1]["decisions"][1][field]
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("target", ["candidate_01", "candidate_03", "candidate_04", "candidate_06", "missing"])
def test_merge_requires_an_earlier_same_match_confirmed_event(api, reviewed, target):
    reviewed[1]["decisions"][2]["merge_duplicate_of"] = target
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("target", ["candidate_04", "candidate_05", "candidate_06", "missing"])
def test_continuity_target_must_be_valid_earlier_and_same_match(api, reviewed, target):
    reviewed[1]["decisions"][3]["continuity_with"] = target
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


@pytest.mark.parametrize("index,field,value", [(2, "no_new_card_play", False), (3, "no_new_card_play", 1),
    (0, "evaluable", True), (0, "event_confirmation", "no_card_play"), (0, "uncertainty_reason", "")])
def test_unresolved_and_continuity_cannot_be_recast_as_negative(api, reviewed, index, field, value):
    reviewed[1]["decisions"][index][field] = value
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


def test_source_semantic_snapshot_must_match_bound_return(api, reviewed):
    reviewed[0]["candidates"][0]["notes"] = "changed after review"
    with pytest.raises(ValueError):
        api.build_lock(*reviewed)


def test_opponent_mortar_uses_official_structure_visual_mapping(api, reviewed):
    plan, returned = reviewed
    candidate = plan["candidates"][5]
    candidate["card_id"] = "mortar"
    candidate["evidence_visual_classes"] = ["visual.structure.mortar"]
    candidate["visual_refs"][0]["canonical_mapping"] = "building.mortar"
    returned["decisions"][5]["card_id"] = "mortar"
    returned["source_binding"]["source_plan_digest"] = semantic_sha(plan)
    event = api.build_lock(plan, returned)["confirmed_events"][1]
    assert event["card_id"] == "mortar"
    assert event["event_type"] == "direct"
    assert event["evidence_visual_classes"] == ["visual.structure.mortar"]


@pytest.mark.parametrize("card,visual,mapping,event_type", [
    ("golden_knight", "visual.unit.golden_knight", "unit.golden-knight", "direct"),
    ("flying_machine", "visual.unit.flying_machine", "unit.flying-machine", "direct"),
    ("royal_hogs", "visual.unit.royal_hog", "unit.royal-hog", "grouped"),
    ("skeleton_barrel", "visual.unit.skeleton_barrel", "unit.skeleton-barrel", "direct"),
])
def test_frozen_visual_canonical_hyphens_are_preserved(api, reviewed, card, visual, mapping, event_type):
    plan, returned = reviewed
    candidate = plan["candidates"][5]
    candidate.update(card_id=card, event_type=event_type, evidence_visual_classes=[visual])
    candidate["visual_refs"][0]["canonical_mapping"] = mapping
    returned["decisions"][5].update(card_id=card, event_type=event_type)
    returned["source_binding"]["source_plan_digest"] = semantic_sha(plan)
    event = api.build_lock(plan, returned)["confirmed_events"][1]
    assert event["card_id"] == card
    assert event["event_type"] == event_type
    assert event["source_visual_group"][0]["canonical_mapping"] == mapping


@pytest.mark.parametrize("mutation", ["unknown_owner", "null_mapping", "spawned_visual", "extra_claim",
    "null_reference_mapping", "wrong_reference_mapping", "spawned_reference", "clone_reference",
    "candidate_truth_claim", "invalid_evidence_list"])
def test_source_evidence_cannot_support_fabricated_opponent_card_play(api, reviewed, mutation):
    plan, returned = reviewed
    candidate = plan["candidates"][1]
    if mutation == "unknown_owner":
        candidate["visual_refs"][0]["owner"] = "unknown"
    elif mutation == "null_mapping":
        candidate["card_id"] = None
    elif mutation == "spawned_visual":
        candidate["evidence_visual_classes"] = ["visual.unit.skeleton"]
    elif mutation == "extra_claim":
        plan["detector_accuracy"] = 1.0
    elif mutation == "null_reference_mapping":
        candidate["visual_refs"][0]["canonical_mapping"] = None
    elif mutation == "wrong_reference_mapping":
        candidate["visual_refs"][0]["canonical_mapping"] = "unit.skeleton"
    elif mutation == "spawned_reference":
        candidate["visual_refs"][0]["origin"] = "spawned"
    elif mutation == "clone_reference":
        candidate["visual_refs"][0]["origin"] = "clone"
    elif mutation == "candidate_truth_claim":
        candidate["training_qualified"] = True
    else:
        candidate["evidence_frame_ids"] = "not-a-list"
    returned["source_binding"]["source_plan_digest"] = semantic_sha(plan)
    with pytest.raises(ValueError):
        api.build_lock(plan, returned)


@pytest.mark.parametrize("version", [0, 2, True, "1"])
def test_only_integer_v1_can_be_frozen(api, reviewed, version):
    with pytest.raises(ValueError):
        api.build_lock(*reviewed, freeze_version=version)


@pytest.mark.parametrize("mutation", ["timestamp", "count", "missing_event", "negative", "limits", "identity", "extra", "version"])
def test_semantic_tampering_is_rejected_even_after_attacker_recalculates_digest(api, reviewed, mutation):
    lock = api.build_lock(*reviewed)
    if mutation == "timestamp":
        lock["confirmed_events"][0]["approximate_timestamp"] = 8.0
    elif mutation == "count":
        lock["summary"]["confirmed_event_count"] = 500
    elif mutation == "missing_event":
        lock["confirmed_events"].pop()
    elif mutation == "negative":
        lock["negative_evidence"].append({"candidate_id": "candidate_01"})
    elif mutation == "limits":
        lock["limitations"]["cross_match_validation"] = True
    elif mutation == "identity":
        lock["freeze_identity"] = "forged"
    elif mutation == "extra":
        lock["training_qualified"] = True
    else:
        lock["freeze_version"] = 2
    lock["lock_digest"] = semantic_sha({key: value for key, value in lock.items() if key != "lock_digest"})
    with pytest.raises(ValueError):
        api.validate_lock(lock)


def test_digest_tamper_is_rejected(api, reviewed):
    lock = api.build_lock(*reviewed)
    lock["human_return"]["decisions"][0]["notes"] = "tampered"
    with pytest.raises(ValueError):
        api.validate_lock(lock)


def test_freeze_roundtrips_exactly_and_never_overwrites(api, reviewed, tmp_path):
    lock = api.build_lock(*reviewed)
    target = tmp_path / "event_gt.v1.json"
    assert api.freeze_lock(lock, target) == target
    assert api.load_lock(target) == lock
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        api.freeze_lock(lock, target)
    assert target.read_bytes() == original
    target.rename(tmp_path / "renamed-history.data")
    with pytest.raises(FileExistsError):
        api.freeze_lock(lock, target)
    assert not target.exists()
    assert (tmp_path / "renamed-history.data").read_bytes() == original


def test_changed_return_cannot_silently_create_same_source_v1_revision(api, reviewed, tmp_path):
    api.freeze_lock(api.build_lock(*reviewed), tmp_path / "first.json")
    reviewed[1]["decisions"][1]["notes"] = "different later correction"
    with pytest.raises(FileExistsError):
        api.freeze_lock(api.build_lock(*reviewed), tmp_path / "second.json")
    assert not (tmp_path / "second.json").exists()


@pytest.mark.parametrize("content", [b'{"schema":"a","schema":"b"}', b'{"x": NaN}',
                                    b'{"x": Infinity}', b'[]', b'broken', b'\xff'])
def test_load_rejects_malformed_json_without_loose_parser(api, tmp_path, content):
    target = tmp_path / "invalid.json"
    target.write_bytes(content)
    with pytest.raises(ValueError):
        api.load_lock(target)


def test_load_has_a_byte_size_bound(api, tmp_path):
    target = tmp_path / "oversized.json"
    target.write_bytes(b" " * (8 * 1024 * 1024 + 1))
    with pytest.raises(ValueError):
        api.load_lock(target)


def test_freeze_refuses_unvalidated_lock_without_creating_file(api, reviewed, tmp_path):
    lock = api.build_lock(*reviewed)
    lock["summary"]["confirmed_event_count"] = 3
    target = tmp_path / "invalid.json"
    with pytest.raises(ValueError):
        api.freeze_lock(lock, target)
    assert not target.exists()


def test_freeze_refuses_parent_traversal_and_relative_destinations(api, reviewed, tmp_path):
    lock = api.build_lock(*reviewed)
    for path in [Path("relative.json"), tmp_path / ".." / "escaped.json"]:
        with pytest.raises(ValueError):
            api.freeze_lock(lock, path)


def test_symlink_parent_or_destination_cannot_escape_explicit_directory(api, reviewed, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "linked"
    try:
        linked.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("creating symlinks requires unavailable OS permission")
    with pytest.raises(ValueError):
        api.freeze_lock(api.build_lock(*reviewed), linked / "escaped.json")
    assert not (outside / "escaped.json").exists()
