"""Subprocess contracts using real anonymous video, reports, indexes and PNGs."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
from PIL import Image

from conftest import make_video
from experiment_fixtures import development_fixture
from lock_fixtures import gt_fixture, model_fixture
from clash_tracker_video.evidence_prepare import load_indexes, prepare_evidence
from clash_tracker_video.experiment_development import _index_snapshot
from clash_tracker_video.experiment_lock import freeze_development, freeze_model, lock_filename


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "clash_tracker_video.experiment_cli", *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", timeout=30)


def write(path, document):
    path.write_text(json.dumps(document, allow_nan=False), encoding="utf-8")


def bind_frames(annotations, index):
    frames = {f["timestamp_seconds"]: f for f in index["frames"]}
    for annotation in annotations:
        frame = frames[annotation["timestamp_seconds"]]
        for field in ("frame_id", "raw_pts", "time_base", "image_path", "image_width", "image_height"):
            annotation[field] = deepcopy(frame[field])


def prepared(root, recording_id, offset=0):
    video = make_video(root / (recording_id + ".mp4"), pts=range(offset, offset + 20001, 100))
    folder = root / (recording_id + "-prepared")
    index = prepare_evidence(video, folder, recording_id=recording_id,
                             times=[0, 1, 1.1, 1.2, 5, 5.1, 5.2, 20])
    # The synthetic perspective is a manual annotation, retained in the disk index.
    index["recording"]["perspective"] = "own_bottom"
    write(folder / "index.json", index)
    return index, folder / "index.json"


@pytest.fixture
def disk():
    root = Path(__file__).resolve().parents[3] / "outputs" / "synthetic-experiment-tests" / uuid.uuid4().hex
    index, index_path = prepared(root, "synthetic")
    draft, _ = development_fixture()
    evidence = draft["candidates"][0]["evidence"]
    evidence["recordings"] = [deepcopy(index["recording"])]
    bind_frames(evidence["frame_annotations"], index)
    path = root / "development-private.json"
    write(path, draft)
    return root, draft, path, index_path


@pytest.fixture
def chain(disk):
    root, draft, path, index_path = disk
    directory = root / "prerequisites"
    development = freeze_development(draft, load_indexes([index_path]), directory)
    model = freeze_model(model_fixture(development), development, directory)
    test_index, test_index_path = prepared(root, "synthetic_test", offset=5000)
    gt = gt_fixture(development, model)
    gt["recording"] = deepcopy(test_index["recording"])
    bind_frames(gt["deployments"][0]["key_frames"], test_index)
    pseudo = {"identity": {"recording_id": "synthetic_test"}, "candidates": [
        {"evidence": {"frame_annotations": gt["deployments"][0]["key_frames"]}}]}
    gt["index_snapshot"] = _index_snapshot(pseudo, load_indexes([test_index_path]))
    gt_path = root / "gt-private.json"
    write(gt_path, gt)
    return (root, gt, gt_path, test_index_path,
            directory / lock_filename(development), directory / lock_filename(model))


def assert_private(result, root):
    output = result.stdout + result.stderr
    for private in (str(root), "development-private.json", "gt-private.json",
                    "anonymous_experiment", "anonymous_match_a", "synthetic_card", "Traceback"):
        assert private not in output


def snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_readiness_binds_real_disk_and_emits_only_status(disk):
    root, _, path, index = disk
    before = snapshot(root)
    result = run("readiness", path, "--indexes", index)
    assert result.returncode == 0
    assert result.stdout.strip() == "Readiness: DEV_VALIDATED."
    assert result.stderr == ""
    assert snapshot(root) == before
    assert_private(result, root)


@pytest.mark.parametrize("kind", ["not_clear", "no_selection"])
def test_valid_not_ready_is_three_and_cannot_freeze(disk, kind):
    root, draft, path, index = disk
    if kind == "not_clear":
        draft["candidates"][0]["deployments"][1]["clear"] = False
    else:
        draft["selection"] = None
    write(path, draft)
    ready = run("readiness", path, "--indexes", index)
    assert ready.returncode == 3
    assert ready.stdout.strip() == "Readiness: NOT_READY."
    destination = root / "rejected-locks"
    before = snapshot(root)
    rejected = run("freeze-development", path, "--indexes", index, "--output", destination)
    assert rejected.returncode == 2
    assert not destination.exists()
    assert snapshot(root) == before
    assert_private(ready, root)
    assert_private(rejected, root)


def test_invalid_evidence_is_two_and_no_output(disk):
    root, draft, path, index = disk
    draft["identity"]["full_human_review"] = False
    write(path, draft)
    assert run("readiness", path, "--indexes", index).returncode == 2
    destination = root / "rejected-locks"
    result = run("freeze-development", path, "--indexes", index, "--output", destination)
    assert result.returncode == 2
    assert not destination.exists()
    assert_private(result, root)


def test_freeze_development_validate_and_refuse_overwrite(disk):
    root, _, path, index = disk
    destination = root / "locks"
    result = run("freeze-development", path, "--indexes", index, "--output", destination)
    assert result.returncode == 0
    assert result.stdout.strip() == "Development: DEV_LOCKED."
    lock = destination / "anonymous_experiment.development.v1.json"
    raw = lock.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    validation = run("validate-lock", lock)
    assert validation.returncode == 0
    assert validation.stdout.strip() == "Lock valid."
    assert run("freeze-development", path, "--indexes", index, "--output", destination).returncode == 2
    assert lock.read_bytes() == raw
    assert len(list(destination.iterdir())) == 1
    assert_private(result, root)
    assert_private(validation, root)


@pytest.mark.parametrize("kind", ["report", "index", "png"])
@pytest.mark.parametrize("command", ["readiness", "freeze-development"])
def test_disk_tamper_fails_before_output_and_preserves_inputs(disk, kind, command):
    root, _, path, index_path = disk
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if kind == "report":
        (index_path.parent / index["export_report"]).write_bytes(b"private-invalid-report")
    elif kind == "index":
        index["frames"][1]["raw_pts"] += 1
        write(index_path, index)
    else:
        image = index_path.parent / index["frames"][1]["image_path"]
        Image.new("RGB", (1, 1)).save(image)
    before = snapshot(root)
    destination = root / "rejected-locks"
    args = [command, path, "--indexes", index_path]
    if command == "freeze-development":
        args += ["--output", destination]
    result = run(*args)
    assert result.returncode == 2
    assert not destination.exists()
    assert snapshot(root) == before
    assert_private(result, root)


def test_gt_disk_binding_freeze_and_full_chain_validation(chain):
    root, _, gt, index, development, model = chain
    before = snapshot(root)
    destination = root / "test-locks"
    result = run("freeze-test-gt", gt, "--development", development, "--model", model,
                 "--indexes", index, "--output", destination)
    assert result.returncode == 0
    assert result.stdout.strip() == "Test GT locked."
    lock = destination / "anonymous_experiment.test_gt.v1.json"
    assert run("validate-lock", model, "--development", development).returncode == 0
    validated = run("validate-lock", lock, "--development", development, "--model", model)
    assert validated.returncode == 0
    assert all(path.read_bytes() == raw for path, raw in before.items())
    original = lock.read_bytes()
    assert run("freeze-test-gt", gt, "--development", development, "--model", model,
               "--indexes", index, "--output", destination).returncode == 2
    assert lock.read_bytes() == original
    assert_private(result, root)
    assert_private(validated, root)


@pytest.mark.parametrize("kind", ["pixel_hash", "aliases", "metadata", "png_content"])
def test_gt_declared_snapshot_cannot_replace_actual_disk(chain, kind):
    root, gt, path, index, development, model = chain
    frame = gt["index_snapshot"]["synthetic_test"]["frames"][0]
    if kind == "pixel_hash":
        frame["_content_hash"] = "d" * 64
    elif kind == "aliases":
        frame["_aliases"].append("exports/other.png")
    elif kind == "metadata":
        frame["requested_seconds"] = 0.9
    else:
        Image.new("RGB", (64, 48), (0, 0, 0)).save(index.parent / frame["image_path"])
    write(path, gt)
    before = snapshot(root)
    destination = root / "rejected-gt-locks"
    result = run("freeze-test-gt", path, "--development", development, "--model", model,
                 "--indexes", index, "--output", destination)
    assert result.returncode == 2
    assert not destination.exists()
    assert snapshot(root) == before
    assert_private(result, root)


@pytest.mark.parametrize("kind", ["missing_development", "missing_model", "wrong_development", "wrong_model", "damaged_model"])
def test_gt_requires_correct_prerequisite_chain(chain, kind):
    root, _, gt, index, development, model = chain
    if kind == "missing_development":
        development = root / "missing-dev.json"
    elif kind == "missing_model":
        model = root / "missing-model.json"
    elif kind == "wrong_development":
        development = model
    elif kind == "wrong_model":
        model = development
    else:
        model.write_bytes(b"{}")
    destination = root / "rejected-gt-locks"
    result = run("freeze-test-gt", gt, "--development", development, "--model", model,
                 "--indexes", index, "--output", destination)
    assert result.returncode == 2
    assert not destination.exists()
    assert_private(result, root)


def test_validate_model_requires_development_and_detects_changed_digest(chain):
    root, _, _, _, development, model = chain
    assert run("validate-lock", model).returncode == 2
    document = json.loads(model.read_text(encoding="utf-8"))
    document["payload"]["confidence_threshold"] = 0.6
    write(model, document)
    result = run("validate-lock", model, "--development", development)
    assert result.returncode == 2
    assert_private(result, root)


@pytest.mark.parametrize("raw", [b"{", b'{"schema_version":1,"schema_version":1}', b'{"schema_version":NaN}', b"[]"])
def test_strict_json_rejects_malformed_duplicate_and_nonfinite(disk, raw):
    root, _, path, index = disk
    path.write_bytes(raw)
    destination = root / "rejected-locks"
    result = run("freeze-development", path, "--indexes", index, "--output", destination)
    assert result.returncode == 2
    assert not destination.exists()
    assert_private(result, root)


@pytest.mark.parametrize("kind", ["traversal", "url", "outside", "output_traversal", "index_traversal"])
def test_local_private_boundary_rejects_paths_without_echo(disk, tmp_path, kind):
    root, _, path, index = disk
    output = root / "rejected-locks"
    if kind == "traversal":
        path = str(root / ".." / root.name / path.name)
    elif kind == "url":
        path = "https://private.invalid/sensitive.json"
    elif kind == "outside":
        path = tmp_path / "private.json"
        path.write_bytes(b"{}")
    elif kind == "index_traversal":
        index = str(index.parent / ".." / index.parent.name / index.name)
    else:
        output = str(root / ".." / root.name / "rejected-locks")
    result = run("freeze-development", path, "--indexes", index, "--output", output)
    assert result.returncode == 2
    assert not (root / "rejected-locks").exists()
    assert str(path) not in result.stdout + result.stderr
    assert_private(result, root)


@pytest.mark.parametrize("args", [[], ["unknown-private"], ["freeze-model"], ["readiness"],
                                 ["readiness", "private.json", "--indexes"],
                                 ["validate-lock", "private.json", "--private-secret"]])
def test_argument_errors_are_two_without_private_echo(args):
    result = run(*args)
    assert result.returncode == 2
    assert "private" not in result.stdout + result.stderr
    assert "Traceback" not in result.stderr


def test_help_is_available_without_enabling_model_freeze():
    result = run("--help")
    assert result.returncode == 0
    assert "readiness" in result.stdout and "freeze-test-gt" in result.stdout
    assert "freeze-model" not in result.stdout
