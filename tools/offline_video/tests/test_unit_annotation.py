"""Synthetic geometry, additive unit revisions and local Tk event behavior."""
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from clash_tracker_video import training_dataset as dataset
from clash_tracker_video.evidence_contract import EvidenceError, load_evidence, valid_type
from clash_tracker_video.experiment_lock import canonical_bytes
from training_dataset_fixtures import dataset_fixture
from test_training_dataset import disk as checked_disk


def api():
    try:
        return import_module("clash_tracker_video.unit_annotation")
    except ModuleNotFoundError:
        pytest.fail("Local unit annotation API is not implemented")


@pytest.mark.parametrize("box,image,display,want", [
    ((150, 75, 250, 125), (400, 200), (50, 25, 400, 200), [.25, .25, .25, .25]),
    ((250, 125, 150, 75), (400, 200), (50, 25, 400, 200), [.25, .25, .25, .25]),
    ((100, 70, 200, 120), (400, 200), (50, 20, 200, 100), [.25, .5, .5, .5]),
    ((50, 20, 370, 260), (640, 480), (50, 20, 320, 240), [0, 0, 1, 1]),
    ((110, 80, 150, 100), (640, 480), (50, 20, 320, 240), [.1875, .25, .125, 1 / 12]),
])
def test_canvas_boxes_use_original_rotated_image_not_letterbox(box, image, display, want):
    assert api().canvas_box_to_normalized(box, image, display) == pytest.approx(want)


@pytest.mark.parametrize("box", [
    (49, 40, 100, 80), (70, 19, 100, 80), (70, 40, 251, 80), (70, 40, 100, 121),
    (100, 40, 100, 80), (70, 80, 100, 80), (float("nan"), 40, 100, 80), (True, 40, 100, 80),
])
def test_outside_zero_area_or_nonfinite_drag_rejects_without_clipping(box):
    with pytest.raises(EvidenceError):
        api().canvas_box_to_normalized(box, (400, 200), (50, 20, 200, 100))


@pytest.mark.parametrize("image,display", [
    ((0, 200), (0, 0, 200, 100)), ((True, 200), (0, 0, 200, 100)),
    ((400, 200), (0, 0, 200, 200)), ((400, 200), (0, 0, 0, 100)),
    ((400, 200), (0, 0, float("inf"), 100)),
])
def test_invalid_size_or_nonuniform_display_scale_rejects(image, display):
    with pytest.raises(EvidenceError):
        api().canvas_box_to_normalized((10, 10, 20, 20), image, display)


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(dataset, "PROJECT_ROOT", tmp_path)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("/outputs/\n/local_data/\n", encoding="utf-8")
    original = dataset_fixture()
    folder = tmp_path / "outputs/original"
    folder.mkdir(parents=True)
    old_draft = folder / "draft.json"
    old_sidecar = folder / "units.json"
    old_draft.write_bytes(canonical_bytes(original) + b"\n")
    old_sidecar.write_bytes(canonical_bytes({"schema_version": 1, "annotation_source_id": "revision_1",
                                           "unit_annotations": original["unit_annotations"]}) + b"\n")
    return tmp_path, original, old_draft, old_sidecar


def request(storage, draft=None, source_id="revision_2"):
    return {"draft": deepcopy(draft or storage[1]), "data_root": storage[0],
            "annotation_source_id": source_id}


def test_revision_exclusively_writes_paired_snapshot_and_preserves_original_bytes(storage):
    root, original, old_draft, old_sidecar = storage
    before = old_draft.read_bytes(), old_sidecar.read_bytes()
    document = request(storage)
    unchanged = deepcopy(document)
    output = root / "outputs/revisions/revision.v2.json"
    assert api().save_annotation_revision(document, output) == output
    saved = load_evidence(output)
    labels_path = output.with_name("revision.v2.units.json")
    labels = load_evidence(labels_path)
    assert labels["schema_version"] == 1
    assert labels["annotation_source_id"] == "revision_2"
    assert saved["annotation_sources"] == [{"annotation_source_id": "revision_2",
                                             "path": "outputs/revisions/revision.v2.units.json",
                                             "sha256": sha256(labels_path.read_bytes()).hexdigest()}]
    assert labels["unit_annotations"] == saved["unit_annotations"]
    assert len(labels["unit_annotations"]) == 96
    for old, new in zip(original["unit_annotations"], labels["unit_annotations"]):
        assert {k: v for k, v in new.items() if k != "annotation_source_id"} == {
            k: v for k, v in old.items() if k != "annotation_source_id"}
    assert saved["frames"] == original["frames"]
    assert saved["deployments"] == original["deployments"]
    assert saved["freeze_version"] == original["freeze_version"]
    assert saved["created_at"] == original["created_at"]
    assert document == unchanged
    assert (old_draft.read_bytes(), old_sidecar.read_bytes()) == before


@pytest.mark.parametrize("collision", ["draft", "sidecar"])
def test_revision_collision_preserves_prior_file_and_creates_no_pair(storage, collision):
    output = storage[0] / "outputs/new.json"
    sidecar = output.with_name("new.units.json")
    existing = output if collision == "draft" else sidecar
    existing.write_bytes(b"Original bytes")
    with pytest.raises(EvidenceError):
        api().save_annotation_revision(request(storage), output)
    assert existing.read_bytes() == b"Original bytes"
    assert not (sidecar if collision == "draft" else output).exists()


@pytest.mark.parametrize("presence", ["positive", "unknown"])
def test_clearing_pending_frame_boxes_never_turns_it_into_a_negative(storage, presence):
    draft = deepcopy(storage[1])
    frame = draft["frames"][0]
    frame.update(review_status="pending", minion_presence=presence, all_identifiable_units_labelled=False)
    draft["unit_annotations"] = [a for a in draft["unit_annotations"]
                                 if (a["recording_id"], a["frame_id"]) != (frame["recording_id"], frame["frame_id"])]
    output = storage[0] / "outputs/pending.json"
    api().save_annotation_revision(request(storage, draft), output)
    saved = load_evidence(output)
    assert saved["frames"][0]["review_status"] == "pending"
    assert saved["frames"][0]["minion_presence"] == presence
    assert saved["confirmed_absent_intervals"] == []


@pytest.mark.parametrize("bad", ["missing_boxes", "incomplete_review", "dangling_frame", "dangling_play"])
def test_whole_draft_validation_rejects_invalid_revision_before_creating_files(storage, bad):
    draft = deepcopy(storage[1])
    if bad == "missing_boxes":
        draft["unit_annotations"] = [a for a in draft["unit_annotations"] if a["frame_id"] != "play_1_frame_1"]
    if bad == "incomplete_review": draft["frames"][0]["all_identifiable_units_labelled"] = False
    if bad == "dangling_frame": draft["unit_annotations"][0]["frame_id"] = "missing"
    if bad == "dangling_play": draft["unit_annotations"][0]["deployment_id"] = "missing"
    output = storage[0] / "outputs/invalid/new.json"
    with pytest.raises(EvidenceError):
        api().save_annotation_revision(request(storage, draft), output)
    assert not output.exists()
    assert not output.with_name("new.units.json").exists()


def test_revision_keeps_non_target_units_and_explicit_semantic_uncertainty(storage):
    draft = deepcopy(storage[1])
    for number, (owner, source, form) in enumerate((("own", "minions", "normal"),
                                                   ("opponent", "minion_horde", "evolved"),
                                                   ("unknown", "unknown", "unknown"))):
        row = deepcopy(draft["unit_annotations"][number])
        row.update(annotation_id=f"extra_{number}", deployment_id=None, owner=owner, source_card=source, form=form)
        row["normalized_bbox"]["y"] = 0.5
        draft["unit_annotations"].append(row)
    output = storage[0] / "outputs/extra.json"
    api().save_annotation_revision(request(storage, draft), output)
    saved = load_evidence(output)
    assert [(a["owner"], a["source_card"], a["form"]) for a in saved["unit_annotations"][-3:]] == [
        ("own", "minions", "normal"), ("opponent", "minion_horde", "evolved"), ("unknown", "unknown", "unknown")]


@pytest.mark.parametrize("location", ["tracked", "outside", "relative"])
def test_destination_rejects_nonprivate_or_implicit_paths_with_sanitized_errors(storage, location):
    root = storage[0]
    output = {"tracked": root / "draft.json", "outside": root.parent / "private_name.json",
              "relative": Path("outputs/new.json")}[location]
    with pytest.raises(EvidenceError) as error:
        api().save_annotation_revision(request(storage), output)
    assert str(root) not in str(error.value)
    assert "private_name" not in str(error.value)
    assert not output.exists()


def test_unit_module_import_does_not_create_a_tk_window():
    import tkinter
    assert tkinter._default_root is None
    api()
    assert tkinter._default_root is None


def test_partial_second_file_failure_removes_only_new_pair(storage, monkeypatch):
    module = api()
    output = storage[0] / "outputs/failed/new.json"
    originals = storage[2].read_bytes(), storage[3].read_bytes()
    write = module.os.write
    writes = 0

    def fail_second(fd, raw):
        nonlocal writes
        writes += 1
        if writes == 2:
            write(fd, raw[:10])
            raise OSError("private_name must not be exposed")
        return write(fd, raw)

    monkeypatch.setattr(module.os, "write", fail_second)
    with pytest.raises(EvidenceError) as error:
        module.save_annotation_revision(request(storage), output)
    assert "private_name" not in str(error.value)
    assert not output.exists()
    assert not output.with_name("new.units.json").exists()
    assert (storage[2].read_bytes(), storage[3].read_bytes()) == originals


def test_cleanup_failure_is_reported_without_exposing_private_path(storage, monkeypatch):
    module = api()
    output = storage[0] / "outputs/cleanup/new.json"
    write = module.os.write
    unlink = Path.unlink
    writes = 0

    def fail_second(fd, raw):
        nonlocal writes
        writes += 1
        if writes == 2:
            raise OSError("private_name")
        return write(fd, raw)

    def fail_cleanup(path, *args, **kwargs):
        if path in {output, output.with_name("new.units.json")}:
            raise OSError("private_name")
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(module.os, "write", fail_second)
    monkeypatch.setattr(Path, "unlink", fail_cleanup)
    with pytest.raises(EvidenceError) as error:
        module.save_annotation_revision(request(storage), output)
    assert "cleanup" in str(error.value).lower()
    assert "private_name" not in str(error.value)


def test_paired_revision_is_accepted_by_actual_task2_disk_binding(checked_disk):
    root, draft, development, old_lock = checked_disk
    old_labels = root / draft["annotation_sources"][0]["path"]
    before = old_labels.read_bytes(), old_lock.read_bytes()
    output = root / "outputs/revision/bound.json"
    api().save_annotation_revision({"draft": draft, "data_root": root,
                                    "annotation_source_id": "revision_2"}, output)
    saved = load_evidence(output)
    indexes = dataset.load_dataset_indexes(saved, root, development_lock_path=old_lock)
    payload = dataset.bind_dataset(saved, indexes, development)
    assert payload["derived"]["counts"]["confirmed_target_deployments"] == 8
    assert payload["derived"]["counts"]["target_positive_matches"] == 4
    assert (old_labels.read_bytes(), old_lock.read_bytes()) == before


def _run_tk_child(command, folder, timeout=120):
    """One process, unchanged environment/cwd; retain output and fail closed."""
    from xml.etree import ElementTree
    folder.mkdir(parents=True, exist_ok=True)
    timed_out = False
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=Path.cwd(), timeout=timeout)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b"", exc.stderr or b"", None
        timed_out = True
    (folder / "stdout.log").write_bytes(stdout)
    (folder / "stderr.log").write_bytes(stderr)
    (folder / "result.json").write_text(json.dumps({"exit_code": code, "timed_out": timed_out}), encoding="utf-8")
    output = (stdout + b"\n" + stderr).decode("utf-8", errors="replace")
    if timed_out or code != 0 or any(marker in output for marker in (
            "Traceback (most recent call last)", "Exception in Tkinter callback", "Exception ignored in:")):
        pytest.fail(f"Isolated Tk child failed (exit={code}, timeout={timed_out}):\n{output}")
    try:
        cases = ElementTree.parse(folder / "results.xml").findall(".//testcase")
    except (OSError, ElementTree.ParseError):
        pytest.fail(f"Isolated Tk child result is missing or invalid:\n{output}")
    if len(cases) != 1 or any(case.find(tag) is not None for case in cases for tag in ("skipped", "failure", "error")):
        pytest.fail(f"Isolated Tk child did not execute exactly one passing GUI case:\n{output}")


def _isolated_tk_case(case, checked_disk):
    node = str(Path(__file__).resolve()) + "::" + case
    if getattr(sys, "_unit_annotation_smoke_case", None) == node:
        return False
    folder = checked_disk[0] / "outputs/tk-smoke"
    program = ("import sys,pytest; sys._unit_annotation_smoke_case=sys.argv[1]; "
               "raise SystemExit(pytest.main([sys.argv[1],'-q','-s','--tb=short','-rs','--junitxml='+sys.argv[2]]))")
    _run_tk_child([sys.executable, "-c", program, node, str(folder / "results.xml")], folder)
    return True


def _withdrawn_tk(factory=None):
    import tkinter
    try:
        root = (factory or tkinter.Tk)()
    except tkinter.TclError as exc:
        message = str(exc).lower()
        if message == "no display name and no $display environment variable":
            pytest.skip("Tk display unavailable: no display name and no DISPLAY environment variable")
        if message.startswith("couldn't connect to display "):
            pytest.skip("Tk display unavailable: cannot connect to declared display")
        if (message.startswith("can't find a usable init.tcl in the following directories:")
                or message == "can't find package tk"):
            pytest.skip("Tcl/Tk runtime unavailable: required initialization runtime not found")
        raise
    root.withdraw()
    return root


@pytest.fixture
def window():
    if not getattr(sys, "_unit_annotation_smoke_case", None):
        yield None  # The parent runs only the checked child, not a second GUI.
        return
    root = _withdrawn_tk()
    yield root
    root.destroy()


def editor(checked_disk, window):
    root, draft, _, old_lock = checked_disk
    indexes = dataset.load_dataset_indexes(draft, root, development_lock_path=old_lock)
    return api()._Annotator(window, draft, indexes, root / "outputs/gui-revisions")


def test_withdrawn_tk_drag_and_delete_preserve_existing_units_and_frame_binding(checked_disk, window):
    if _isolated_tk_case("test_withdrawn_tk_drag_and_delete_preserve_existing_units_and_frame_binding", checked_disk):
        return
    app = editor(checked_disk, window)
    window.update()
    frame = app.draft["frames"][0]
    original = deepcopy(app.draft["unit_annotations"])
    left, top, width, height = app.display_rect
    app._drag_start(SimpleNamespace(x=left + width * .7, y=top + height * .5))
    app._drag_end(SimpleNamespace(x=left + width * .8, y=top + height * .6))
    row = app.draft["unit_annotations"][-1]
    assert row["recording_id"] == frame["recording_id"]
    assert row["frame_id"] == frame["frame_id"]
    assert row["normalized_bbox"] == pytest.approx({"x": .7, "y": .5, "width": .1, "height": .1})
    assert frame["review_status"] == "pending"
    app.units.selection_clear(0, "end")
    app.units.selection_set(3)
    app._delete_unsaved()
    assert app.draft["unit_annotations"] == original
    assert frame["minion_presence"] == "positive"
    app.units.selection_set(0)
    app._delete_unsaved()
    assert app.draft["unit_annotations"] == original


def test_withdrawn_tk_complete_review_save_and_next_preserve_uncertain_unit_metadata(checked_disk, window):
    if _isolated_tk_case("test_withdrawn_tk_complete_review_save_and_next_preserve_uncertain_unit_metadata", checked_disk):
        return
    app = editor(checked_disk, window)
    left, top, width, height = app.display_rect
    app._drag_start(SimpleNamespace(x=left + width * .7, y=top + height * .5))
    app._drag_end(SimpleNamespace(x=left + width * .8, y=top + height * .6))
    app.owner.set("own")
    app.source_card.set("minion_horde")
    app.form.set("unknown")
    app.unit_review.set("verified")
    app._apply_metadata()
    app.frame_review.set("complete")
    app.presence.set("positive")
    app.full_review.set(True)
    app.reviewer.set("Synthetic reviewer")
    app.review_notes.set("All visible units checked in synthetic image")
    app._save()
    assert app.last_saved_path is not None
    saved = load_evidence(app.last_saved_path)
    assert saved["frames"][0]["all_identifiable_units_labelled"] is True
    assert saved["unit_annotations"][-1]["owner"] == "own"
    assert saved["unit_annotations"][-1]["form"] == "unknown"
    assert saved["unit_annotations"][-1]["deployment_id"] is None
    prior_frame_id = app.draft["frames"][app.frame_index]["frame_id"]
    app._next()
    assert app.frame_index == 1
    assert app.draft["frames"][app.frame_index]["frame_id"] != prior_frame_id


def test_launch_rejects_a_plain_snapshot_without_creating_a_gui(storage):
    import tkinter
    assert tkinter._default_root is None
    with pytest.raises(EvidenceError):
        api().launch_annotator(storage[2], {}, storage[0] / "outputs/gui")
    assert tkinter._default_root is None


def test_launch_uses_checked_disk_and_real_withdrawn_tk_mainloop(checked_disk, monkeypatch):
    if _isolated_tk_case("test_launch_uses_checked_disk_and_real_withdrawn_tk_mainloop", checked_disk):
        return
    import tkinter
    root, draft, _, old_lock = checked_disk
    path = root / "outputs/gui-input.json"
    path.write_bytes(canonical_bytes(draft) + b"\n")
    indexes = dataset.load_dataset_indexes(draft, root, development_lock_path=old_lock)
    factory = tkinter.Tk

    def withdrawn_window():
        window = _withdrawn_tk(factory)
        window.after(30, window.quit)
        return window

    monkeypatch.setattr(tkinter, "Tk", withdrawn_window)
    api().launch_annotator(path, indexes, root / "outputs/gui-launched")
    assert tkinter._default_root is None


def test_edge_box_float_rounding_remains_inside_the_normalized_image():
    box = api().canvas_box_to_normalized((1, 0, 11, 11), (11, 11), (0, 0, 11, 11))
    assert box == pytest.approx([1 / 11, 0, 10 / 11, 1])
    assert valid_type(dict(zip(("x", "y", "width", "height"), box)), "box")


def test_next_image_failure_keeps_original_frame_and_canvas_binding(checked_disk, window):
    if _isolated_tk_case("test_next_image_failure_keeps_original_frame_and_canvas_binding", checked_disk):
        return
    app = editor(checked_disk, window)
    original_frame = app._frame()["frame_id"]
    original_image = app.image
    next_path = checked_disk[0] / app.draft["frames"][1]["image_path"]
    next_path.write_bytes(b"Changed synthetic image")
    app._next()
    assert app.frame_index == 0
    assert app._frame()["frame_id"] == original_frame
    assert app.image is original_image


def test_gui_save_rejects_changed_immutable_development_artifact(checked_disk, window):
    if _isolated_tk_case("test_gui_save_rejects_changed_immutable_development_artifact", checked_disk):
        return
    app = editor(checked_disk, window)
    checked_disk[3].write_bytes(checked_disk[3].read_bytes() + b" ")
    app._save()
    assert app.last_saved_path is None
    assert list(app.output_directory.glob("*.json")) == []


def test_launch_rejects_changed_development_file_even_with_same_canonical_digest(checked_disk, monkeypatch):
    import tkinter
    root, draft, _, old_lock = checked_disk
    path = root / "outputs/stale-gui-input.json"
    path.write_bytes(canonical_bytes(draft) + b"\n")
    indexes = dataset.load_dataset_indexes(draft, root, development_lock_path=old_lock)
    old_lock.write_bytes(old_lock.read_bytes() + b" ")
    factory = tkinter.Tk

    def withdrawn_window():
        window = factory()
        window.withdraw()
        window.after(30, window.quit)
        return window

    monkeypatch.setattr(tkinter, "Tk", withdrawn_window)
    with pytest.raises(EvidenceError):
        api().launch_annotator(path, indexes, root / "outputs/stale-gui")
    assert tkinter._default_root is None


def test_unavailable_tk_display_is_a_sanitized_local_error(checked_disk, monkeypatch):
    import tkinter
    root, draft, _, old_lock = checked_disk
    path = root / "outputs/no-display-input.json"
    path.write_bytes(canonical_bytes(draft) + b"\n")
    indexes = dataset.load_dataset_indexes(draft, root, development_lock_path=old_lock)

    def unavailable_window():
        raise tkinter.TclError("private_name display detail")

    monkeypatch.setattr(tkinter, "Tk", unavailable_window)
    with pytest.raises(EvidenceError) as error:
        api().launch_annotator(path, indexes, root / "outputs/no-display-gui")
    assert "private_name" not in str(error.value)


@pytest.mark.parametrize("message", [
    "can't invoke wm command: application has been destroyed",
    "unexpected Tk initialization defect",
])
def test_tk_fixture_propagates_initialization_defects_instead_of_skipping(monkeypatch, message):
    import tkinter

    def broken_window():
        raise tkinter.TclError(message)

    monkeypatch.setattr(tkinter, "Tk", broken_window)
    try:
        with pytest.raises(tkinter.TclError):
            _withdrawn_tk()
    except pytest.skip.Exception:
        pytest.fail("Unexpected Tk initialization fault was hidden as an availability skip")


def test_tk_fixture_only_recognizes_an_explicit_unavailable_display(monkeypatch):
    import tkinter

    def unavailable_window():
        raise tkinter.TclError("no display name and no $DISPLAY environment variable")

    monkeypatch.setattr(tkinter, "Tk", unavailable_window)
    with pytest.raises(pytest.skip.Exception):
        _withdrawn_tk()


@pytest.mark.parametrize("fault", ["nonzero", "callback", "timeout", "skip"])
def test_isolated_tk_child_faults_fail_parent_and_retain_full_output(tmp_path, fault):
    runner = globals().get("_run_tk_child")
    if runner is None:
        pytest.fail("Isolated Tk child faults are not propagated")
    folder = tmp_path / "child-evidence"
    if fault == "skip":
        test_file = tmp_path / "test_explicit_child_skip.py"
        test_file.write_text("import pytest\ndef test_child():\n    pytest.skip('unexpected GUI skip')\n", encoding="utf-8")
        command = [sys.executable, "-m", "pytest", str(test_file), "-q",
                   "--junitxml=" + str(folder / "results.xml")]
    else:
        program = {
            "nonzero": "import sys; print('full child stdout'); print('full child stderr',file=sys.stderr); sys.exit(7)",
            "callback": "import sys; print('full child stdout'); print('Exception in Tkinter callback\\nTraceback (most recent call last):\\ncallback fault',file=sys.stderr)",
            "timeout": "import time; time.sleep(30)",
        }[fault]
        command = [sys.executable, "-c", program]
    with pytest.raises(pytest.fail.Exception):
        runner(command, folder, timeout=.1 if fault == "timeout" else 30)
    result = json.loads((folder / "result.json").read_text(encoding="utf-8"))
    assert (folder / "stdout.log").exists()
    assert (folder / "stderr.log").exists()
    if fault == "nonzero":
        assert result["exit_code"] == 7
        assert (folder / "stdout.log").read_text() == "full child stdout\n"
        assert (folder / "stderr.log").read_text() == "full child stderr\n"
    if fault == "callback":
        assert result["exit_code"] == 0
        assert "callback fault" in (folder / "stderr.log").read_text()
    if fault == "timeout":
        assert result["timed_out"] is True
    if fault == "skip":
        assert result["exit_code"] == 0
        assert "unexpected GUI skip" in (folder / "results.xml").read_text()


def test_tk_loader_error_reports_neutral_initialization_failure(checked_disk, monkeypatch):
    import tkinter
    root, draft, _, old_lock = checked_disk
    path = root / "outputs/loader-error-input.json"
    path.write_bytes(canonical_bytes(draft) + b"\n")
    indexes = dataset.load_dataset_indexes(draft, root, development_lock_path=old_lock)

    def loader_failure():
        raise tkinter.TclError("Can't find a usable tk.tcl: private_name/scrollbar.tcl")

    monkeypatch.setattr(tkinter, "Tk", loader_failure)
    with pytest.raises(EvidenceError) as error:
        api().launch_annotator(path, indexes, root / "outputs/loader-error-gui")
    assert "private_name" not in str(error.value)
    assert "display" not in str(error.value).lower()
    assert "unavailable" not in str(error.value).lower()
