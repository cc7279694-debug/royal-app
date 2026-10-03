"""CLI for user-selected local files."""
import argparse
import sys
from pathlib import Path

from .pipeline import VideoError, extract_frames, inspect_video


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Local SDR MP4 inspection and PNG extraction.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Inspect first actual video stream.")
    inspect.add_argument("input")
    extract = sub.add_parser("extract", help="Extract by seconds relative to first display frame.")
    extract.add_argument("input")
    extract.add_argument("--times", type=float, nargs="+", required=True)
    extract.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            info = inspect_video(args.input)
            print(f"File: {info['filename']}")
            print(f"Video stream: {info['stream_index']} | Codec: {info['codec']}")
            print(f"Encoded size: {info['width']} x {info['height']}")
            print(f"Duration: {info['duration_seconds']} s | source: {info['duration_source'] or 'unknown'}")
            print(f"Average FPS (metadata only): {info['average_fps'] or 'unknown'}")
            print(f"Display rotation (counterclockwise): {info['rotation_degrees']} degrees")
            for warning in info["warnings"]:
                print(f"Warning: {warning}")
            return 0
        report = extract_frames(args.input, args.times, args.output)
        successes = sum(e["status"] == "success" for e in report["results"])
        print(f"{successes}/{len(report['results'])} targets extracted; status: {report['status']}")
        print(f"Report: {Path(args.output) / 'report.json'}")
        return 0 if report["status"] == "success" else 3
    except VideoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
