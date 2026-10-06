"""Metadata-only backend exports from checked synthetic immutable data."""
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
import json
from fractions import Fraction
from pathlib import Path

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.experiment_lock import canonical_bytes
from clash_tracker_video import multiclass_dataset as checked
from clash_tracker_video.evidence_prepare import frame_id
from clash_tracker_video.evidence_prepare import file_hash
from conftest import make_video
from multiclass_fixtures import multiclass_fixture, multiclass_disk_fixture
from test_multiclass_dataset import disk, selection, scale


def api():
    try:
        return import_module("clash_tracker_video.multiclass_export")
    except ModuleNotFoundError:
        pytest.fail("Checked metadata-only multiclass export is not implemented")


def frozen(disk):
    root, draft = disk
    prior = scale(disk)
    checked.freeze_multiclass_dataset(checked.bind_multiclass(selection(draft, prior), root),
                                     prior, root / "outputs/final")
    return next((root / "outputs/final").iterdir())


def test_yolox_zero_is_foreground_torchvision_zero_is_background():
    module = api()
    ids = ["unit.speck", "building.anchor", "unit.guard"]
    assert module.build_backend_label_map(ids, "yolox") == {
        "building.anchor::opponent": 0, "building.anchor::own": 1,
        "unit.guard::opponent": 2, "unit.guard::own": 3,
        "unit.speck::opponent": 4, "unit.speck::own": 5}
    assert module.build_backend_label_map(ids, "torchvision") == {
        "building.anchor::opponent": 1, "building.anchor::own": 2,
        "unit.guard::opponent": 3, "unit.guard::own": 4,
        "unit.speck::opponent": 5, "unit.speck::own": 6}
    with pytest.raises(EvidenceError):
        module.build_backend_label_map(ids, "other_backend")


@pytest.mark.parametrize("backend", ["yolox", "torchvision"])
def test_checked_export_preserves_original_images_identity_and_counts(disk, backend):
    module = api()
    root, draft = disk
    path = frozen(disk)
    before = {root / f["image_path"]: (root / f["image_path"]).read_bytes() for f in draft["frames"]}
    output = root / f"outputs/export-{backend}"
    manifest = module.export_multiclass_dataset(path, data_root=root, backend=backend, output_directory=output)
    assert manifest["counts"] == {"matches": 2, "groups": 8, "entities": 8, "frames": 6, "boxes": 8}
    assert manifest["reasons"] == []
    assert json.loads((output / "manifest.json").read_text()) == manifest
    assert set(p.name for p in output.iterdir()) == {"labels.json", "manifest.json"}
    for frame in manifest["frames"]:
        assert frame["status"] == "exported" and frame["label_path"] == "labels.json"
        assert frame["image_path"] in {f["image_path"] for f in draft["frames"]}
        assert frame["label_sha256"] == sha256((output / "labels.json").read_bytes()).hexdigest()
        assert frame["transform"] == {"original_width": 64, "original_height": 48,
            "offset_x": 0, "offset_y": 0, "scale_x": 1, "scale_y": 1,
            "output_width": 64, "output_height": 48, "rotation_degrees": 0}
    assert all(p.read_bytes() == value for p, value in before.items())
    labels = json.loads((output / "labels.json").read_text())
    if backend == "yolox":
        assert [c["id"] for c in labels["categories"]] == list(range(6))
        assert len(labels["images"]) == 6 and len(labels["annotations"]) == 8
        box = next(a for a in labels["annotations"] if a["annotation_id"] == "match_1_class_0_opponent_annotation")
        assert box["bbox"] == pytest.approx([6.4, 9.6, 1.92, 2.88])
        assert box["category_id"] == 4
    else:
        frame = next(f for f in labels["frames"] if any(a["annotation_id"] == "match_1_class_0_opponent_annotation" for a in f["observations"]))
        assert frame["labels"] == [5, 6]
        assert frame["boxes"][0] == pytest.approx([6.4, 9.6, 8.32, 12.48])
        assert all(value > 0 for f in labels["frames"] for value in f["labels"])


def test_export_is_deterministic_and_cannot_overwrite_directory(disk):
    module = api()
    root, _ = disk
    path = frozen(disk)
    one, two = root / "outputs/export-one", root / "outputs/export-two"
    module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=one)
    module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=two)
    assert {p.name: p.read_bytes() for p in one.iterdir()} == {p.name: p.read_bytes() for p in two.iterdir()}
    original = (one / "manifest.json").read_bytes()
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=one)
    assert (one / "manifest.json").read_bytes() == original


def test_export_rejects_corrupt_lock_before_creating_output(disk):
    module = api()
    root, _ = disk
    path = frozen(disk)
    document = json.loads(path.read_text())
    document["payload"]["draft"]["split_assignment"][0]["split"] = "prospective_test"
    path.write_bytes(canonical_bytes(document))
    output = root / "outputs/bad-export"
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    assert not output.exists()


def test_unknown_other_form_blocks_whole_frame_export(disk):
    module = api()
    root, _ = disk
    draft = multiclass_fixture()
    problems = ("unknown_owner", "neutral", "evolved", "unknown_form", "unknown_interval", "ignore_region", "pending", "excluded")
    for index, problem in enumerate(problems):
        frame, coverage = deepcopy(draft["frames"][0]), deepcopy(draft["coverage"][0])
        timestamp = 40 + index
        fid = frame_id("recording_1", 1000 + timestamp * 1000, Fraction(1, 1000))
        frame.update(frame_id=fid, raw_pts=1000 + timestamp * 1000, timestamp_seconds=timestamp,
                     image_path=f"synthetic/problem-{index}.png")
        coverage.update(frame_id=fid, coverage_id=f"problem_coverage_{index}")
        good, bad = deepcopy(draft["annotations"][0]), deepcopy(draft["annotations"][0])
        for number, annotation in enumerate((good, bad)):
            annotation.update(annotation_id=f"problem_{index}_{number}", frame_id=fid,
                              appearance_group_id=None, entity_occurrence_id=None)
            annotation["box"]["x"] = 0.1 + 0.3 * number
        if problem == "unknown_owner":
            bad["owner"] = "unknown"
        elif problem == "neutral":
            bad["owner"] = "neutral"
        elif problem == "evolved":
            bad["observed_form"] = "evolved"
        elif problem == "unknown_form":
            bad["observed_form"] = "unknown"
        elif problem == "unknown_interval":
            coverage["unknown_intervals"] = [{"start_seconds": timestamp, "end_seconds": timestamp + 1,
                "visual_class_ids": ["unit.speck"], "reason": "Synthetic unresolved target interval"}]
        elif problem == "ignore_region":
            coverage["ignore_regions"] = [{"box": {"x": 0, "y": 0, "width": 0.2, "height": 0.2},
                "visual_class_ids": ["unit.speck"], "reason": "Synthetic ignore without backend loss mask"}]
        elif problem == "pending":
            bad["review_state"] = "pending"
            coverage["exhaustive_state"] = "pending"
            frame["review_state"] = "pending"
        else:
            frame["review_state"] = "excluded"
        draft["frames"].append(frame)
        draft["coverage"].append(coverage)
        draft["annotations"].extend([good, bad])
    root = root / "outputs/safety-case"
    root.mkdir()
    current = multiclass_disk_fixture(root, draft=draft)
    path = frozen((root, current))
    output = root / "outputs/unsafe-frames"
    manifest = module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    labels = json.loads((output / "labels.json").read_text())
    assert manifest["counts"]["frames"] == 6 and manifest["counts"]["boxes"] == 8
    assert len(manifest["frames"]) == 14
    assert sum(r["status"] == "pending" for r in manifest["frames"]) == 7
    assert sum(r["status"] == "excluded" for r in manifest["frames"]) == 1
    assert not any(a["annotation_id"].startswith("problem_") for a in labels["annotations"])
    assert all(r["image_path"] is None and r["label_path"] is None for r in manifest["frames"] if r["status"] != "exported")


def test_prospective_test_material_rejected_before_output_creation(disk):
    module = api()
    root, draft = disk
    draft = deepcopy(draft)
    source = make_video(root / "local_data/prospective.mp4")
    record = deepcopy(draft["recordings"][0])
    record.update(recording_id="future_test", underlying_match_id="future_match", split="prospective_test",
                  source_path="local_data/prospective.mp4", source_sha256=file_hash(source),
                  technical_valid=False, complete_recording=False, full_human_review=False,
                  completion_attestation="pending", match_segment=None, exports=[])
    for key in ("width", "height", "rotation_degrees", "time_base", "origin_pts", "origin_time_base", "last_frame_seconds"):
        record[key] = None
    draft["recordings"].append(record)
    draft["matches"].append({"underlying_match_id": "future_match", "provenance": "natural", "identity_attestation": "pending", "notes": "Reserved, not evaluated"})
    draft["split_assignment"].append({"underlying_match_id": "future_match", "split": "prospective_test"})
    draft["intake"].append({"intake_id": "future_intake", "recording_id": "future_test", "status": "pending", "reason": "Reserved for later authorization", "history": []})
    path = frozen((root, draft))
    output = root / "outputs/no-blind-export"
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    assert not output.exists()


def test_export_rejects_output_outside_container_and_changed_source(disk):
    module = api()
    root, draft = disk
    path = frozen(disk)
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=root.parent / "outside-export")
    assert not (root.parent / "outside-export").exists()
    (root / draft["recordings"][0]["source_path"]).write_bytes(b"damaged test-only source")
    output = root / "outputs/changed-source"
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    assert not output.exists()


def test_short_label_write_never_publishes_success_manifest(disk, monkeypatch):
    module = api()
    root, _ = disk
    path = frozen(disk)
    original = Path.open

    class ShortWriter:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *arguments):
            return self.stream.__exit__(*arguments)

        def write(self, raw):
            return self.stream.write(raw[:7])  # A real new file gets only a prefix.

        def fileno(self):
            return self.stream.fileno()

        def flush(self):
            self.stream.flush()

    def opened(current, mode="r", *args, **kwargs):
        stream = original(current, mode, *args, **kwargs)
        return ShortWriter(stream) if mode == "xb" and current.name == "labels.json" else stream

    monkeypatch.setattr(Path, "open", opened)
    output = root / "outputs/short-write"
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    assert not (output / "manifest.json").exists() and not (output / "labels.json").exists()


def test_manifest_fsync_failure_cleans_only_owned_export_files(disk, monkeypatch):
    module = api()
    root, _ = disk
    path = frozen(disk)
    original = root / "outputs/prior-export"
    module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=original)
    before = {p.name: p.read_bytes() for p in original.iterdir()}
    fsync, calls = module.os.fsync, []

    def fail_second(handle):
        calls.append(handle)
        if len(calls) == 2:
            raise OSError("Injected second-file fsync fault")
        return fsync(handle)

    monkeypatch.setattr(module.os, "fsync", fail_second)
    output = root / "outputs/failed-export"
    with pytest.raises(EvidenceError):
        module.export_multiclass_dataset(path, data_root=root, backend="yolox", output_directory=output)
    assert not (output / "manifest.json").exists() and not (output / "labels.json").exists()
    assert {p.name: p.read_bytes() for p in original.iterdir()} == before
