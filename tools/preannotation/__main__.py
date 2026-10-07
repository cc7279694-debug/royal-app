"""Run from repository root: python -m tools.preannotation --help."""
from __future__ import annotations

import argparse
import copy
import json
import mimetypes
import sys
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import av
from PIL import Image, ImageDraw

from .bundle import (file_sha, import_return, load_bundle, prepare_bundle, read_json,
                     refresh_presentation, safe_bundle_path, write_json)
from .contract import require, return_template, validate_return


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "outputs/existing-multiclass-benchmark/katacr-20261007-01"
INVENTORY = ROOT / "outputs/module2b2/data-preparation-20261005-9957a75d15744495935bb2fd67f07ac6/pending-dataset.v3.json"
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"


def private_output(value: str) -> Path:
    path = Path(value).resolve()
    require(path.is_relative_to(ROOT / "outputs/milestone1") and path != ROOT / "outputs/milestone1",
            "private outputs must be a new directory under outputs/milestone1")
    return path


def create_demo(out: Path) -> dict:
    """Entirely synthetic clip and explicit synthetic five-operation return."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    inputs = out / "synthetic-inputs"
    inputs.mkdir()
    source = inputs / "synthetic.mp4"
    boxes = [[30, 180, 90, 250], [140, 180, 200, 250], [250, 180, 310, 250],
             [30, 400, 90, 470], [140, 400, 200, 470]]
    with av.open(str(source), mode="w") as container:
        stream = container.add_stream("mpeg4", rate=2)
        stream.width, stream.height, stream.pix_fmt = 432, 960, "yuv420p"
        for index in range(3):
            image = Image.new("RGB", (432, 960), "#17232d")
            drawing = ImageDraw.Draw(image)
            drawing.text((25, 35), f"SYNTHETIC REVIEW DEMO / FRAME {index + 1}", fill="white")
            for row, box in enumerate(boxes):
                drawing.rectangle(box, fill=["#d8bd75", "#7dbb9f", "#ba98d3", "#80b1d1", "#cc9a87"][row])
                drawing.text((box[0], box[3] + 8), f"shape {row + 1}", fill="white")
            frame = av.VideoFrame.from_image(image)
            frame.pts, frame.time_base = index, Fraction(1, 2)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    with av.open(str(source)) as container:
        frames = [{"raw_pts": frame.pts, "time_base": str(frame.time_base),
                   "timestamp_seconds": float(frame.pts * frame.time_base),
                   "detections": [{"class": "witch", "confidence": .75,
                                   "owner_prediction": "opponent", "bbox_xyxy_original": box}
                                  for box in boxes]} for frame in container.decode(video=0)]
    config = inputs / "config.json"
    write_json(config, {"source_recording": str(source.resolve()), "source_sha256": file_sha(source),
                       "underlying_match_id": "natural_match_01", "source_dimensions_wh": [432, 960], "synthetic_input": True})
    predictions = inputs / "predictions.json"
    write_json(predictions, {"schema": "offline_predictions_v1", "config_sha256": file_sha(config), "frames": frames})
    bundle = prepare_bundle(predictions, config, out / "bundle", stride=1, max_frames=3, prediction_format="generic")
    returned = return_template(bundle)
    returned["provenance"] = {"kind": "synthetic", "reviewer": "synthetic five-operation demonstration",
                              "synthetic": True, "human_review_attested": False}
    def decision(frame_index, row, action="accept", **changes):
        proposal = bundle["frames"][frame_index]["proposals"][row]
        return {"proposal_id": proposal["proposal_id"], "action": action,
                "decision": "rejected" if action == "reject" else "accepted",
                "visual_class": "visual.unit.witch", "canonical_mapping": "unit.witch",
                "bbox_xyxy": copy.deepcopy(proposal["bbox_xyxy"]), "owner": "unknown", "form": "unknown",
                "origin": "unknown", "appearance_id": f"shape-{row}", "visibility": "visible", "uncertainty": "none",
                "note": "synthetic demonstration only", **changes}
    returned["frames"][0]["decisions"] = [decision(0, 0), decision(0, 1, "reject", visual_class=None, canonical_mapping=None, appearance_id=None),
        decision(0, 2, "relabel", visual_class="visual.unit.balloon", canonical_mapping="unit.balloon"),
        decision(0, 3, "bbox-correct", bbox_xyxy=[32, 402, 88, 468]),
        decision(0, 4, "missing-box", proposal_id=None, manual_id="missing-1", appearance_id="missing-shape",
                 bbox_xyxy=[250, 400, 310, 470])]
    returned["frames"][1]["decisions"] = [decision(1, 0)]
    returned["frames"][2]["decisions"] = [decision(2, 0)]
    write_json(out / "synthetic-return.json", returned)
    gt = import_return(out / "bundle", out / "synthetic-return.json", out / "synthetic-revision-v1", allow_synthetic=True)
    return {"status": gt["status"], "bundle": str(out / "bundle"), "page": str(out / "bundle/review.html"),
            "five_actions": [d["action"] for d in returned["frames"][0]["decisions"]],
            "positive_boxes": len(gt["positive_boxes"]), "appearance_groups": len(gt["appearance_groups"]),
            "independent_deployments": gt["independent_deployments"], "training_qualified": gt["training_qualified"]}


def make_server(bundle_root: Path, port: int) -> ThreadingHTTPServer:
    root = Path(bundle_root).resolve()
    load_bundle(root)
    allowed = read_json(root / "manifest.json")["files"]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.respond(False)

        def do_HEAD(self):
            self.respond(True)

        def respond(self, head_only):
            if self.headers.get("Host", "").split(":")[0].lower() not in {"localhost", "127.0.0.1"}:
                self.send_error(403)
                return
            route = unquote(urlsplit(self.path).path)
            if route == "/favicon.ico":
                self.send_response(204)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            name = "review.html" if route == "/" else route.removeprefix("/")
            if name not in allowed:
                self.send_error(404)
                return
            try:
                path = safe_bundle_path(root, name)
                require(file_sha(path) == allowed[name], "immutable served member changed")
                payload = path.read_bytes()
            except (OSError, ValueError):
                self.send_error(409)
                return
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if not head_only:
                self.wfile.write(payload)

        def log_message(self, _format, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline pending visual proposals / separate human correction revisions")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="copy immutable teacher bytes and export exact source PTS PNGs")
    prepare.add_argument("--predictions", type=Path, default=BENCHMARK / "detections.json")
    prepare.add_argument("--config", type=Path, default=BENCHMARK / "probe-config.json")
    prepare.add_argument("--inventory", type=Path, default=INVENTORY)
    prepare.add_argument("--format", choices=["katacr", "generic"], default="katacr")
    prepare.add_argument("--stride", type=int, default=20)
    prepare.add_argument("--max-frames", type=int, default=12)
    prepare.add_argument("--out", required=True)
    presentation = commands.add_parser("presentation", help="create a new presentation from unchanged bundle data/PNGs; no video decode")
    presentation.add_argument("--bundle", type=Path, required=True)
    presentation.add_argument("--out", required=True)
    validate = commands.add_parser("validate", help="validate immutable files and optionally a separate human return")
    validate.add_argument("--bundle", type=Path, required=True)
    validate.add_argument("--return", dest="return_file", type=Path)
    validate.add_argument("--synthetic", action="store_true", help="explicitly validate simulation, never human GT")
    importer = commands.add_parser("import", help="validate then create a new exclusive reviewed annotation revision")
    importer.add_argument("--bundle", type=Path, required=True)
    importer.add_argument("--return", dest="return_file", type=Path, required=True)
    importer.add_argument("--revision", required=True)
    importer.add_argument("--synthetic", action="store_true", help="explicit synthetic-only revision")
    demo = commands.add_parser("demo", help="create synthetic five-action round-trip, never real human GT")
    demo.add_argument("--out", required=True)
    server = commands.add_parser("serve", help="read-only loopback reviewer; no upload endpoints or external connections")
    server.add_argument("--bundle", type=Path, required=True)
    server.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            bundle = prepare_bundle(args.predictions, args.config, private_output(args.out), inventory_path=args.inventory,
                                    stride=args.stride, max_frames=args.max_frames, prediction_format=args.format)
            result = {"status": "pending_human_review", "frames": len(bundle["frames"]),
                      "proposals": sum(len(f["proposals"]) for f in bundle["frames"]),
                      "bundle_sha256": bundle["bundle_sha256"], "page": str(Path(args.out) / "review.html")}
        elif args.command == "presentation":
            refreshed = refresh_presentation(args.bundle, private_output(args.out))
            result = {"status": "new_presentation_same_data_identity", "bundle_sha256": refreshed["bundle_sha256"],
                      "page": str(Path(args.out) / "review.html")}
        elif args.command == "validate":
            bundle = load_bundle(args.bundle)
            if args.return_file:
                result = validate_return(bundle, read_json(args.return_file), allow_synthetic=args.synthetic)
            else:
                result = {"status": "valid_pending_bundle", "frames": len(bundle["frames"]), "bundle_sha256": bundle["bundle_sha256"]}
        elif args.command == "import":
            result = import_return(args.bundle, args.return_file, private_output(args.revision), allow_synthetic=args.synthetic)
        elif args.command == "demo":
            result = create_demo(private_output(args.out))
        else:
            require(0 <= args.port <= 65535, "invalid loopback port")
            service = make_server(args.bundle, args.port)
            print(f"Read-only local review: http://127.0.0.1:{service.server_port}/", flush=True)
            try:
                service.serve_forever()
            finally:
                service.server_close()
            return 0
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError) as error:
        print(f"preannotation: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
