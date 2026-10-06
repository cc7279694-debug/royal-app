"""Extensible synthetic multiclass declarations; no real game/media data."""
from copy import deepcopy
from fractions import Fraction

from clash_tracker_video.evidence_prepare import frame_id


def multiclass_fixture(class_ids=("unit.speck", "unit.guard", "building.anchor"),
                       *, match_count=2, own_class_ids=None):
    """Three arbitrary classes/two matches; one own control, all opponent support."""
    own_class_ids = set(class_ids[:1] if own_class_ids is None else own_class_ids)
    review = {"method": "manual", "reviewed_by": "synthetic_reviewer",
              "notes": "Program-generated synthetic evidence"}
    draft = {
        "kind": "multiclass_visual_dataset", "schema_version": 1,
        "dataset_id": "synthetic_multiclass", "freeze_version": 1,
        "created_at": "2026-10-05T01:00:00Z",
        "taxonomy": {"taxonomy_id": "synthetic_visual_types", "version": 1,
                     "classes": [], "alias_mapping": []},
        "coordinate_policy": {"space": "normalized_full_image", "box_extent": "visible",
                              "image_basis": "original_rotated"},
        "intake": [], "matches": [], "recordings": [], "groups": [], "frames": [],
        "annotations": [], "coverage": [], "split_assignment": [],
        "annotation_sources": [{"annotation_source_id": "revision_1",
                                "path": "synthetic/annotations.v1.json", "sha256": "a" * 64}],
        "provenance": [{"source_id": "synthetic_source", "creator": "synthetic_test_author",
                        "source_url": None, "artifact_kind": "synthetic_test",
                        "license_evidence": "Generated test geometry; no game assets",
                        "allowed_scope": "development_training"}],
        "selection": None, "backend_label_maps": {},
    }
    for index, cid in enumerate(class_ids):
        draft["taxonomy"]["classes"].append({
            "visual_class_id": cid, "kind": "building" if cid.startswith("building.") else "unit",
            "mobility": "static" if cid.startswith("building.") else "moving",
            "definition": f"Synthetic visible geometry {index + 1}",
        })
    for match_number in range(1, match_count + 1):
        mid, rid = f"match_{match_number}", f"recording_{match_number}"
        split = "train" if match_number % 2 else "development_validation"
        perspective = f"{mid}_view"
        draft["matches"].append({"underlying_match_id": mid, "provenance": "natural",
                                 "identity_attestation": "human_confirmed", "notes": "Synthetic identity"})
        draft["split_assignment"].append({"underlying_match_id": mid, "split": split})
        draft["intake"].append({"intake_id": f"intake_{match_number}", "recording_id": rid,
                                "status": "included", "reason": "Synthetic complete source", "history": []})
        draft["recordings"].append({
            "recording_id": rid, "underlying_match_id": mid, "split": split,
            "source_id": "synthetic_source", "source_sha256": f"{match_number:064x}",
            "source_path": f"synthetic/{rid}.mp4", "perspective_ref": perspective,
            "width": 640, "height": 480, "rotation_degrees": 0,
            "time_base": {"numerator": 1, "denominator": 1000}, "origin_pts": 1000,
            "origin_time_base": {"numerator": 1, "denominator": 1000},
            "last_frame_seconds": 100, "technical_valid": True, "complete_recording": True,
            "unedited_recording": True, "full_human_review": True,
            "completion_attestation": "user_confirmed", "terminal_result_screen_present": False,
            "match_segment": {"start_seconds": 0, "end_seconds": 100, "complete_match": True},
            "exports": [{"export_id": "export_1", "report_path": f"synthetic/{rid}/report.json",
                         "index_path": f"synthetic/{rid}/index.json", "report_sha256": "c" * 64,
                         "index_sha256": "b" * 64}], "review_provenance": deepcopy(review),
        })
        for class_index, cid in enumerate(class_ids):
            timestamp = 10 + class_index * 10
            pts = 1000 + timestamp * 1000
            fid = frame_id(rid, pts, Fraction(1, 1000))
            draft["frames"].append({
                "frame_id": fid, "recording_id": rid, "export_ids": ["export_1"],
                "timestamp_seconds": timestamp, "raw_pts": pts,
                "time_base": {"numerator": 1, "denominator": 1000},
                "origin": {"raw_pts": 1000, "time_base": {"numerator": 1, "denominator": 1000}},
                "image_path": f"synthetic/{rid}/{fid}.png", "image_width": 640, "image_height": 480,
                "image_sha256": f"{match_number * 100 + class_index:064x}",
                "perspective_ref": perspective, "perspective_change_reason": None,
                "review_state": "complete", "review_provenance": deepcopy(review),
            })
            draft["coverage"].append({
                "coverage_id": f"{rid}_coverage_{class_index}", "recording_id": rid, "frame_id": fid,
                "exhaustive_for_classes": list(class_ids), "exhaustive_state": "complete",
                "reviewed_regions": [{"x": 0, "y": 0, "width": 1, "height": 1}],
                "unknown_intervals": [], "ignore_regions": [], "ignore_reasons": [],
                "review_provenance": deepcopy(review),
            })
            for owner_index, owner in enumerate(("opponent", "own") if cid in own_class_ids else ("opponent",)):
                gid = f"{mid}_class_{class_index}_{owner}"
                entity = f"{gid}_entity_1"
                draft["groups"].append({
                    "appearance_group_id": gid, "underlying_match_id": mid, "recording_id": rid,
                    "visual_class_id": cid, "owner": owner, "observed_form": "normal",
                    "origin_kind": "direct", "causal_root_id": gid, "parent_group_id": None,
                    "entity_occurrence_id": None, "human_deployment_id": f"{gid}_human_event",
                    "independence_attestation": "human_confirmed", "verification_state": "confirmed",
                    "start_seconds": timestamp, "end_seconds": timestamp + 3,
                    "review_provenance": deepcopy(review),
                })
                size = 0.03 if class_index == 0 else 0.09 if class_index == 1 else 0.15
                draft["annotations"].append({
                    "annotation_id": f"{gid}_annotation", "annotation_source_id": "revision_1",
                    "recording_id": rid, "frame_id": fid, "appearance_group_id": gid,
                    "entity_occurrence_id": entity, "visual_class_id": cid, "owner": owner,
                    "perspective_ref": perspective, "observed_form": "normal", "visual_stage": None,
                    "box": {"x": 0.1 + owner_index * 0.3, "y": 0.2, "width": size, "height": size * 2},
                    "source_card_id": None, "source_card_candidates": [], "mapping_basis": "unknown",
                    "mapping_verification": "pending", "occlusion": "none", "truncation": "none",
                    "review_state": "verified", "review_provenance": deepcopy(review),
                })
    return draft


def add_rerecording(draft, recording_id="recording_1"):
    """Add a synthetic re-encode of an existing match, no extra cause or frame."""
    old = next(r for r in draft["recordings"] if r["recording_id"] == recording_id)
    record = deepcopy(old)
    record["recording_id"] += "_rerun"
    record["source_path"] = f"synthetic/{record['recording_id']}.mp4"
    record["source_sha256"] = "e" * 64
    for export in record["exports"]:
        for key in ("report_path", "index_path"):
            export[key] = export[key].replace(recording_id, record["recording_id"])
    draft["recordings"].append(record)
    draft["intake"].append({"intake_id": record["recording_id"] + "_intake",
                            "recording_id": record["recording_id"], "status": "included",
                            "reason": "Same synthetic underlying match", "history": []})
    return record


def write_multiclass_sidecars(root, draft):
    """Materialize additive synthetic label rows, never alter pure fixture logic."""
    from clash_tracker_video.evidence_prepare import file_hash
    from clash_tracker_video.experiment_lock import canonical_bytes
    for source in draft["annotation_sources"]:
        path = root / source["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        document = {"schema_version": 1, "annotation_source_id": source["annotation_source_id"],
                    "annotations": [deepcopy(r) for r in draft["annotations"]
                                    if r["annotation_source_id"] == source["annotation_source_id"]]}
        path.write_bytes(canonical_bytes(document) + b"\n")
        source["sha256"] = file_hash(path)


def multiclass_disk_fixture(root, *, draft=None, rotation=0):
    """Real synthetic MP4 producer exports, with no gameplay or fabricated report."""
    from conftest import make_video
    from clash_tracker_video import evidence_prepare as ep
    current = deepcopy(draft) if draft is not None else multiclass_fixture()
    for number, record in enumerate(current["recordings"], 1):
        rid = record["recording_id"]
        frames = sorted([f for f in current["frames"] if f["recording_id"] == rid],
                        key=lambda f: f["timestamp_seconds"])
        times = [f["timestamp_seconds"] for f in frames]
        source = make_video(root / f"local_data/{rid}.mp4",
                            pts=[number * 1000, *[number * 1000 + int(t * 1000) for t in times],
                                 number * 1000 + 100000], rotation=rotation)
        run = root / f"outputs/{rid}"
        index = ep.prepare_evidence(source, run, recording_id=rid, times=times)
        record["source_path"] = source.relative_to(root).as_posix()
        for key in ("source_sha256", "width", "height", "rotation_degrees", "time_base",
                    "origin_pts", "origin_time_base", "last_frame_seconds"):
            record[key] = deepcopy(index["recording"][key])
        record["match_segment"]["end_seconds"] = record["last_frame_seconds"]
        record["exports"] = [{"export_id": "export_1", "index_path": f"outputs/{rid}/index.json",
                              "report_path": f"outputs/{rid}/exports/report.json",
                              "index_sha256": ep.file_hash(run / "index.json"),
                              "report_sha256": ep.file_hash(run / "exports/report.json")}]
        for frame, actual in zip(frames, index["frames"]):
            old_id = frame["frame_id"]
            for key in ("frame_id", "timestamp_seconds", "raw_pts", "time_base", "image_width", "image_height"):
                frame[key] = deepcopy(actual[key])
            frame["origin"] = {"raw_pts": record["origin_pts"], "time_base": deepcopy(record["origin_time_base"])}
            frame["image_path"] = (run / actual["image_path"]).relative_to(root).as_posix()
            frame["image_sha256"] = ep.file_hash(root / frame["image_path"])
            for row in [*current["annotations"], *current["coverage"]]:
                if row["frame_id"] == old_id:
                    row["frame_id"] = frame["frame_id"]
    for source in current["annotation_sources"]:
        source["path"] = f"outputs/labels/{source['annotation_source_id']}.json"
    write_multiclass_sidecars(root, current)
    return current
