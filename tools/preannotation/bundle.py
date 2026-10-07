"""Source-byte/PTS binding and exclusive local bundle/revision I/O."""
from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image

from .contract import (bbox, bundle_digest, digest, frame_id, proposal_id, require,
                       return_template, validate_bundle, validate_return)


PRESENTATION_FILES = {"review.html", "reviewer.js", "review-ui.js", "review.css", "review-data.js"}


def file_sha(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def parse_json_bytes(snapshot: bytes) -> dict:
    def pairs(values):
        result = {}
        for key, value in values:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def invalid_number(value):
        raise ValueError(f"non-finite JSON number: {value}")

    value = json.loads(snapshot.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_number)
    require(isinstance(value, dict), "JSON root must be an object")
    return value


def read_json(path: Path) -> dict:
    return parse_json_bytes(path.read_bytes())


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n")


def retained_inventory(path: Path | None = None) -> list[dict]:
    result = []
    if path is not None:
        data = read_json(path)
        recordings = {r["recording_id"]: r for r in data["recordings"]}
        require(len(data["intake"]) == 4, "inventory requires all four retained recordings")
        ordered = [recordings[item["recording_id"]] for item in data["intake"]]
        require([r["underlying_match_id"] for r in ordered] == [f"natural_match_0{i}" for i in range(1, 5)],
                "source inventory is not in original retained order")
    else:
        ordered = [{"underlying_match_id": f"natural_match_0{i}"} for i in range(1, 5)]
    for index, recording in enumerate(ordered, 1):
        item = {"recording_id": recording["underlying_match_id"], "intake_order": index,
                "truncated": index == 2, "training_excluded": index == 2,
                "exclusion_reason": "user-confirmed mid-match truncation" if index == 2 else None,
                "training_qualified": False, "exposed_to_predictions_or_development": True,
                "data_usage": "DEV_TUNE" if index == 4 else "development_only"}
        for key in ("source_path", "source_sha256", "width", "height", "origin_pts", "origin_time_base"):
            if key in recording:
                item[key] = copy.deepcopy(recording[key])
        result.append(item)
    return result


def exact_images(source: Path, selected: list[dict]) -> tuple[list[Image.Image], Fraction]:
    targets = {(f["raw_pts"], Fraction(f["time_base"])): i for i, f in enumerate(selected)}
    require(len(targets) == len(selected), "duplicate exact source timestamps")
    images: dict[int, Image.Image] = {}
    origin = None
    with av.open(str(source)) as container:
        require(len(container.streams.video) == 1, "one unambiguous video stream is required")
        for frame in container.decode(video=0):
            require(frame.pts is not None and frame.time_base is not None, "decoded frame has no exact PTS")
            if origin is None:
                origin = Fraction(frame.pts) * frame.time_base
            key = (frame.pts, Fraction(frame.time_base))
            if key in targets:
                index = targets[key]
                require(index not in images, "ambiguous repeated source PTS")
                images[index] = frame.to_image().convert("RGB")
            if len(images) == len(selected):
                break
    require(origin is not None and len(images) == len(selected), "prediction exact PTS not found in source video")
    return [images[i] for i in range(len(selected))], origin


def prepare_bundle(predictions_path: Path, config_path: Path, out: Path, *,
                   inventory_path: Path | None = None, stride: int = 20, max_frames: int = 12,
                   prediction_format: str = "katacr") -> dict:
    predictions_path, config_path, out = Path(predictions_path), Path(config_path), Path(out)
    if out.exists():
        raise FileExistsError(f"exclusive bundle already exists: {out}")
    require(type(stride) is int and stride > 0 and type(max_frames) is int and 1 <= max_frames <= 240,
            "selection requires positive stride and 1..240 frame limit")
    prediction_sha, config_sha = file_sha(predictions_path), file_sha(config_path)
    predictions, config = read_json(predictions_path), read_json(config_path)
    require(predictions.get("config_sha256") == config_sha, "prediction/config SHA binding mismatch")
    require(prediction_format in {"katacr", "generic"}, "unknown prediction adapter")
    if prediction_format == "generic":
        require(predictions.get("schema") == "offline_predictions_v1", "unsupported future prediction protocol")
    require(isinstance(predictions.get("frames"), list) and bool(predictions["frames"]), "predictions have no frames")
    selected = predictions["frames"][::stride][:max_frames]
    source = Path(config["source_recording"])
    require(file_sha(source) == config["source_sha256"], "source recording SHA binding mismatch")
    inventory = retained_inventory(inventory_path)
    recording = config["underlying_match_id"]
    item = next((r for r in inventory if r["recording_id"] == recording), None)
    require(item is not None, "prediction recording absent from retained inventory")
    if "source_sha256" in item:
        require(item["source_sha256"] == config["source_sha256"], "inventory source SHA mismatch")
    images, origin = exact_images(source, selected)
    frames = []
    for teacher_frame, image in zip(selected, images, strict=True):
        pts, base = teacher_frame["raw_pts"], teacher_frame["time_base"]
        require(type(pts) is int and Fraction(base) > 0, "exact positive PTS time base required")
        actual_time = Fraction(pts) * Fraction(base) - origin
        if "timestamp_seconds" in teacher_frame:
            require(abs(float(actual_time) - teacher_frame["timestamp_seconds"]) < .000001,
                    "prediction relative timestamp disagrees with exact source PTS")
        if "width" in item:
            require(image.size == (item["width"], item["height"]), "inventory dimensions differ from decoded source")
        if "source_dimensions_wh" in config:
            require(list(image.size) == config["source_dimensions_wh"], "config dimensions differ from decoded source")
        fid = frame_id(recording, pts, base)
        proposals = []
        require(isinstance(teacher_frame.get("detections"), list), "prediction detections must be an array")
        for row, detection in enumerate(teacher_frame["detections"]):
            require(isinstance(detection, dict) and isinstance(detection.get("class"), str) and
                    bool(detection["class"].strip()), "raw teacher class required")
            require(type(detection.get("confidence")) in (int, float) and 0 <= detection["confidence"] <= 1,
                    "invalid teacher confidence")
            coordinates = detection.get("bbox_xyxy_original")
            bbox(coordinates, *image.size)
            proposals.append({"proposal_id": proposal_id(prediction_sha, recording, pts, base, row),
                              "row_index": row, "status": "pending", "bbox_xyxy": copy.deepcopy(coordinates),
                              "raw_teacher": copy.deepcopy(detection)})
        frames.append({"frame_id": fid, "raw_pts": pts, "time_base": str(Fraction(base)),
                       "source_relative_seconds": float(actual_time), "width": image.width, "height": image.height,
                       "image": f"images/{fid}.png", "proposals": proposals, "whole_frame_review": "unreviewed"})
    require(file_sha(source) == config["source_sha256"] and file_sha(predictions_path) == prediction_sha and
            file_sha(config_path) == config_sha, "input bytes changed during preparation")
    bundle = {"schema": "preannotation_bundle_v1", "recording_id": recording, "inventory": inventory,
              "prediction_sha256": prediction_sha, "config_sha256": config_sha,
              "source_sha256": config["source_sha256"], "source_recording": str(source),
              "source_origin_seconds_exact": str(origin), "adapter": prediction_format,
              "selection": {"stride_rows": stride, "max_frames": max_frames, "quality_selection": False},
              "training_qualified": False, "frames": frames}
    if config.get("synthetic_input") is True:
        bundle["synthetic"] = True
    bundle["bundle_sha256"] = bundle_digest(bundle)
    validate_bundle(bundle)
    out.mkdir(parents=True, exist_ok=False)
    (out / "images").mkdir()
    for frame, image in zip(frames, images, strict=True):
        with (out / frame["image"]).open("xb") as handle:
            image.save(handle, format="PNG")
    for name, source_path in (("teacher-predictions.json", predictions_path), ("teacher-config.json", config_path)):
        with (out / name).open("xb") as handle:
            handle.write(source_path.read_bytes())
    write_json(out / "bundle.json", bundle)
    write_json(out / "human-return-template.json", return_template(bundle))
    write_presentation_assets(out, bundle)
    write_manifest(out, bundle)
    require(load_bundle(out) == bundle, "bundle readback failed")
    return bundle


def write_presentation_assets(out: Path, bundle: dict) -> None:
    assets = Path(__file__).parent
    for name in ("review.html", "reviewer.js", "review-ui.js", "review.css"):
        with (out / name).open("xb") as handle:
            handle.write((assets / name).read_bytes())
    with (out / "review-data.js").open("x", encoding="utf-8") as handle:
        safe_json = json.dumps(bundle, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        handle.write("globalThis.PREANNOTATION_BUNDLE = " + safe_json + ";\n")


def write_manifest(out: Path, bundle: dict) -> None:
    files = {p.relative_to(out).as_posix(): file_sha(p) for p in out.rglob("*") if p.is_file()}
    manifest = {"schema": "preannotation_file_manifest_v1", "bundle_sha256": bundle["bundle_sha256"], "files": files}
    manifest["manifest_sha256"] = digest(manifest)
    write_json(out / "manifest.json", manifest)


def refresh_presentation(source_root: Path, out: Path) -> dict:
    """New exclusive presentation; original JSON/PNGs and original folder untouched."""
    source_root, out = Path(source_root), Path(out)
    bundle = load_bundle(source_root)
    members = read_json(source_root / "manifest.json")["files"]
    out.mkdir(parents=True, exist_ok=False)
    for name in members:
        if name in PRESENTATION_FILES:
            continue
        destination = safe_bundle_path(out, name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = safe_bundle_path(source_root, name).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == members[name], "original member changed during presentation copy")
        with destination.open("xb") as handle:
            handle.write(payload)
    write_presentation_assets(out, bundle)
    write_manifest(out, bundle)
    require(load_bundle(out) == bundle, "presentation readback changed data identity")
    require(load_bundle(source_root) == bundle, "original bundle changed during presentation copy")
    return bundle


def safe_bundle_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts and bool(path.parts), "unsafe bundle member path")
    absolute = (root / path).resolve()
    require(absolute.is_relative_to(root.resolve()) and not (root / path).is_symlink(), "bundle path escaped through symlink")
    return absolute


def load_bundle(root: Path) -> dict:
    root = Path(root)
    manifest = read_json(root / "manifest.json")
    require(manifest.get("schema") == "preannotation_file_manifest_v1", "unsupported manifest")
    require(manifest.get("manifest_sha256") == digest({k: v for k, v in manifest.items() if k != "manifest_sha256"}),
            "manifest checksum mismatch")
    for relative, expected in manifest["files"].items():
        path = safe_bundle_path(root, relative)
        require(path.is_file() and file_sha(path) == expected, f"immutable member changed: {relative}")
    bundle = read_json(root / "bundle.json")
    validate_bundle(bundle)
    require(bundle["bundle_sha256"] == manifest["bundle_sha256"], "manifest/bundle identity mismatch")
    require(file_sha(root / "teacher-predictions.json") == bundle["prediction_sha256"] and
            file_sha(root / "teacher-config.json") == bundle["config_sha256"], "raw teacher binding mismatch")
    for frame in bundle["frames"]:
        require(frame["image"] in manifest["files"], "unbound source image")
        with Image.open(safe_bundle_path(root, frame["image"])) as image:
            require(image.format == "PNG" and image.size == (frame["width"], frame["height"]), "source PNG mismatch")
    return bundle


def import_return(bundle_root: Path, human_path: Path, revision: Path, *, allow_synthetic: bool = False) -> dict:
    bundle = load_bundle(bundle_root)
    snapshot = Path(human_path).read_bytes()
    returned = parse_json_bytes(snapshot)
    gt = validate_return(bundle, returned, allow_synthetic=allow_synthetic)
    revision = Path(revision)
    revision.mkdir(parents=True, exist_ok=False)
    with (revision / "human-return.json").open("xb") as handle:
        handle.write(snapshot)
    write_json(revision / "reviewed-annotations.json", gt)
    receipt = {
        "schema": "preannotation_revision_receipt_v1", "bundle_sha256": bundle["bundle_sha256"],
        "human_return_sha256": hashlib.sha256(snapshot).hexdigest(),
        "reviewed_annotations_sha256": file_sha(revision / "reviewed-annotations.json"),
        "synthetic": returned["provenance"]["synthetic"], "training_qualified": False}
    write_json(revision / "revision-receipt.json", receipt)
    archived = (revision / "human-return.json").read_bytes()
    require(archived == snapshot and parse_json_bytes(archived) == returned, "archived return differs from validated snapshot")
    require(read_json(revision / "revision-receipt.json") == receipt and
            file_sha(revision / "human-return.json") == receipt["human_return_sha256"] and
            file_sha(revision / "reviewed-annotations.json") == receipt["reviewed_annotations_sha256"], "revision receipt readback mismatch")
    require(read_json(revision / "reviewed-annotations.json") == gt, "revision readback failed")
    return gt
