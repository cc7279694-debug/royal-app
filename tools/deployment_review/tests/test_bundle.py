"""Manual event review packaging never promotes visual observations into GT."""
import copy
import csv
import hashlib
import importlib
import json
from pathlib import Path
import zipfile

import pytest
from PIL import Image


@pytest.fixture
def api():
    class Access:
        def __getattr__(self, name):
            try:
                return getattr(importlib.import_module("tools.deployment_review.bundle"), name)
            except ImportError:
                pytest.fail("manual deployment review packager is not implemented")
    return Access()


@pytest.fixture
def data(tmp_path):
    media = tmp_path / "media"
    media.mkdir()
    Image.new("RGB", (32, 64), "blue").save(media / "frame.png")
    (media / "context.mp4").write_bytes(b"synthetic presentation fixture")
    plan = {
        "schema": "deployment_event_review_plan_v1",
        "inventory": [{"intake_order": n, "underlying_match_id": f"match_{n}",
                       "recording_id": f"recording_{n}", "disposition": "candidate_context" if n == 1 else "not_selected",
                       "source_sha256": "b" * 64,
                       "reason": "manually selected from existing visual evidence"} for n in range(1, 5)],
        "evidence_sources": [{"source_id": "visual_gt", "sha256": "a" * 64}],
        "candidates": [{
            "candidate_id": "candidate_01", "underlying_match_id": "match_1", "recording_id": "recording_1",
            "approximate_timestamp": 5.0, "timestamp_kind": "visual_anchor_not_confirmed_spawn",
            "owner": "opponent", "card_id": "witch", "form": "unknown", "event_type": "direct",
            "evaluable": False, "confidence": "uncertain", "review_state": "pending_human_review",
            "evidence_visual_classes": ["visual.unit.witch"], "evidence_frame_ids": ["old_frame"],
            "visual_refs": [{"source_id": "visual_gt", "object_id": "old_object", "appearance_id": "old_group", "owner": "opponent"}],
            "candidate_reason": "Visual anchor only; inspect context to determine whether this is new.",
            "notes": "Could be a persistent old unit; no event truth inferred.", "duplicate_hint": None,
            "context": {"start_seconds": 2.0, "end_seconds": 8.0, "clip": "context.mp4",
                        "clip_presentation_only": True, "source_sha256": "b" * 64,
                        "frames": [{"image": "frame.png", "frame_id": "context_frame", "raw_pts": 50,
                                    "time_base": "1/10", "origin_seconds_exact": "0", "timestamp_seconds": 5.0}]} }],
    }
    return plan, media


def test_blank_return_is_unattested_and_never_gt(api, data):
    returned = api.return_template(data[0])
    assert returned["human_review_attested"] is False
    assert returned["reviewer"] == ""
    row = returned["decisions"][0]
    assert row["decision"] == "pending"
    assert row["corrected_timestamp"] is None
    assert returned["confirmed_card_events"] == []
    assert returned["negative_evidence"] == []


@pytest.mark.parametrize("field,value", [("review_state", "confirmed"), ("evaluable", True),
    ("confidence", "human_confirmed"), ("owner", "own"), ("card_id", "cannon"),
    ("card_id", "skeletons"), ("card_id", "barbarian_barrel"), ("form", "invalid"),
    ("approximate_timestamp", float("nan")), ("approximate_timestamp", -1),
    ("timestamp_kind", "deployment_time")])
def test_rejects_automatic_promotion_and_ineligible_hints(api, data, field, value):
    plan = copy.deepcopy(data[0])
    plan["candidates"][0][field] = value
    with pytest.raises(ValueError):
        api.validate_plan(plan)


def test_validates_every_candidate_before_packaging(api, data):
    plan = copy.deepcopy(data[0])
    plan["candidates"].append(copy.deepcopy(plan["candidates"][0]))
    with pytest.raises(ValueError):
        api.validate_plan(plan)


def test_order_and_recording_match_pair_are_not_interchangeable(api, data):
    plan = copy.deepcopy(data[0])
    plan["candidates"][0]["underlying_match_id"] = "recording_1"
    with pytest.raises(ValueError):
        api.validate_plan(plan)
    plan = copy.deepcopy(data[0])
    plan["inventory"].reverse()
    with pytest.raises(ValueError):
        api.validate_plan(plan)


@pytest.mark.parametrize("field,value", [("image", "../outside.png"), ("image", "C:/private/frame.png"),
                                       ("time_base", "0"), ("timestamp_seconds", 5.1)])
def test_context_paths_and_exact_pts_are_checked(api, data, field, value):
    plan = copy.deepcopy(data[0])
    plan["candidates"][0]["context"]["frames"][0][field] = value
    with pytest.raises(ValueError):
        api.validate_plan(plan)


def test_actual_bundle_has_context_review_fields_hashes_and_no_lock(api, data, tmp_path):
    plan, media = data
    out = tmp_path / "review"
    manifest = api.write_bundle(plan, media, out)
    assert (out / "index.html").is_file()
    assert (out / "contacts/candidate_01.jpg").is_file()
    assert json.loads((out / "human-return.template.json").read_text())["confirmed_card_events"] == []
    rows = list(csv.DictReader((out / "event-review.csv").open(encoding="utf-8-sig", newline="")))
    assert rows[0]["decision"] == "pending"
    assert rows[0]["corrected_card"] == rows[0]["corrected_owner"] == rows[0]["merge_into"] == ""
    assert "confirm / reject / uncertain / merge_duplicate" in (out / "HUMAN_REVIEW.md").read_text(encoding="utf-8")
    assert not list(out.rglob("*lock*"))
    for name, sha in manifest["files"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == sha
    archive = tmp_path / "review.zip"
    api.zip_bundle(out, archive)
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        assert set(zipped.namelist()) == set(manifest["files"]) | {"manifest.json"}
    original = (out / "candidates.json").read_bytes()
    with pytest.raises(FileExistsError):
        api.write_bundle(plan, media, out)
    assert (out / "candidates.json").read_bytes() == original
    with pytest.raises(FileExistsError):
        api.zip_bundle(out, archive)


def test_tampered_member_is_not_archived(api, data, tmp_path):
    out = tmp_path / "review"
    api.write_bundle(*data, out)
    (out / "event-review.csv").write_text("tampered")
    with pytest.raises(ValueError):
        api.zip_bundle(out, tmp_path / "bad.zip")
    assert not (tmp_path / "bad.zip").exists()


def test_html_does_not_execute_candidate_notes(api, data, tmp_path):
    plan, media = data
    plan["candidates"][0]["notes"] = "<script>alert('x')</script>"
    out = tmp_path / "review"
    api.write_bundle(plan, media, out)
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_archive_detects_member_change_during_read(api, data, tmp_path, monkeypatch):
    out = tmp_path / "review"
    api.write_bundle(*data, out)
    real_write = zipfile.ZipFile.write

    def change_during_read(zipped, filename, arcname=None, **kwargs):
        path = out / "event-review.csv"
        original = path.read_bytes()
        if arcname == "event-review.csv":
            path.write_bytes(b"changed only during ZIP read")
        try:
            return real_write(zipped, filename, arcname=arcname, **kwargs)
        finally:
            path.write_bytes(original)

    monkeypatch.setattr(zipfile.ZipFile, "write", change_during_read)
    with pytest.raises(ValueError):
        api.zip_bundle(out, tmp_path / "race.zip")


def test_own_reference_cannot_be_rebranded_as_opponent_candidate(api, data):
    data[0]["candidates"][0]["visual_refs"][0]["owner"] = "own"
    with pytest.raises(ValueError):
        api.validate_plan(data[0])


def test_one_recording_cannot_claim_two_underlying_matches(api, data):
    plan = data[0]
    plan["inventory"][1]["recording_id"] = "recording_1"
    with pytest.raises(ValueError):
        api.validate_plan(plan)


@pytest.mark.parametrize("field,value", [("confirmed_card_events", [{"card": "witch"}]),
    ("human_review_attested", True), ("negative_evidence", [{"absent": "witch"}]),
    ("independent_confirmed_card_play_count", 1), ("event_gt_lock_created", True)])
def test_extra_truth_claims_cannot_survive_pending_packaging(api, data, field, value):
    data[0][field] = value
    with pytest.raises(ValueError):
        api.validate_plan(data[0])


def test_duplicate_visual_source_id_cannot_hide_different_sha(api, data):
    data[0]["evidence_sources"].append({"source_id": "visual_gt", "sha256": "c" * 64})
    with pytest.raises(ValueError):
        api.validate_plan(data[0])


def test_context_video_sha_must_match_the_selected_recording(api, data):
    data[0]["candidates"][0]["context"]["source_sha256"] = "c" * 64
    with pytest.raises(ValueError):
        api.validate_plan(data[0])


def test_manifest_change_between_validation_and_archive_is_rejected(api, data, tmp_path, monkeypatch):
    out = tmp_path / "review"
    api.write_bundle(*data, out)
    real_open = Path.open
    altered = False

    def mutate_manifest_when_first_member_is_checked(path, *args, **kwargs):
        nonlocal altered
        if path == out / "candidates.json" and args and args[0] == "rb" and not altered:
            manifest_path = out / "manifest.json"
            with real_open(manifest_path, encoding="utf-8") as handle:
                changed = json.load(handle)
            changed["files"]["event-review.csv"] = "c" * 64
            with real_open(manifest_path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            altered = True
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", mutate_manifest_when_first_member_is_checked)
    with pytest.raises(ValueError):
        api.zip_bundle(out, tmp_path / "manifest-race.zip")
