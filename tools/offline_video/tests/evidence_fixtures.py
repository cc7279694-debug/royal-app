"""Synthetic geometry only; no game imagery or private source metadata."""
from copy import deepcopy


def synthetic_evidence(plays=4):
    recording = dict(recording_id="synthetic", source_sha256="0" * 64,
                     width=64, height=48, duration_seconds=20.1,
                     time_base=dict(numerator=1, denominator=1000), origin_pts=5000,
                     origin_time_base=dict(numerator=1, denominator=1000),
                     last_frame_seconds=20, rotation_degrees=0,
                     orientation="landscape", perspective="own_bottom")
    doc = dict(schema_version=1, recordings=[recording], match_segments=[dict(
        segment_id="match", recording_id="synthetic", start_seconds=0,
        end_seconds=19, perspective="own_bottom", validation_status="verified",
        capture_complete=True, boundary_uncertainty_seconds=0, notes="Synthetic full match")],
        target_card=dict(card_id="synthetic_card", display_name="Synthetic unit",
                         selection_reason="Synthetic test", ambiguity_notes="", variant="normal"),
        occurrences=[], frame_annotations=[], negative_intervals=[])
    previous = 0
    for i in range(plays):
        start = 1 + i * 4
        play = f"play{i}"
        ids = []
        for j in range(3):
            timestamp = start + j * .1
            aid = f"box{i}_{j}"
            ids.append(aid)
            doc["frame_annotations"].append(dict(
                annotation_id=aid, frame_id=f"frame{i}_{j}", recording_id="synthetic",
                play_id=play, timestamp_seconds=timestamp,
                raw_pts=5000 + start * 1000 + j * 100,
                time_base=dict(numerator=1, denominator=1000), image_path=f"exports/{aid}.png",
                image_width=64, image_height=48,
                normalized_bbox=dict(x=.1, y=.1, width=.3, height=.3),
                annotation_source="manual", review_status="verified"))
        doc["occurrences"].append(dict(
            play_id=play, recording_id="synthetic", card_id="synthetic_card", owner="opponent",
            last_absent_seconds=start - .1, deployment_lower_seconds=start - .1,
            deployment_time_seconds=start, deployment_upper_seconds=start,
            visible_start_seconds=start, visible_end_seconds=start + 1,
            match_segment_id="match", manual_verification_status="verified",
            evidence_annotation_ids=ids, notes="Reviewed absence then new spawn then continued visible unit"))
        doc["negative_intervals"].append(dict(
            negative_id=f"negative{i}", recording_id="synthetic", start_seconds=previous,
            end_seconds=start, reason="target_absent", match_segment_id="match",
            non_match=False, review_status="verified"))
        previous = start + 1
    doc["negative_intervals"].extend([
        dict(negative_id="tail", recording_id="synthetic", start_seconds=previous,
             end_seconds=19, reason="target_absent", match_segment_id="match", non_match=False,
             review_status="verified"),
        dict(negative_id="menu", recording_id="synthetic", start_seconds=19,
             end_seconds=20, reason="result", match_segment_id=None, non_match=True,
             review_status="verified")])
    return doc


def synthetic_indexes(doc):
    return {r["recording_id"]: dict(recording=deepcopy(r), frames=[dict(
        frame_id=a["frame_id"], requested_seconds=a["timestamp_seconds"],
        timestamp_seconds=a["timestamp_seconds"], raw_pts=a["raw_pts"],
        time_base=deepcopy(a["time_base"]), image_path=a["image_path"],
        image_width=a["image_width"], image_height=a["image_height"], status="success", reason=None)
        for a in doc["frame_annotations"] if a["recording_id"] == r["recording_id"]])
        for r in doc["recordings"]}
