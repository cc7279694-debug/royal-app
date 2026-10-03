import hashlib
import json
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import av
import pytest
from PIL import Image

from clash_tracker_video import pipeline
from conftest import COLORS, make_video

def test_inspect_real_mp4(video):
    info = pipeline.inspect_video(video)
    assert (info["width"], info["height"], info["codec"]) == (64, 48, "h264")
    assert info["filename"] == "中文 录像.mp4"
    assert info["stream_index"] == 0
    assert info["average_fps"] == pytest.approx(10)
    assert info["duration_seconds"] == pytest.approx(0.4)
    assert info["duration_source"] == "stream"
    assert info["rotation_degrees"] == 0

def test_real_extract_first_middle_end_and_png_json(video, tmp_path):
    before = hashlib.sha256(video.read_bytes()).hexdigest()
    output = tmp_path / "导出 空格"
    report = pipeline.extract_frames(video, [0, 0.15, 0.299, 9], output)
    assert report["status"] == "partial"
    entries = report["results"]
    assert [e["status"] for e in entries] == ["success"] * 3 + ["miss"]
    assert [e["actual_time_seconds"] for e in entries[:3]] == [0, 0.2, 0.3]
    assert entries[1]["error_seconds"] == pytest.approx(0.05)
    assert entries[3]["image"] is None
    assert entries[3]["reason"] == "no_frame_at_or_after_target"
    for entry, expected in zip(entries[:3], [COLORS[0], COLORS[2], COLORS[3]]):
        with Image.open(output / entry["image"]) as image:
            assert image.size == (64, 48)
            assert all(abs(a-b) <= 4 for a,b in zip(image.getpixel((32,24)), expected))
    assert json.loads((output / "report.json").read_text(encoding="utf-8")) == report
    assert hashlib.sha256(video.read_bytes()).hexdigest() == before

def test_vfr_nonzero_start_and_same_frame(tmp_path):
    source = make_video(tmp_path / "vfr.mp4", (5000, 5070, 5210, 5500))
    report = pipeline.extract_frames(source, [0, 0.06, 0.065, 0.2], tmp_path / "out")
    entries = report["results"]
    assert [e["actual_time_seconds"] for e in entries] == [0, 0.07, 0.07, 0.21]
    assert entries[1]["raw_pts"] == entries[2]["raw_pts"]
    assert entries[0]["raw_time_seconds"] == 5.0
    assert report["timeline"]["origin_seconds"] == 5.0
    assert entries[1]["time_base"] is not None

def test_tolerance_inclusive_and_miss(tmp_path):
    source = make_video(tmp_path / "gap.mp4", (0, 200, 300, 400))
    report = pipeline.extract_frames(source, [0.099, 0.1], tmp_path / "out")
    miss, hit = report["results"]
    assert miss["status"] == "miss"
    assert miss["actual_time_seconds"] == 0.2
    assert miss["image"] is None
    assert hit["status"] == "success"
    assert hit["error_seconds"] == 0.1

@pytest.mark.parametrize("times", [[], [-1], [float("nan")], [float("inf")], [0,0], [1,0]])
def test_invalid_times_leave_no_output(video, tmp_path, times):
    output = tmp_path / "out"
    with pytest.raises(pipeline.VideoError):
        pipeline.extract_frames(video, times, output)
    assert not output.exists()

@pytest.mark.parametrize("kind", ["missing", "directory", "empty", "corrupt", "audio"])
def test_invalid_input(tmp_path, kind):
    source = tmp_path / "bad.mp4"
    if kind == "directory":
        source.mkdir()
    elif kind == "empty":
        source.touch()
    elif kind == "corrupt":
        source.write_bytes(b"not a video")
    elif kind == "audio":
        with av.open(str(source), "w") as container:
            stream = container.add_stream("aac", rate=48000)
            frame = av.AudioFrame(format="fltp", layout="mono", samples=1024)
            frame.sample_rate = 48000
            for plane in frame.planes:
                plane.update(bytes(plane.buffer_size))
            for packet in stream.encode(frame):
                container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)
    with pytest.raises(pipeline.VideoError):
        pipeline.inspect_video(source)

def test_existing_output_and_input_protected(video, tmp_path):
    output = tmp_path / "out"
    output.mkdir()
    existing = output / "sentinel.txt"
    existing.write_text("keep", encoding="utf-8")
    for target in (output, video, video.parent):
        with pytest.raises(pipeline.VideoError):
            pipeline.extract_frames(video, [0], target)
    assert existing.read_text() == "keep"

def test_output_is_file(video, tmp_path):
    target = tmp_path / "file"
    target.write_text("keep")
    with pytest.raises(pipeline.VideoError):
        pipeline.extract_frames(video, [0], target)
    assert target.read_text() == "keep"

@pytest.mark.parametrize("rotation,expected_size,corner", [
    (0,(64,48),(2,2)), (90,(48,64),(2,61)),
    (180,(64,48),(61,45)), (270,(48,64),(45,2)),
])
def test_real_display_rotation(tmp_path, rotation, expected_size, corner):
    source = make_video(tmp_path / "rot.mp4", rotation=rotation)
    output = tmp_path / "out"
    report = pipeline.extract_frames(source, [0], output)
    assert report["video"]["rotation_degrees"] == rotation
    assert report["results"][0]["output_width"] == expected_size[0]
    with Image.open(output / report["results"][0]["image"]) as image:
        assert image.size == expected_size
        assert min(image.getpixel(corner)) >= 245

def test_arbitrary_rotation_rejected(tmp_path):
    source = make_video(tmp_path / "rot.mp4", rotation=45)
    with pytest.raises(pipeline.VideoError, match="transform|rotation"):
        pipeline.extract_frames(source, [0], tmp_path / "out")

def test_git_ignores_data_and_generated_output():
    import subprocess
    root = Path(__file__).resolve().parents[3]
    paths = ["local_data/recordings/private.mp4", "outputs/m1/frame.png",
             ".venv/test", "tools/offline_video/src/__pycache__/cache.pyc",
             "tools/offline_video/.pytest_cache/test", "tools/offline_video/build/test"]
    result = subprocess.run(["git", "check-ignore", *paths], cwd=root,
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == len(paths)


@pytest.mark.parametrize("options", [{"hflip": True}, {"hdr": True}, {"sar": Fraction(2,1)}])
def test_real_unsupported_display_formats(tmp_path, options):
    source = make_video(tmp_path / "unsupported.mp4", **options)
    with pytest.raises(pipeline.VideoError, match="Unsupported"):
        pipeline.extract_frames(source, [0], tmp_path / "out")
    report = json.loads((tmp_path / "out/report.json").read_text(encoding="utf-8"))
    assert report["status"] == "error"
    assert not list((tmp_path / "out").glob("*.png"))


def test_missing_optional_metadata_is_unknown(video):
    with av.open(str(video)) as container:
        actual = container.streams.video[0]
        frame = next(container.decode(actual))
        stream = SimpleNamespace(duration=None, time_base=actual.time_base,
                                 average_rate=None, sample_aspect_ratio=actual.sample_aspect_ratio,
                                 index=actual.index, codec_context=actual.codec_context)
        info = pipeline._video_info(video, SimpleNamespace(duration=None), stream, frame)
        assert info["duration_seconds"] is None
        assert info["duration_source"] is None
        assert info["average_fps"] is None
        assert len(info["warnings"]) >= 2


@pytest.mark.parametrize("kind", ["missing_pts", "missing_time_base", "duplicate", "backwards", "empty", "dimensions"])
def test_decoder_timeline_errors_reported(video, tmp_path, monkeypatch, kind):
    # MP4 muxers enforce timestamps, so inject only the decoded-frame boundary.
    # Everything else uses a real container and real decoded frames.
    original_open = av.open

    class DecodeOverride:
        def __init__(self, *args, **kwargs):
            self.container = original_open(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self.container, name)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.container.close()

        def decode(self, stream):
            if kind == "empty":
                return
            first_pts = None
            for i, frame in enumerate(self.container.decode(stream)):
                if i == 0:
                    first_pts = frame.pts
                    if kind == "missing_pts":
                        frame.pts = None
                    elif kind == "missing_time_base":
                        frame.time_base = Fraction(0, 1)
                elif i == 1:
                    if kind == "duplicate":
                        frame.pts = first_pts
                    elif kind == "backwards":
                        frame.pts = first_pts - 1
                    elif kind == "dimensions":
                        frame = frame.reformat(width=32, height=24)
                yield frame

    monkeypatch.setattr(av, "open", DecodeOverride)
    output = tmp_path / "out"
    with pytest.raises(pipeline.VideoError):
        pipeline.extract_frames(video, [0, 0.2], output)
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "error"
    assert report["warnings"]
    assert report["results"][1]["status"] == "error"


def test_unwritable_png_produces_error_report(video, tmp_path, monkeypatch):
    original_open = Path.open

    def denied_png(path, *args, **kwargs):
        if path.suffix == ".png":
            raise PermissionError("simulated filesystem permission denial")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied_png)
    output = tmp_path / "out"
    with pytest.raises(pipeline.VideoError):
        pipeline.extract_frames(video, [0], output)
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "error"
    assert report["results"][0]["status"] == "error"
    assert report["results"][0]["reason"]


def test_cover_stream_not_selected(video):
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        cover = SimpleNamespace(disposition=av.stream.Disposition.attached_pic)
        wrapper = SimpleNamespace(format=container.format,
                                  streams=SimpleNamespace(video=[cover, stream]))
        assert pipeline._stream(wrapper) is stream


def test_unwritable_output_reports_report_failure(video, tmp_path, monkeypatch):
    original_open = Path.open
    output = tmp_path / "out"

    def denied_output(path, *args, **kwargs):
        if path.parent == output:
            raise PermissionError("simulated directory write denial")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied_output)
    with pytest.raises(pipeline.VideoError, match="report.*not.*written"):
        pipeline.extract_frames(video, [0], output)
    assert not list(output.iterdir())
