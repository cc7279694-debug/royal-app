"""Exclusive presentation of manually selected windows; no event engine or GT import."""
from __future__ import annotations

import copy
import csv
import hashlib
import html
import json
import math
import re
import shutil
import zipfile
from fractions import Fraction
from pathlib import Path, PureWindowsPath

from PIL import Image, ImageDraw


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _relative(value: str) -> str:
    _require(isinstance(value, str) and bool(value) and "\\" not in value and ":" not in value
             and not Path(value).is_absolute() and not PureWindowsPath(value).is_absolute()
             and ".." not in Path(value).parts, "unsafe presentation member")
    return value


def _path(root: Path, relative: str) -> Path:
    path = root / _relative(relative)
    _require(path.resolve().is_relative_to(root.resolve()), "member escaped presentation root")
    _require(not any(parent.is_symlink() for parent in [path, *path.parents] if parent != root.parent),
             "symlink presentation member")
    return path


def _sha(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
        stream.write("\n")


def validate_plan(plan: dict) -> None:
    """Validate manual review input, not card rules or event truth."""
    _require(plan.get("schema") == "deployment_event_review_plan_v1", "unsupported manual plan")
    _require(not plan.get("confirmed_card_events") and not plan.get("card_events")
             and plan.get("human_review_attested", False) is False
             and plan.get("confirmed_event_count", 0) == 0
             and plan.get("independent_confirmed_card_play_count", 0) == 0
             and not plan.get("negative_evidence") and plan.get("event_gt_lock_created", False) is False,
             "manual review plan cannot carry truth or negative claims")
    inventory = plan.get("inventory", [])
    _require(bool(inventory) and [i.get("intake_order") for i in inventory] == list(range(1, len(inventory) + 1)),
             "recordings must retain original intake order")
    pairs = [(i["underlying_match_id"], i["recording_id"]) for i in inventory]
    _require(len(set(pairs)) == len(pairs), "duplicate recording identity")
    _require(len({i["recording_id"] for i in inventory}) == len(inventory),
             "one recording cannot belong to different underlying matches")
    sources = {s["source_id"] for s in plan.get("evidence_sources", [])}
    _require(bool(sources) and len(sources) == len(plan["evidence_sources"])
             and all(re.fullmatch(r"[a-f0-9]{64}", s["sha256"])
                                 for s in plan["evidence_sources"]), "bound visual sources required")
    seen, order = set(), []
    candidates = plan.get("candidates", [])
    _require(isinstance(candidates, list) and bool(candidates), "manual candidate windows required")
    for c in candidates:
        cid = c.get("candidate_id", "")
        _require(re.fullmatch(r"[A-Za-z0-9_-]+", cid) is not None and cid not in seen, "duplicate/invalid candidate id")
        seen.add(cid)
        pair = (c.get("underlying_match_id"), c.get("recording_id"))
        _require(pair in pairs, "recording and underlying match binding mismatch")
        idx = pairs.index(pair)
        _require(inventory[idx]["disposition"] == "candidate_context", "excluded recording cannot supply candidates")
        time = c.get("approximate_timestamp")
        _require(type(time) in (int, float) and math.isfinite(time) and time >= 0, "invalid anchor time")
        order.append((idx, time))
        _require(c.get("timestamp_kind") == "visual_anchor_not_confirmed_spawn", "visual anchor is not deployment time")
        _require(c.get("review_state") == "pending_human_review" and c.get("evaluable") is False
                 and c.get("confidence") == "uncertain", "packager cannot confirm event truth")
        _require(c.get("owner") in {"opponent", "unknown"}, "own visual evidence cannot become opponent candidate")
        _require(c.get("card_id") in {"witch", "golden_knight", "flying_machine", "mortar",
                                      "skeleton_barrel", "minions", "royal_hogs", None}, "unsupported/visual-only card hint")
        _require(c.get("form") in {"normal", "evolved", "unknown"} and
                 c.get("event_type") in {"direct", "grouped", "uncertain"}, "invalid pending metadata")
        _require(bool(c.get("evidence_visual_classes")) and bool(c.get("evidence_frame_ids"))
                 and bool(c.get("visual_refs")), "existing visual evidence required")
        _require(all(r.get("source_id") in sources and bool(r.get("object_id")) for r in c["visual_refs"]),
                 "unbound visual reference")
        _require(all(r.get("owner") in {"opponent", "unknown"} for r in c["visual_refs"]),
                 "own reference cannot be presented as an opponent candidate")
        _require(bool(c.get("candidate_reason")) and isinstance(c.get("notes"), str), "manual reason and limits required")
        context = c["context"]
        start, end = context["start_seconds"], context["end_seconds"]
        _require(all(type(v) in (int, float) and math.isfinite(v) for v in (start, end))
                 and 0 <= start <= time <= end and start < end, "invalid context interval")
        _relative(context["clip"])
        _require(context.get("clip_presentation_only") is True, "context clip is not an exact timestamp source")
        _require(re.fullmatch(r"[a-f0-9]{64}", context["source_sha256"]) is not None, "source video SHA required")
        _require(context["source_sha256"] == inventory[idx].get("source_sha256"),
                 "context source video differs from selected recording")
        frames = context.get("frames", [])
        _require(bool(frames), "exact-PTS context frames required")
        times = []
        for f in frames:
            _relative(f["image"])
            _require(type(f["raw_pts"]) is int and Fraction(f["time_base"]) > 0, "exact PTS required")
            exact = f["raw_pts"] * Fraction(f["time_base"]) - Fraction(f["origin_seconds_exact"])
            _require(f["timestamp_seconds"] == float(exact) and start <= float(exact) <= end,
                     "context timestamp/PTS mismatch")
            times.append(exact)
        _require(times == sorted(set(times)), "context frames must be unique and chronological")
    _require(order == sorted(order), "candidates must retain recording/time order")
    for c in candidates:
        hint = c.get("duplicate_hint")
        _require(hint is None or (hint in seen and hint != c["candidate_id"]), "invalid duplicate review hint")
        if hint is not None:
            other = next(item for item in candidates if item["candidate_id"] == hint)
            _require(other["underlying_match_id"] == c["underlying_match_id"],
                     "duplicate review hint cannot cross underlying matches")


def return_template(plan: dict) -> dict:
    validate_plan(plan)
    return {"schema": "deployment_event_human_return_draft_v1", "reviewer": "", "human_review_attested": False,
            "confirmed_card_events": [], "negative_evidence": [], "decisions": [{
                "candidate_id": c["candidate_id"], "decision": "pending", "corrected_card": None,
                "corrected_owner": None, "corrected_timestamp": None, "corrected_form": None,
                "last_absent_seconds": None, "first_visible_seconds": None, "merge_into": None,
                "uncertainty_reason": "", "notes": ""} for c in plan["candidates"]]}


def write_bundle(plan: dict, media_root: Path, out: Path) -> dict:
    validate_plan(plan)
    media_root, out = Path(media_root), Path(out)
    _require(not out.resolve().is_relative_to(media_root.resolve())
             and not media_root.resolve().is_relative_to(out.resolve()), "output cannot overlap source media")
    files = {c["context"]["clip"] for c in plan["candidates"]}
    files.update(f["image"] for c in plan["candidates"] for f in c["context"]["frames"])
    for name in files:
        _require(_path(media_root, name).is_file(), "missing presentation media")
    out.mkdir(parents=True, exist_ok=False)
    for name in sorted(files):
        target = _path(out, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as destination, _path(media_root, name).open("rb") as source:
            shutil.copyfileobj(source, destination)
    pending = copy.deepcopy(plan)
    pending.update(confirmed_event_count=0, negative_evidence=[], event_gt_lock_created=False)
    _write_json(out / "candidates.json", pending)
    returned = return_template(plan)
    _write_json(out / "human-return.template.json", returned)
    fields = list(returned["decisions"][0])
    with (out / "event-review.csv").open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(returned["decisions"])
    instructions = """# Deployment Event Human Review — pending, not Ground Truth

Watch each context MP4 and inspect its exact-PTS contact sheet. All card/owner/time
hints are provisional. First visual evidence is NOT proof of a new deployment.
If spawn is outside the supplied window, mark uncertain and request wider context;
do not guess a timestamp or confirm from persistent-unit screenshots alone.

Fill event-review.csv or human-return.template.json using:
confirm / reject / uncertain / merge_duplicate. A confirm may also correct card,
owner, form or timestamp. Use corrected_* fields, last_absent/first_visible,
merge_into, uncertainty_reason and notes. Retain the candidate IDs.

Only an explicitly human-attested opponent NEW deployment may later become GT.
Own objects, unknown owner, visual-only/null source-card mappings and spawned
Skeletons cannot become opponent card plays. A grouped card is one event, not one
per unit. Persistent/reappearing entities must be merged or rejected as duplicate.
Rejected/uncertain/unreviewed candidates never become Negative evidence.

ChatGPT suggestions need explicit user confirmation; do not call ChatGPT a human
reviewer. This package does not import results, freeze an Event GT Lock or run an
event engine. No training, App connection or gameplay HUD is enabled.
"""
    with (out / "HUMAN_REVIEW.md").open("x", encoding="utf-8") as stream:
        stream.write(instructions)
    (out / "contacts").mkdir()
    sections = []
    escape = html.escape
    for c in plan["candidates"]:
        frames = c["context"]["frames"]
        sheet = Image.new("RGB", (5 * 190, math.ceil(len(frames) / 5) * 350), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        for n, frame in enumerate(frames):
            x, y = (n % 5) * 190, (n // 5) * 350
            with Image.open(_path(out, frame["image"])) as image:
                thumb = image.convert("RGB")
                thumb.thumbnail((180, 305))
                sheet.paste(thumb, (x + 5, y + 5))
            draw.text((x + 5, y + 313), f"{frame['timestamp_seconds']:.3f}s  PTS {frame['raw_pts']}", fill="black")
        name = f"contacts/{c['candidate_id']}.jpg"
        sheet.save(out / name, quality=92)
        label = f"{c['candidate_id']} | {c['underlying_match_id']} | {c['recording_id']}"
        content = json.dumps({k: c[k] for k in c if k != "context"}, indent=2, ensure_ascii=False)
        sections.append(f'<section><h2>{escape(label)}</h2><p>Pending hint: {escape(str(c["card_id"]))} / '
                        f'{escape(c["owner"])} / {c["approximate_timestamp"]:.3f}s — NOT confirmed spawn.</p>'
                        f'<video controls preload="none" src="{escape(c["context"]["clip"], quote=True)}"></video>'
                        f'<p><a href="{name}">Full contact sheet</a></p><img src="{name}"><pre>{escape(content)}</pre>'
                        + "".join(f'<a href="{escape(f["image"], quote=True)}">{f["timestamp_seconds"]:.3f}s original</a> '
                                  for f in frames) + '</section>')
    with (out / "index.html").open("x", encoding="utf-8") as stream:
        stream.write('<!doctype html><meta charset="utf-8"><title>Pending Deployment Review</title>'
                     '<style>body{font-family:system-ui;margin:24px}video{width:260px}img{max-width:100%}'
                     'pre{white-space:pre-wrap}section{border-top:2px solid #aaa;padding:20px 0}</style>'
                     '<h1>Manual review — 0 confirmed card plays</h1><p>Visual anchors are not deployment timestamps. '
                     'Open HUMAN_REVIEW.md; complete event-review.csv. No candidate is auto-confirmed.</p>'
                     + "".join(sections))
    manifest = {"schema": "deployment_event_review_manifest_v1", "confirmed_event_count": 0,
                "files": {p.relative_to(out).as_posix(): _sha(p) for p in sorted(out.rglob("*")) if p.is_file()}}
    _write_json(out / "manifest.json", manifest)
    return manifest


def zip_bundle(root: Path, archive: Path) -> None:
    root, archive = Path(root), Path(archive)
    manifest_bytes = (root / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    _require(manifest.get("schema") == "deployment_event_review_manifest_v1", "unsupported manifest")
    for name, sha in manifest["files"].items():
        _require(_sha(_path(root, name)) == sha, "presentation member changed")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as zipped:
        for name in sorted(manifest["files"]):
            zipped.write(_path(root, name), name)
        zipped.write(root / "manifest.json", "manifest.json")
    # Verify the bytes actually archived, not only earlier reads of the folder.
    # Failed exclusive archives are retained for diagnosis, never reported ready.
    with zipfile.ZipFile(archive) as zipped:
        _require(zipped.testzip() is None and zipped.read("manifest.json") == manifest_bytes,
                 "archive manifest/CRC changed")
        _require(set(zipped.namelist()) == set(manifest["files"]) | {"manifest.json"}, "archive member mismatch")
        for name, expected in manifest["files"].items():
            actual = hashlib.sha256()
            with zipped.open(name) as member:
                for chunk in iter(lambda: member.read(1024 * 1024), b""):
                    actual.update(chunk)
            _require(actual.hexdigest() == expected, "archive member bytes changed during packaging")
