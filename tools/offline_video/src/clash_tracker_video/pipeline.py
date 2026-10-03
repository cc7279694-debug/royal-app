"""Local MP4 decoding with exact PTS selection and bounded frame memory."""
from __future__ import annotations

import json
import math
import struct
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image

TOLERANCE = Fraction(1, 10)


class VideoError(Exception):
    """A concise input, decoding, timeline, or output error."""


def _input(path: str | Path) -> Path:
    text = str(path)
    if "://" in text or text.startswith(("\\\\", "//")):
        raise VideoError("Only local files are accepted; URLs/network paths are unsupported.")
    source = Path(path)
    if not source.exists():
        raise VideoError("Input file does not exist.")
    if not source.is_file():
        raise VideoError("Input must be a file, not a directory.")
    if source.suffix.lower() != ".mp4":
        raise VideoError("Module 1 accepts local MP4 files only.")
    if not source.stat().st_size:
        raise VideoError("Input file is empty.")
    return source


def _stream(container):
    if "mp4" not in container.format.name.split(","):
        raise VideoError("Input is not an MP4 container.")
    for stream in container.streams.video:
        if not stream.disposition & av.stream.Disposition.attached_pic:
            return stream
    raise VideoError("No actual video stream (cover images are excluded).")


def _timestamp(frame) -> Fraction:
    if frame.pts is None or frame.time_base is None or frame.time_base <= 0:
        raise VideoError("Missing or invalid frame PTS/time_base; cannot establish timeline.")
    return frame.pts * frame.time_base


def _rotation(frame) -> int:
    angle = frame.rotation % 360
    if angle not in (0, 90, 180, 270):
        raise VideoError("Unsupported display rotation; only 0/90/180/270 are supported.")
    matrices = {
        0: (65536, 0, 0, 0, 65536, 0, 0, 0, 1073741824),
        90: (0, -65536, 0, 65536, 0, 0, 0, 0, 1073741824),
        180: (-65536, 0, 0, 0, -65536, 0, 0, 0, 1073741824),
        270: (0, 65536, 0, -65536, 0, 0, 0, 0, 1073741824),
    }
    for data in frame.side_data.values():
        if data.type.name == "DISPLAYMATRIX":
            raw = bytes(data)
            if len(raw) != 36 or struct.unpack("=9i", raw) != matrices[angle]:
                raise VideoError("Unsupported display transform (mirror/scale/perspective).")
    return angle


def _validate_frame(frame) -> int:
    if frame.is_corrupt:
        raise VideoError("Decoder reported a corrupt video frame.")
    _timestamp(frame)
    if frame.color_trc in (16, 18) or any(c.bits > 8 for c in frame.format.components):
        raise VideoError("Unsupported HDR/high-bit-depth video; only 8-bit SDR is supported.")
    return _rotation(frame)


def _video_info(source, container, stream, frame) -> dict:
    warnings = []
    duration, duration_source = None, None
    if stream.duration is not None and stream.time_base is not None:
        duration = float(stream.duration * stream.time_base)
        duration_source = "stream"
    elif container.duration is not None:
        duration = container.duration / av.time_base
        duration_source = "container"
        warnings.append("Duration uses container metadata and may include other streams.")
    else:
        warnings.append("Duration metadata unavailable.")
    fps = float(stream.average_rate) if stream.average_rate else None
    if fps is None:
        warnings.append("Average FPS metadata unavailable; not used for selection.")
    rotation = _validate_frame(frame)
    if stream.sample_aspect_ratio and stream.sample_aspect_ratio != 1:
        raise VideoError("Unsupported non-square pixel aspect ratio.")
    if not stream.sample_aspect_ratio:
        warnings.append("Pixel aspect ratio unspecified; preserving encoded pixel dimensions.")
    return {
        "filename": source.name, "stream_index": stream.index,
        "codec": stream.codec_context.name, "width": frame.width, "height": frame.height,
        "duration_seconds": duration, "duration_source": duration_source,
        "average_fps": fps, "fps_source": "stream.average_rate" if fps else None,
        "rotation_degrees": rotation,
        "rotation_source": "decoded DISPLAYMATRIX or default identity",
        "warnings": warnings,
    }


def inspect_video(path: str | Path) -> dict:
    """Inspect metadata and validate the first decoded display frame."""
    try:
        source = _input(path)
        with av.open(str(source), "r") as container:
            stream = _stream(container)
            first = next(container.decode(stream), None)
            if first is None:
                raise VideoError("No decodable video frames.")
            return _video_info(source, container, stream, first)
    except (av.FFmpegError, OSError, ValueError) as exc:
        raise VideoError(f"Cannot read video ({type(exc).__name__}).") from exc


def _times(values) -> list[Fraction]:
    if not values:
        raise VideoError("Provide at least one target time.")
    result = []
    for value in values:
        try:
            number = float(value)
            if not math.isfinite(number) or number < 0:
                raise ValueError
            time = Fraction(str(value))
        except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
            raise VideoError("Times must be finite, non-negative seconds.") from exc
        if result and time <= result[-1]:
            raise VideoError("Times must be strictly increasing without duplicates.")
        result.append(time)
    return result


def _output(path: str | Path, source: Path) -> Path:
    output = Path(path)
    if output.resolve() == source.resolve():
        raise VideoError("Output must not overwrite the input video.")
    if output.is_symlink():
        raise VideoError("Output directory must not be a symbolic link.")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise VideoError("Output must be an empty directory or a new directory.")
    output.mkdir(parents=True, exist_ok=True)
    return output


def _write_report(output: Path, report: dict) -> None:
    with (output / "report.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def extract_frames(path: str | Path, times: list[float], output: str | Path) -> dict:
    """Select first display frame at/after each target, scanning once to EOF.

    On decode/timeline failure, retain prior entries in an error report where
    output is writable, and raise VideoError. No last-frame fallback occurs.
    """
    report = {
        "report_format_version": 1, "status": "error", "video": None,
        "timeline": {
            "basis": "PTS * time_base, relative to first display frame; not game clock",
            "origin_seconds": None, "origin_pts": None, "origin_time_base": None,
            "tolerance_seconds": 0.1, "selection": "first frame at or after target",
        },
        "warnings": [], "results": [],
    }
    destination = None
    try:
        targets = _times(times)
        source = _input(path)
        destination = _output(output, source)
        report["results"] = [
            {"requested_time_seconds": float(t), "status": "error",
             "actual_time_seconds": None, "error_seconds": None, "image": None,
             "raw_pts": None, "time_base": None, "raw_time_seconds": None,
             "output_width": None, "output_height": None, "reason": "not_processed"}
            for t in targets
        ]
        with av.open(str(source), "r") as container:
            stream = _stream(container)
            origin = previous = None
            index = 0
            for frame in container.decode(stream):
                rotation = _validate_frame(frame)
                raw_time = _timestamp(frame)
                if previous is not None and raw_time <= previous:
                    raise VideoError("Non-increasing presentation timestamps; invalid timeline.")
                previous = raw_time
                if origin is None:
                    origin = raw_time
                    report["video"] = _video_info(source, container, stream, frame)
                    report["warnings"].extend(report["video"]["warnings"])
                    report["timeline"].update(
                        origin_seconds=float(origin), origin_pts=frame.pts,
                        origin_time_base=str(frame.time_base),
                    )
                elif (frame.width, frame.height, rotation) != (
                    report["video"]["width"], report["video"]["height"],
                    report["video"]["rotation_degrees"],
                ):
                    raise VideoError("Video dimensions or display transform changed mid-stream.")
                relative = raw_time - origin
                while index < len(targets) and relative >= targets[index]:
                    entry = report["results"][index]
                    delta = relative - targets[index]
                    entry.update(
                        actual_time_seconds=float(relative), error_seconds=float(delta),
                        raw_pts=frame.pts, time_base=str(frame.time_base),
                        raw_time_seconds=float(raw_time), reason=None,
                    )
                    if delta > TOLERANCE:
                        entry.update(status="miss", reason="outside_100ms_tolerance")
                    else:
                        image = frame.to_image()
                        operations = {90: Image.Transpose.ROTATE_90,
                                      180: Image.Transpose.ROTATE_180,
                                      270: Image.Transpose.ROTATE_270}
                        if rotation:
                            image = image.transpose(operations[rotation])
                        filename = f"frame_{index:04d}.png"
                        with (destination / filename).open("xb") as handle:
                            image.save(handle, format="PNG")
                        entry.update(status="success", image=filename,
                                     output_width=image.width, output_height=image.height)
                    index += 1
            if origin is None:
                raise VideoError("No decodable video frames.")
            for entry in report["results"][index:]:
                entry.update(status="miss", reason="no_frame_at_or_after_target")
            report["status"] = (
                "success" if all(e["status"] == "success" for e in report["results"])
                else "partial"
            )
        _write_report(destination, report)
        return report
    except (VideoError, av.FFmpegError, OSError, ValueError) as exc:
        message = str(exc) if isinstance(exc, VideoError) else (
            f"Video decode/output failed ({type(exc).__name__})."
        )
        report["status"] = "error"
        report["warnings"].append(message)
        for entry in report["results"]:
            if entry["status"] == "error":
                entry["reason"] = message
        if destination is not None and not (destination / "report.json").exists():
            try:
                _write_report(destination, report)
            except OSError as report_error:
                message += f" Error report could not be written ({type(report_error).__name__})."
        raise VideoError(message) from exc
