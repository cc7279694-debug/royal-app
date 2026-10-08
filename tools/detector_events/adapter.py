"""KataCR predictions to observations only. No GT or human-identity input."""
from copy import deepcopy
from fractions import Fraction
import math
import re

from tools.event_engine.engine import stable_id, validate_observations


LABELS = {
    'witch': 'visual.unit.witch', 'flying-machine': 'visual.unit.flying_machine',
    'golden-knight': 'visual.unit.golden_knight', 'minion': 'visual.unit.minion',
    'royal-hog': 'visual.unit.royal_hog', 'skeleton': 'visual.unit.skeleton',
    'skeleton-barrel': 'visual.unit.skeleton_barrel', 'mortar': 'visual.structure.mortar',
    'cannon': 'visual.structure.cannon',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def convert_predictions(predictions, config, *, prediction_sha, config_sha):
    require(predictions.get('config_sha256') == config_sha, 'prediction/config SHA mismatch')
    require(all(isinstance(s, str) and re.fullmatch('[a-f0-9]{64}', s)
                for s in (prediction_sha, config_sha)), 'invalid source digest')
    match = config['underlying_match_id']
    width, height = config['source_dimensions_wh']
    require(type(width) is int and type(height) is int and width > 0 and height > 0,
            'invalid source dimensions')
    origin = Fraction(config['source_origin_seconds_exact'])
    frames = predictions.get('frames')
    require(isinstance(frames, list) and frames, 'prediction frames required')
    rows, bindings, metadata, previous, duplicates = [], [], [], -1., 0
    for frame in frames:
        pts = frame['raw_pts']
        require(type(pts) is int, 'exact PTS required')
        base = Fraction(frame['time_base'])
        require(base > 0, 'invalid time base')
        timestamp = frame['timestamp_seconds']
        require(finite(timestamp) and timestamp > previous and timestamp >= 0,
                'frames must be strictly chronological')
        require(abs(timestamp - float(pts * base - origin)) <= 1e-6, 'PTS/time mismatch')
        previous = timestamp
        require(isinstance(frame.get('detections'), list), 'detections array required')
        seen = set()
        for index, prediction in enumerate(frame['detections']):
            label = prediction['class']
            require(isinstance(label, str) and re.fullmatch('[a-z0-9]+(?:[-_][a-z0-9]+)*', label),
                    'invalid raw visual label')
            visual = LABELS.get(label, 'visual.other.' + label.replace('-', '_'))
            owner, channel = prediction.get('owner_prediction'), prediction.get('owner_channel')
            consistent = (type(channel) is int and channel in (0, 1)
                          and owner == ('opponent' if channel == 1 else 'own'))
            if not consistent:
                owner = 'unknown'
            form = prediction.get('form', 'unknown')
            if form not in {'normal', 'evolved', 'unknown'}:
                form = 'unknown'
            # Upstream has no spawn-origin classifier; card/name hints are not provenance.
            bbox = prediction['bbox_xyxy_original']
            require(isinstance(bbox, list) and len(bbox) == 4 and all(finite(v) for v in bbox)
                    and 0 <= bbox[0] < bbox[2] <= width and 0 <= bbox[1] < bbox[3] <= height,
                    'bbox outside source')
            confidence = prediction['confidence']
            require(finite(confidence) and 0 <= confidence <= 1, 'invalid confidence')
            oid = stable_id('det-', [prediction_sha, match, pts, str(base), index])
            key = (visual, owner, tuple(bbox))
            binding = {'observation_id': oid, 'sample_index': frame['sample_index'],
                       'match_id': match, 'timestamp': timestamp,
                       'row_index': index, 'raw_prediction': deepcopy(prediction),
                       'uncertainty': {'owner_is_prediction_not_confirmation': True,
                                       'owner_channel_consistent': consistent,
                                       'origin_unavailable': True}, 'excluded_identical_box': key in seen}
            bindings.append(binding)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            rows.append({'observation_id': oid, 'match_id': match, 'timestamp': timestamp,
                         'visual_class': visual, 'bbox': deepcopy(bbox), 'owner': owner,
                         'form': form, 'origin_kind': 'unknown', 'confidence': confidence,
                         'source': 'katacr_prediction'})
        metadata.append({'timestamp': timestamp, 'raw_pts': pts, 'time_base': str(base),
                         'sample_index': frame['sample_index'], 'prediction_count': len(frame['detections'])})
    validate_observations(rows)
    return {'schema': 'detector_visual_stream_v1', 'observations': rows, 'bindings': bindings,
            'frames': metadata, 'prediction_sha256': prediction_sha, 'config_sha256': config_sha,
            'event_gt_used_as_input': False, 'human_identity_used': False,
            'identical_box_duplicates': duplicates, 'unknown_is_negative': False}
