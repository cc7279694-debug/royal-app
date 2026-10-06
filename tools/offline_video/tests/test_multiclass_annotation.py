"""Additive manual multiclass revisions; real synthetic native Tk scenarios."""
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import sys
from xml.etree import ElementTree

import pytest

from clash_tracker_video import evidence_prepare as ep, training_dataset as safe
from clash_tracker_video import multiclass_dataset as dataset
from clash_tracker_video.evidence_contract import EvidenceError, load_evidence
from clash_tracker_video.experiment_lock import canonical_bytes
from clash_tracker_video.multiclass_contract import backend_label_maps
from clash_tracker_video.multiclass_readiness import frame_export_reasons
from multiclass_fixtures import multiclass_disk_fixture


def api():
    try:
        return import_module("clash_tracker_video.multiclass_annotation")
    except ModuleNotFoundError:
        pytest.fail("Manual multiclass annotation APIs are not implemented")


@pytest.fixture
def disk(tmp_path, monkeypatch, request):
    for owner in (ep, safe, dataset):
        monkeypatch.setattr(owner, "PROJECT_ROOT", tmp_path)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("/outputs/\n/local_data/\n", encoding="utf-8")
    return tmp_path, multiclass_disk_fixture(tmp_path, rotation=getattr(request, "param", 0))


def test_group_units_save_without_inventing_new_deployment(disk):
    root, draft = disk
    original = deepcopy(draft)
    old = root / draft["annotation_sources"][0]["path"]
    old_bytes = old.read_bytes()
    row = deepcopy(draft["annotations"][0])
    row.update(annotation_id="second_unit", entity_occurrence_id="second_entity")
    row["box"]["x"] = .6
    draft["annotations"].append(row)
    draft["groups"][0]["human_deployment_id"] = None
    saved_path = api().save_multiclass_revision(draft, data_root=root, output=root / "outputs/revision.json")
    saved = load_evidence(saved_path)
    bound = dataset.bind_multiclass(saved, root)
    assert len(bound.draft["groups"]) == len(original["groups"])
    assert saved["groups"][0]["human_deployment_id"] is None
    assert len([a for a in saved["annotations"] if a["appearance_group_id"] == row["appearance_group_id"]]) == 2
    assert saved["selection"] is None and saved["backend_label_maps"] == {}
    assert old.read_bytes() == old_bytes


def test_edited_rows_bind_new_complete_sidecar_not_old_rows(disk):
    root, draft = disk
    draft["annotations"][0]["box"]["x"] = .15
    path = api().save_multiclass_revision(draft, data_root=root, output=root / "outputs/edited.json")
    saved = load_evidence(path)
    labels = load_evidence(root / saved["annotation_sources"][0]["path"])
    assert set(labels) == {"schema_version", "annotation_source_id", "annotations"}
    assert len(labels["annotations"]) == len(draft["annotations"])
    assert saved["annotations"][0]["box"]["x"] == .15
    dataset.bind_multiclass(saved, root)


@pytest.mark.parametrize("artifact", ["sidecar", "png"])
def test_changed_old_artifact_rejected_without_publishing_revision(disk, artifact):
    root, draft = disk
    path = root / (draft["annotation_sources"][0]["path"] if artifact == "sidecar" else draft["frames"][0]["image_path"])
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(EvidenceError):
        api().save_multiclass_revision(draft, data_root=root, output=root / "outputs/new.json")
    assert not (root / "outputs/new.json").exists()
    assert not (root / "outputs/new.labels.json").exists()


@pytest.mark.parametrize("existing", ["draft", "sidecar"])
def test_revision_collision_preserves_existing_bytes(disk, existing):
    root, draft = disk
    output = root / "outputs/new.json"
    preserved = output if existing == "draft" else root / "outputs/new.labels.json"
    preserved.write_bytes(b"original private artifact")
    with pytest.raises(EvidenceError):
        api().save_multiclass_revision(draft, data_root=root, output=output)
    assert preserved.read_bytes() == b"original private artifact"
    assert set((root / "outputs").glob("new*.json")) == {preserved}


@pytest.mark.parametrize("fault", ["half_sidecar", "second_file", "fsync", "close"])
def test_paired_write_failure_cleans_only_new_pair(disk, monkeypatch, fault):
    root, draft = disk
    module = api()
    old = root / draft["annotation_sources"][0]["path"]
    old_bytes = old.read_bytes()
    write, fsync, close = module.os.write, module.os.fsync, module.os.close
    calls = 0

    def failing_write(fd, raw):
        nonlocal calls
        calls += 1
        if fault == "half_sidecar" and calls == 1:
            return write(fd, raw[:10])
        if (fault == "half_sidecar" and calls == 2) or (fault == "second_file" and calls == 2):
            raise OSError("private detail")
        return write(fd, raw)

    def failing_fsync(fd):
        if fault == "fsync":
            raise OSError("private detail")
        return fsync(fd)

    def failing_close(fd):
        close(fd)
        if fault == "close":
            raise OSError("private detail")

    monkeypatch.setattr(module.os, "write", failing_write)
    monkeypatch.setattr(module.os, "fsync", failing_fsync)
    monkeypatch.setattr(module.os, "close", failing_close)
    with pytest.raises(EvidenceError) as error:
        module.save_multiclass_revision(draft, data_root=root, output=root / "outputs/new.json")
    assert "private detail" not in str(error.value)
    assert old.read_bytes() == old_bytes
    assert not list((root / "outputs").glob("new*.json"))


def _native_case(request, disk):
    """Actual fresh-process Tk; parent fails on skip/native error/timeout."""
    node = str(Path(__file__).resolve()) + "::" + request.node.name
    if getattr(sys, "_multiclass_native_case", None) == node:
        return False
    folder = disk[0] / "outputs/native-evidence"
    folder.mkdir()
    program = ("import sys,pytest; sys._multiclass_native_case=sys.argv[1]; "
               "raise SystemExit(pytest.main([sys.argv[1],'-q','-s','--tb=short','-rs','--junitxml='+sys.argv[2]]))")
    try:
        result = subprocess.run([sys.executable, "-c", program, node, str(folder / "results.xml")],
                                cwd=Path.cwd(), capture_output=True, timeout=180)
        stdout, stderr, code, timed_out = result.stdout, result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code, timed_out = exc.stdout or b"", exc.stderr or b"", None, True
    (folder / "stdout.log").write_bytes(stdout)
    (folder / "stderr.log").write_bytes(stderr)
    (folder / "result.json").write_text(json.dumps({"exit_code": code, "timed_out": timed_out}), encoding="utf-8")
    output = (stdout + b"\n" + stderr).decode("utf-8", errors="replace")
    assert not timed_out and code == 0, output
    assert not any(marker in output for marker in ("Exception in Tkinter callback", "Traceback (most recent call last)", "Exception ignored in:")), output
    cases = ElementTree.parse(folder / "results.xml").findall(".//testcase")
    assert len(cases) == 1 and all(cases[0].find(tag) is None for tag in ("skipped", "failure", "error")), output
    return True


@pytest.fixture
def window():
    if not getattr(sys, "_multiclass_native_case", None):
        yield None
        return
    import tkinter
    native = tkinter.Tk()  # No availability skip: native failures must propagate.
    native.withdraw()
    yield native
    native.destroy()


def editor(disk, window):
    root, draft = disk
    return api()._MulticlassAnnotator(window, dataset.bind_multiclass(draft, root), root / "outputs/gui")


def unlabelled(draft):
    result = deepcopy(draft)
    result["annotations"], result["annotation_sources"] = [], []
    for frame in result["frames"]:
        frame["review_state"] = "pending"
    for coverage in result["coverage"]:
        coverage.update(exhaustive_state="pending", exhaustive_for_classes=[], reviewed_regions=[])
    return result


def drag(app, *, x=.6, y=.5):
    left, top, width, height = app.display_rect
    app._drag_start(SimpleNamespace(x=left + width * x, y=top + height * y))
    app._drag_end(SimpleNamespace(x=left + width * (x + .1), y=top + height * (y + .1)))


def test_class_owner_form_are_independent_controls(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    app.visual_class.set("unit.speck")
    drag(app)
    row = app._rows()[-1]
    assert row["owner"] == row["observed_form"] == "unknown"
    app.owner.set("own")
    app.form.set("evolved")
    app.visual_class.set("unit.guard")
    app._apply_metadata()
    assert (row["visual_class_id"], row["owner"], row["observed_form"]) == ("unit.guard", "own", "evolved")
    assert row["appearance_group_id"] is None and row["entity_occurrence_id"] is None
    assert app.draft["groups"] == disk[1]["groups"]
    assert app._frame()["review_state"] == "pending"
    assert app._coverage()["exhaustive_state"] == "pending"
    assert app.draft["selection"] is None


def test_unknown_object_prevents_exhaustive_export(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    fid = disk[1]["frames"][0]["frame_id"]
    app.frame_index = next(i for i, frame in enumerate(app.draft["frames"]) if frame["frame_id"] == fid)
    app._show_frame(app._load_image(app.frame_index))
    app.unknown_object.set(True)
    drag(app)
    assert len(app._rows()) == 2  # Existing boxes, not invented unknown class.
    app.reviewer.set("Synthetic reviewer")
    app.full_review.set(True)
    app.exhaustive.set(True)
    app.class_coverage.selection_set(0, "end")
    app._save()
    assert app.last_saved_path is not None
    saved = load_evidence(app.last_saved_path)
    frame = next(r for r in saved["frames"] if r["frame_id"] == fid)
    coverage = next(r for r in saved["coverage"] if r["frame_id"] == fid)
    assert coverage["ignore_regions"][0]["visual_class_ids"] == []
    assert frame["review_state"] == "pending"
    assert coverage["exhaustive_state"] == "pending"
    ids = [r["visual_class_id"] for r in saved["taxonomy"]["classes"]]
    saved["selection"] = {"selected_class_ids": ids,
        "class_decisions": [{"visual_class_id": cid, "selected": True, "reason": "Synthetic selection only"} for cid in ids],
        "scale_snapshot_digest": "a" * 64, "policy_id": "dev_moving_area_quantiles_v1"}
    saved["backend_label_maps"] = backend_label_maps(ids)
    reasons = frame_export_reasons(saved, fid)
    assert "frame_review_not_complete" in reasons and "coverage_not_complete" in reasons
    assert "selection_missing" not in reasons


def test_invalid_save_does_not_advance_navigation(request, disk, window, monkeypatch):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    old_id, old_image = app._frame()["frame_id"], app.image
    app.visual_class.set("unit.speck")
    drag(app)
    row = app._rows()[-1]
    row["box"]["width"] = 2
    app._save()
    app._next()
    assert app.last_saved_path is None and app.frame_index == 0
    assert app._frame()["frame_id"] == old_id and app.image is old_image
    assert row in app._rows()
    assert not list(app.output_directory.glob("*.json"))
    # Correcting the retained pending box allows navigation after explicit choice.
    from tkinter import messagebox
    monkeypatch.setattr(messagebox, "askyesnocancel", lambda *a, **k: False)
    row["box"]["width"] = .1
    app._next()
    assert app.frame_index == 1
    app._previous()
    assert app.frame_index == 0 and row in app._rows()


def test_next_image_failure_keeps_original_edit_state(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    original = app.image
    (disk[0] / app.draft["frames"][1]["image_path"]).write_bytes(b"bad image")
    app._next()
    assert app.frame_index == 0 and app.image is original


def test_unsaved_navigation_cancel_retains_current_canvas(request, disk, window, monkeypatch):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    app.visual_class.set("unit.speck")
    drag(app)
    from tkinter import messagebox
    monkeypatch.setattr(messagebox, "askyesnocancel", lambda *a, **k: None)
    app._next()
    assert app.frame_index == 0 and len(app._rows()) == 3


def test_canvas_letterbox_drag_is_rejected_without_label(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    app.visual_class.set("unit.speck")
    rows = deepcopy(app._rows())
    left, top, width, height = app.display_rect
    app._drag_start(SimpleNamespace(x=left - 1, y=top + height * .5))
    app._drag_end(SimpleNamespace(x=left + width * .1, y=top + height * .6))
    assert app._rows() == rows


def test_launch_checks_disk_before_native_window(disk, monkeypatch):
    root, draft = disk
    import tkinter
    assert tkinter._default_root is None
    path = root / "outputs/input.json"
    path.write_bytes(canonical_bytes(draft))
    (root / draft["annotation_sources"][0]["path"]).write_bytes(b"stale")
    with pytest.raises(EvidenceError):
        api().launch_multiclass_annotator(path, data_root=root, output_directory=root / "outputs/gui")
    assert tkinter._default_root is None


def test_launch_runs_real_native_window_and_releases_it(request, disk, monkeypatch):
    if _native_case(request, disk):
        return
    import tkinter
    root, draft = disk
    path = root / "outputs/input.json"
    path.write_bytes(canonical_bytes(draft))
    factory = tkinter.Tk

    def real_window():
        native = factory()
        native.withdraw()
        native.after(40, native.quit)
        return native

    monkeypatch.setattr(tkinter, "Tk", real_window)
    api().launch_multiclass_annotator(path, data_root=root, output_directory=root / "outputs/gui")
    assert tkinter._default_root is None


def test_first_unit_without_previous_sidecar_can_be_saved(request, disk, window):
    if _native_case(request, disk):
        return
    root, draft = disk
    draft = unlabelled(draft)
    app = api()._MulticlassAnnotator(window, dataset.bind_multiclass(draft, root), root / "outputs/gui")
    app.visual_class.set("unit.speck")
    drag(app)
    app._save()
    assert app.last_saved_path is not None
    saved = load_evidence(app.last_saved_path)
    assert len(saved["annotations"]) == 1
    assert saved["annotations"][0]["review_state"] == "pending"
    assert saved["annotations"][0]["owner"] == saved["annotations"][0]["observed_form"] == "unknown"
    assert saved["annotation_sources"][0]["sha256"] != "0" * 64
    dataset.bind_multiclass(saved, root)


def test_unapplied_box_controls_cannot_be_silently_saved_or_advanced(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    app.units.selection_set(0)
    app._selected()
    old = deepcopy(app._rows()[0])
    app.owner.set("unknown")
    app._save()
    app._next()
    assert app.last_saved_path is None and app.frame_index == 0
    assert app.dirty and app.owner.get() == "unknown"
    assert app._rows()[0] == old
    assert not list(app.output_directory.glob("*.json"))


def test_gui_uses_intake_then_timestamp_not_hashed_frame_order(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    assert [f["recording_id"] for f in app.draft["frames"]] == ["recording_1"] * 3 + ["recording_2"] * 3
    assert [f["timestamp_seconds"] for f in app.draft["frames"]] == [10, 20, 30, 10, 20, 30]


@pytest.mark.parametrize("disk", [90], indirect=True)
def test_original_rotated_image_uses_one_normalized_coordinate_basis(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    assert app.image_size == (48, 64)
    app.visual_class.set("unit.speck")
    drag(app, x=.6, y=.5)
    assert app._rows()[-1]["box"] == pytest.approx({"x": .6, "y": .5, "width": .1, "height": .1})


def test_existing_zero_hash_placeholder_is_not_an_old_sidecar_bypass(disk):
    root, draft = disk
    draft = unlabelled(draft)
    fake_path = root / "outputs/pending.labels.json"
    fake_path.write_bytes(b"original private label data")
    draft["annotation_sources"] = [{"annotation_source_id": "pending_labels", "path": "outputs/pending.labels.json", "sha256": "0" * 64}]
    with pytest.raises(EvidenceError):
        api().save_multiclass_revision(draft, data_root=root, output=root / "outputs/new.json")
    assert fake_path.read_bytes() == b"original private label data"
    assert not (root / "outputs/new.json").exists()


def test_first_box_can_receive_explicit_manual_review_before_materialization(request, disk, window):
    if _native_case(request, disk):
        return
    root, draft = disk
    app = api()._MulticlassAnnotator(window, dataset.bind_multiclass(unlabelled(draft), root), root / "outputs/gui")
    app.visual_class.set("unit.speck")
    drag(app)
    app.owner.set("opponent")
    app.form.set("normal")
    app.unit_review.set("verified")
    app.reviewer.set("Synthetic reviewer")
    app._apply_metadata()
    app._save()
    assert app.last_saved_path is not None
    saved = load_evidence(app.last_saved_path)
    assert saved["annotations"][0]["review_state"] == "verified"
    assert saved["annotations"][0]["owner"] == "opponent"
    assert saved["frames"][0]["review_state"] == "pending"
    assert saved["groups"] == app.original["groups"]  # No inferred group from a reviewed box.
    dataset.bind_multiclass(saved, root)


def test_native_callback_failure_reaches_launch_caller(request, disk, monkeypatch):
    if _native_case(request, disk):
        return
    import tkinter
    root, draft = disk
    path = root / "outputs/input.json"
    path.write_bytes(canonical_bytes(draft))
    factory = tkinter.Tk

    def actual_callback_fault():
        raise RuntimeError("private callback detail")

    def real_window():
        native = factory()
        native.withdraw()
        native.after(40, actual_callback_fault)
        return native

    monkeypatch.setattr(tkinter, "Tk", real_window)
    with pytest.raises(EvidenceError) as error:
        api().launch_multiclass_annotator(path, data_root=root, output_directory=root / "outputs/gui")
    assert "callback" in str(error.value).lower() and "private callback detail" not in str(error.value)
    assert tkinter._default_root is None


def test_cross_box_selection_retains_unapplied_controls_and_dirty_state(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    window.deiconify()
    window.update()
    app.units.selection_set(0)
    app.units.event_generate("<<ListboxSelect>>")
    window.update()
    assert app.owner.get() == "opponent"  # Native selection callback executed.
    original = deepcopy(app._rows()[0])
    app.occlusion.set("partial")
    app.units.selection_clear(0, "end")
    app.units.selection_set(1)
    app.units.event_generate("<<ListboxSelect>>")
    window.update()
    assert app.units.curselection() == (0,)
    assert app.occlusion.get() == "partial" and app.dirty
    assert app._rows()[0] == original
    app._save()
    assert app.last_saved_path is None and app.dirty
    # Explicitly applying A permits selecting B; no implicit metadata copy.
    app._apply_metadata()
    app.units.selection_clear(0, "end")
    app.units.selection_set(1)
    app.units.event_generate("<<ListboxSelect>>")
    window.update()
    assert app.units.curselection() == (1,)
    assert app._rows()[0]["occlusion"] == "partial"
    assert app.occlusion.get() == "none"
    app._save()
    assert app.last_saved_path is not None
    saved = load_evidence(app.last_saved_path)
    assert next(a for a in saved["annotations"] if a["annotation_id"] == original["annotation_id"])["occlusion"] == "partial"


def test_deleted_selected_box_does_not_resurrect_or_block_another_selection(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    window.deiconify()
    window.update()
    app.units.selection_set(0)
    app.units.event_generate("<<ListboxSelect>>")
    window.update()
    old_id = app._rows()[0]["annotation_id"]
    app._delete()
    app.units.selection_set(0)
    app.units.event_generate("<<ListboxSelect>>")
    window.update()
    assert old_id not in {a["annotation_id"] for a in app._rows()}
    assert app.owner.get() == "own"


def test_new_box_mode_requires_applied_old_controls_then_keeps_unknown_defaults(request, disk, window):
    if _native_case(request, disk):
        return
    app = editor(disk, window)
    app.units.selection_set(0)
    app._selected()
    app.occlusion.set("partial")
    app._new_box()
    assert app.units.curselection() == (0,) and app.occlusion.get() == "partial"
    app._apply_metadata()
    app._new_box()
    assert app.units.curselection() == ()
    app.visual_class.set("unit.guard")
    drag(app)
    assert app._rows()[-1]["visual_class_id"] == "unit.guard"
    assert app._rows()[-1]["owner"] == app._rows()[-1]["observed_form"] == "unknown"
    assert app._rows()[-1]["appearance_group_id"] is None
