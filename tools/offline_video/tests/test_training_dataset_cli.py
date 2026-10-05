"""Thin CLI contracts with real synthetic bindings; no gameplay or live Tk."""
from copy import deepcopy
from importlib import import_module
import json
import subprocess
import sys

import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from test_training_dataset import disk, write_json


def api():
    try:
        return import_module("clash_tracker_video.training_dataset_cli")
    except ModuleNotFoundError:
        pytest.fail("Training dataset CLI is not implemented")


def draft_path(disk, draft=None):
    path = disk[0] / "outputs/cli/dataset-private.json"
    write_json(path, draft if draft is not None else disk[1])
    return path


def arguments(command, path, disk, *extra):
    return [command, str(path), "--data-root", str(disk[0]),
            "--development", str(disk[3]), *map(str, extra)]


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for folder in ("outputs", "local_data")
            for p in (root / folder).rglob("*") if p.is_file()}


def assert_private(output, disk):
    for value in (str(disk[0]), "dataset-private.json", "recording_1", "match_1",
                  "synthetic_minion_units", disk[2]["sha256"], "Traceback"):
        assert value not in output


def test_ready_draft_uses_checked_disk_and_anonymous_aggregate(disk, capsys):
    path = draft_path(disk)
    before = snapshot(disk[0])
    assert api().main(arguments("validate-dataset", path, disk)) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["valid"] is True
    assert report["training_data_ready"] is True
    assert report["evaluation_ready"] is True
    assert report["counts"]["target_positive_matches"] == 4
    assert report["counts"]["confirmed_target_deployments"] == 8
    assert report["counts"]["training_images"] == 8
    assert report["counts"]["training_unit_boxes"] == 24
    assert "per_match" not in report and "per_recording" not in report
    assert captured.err == ""
    assert snapshot(disk[0]) == before
    assert_private(captured.out, disk)


@pytest.mark.parametrize("kind", ["matches", "plays"])
def test_valid_insufficient_data_returns_three_and_freeze_creates_nothing(disk, capsys, kind):
    draft = deepcopy(disk[1])
    if kind == "matches":
        for play in draft["deployments"]:
            if play["underlying_match_id"] == "match_4":
                play["independence_attestation"] = "pending"
        expected = (3, 6)
    else:
        draft["deployments"][0]["independence_attestation"] = "pending"
        expected = (4, 7)
    path = draft_path(disk, draft)
    destination = disk[0] / "outputs/rejected-locks"
    before = snapshot(disk[0])
    module = api()
    assert module.main(arguments("validate-dataset", path, disk)) == 3
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["valid"] is True and report["training_data_ready"] is False
    assert (report["counts"]["target_positive_matches"],
            report["counts"]["confirmed_target_deployments"]) == expected
    assert_private(captured.out + captured.err, disk)
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)
    assert not destination.exists()
    assert snapshot(disk[0]) == before


def test_training_ready_without_absent_coverage_remains_zero_and_freezable(disk, capsys):
    draft = deepcopy(disk[1])
    draft["confirmed_absent_intervals"] = []
    path = draft_path(disk, draft)
    module = api()
    assert module.main(arguments("validate-dataset", path, disk)) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["training_data_ready"] is True and report["evaluation_ready"] is False
    assert report["evaluation_reasons"] == ["missing_absent_coverage"]
    destination = disk[0] / "outputs/no-evaluation-locks"
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 0
    lock = json.loads(next(destination.iterdir()).read_text(encoding="utf-8"))
    assert lock["payload"]["derived"]["evaluation_ready"] is False


def test_freeze_reloads_checked_lock_and_refuses_existing_version(disk, capsys):
    path = draft_path(disk)
    destination = disk[0] / "outputs/cli-locks"
    before = snapshot(disk[0])
    module = api()
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 0
    captured = capsys.readouterr()
    assert "locked" in captured.out.lower() and captured.err == ""
    assert_private(captured.out, disk)
    lock_path = destination / "synthetic_minion_units.training_dataset.v1.json"
    raw = lock_path.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    lock = json.loads(raw)
    assert lock["lock_type"] == "training_dataset"
    assert lock["payload"]["derived"]["counts"]["confirmed_target_deployments"] == 8
    assert len(lock["payload"]["folds"]) == 4
    assert module.main(arguments("validate-dataset-lock", lock_path, disk)) == 0
    capsys.readouterr()
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)
    assert lock_path.read_bytes() == raw and len(list(destination.iterdir())) == 1
    after = snapshot(disk[0])
    assert all(after[name] == value for name, value in before.items())


@pytest.mark.parametrize("kind", ["source", "image", "sidecar", "development"])
def test_validation_rejects_changed_external_files_instead_of_snapshot_success(disk, capsys, kind):
    path = draft_path(disk)
    draft = disk[1]
    target = {"source": disk[0] / draft["recordings"][0]["source_path"],
              "image": disk[0] / draft["frames"][0]["image_path"],
              "sidecar": disk[0] / draft["annotation_sources"][0]["path"],
              "development": disk[3]}[kind]
    target.write_bytes(target.read_bytes() + b"changed")
    before = snapshot(disk[0])
    assert api().main(arguments("validate-dataset", path, disk)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)
    assert snapshot(disk[0]) == before


def test_lock_validation_rechecks_external_pixels(disk, capsys):
    path = draft_path(disk)
    destination = disk[0] / "outputs/checked-locks"
    module = api()
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 0
    capsys.readouterr()
    lock_path = next(destination.iterdir())
    image = disk[0] / disk[1]["frames"][0]["image_path"]
    image.write_bytes(image.read_bytes() + b"changed")
    before = snapshot(disk[0])
    assert module.main(arguments("validate-dataset-lock", lock_path, disk)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)
    assert snapshot(disk[0]) == before


def test_freeze_cannot_report_success_when_postwrite_reload_fails(disk, monkeypatch, capsys):
    module = api()
    path = draft_path(disk)
    destination = disk[0] / "outputs/postwrite-locks"
    # Simulate a disk failure at the post-write validation boundary. The actual
    # write remains real; existing inputs must survive and success must be absent.
    def unavailable(*args, **kwargs):
        raise EvidenceError("private-postwrite-diagnostic")
    monkeypatch.setattr(module, "load_dataset_lock", unavailable)
    before = snapshot(disk[0])
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "private-postwrite-diagnostic" not in captured.err
    assert destination.is_dir() and len(list(destination.iterdir())) == 1
    assert json.loads(next(destination.iterdir()).read_bytes())["lock_type"] == "training_dataset"
    after = snapshot(disk[0])
    assert all(after[name] == value for name, value in before.items())


@pytest.mark.parametrize("content", ["{", '{"schema_version":1,"schema_version":1}',
                                     '{"private_field":NaN}', '{"private_field":1}'])
def test_strict_json_and_unknown_fields_return_two_without_echo(disk, capsys, content):
    path = draft_path(disk)
    path.write_text(content, encoding="utf-8")
    before = snapshot(disk[0])
    assert api().main(arguments("validate-dataset", path, disk)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "private_field" not in captured.err
    assert_private(captured.err, disk)
    assert snapshot(disk[0]) == before


@pytest.mark.parametrize("argv", [[], ["private-unknown-command"], ["validate-dataset"],
    ["validate-dataset", "private-file", "--private-unknown-flag", "private-value"],
    ["validate-dataset", "private-file", "--data-r", "private-root", "--development", "private-lock"]])
def test_parser_rejects_missing_unknown_and_abbreviated_arguments_without_echo(argv, capsys):
    assert api().main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert "private-" not in captured.err and "Traceback" not in captured.err


@pytest.mark.parametrize("kind", ["unknown", "abbreviated"])
def test_strict_flags_reject_on_otherwise_valid_disk_inputs(disk, capsys, kind):
    path = draft_path(disk)
    argv = arguments("validate-dataset", path, disk)
    if kind == "unknown":
        argv += ["--private-unknown-flag", "private-value"]
    else:
        argv[argv.index("--data-root")] = "--data-r"
    before = snapshot(disk[0])
    assert api().main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert "private-" not in captured.err
    assert_private(captured.err, disk)
    assert snapshot(disk[0]) == before


@pytest.mark.parametrize("kind", ["outside", "traversal", "url", "root"])
def test_artifact_paths_cannot_escape_private_roots(disk, capsys, kind):
    path = draft_path(disk)
    if kind == "outside":
        unsafe = disk[0] / "public.json"
        write_json(unsafe, disk[1])
    elif kind == "traversal":
        unsafe = disk[0] / "outputs/cli/../cli/dataset-private.json"
    elif kind == "url":
        unsafe = "https://private.invalid/dataset.json"
    else:
        unsafe = disk[0] / "outputs"
    assert api().main(arguments("validate-dataset", unsafe, disk)) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert "private.invalid" not in captured.err
    assert_private(captured.err, disk)


def test_data_root_is_explicit_absolute_and_output_is_private(disk, capsys):
    path = draft_path(disk)
    module = api()
    args = arguments("validate-dataset", path, disk)
    args[args.index("--data-root") + 1] = "."
    assert module.main(args) == 2
    assert capsys.readouterr().out == ""
    destination = disk[0] / "public-locks"
    assert module.main(arguments("freeze-dataset", path, disk, "--output", destination)) == 2
    assert not destination.exists()
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)


def test_annotate_uses_checked_context_and_closed_session_makes_no_save_claim(disk, monkeypatch, capsys):
    module = api()
    annotation = import_module("clash_tracker_video.unit_annotation")
    path = draft_path(disk)
    destination = disk[0] / "outputs/revisions"
    before = snapshot(disk[0])
    # GUI interaction belongs to Task 3. Only its event-loop boundary is replaced;
    # this CLI test still requires real disk binding before a window can open.
    def close_without_edit(draft, indexes, output):
        assert draft == path and indexes.root == disk[0] and output == destination
        assert indexes.development_path == disk[3]
        assert len(indexes) == 4
    monkeypatch.setattr(annotation, "launch_annotator", close_without_edit)
    assert module.main(arguments("annotate", path, disk, "--output", destination)) == 0
    captured = capsys.readouterr()
    assert "closed" in captured.out.lower() and captured.err == ""
    assert not any(word in captured.out.lower() for word in ("saved", "locked", "success"))
    assert_private(captured.out, disk)
    assert snapshot(disk[0]) == before and not destination.exists()


def test_annotate_rejects_changed_bindings_before_opening_gui(disk, monkeypatch, capsys):
    module = api()
    annotation = import_module("clash_tracker_video.unit_annotation")
    path = draft_path(disk)
    source = disk[0] / disk[1]["recordings"][0]["source_path"]
    source.write_bytes(source.read_bytes() + b"changed")
    def must_not_open(*args, **kwargs):
        pytest.fail("Invalid external evidence reached the GUI")
    monkeypatch.setattr(annotation, "launch_annotator", must_not_open)
    assert module.main(arguments("annotate", path, disk, "--output", disk[0] / "outputs/revisions")) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err
    assert_private(captured.err, disk)


@pytest.mark.parametrize("kind", ["evidence", "tk"])
def test_annotate_diagnostic_is_sanitized(disk, monkeypatch, capsys, kind):
    module = api()
    annotation = import_module("clash_tracker_video.unit_annotation")
    path = draft_path(disk)
    def unavailable(*args, **kwargs):
        if kind == "tk":
            from tkinter import TclError
            raise TclError("private-tk-diagnostic")
        raise EvidenceError("private-tk-diagnostic")
    monkeypatch.setattr(annotation, "launch_annotator", unavailable)
    assert module.main(arguments("annotate", path, disk, "--output", disk[0] / "outputs/revisions")) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "private-tk-diagnostic" not in captured.err
    assert_private(captured.err, disk)


@pytest.mark.parametrize("argv,want", [(["--help"], 0), (["private-command"], 2),
    (["validate-dataset", "private-file", "--private-flag", "private-value"], 2)])
def test_python_module_entrypoint_preserves_exit_codes_and_no_traceback(argv, want):
    api()
    result = subprocess.run([sys.executable, "-m", "clash_tracker_video.training_dataset_cli", *argv],
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == want
    assert "Traceback" not in result.stdout + result.stderr
    if want == 2:
        assert result.stdout == "" and "private-" not in result.stderr
