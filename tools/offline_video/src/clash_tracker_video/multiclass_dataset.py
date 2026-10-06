"""Checked, local multiclass bindings and two separate immutable data locks.

Hashes bind existing producer metadata, not independent video authenticity or
human review. No source video is decoded, labelled, regenerated or overwritten.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
from hashlib import sha256
import os
from pathlib import Path

from .evidence_contract import EvidenceError, load_evidence
from .evidence_prepare import file_hash, load_indexes, safe_path
from .experiment_lock import MAX_LOCK_BYTES, canonical_bytes
from .multiclass_contract import (
    BoundMulticlass, CheckedLabelSnapshot, CheckedMediaSnapshot, MulticlassDraft,
    MulticlassLock, ScaleSnapshot, _validate_types, validate_multiclass_shape,
)
from .multiclass_readiness import (
    candidate_eligibility, development_scale_report, multiclass_readiness,
    scale_basis, scale_basis_sha256,
)
from .training_dataset import _disk_operation, dataset_artifact_path, private_artifact_path

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _disk(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
            raise EvidenceError("Cannot check local multiclass artifacts.") from exc
    return _disk_operation(checked)


def _canonical(value, key=None):
    if type(value) is dict:
        return {k: _canonical(v, k) for k, v in value.items()}
    if type(value) is list:
        rows = [_canonical(v) for v in value]
        return rows if key in ("intake", "history") else sorted(rows, key=canonical_bytes)
    return value


def _sha(value):
    return sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class _Bound:
    draft: MulticlassDraft
    media_snapshot: list[CheckedMediaSnapshot]
    label_snapshot: list[CheckedLabelSnapshot]
    file_hashes: dict[str, str]
    semantic_sha256: str
    data_root: Path


class _CheckedScale(dict):
    """JSON stays closed; checked origin is in-memory only, never a JSON field."""
    def __init__(self, envelope, path, root, raw_sha):
        super().__init__(deepcopy(envelope))
        self.path, self.data_root, self.file_sha256 = path, root, raw_sha


def _artifact(root, relative, expected, hashes):
    path = dataset_artifact_path(root, relative)
    if not path.is_file():
        raise EvidenceError("Missing declared multiclass artifact.")
    actual = file_hash(path)
    if expected is not None and actual != expected:
        raise EvidenceError("Changed declared multiclass artifact.")
    if relative in hashes and hashes[relative] != actual:
        raise EvidenceError("Multiclass artifact changed during binding.")
    hashes[relative] = actual
    return path


def _export_relative(root, index_path, relative):
    # Resolve every reference before the legacy loader; do not normalize away '..'.
    if (type(relative) is not str or not relative or "\\" in relative or ":" in relative
            or relative.startswith("/") or any(p in ("", ".", "..") for p in relative.split("/"))):
        raise EvidenceError("Unsafe multiclass export artifact reference.")
    path = index_path.parent / relative
    if not path.is_relative_to(root):
        raise EvidenceError("Multiclass export escapes the explicit container.")
    result = path.relative_to(root).as_posix()
    dataset_artifact_path(root, result)
    return result


def _read_media(draft, root, hashes):
    snapshots = []
    for record in draft["recordings"]:
        rid = record["recording_id"]
        _artifact(root, record["source_path"], record["source_sha256"], hashes)
        indexes, exports = [], {}
        for export in record["exports"]:
            index_path = _artifact(root, export["index_path"], export["index_sha256"], hashes)
            report_path = _artifact(root, export["report_path"], export["report_sha256"], hashes)
            document = load_evidence(index_path)
            report_relative = _export_relative(root, index_path, document.get("export_report"))
            if dataset_artifact_path(root, report_relative) != report_path:
                raise EvidenceError("Multiclass report/index pairing conflicts.")
            for relative in document.get("contact_pages", []):
                _artifact(root, _export_relative(root, index_path, relative), None, hashes)
            for row in document.get("frames", []):
                if type(row) is dict and row.get("status") == "success":
                    _artifact(root, _export_relative(root, index_path, row.get("image_path")), None, hashes)
            checked = load_indexes([index_path])
            if set(checked) != {rid}:
                raise EvidenceError("Multiclass export recording identity conflicts.")
            actual = checked[rid]["recording"]
            for key in ("recording_id", "source_sha256", "width", "height", "rotation_degrees", "time_base",
                        "origin_pts", "origin_time_base", "last_frame_seconds"):
                if actual[key] != record[key]:
                    raise EvidenceError("Multiclass source/index metadata conflicts.")
            exports[export["export_id"]] = {
                row["frame_id"]: (row, {_export_relative(root, index_path, alias) for alias in row["_aliases"]})
                for row in checked[rid]["frames"] if row["status"] == "success"}
            indexes.append(index_path)
        if indexes:
            # Per-run path bases above are preserved; full merge checks duplicate pixels.
            load_indexes(indexes)
        frames = [r for r in draft["frames"] if r["recording_id"] == rid]
        for frame in frames:
            _artifact(root, frame["image_path"], frame["image_sha256"], hashes)
            matched_path = False
            for eid in frame["export_ids"]:
                entry = exports.get(eid, {}).get(frame["frame_id"])
                if entry is None:
                    raise EvidenceError("Declared multiclass frame is absent from its export.")
                actual, aliases = entry
                if any(frame[k] != actual[k] for k in
                       ("raw_pts", "time_base", "timestamp_seconds", "image_width", "image_height")):
                    raise EvidenceError("Multiclass frame differs from actual export metadata.")
                matched_path |= frame["image_path"] in aliases
            if not matched_path:
                raise EvidenceError("Multiclass image path is not an actual frame alias.")
        snapshots.append({"recording": deepcopy(record), "frames": deepcopy(frames)})
    return _canonical(snapshots)


def _read_labels(draft, root, hashes):
    snapshots = []
    for source in draft["annotation_sources"]:
        document = load_evidence(_artifact(root, source["path"], source["sha256"], hashes))
        rows = [r for r in draft["annotations"] if r["annotation_source_id"] == source["annotation_source_id"]]
        expected = {"schema_version": 1, "annotation_source_id": source["annotation_source_id"], "annotations": rows}
        if canonical_bytes(_canonical(document)) != canonical_bytes(_canonical(expected)):
            raise EvidenceError("Multiclass sidecar differs from the complete declared label rows.")
        snapshots.append({"annotation_source": deepcopy(source), "annotations": deepcopy(rows)})
    return _canonical(snapshots)


@_disk
def bind_multiclass(draft: MulticlassDraft, data_root: Path) -> BoundMulticlass:
    """Read every declared dependency from one explicit repository container."""
    validate_multiclass_shape(draft)
    # Public resolver verifies the absolute container, links, Git ignore and tracking.
    if not isinstance(data_root, Path) or not data_root.is_absolute():
        raise EvidenceError("Explicit absolute multiclass data container required.")
    root = safe_path(data_root)
    if not root.is_dir() or not root.is_relative_to(PROJECT_ROOT):
        raise EvidenceError("Multiclass container must be within the selected repository.")
    canonical = _canonical(deepcopy(draft))
    hashes = {}
    media = _read_media(canonical, root, hashes)
    labels = _read_labels(canonical, root, hashes)
    for relative, expected in list(hashes.items()):
        _artifact(root, relative, expected, hashes)
    return _Bound(canonical, media, labels, hashes, _sha(canonical), root)


def _fresh(bound):
    if type(bound) is not _Bound:
        raise EvidenceError("Live checked multiclass binding required.")
    actual = bind_multiclass(bound.draft, bound.data_root)
    if (actual.semantic_sha256 != bound.semantic_sha256 or actual.file_hashes != bound.file_hashes
            or actual.media_snapshot != bound.media_snapshot or actual.label_snapshot != bound.label_snapshot):
        raise EvidenceError("Multiclass data changed after binding.")
    return actual


def _envelope(kind, draft, payload):
    result = {"kind": kind, "version": 1, "id": draft["dataset_id"],
              "created_at": draft["created_at"], "payload": payload}
    result["digest"] = _sha(result)
    return result


def _validate_envelope(envelope, schema):
    _validate_types(envelope, schema)
    if envelope["digest"] != _sha({k: v for k, v in envelope.items() if k != "digest"}):
        raise EvidenceError("Multiclass lock digest conflicts.")
    draft = envelope["payload"]["draft"]
    validate_multiclass_shape(draft)
    if envelope["id"] != draft["dataset_id"] or envelope["created_at"] != draft["created_at"]:
        raise EvidenceError("Multiclass lock identity/time conflicts.")


def _scale_envelope(bound):
    draft = scale_basis(bound.draft)
    candidates, scale = candidate_eligibility(draft), development_scale_report(draft)
    readiness = multiclass_readiness(draft)
    if (candidates["reasons"] or scale["size_coverage_status"] != "SIZE_COVERAGE_SUFFICIENT"
            or readiness["status"] in ("INVALID_DATASET", "PROVENANCE_INSUFFICIENT")):
        raise EvidenceError("Full multiclass candidate scale/provenance evidence is not ready.")
    return _envelope("multiclass_scale_snapshot", draft,
                     {"draft": draft, "draft_semantic_sha256": scale_basis_sha256(draft),
                      "candidate_report": candidates, "scale_report": scale})


def _write(envelope, directory):
    raw = canonical_bytes(envelope) + b"\n"
    if len(raw) > MAX_LOCK_BYTES:
        raise EvidenceError("Multiclass lock exceeds strict JSON size limit.")
    folder = private_artifact_path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    private_artifact_path(folder)
    version = envelope["payload"]["draft"]["freeze_version"]
    for existing in folder.iterdir():
        private_artifact_path(existing)
        if not existing.is_file():
            raise EvidenceError("Multiclass lock directory needs regular lock files only.")
        prior = load_evidence(existing)
        schema = ScaleSnapshot if prior.get("kind") == "multiclass_scale_snapshot" else MulticlassLock
        _validate_envelope(prior, schema)
        if (prior["kind"], prior["id"], prior["payload"]["draft"]["freeze_version"]) == (
                envelope["kind"], envelope["id"], version):
            raise EvidenceError("Multiclass kind/identity/freeze version already exists.")
    # IDs are untrusted strings, not filenames. Fixed hash namespace prevents traversal.
    namespace = sha256(envelope["id"].encode("utf-8")).hexdigest()
    path = private_artifact_path(folder / f"{namespace}.{envelope['kind']}.v{version}.json")
    fd, identity, completed = None, None, False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
        info = os.fstat(fd)
        identity = (info.st_dev, info.st_ino)
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            if written <= 0:
                raise OSError("Incomplete multiclass lock write")
            offset += written
        os.fsync(fd)
        os.close(fd)
        fd = None
        completed = True
        return path
    finally:
        try:
            if fd is not None:
                os.close(fd)
        finally:
            if identity is not None and not completed:
                try:
                    # Close errors must not bypass cleanup, nor permit deleting
                    # a different writer's replacement or a pre-existing file.
                    if path.exists() and not path.is_symlink() and not path.is_junction():
                        current = path.stat()
                        if (current.st_dev, current.st_ino) == identity:
                            path.unlink()
                except OSError as exc:
                    raise EvidenceError("Cannot clean owned incomplete multiclass lock.") from exc


@_disk
def freeze_scale_snapshot(bound: BoundMulticlass, directory: Path) -> ScaleSnapshot:
    fresh = _fresh(bound)
    if fresh.draft["selection"] is not None:
        raise EvidenceError("Scale snapshot must precede final class selection.")
    envelope = _scale_envelope(fresh)
    _validate_envelope(envelope, ScaleSnapshot)
    path = _write(envelope, directory)
    return _CheckedScale(envelope, path, fresh.data_root, file_hash(path))


@_disk
def load_scale_snapshot(path: Path, data_root: Path) -> ScaleSnapshot:
    path = private_artifact_path(path)
    raw_sha = file_hash(path)
    envelope = load_evidence(path)
    _validate_envelope(envelope, ScaleSnapshot)
    fresh = bind_multiclass(envelope["payload"]["draft"], data_root)
    if envelope != _scale_envelope(fresh) or file_hash(path) != raw_sha:
        raise EvidenceError("Scale snapshot differs from checked full candidate evidence.")
    return _CheckedScale(envelope, path, fresh.data_root, raw_sha)


def _checked_scale(snapshot, root):
    if type(snapshot) is not _CheckedScale or snapshot.data_root != root:
        raise EvidenceError("Prior checked scale snapshot from this container required.")
    actual = load_scale_snapshot(snapshot.path, root)
    if actual.file_sha256 != snapshot.file_sha256 or dict(actual) != dict(snapshot):
        raise EvidenceError("Prior scale snapshot changed after loading.")
    return dict(actual)


def _dataset_envelope(bound, snapshot):
    readiness = multiclass_readiness(bound.draft, snapshot)
    if not readiness["ready"]:
        raise EvidenceError("Selected multiclass data is not ready for immutable freeze.")
    return _envelope("multiclass_dataset_lock", bound.draft,
                     {"draft": deepcopy(bound.draft), "draft_semantic_sha256": bound.semantic_sha256,
                      "scale_snapshot": deepcopy(snapshot), "readiness": readiness,
                      "media_snapshot": deepcopy(bound.media_snapshot), "label_snapshot": deepcopy(bound.label_snapshot)})


@_disk
def freeze_multiclass_dataset(bound: BoundMulticlass, scale_snapshot: ScaleSnapshot, directory: Path) -> MulticlassLock:
    fresh = _fresh(bound)
    snapshot = _checked_scale(scale_snapshot, fresh.data_root)
    envelope = _dataset_envelope(fresh, snapshot)
    _validate_envelope(envelope, MulticlassLock)
    _write(envelope, directory)
    return deepcopy(envelope)


@_disk
def load_multiclass_dataset_lock(path: Path, data_root: Path) -> MulticlassLock:
    path = private_artifact_path(path)
    raw_sha = file_hash(path)
    envelope = load_evidence(path)
    _validate_envelope(envelope, MulticlassLock)
    fresh = bind_multiclass(envelope["payload"]["draft"], data_root)
    snapshot = envelope["payload"]["scale_snapshot"]
    _validate_envelope(snapshot, ScaleSnapshot)
    scale_bound = bind_multiclass(snapshot["payload"]["draft"], data_root)
    if snapshot != _scale_envelope(scale_bound) or envelope != _dataset_envelope(fresh, snapshot):
        raise EvidenceError("Dataset lock differs from checked scale/data evidence.")
    if file_hash(path) != raw_sha:
        raise EvidenceError("Dataset lock changed during loading.")
    return deepcopy(envelope)
