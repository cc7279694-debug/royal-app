"""Source-bound presentation export of frozen detector candidates; no GT/model input.

Confidence is the maximum source detector confidence, not a probability of a play.
Frames are the first/middle/last distinct actual samples supporting each candidate.
The consumer initializes review decisions separately; this packet contains no GT.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from fractions import Fraction
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import re

import av
from PIL import Image, ImageDraw


SCHEMA = 'offline_assisted_candidates_v1'
MAX_PACKET_BYTES = 24 * 1024 * 1024
MAX_IMAGE_BYTES = 512 * 1024
MAX_EVIDENCE = 128
ROOT_KEYS = {'schema', 'packet_id', 'match_id', 'provenance', 'candidates', 'evidence', 'summary'}
PROVENANCE_KEYS = {'recording_sha256', 'prediction_sha256', 'config_sha256', 'replay_sha256',
                   'engine_rule_version', 'input_source', 'event_gt_used_as_input'}
CANDIDATE_KEYS = {'candidate_id', 'card_id', 'owner', 'timestamp', 'confirmed_at', 'confidence',
                  'evidence_level', 'kind', 'source_observation_ids', 'source_appearance_groups',
                  'evidence_ids', 'reason'}
EVIDENCE_KEYS = {'evidence_id', 'frame_id', 'timestamp', 'raw_pts', 'time_base', 'source_width',
                 'source_height', 'bboxes', 'image_data_url', 'image_sha256'}
SUMMARY_KEYS = {'total_match_candidates', 'exported_candidates', 'excluded_candidates',
                'exclusion_reasons', 'raw_candidate_inventory_sha256', 'evidence_frame_selection',
                'confidence_semantics', 'image_display_semantics', 'coverage_semantics'}
EXCLUSION_KEYS = {'owner_guard', 'unsupported_card', 'insufficient_evidence'}
FRAME_SELECTION = 'first_middle_last_of_candidate_observations'
CONFIDENCE_SEMANTICS = 'maximum source detector confidence; not calibrated event probability'
IMAGE_SEMANTICS = 'native source frame JPEG; source-pixel xyxy boxes; private local evidence'
COVERAGE_SEMANTICS = 'candidate-derived sampled screenshots; not exhaustive full-match event review'


def require(condition, message='invalid assisted evidence'):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read_json(path, maximum=128 * 1024 * 1024):
    path = Path(path)
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= maximum)

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result

    def invalid(_):
        raise ValueError('non-finite JSON')

    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=invalid)


def exact_keys(value, keys):
    require(isinstance(value, dict) and set(value) == keys)


def token(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[a-zA-Z0-9_.:-]{1,200}', value))


def sha_value(value):
    return isinstance(value, str) and bool(re.fullmatch('[a-f0-9]{64}', value))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def unique_strings(values, *, nonempty=True):
    require(isinstance(values, list) and (bool(values) or not nonempty)
            and len(values) <= 100000 and all(token(value) for value in values)
            and len(set(values)) == len(values))


def validate_packet(packet):
    """Strictly validate the interchange format; never accept review decisions."""
    require(len(canonical(packet)) <= MAX_PACKET_BYTES, 'packet too large')
    exact_keys(packet, ROOT_KEYS)
    require(packet['schema'] == SCHEMA and token(packet['packet_id']) and token(packet['match_id']))
    provenance = packet['provenance']
    exact_keys(provenance, PROVENANCE_KEYS)
    require(all(sha_value(provenance[key]) for key in ('recording_sha256', 'prediction_sha256',
                                                       'config_sha256', 'replay_sha256')))
    require(token(provenance['engine_rule_version']) and provenance['input_source'] == 'katacr_prediction'
            and provenance['event_gt_used_as_input'] is False)
    require(isinstance(packet['evidence'], list) and len(packet['evidence']) <= MAX_EVIDENCE)
    evidence_ids, frame_ids = set(), set()
    for item in packet['evidence']:
        exact_keys(item, EVIDENCE_KEYS)
        require(token(item['evidence_id']) and item['evidence_id'] not in evidence_ids
                and token(item['frame_id']) and item['frame_id'] not in frame_ids)
        evidence_ids.add(item['evidence_id']); frame_ids.add(item['frame_id'])
        require(number(item['timestamp']) and item['timestamp'] >= 0 and type(item['raw_pts']) is int)
        require(isinstance(item['time_base'], str)
                and bool(re.fullmatch(r'[1-9][0-9]*/[1-9][0-9]*', item['time_base'])))
        width, height = item['source_width'], item['source_height']
        require(type(width) is int and type(height) is int and 0 < width <= 16384
                and 0 < height <= 16384 and width * height <= 32000000)
        require(isinstance(item['bboxes'], list) and 0 < len(item['bboxes']) <= 256)
        for box in item['bboxes']:
            require(isinstance(box, list) and len(box) == 4 and all(number(v) for v in box)
                    and 0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height)
        url = item['image_data_url']
        prefix = 'data:image/jpeg;base64,'
        require(isinstance(url, str) and url.startswith(prefix) and len(url) <= MAX_IMAGE_BYTES * 4 // 3 + 32)
        data = base64.b64decode(url[len(prefix):], validate=True)
        require(0 < len(data) <= MAX_IMAGE_BYTES and sha_value(item['image_sha256'])
                and digest(data) == item['image_sha256'])
        with Image.open(BytesIO(data)) as image:
            require(image.format == 'JPEG' and image.size == (width, height))
            image.verify()
    require(isinstance(packet['candidates'], list) and len(packet['candidates']) <= 1000)
    candidate_ids, referenced = set(), set()
    for candidate in packet['candidates']:
        exact_keys(candidate, CANDIDATE_KEYS)
        require(token(candidate['candidate_id']) and candidate['candidate_id'] not in candidate_ids)
        candidate_ids.add(candidate['candidate_id'])
        require(candidate['card_id'] is None or token(candidate['card_id']))
        require(candidate['owner'] in {'opponent', 'own', 'unknown'})
        require(number(candidate['timestamp']) and candidate['timestamp'] >= 0)
        require(candidate['confirmed_at'] is None or number(candidate['confirmed_at'])
                and candidate['confirmed_at'] >= candidate['timestamp'])
        require(candidate['confidence'] is None or number(candidate['confidence'])
                and 0 <= candidate['confidence'] <= 1)
        require(candidate['evidence_level'] in {'STRONG', 'MEDIUM', 'WEAK'}
                and candidate['kind'] in {'direct', 'grouped', None}
                and isinstance(candidate['reason'], str) and 0 < len(candidate['reason']) <= 1000)
        unique_strings(candidate['source_observation_ids'])
        unique_strings(candidate['source_appearance_groups'], nonempty=False)
        unique_strings(candidate['evidence_ids'])
        require(len(candidate['evidence_ids']) <= 3 and set(candidate['evidence_ids']) <= evidence_ids)
        referenced.update(candidate['evidence_ids'])
    require(referenced == evidence_ids, 'unbound evidence')
    summary = packet['summary']
    exact_keys(summary, SUMMARY_KEYS)
    exact_keys(summary['exclusion_reasons'], EXCLUSION_KEYS)
    for count in [summary['total_match_candidates'], summary['exported_candidates'], summary['excluded_candidates'],
                  *summary['exclusion_reasons'].values()]:
        require(type(count) is int and count >= 0)
    require(summary['exported_candidates'] == len(packet['candidates'])
            and summary['total_match_candidates'] == summary['exported_candidates'] + summary['excluded_candidates']
            and sum(summary['exclusion_reasons'].values()) == summary['excluded_candidates'])
    require(sha_value(summary['raw_candidate_inventory_sha256'])
            and summary['evidence_frame_selection'] == FRAME_SELECTION
            and summary['confidence_semantics'] == CONFIDENCE_SEMANTICS
            and summary['image_display_semantics'] == IMAGE_SEMANTICS
            and summary['coverage_semantics'] == COVERAGE_SEMANTICS)
    return packet


def _safe_output(output, replay_dir, config, source):
    output = Path(output)
    require(not output.exists(), 'output exists')
    for parent in (output, *output.parents):
        require(not parent.is_symlink() and not parent.is_junction(), 'linked output')
    resolved = output.resolve()
    require(not resolved.is_relative_to(replay_dir.resolve())
            and not replay_dir.resolve().is_relative_to(resolved), 'output overlaps replay')
    require(not any(path.resolve().is_relative_to(resolved) for path in (config, source)), 'output overlaps source')
    return output


def _load_frozen(replay_dir, config_path, source, match):
    replay_dir, config_path, source = Path(replay_dir), Path(config_path), Path(source)
    require(token(match) and source.suffix.lower() == '.mp4' and source.is_file())
    for path in (replay_dir, config_path, source):
        require(not any(parent.is_symlink() or parent.is_junction() for parent in (path, *path.parents)))
    manifest = read_json(replay_dir / 'manifest.json', 1024 * 1024)
    exact_keys(manifest, {'schema', 'files'})
    require(manifest.get('schema') == 'oracle_artifact_manifest_v1' and isinstance(manifest.get('files'), dict))
    require({'replay.json', 'detector-visual-stream.json', 'source-summary.json',
             'card-play-candidates.json', 'opponent-card-played.json'} == set(manifest['files']))
    hashes = {}
    for name, expected in manifest['files'].items():
        require(isinstance(name, str) and re.fullmatch('[a-z0-9-]+[.]json', name)
                and name != 'manifest.json' and sha_value(expected))
        path = replay_dir / name
        require(path.is_file() and not path.is_symlink() and file_sha(path) == expected, 'frozen hash mismatch')
        hashes[path] = expected
    hashes[replay_dir / 'manifest.json'] = file_sha(replay_dir / 'manifest.json')
    replay = read_json(replay_dir / 'replay.json')
    stream = read_json(replay_dir / 'detector-visual-stream.json')
    summary = read_json(replay_dir / 'source-summary.json', 1024 * 1024)
    config = read_json(config_path, 1024 * 1024)
    require(summary.get('input_source') == 'katacr_prediction'
            and summary.get('event_gt_used_as_input') is False and summary.get('human_identity_used') is False)
    require(stream.get('schema') == 'detector_visual_stream_v1'
            and replay.get('schema') == 'oracle_event_replay_v1'
            and token(replay.get('rule_version')))
    sources = [row for row in summary['sources'] if row['match_id'] == match]
    require(len(sources) == 1 and sources[0] in stream['sources'], 'source binding missing')
    provenance = sources[0]
    require(config['underlying_match_id'] == match and config['source_sha256'] == provenance['source_sha256']
            and file_sha(config_path) == provenance['config_sha256']
            and file_sha(source) == provenance['source_sha256'], 'source binding changed')
    predictions_path = config_path.parent / 'predictions.json'
    require(predictions_path.is_file() and not predictions_path.is_symlink()
            and file_sha(predictions_path) == provenance['prediction_sha256'], 'prediction source changed')
    hashes[config_path] = provenance['config_sha256']; hashes[source] = provenance['source_sha256']
    hashes[predictions_path] = provenance['prediction_sha256']
    require(read_json(replay_dir / 'card-play-candidates.json')['candidates'] == replay['candidates'])
    require(read_json(replay_dir / 'opponent-card-played.json')['events'] == replay['events'])
    require(summary['observation_count'] == len(stream['observations'])
            and summary['candidate_count'] == len(replay['candidates'])
            and summary['event_count'] == len(replay['events']))
    return replay, stream, config, provenance, hashes


def _join_evidence(replay, stream, config, match):
    observations = {row['observation_id']: row for row in stream['observations']}
    bindings = {row['observation_id']: row for row in stream['bindings']}
    require(len(observations) == len(stream['observations']) and len(bindings) == len(stream['bindings']))
    frames = {(row['match_id'], row['sample_index']): row for row in stream['frames']}
    require(len(frames) == len(stream['frames']))
    origin = Fraction(config['source_origin_seconds_exact'])
    match_frames = sorted((row for row in stream['frames'] if row['match_id'] == match), key=lambda row: row['timestamp'])
    require(match_frames and len(match_frames) == next(row['frame_count'] for row in stream['sources'] if row['match_id'] == match))
    previous = -1.
    for frame in match_frames:
        require(type(frame['raw_pts']) is int and Fraction(frame['time_base']) > 0
                and number(frame['timestamp']) and frame['timestamp'] > previous
                and abs(float(frame['raw_pts'] * Fraction(frame['time_base']) - origin) - frame['timestamp']) <= 1e-6)
        previous = frame['timestamp']
    inventory = [row for row in replay['candidates'] if row['match_id'] == match]
    require(len({row['candidate_id'] for row in inventory}) == len(inventory))
    excluded = Counter({key: 0 for key in EXCLUSION_KEYS})
    selected, requests = [], {}
    width, height = config['source_dimensions_wh']
    require(type(width) is int and type(height) is int and 0 < width <= 16384
            and 0 < height <= 16384 and width * height <= 32000000)
    for candidate in inventory:
        reason = ('owner_guard' if candidate['owner'] != 'opponent' else
                  'unsupported_card' if candidate['card_id'] is None else
                  'insufficient_evidence' if candidate['evidence_level'] not in {'STRONG', 'MEDIUM'} else None)
        if reason:
            excluded[reason] += 1
            continue
        unique_strings(candidate['source_observation_ids'])
        rows, supported_frames = [], {}
        for oid in candidate['source_observation_ids']:
            require(oid in observations and oid in bindings, 'candidate observation missing')
            observation, binding = observations[oid], bindings[oid]
            require(observation['match_id'] == match and observation['source'] == 'katacr_prediction'
                    and not observation.get('appearance_group_id') and observation['owner'] == candidate['owner']
                    and observation['origin_kind'] == 'unknown' and binding['match_id'] == match
                    and binding['excluded_identical_box'] is False and binding['timestamp'] == observation['timestamp'])
            require(replay['registry'].get(observation['visual_class'], {}).get('card_id') == candidate['card_id'])
            raw = binding['raw_prediction']
            require(raw['bbox_xyxy_original'] == observation['bbox'] and raw['confidence'] == observation['confidence']
                    and raw['owner_prediction'] == observation['owner'] and raw['owner_channel'] == 1)
            frame = frames.get((match, binding['sample_index']))
            require(frame is not None and frame['timestamp'] == observation['timestamp'])
            box = observation['bbox']
            require(isinstance(box, list) and len(box) == 4 and all(number(v) for v in box)
                    and 0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height)
            require(number(observation['confidence']) and 0 <= observation['confidence'] <= 1)
            key = (frame['raw_pts'], str(Fraction(frame['time_base'])))
            supported_frames[key] = frame
            rows.append(observation)
        require(candidate['timestamp'] == min(row['timestamp'] for row in rows))
        require(candidate['confirmed_at'] is None or candidate['confirmed_at'] in {row['timestamp'] for row in rows})
        ordered = sorted(supported_frames, key=lambda key: (supported_frames[key]['timestamp'], key))
        chosen = list(dict.fromkeys([ordered[0], ordered[len(ordered) // 2], ordered[-1]]))
        for key in chosen:
            request = requests.setdefault(key, {'frame': supported_frames[key], 'bboxes': set()})
            for row in rows:
                if row['timestamp'] == supported_frames[key]['timestamp']:
                    request['bboxes'].add(tuple(row['bbox']))
        selected.append((candidate, rows, chosen))
    require(len(requests) <= MAX_EVIDENCE)
    return inventory, selected, requests, dict(excluded)


def _decode(source, config, match, requests):
    images, metadata = {}, {}
    origin, previous = None, None
    with av.open(str(source), 'r') as container:
        require(len(container.streams.video) == 1, 'ambiguous source stream')
        for frame in container.decode(video=0):
            require(frame.pts is not None and frame.time_base is not None)
            raw_time = frame.pts * frame.time_base
            require(previous is None or raw_time > previous, 'non-increasing source PTS')
            previous = raw_time
            if origin is None:
                origin = raw_time
                require(origin == Fraction(config['source_origin_seconds_exact']))
            require([frame.width, frame.height] == config['source_dimensions_wh'])
            key = (frame.pts, str(Fraction(frame.time_base)))
            if key not in requests:
                continue
            require(key not in images and abs(float(raw_time - origin) - requests[key]['frame']['timestamp']) <= 1e-6)
            image = frame.to_image().convert('RGB')
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=80, optimize=False, progressive=False)
            data = buffer.getvalue()
            require(len(data) <= MAX_IMAGE_BYTES, 'native JPEG exceeds image limit')
            frame_id = 'frame-' + digest(canonical([config['source_sha256'], match, key]))[:24]
            eid = 'evidence-' + digest(canonical([frame_id]))[:24]
            metadata[key] = {'evidence_id': eid, 'frame_id': frame_id,
                             'timestamp': requests[key]['frame']['timestamp'], 'raw_pts': key[0], 'time_base': key[1],
                             'source_width': frame.width, 'source_height': frame.height,
                             'bboxes': [list(box) for box in sorted(requests[key]['bboxes'])],
                             'image_data_url': 'data:image/jpeg;base64,' + base64.b64encode(data).decode('ascii'),
                             'image_sha256': digest(data)}
            images[eid] = data
    require(origin is not None and len(metadata) == len(requests), 'selected exact source PTS missing')
    return metadata, images


def _contact_sheet(packet, images):
    """Private presentation only; candidate labels stay hypotheses."""
    columns, width, header = 4, 240, 52
    height = max((round(row['source_height'] * width / row['source_width']) for row in packet['evidence']), default=100)
    rows = max(1, math.ceil(len(packet['evidence']) / columns))
    canvas = Image.new('RGB', (columns * width, rows * (height + header)), '#20202a')
    painter = ImageDraw.Draw(canvas)
    for index, item in enumerate(packet['evidence']):
        x, y = index % columns * width, index // columns * (height + header)
        with Image.open(BytesIO(images[item['evidence_id']])) as image:
            image.thumbnail((width, height))
            canvas.paste(image, (x, y + header))
        painter.text((x + 5, y + 3), f"{item['timestamp']:.3f}s | MODEL OBSERVATION", fill='white')
        painter.text((x + 5, y + 20), item['frame_id'][-12:], fill='#ffe080')
        painter.text((x + 5, y + 35), 'Source sample; pending review', fill='#c9c9d0')
    buffer = BytesIO()
    canvas.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def export_packet(replay_dir, config_path, source, match, output):
    replay_dir, config_path, source = Path(replay_dir), Path(config_path), Path(source)
    output = _safe_output(output, replay_dir, config_path, source)
    replay, stream, config, source_binding, hashes = _load_frozen(replay_dir, config_path, source, match)
    inventory, selected, requests, excluded = _join_evidence(replay, stream, config, match)
    metadata, images = _decode(source, config, match, requests)
    candidates = []
    for candidate, rows, chosen in selected:
        candidates.append({key: candidate[key] for key in ('candidate_id', 'card_id', 'owner', 'timestamp',
                           'confirmed_at', 'evidence_level', 'kind', 'source_observation_ids',
                           'source_appearance_groups', 'reason')} |
                          {'confidence': max(row['confidence'] for row in rows),
                           'evidence_ids': [metadata[key]['evidence_id'] for key in chosen]})
    packet = {'schema': SCHEMA, 'packet_id': '', 'match_id': match,
              'provenance': {'recording_sha256': source_binding['source_sha256'],
                             'prediction_sha256': source_binding['prediction_sha256'],
                             'config_sha256': source_binding['config_sha256'],
                             'replay_sha256': hashes[replay_dir / 'replay.json'],
                             'engine_rule_version': replay['rule_version'], 'input_source': 'katacr_prediction',
                             'event_gt_used_as_input': False},
              'candidates': candidates,
              'evidence': sorted(metadata.values(), key=lambda row: (row['timestamp'], row['evidence_id'])),
              'summary': {'total_match_candidates': len(inventory), 'exported_candidates': len(candidates),
                          'excluded_candidates': len(inventory) - len(candidates), 'exclusion_reasons': excluded,
                          'raw_candidate_inventory_sha256': digest(canonical(inventory)),
                          'evidence_frame_selection': FRAME_SELECTION, 'confidence_semantics': CONFIDENCE_SEMANTICS,
                          'image_display_semantics': IMAGE_SEMANTICS, 'coverage_semantics': COVERAGE_SEMANTICS}}
    packet['packet_id'] = 'packet-' + digest(canonical(packet))[:24]
    validate_packet(packet)
    encoded = canonical(packet) + b'\n'
    require(len(encoded) <= MAX_PACKET_BYTES)
    sheet = _contact_sheet(packet, images)
    require(all(file_sha(path) == expected for path, expected in hashes.items()), 'input changed during export')
    # Inputs are validated before the new directory exists. Never overwrite any material.
    output.mkdir(parents=True, exist_ok=False)
    (output / 'evidence').mkdir()
    files = {'candidates.json': encoded, 'contact-sheet.jpg': sheet,
             **{f'evidence/{eid}.jpg': data for eid, data in images.items()}}
    for name, data in files.items():
        with (output / name).open('xb') as handle:
            handle.write(data)
    manifest = {'schema': 'offline_assisted_export_manifest_v1', 'packet_id': packet['packet_id'],
                'provenance': packet['provenance'], 'files': {name: digest(data) for name, data in files.items()},
                'sources_unchanged': True, 'new_inference': False, 'training': False, 'event_gt_read': False}
    with (output / 'manifest.json').open('xb') as handle:
        handle.write(canonical(manifest) + b'\n')
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description='Private frozen detector candidate export; no GT or inference')
    for name in ('replay', 'config', 'source', 'match', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args(argv)
    try:
        packet = export_packet(args.replay, args.config, args.source, args.match, args.output)
        print(json.dumps({'schema': SCHEMA, 'packet_id': packet['packet_id'],
                          'candidates': len(packet['candidates']), 'evidence': len(packet['evidence']),
                          'new_inference': False, 'event_gt_read': False}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError, ZeroDivisionError, av.FFmpegError):
        print('Assisted evidence rejected; private paths are not disclosed.')
        return 2
