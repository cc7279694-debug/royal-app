"""Private-source ByteTrack sidecar: geometric identity hypotheses, never events.

The hash-bound official core stays outside Git. Loading it requires an explicitly
supplied source directory and a compatible isolated NumPy/SciPy/LAP environment.
No detector, GT, scorer, learned appearance model or owner correction is imported.
"""
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace


UPSTREAM_COMMIT = "d1bf0191adff59bc8fcfeaa0b33d3d1642552a99"
SOURCE_HASHES = {
    "basetrack.py": "03f1fb99d1edc094f42c7510d0142626fe31b99bcef28e0e4327eef034c1885b",
    "byte_tracker.py": "6b16fcee83568102d4c8718d1d8ffe5cb89c32bdae64702d5b45602cb1bb058e",
    "kalman_filter.py": "c9d28b2b5943acbf89ce8cfc579f5da8350842080467e85ee04aa62119cea7ba",
    "matching.py": "5ed8540620562fa70ec73f6d056e4ad10f2bf5ad7c8e824172ee7f60cd7460b6",
    "LICENSE": "034dd352af190b6037e784ecc4874bcd224248290493fd22bf1d82ed101a4309",
    "NOTICE": "c575d3f157c657cc9b74d81a76614b9158b192b1a029bbe3367db89060d0544c",
}
DEFAULT_CONFIG = {"high_thresh": .5, "low_thresh": .1, "match_thresh": .8,
                  "buffer_seconds": 2., "sample_fps": 4., "mot20": False}
TRACKING_CONFIG = dict(DEFAULT_CONFIG)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def load_backend(source_root):
    """Verify bytes before executing this exact private four-file source closure."""
    root = Path(source_root).resolve(strict=True)
    _require(root.is_dir(), "ByteTrack source directory required")
    manifest_path = root / "provenance.json"
    _require(manifest_path.is_file() and not manifest_path.is_symlink(), "source provenance required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(manifest.get("upstream_commit") == UPSTREAM_COMMIT, "source commit mismatch")
    _require(manifest.get("adapted_sha256") == SOURCE_HASHES, "source manifest hash mismatch")
    verified = {}
    for name, expected in SOURCE_HASHES.items():
        path = root / name
        _require(path.is_file() and not path.is_symlink(), "source file or notice missing")
        data = path.read_bytes()
        _require(hashlib.sha256(data).hexdigest() == expected, "source hash mismatch: " + name)
        verified[name] = data
    # A private namespace avoids importing YOLOX/Ultralytics or writing bytecode.
    # Execute the verified bytes, rather than reopening paths after hashing.
    name = "_clash_private_bytetrack"
    for key in list(sys.modules):
        if key == name or key.startswith(name + "."):
            del sys.modules[key]
    package = ModuleType(name)
    package.__path__ = []
    sys.modules[name] = package
    try:
        for file in ("basetrack.py", "kalman_filter.py", "matching.py", "byte_tracker.py"):
            subname = name + "." + file[:-3]
            part = ModuleType(subname)
            part.__package__ = name
            part.__file__ = str(root / file)
            sys.modules[subname] = part
            setattr(package, file[:-3], part)
            exec(compile(verified[file], part.__file__, "exec"), part.__dict__)
    except BaseException:
        for key in list(sys.modules):
            if key == name or key.startswith(name + "."):
                del sys.modules[key]
        raise
    return package


def _validate(observations, frames):
    _require(isinstance(observations, list), "observations array required")
    _require(isinstance(frames, list) and frames, "frames including empty frames required")
    frame_keys = set()
    times_by_match = defaultdict(list)
    for frame in frames:
        _require(isinstance(frame, dict) and isinstance(frame.get("match_id"), str)
                 and frame["match_id"], "frame match_id required")
        _require(_number(frame.get("timestamp")) and frame["timestamp"] >= 0, "invalid frame timestamp")
        key = (frame["match_id"], frame["timestamp"])
        _require(key not in frame_keys, "duplicate frame timestamp")
        frame_keys.add(key)
        times_by_match[frame["match_id"]].append(frame["timestamp"])
    for times in times_by_match.values():
        ordered_times = sorted(times)
        _require(all(abs((later - earlier) - .25) <= 1e-6
                     for earlier, later in zip(ordered_times, ordered_times[1:])),
                 "contiguous frozen 4FPS cadence required, including empty frames")
    seen = set()
    for row in observations:
        _require(isinstance(row, dict), "observation object required")
        for field in ("observation_id", "match_id", "visual_class", "owner"):
            _require(isinstance(row.get(field), str) and row[field], "missing observation " + field)
        oid = row["observation_id"]
        _require("appearance_group_id" not in row and "human_identity" not in row
                 and "track_id" not in row, "human or prior appearance/track identity is forbidden")
        _require(row.get("source") in {"katacr_prediction", "synthetic"}, "unapproved observation source")
        _require(oid not in seen, "duplicate observation_id")
        seen.add(oid)
        _require(_number(row.get("timestamp")) and row["timestamp"] >= 0, "invalid observation timestamp")
        _require((row["match_id"], row["timestamp"]) in frame_keys, "observation frame missing")
        _require(_number(row.get("confidence")) and 0 <= row["confidence"] <= 1,
                 "missing or invalid confidence")
        box = row.get("bbox")
        _require(isinstance(box, list) and len(box) == 4 and all(_number(v) for v in box)
                 and box[0] < box[2] and box[1] < box[3], "invalid observation bbox")


def _stable_id(match, visual_class, first_observation_id):
    text = json.dumps([match, visual_class, first_observation_id], ensure_ascii=False, separators=(",", ":"))
    return "byte-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def track_stream(observations, frames, source_root, config=None):
    """Attach one diagnostic association per original row; preserve raw inputs.

    Class partitions are independent; owner is never used for association. Low
    proposals can extend tracks but cannot manufacture births. Unconfirmed and
    ambiguous assignments are retained as hypotheses for later abstention.
    """
    selected = dict(DEFAULT_CONFIG)
    if config is not None:
        _require(isinstance(config, dict) and set(config) <= set(DEFAULT_CONFIG), "invalid tracker config")
        selected.update(config)
    _require(selected == DEFAULT_CONFIG, "tracker configuration is frozen for this experiment")
    _validate(observations, frames)
    backend = load_backend(source_root)
    import numpy as np

    ordered = sorted(deepcopy(observations), key=lambda r: (r["match_id"], r["timestamp"], r["observation_id"]))
    metadata = sorted(deepcopy(frames), key=lambda f: (f["match_id"], f["timestamp"]))
    row_by_id = {r["observation_id"]: r for r in ordered}
    buckets = defaultdict(list)
    classes = defaultdict(set)
    for row in ordered:
        buckets[(row["match_id"], row["timestamp"], row["visual_class"])].append(row)
        classes[row["match_id"]].add(row["visual_class"])
    args = SimpleNamespace(track_thresh=selected["high_thresh"], low_thresh=selected["low_thresh"],
                           match_thresh=selected["match_thresh"], mot20=selected["mot20"],
                           track_buffer=30 * selected["buffer_seconds"])
    trackers, registry, associations, frame_output = {}, {}, {}, []
    registry_by_partition, numeric_to_public = defaultdict(dict), {}
    for frame in metadata:
        match, timestamp = frame["match_id"], frame["timestamp"]
        frame_tracks = []
        for visual in sorted(classes[match]):
            key = (match, visual)
            if key not in trackers:
                trackers[key] = backend.byte_tracker.BYTETracker(args, frame_rate=selected["sample_fps"])
            tracker = trackers[key]
            current = buckets.get((match, timestamp, visual), [])
            matrix = np.asarray([r["bbox"] + [r["confidence"]] for r in current], dtype=np.float64).reshape(-1, 5)
            # Boxes are already in original coordinates: explicit scale=1.
            tracker.update(matrix, (1, 1), (1, 1), [r["observation_id"] for r in current])
            live = tracker.tracked_stracks + tracker.lost_stracks + tracker.removed_stracks
            by_numeric_id = {t.track_id: t for t in live}
            retained_ids = {_stable_id(match, visual, t.observation_ids[0]) for t in by_numeric_id.values()}
            # Upstream duplicate suppression drops a hypothesis without changing
            # its TrackState. Preserve the prior history and name that disappearance.
            for public_id, record in registry_by_partition[key].items():
                if public_id not in retained_ids \
                        and record["lifecycle"][-1]["state"] not in {"removed", "suppressed"}:
                    record["lifecycle"].append({"timestamp": timestamp, "state": "suppressed"})
            for track in by_numeric_id.values():
                first = row_by_id[track.observation_ids[0]]
                public_id = _stable_id(match, visual, first["observation_id"])
                state = {0: "new", 1: "tracked", 2: "lost", 3: "removed"}[track.state]
                if track.state == backend.basetrack.TrackState.Tracked and not track.is_activated:
                    state = "unconfirmed"
                if public_id not in registry:
                    registry[public_id] = {"track_id": public_id, "match_id": match, "visual_class": visual,
                                           "first_seen": first["timestamp"], "last_seen": first["timestamp"],
                                           "observation_ids": [], "owner_history": [], "lifecycle": []}
                    registry_by_partition[key][public_id] = registry[public_id]
                numeric_to_public[(match, visual, track.track_id)] = public_id
                record = registry[public_id]
                if not record["lifecycle"] or record["lifecycle"][-1]["state"] != state:
                    record["lifecycle"].append({"timestamp": timestamp, "state": state})
                record["observation_ids"] = list(track.observation_ids)
                record["last_seen"] = row_by_id[track.observation_ids[-1]]["timestamp"]
                record["owner_history"] = [{"observation_id": oid, "owner": row_by_id[oid]["owner"]}
                                           for oid in track.observation_ids]
                if state != "removed":
                    frame_tracks.append({"track_id": public_id, "state": state})
                if track.observation_id in {r["observation_id"] for r in current}:
                    associations[track.observation_id] = {"track_id": public_id, "state": state}
            for row in current:
                oid = row["observation_id"]
                diagnostic = associations.setdefault(oid, {"track_id": None, "state": "unassigned"})
                competitors = tracker.observation_competitors.get(oid, set())
                diagnostic["association_ambiguous"] = bool(competitors)
                diagnostic["competing_track_ids"] = sorted(
                    numeric_to_public[(match, visual, i)]
                    for i in competitors if (match, visual, i) in numeric_to_public)
                diagnostic["low_confidence"] = row["confidence"] <= selected["high_thresh"]
        frame_output.append(frame | {"track_states": sorted(frame_tracks, key=lambda r: r["track_id"])})
    enriched = [r | associations[r["observation_id"]]
                | {"association_ambiguity": associations[r["observation_id"]]["association_ambiguous"]}
                for r in ordered]
    return {"schema": "visual_track_sidecar_v1", "config": selected,
            "source": {"repository": "https://github.com/FoundationVision/ByteTrack",
                       "upstream_commit": UPSTREAM_COMMIT, "adapted_sha256": dict(SOURCE_HASHES),
                       "rights_clearance": "unverified", "private_local_research_only": True},
            "observations": enriched,
            "associations": [{"observation_id": r["observation_id"], "track_id": r["track_id"],
                              "association_ambiguous": r["association_ambiguous"]} for r in enriched],
            "tracks": sorted(registry.values(), key=lambda r: (r["match_id"], r["first_seen"], r["track_id"])),
            "frames": frame_output, "event_gt_used_as_input": False, "human_identity_used": False,
            "track_ids_are_identity_hypotheses": True, "unknown_is_negative": False}
