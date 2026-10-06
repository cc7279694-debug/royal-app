"""Separate CLI readiness, checked freezes and sanitized local failures."""
from copy import deepcopy
from importlib import import_module
import json
import subprocess
import sys

import pytest

from clash_tracker_video.experiment_lock import canonical_bytes
from clash_tracker_video import multiclass_dataset as checked
from test_multiclass_dataset import disk, selection, scale


def api():
    try:
        return import_module("clash_tracker_video.multiclass_cli")
    except ModuleNotFoundError:
        pytest.fail("Separate multiclass preparation CLI is not implemented")


def draft_path(disk, draft=None, name="draft-private.json"):
    path = disk[0] / "outputs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(draft if draft is not None else disk[1]))
    return path


def arguments(command, path, disk, *extra):
    return [command, str(path), "--data-root", str(disk[0]), *map(str, extra)]


def test_unselected_draft_is_valid_insufficient_without_creating_lock(disk, capsys):
    module = api()
    path = draft_path(disk)
    assert module.main(arguments("validate-dataset", path, disk)) == 3
    report = json.loads(capsys.readouterr().out)
    assert report["ready"] is False and "select_three_to_five_classes" in report["blocking_reasons"]
    assert module.main(arguments("scale-report", path, disk)) == 3
    assert json.loads(capsys.readouterr().out)["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    assert not (disk[0] / "outputs/final").exists()


def test_ready_checked_draft_and_existing_lock_commands_return_zero(disk, capsys):
    module = api()
    root, draft = disk
    prior = scale(disk)
    selected = selection(draft, prior)
    path = draft_path(disk, selected)
    prior_path = next((root / "outputs/scale").iterdir())
    assert module.main(arguments("validate-dataset", path, disk, "--scale-snapshot", prior_path)) == 0
    assert json.loads(capsys.readouterr().out)["ready"] is True
    output = root / "outputs/final"
    assert module.main(arguments("freeze-dataset", path, disk, "--scale-snapshot", prior_path, "--output", output)) == 0
    assert "MULTICLASS_DATASET_LOCKED" in capsys.readouterr().out
    lock_path = next(output.iterdir())
    assert module.main(arguments("validate-dataset-lock", lock_path, disk)) == 0
    capsys.readouterr()
    export = root / "outputs/export"
    assert module.main(arguments("export", lock_path, disk, "--backend", "torchvision", "--output", export)) == 0
    assert (export / "manifest.json").is_file()


@pytest.mark.parametrize("command", ["validate-dataset", "scale-report"])
def test_cli_bad_report_returns_two_without_private_paths_or_output(disk, capsys, command):
    module = api()
    root, draft = disk
    path = draft_path(disk)
    (root / draft["recordings"][0]["exports"][0]["report_path"]).write_text("damaged", encoding="utf-8")
    assert module.main(arguments(command, path, disk)) == 2
    output = capsys.readouterr()
    assert not output.out and output.err
    assert str(root) not in output.err and "Traceback" not in output.err and "draft-private" not in output.err
    assert not (root / "outputs/final").exists()


def test_missing_snapshot_or_unknown_arguments_do_not_write_or_leak(disk, capsys):
    module = api()
    path = draft_path(disk)
    output = disk[0] / "outputs/should-not-exist"
    assert module.main(arguments("freeze-dataset", path, disk, "--output", output)) == 2
    assert module.main(["validate-dataset", str(path), "--evil-private", str(disk[0])]) == 2
    captured = capsys.readouterr()
    assert not captured.out and str(disk[0]) not in captured.err and str(path) not in captured.err
    assert not output.exists()


def test_help_imports_no_tk_or_model_framework_in_fresh_process():
    module = api()
    code = "from clash_tracker_video.multiclass_cli import main; import sys; " \
           "assert main(['--help']) == 0; " \
           "assert not any(x in sys.modules for x in ('tkinter','torch','torchvision','yolox')); " \
           "assert main(['annotate','--help']) == 0"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    for command in ("validate-dataset", "scale-report", "freeze-scale", "freeze-dataset", "validate-dataset-lock", "annotate", "export"):
        assert command in result.stdout


def test_freeze_scale_is_separate_preselection_gate_and_cannot_overwrite(disk, capsys):
    module = api()
    root, _ = disk
    path = draft_path(disk)
    output = root / "outputs/cli-scale"
    assert module.main(arguments("freeze-scale", path, disk, "--output", output)) == 0
    capsys.readouterr()
    original = {p.name: p.read_bytes() for p in output.iterdir()}
    assert module.main(arguments("freeze-scale", path, disk, "--output", output)) == 2
    assert {p.name: p.read_bytes() for p in output.iterdir()} == original
    assert str(root) not in capsys.readouterr().err


def test_pending_support_cannot_satisfy_exported_label_gate(disk, capsys):
    module = api()
    root, draft = disk
    prior = scale(disk)
    selected = selection(draft, prior)
    for frame in selected["frames"]:
        frame["review_state"] = "pending"
    for coverage in selected["coverage"]:
        coverage["exhaustive_state"] = "pending"
    path = draft_path(disk, selected)
    prior_path = next((root / "outputs/scale").iterdir())
    assert module.main(arguments("validate-dataset", path, disk)) == 3
    assert json.loads(capsys.readouterr().out)["ready"] is False
    output = root / "outputs/pending-lock"
    assert module.main(arguments("freeze-dataset", path, disk, "--scale-snapshot", prior_path, "--output", output)) == 2
    assert not output.exists()
    captured = capsys.readouterr()
    assert not captured.out and str(root) not in captured.err


def test_corrupt_draft_export_is_not_a_lock_and_writes_nothing(disk, capsys):
    module = api()
    path = draft_path(disk)
    output = disk[0] / "outputs/no-draft-export"
    assert module.main(arguments("export", path, disk, "--backend", "yolox", "--output", output)) == 2
    assert not output.exists()
    captured = capsys.readouterr()
    assert not captured.out and str(disk[0]) not in captured.err


def test_cli_annotate_launches_real_native_window_in_fresh_process(disk):
    api()
    root, _ = disk
    path = draft_path(disk)
    output = root / "outputs/untouched-gui"
    program = """
import sys
from pathlib import Path
import tkinter as tk
from clash_tracker_video import evidence_prepare as ep, training_dataset as safe, multiclass_dataset as data
from clash_tracker_video.multiclass_cli import main
root = Path(sys.argv[1])
for module in (ep, safe, data):
    module.PROJECT_ROOT = root
original = tk.Tk.mainloop
def bounded_loop(self, *args, **kwargs):
    self.after(100, self.quit)
    return original(self, *args, **kwargs)
tk.Tk.mainloop = bounded_loop
raise SystemExit(main(['annotate', sys.argv[2], '--data-root', str(root), '--output', sys.argv[3]]))
"""
    result = subprocess.run([sys.executable, "-c", program, str(root), str(path), str(output)],
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "annotation session closed" in result.stdout and result.stderr == ""
    assert not output.exists()  # Merely opening a window does not invent a revision.
