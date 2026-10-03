"""Strict local evidence v1; observations never become runtime game events."""
from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from pathlib import Path, PureWindowsPath
from collections.abc import Mapping


class EvidenceError(Exception):
    """A path-free evidence diagnostic."""


def load_evidence(path: Path) -> dict[str, object]:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise EvidenceError("Duplicate JSON key.")
            result[key] = value
        return result

    def constant(_):
        raise EvidenceError("Non-finite JSON constant.")

    try:
        with Path(path).open('rb') as handle:
            content = handle.read(16 * 1024 * 1024 + 1)
        if len(content) > 16 * 1024 * 1024:
            raise EvidenceError("JSON exceeds 16MiB.")
        doc = json.loads(content.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
        if not isinstance(doc, dict):
            raise EvidenceError("JSON root must be an object.")
        return doc
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise EvidenceError("Cannot read strict evidence JSON.") from exc


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def rational(value):
    if not isinstance(value, dict) or set(value) != {'numerator', 'denominator'}:
        raise EvidenceError('Invalid rational time_base.')
    if any(type(v) is not int or v <= 0 for v in value.values()):
        raise EvidenceError('Invalid rational time_base.')
    return Fraction(value['numerator'], value['denominator'])


def seconds(value):
    if not number(value) or value < 0:
        raise EvidenceError('Invalid seconds.')
    return Fraction(str(value))


def interval_contains(t: Fraction, start: Fraction, end: Fraction, *,
                      last_frame: Fraction, terminal_negative: bool = False) -> bool:
    return start <= t and (t < end or (terminal_negative is True and end == last_frame and t == end))


def relative_png(value):
    return (isinstance(value, str) and bool(value) and '\\' not in value and ':' not in value
            and not value.startswith('/') and not PureWindowsPath(value).drive
            and all(p not in ('', '.', '..') for p in value.split('/'))
            and value.lower().endswith('.png'))


STATUS = {'draft', 'verified', 'ambiguous', 'rejected'}
PERSPECTIVE = {'own_bottom', 'opponent_bottom', 'unknown'}
SCHEMAS = {
    'recordings': dict(recording_id='id', source_sha256='hash', width='positive_int', height='positive_int',
                       duration_seconds='duration', time_base='rational', origin_pts='int',
                       origin_time_base='rational', last_frame_seconds='seconds',
                       rotation_degrees={0,90,180,270}, orientation={'portrait','landscape','square'},
                       perspective=PERSPECTIVE),
    'match_segments': dict(segment_id='id', recording_id='id', start_seconds='seconds', end_seconds='seconds',
                           perspective=PERSPECTIVE, validation_status=STATUS, capture_complete='bool',
                           boundary_uncertainty_seconds='seconds', notes='text'),
    'target_card': dict(card_id='id', display_name='id', selection_reason='id', ambiguity_notes='text',
                        variant={'normal','known_evolution','unknown'}),
    'occurrences': dict(play_id='id', recording_id='id', card_id='id', owner={'opponent'},
                        last_absent_seconds='seconds', deployment_lower_seconds='seconds',
                        deployment_time_seconds='seconds', deployment_upper_seconds='seconds',
                        visible_start_seconds='seconds', visible_end_seconds='seconds', match_segment_id='id',
                        manual_verification_status=STATUS, evidence_annotation_ids='ids', notes='text'),
    'frame_annotations': dict(annotation_id='id', frame_id='id', recording_id='id', play_id='id',
                              timestamp_seconds='seconds', raw_pts='int', time_base='rational',
                              image_path='png', image_width='positive_int', image_height='positive_int',
                              normalized_bbox='box', annotation_source={'manual'}, review_status=STATUS),
    'negative_intervals': dict(negative_id='id', recording_id='id', start_seconds='seconds', end_seconds='seconds',
                               reason={'target_absent','menu','loading','selection','result','system_ui','transition'},
                               match_segment_id='nullable_id', non_match='bool', review_status=STATUS),
}


def valid_type(value, kind):
    if isinstance(kind, set):
        return type(value) in (str, int) and value in kind
    if kind == 'id': return isinstance(value, str) and bool(value.strip())
    if kind == 'text': return isinstance(value, str)
    if kind == 'int': return type(value) is int
    if kind == 'positive_int': return type(value) is int and value > 0
    if kind == 'bool': return type(value) is bool
    if kind == 'nullable_id': return value is None or valid_type(value, 'id')
    if kind == 'ids': return isinstance(value, list) and all(valid_type(v, 'id') for v in value) and len(set(value)) == len(value)
    if kind == 'hash': return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None
    if kind == 'seconds': return number(value) and value >= 0
    if kind == 'duration': return value is None or (number(value) and value > 0)
    if kind == 'png': return relative_png(value)
    if kind == 'rational':
        try: rational(value); return True
        except EvidenceError: return False
    if kind == 'box':
        return (isinstance(value, dict) and set(value) == {'x','y','width','height'}
                and all(number(v) for v in value.values())
                and 0 <= value['x'] <= 1 and 0 <= value['y'] <= 1
                and 0 < value['width'] <= 1 and 0 < value['height'] <= 1
                and Fraction(str(value['x'])) + Fraction(str(value['width'])) <= 1
                and Fraction(str(value['y'])) + Fraction(str(value['height'])) <= 1)
    return False


def validate_evidence(doc: Mapping[str, object], indexes: Mapping[str, Mapping[str, object]]) -> list[str]:
    """Validate metadata without mutation; disk/image integrity belongs to index loading."""
    errors = []
    required = set(SCHEMAS)
    if not isinstance(doc, Mapping) or not required <= set(doc) or set(doc) - required - {'schema_version','preparation_report'}:
        return ['root: missing or unknown fields']
    if 'schema_version' in doc and (type(doc['schema_version']) is not int or doc['schema_version'] != 1):
        errors.append('schema_version: expected 1')
    entities = {}
    for name, schema in SCHEMAS.items():
        values = ([doc[name]] if doc[name] is not None else []) if name == 'target_card' else doc[name]
        if not isinstance(values, list):
            errors.append(f'{name}: expected array'); continue
        entities[name] = values
        seen = set()
        for i, item in enumerate(values):
            prefix = f'{name}[{i}]'
            if not isinstance(item, dict) or set(item) != set(schema):
                errors.append(f'{prefix}: missing or unknown fields'); continue
            for field, kind in schema.items():
                if not valid_type(item[field], kind):
                    errors.append(f'{prefix}.{field}: invalid type/value')
            identity = next(iter(schema))
            if isinstance(item[identity], str):
                if item[identity] in seen: errors.append(f'{prefix}.{identity}: duplicate')
                seen.add(item[identity])
    if 'preparation_report' in doc:
        report = doc['preparation_report']
        if (not isinstance(report, dict) or set(report) != {'status','candidate_gate','experiment_gate','counts','reasons','coverage_gaps'}
                or report.get('status') not in {'invalid','insufficient'}
                or type(report.get('candidate_gate')) is not bool or type(report.get('experiment_gate')) is not bool
                or not isinstance(report.get('counts'), dict)
                or set(report.get('counts', {})) != {'recordings','reviewed_complete_segments','verified_plays','annotated_key_frames'}
                or any(type(v) is not int or v < 0 for v in report.get('counts', {}).values())
                or not isinstance(report.get('reasons'), list) or not all(isinstance(v,str) for v in report.get('reasons', []))
                or not isinstance(report.get('coverage_gaps'), list)):
            errors.append('preparation_report: invalid advisory report')
    if errors: return errors
    recordings = {r['recording_id']:r for r in entities['recordings']}
    segments = {s['segment_id']:s for s in entities['match_segments']}
    plays = {p['play_id']:p for p in entities['occurrences']}
    annotations = {a['annotation_id']:a for a in entities['frame_annotations']}
    frames = {}
    for rid, r in recordings.items():
        index = indexes.get(rid)
        indexed_recording = index.get('recording') if isinstance(index, Mapping) else None
        compatible = (isinstance(indexed_recording,dict) and set(indexed_recording)==set(r)
                      and all(indexed_recording[k]==v for k,v in r.items() if k!='perspective')
                      and indexed_recording['perspective'] in ('unknown',r['perspective']))
        if not compatible or not isinstance(index.get('frames'),list):
            errors.append('recordings: missing/conflicting index'); continue
        frames[rid] = {}
        for f in index['frames']:
            if not isinstance(f, dict) or f.get('status') != 'success': continue
            fid = f.get('frame_id')
            if not isinstance(fid, str): errors.append('indexes: missing frame_id'); continue
            if fid in frames[rid] and frames[rid][fid] != f:
                errors.append('indexes: conflicting frame_id')
            frames[rid][fid] = f
        w,h = (r['height'],r['width']) if r['rotation_degrees'] in (90,270) else (r['width'],r['height'])
        expected = 'portrait' if h>w else 'landscape' if w>h else 'square'
        if r['orientation'] != expected: errors.append('recordings.orientation: inconsistent dimensions')
    for name in ('match_segments','occurrences','frame_annotations','negative_intervals'):
        for item in entities[name]:
            if item['recording_id'] not in recordings: errors.append(f'{name}.recording_id: dangling')
    if errors: return errors
    for s in segments.values():
        r = recordings[s['recording_id']]
        if not 0 <= seconds(s['start_seconds']) < seconds(s['end_seconds']) <= seconds(r['last_frame_seconds']):
            errors.append('match_segments: interval out of bounds')
        if s['perspective'] != r['perspective']: errors.append('match_segments.perspective: conflict')
    for p in plays.values():
        s = segments.get(p['match_segment_id'])
        if s is None or s['recording_id'] != p['recording_id']:
            errors.append('occurrences.match_segment_id: dangling/conflicting'); continue
        target = doc['target_card']
        if target is None or p['card_id'] != target['card_id']: errors.append('occurrences.card_id: target mismatch')
        ordered = [s['start_seconds'],p['last_absent_seconds'],p['deployment_lower_seconds'],p['deployment_time_seconds'],
                   p['deployment_upper_seconds'],p['visible_start_seconds'],p['visible_end_seconds'],s['end_seconds']]
        if any(seconds(a)>seconds(b) for a,b in zip(ordered,ordered[1:])) or p['visible_start_seconds'] >= p['visible_end_seconds']:
            errors.append('occurrences: invalid onset/visible bounds')
        evidence = [annotations.get(aid) for aid in p['evidence_annotation_ids']]
        if any(a is None or a['play_id'] != p['play_id'] for a in evidence):
            errors.append('occurrences.evidence_annotation_ids: dangling/conflicting'); continue
        if p['manual_verification_status'] == 'verified':
            verified = [a for a in evidence if a['review_status'] == 'verified']
            times = {a['raw_pts'] * rational(a['time_base']) for a in verified}
            if not 3 <= len(verified) <= 5 or len(times) != len(verified):
                errors.append('occurrences: verified play needs 3–5 distinct timestamps')
            if not p['notes'].strip(): errors.append('occurrences.notes: missing manual narrative')
            if target is None or target['variant'] == 'unknown' or s['perspective'] == 'unknown' or s['validation_status'] != 'verified':
                errors.append('occurrences: unresolved verified identity/perspective')
    for a in annotations.values():
        p = plays.get(a['play_id'])
        r = recordings[a['recording_id']]
        f = frames.get(a['recording_id'],{}).get(a['frame_id'])
        if p is None or p['recording_id'] != a['recording_id']:
            errors.append('frame_annotations.play_id: dangling/conflicting'); continue
        if a['annotation_id'] not in p['evidence_annotation_ids']: errors.append('frame_annotations: unreferenced box')
        if (f is None or any(a[k] != f.get(k) for k in ('raw_pts','time_base','image_width','image_height','timestamp_seconds'))
                or a['image_path'] not in f.get('_aliases',[f.get('image_path')])):
            errors.append('frame_annotations.frame_id: missing/conflicting export')
        actual = a['raw_pts'] * rational(a['time_base']) - r['origin_pts'] * rational(r['origin_time_base'])
        if abs(actual-seconds(a['timestamp_seconds'])) > Fraction(1,1000000): errors.append('frame_annotations.timestamp_seconds: PTS mismatch')
        w,h = (r['height'],r['width']) if r['rotation_degrees'] in (90,270) else (r['width'],r['height'])
        if (a['image_width'],a['image_height']) != (w,h): errors.append('frame_annotations: displayed dimensions mismatch')
        if not interval_contains(actual, seconds(p['visible_start_seconds']),seconds(p['visible_end_seconds']),last_frame=seconds(r['last_frame_seconds'])):
            errors.append('frame_annotations: timestamp outside visible interval')
    for n in entities['negative_intervals']:
        r = recordings[n['recording_id']]
        start,end = seconds(n['start_seconds']),seconds(n['end_seconds'])
        if not 0 <= start < end <= seconds(r['last_frame_seconds']): errors.append('negative_intervals: invalid bounds')
        if n['non_match']:
            if n['match_segment_id'] is not None or n['reason']=='target_absent': errors.append('negative_intervals: non-match requires non-match reason/null segment')
            for s in segments.values():
                if s['recording_id']==n['recording_id'] and start<seconds(s['end_seconds']) and seconds(s['start_seconds'])<end:
                    errors.append('negative_intervals: non-match overlaps match')
        else:
            s = segments.get(n['match_segment_id'])
            if (s is None or s['recording_id'] != n['recording_id'] or n['reason'] != 'target_absent'
                    or not seconds(s['start_seconds']) <= start < end <= seconds(s['end_seconds'])):
                errors.append('negative_intervals: segment/reason mismatch')
        for p in plays.values():
            if p['recording_id']==n['recording_id'] and p['manual_verification_status'] != 'rejected' and start<seconds(p['visible_end_seconds']) and seconds(p['visible_start_seconds'])<end:
                errors.append('negative_intervals: overlaps possible target visibility')
    return errors
