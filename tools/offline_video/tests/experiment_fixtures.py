"""Anonymous, complete synthetic development draft: no real match or media."""
from copy import deepcopy

from evidence_fixtures import synthetic_evidence, synthetic_indexes


def development_fixture():
    evidence = synthetic_evidence(2)
    draft = {
        "schema_version": 1, "experiment_id": "anonymous_experiment",
        "freeze_version": 1, "created_at": "2026-10-04T01:00:00Z",
        "protocol_version": 1, "policy_version": 1,
        "identity": {
            "underlying_match_id": "anonymous_match_a", "recording_id": "synthetic",
            "split": "development", "provenance": "new_natural",
            "complete_recording": True, "unedited_recording": True,
            "full_human_review": True,
        },
        "candidates": [{
            "candidate_id": "candidate_normal", "card_id": "synthetic_card", "form": "normal",
            "notes": {
                "distinctness": "Separate absence and spawn for each occurrence",
                "visibility": "Three original visible key frames per occurrence",
                "occlusion": "No relevant occlusion in these synthetic examples",
                "owner_clarity": "Opponent perspective manually reviewed",
                "form_clarity": "Normal appearance manually reviewed",
            },
            "evidence": evidence,
            "deployments": [{
                "play_id": p["play_id"], "clear": True, "form": "normal",
                "possible_missed_play": False,
                "evolution": {"progress": "known", "remaining_count": 1, "source": "manual"},
            } for p in evidence["occurrences"]],
            "evolution": {
                "capable": True, "equipped": "verified", "charge_requirement": 2,
                "rules_version": "anonymous_rules_v1",
            },
        }],
        "selection": {
            "candidate_id": "candidate_normal", "card_id": "synthetic_card",
            "form": "normal", "method": "manual", "reason": "Two distinct clear normal plays",
        },
        "unknown_intervals": [],
    }
    return draft, synthetic_indexes(evidence)


def split_forms(draft):
    """Retain one independent occurrence in each known form, with no negatives."""
    original = draft["candidates"][0]
    candidates = []
    for i, form in enumerate(("normal", "evolved")):
        candidate = deepcopy(original)
        candidate["candidate_id"] = "candidate_" + form
        candidate["form"] = form
        candidate["evidence"]["target_card"]["variant"] = (
            "known_evolution" if form == "evolved" else "normal")
        candidate["evidence"]["occurrences"] = [candidate["evidence"]["occurrences"][i]]
        ids = candidate["evidence"]["occurrences"][0]["evidence_annotation_ids"]
        candidate["evidence"]["frame_annotations"] = [
            a for a in candidate["evidence"]["frame_annotations"] if a["annotation_id"] in ids]
        candidate["evidence"]["negative_intervals"] = []
        candidate["deployments"] = [candidate["deployments"][i]]
        candidate["deployments"][0]["form"] = form
        candidate["deployments"][0]["evolution"] = {
            "progress": "unknown", "remaining_count": None, "source": "manual"}
        candidates.append(candidate)
    draft["candidates"] = candidates
    return draft


def user_confirmed_development_fixture():
    """No result-screen negative; actual file end and terminal uncertainty retained."""
    draft, indexes = development_fixture()
    draft["identity"].update(completion_attestation="user_confirmed",
                             terminal_result_screen_present=False)
    candidate = draft["candidates"][0]
    candidate["evidence"]["match_segments"][0]["end_seconds"] = 20
    candidate["evidence"]["negative_intervals"] = [
        n for n in candidate["evidence"]["negative_intervals"] if n["reason"] != "result"]
    draft["unknown_intervals"] = [{"unknown_id": "terminal_unknown", "recording_id": "synthetic",
        "start_seconds": 19, "end_seconds": 20, "reason": "Result UI is absent; target absence is not inferred"}]
    for deployment in candidate["deployments"]:
        deployment["evolution"] = {"progress": "unknown", "remaining_count": None, "source": "manual"}
    return draft, indexes
