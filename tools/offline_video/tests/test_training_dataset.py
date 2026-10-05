"""Synthetic disk bindings and exclusive dataset versions; no gameplay data."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from importlib import import_module
import json
import os
from pathlib import Path
import subprocess

import av
import pytest
from PIL import Image

from conftest import make_video
from clash_tracker_video import evidence_prepare as ep, experiment_lock as legacy
from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.training_dataset_contract import validate_dataset_shape
from experiment_fixtures import development_fixture
from training_dataset_fixtures import dataset_fixture


def api():
    try:
        return import_module("clash_tracker_video.training_dataset")
    except ModuleNotFoundError:
        pytest.fail("Checked training dataset bindings are not implemented")


def test_required_checked_dataset_api_exists():
    module = api()
    for name in ("load_dataset_indexes", "bind_dataset", "make_dataset_lock",
                 "validate_dataset_lock", "freeze_dataset", "load_dataset_lock"):
        assert callable(getattr(module, name, None)), name


def write_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(legacy.canonical_bytes(document) + b"\n")


def sidecar(draft):
    return {"schema_version": 1, "annotation_source_id": "revision_1",
            "unit_annotations": deepcopy(draft["unit_annotations"])}


def resign(lock):
    lock["sha256"] = sha256(legacy.canonical_bytes(
        {k: v for k, v in lock.items() if k != "sha256"})).hexdigest()
    return lock


@pytest.fixture
def disk(tmp_path, monkeypatch):
    module = api()
    for owner in (module, ep, legacy):
        monkeypatch.setattr(owner, "PROJECT_ROOT", tmp_path)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("/outputs/\n/local_data/\n", encoding="utf-8")
    old, old_indexes = development_fixture()
    old["selection"]["card_id"] = "minions"
    old["candidates"][0]["card_id"] = "minions"
    old["candidates"][0]["evidence"]["target_card"]["card_id"] = "minions"
    for play in old["candidates"][0]["evidence"]["occurrences"]:
        play["card_id"] = "minions"
    development = legacy.make_development_lock(old, old_indexes)
    old_path = tmp_path / "outputs/old-lock/development.json"
    write_json(old_path, development)
    draft = dataset_fixture(absent=True)
    # One complete positive frame per actual deployment is sufficient, not 4.
    keep = {(f["recording_id"], f["frame_id"]) for f in draft["frames"]
            if f["frame_id"].endswith("frame_1")}
    draft["frames"] = [f for f in draft["frames"] if (f["recording_id"], f["frame_id"]) in keep]
    draft["unit_annotations"] = [a for a in draft["unit_annotations"]
                                 if (a["recording_id"], a["frame_id"]) in keep]
    draft["development_lock_sha256"] = development["sha256"]
    for n, recording in enumerate(draft["recordings"], 1):
        rid = recording["recording_id"]
        source = make_video(tmp_path / f"local_data/{rid}.mp4",
                            pts=(n * 1000, n * 1000 + 10200, n * 1000 + 30200,
                                 n * 1000 + 100000))
        run = tmp_path / f"outputs/{rid}"
        index = ep.prepare_evidence(source, run, recording_id=rid, times=[10.2, 30.2])
        recording["source_path"] = source.relative_to(tmp_path).as_posix()
        for key in ("source_sha256", "width", "height", "rotation_degrees", "time_base",
                    "origin_pts", "origin_time_base", "last_frame_seconds"):
            recording[key] = deepcopy(index["recording"][key])
        recording["complete_segment"]["end_seconds"] = recording["last_frame_seconds"]
        recording["exports"] = [{"export_id": "export_1",
            "index_path": f"outputs/{rid}/index.json", "index_sha256": ep.file_hash(run / "index.json"),
            "report_path": f"outputs/{rid}/exports/report.json",
            "report_sha256": ep.file_hash(run / "exports/report.json")}]
        for frame, checked in zip((f for f in draft["frames"] if f["recording_id"] == rid), index["frames"]):
            prior_id = frame["frame_id"]
            for key in ("frame_id", "timestamp_seconds", "raw_pts", "time_base", "image_width", "image_height"):
                frame[key] = deepcopy(checked[key])
            frame["image_path"] = (run / checked["image_path"]).relative_to(tmp_path).as_posix()
            frame["image_sha256"] = ep.file_hash(tmp_path / frame["image_path"])
            for annotation in draft["unit_annotations"]:
                if annotation["recording_id"] == rid and annotation["frame_id"] == prior_id:
                    annotation["frame_id"] = frame["frame_id"]
    annotation = tmp_path / "outputs/annotations/units.v1.json"
    write_json(annotation, sidecar(draft))
    draft["annotation_sources"][0].update(path=annotation.relative_to(tmp_path).as_posix(),
                                         sha256=ep.file_hash(annotation))
    return tmp_path, draft, development, old_path


def context(disk, draft=None):
    root, original, _, old_path = disk
    return api().load_dataset_indexes(draft or original, root, development_lock_path=old_path)


def bound(disk, draft=None):
    current = draft or disk[1]
    return api().bind_dataset(current, context(disk, current), disk[2])


def test_checked_payload_derives_readiness_and_fold_ownership_without_mutating_inputs(disk):
    before = deepcopy(disk[1])
    payload = bound(disk)
    assert payload["derived"]["counts"]["confirmed_target_deployments"] == 8
    assert payload["derived"]["counts"]["target_positive_matches"] == 4
    assert payload["derived"]["counts"]["training_images"] == 8
    assert payload["derived"]["counts"]["training_unit_boxes"] == 24
    assert payload["derived"]["confirmed_absent_seconds"] == 32
    assert len(payload["folds"]) == 4
    assert payload["folds"][0]["validation_match_ids"] == ["match_1"]
    assert disk[1] == before


@pytest.mark.parametrize("last_tick,last_seconds,final_request", [
    (5345, 178.16666666666666, 178.1),
    (5348, 178.26666666666668, 178.2),
], ids=["rounded_down", "rounded_up"])
def test_checked_binding_accepts_native_30hz_final_export_with_nonzero_origin(
        disk, last_tick, last_seconds, final_request):
    root, draft, _, _ = disk
    recording = draft["recordings"][0]
    rid = recording["recording_id"]
    source = root / "local_data/thirty.mp4"
    with av.open(str(source), "w") as container:
        stream = container.add_stream("libx264", rate=30)
        stream.width, stream.height = 64, 48
        stream.pix_fmt = "yuv420p"
        stream.time_base = stream.codec_context.time_base = Fraction(1, 30)
        stream.options = {"bf": "0", "crf": "0"}
        for pts in (30, 336, 936, 30 + last_tick):
            frame = av.VideoFrame.from_image(Image.new("RGB", (64, 48), "red"))
            frame.pts, frame.time_base = pts, Fraction(1, 30)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    run = root / "outputs/thirty"
    index = ep.prepare_evidence(source, run, recording_id=rid, times=[10.2, 30.2, final_request])
    assert index["recording"]["last_frame_seconds"] == last_seconds
    origin_base = index["recording"]["origin_time_base"]
    assert index["recording"]["origin_pts"] * Fraction(
        origin_base["numerator"], origin_base["denominator"]) == 1
    final = index["frames"][-1]
    assert final["status"] == "success"
    assert final["timestamp_seconds"] == last_seconds
    assert len(ep.load_indexes([run / "index.json"])[rid]["frames"]) == 3
    recording["source_path"] = source.relative_to(root).as_posix()
    for key in ("source_sha256", "width", "height", "rotation_degrees", "time_base",
                "origin_pts", "origin_time_base", "last_frame_seconds"):
        recording[key] = deepcopy(index["recording"][key])
    recording["complete_segment"]["end_seconds"] = last_seconds
    recording["exports"] = [{"export_id": "export_1", "index_path": "outputs/thirty/index.json",
        "index_sha256": ep.file_hash(run / "index.json"),
        "report_path": "outputs/thirty/exports/report.json",
        "report_sha256": ep.file_hash(run / "exports/report.json")}]
    for frame, checked in zip((f for f in draft["frames"] if f["recording_id"] == rid), index["frames"]):
        old_id = frame["frame_id"]
        for key in ("frame_id", "timestamp_seconds", "raw_pts", "time_base", "image_width", "image_height"):
            frame[key] = deepcopy(checked[key])
        frame["image_path"] = (run / checked["image_path"]).relative_to(root).as_posix()
        frame["image_sha256"] = ep.file_hash(root / frame["image_path"])
        for annotation in draft["unit_annotations"]:
            if annotation["recording_id"] == rid and annotation["frame_id"] == old_id:
                annotation["frame_id"] = frame["frame_id"]
    annotation_path = root / draft["annotation_sources"][0]["path"]
    write_json(annotation_path, sidecar(draft))
    draft["annotation_sources"][0]["sha256"] = ep.file_hash(annotation_path)
    payload = bound(disk)
    images = payload["index_snapshot"][rid]["exports"][0]["images"]
    assert images[-1]["frame_id"] == final["frame_id"]
    assert images[-1]["timestamp_seconds"] == last_seconds
    assert payload["derived"]["counts"]["confirmed_target_deployments"] == 8
    api().make_dataset_lock(payload)


def test_snapshot_rejects_one_pts_tick_beyond_last_without_millisecond_epsilon(disk):
    payload = bound(disk)
    recording = payload["draft"]["recordings"][0]
    images = payload["index_snapshot"][recording["recording_id"]]["exports"][0]["images"]
    beyond = deepcopy(images[0])
    base = Fraction(beyond["time_base"]["numerator"], beyond["time_base"]["denominator"])
    beyond["raw_pts"] = recording["origin_pts"] + int(Fraction(100) / base) + 1
    beyond["frame_id"] = ep.frame_id(recording["recording_id"], beyond["raw_pts"], base)
    beyond["timestamp_seconds"] = float(Fraction(100) + base)
    images.append(beyond)
    with pytest.raises(EvidenceError, match="Checked frame identity/time/geometry conflicts"):
        api().make_dataset_lock(payload)


def test_extreme_integer_snapshot_pts_rejects_with_path_free_evidence_error(disk):
    payload = bound(disk)
    recording = payload["draft"]["recordings"][0]
    image = payload["index_snapshot"][recording["recording_id"]]["exports"][0]["images"][0]
    image["raw_pts"] = 10 ** 400
    base = Fraction(image["time_base"]["numerator"], image["time_base"]["denominator"])
    image["frame_id"] = ep.frame_id(recording["recording_id"], image["raw_pts"], base)
    with pytest.raises(EvidenceError) as caught:
        api().make_dataset_lock(payload)
    assert str(disk[0]) not in str(caught.value)


def test_canonical_freeze_load_recomputes_digest_and_retains_old_lock(disk):
    payload = bound(disk)
    old_bytes = disk[3].read_bytes()
    lock = api().make_dataset_lock(payload)
    assert lock["lock_type"] == "training_dataset"
    assert legacy.canonical_bytes(lock) == legacy.canonical_bytes(api().make_dataset_lock(bound(disk)))
    directory = disk[0] / "outputs/dataset-locks"
    assert api().freeze_dataset(payload, directory) == lock
    path = directory / "synthetic_minion_units.training_dataset.v1.json"
    assert path.read_bytes() == legacy.canonical_bytes(lock) + b"\n"
    assert api().load_dataset_lock(path, disk[2], context(disk)) == lock
    assert disk[3].read_bytes() == old_bytes


@pytest.mark.parametrize("mutation", ["source", "report", "index", "pixels", "annotation", "old_lock"])
def test_stale_checked_context_never_proves_unchanged_external_files(disk, mutation):
    checked = context(disk)
    root, draft, development, old_path = disk
    paths = {"source": draft["recordings"][0]["source_path"],
             "report": draft["recordings"][0]["exports"][0]["report_path"],
             "index": draft["recordings"][0]["exports"][0]["index_path"],
             "pixels": draft["frames"][0]["image_path"],
             "annotation": draft["annotation_sources"][0]["path"]}
    path = old_path if mutation == "old_lock" else root / paths[mutation]
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(EvidenceError):
        api().bind_dataset(draft, checked, development)


def test_bind_rejects_plain_stored_snapshot(disk):
    with pytest.raises(EvidenceError):
        api().bind_dataset(disk[1], dict(context(disk)), disk[2])


def test_checked_old_lock_reference_rejects_byte_changes_even_with_same_semantic_digest(disk):
    checked = context(disk)
    disk[3].write_bytes(disk[3].read_bytes() + b"\n")
    with pytest.raises(EvidenceError):
        api().bind_dataset(disk[1], checked, disk[2])


@pytest.mark.parametrize("field,value", [("raw_pts", 999), ("image_width", 63),
                                        ("frame_id", "nonexistent"), ("image_sha256", "f" * 64)])
def test_declared_frame_metadata_must_match_actual_index(disk, field, value):
    draft = deepcopy(disk[1])
    draft["frames"][0][field] = value
    if field == "raw_pts":
        # Keep the draft's own PTS contract valid; only the actual export disagrees.
        frame = draft["frames"][0]
        frame["raw_pts"] = disk[1]["frames"][0]["raw_pts"] + 1
        base = frame["time_base"]
        frame["timestamp_seconds"] = disk[1]["frames"][0]["timestamp_seconds"] + base["numerator"] / base["denominator"]
    if field == "image_width":
        draft["recordings"][0]["width"] = value
        for frame in draft["frames"]:
            if frame["recording_id"] == "recording_1":
                frame["image_width"] = value
    if field == "frame_id":
        for annotation in draft["unit_annotations"][:3]:
            annotation["frame_id"] = value
        write_json(disk[0] / draft["annotation_sources"][0]["path"], sidecar(draft))
        draft["annotation_sources"][0]["sha256"] = ep.file_hash(disk[0] / draft["annotation_sources"][0]["path"])
    validate_dataset_shape(draft)
    with pytest.raises(EvidenceError):
        bound(disk, draft)


def test_hash_matching_annotation_sidecar_still_needs_same_semantic_rows(disk):
    draft = deepcopy(disk[1])
    path = disk[0] / draft["annotation_sources"][0]["path"]
    labels = sidecar(draft)
    labels["unit_annotations"][0]["normalized_bbox"]["width"] = 0.06
    write_json(path, labels)
    draft["annotation_sources"][0]["sha256"] = ep.file_hash(path)
    with pytest.raises(EvidenceError):
        bound(disk, draft)


def test_multiple_exports_resolve_relative_png_aliases_and_check_each_declared_export(disk):
    draft = deepcopy(disk[1])
    recording = draft["recordings"][0]
    rid = recording["recording_id"]
    run = disk[0] / "outputs/additional"
    ep.prepare_evidence(disk[0] / recording["source_path"], run, recording_id=rid, times=[10.2])
    recording["exports"].append({"export_id": "export_2", "index_path": "outputs/additional/index.json",
        "index_sha256": ep.file_hash(run / "index.json"),
        "report_path": "outputs/additional/exports/report.json",
        "report_sha256": ep.file_hash(run / "exports/report.json")})
    draft["frames"][0]["export_ids"].append("export_2")
    assert bound(disk, draft)["derived"]["training_data_ready"] is True
    draft["frames"][1]["export_ids"].append("export_2")
    with pytest.raises(EvidenceError):
        bound(disk, draft)


def test_changed_development_reference_and_resigned_derived_or_split_claims_reject(disk):
    lock = api().make_dataset_lock(bound(disk))
    for key in ("reference", "counts", "folds", "snapshot"):
        altered = deepcopy(lock)
        if key == "reference":
            altered["payload"]["draft"]["development_lock_sha256"] = "a" * 64
        elif key == "counts":
            altered["payload"]["derived"]["counts"]["confirmed_target_deployments"] = 100
        elif key == "folds":
            altered["payload"]["folds"][0]["train_match_ids"].append("match_1")
        else:
            altered["payload"]["index_snapshot"]["recording_1"]["recording"]["width"] = 1
        with pytest.raises(EvidenceError):
            api().validate_dataset_lock(resign(altered), disk[2])


@pytest.mark.parametrize("kind", ["box", "event", "unknown", "absent", "intake", "form", "time", "version"])
def test_changed_semantics_change_canonical_digest(disk, kind):
    baseline = api().make_dataset_lock(bound(disk))["sha256"]
    draft = deepcopy(disk[1])
    if kind == "box":
        draft["unit_annotations"][0]["normalized_bbox"]["width"] = 0.06
    elif kind == "event":
        draft["deployments"][0]["deployment_id"] = "renamed_event"
        for annotation in draft["unit_annotations"][:3]:
            annotation["deployment_id"] = "renamed_event"
    elif kind == "unknown":
        draft["unknown_intervals"].append({"interval_id": "new_unknown", "recording_id": "recording_1",
            "start_seconds": 90, "end_seconds": 100, "reason": "Synthetic terminal uncertainty"})
    elif kind == "absent":
        draft["confirmed_absent_intervals"][1]["end_seconds"] = 9
    elif kind == "intake":
        draft["intake"] = draft["intake"][1:] + draft["intake"][:1]
    elif kind == "form":
        # A retained non-target unknown visual positive does not become negative.
        item = deepcopy(draft["unit_annotations"][0])
        item.update(annotation_id="other_unit", deployment_id=None, owner="unknown", form="unknown")
        item["normalized_bbox"]["y"] = 0.5
        draft["unit_annotations"].append(item)
    elif kind == "time":
        draft["created_at"] = "2026-10-05T02:00:00Z"
    else:
        draft["freeze_version"] = 2
    write_json(disk[0] / draft["annotation_sources"][0]["path"], sidecar(draft))
    draft["annotation_sources"][0]["sha256"] = ep.file_hash(disk[0] / draft["annotation_sources"][0]["path"])
    assert api().make_dataset_lock(bound(disk, draft))["sha256"] != baseline


def test_fixed_target_mutation_rejects_instead_of_producing_invalid_lock(disk):
    draft = deepcopy(disk[1])
    draft["target"]["form"] = "evolved"
    with pytest.raises(EvidenceError):
        bound(disk, draft)


def test_freeze_requires_ready_data_and_live_context_but_allows_missing_evaluation_coverage(disk):
    draft = deepcopy(disk[1])
    draft["confirmed_absent_intervals"] = []
    payload = bound(disk, draft)
    assert payload["derived"]["evaluation_ready"] is False
    api().freeze_dataset(payload, disk[0] / "outputs/coverage-not-ready")
    with pytest.raises(EvidenceError):
        api().freeze_dataset(dict(payload), disk[0] / "outputs/unchecked")
    draft["unit_annotations"][0]["review_status"] = "pending"
    draft["frames"][0]["review_status"] = "pending"
    write_json(disk[0] / draft["annotation_sources"][0]["path"], sidecar(draft))
    draft["annotation_sources"][0]["sha256"] = ep.file_hash(disk[0] / draft["annotation_sources"][0]["path"])
    payload = bound(disk, draft)
    with pytest.raises(EvidenceError):
        api().freeze_dataset(payload, disk[0] / "outputs/not-ready")


def test_renamed_version_and_preexisting_bytes_survive_duplicate_freeze(disk):
    directory = disk[0] / "outputs/locks"
    payload = bound(disk)
    api().freeze_dataset(payload, directory)
    original = next(directory.iterdir())
    raw = original.read_bytes()
    renamed = directory / "renamed-copy.json"
    original.rename(renamed)
    with pytest.raises(EvidenceError):
        api().freeze_dataset(payload, directory)
    assert renamed.read_bytes() == raw
    draft = deepcopy(disk[1])
    draft["freeze_version"] = 2
    assert api().freeze_dataset(bound(disk, draft), directory)["freeze_version"] == 2


def test_partial_write_failure_removes_only_new_incomplete_destination(disk, monkeypatch):
    directory = disk[0] / "outputs/locks"
    payload = bound(disk)
    api().freeze_dataset(payload, directory)
    original = next(directory.iterdir())
    raw = original.read_bytes()
    draft = deepcopy(disk[1])
    draft["freeze_version"] = 2
    second = bound(disk, draft)
    real_write = os.write
    count = 0
    def broken_write(fd, data):
        nonlocal count
        count += 1
        if count == 1:
            return real_write(fd, data[:10])
        raise OSError("synthetic write failure")
    monkeypatch.setattr(api().os, "write", broken_write)
    with pytest.raises(EvidenceError):
        api().freeze_dataset(second, directory)
    assert list(directory.iterdir()) == [original]
    assert original.read_bytes() == raw


@pytest.mark.parametrize("location", ["outside.json", "outputs/../escaped.json", "outputs//invalid.json"])
def test_path_base_is_explicit_and_each_artifact_remains_private(disk, location):
    with pytest.raises(EvidenceError):
        api().dataset_artifact_path(disk[0], location)
    with pytest.raises(EvidenceError):
        api().load_dataset_indexes(disk[1], Path("."), development_lock_path=disk[3])


def test_unignored_private_folder_is_refused(disk):
    (disk[0] / ".gitignore").write_text("", encoding="utf-8")
    with pytest.raises(EvidenceError):
        context(disk)


def test_junction_escape_cannot_bind_or_write_locks(disk, tmp_path):
    if os.name != "nt":
        pytest.skip("Windows junction behavior")
    outside = tmp_path / "external"
    outside.mkdir()
    junction = disk[0] / "outputs/junction"
    subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
                   check=True, capture_output=True)
    try:
        with pytest.raises(EvidenceError):
            api().dataset_artifact_path(disk[0], "outputs/junction/image.png")
        with pytest.raises(EvidenceError):
            api().freeze_dataset(bound(disk), junction)
        assert list(outside.iterdir()) == []
    finally:
        junction.rmdir()


def test_symlink_escape_cannot_bind_or_write_locks(disk):
    link = disk[0] / "outputs/link"
    try:
        link.symlink_to(disk[0] / "local_data", target_is_directory=True)
    except OSError:
        pytest.skip("Windows symlink privilege unavailable")
    with pytest.raises(EvidenceError):
        api().dataset_artifact_path(disk[0], "outputs/link/recording_1.mp4")


@pytest.mark.parametrize("raw", [b'{"schema_version":1,"schema_version":1}',
                                 b'{"bad":NaN}', b'{"bad":1e9999}', b'[]',
                                 b' ' * (16 * 1024 * 1024 + 1)],
                         ids=["duplicate_key", "nonfinite", "overflow", "array_root", "oversized"])
def test_strict_loaded_json_is_sanitized(disk, raw):
    path = disk[0] / "outputs/malformed.json"
    path.write_bytes(raw)
    with pytest.raises(EvidenceError) as caught:
        api().load_dataset_lock(path, disk[2], context(disk))
    assert str(disk[0]) not in str(caught.value)


def test_loaded_lock_rechecks_pixels_even_when_caller_retains_old_context(disk):
    payload = bound(disk)
    directory = disk[0] / "outputs/locks"
    api().freeze_dataset(payload, directory)
    checked = context(disk)
    Image.new("RGB", (64, 48), "black").save(disk[0] / disk[1]["frames"][0]["image_path"])
    with pytest.raises(EvidenceError):
        api().load_dataset_lock(next(directory.iterdir()), disk[2], checked)
