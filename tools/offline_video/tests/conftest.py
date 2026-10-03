from fractions import Fraction
from pathlib import Path

import av
import pytest
from PIL import Image

COLORS = [(240, 20, 20), (20, 240, 20), (20, 20, 240), (220, 220, 20)]

def make_video(path: Path, pts=(0, 100, 200, 300), rotation=0, hflip=False, hdr=False, sar=None):
    """Encode real MP4 frames with independently chosen millisecond PTS."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with av.open(str(path), "w") as container:
        stream = container.add_stream("libx264", rate=10)
        stream.width, stream.height = 64, 48
        stream.pix_fmt = "yuv420p"
        stream.time_base = Fraction(1, 1000)
        stream.codec_context.time_base = Fraction(1, 1000)
        stream.options = {"bf": "0", "crf": "0"}
        if rotation or hflip:
            stream.set_display_rotation(rotation, hflip=hflip)
        if hdr:
            stream.codec_context.color_trc = 16
        if sar:
            stream.codec_context.sample_aspect_ratio = sar
        for i, timestamp in enumerate(pts):
            image = Image.new("RGB", (64, 48), COLORS[i % 4])
            # Asymmetric white corner makes rotation observable.
            image.paste((255, 255, 255), (0, 0, 12, 8))
            frame = av.VideoFrame.from_image(image)
            frame.pts, frame.time_base = timestamp, Fraction(1, 1000)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    return path

@pytest.fixture
def video(tmp_path):
    return make_video(tmp_path / "中文 录像.mp4")
