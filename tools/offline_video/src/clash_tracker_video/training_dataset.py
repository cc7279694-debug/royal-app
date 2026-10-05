"""Checked local media binding and separate immutable training-dataset locks.

Python objects are not disk-integrity proof: bind, freeze and load re-read every
declared artifact through the unchanged legacy index/lock loaders. Human match
identity and exhaustive visual review remain attestations, not software proof.
"""
from __future__ import annotations

from copy import deepcopy
from contextvars import ContextVar
from functools import wraps
from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess

from .evidence_contract import EvidenceError, SCHEMAS, load_evidence, rational, seconds, valid_type
from .evidence_prepare import file_hash, frame_id, load_indexes, safe_path
from .experiment_contract import utc_time
from .experiment_lock import MAX_LOCK_BYTES, canonical_bytes, load_lock, validate_lock
from .training_dataset_contract import (ANNOTATION_SCHEMA, MEDIA_FIELDS, _relative_path,
                                        dataset_readiness, grouped_folds, validate_dataset_shape)


PROJECT_ROOT = Path(__file__).resolve().parents[4]
IDENTITY_FIELDS = {"schema_version", "dataset_id", "freeze_version", "created_at"}
PAYLOAD_FIELDS = {"draft", "derived", "folds", "index_snapshot", "development_lock_reference"}
IMAGE_FIELDS = {"frame_id", "raw_pts", "time_base", "timestamp_seconds", "image_path",
                "image_width", "image_height", "image_sha256", "rgba_sha256"}
_privacy_checks = ContextVar("dataset_privacy_checks", default=None)


def _disk_operation(function):
    @wraps(function)
    def checked(*args, **kwargs):
        if _privacy_checks.get() is not None:
            return function(*args, **kwargs)
        token = _privacy_checks.set(set())
        try:
            return function(*args, **kwargs)
        finally:
            _privacy_checks.reset(token)
    return checked


def _verify_privacy(paths):
    paths = list(dict.fromkeys(paths))
    relative = [path.relative_to(PROJECT_ROOT).as_posix() for path in paths]
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"],
                             input=b"\0".join(p.encode("utf-8") for p in relative) + b"\0",
                             cwd=PROJECT_ROOT, capture_output=True, check=False)
    if ignored.returncode != 0 or set(ignored.stdout.rstrip(b"\0").split(b"\0")) != {
            p.encode("utf-8") for p in relative}:
        raise EvidenceError("Data artifacts must be Git-ignored.")
    tracked = subprocess.run(["git", "ls-files", "-z", "--", *relative], cwd=PROJECT_ROOT,
                             capture_output=True, check=False)
    if tracked.returncode != 0 or tracked.stdout:
        raise EvidenceError("Data artifacts must not be tracked.")
    if _privacy_checks.get() is not None:
        _privacy_checks.get().update(paths)


class _CheckedIndexes(dict):
    """Only provenance for re-reading files; never an authority for its contents."""
    def __init__(self, snapshot, root, development_path, development_file_sha256):
        super().__init__(snapshot)
        self.root = root
        self.development_path = development_path
        self.development_file_sha256 = development_file_sha256


class _BoundPayload(dict):
    def __init__(self, payload, context, development):
        super().__init__(payload)
        self.context = context
        self.development = deepcopy(development)


def _object(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise EvidenceError("Invalid closed training dataset lock object.")


def _container(value):
    if not isinstance(value, Path) or not value.is_absolute():
        raise EvidenceError("Explicit absolute local data container required.")
    path = safe_path(value)
    if not path.is_dir() or not path.is_relative_to(PROJECT_ROOT):
        raise EvidenceError("Data container must stay within the selected repository.")
    return path


def _confined_path(value):
    try:
        if not isinstance(value, Path) or not value.is_absolute():
            raise EvidenceError("Explicit absolute private artifact path required.")
        path = safe_path(value)
        if not any(path.is_relative_to(PROJECT_ROOT / folder) and path != PROJECT_ROOT / folder
                   for folder in ("outputs", "local_data")):
            raise EvidenceError("Data artifacts must stay inside private outputs or local_data.")
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        raise EvidenceError("Cannot check private local artifact path.") from exc


def private_artifact_path(value: Path) -> Path:
    """Check an explicit absolute artifact/output path, without creating it."""
    try:
        path = _confined_path(value)
        if _privacy_checks.get() is None or path not in _privacy_checks.get():
            _verify_privacy([path])
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        raise EvidenceError("Cannot check private local artifact path.") from exc


def dataset_artifact_path(data_root: Path, relative: str) -> Path:
    """Resolve container-relative paths; repository root is a legal container."""
    try:
        root = _container(data_root)
        if not _relative_path(relative):
            raise EvidenceError("Invalid container-relative artifact path.")
        path = private_artifact_path(root / relative)
        if not path.is_relative_to(root):
            raise EvidenceError("Data artifact escapes the explicit container.")
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        raise EvidenceError("Cannot resolve private dataset artifact.") from exc


def validate_annotation_source(document: dict) -> None:
    """Closed additive sidecar; hash/whole-draft correspondence are bind duties."""
    _object(document, {"schema_version", "annotation_source_id", "unit_annotations"})
    if (type(document["schema_version"]) is not int or document["schema_version"] != 1
            or not valid_type(document["annotation_source_id"], "id")
            or type(document["unit_annotations"]) is not list):
        raise EvidenceError("Invalid unit annotation sidecar.")
    seen, boxes = set(), set()
    for annotation in document["unit_annotations"]:
        _object(annotation, ANNOTATION_SCHEMA)
        if (any(not valid_type(annotation[k], kind) for k, kind in ANNOTATION_SCHEMA.items())
                or annotation["annotation_source_id"] != document["annotation_source_id"]):
            raise EvidenceError("Invalid sidecar unit annotation or source identity.")
        box = (annotation["recording_id"], annotation["frame_id"],
               tuple(seconds(annotation["normalized_bbox"][k]) for k in ("x", "y", "width", "height")))
        if annotation["annotation_id"] in seen or box in boxes:
            raise EvidenceError("Duplicate sidecar annotation evidence.")
        seen.add(annotation["annotation_id"])
        boxes.add(box)


def _hashed_path(root, relative, expected):
    path = dataset_artifact_path(root, relative)
    if not path.is_file() or file_hash(path) != expected:
        raise EvidenceError("Missing or changed declared dataset artifact.")
    return path


def _read_bindings(draft, root):
    """Legacy loader verifies each report/PNG before merge; retain alias bases."""
    snapshot = {}
    for recording in draft["recordings"]:
        rid = recording["recording_id"]
        _hashed_path(root, recording["source_path"], recording["source_sha256"])
        paths, export_rows = [], []
        for export in recording["exports"]:
            index_path = _hashed_path(root, export["index_path"], export["index_sha256"])
            report_path = _hashed_path(root, export["report_path"], export["report_sha256"])
            original = load_evidence(index_path)
            relative_report = original.get("export_report")
            if (not _relative_path(relative_report)
                    or dataset_artifact_path(root, (index_path.parent / relative_report).relative_to(root).as_posix()) != report_path):
                raise EvidenceError("Declared report is not paired with its index.")
            # Check every external reference before giving it to the legacy loader.
            for relative in [*original.get("contact_pages", []),
                             *[f.get("image_path") for f in original.get("frames", [])
                               if type(f) is dict and f.get("status") == "success"]]:
                if not _relative_path(relative):
                    raise EvidenceError("Unsafe legacy index artifact reference.")
                path = _confined_path(index_path.parent / relative)
                if not path.is_relative_to(root):
                    raise EvidenceError("Legacy artifact escapes explicit container.")
            referenced_paths = [_confined_path(index_path.parent / relative)
                                for relative in [*original.get("contact_pages", []),
                                                 *[f["image_path"] for f in original.get("frames", [])
                                                   if type(f) is dict and f.get("status") == "success"]]]
            if referenced_paths:
                _verify_privacy(referenced_paths)
            checked = load_indexes([index_path])
            if set(checked) != {rid}:
                raise EvidenceError("Export recording identity conflicts.")
            paths.append(index_path)
            images = []
            for frame in checked[rid]["frames"]:
                if frame["status"] != "success":
                    continue
                relative = (index_path.parent / frame["image_path"]).relative_to(root).as_posix()
                path = dataset_artifact_path(root, relative)
                images.append({**{k: deepcopy(frame[k]) for k in IMAGE_FIELDS
                                  - {"image_path", "image_sha256", "rgba_sha256"}},
                               "image_path": relative, "image_sha256": file_hash(path),
                               "rgba_sha256": frame["_content_hash"]})
            export_rows.append({"export_id": export["export_id"], "images": images})
        merged = load_indexes(paths) if paths else {}
        snapshot[rid] = {"recording": deepcopy(merged[rid]["recording"]) if paths else None,
                         "exports": export_rows}
    for source in draft["annotation_sources"]:
        path = _hashed_path(root, source["path"], source["sha256"])
        document = load_evidence(path)
        validate_annotation_source(document)
        expected = {"schema_version": 1, "annotation_source_id": source["annotation_source_id"],
                    "unit_annotations": [a for a in draft["unit_annotations"]
                                         if a["annotation_source_id"] == source["annotation_source_id"]]}
        if canonical_bytes(document) != canonical_bytes(expected):
            raise EvidenceError("Annotation sidecar does not match declared unit labels.")
    _validate_snapshot(draft, snapshot)
    return snapshot


@_disk_operation
def load_dataset_indexes(draft: dict, data_root: Path, *, development_lock_path: Path) -> dict:
    """Create checked context with explicit private paths, reloaded on consumption."""
    try:
        validate_dataset_shape(draft)
        root = _container(data_root)
        relative_paths = [r["source_path"] for r in draft["recordings"]]
        relative_paths += [e[k] for r in draft["recordings"] for e in r["exports"]
                           for k in ("index_path", "report_path")]
        relative_paths += [f["image_path"] for f in draft["frames"]]
        relative_paths += [a["path"] for a in draft["annotation_sources"]]
        paths = [_confined_path(root / relative) for relative in relative_paths]
        paths.append(_confined_path(development_lock_path))
        if any(not path.is_relative_to(root) for path in paths):
            raise EvidenceError("Dataset artifact escapes the explicit data container.")
        _verify_privacy(paths)
        development_path = private_artifact_path(development_lock_path)
        if not development_path.is_relative_to(root):
            raise EvidenceError("Development Lock escapes the explicit data container.")
        development_file_sha256 = file_hash(development_path)
        development = load_lock(development_path)
        _development_reference(draft, development)
        snapshot = _read_bindings(draft, root)
        if file_hash(development_path) != development_file_sha256:
            raise EvidenceError("Development Lock artifact changed while checking data.")
        return _CheckedIndexes(snapshot, root, development_path, development_file_sha256)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, RecursionError) as exc:
        raise EvidenceError("Cannot check local training dataset bindings.") from exc


def _development_reference(draft, development):
    validated = validate_lock(development)
    if (validated["lock_type"] != "development" or validated["sha256"] != draft["development_lock_sha256"]
            or any(validated["payload"]["draft"]["selection"][k] != draft["target"][k]
                   for k in ("card_id", "form"))
            or utc_time(draft["created_at"]) <= utc_time(validated["created_at"])):
        raise EvidenceError("Training dataset Development Lock/target/time reference conflicts.")


def _validate_snapshot(draft, snapshot):
    _object(snapshot, [r["recording_id"] for r in draft["recordings"]])
    for record in draft["recordings"]:
        entry = snapshot[record["recording_id"]]
        _object(entry, {"recording", "exports"})
        if type(entry["exports"]) is not list or len(entry["exports"]) != len(record["exports"]):
            raise EvidenceError("Invalid dataset export snapshot.")
        if not record["exports"]:
            if entry["recording"] is not None:
                raise EvidenceError("Unavailable recording cannot invent an index snapshot.")
            continue
        _object(entry["recording"], SCHEMAS["recordings"])
        if (any(not valid_type(entry["recording"][k], kind) for k, kind in SCHEMAS["recordings"].items())
                or any(entry["recording"][k] != record[k] for k in MEDIA_FIELDS | {"recording_id", "source_sha256"})):
            raise EvidenceError("Recording metadata conflicts with checked indexes.")
        for declared, export in zip(record["exports"], entry["exports"]):
            _object(export, {"export_id", "images"})
            if export["export_id"] != declared["export_id"] or type(export["images"]) is not list:
                raise EvidenceError("Export snapshot identity conflicts.")
            seen = set()
            for image in export["images"]:
                _object(image, IMAGE_FIELDS)
                types = {"frame_id": "id", "raw_pts": "int", "time_base": "rational",
                         "timestamp_seconds": "seconds", "image_path": "png", "image_width": "positive_int",
                         "image_height": "positive_int", "image_sha256": "hash", "rgba_sha256": "hash"}
                if any(not valid_type(image[k], kind) for k, kind in types.items()) or not _relative_path(image["image_path"]):
                    raise EvidenceError("Invalid checked frame snapshot metadata.")
                base = rational(image["time_base"])
                normalized = image["raw_pts"] * base - record["origin_pts"] * rational(record["origin_time_base"])
                size = (record["height"], record["width"]) if record["rotation_degrees"] in (90, 270) else (record["width"], record["height"])
                if (image["frame_id"] in seen or image["frame_id"] != frame_id(record["recording_id"], image["raw_pts"], base)
                        or abs(normalized - seconds(image["timestamp_seconds"])) > seconds(0.000001)
                        or normalized < 0 or float(normalized) > record["last_frame_seconds"]
                        or (image["image_width"], image["image_height"]) != size):
                    raise EvidenceError("Checked frame identity/time/geometry conflicts.")
                seen.add(image["frame_id"])
    for frame in draft["frames"]:
        images = []
        for export_id in frame["export_ids"]:
            export = next(e for e in snapshot[frame["recording_id"]]["exports"] if e["export_id"] == export_id)
            image = next((i for i in export["images"] if i["frame_id"] == frame["frame_id"]), None)
            if image is None or any(image[k] != frame[k] for k in ("raw_pts", "time_base", "timestamp_seconds", "image_width", "image_height")):
                raise EvidenceError("Dataset frame is absent or conflicts with a declared export.")
            images.append(image)
        if (not any(i["image_path"] == frame["image_path"] and i["image_sha256"] == frame["image_sha256"] for i in images)
                or len({i["rgba_sha256"] for i in images}) != 1):
            raise EvidenceError("Dataset image/file/pixel binding conflicts.")


@_disk_operation
def bind_dataset(draft: dict, indexes: dict, development_lock: dict) -> dict:
    """Re-read disk and derive isolated payload; arbitrary snapshots are rejected."""
    if not isinstance(indexes, _CheckedIndexes):
        raise EvidenceError("Checked dataset disk context required.")
    current = load_dataset_indexes(draft, indexes.root, development_lock_path=indexes.development_path)
    if current.development_file_sha256 != indexes.development_file_sha256:
        raise EvidenceError("Immutable Development Lock artifact changed since context loading.")
    _development_reference(draft, development_lock)
    actual_development = load_lock(current.development_path)
    if canonical_bytes(actual_development) != canonical_bytes(development_lock):
        raise EvidenceError("Actual Development Lock differs from the supplied prerequisite.")
    payload = {"draft": deepcopy(draft), "derived": dataset_readiness(draft), "folds": grouped_folds(draft),
               "index_snapshot": deepcopy(dict(current)),
               "development_lock_reference": {"path": current.development_path.relative_to(current.root).as_posix(),
                                              "file_sha256": current.development_file_sha256}}
    return _BoundPayload(payload, current, development_lock)


def _payload(payload):
    # Dict subclasses carry ephemeral checked context outside canonical JSON.
    _object(dict(payload) if isinstance(payload, _BoundPayload) else payload, PAYLOAD_FIELDS)
    draft = payload["draft"]
    validate_dataset_shape(draft)
    if (canonical_bytes(payload["derived"]) != canonical_bytes(dataset_readiness(draft))
            or canonical_bytes(payload["folds"]) != canonical_bytes(grouped_folds(draft))):
        raise EvidenceError("Editable dataset readiness or fold assignment conflicts.")
    _validate_snapshot(draft, payload["index_snapshot"])
    reference = payload["development_lock_reference"]
    _object(reference, {"path", "file_sha256"})
    if not _relative_path(reference["path"]) or not reference["path"].endswith(".json") or not valid_type(reference["file_sha256"], "hash"):
        raise EvidenceError("Invalid immutable Development Lock artifact reference.")
    identifier = draft["dataset_id"]
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", identifier) or identifier.upper() in {
            "CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise EvidenceError("Unsafe dataset lock identifier.")


def make_dataset_lock(payload: dict) -> dict:
    """Pure canonical envelope; freezing separately requires a live disk context."""
    try:
        _payload(payload)
        envelope = {k: deepcopy(payload["draft"][k]) for k in IDENTITY_FIELDS}
        envelope.update(lock_type="training_dataset", payload=deepcopy(dict(payload)))
        envelope["sha256"] = sha256(canonical_bytes(envelope)).hexdigest()
        return envelope
    except (TypeError, ValueError, KeyError, AttributeError, StopIteration, RecursionError) as exc:
        raise EvidenceError("Invalid training dataset lock payload.") from exc


def validate_dataset_lock(lock: dict, development_lock: dict) -> None:
    """Pure digest/contract/prerequisite validation, never a disk proof."""
    try:
        _object(lock, IDENTITY_FIELDS | {"lock_type", "payload", "sha256"})
        expected = make_dataset_lock(lock["payload"])
        if canonical_bytes(lock) != canonical_bytes(expected):
            raise EvidenceError("Training dataset digest or envelope identity conflicts.")
        _development_reference(lock["payload"]["draft"], development_lock)
        if not lock["payload"]["derived"]["training_data_ready"]:
            raise EvidenceError("Training dataset is not ready for an immutable freeze.")
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError) as exc:
        raise EvidenceError("Invalid training dataset lock contract.") from exc


@_disk_operation
def freeze_dataset(payload: dict, directory: Path) -> dict:
    """Rebind, reject renamed versions, exclusively write and clean failed writes."""
    if not isinstance(payload, _BoundPayload):
        raise EvidenceError("Freezing requires live checked dataset context.")
    fresh = bind_dataset(payload["draft"], payload.context, payload.development)
    if canonical_bytes(dict(fresh)) != canonical_bytes(dict(payload)):
        raise EvidenceError("Dataset changed since binding; prepare a fresh payload.")
    envelope = make_dataset_lock(fresh)
    validate_dataset_lock(envelope, payload.development)
    raw = canonical_bytes(envelope) + b"\n"
    if len(raw) > MAX_LOCK_BYTES:
        raise EvidenceError("Training dataset lock exceeds strict JSON size limit.")
    folder = private_artifact_path(directory)
    destination = None
    fd = None
    created = False
    try:
        folder.mkdir(parents=True, exist_ok=True)
        private_artifact_path(folder)
        for existing in folder.iterdir():
            private_artifact_path(existing)
            if not existing.is_file():
                raise EvidenceError("Dataset lock directory requires regular lock files only.")
            prior = load_evidence(existing)
            # Check contracts/digests before duplicate identity regardless of filename.
            validate_dataset_lock(prior, payload.development)
            if all(prior[k] == envelope[k] for k in ("dataset_id", "lock_type", "freeze_version")):
                raise EvidenceError("Dataset/type/freeze version already exists.")
        destination = private_artifact_path(folder / f"{envelope['dataset_id']}.training_dataset.v{envelope['freeze_version']}.json")
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
        created = True
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            if written <= 0:
                raise OSError("Incomplete dataset lock write")
            offset += written
        os.fsync(fd)
        os.close(fd)
        fd = None
        return envelope
    except OSError as exc:
        raise EvidenceError("Cannot exclusively write immutable training dataset lock.") from exc
    finally:
        if fd is not None:
            try:
                os.close(fd)
            finally:
                if created and destination is not None:
                    destination.unlink(missing_ok=True)


@_disk_operation
def load_dataset_lock(path: Path, development_lock: dict, indexes: dict) -> dict:
    """Validate strict lock and rederive actual external bindings, never snapshots."""
    if not isinstance(indexes, _CheckedIndexes):
        raise EvidenceError("Loading requires checked dataset disk context.")
    try:
        lock = load_evidence(private_artifact_path(path))
        validate_dataset_lock(lock, development_lock)
        reference = lock["payload"]["development_lock_reference"]
        actual_path = _hashed_path(indexes.root, reference["path"], reference["file_sha256"])
        if actual_path != indexes.development_path:
            raise EvidenceError("Dataset context does not reference the frozen Development Lock.")
        actual = bind_dataset(lock["payload"]["draft"], indexes, development_lock)
        if canonical_bytes(dict(actual)) != canonical_bytes(lock["payload"]):
            raise EvidenceError("Loaded dataset external bindings differ from the frozen payload.")
        return deepcopy(lock)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, RecursionError) as exc:
        raise EvidenceError("Cannot load checked local training dataset lock.") from exc
