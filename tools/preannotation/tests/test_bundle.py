"""Breaks caught: wrong PTS/source binding, overwritten revisions and tampering."""
import hashlib
import importlib
import json
from fractions import Fraction
from pathlib import Path

import av
import pytest
from PIL import Image


@pytest.fixture
def io_api():
    class Access:
        def __getattr__(self, name):
            try:
                return getattr(importlib.import_module("tools.preannotation.bundle"), name)
            except ImportError:
                pytest.fail("bundle I/O is not implemented")
    return Access()


@pytest.fixture
def inputs(tmp_path):
    source = tmp_path / "source.mp4"
    with av.open(str(source), mode="w") as container:
        stream = container.add_stream("mpeg4", rate=2)
        stream.width, stream.height, stream.pix_fmt = 100, 200, "yuv420p"
        for index in range(3):
            frame = av.VideoFrame.from_image(Image.new("RGB", (100, 200), (index * 50, 60, 70)))
            frame.pts, frame.time_base = index, Fraction(1, 2)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    with av.open(str(source)) as container:
        frames = [{"raw_pts": f.pts, "time_base": str(f.time_base),
                   "timestamp_seconds": float(f.pts * f.time_base),
                   "detections": [{"class": "witch", "confidence": .75,
                       "owner_prediction": "opponent", "bbox_xyxy_original": [10, 20, 30, 40]}]}
                  for f in container.decode(video=0)]
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"source_recording": str(source), "source_sha256": source_sha,
        "underlying_match_id": "natural_match_01", "source_dimensions_wh": [100, 200]}))
    predictions = tmp_path / "predictions.json"
    predictions.write_text(json.dumps({"schema": "offline_predictions_v1",
                                       "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
                                       "frames": frames}))
    return source, predictions, config, frames


def test_prepare_exports_exact_pts_full_pngs_and_immutable_pending_proposals(io_api, inputs, tmp_path):
    source, predictions, config, frames = inputs
    before = (source.read_bytes(), predictions.read_bytes(), config.read_bytes())
    out = tmp_path / "bundle"
    bundle = io_api.prepare_bundle(predictions, config, out, stride=1, max_frames=3, prediction_format="generic")
    assert len(bundle["frames"]) == 3
    assert [(f["raw_pts"], f["time_base"]) for f in bundle["frames"]] == [(f["raw_pts"], f["time_base"]) for f in frames]
    for frame in bundle["frames"]:
        with Image.open(out / frame["image"]) as image:
            assert image.size == (100, 200)
        assert frame["proposals"][0]["raw_teacher"]["owner_prediction"] == "opponent"
        assert frame["proposals"][0]["status"] == "pending"
        assert "owner" not in frame["proposals"][0]
    assert io_api.load_bundle(out) == bundle
    assert before == (source.read_bytes(), predictions.read_bytes(), config.read_bytes())
    assert (out / "review.html").is_file()
    with pytest.raises(FileExistsError):
        io_api.prepare_bundle(predictions, config, out, stride=1, prediction_format="generic")


def test_different_selection_keeps_same_row_identity(io_api, inputs, tmp_path):
    _, predictions, config, _ = inputs
    all_frames = io_api.prepare_bundle(predictions, config, tmp_path / "all", stride=1, prediction_format="generic")
    sparse = io_api.prepare_bundle(predictions, config, tmp_path / "sparse", stride=2, prediction_format="generic")
    assert sparse["frames"][1]["proposals"][0]["proposal_id"] == all_frames["frames"][2]["proposals"][0]["proposal_id"]


@pytest.mark.parametrize("mutation", ["wrong_source", "wrong_config", "nonexistent_pts"])
def test_prepare_rejects_wrong_source_config_or_pts_before_creating_output(io_api, inputs, tmp_path, mutation):
    _, predictions, config, _ = inputs
    if mutation == "wrong_source":
        d = json.loads(config.read_text())
        d["source_sha256"] = "0" * 64
        config.write_text(json.dumps(d))
        p = json.loads(predictions.read_text())
        p["config_sha256"] = hashlib.sha256(config.read_bytes()).hexdigest()
        predictions.write_text(json.dumps(p))
    elif mutation == "wrong_config":
        config.write_text(config.read_text() + " ")
    else:
        p = json.loads(predictions.read_text())
        p["frames"][0]["raw_pts"] = 1
        predictions.write_text(json.dumps(p))
    out = tmp_path / "invalid"
    with pytest.raises(ValueError):
        io_api.prepare_bundle(predictions, config, out, stride=1, prediction_format="generic")
    assert not out.exists()


def test_image_and_prediction_tampering_fails_validation(io_api, inputs, tmp_path):
    _, predictions, config, _ = inputs
    out = tmp_path / "bundle"
    bundle = io_api.prepare_bundle(predictions, config, out, stride=1, prediction_format="generic")
    png = out / bundle["frames"][0]["image"]
    png.write_bytes(png.read_bytes() + b"modified")
    with pytest.raises(ValueError):
        io_api.load_bundle(out)


def test_exclusive_revision_readback_preserves_proposals_and_prior_revision(io_api, inputs, tmp_path):
    from tools.preannotation.contract import return_template
    _, predictions, config, _ = inputs
    out = tmp_path / "bundle"
    bundle = io_api.prepare_bundle(predictions, config, out, stride=1, prediction_format="generic")
    returned = return_template(bundle)
    returned["provenance"] = {"kind": "human", "reviewer": "Fixture human",
                              "synthetic": False, "human_review_attested": True}
    human_file = tmp_path / "return.json"
    human_file.write_text(json.dumps(returned))
    immutable = (out / "bundle.json").read_bytes()
    revision = tmp_path / "revision-v1"
    gt = io_api.import_return(out, human_file, revision)
    assert gt["positive_boxes"] == []
    assert gt["negative_evidence"] == []
    assert json.loads((revision / "reviewed-annotations.json").read_text()) == gt
    assert (revision / "human-return.json").read_bytes() == human_file.read_bytes()
    assert (out / "bundle.json").read_bytes() == immutable
    with pytest.raises(FileExistsError):
        io_api.import_return(out, human_file, revision)
    assert json.loads((revision / "reviewed-annotations.json").read_text()) == gt


def test_import_rejects_invalid_return_without_output_side_effects(io_api, inputs, tmp_path):
    _, predictions, config, _ = inputs
    out = tmp_path / "bundle"
    io_api.prepare_bundle(predictions, config, out, prediction_format="generic")
    invalid = tmp_path / "invalid-return.json"
    invalid.write_text((out / "human-return-template.json").read_text())
    revision = tmp_path / "revision"
    with pytest.raises(ValueError):
        io_api.import_return(out, invalid, revision)
    assert not revision.exists()


@pytest.mark.parametrize("change", ["replace", "delete"])
def test_import_archives_exact_validated_snapshot_when_input_changes_after_validation(tmp_path, monkeypatch, change):
    from tools.preannotation import bundle as module
    from tools.preannotation.__main__ import create_demo

    demo = tmp_path / "synthetic-only"
    create_demo(demo)
    source = demo / "synthetic-return.json"
    snapshot = source.read_bytes()
    changed = json.loads(snapshot)
    changed["provenance"]["reviewer"] = "different synthetic reviewer after validation"
    replacement = json.dumps(changed).encode("utf-8")
    real_validate = module.validate_return

    def validate_then_change(*args, **kwargs):
        result = real_validate(*args, **kwargs)
        if change == "replace":
            source.write_bytes(replacement)
        else:
            source.unlink()
        return result

    monkeypatch.setattr(module, "validate_return", validate_then_change)
    revision = tmp_path / "new-checked-revision"
    gt = module.import_return(demo / "bundle", source, revision, allow_synthetic=True)
    archive = revision / "human-return.json"
    assert archive.read_bytes() == snapshot
    assert gt["provenance"] == json.loads(snapshot)["provenance"]
    assert json.loads(archive.read_bytes())["provenance"] == gt["provenance"]
    receipt = json.loads((revision / "revision-receipt.json").read_bytes())
    assert receipt["human_return_sha256"] == hashlib.sha256(snapshot).hexdigest()
    assert receipt["reviewed_annotations_sha256"] == hashlib.sha256((revision / "reviewed-annotations.json").read_bytes()).hexdigest()
    assert gt["status"] == "synthetic_not_gt"
    if change == "replace":
        assert source.read_bytes() == replacement
    else:
        assert not source.exists()


@pytest.mark.parametrize("payload", [b'{"x":1,"x":2}', b'{"nested":{"x":1,"x":2}}',
                                     b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'[]'])
def test_byte_snapshot_parser_keeps_strict_json_rejection(io_api, payload):
    with pytest.raises(ValueError):
        io_api.parse_json_bytes(payload)


def test_manifest_paths_cannot_escape_bundle(io_api, inputs, tmp_path):
    _, predictions, config, _ = inputs
    out = tmp_path / "bundle"
    io_api.prepare_bundle(predictions, config, out, prediction_format="generic")
    manifest = json.loads((out / "manifest.json").read_text())
    manifest["files"]["../outside.json"] = "0" * 64
    (out / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        io_api.load_bundle(out)


def test_new_presentation_uses_current_assets_without_changing_source_bundle_or_redecoding(io_api, inputs, tmp_path):
    _, predictions, config, _ = inputs
    old = tmp_path / "old"
    bundle = io_api.prepare_bundle(predictions, config, old, prediction_format="generic")
    # A controlled earlier presentation: reseal its changed CSS independently.
    (old / "review.css").write_bytes(b"body { color: red; }\n")
    manifest = json.loads((old / "manifest.json").read_text())
    manifest["files"]["review.css"] = hashlib.sha256((old / "review.css").read_bytes()).hexdigest()
    manifest.pop("manifest_sha256")
    manifest["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (old / "manifest.json").write_text(json.dumps(manifest))
    before = {p.relative_to(old).as_posix(): p.read_bytes() for p in old.rglob("*") if p.is_file()}
    new = tmp_path / "fresh-presentation"
    refreshed = io_api.refresh_presentation(old, new)
    assert refreshed == bundle
    assert io_api.load_bundle(new) == bundle
    assert (new / "review.css").read_bytes() == (Path(__file__).parents[1] / "review.css").read_bytes()
    assert (new / "bundle.json").read_bytes() == before["bundle.json"]
    for frame in bundle["frames"]:
        assert (new / frame["image"]).read_bytes() == before[frame["image"]]
    assert before == {p.relative_to(old).as_posix(): p.read_bytes() for p in old.rglob("*") if p.is_file()}
    with pytest.raises(FileExistsError):
        io_api.refresh_presentation(old, new)
