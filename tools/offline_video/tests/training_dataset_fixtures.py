"""Anonymous synthetic unit annotations, never real gameplay ground truth."""
from copy import deepcopy


def dataset_fixture(play_counts=(2, 2, 2, 2), *, absent=False):
    """Build hand-timed synthetic matches with four frames/three boxes per play."""
    draft = {
        "schema_version": 1, "dataset_id": "synthetic_minion_units",
        "freeze_version": 1, "created_at": "2026-10-05T01:00:00Z",
        "development_lock_sha256": "d" * 64,
        "target": {"card_id": "minions", "owner": "opponent", "form": "normal"},
        "visual_class": "minion_unit",
        "coordinate_policy": {"space": "normalized_full_image", "box_extent": "visible",
                              "image_basis": "original_rotated"},
        "intake": [], "matches": [], "recordings": [], "deployments": [],
        "frames": [], "unit_annotations": [], "unknown_intervals": [],
        "confirmed_absent_intervals": [],
        "annotation_sources": [{"annotation_source_id": "revision_1",
                                "path": "synthetic/units.v1.json", "sha256": "a" * 64}],
    }
    provenance = {"method": "manual", "reviewed_by": "synthetic_reviewer",
                  "notes": "Synthetic independent visible evidence"}
    for match_number, play_count in enumerate(play_counts, 1):
        mid, rid = f"match_{match_number}", f"recording_{match_number}"
        draft["matches"].append({"underlying_match_id": mid, "provenance": "natural",
                                 "identity_attestation": "human_confirmed",
                                 "notes": "Synthetic match identity"})
        draft["intake"].append({"intake_id": f"intake_{match_number}", "recording_id": rid,
                                "status": "included", "reason": "Synthetic eligible source",
                                "history": [{"status": "pending", "reason": "Awaited review"}]})
        draft["recordings"].append({
            "recording_id": rid, "underlying_match_id": mid,
            "source_sha256": f"{match_number:064x}", "source_path": f"synthetic/{rid}.mp4",
            "exports": [{"export_id": "export_1", "report_sha256": "c" * 64,
                         "index_sha256": "b" * 64,
                         "report_path": f"synthetic/{rid}/report.json",
                         "index_path": f"synthetic/{rid}/index.json"}],
            "width": 640, "height": 480, "rotation_degrees": 0,
            "time_base": {"numerator": 1, "denominator": 1000}, "origin_pts": 1000,
            "origin_time_base": {"numerator": 1, "denominator": 1000},
            "last_frame_seconds": 100,
            "technical_valid": True, "complete_recording": True,
            "unedited_recording": True, "full_human_review": True,
            "completion_attestation": "user_confirmed", "terminal_result_screen_present": False,
            "complete_segment": {"start_seconds": 0, "end_seconds": 100},
            "review_provenance": deepcopy(provenance),
        })
        for play_number in range(play_count):
            deployment_id = f"play_{play_number + 1}"
            onset = 10 + 20 * play_number
            draft["deployments"].append({
                "deployment_id": deployment_id, "underlying_match_id": mid, "recording_id": rid,
                "owner": "opponent", "source_card": "minions", "form": "normal",
                "verification_status": "confirmed", "independence_attestation": "human_confirmed",
                "onset_lower_seconds": onset, "onset_seconds": onset,
                "onset_upper_seconds": onset, "visible_start_seconds": onset,
                "visible_end_seconds": onset + 4, "occlusion": "none", "truncation": "none",
                "review_provenance": deepcopy(provenance),
            })
            for frame_number in range(4):
                fid = f"play_{play_number + 1}_frame_{frame_number + 1}"
                timestamp = onset + (frame_number + 1) / 5
                draft["frames"].append({
                    "frame_id": fid, "recording_id": rid, "export_ids": ["export_1"],
                    "timestamp_seconds": timestamp,
                    "raw_pts": round(timestamp * 1000) + 1000,
                    "time_base": {"numerator": 1, "denominator": 1000},
                    "image_path": f"synthetic/{rid}/{fid}.png", "image_width": 640,
                    "image_height": 480, "image_sha256": f"{match_number * 1000 + play_number * 10 + frame_number:064x}",
                    "review_status": "complete", "minion_presence": "positive",
                    "all_identifiable_units_labelled": True, "review_provenance": deepcopy(provenance),
                })
                for unit_number in range(3):
                    draft["unit_annotations"].append({
                        "annotation_id": f"{rid}_{fid}_unit_{unit_number + 1}",
                        "annotation_source_id": "revision_1", "recording_id": rid, "frame_id": fid,
                        "deployment_id": deployment_id, "owner": "opponent", "source_card": "minions",
                        "form": "normal", "visual_class": "minion_unit",
                        "normalized_bbox": {"x": 0.1 + unit_number / 5, "y": 0.2,
                                            "width": 0.05, "height": 0.1},
                        "occlusion": "none", "truncation": "none", "review_status": "verified",
                    })
        if absent:
            for interval_number, (start, end) in enumerate(((0, 5), (3, 8)), 1):
                draft["confirmed_absent_intervals"].append({
                    "interval_id": f"{rid}_absent_{interval_number}", "recording_id": rid,
                    "start_seconds": start, "end_seconds": end,
                    "review_provenance": deepcopy(provenance),
                })
    return draft


def add_reencoded_recording(draft, match_number=1):
    """Same declared match, distinct synthetic file; it creates no new event."""
    original = next(r for r in draft["recordings"] if r["recording_id"] == f"recording_{match_number}")
    copy = deepcopy(original)
    old_id, new_id = original["recording_id"], original["recording_id"] + "_reencoded"
    copy["recording_id"] = new_id
    copy["source_sha256"] = "e" * 64
    copy["source_path"] = f"synthetic/{new_id}.mp4"
    for export in copy["exports"]:
        export["report_path"] = export["report_path"].replace(old_id, new_id)
        export["index_path"] = export["index_path"].replace(old_id, new_id)
    draft["recordings"].append(copy)
    draft["intake"].append({"intake_id": "reencoded_intake", "recording_id": new_id,
                            "status": "included", "reason": "Same human-confirmed match", "history": []})
    for frame in list(draft["frames"]):
        if frame["recording_id"] == old_id:
            copy_frame = deepcopy(frame)
            copy_frame["recording_id"] = new_id
            copy_frame["image_path"] = copy_frame["image_path"].replace(old_id, new_id)
            draft["frames"].append(copy_frame)
    for annotation in list(draft["unit_annotations"]):
        if annotation["recording_id"] == old_id:
            copy_annotation = deepcopy(annotation)
            copy_annotation["annotation_id"] += "_reencoded"
            copy_annotation["recording_id"] = new_id
            draft["unit_annotations"].append(copy_annotation)
    return draft
