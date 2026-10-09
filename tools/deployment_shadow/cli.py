"""Generate sealed experimental outputs; Event GT is not a replay input."""
from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

from tools.event_engine.cli import verify_artifacts, write_artifacts
from tools.event_engine.oracle import file_sha, read_json
from tools.preannotation.bundle import parse_json_bytes
from .prototype import run_shadow


def read_detector_stream(path):
    # Prediction bindings are larger than the separate Oracle/GT metadata cap.
    if not path.is_file() or path.stat().st_size > 64*1024*1024:
        raise ValueError('detector stream missing or oversized')
    return parse_json_bytes(path.read_bytes())


def replay_files(replay_dir, out):
    source, out = Path(replay_dir).resolve(), Path(out).resolve()
    if source.is_relative_to(out) or out.is_relative_to(source):
        raise ValueError('output overlaps source evidence')
    if out.exists():
        raise ValueError('choose a new output version')
    manifest = verify_artifacts(source)
    if not {'detector-visual-stream.json', 'replay.json'} <= set(manifest['files']):
        raise ValueError('sealed detector replay required')
    before = file_sha(source/'manifest.json')
    stream = read_detector_stream(source/'detector-visual-stream.json')
    shadow = run_shadow(stream['observations'], stream['frames'])
    if shadow['baseline_replay'] != read_json(source/'replay.json'):
        raise ValueError('observations do not reproduce the frozen baseline')
    verify_artifacts(source)
    if file_sha(source/'manifest.json') != before:
        raise ValueError('source manifest changed during replay')
    result = deepcopy(shadow)
    baseline = result.pop('baseline_replay')
    summary = {'schema':'deployment_shadow_run_v1',
        'source_manifest_sha256':before, 'source_stream_sha256':manifest['files']['detector-visual-stream.json'],
        'baseline_event_count':len(baseline['events']), 'provisional_event_count':len(result['events']),
        'unresolved_candidate_count':len(result['unresolved']), 'event_gt_used_as_input':False,
        'model_inference_rerun':False, 'production_replacement':False,
        'confirmed_card_play_count':0, 'unknown_is_negative':False}
    write_artifacts(out, {'shadow-replay.json':result, 'baseline-replay.json':baseline,
        'opponent-card-played.json':{'events':result['events'], 'experimental_provisional_only':True},
        'card-play-candidates.json':{'candidates':result['candidates']},
        'unresolved.json':{'candidates':result['unresolved']},
        'time-evidence.json':{'evidence':result['time_evidence']}, 'source-summary.json':summary})
    return summary


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Shadow arguments rejected; private paths are not disclosed.\n')


def main(argv=None):
    parser = SafeParser(description='Offline provisional Spawn Group experiment; no game or GT input')
    parser.add_argument('--replay', required=True)
    parser.add_argument('--output', required=True)
    args=parser.parse_args(argv)
    try:
        import json
        print(json.dumps(replay_files(args.replay, args.output), allow_nan=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError,OverflowError):
        print('Shadow evidence rejected; private paths are not disclosed.')
        return 2
