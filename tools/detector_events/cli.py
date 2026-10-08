"""Separate prediction replay and post-seal evaluation; frozen engine untouched."""
import argparse
import json
from pathlib import Path
import time

from tools.event_engine.engine import replay
from tools.event_engine.cli import write_artifacts
from tools.preannotation.bundle import file_sha, read_json
from .adapter import convert_predictions, require


def replay_files(descriptor, out):
    require(set(descriptor) == {'sources'} and isinstance(descriptor['sources'], list)
            and descriptor['sources'], 'explicit prediction sources only')
    out = Path(out)
    require(not out.exists(), 'output already exists; select a new version')
    observations, sources, bindings, frames, matches = [], [], [], [], set()
    started = time.perf_counter()
    for item in descriptor['sources']:
        require(set(item) == {'predictions', 'config', 'prediction_sha256', 'config_sha256'},
                'invalid prediction descriptor')
        pred, cfg = Path(item['predictions']), Path(item['config'])
        require(not any(p.resolve().is_relative_to(out.resolve()) for p in (pred, cfg)),
                'output overlaps source evidence')
        require(file_sha(pred) == item['prediction_sha256'] and file_sha(cfg) == item['config_sha256'],
                'input SHA mismatch')
        config = read_json(cfg)
        source = Path(config['source_recording'])
        require(not source.resolve().is_relative_to(out.resolve()), 'output overlaps recording')
        require(file_sha(source) == config['source_sha256'], 'recording SHA mismatch')
        require(config['underlying_match_id'] not in matches, 'repeated underlying match')
        matches.add(config['underlying_match_id'])
        stream = convert_predictions(read_json(pred), config, prediction_sha=item['prediction_sha256'],
                                     config_sha=item['config_sha256'])
        observations.extend(stream['observations'])
        bindings.extend(stream['bindings'])
        frames.extend([{'match_id': config['underlying_match_id'], **f} for f in stream['frames']])
        sources.append({'match_id': config['underlying_match_id'], 'frame_count': len(stream['frames']),
                        'prediction_sha256': item['prediction_sha256'], 'config_sha256': item['config_sha256'],
                        'source_sha256': config['source_sha256'],
                        'identical_box_duplicates': stream['identical_box_duplicates']})
        require(file_sha(pred) == item['prediction_sha256'] and file_sha(cfg) == item['config_sha256']
                and file_sha(source) == config['source_sha256'], 'inputs changed during replay')
    engine_start = time.perf_counter()
    result = replay(observations)
    summary = {'schema': 'detector_event_run_v1', 'input_source': 'katacr_prediction',
               'sources': sources, 'observation_count': len(observations), 'candidate_count': len(result['candidates']),
               'event_count': len(result['events']), 'engine_seconds': time.perf_counter() - engine_start,
               'processing_seconds': time.perf_counter() - started,
               'event_gt_used_as_input': False, 'human_identity_used': False,
               'owner_is_unvalidated_prediction': True, 'origin_unavailable': True,
               'onset_proven': False, 'android_or_live_game': False}
    write_artifacts(out, {'detector-visual-stream.json': {'schema': 'detector_visual_stream_v1',
                                                         'observations': observations, 'frames': frames,
                                                         'bindings': bindings, 'sources': sources},
                         'replay.json': result, 'card-play-candidates.json': {'candidates': result['candidates']},
                         'opponent-card-played.json': {'events': result['events']}, 'source-summary.json': summary})
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description='Local detector event baseline; no training or game access')
    parser.add_argument('--sources', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        result = replay_files(read_json(Path(args.sources)), Path(args.output))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, ZeroDivisionError, OverflowError):
        print('Detector evidence rejected; private paths are not disclosed.')
        return 2
