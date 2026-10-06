"""Checked synthetic multiclass artifacts and immutable, ordered freezes."""
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
import json
import os
from fractions import Fraction
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest
from PIL import Image
import av

from clash_tracker_video import evidence_prepare as ep, training_dataset as safe
from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.experiment_lock import canonical_bytes
from clash_tracker_video.multiclass_contract import backend_label_maps
from multiclass_fixtures import multiclass_disk_fixture, write_multiclass_sidecars


def api():
    try:
        return import_module("clash_tracker_video.multiclass_dataset")
    except ModuleNotFoundError:
        pytest.fail("Checked multiclass dataset APIs are not implemented")


@pytest.fixture
def disk(tmp_path, monkeypatch):
    for owner in (ep, safe, api()):
        monkeypatch.setattr(owner, "PROJECT_ROOT", tmp_path)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("/outputs/\n/local_data/\n", encoding="utf-8")
    return tmp_path, multiclass_disk_fixture(tmp_path)


def selection(draft, snapshot):
    result = deepcopy(draft)
    ids = [r["visual_class_id"] for r in result["taxonomy"]["classes"]]
    result["selection"] = {"selected_class_ids": ids,
        "class_decisions": [{"visual_class_id": cid, "selected": True, "reason": "Synthetic support"} for cid in ids],
        "scale_snapshot_digest": snapshot["digest"], "policy_id": "dev_moving_area_quantiles_v1"}
    result["backend_label_maps"] = backend_label_maps(ids)
    return result


def scale(disk):
    root, draft = disk
    return api().freeze_scale_snapshot(api().bind_multiclass(draft, root), root / "outputs/scale")


def test_freeze_requires_prior_full_candidate_snapshot(disk):
    root, draft = disk
    module = api()
    prior = scale(disk)
    bound = module.bind_multiclass(selection(draft, prior), root)
    for missing in (None, deepcopy(dict(prior))):
        with pytest.raises(EvidenceError):
            module.freeze_multiclass_dataset(bound, missing, root / "outputs/final")
    assert not (root / "outputs/final").exists()


def test_selection_cannot_omit_qualified_small_from_inventory(disk):
    root, draft = disk
    prior = scale(disk)
    selected = selection(draft, prior)
    # A post-snapshot GT change must not silently change the full-pool basis.
    selected["annotations"] = [a for a in selected["annotations"] if a["visual_class_id"] != "unit.speck"]
    selected["annotation_sources"][0]["path"] = "outputs/labels/new-revision.json"
    write_multiclass_sidecars(root, selected)
    with pytest.raises(EvidenceError):
        api().freeze_multiclass_dataset(api().bind_multiclass(selected, root), prior, root / "outputs/final")


def test_frame_swapped_after_bind_is_rejected(disk):
    root, draft = disk
    bound = api().bind_multiclass(draft, root)
    frame = draft["frames"][0]
    Image.new("RGB", (frame["image_width"], frame["image_height"]), "purple").save(root / frame["image_path"])
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/scale")
    assert not (root / "outputs/scale").exists()


def test_same_version_different_digest_cannot_overwrite(disk):
    root, draft = disk
    changed = deepcopy(draft)
    changed["matches"][0]["notes"] = "Different declared note"
    first, second = [api().bind_multiclass(d, root) for d in (draft, changed)]
    directory = root / "outputs/race"
    def freeze(bound):
        try:
            return api().freeze_scale_snapshot(bound, directory)
        except EvidenceError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(freeze, (first, second)))
    assert sum(r is not None for r in outcomes) == 1
    paths = list(directory.iterdir())
    assert len(paths) == 1
    before = paths[0].read_bytes()
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(first, directory)
    assert paths[0].read_bytes() == before


def test_split_and_scale_policy_are_digest_bound(disk):
    root, draft = disk
    prior = scale(disk)
    changed = deepcopy(draft)
    for row in [*changed["recordings"], *changed["split_assignment"]]:
        row["split"] = "development_validation" if row["split"] == "train" else "train"
    other = api().freeze_scale_snapshot(api().bind_multiclass(changed, root), root / "outputs/other-scale")
    assert other["digest"] != prior["digest"]
    path = next((root / "outputs/scale").iterdir())
    forged = json.loads(path.read_bytes())
    forged["payload"]["scale_report"]["policy_id"] = "other_policy"
    forged["digest"] = sha256(canonical_bytes({k: v for k, v in forged.items() if k != "digest"})).hexdigest()
    path.write_bytes(canonical_bytes(forged))
    with pytest.raises(EvidenceError):
        api().load_scale_snapshot(path, root)


def test_snapshot_then_selection_freeze_roundtrip_is_checked(disk):
    root, draft = disk
    original = deepcopy(draft)
    prior = scale(disk)
    assert prior["kind"] == "multiclass_scale_snapshot"
    assert prior["payload"]["draft"]["selection"] is None
    assert prior["payload"]["scale_report"]["candidate_class_ids"] == ["unit.guard", "unit.speck"]
    loaded = api().load_scale_snapshot(next((root / "outputs/scale").iterdir()), root)
    final = api().freeze_multiclass_dataset(api().bind_multiclass(selection(draft, loaded), root),
                                          loaded, root / "outputs/final")
    assert final["payload"]["readiness"]["ready"] is True
    assert final["kind"] == "multiclass_dataset_lock"
    assert api().load_multiclass_dataset_lock(next((root / "outputs/final").iterdir()), root) == final
    assert draft == original


def test_semantic_sets_reorder_stably_but_intake_order_is_bound(disk):
    root, draft = disk
    one = scale(disk)
    changed = deepcopy(draft)
    for key in ("recordings", "matches", "frames", "annotations", "groups", "coverage", "split_assignment"):
        changed[key].reverse()
    for row in changed["coverage"]:
        row["exhaustive_for_classes"].reverse()
    write_multiclass_sidecars(root, changed)
    # Sidecar bytes also matter; retain original file ordering for semantic-only test.
    write_multiclass_sidecars(root, draft)
    changed["annotation_sources"] = deepcopy(draft["annotation_sources"])
    two = api().freeze_scale_snapshot(api().bind_multiclass(changed, root), root / "outputs/reordered")
    assert two["digest"] == one["digest"]
    changed["intake"].reverse()
    three = api().freeze_scale_snapshot(api().bind_multiclass(changed, root), root / "outputs/intake")
    assert three["digest"] != one["digest"]


@pytest.mark.parametrize("artifact", ["source", "index", "report", "label"])
def test_any_declared_dependency_changed_after_bind_is_rejected(disk, artifact):
    root, draft = disk
    bound = api().bind_multiclass(draft, root)
    record = draft["recordings"][0]
    relative = (record["source_path"] if artifact == "source" else
                draft["annotation_sources"][0]["path"] if artifact == "label" else
                record["exports"][0][artifact + "_path"])
    with (root / relative).open("ab") as handle:
        handle.write(b" ")
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/scale")
    assert not (root / "outputs/scale").exists()


def test_load_and_prior_snapshot_recheck_all_disk_dependencies(disk):
    root, draft = disk
    prior = scale(disk)
    bound = api().bind_multiclass(selection(draft, prior), root)
    path = next((root / "outputs/scale").iterdir())
    with path.open("ab") as handle:
        handle.write(b" ")
    with pytest.raises(EvidenceError):
        api().freeze_multiclass_dataset(bound, prior, root / "outputs/final")
    # Re-reading a valid byte-format variation is okay for a new checked handle.
    loaded = api().load_scale_snapshot(path, root)
    final = api().freeze_multiclass_dataset(bound, loaded, root / "outputs/final")
    with (root / draft["annotation_sources"][0]["path"]).open("ab") as handle:
        handle.write(b" ")
    with pytest.raises(EvidenceError):
        api().load_scale_snapshot(path, root)
    with pytest.raises(EvidenceError):
        api().load_multiclass_dataset_lock(next((root / "outputs/final").iterdir()), root)
    assert final["payload"]["readiness"]["ready"]


@pytest.mark.parametrize("relative", ["../outside.mp4", "https://example.test/record.mp4", "//server/record.mp4", "C:/record.mp4"])
def test_unsafe_artifact_paths_are_rejected_without_private_path_leak(disk, relative):
    root, draft = disk
    draft["recordings"][0]["source_path"] = relative
    with pytest.raises(EvidenceError) as caught:
        api().bind_multiclass(draft, root)
    assert str(root) not in str(caught.value)


def test_reference_only_source_cannot_formally_freeze(disk):
    root, draft = disk
    draft["provenance"][0]["allowed_scope"] = "reference_only"
    bound = api().bind_multiclass(draft, root)
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/scale")
    assert not (root / "outputs/scale").exists()


def test_renaming_lock_does_not_reopen_same_version(disk):
    root, draft = disk
    prior = scale(disk)
    directory = root / "outputs/scale"
    path = next(directory.iterdir())
    renamed = path.with_name("renamed.json")
    path.rename(renamed)
    before = renamed.read_bytes()
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(api().bind_multiclass(draft, root), directory)
    assert renamed.read_bytes() == before
    assert api().load_scale_snapshot(renamed, root) == prior


def test_partial_write_removes_only_new_file_preserving_existing_lock(disk, monkeypatch):
    root, draft = disk
    module = api()
    scale(disk)
    directory = root / "outputs/scale"
    path = next(directory.iterdir())
    before = path.read_bytes()
    draft["freeze_version"] = 2
    bound = module.bind_multiclass(draft, root)
    def failed_write(fd, raw):
        raise OSError("Synthetic disk write fault")
    monkeypatch.setattr(module.os, "write", failed_write)
    with pytest.raises(EvidenceError):
        module.freeze_scale_snapshot(bound, directory)
    assert list(directory.iterdir()) == [path]
    assert path.read_bytes() == before


def test_plain_bound_dictionary_cannot_freeze(disk):
    root, draft = disk
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot({"draft": draft, "data_root": root}, root / "outputs/scale")


def test_empty_pending_draft_rejects_external_data_container(disk):
    root, draft = disk
    for key in ("intake", "matches", "recordings", "groups", "frames", "annotations", "annotation_sources", "coverage", "split_assignment"):
        draft[key] = []
    with pytest.raises(EvidenceError):
        api().bind_multiclass(draft, root.parent)


def test_rotated_original_geometry_and_nonzero_origin_bind(disk):
    root, _ = disk
    other = root / "outputs/rotated-container"
    other.mkdir()
    draft = multiclass_disk_fixture(other, rotation=90)
    bound = api().bind_multiclass(draft, other)
    assert {r["recording"]["rotation_degrees"] for r in bound.media_snapshot} == {90}
    assert {(f["image_width"], f["image_height"]) for f in bound.draft["frames"]} == {(48, 64)}
    assert all(r["origin_pts"] != 0 for r in bound.draft["recordings"])


def test_native_30hz_final_frame_rounding_nonzero_origin_is_accepted(disk):
    root, draft = disk
    record = draft["recordings"][0]
    source = root / "local_data/thirty.mp4"
    with av.open(str(source), "w") as container:
        stream = container.add_stream("libx264", rate=30)
        stream.width, stream.height = 64, 48
        stream.pix_fmt = "yuv420p"
        stream.time_base = stream.codec_context.time_base = Fraction(1, 30)
        stream.options = {"bf": "0", "crf": "0"}
        for pts in (30, 330, 630, 930, 5375):
            frame = av.VideoFrame.from_image(Image.new("RGB", (64, 48), "red"))
            frame.pts, frame.time_base = pts, Fraction(1, 30)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    run = root / "outputs/thirty"
    index = ep.prepare_evidence(source, run, recording_id=record["recording_id"], times=[10, 20, 30, 178.1])
    assert index["recording"]["last_frame_seconds"] == 178.16666666666666
    assert index["frames"][-1]["timestamp_seconds"] == 178.16666666666666
    record["source_path"] = "local_data/thirty.mp4"
    for key in ("source_sha256", "width", "height", "rotation_degrees", "time_base", "origin_pts", "origin_time_base", "last_frame_seconds"):
        record[key] = deepcopy(index["recording"][key])
    record["match_segment"]["end_seconds"] = record["last_frame_seconds"]
    record["exports"] = [{"export_id": "export_1", "index_path": "outputs/thirty/index.json",
        "report_path": "outputs/thirty/exports/report.json", "index_sha256": ep.file_hash(run / "index.json"),
        "report_sha256": ep.file_hash(run / "exports/report.json")}]
    for frame, actual in zip([f for f in draft["frames"] if f["recording_id"] == record["recording_id"]], index["frames"]):
        old_id = frame["frame_id"]
        for key in ("frame_id", "timestamp_seconds", "raw_pts", "time_base", "image_width", "image_height"):
            frame[key] = deepcopy(actual[key])
        frame["origin"] = {"raw_pts": record["origin_pts"], "time_base": deepcopy(record["origin_time_base"])}
        frame["image_path"] = (run / actual["image_path"]).relative_to(root).as_posix()
        frame["image_sha256"] = ep.file_hash(root / frame["image_path"])
        for row in [*draft["annotations"], *draft["coverage"]]:
            if row["frame_id"] == old_id:
                row["frame_id"] = frame["frame_id"]
    terminal = deepcopy(draft["frames"][0])
    terminal.update({k: deepcopy(index["frames"][-1][k]) for k in
                     ("frame_id", "raw_pts", "time_base", "timestamp_seconds", "image_width", "image_height")})
    terminal.update(image_path=(run / index["frames"][-1]["image_path"]).relative_to(root).as_posix(),
                    review_state="pending", review_provenance={"method": "pending", "reviewed_by": None, "notes": "Synthetic terminal"})
    terminal["image_sha256"] = ep.file_hash(root / terminal["image_path"])
    draft["frames"].append(terminal)
    write_multiclass_sidecars(root, draft)
    bound = api().bind_multiclass(draft, root)
    assert any(f["timestamp_seconds"] == 178.16666666666666 for f in bound.draft["frames"])
    draft["frames"][-1]["raw_pts"] += 3000
    with pytest.raises(EvidenceError):
        api().bind_multiclass(draft, root)


def test_each_export_keeps_its_path_base_and_conflicting_pixels_cannot_merge(disk):
    root, draft = disk
    record = draft["recordings"][0]
    run = root / "outputs/second-export"
    index = ep.prepare_evidence(root / record["source_path"], run, recording_id=record["recording_id"], times=[10, 20, 30])
    record["exports"].append({"export_id": "export_2", "index_path": "outputs/second-export/index.json",
        "report_path": "outputs/second-export/exports/report.json", "index_sha256": ep.file_hash(run / "index.json"),
        "report_sha256": ep.file_hash(run / "exports/report.json")})
    for frame in draft["frames"]:
        if frame["recording_id"] == record["recording_id"]:
            frame["export_ids"].append("export_2")
    one = api().bind_multiclass(draft, root)
    assert len(one.draft["frames"]) == 6  # requests/copies do not add real frames
    Image.new("RGB", (64, 48), "black").save(run / index["frames"][0]["image_path"])
    with pytest.raises(EvidenceError):
        api().bind_multiclass(draft, root)


@pytest.mark.parametrize("change", ["raw_pts", "report", "labels"])
def test_resigned_declared_hashes_cannot_hide_semantic_conflicts(disk, change):
    root, draft = disk
    if change == "raw_pts":
        draft["frames"][0]["raw_pts"] += 1
    elif change == "report":
        export = draft["recordings"][0]["exports"][0]
        path = root / export["report_path"]
        doc = json.loads(path.read_bytes())
        doc["timeline"]["tolerance_seconds"] = 0.101
        path.write_bytes(canonical_bytes(doc))
        export["report_sha256"] = ep.file_hash(path)
    else:
        source = draft["annotation_sources"][0]
        path = root / source["path"]
        doc = json.loads(path.read_bytes())
        doc["annotations"][0]["owner"] = "unknown"
        path.write_bytes(canonical_bytes(doc))
        source["sha256"] = ep.file_hash(path)
    with pytest.raises(EvidenceError):
        api().bind_multiclass(draft, root)


def test_junction_artifacts_are_rejected(disk):
    root, draft = disk
    link = root / "outputs/junction"
    if os.name != "nt":
        pytest.skip("Windows junction only")
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(root / "local_data")], check=True, capture_output=True)
    try:
        draft["recordings"][0]["source_path"] = "outputs/junction/recording_1.mp4"
        with pytest.raises(EvidenceError):
            api().bind_multiclass(draft, root)
    finally:
        link.rmdir()


def test_symlink_artifacts_are_rejected(disk):
    root, draft = disk
    link = root / "outputs/symlink"
    try:
        link.symlink_to(root / "local_data", target_is_directory=True)
    except OSError as exc:
        if os.name == "nt" and exc.winerror == 1314:
            pytest.skip("Windows symlink privilege unavailable (WinError 1314)")
        raise
    try:
        draft["recordings"][0]["source_path"] = "outputs/symlink/recording_1.mp4"
        with pytest.raises(EvidenceError):
            api().bind_multiclass(draft, root)
    finally:
        link.unlink()


@pytest.mark.parametrize("privacy", ["not_ignored", "tracked"])
def test_artifact_privacy_changes_are_rechecked_on_subsequent_operation(disk, privacy):
    root, draft = disk
    api().bind_multiclass(draft, root)
    if privacy == "not_ignored":
        (root / ".gitignore").write_text("", encoding="utf-8")
    else:
        subprocess.run(["git", "add", "-f", draft["recordings"][0]["source_path"]], cwd=root, check=True)
    with pytest.raises(EvidenceError):
        api().bind_multiclass(draft, root)


def test_pending_unknown_rows_bind_without_becoming_negative_or_ready(disk):
    root, draft = disk
    for frame in draft["frames"]:
        frame["review_state"] = "pending"
    for row in draft["annotations"]:
        row.update(review_state="pending", owner="unknown", observed_form="unknown",
                   appearance_group_id=None, entity_occurrence_id=None, occlusion="unknown")
    for row in draft["coverage"]:
        row.update(exhaustive_state="pending", reviewed_regions=[])
    draft["annotation_sources"][0]["path"] = "outputs/labels/pending.json"
    write_multiclass_sidecars(root, draft)
    bound = api().bind_multiclass(draft, root)
    assert len(bound.draft["annotations"]) == 8
    assert {a["owner"] for a in bound.draft["annotations"]} == {"unknown"}
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/pending-scale")


def test_candidate_scale_from_pending_frame_is_not_final_export_support(disk):
    root, draft = disk
    draft["frames"][0]["review_state"] = "pending"
    prior = scale(disk)
    assert prior["payload"]["scale_report"]["size_coverage_status"] == "SIZE_COVERAGE_SUFFICIENT"
    with pytest.raises(EvidenceError):
        api().freeze_multiclass_dataset(api().bind_multiclass(selection(draft, prior), root),
                                        prior, root / "outputs/final")
    assert not (root / "outputs/final").exists()


def test_unlisted_export_frames_never_supply_gt_or_scale_weight(disk):
    root, draft = disk
    record = draft["recordings"][0]
    run = root / "outputs/extra-locators"
    index = ep.prepare_evidence(root / record["source_path"], run, recording_id=record["recording_id"], times=[0, 10, 20, 30])
    record["exports"].append({"export_id": "locator_2", "index_path": "outputs/extra-locators/index.json",
        "report_path": "outputs/extra-locators/exports/report.json", "index_sha256": ep.file_hash(run / "index.json"),
        "report_sha256": ep.file_hash(run / "exports/report.json")})
    bound = api().bind_multiclass(draft, root)
    assert len(bound.draft["frames"]) == 6
    prior = api().freeze_scale_snapshot(bound, root / "outputs/scale")
    assert prior["payload"]["scale_report"]["class_reports"][2]["all_reviewed"]["area_norm"]["count"] == 4
    extra = run / index["frames"][0]["image_path"]
    assert extra.relative_to(root).as_posix() in bound.file_hashes
    Image.new("RGB", (64, 48), "purple").save(extra)
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/another")
    # Deliberate closed-schema limit: historical hash is not persisted for this
    # unlisted locator; current loader validity is checked, but it has no GT role.
    assert api().load_scale_snapshot(next((root / "outputs/scale").iterdir()), root) == prior


def test_untrusted_dataset_id_is_not_used_as_a_path(disk):
    root, draft = disk
    draft["dataset_id"] = "../synthetic/escape"
    prior = scale(disk)
    paths = list((root / "outputs/scale").iterdir())
    assert len(paths) == 1 and paths[0].parent == root / "outputs/scale"
    assert api().load_scale_snapshot(paths[0], root) == prior
    assert not (root / "synthetic").exists()


def test_scale_freeze_rejects_final_selection_before_creating_output(disk):
    root, draft = disk
    selected = selection(draft, {"digest": "d" * 64})
    bound = api().bind_multiclass(selected, root)
    with pytest.raises(EvidenceError):
        api().freeze_scale_snapshot(bound, root / "outputs/too-late-scale")
    assert not (root / "outputs/too-late-scale").exists()


@pytest.mark.parametrize("fault", ["partial_write_and_close", "fsync", "close"])
def test_io_faults_clean_owned_new_lock_even_when_handle_close_raises(disk, monkeypatch, fault):
    root, draft = disk
    module = api()
    scale(disk)
    directory = root / "outputs/scale"
    prior = next(directory.iterdir())
    before = prior.read_bytes()
    draft["freeze_version"] = 2
    bound = module.bind_multiclass(draft, root)
    real_write, real_close, real_fsync = module.os.write, module.os.close, module.os.fsync
    target_fd, close_fault_raised = None, False
    def write(fd, raw):
        nonlocal target_fd
        target_fd = fd
        if fault == "partial_write_and_close":
            real_write(fd, raw[:17])
            raise OSError("Synthetic partial-byte failure")
        return real_write(fd, raw)
    def close(fd):
        nonlocal close_fault_raised
        real_close(fd)
        if fd == target_fd and fault != "fsync" and not close_fault_raised:
            close_fault_raised = True
            raise OSError("Synthetic handle closed but close reports failure")
    def fsync(fd):
        if fd == target_fd and fault == "fsync":
            raise OSError("Synthetic fsync failure")
        return real_fsync(fd)
    monkeypatch.setattr(module.os, "write", write)
    monkeypatch.setattr(module.os, "close", close)
    monkeypatch.setattr(module.os, "fsync", fsync)
    with pytest.raises(EvidenceError) as caught:
        module.freeze_scale_snapshot(bound, directory)
    assert str(root) not in str(caught.value)
    assert list(directory.iterdir()) == [prior]
    assert prior.read_bytes() == before
