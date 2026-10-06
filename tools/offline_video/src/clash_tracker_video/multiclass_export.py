"""Checked metadata-only exports; no image transform, model or prediction.

Image references are relative to the explicit data container. Label references
in the manifest are relative to the new export directory. Already-rotated PNGs
retain identity geometry: no ROI crop, resize or double rotation is inferred.
"""
from __future__ import annotations

from collections import Counter
import os
from pathlib import Path

from .evidence_contract import EvidenceError
from .evidence_prepare import file_hash
from .experiment_lock import MAX_LOCK_BYTES, canonical_bytes
from .multiclass_contract import ExportManifest, _validate_types, backend_label_maps
from .multiclass_dataset import load_multiclass_dataset_lock
from .multiclass_readiness import frame_export_reasons
from .training_dataset import _disk_operation, dataset_artifact_path, private_artifact_path


def build_backend_label_map(selected_class_ids: list[str], backend: str) -> dict[str, int]:
    if backend not in ("yolox", "torchvision"):
        raise EvidenceError("Unsupported multiclass metadata backend.")
    return backend_label_maps(selected_class_ids)[backend]


def _identity(frame):
    return {"original_width": frame["image_width"], "original_height": frame["image_height"],
            "offset_x": 0, "offset_y": 0, "scale_x": 1, "scale_y": 1,
            "output_width": frame["image_width"], "output_height": frame["image_height"],
            "rotation_degrees": 0}


def _new_json(path, document, created):
    raw = canonical_bytes(document) + b"\n"
    if len(raw) > MAX_LOCK_BYTES:
        raise EvidenceError("Multiclass metadata exceeds strict JSON size limit.")
    private_artifact_path(path)
    with path.open("xb") as stream:
        info = os.fstat(stream.fileno())
        created.append((path, info.st_dev, info.st_ino))
        if stream.write(raw) != len(raw):
            raise OSError("Incomplete multiclass metadata write")
        stream.flush()
        os.fsync(stream.fileno())


def _cleanup(created):
    for path, device, inode in reversed(created):
        try:
            info = path.lstat()
            if not path.is_symlink() and not path.is_junction() and (info.st_dev, info.st_ino) == (device, inode):
                path.unlink()
        except FileNotFoundError:
            pass


@_disk_operation
def export_multiclass_dataset(lock_path: Path, *, data_root: Path, backend: str,
                              output_directory: Path) -> ExportManifest:
    """Reload a qualified immutable lock, then publish labels/manifest once.

Unsafe selected observations/coverage exclude their entire frame, never just
their boxes. Unknown coverage is not a negative image. Counts describe only
exported observations, not event detection or FP/min evaluation.
"""
    created = []
    try:
        if backend not in ("yolox", "torchvision"):
            raise EvidenceError("Unsupported multiclass metadata backend.")
        lock = load_multiclass_dataset_lock(lock_path, data_root)
        draft = lock["payload"]["draft"]
        if any(row["split"] == "prospective_test" for row in draft["recordings"]):
            raise EvidenceError("Prospective test material cannot enter Phase A export.")
        joint = build_backend_label_map(draft["selection"]["selected_class_ids"], backend)
        if joint != draft["backend_label_maps"][backend]:
            raise EvidenceError("Backend labels differ from the frozen joint map.")
        destination = dataset_artifact_path(data_root, output_directory.relative_to(data_root).as_posix())
        records = {r["recording_id"]: r for r in draft["recordings"]}
        groups = {r["appearance_group_id"]: r for r in draft["groups"]}
        selected = set(draft["selection"]["selected_class_ids"])
        frames, observations, images, coco_rows, torch_rows = [], [], [], [], []
        reasons = Counter()
        image_id = 0
        for frame in sorted(draft["frames"], key=lambda r: r["frame_id"]):
            why = frame_export_reasons(draft, frame["frame_id"])
            reasons.update(why)
            row = {"frame_id": frame["frame_id"], "recording_id": frame["recording_id"],
                   "split": records[frame["recording_id"]]["split"],
                   "status": "excluded" if frame["review_state"] == "excluded" else "pending",
                   "reasons": why, "original_sha256": frame["image_sha256"],
                   "image_path": None, "label_path": None, "label_sha256": None, "transform": None}
            if not why:
                image_id += 1
                row.update(status="exported", image_path=frame["image_path"], label_path="labels.json",
                           transform=_identity(frame))
                current = sorted((r for r in draft["annotations"] if r["frame_id"] == frame["frame_id"]
                                  and r["visual_class_id"] in selected), key=lambda r: r["annotation_id"])
                observations.extend(current)
                images.append({"id": image_id, "file_name": frame["image_path"],
                               "width": frame["image_width"], "height": frame["image_height"],
                               "frame_id": frame["frame_id"], "recording_id": frame["recording_id"],
                               "underlying_match_id": records[frame["recording_id"]]["underlying_match_id"],
                               "split": row["split"], "transform": row["transform"]})
                boxes, labels, metadata = [], [], []
                for annotation in current:
                    box = annotation["box"]
                    x, y = box["x"] * frame["image_width"], box["y"] * frame["image_height"]
                    w, h = box["width"] * frame["image_width"], box["height"] * frame["image_height"]
                    label = joint[f"{annotation['visual_class_id']}::{annotation['owner']}"]
                    group = groups.get(annotation["appearance_group_id"])
                    identity = {key: annotation[key] for key in ("annotation_id", "appearance_group_id",
                                "entity_occurrence_id", "visual_class_id", "owner", "observed_form")}
                    identity["causal_root_id"] = group["causal_root_id"] if group else None
                    coco_rows.append({"id": len(coco_rows) + 1, "image_id": image_id,
                                      "category_id": label, "bbox": [x, y, w, h],
                                      "area": w * h, "iscrowd": 0, **identity})
                    boxes.append([x, y, x + w, y + h])
                    labels.append(label)
                    metadata.append(identity)
                torch_rows.append({**images[-1], "boxes": boxes, "labels": labels, "observations": metadata})
            frames.append(row)
        exported = [f for f in frames if f["status"] == "exported"]
        mids = {records[f["recording_id"]]["underlying_match_id"] for f in exported}
        causes = {(records[r["recording_id"]]["underlying_match_id"], groups[r["appearance_group_id"]]["causal_root_id"])
                  for r in observations if r["appearance_group_id"] is not None}
        entities = {(records[r["recording_id"]]["underlying_match_id"], r["entity_occurrence_id"])
                    for r in observations if r["entity_occurrence_id"] is not None}
        manifest = {"dataset_digest": lock["digest"], "backend": backend, "joint_label_map": joint,
                    "frames": frames, "reasons": [{"reason": key, "count": count} for key, count in sorted(reasons.items())],
                    "counts": {"matches": len(mids), "groups": len(causes), "entities": len(entities),
                               "frames": len(exported), "boxes": len(observations)}}
        labels_document = ({"info": {"dataset_digest": lock["digest"], "geometry": "identity_original_rotated"},
                            "images": images, "annotations": coco_rows,
                            "categories": [{"id": value, "name": label} for label, value in joint.items()]}
                           if backend == "yolox" else
                           {"dataset_digest": lock["digest"], "geometry": "identity_original_rotated",
                            "joint_label_map": joint, "frames": torch_rows})
        destination.parent.mkdir(parents=True, exist_ok=True)
        private_artifact_path(destination)
        destination.mkdir()  # Exclusive directory: no prior artifact is overwritten.
        _new_json(destination / "labels.json", labels_document, created)
        label_sha = file_hash(destination / "labels.json")
        for row in exported:
            row["label_sha256"] = label_sha
        _validate_types(manifest, ExportManifest)
        if load_multiclass_dataset_lock(lock_path, data_root) != lock:
            raise EvidenceError("Multiclass lock changed during export.")
        _new_json(destination / "manifest.json", manifest, created)  # Commit point last.
        return manifest
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        try:
            _cleanup(created)
        except OSError as cleanup_error:
            raise EvidenceError("Cannot clean owned incomplete multiclass export.") from cleanup_error
        raise EvidenceError("Cannot export checked local multiclass metadata.") from exc
