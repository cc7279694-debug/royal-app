from copy import deepcopy
from fractions import Fraction as F
import json

import pytest

from clash_tracker_video.evidence_contract import EvidenceError, load_evidence, validate_evidence, interval_contains
from evidence_fixtures import synthetic_evidence, synthetic_indexes


def test_valid_and_non_mutating():
    doc = synthetic_evidence()
    original = deepcopy(doc)
    assert validate_evidence(doc, synthetic_indexes(doc)) == []
    assert doc == original
    del doc['schema_version']
    assert validate_evidence(doc, synthetic_indexes(doc)) == []


def test_terminal_negative_only():
    assert not interval_contains(F(1), F(0), F(1), last_frame=F(1))
    assert interval_contains(F(1), F(0), F(1), last_frame=F(1), terminal_negative=True)
    assert not interval_contains(F(1, 2), F(0), F(1, 2), last_frame=F(1), terminal_negative=True)
    assert not interval_contains(F('0.999999999999'), F(0), F('0.999999999999'), last_frame=F(1), terminal_negative=True)


@pytest.mark.parametrize('text', ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '[]', '{broken'])
def test_strict_json(tmp_path, text):
    path = tmp_path / 'bad.json'
    path.write_text(text)
    with pytest.raises(EvidenceError):
        load_evidence(path)


def test_json_limit(tmp_path):
    path = tmp_path / 'large.json'
    path.write_bytes(b' ' * (16 * 1024 * 1024 + 1))
    with pytest.raises(EvidenceError):
        load_evidence(path)


@pytest.mark.parametrize('field', ['recordings', 'match_segments', 'target_card', 'occurrences', 'frame_annotations', 'negative_intervals'])
def test_required_root(field):
    doc = synthetic_evidence()
    del doc[field]
    assert validate_evidence(doc, {})


@pytest.mark.parametrize('field', ['evaluation_frames', 'evaluation_protocol', 'split_manifest', 'test_locked', 'freeze', 'other'])
def test_deferred_or_unknown(field):
    doc = synthetic_evidence()
    doc[field] = {}
    assert validate_evidence(doc, synthetic_indexes(doc))


@pytest.mark.parametrize('entity,field,value', [
    ('recordings','width',True), ('recordings','source_sha256','bad'),
    ('recordings','last_frame_seconds',float('nan')), ('recordings','origin_pts',True),
    ('match_segments','capture_complete',1), ('match_segments','perspective','bad'),
    ('occurrences','match_segment_id','missing'), ('occurrences','owner','own'),
    ('occurrences','last_absent_seconds',4), ('occurrences','notes',''),
    ('frame_annotations','raw_pts',6001), ('frame_annotations','image_width',48),
    ('frame_annotations','image_path','../escape.png'), ('frame_annotations','play_id','missing'),
    ('frame_annotations','timestamp_seconds',1.01), ('frame_annotations','review_status','bad'),
    ('negative_intervals','start_seconds',1), ('negative_intervals','non_match',1),
])
def test_invalid_fields(entity, field, value):
    doc = synthetic_evidence()
    indexes = synthetic_indexes(doc)
    doc[entity][0][field] = value
    assert validate_evidence(doc, indexes)


def test_nonzero_vfr_and_rotation():
    doc = synthetic_evidence(1)
    doc['recordings'][0].update(rotation_degrees=90, orientation='portrait')
    for a, t, pts in zip(doc['frame_annotations'], [1, 1.07, 1.21], [6000,6070,6210]):
        a.update(timestamp_seconds=t, raw_pts=pts, image_width=48, image_height=64)
    indexes = synthetic_indexes(doc)
    assert validate_evidence(doc, indexes) == []
    doc['frame_annotations'][2]['timestamp_seconds'] = 1.2
    assert validate_evidence(doc, indexes)


def test_repeated_real_time_and_too_many_boxes():
    doc = synthetic_evidence(1)
    doc['frame_annotations'][2].update({k:v for k,v in doc['frame_annotations'][1].items()
                                      if k not in ('annotation_id',)})
    assert validate_evidence(doc, synthetic_indexes(doc))
    doc = synthetic_evidence(1)
    for i in range(3,6):
        a = deepcopy(doc['frame_annotations'][0])
        a.update(annotation_id=f'extra{i}', frame_id=f'extra{i}', raw_pts=6000+i*100, timestamp_seconds=1+i*.1)
        doc['frame_annotations'].append(a)
        doc['occurrences'][0]['evidence_annotation_ids'].append(a['annotation_id'])
    assert validate_evidence(doc, synthetic_indexes(doc))


def test_ambiguous_visibility_cannot_be_negative():
    doc = synthetic_evidence(1)
    doc['occurrences'][0]['manual_verification_status'] = 'ambiguous'
    doc['negative_intervals'][0]['end_seconds'] = 1.5
    assert validate_evidence(doc, synthetic_indexes(doc))


def test_bbox_overflow_and_unknown_nested_key():
    doc = synthetic_evidence()
    doc['frame_annotations'][0]['normalized_bbox'].update(x=.9, width=.2)
    assert validate_evidence(doc, synthetic_indexes(doc))


def test_overflow_number_rejected_without_crash():
    doc = synthetic_evidence()
    doc['recordings'][0]['last_frame_seconds'] = 10 ** 400
    assert validate_evidence(doc,synthetic_indexes(doc))


def test_unhashable_report_status_rejected_without_crash():
    doc = synthetic_evidence()
    doc['preparation_report'] = dict(status=[],candidate_gate=False,experiment_gate=False,
        counts=dict(recordings=0,reviewed_complete_segments=0,verified_plays=0,annotated_key_frames=0),reasons=[],coverage_gaps=[])
    assert validate_evidence(doc,synthetic_indexes(doc))


def test_json_overflow_constant_rejected(tmp_path):
    path = tmp_path/'bad.json'
    path.write_text('{"seconds":1e999}')
    with pytest.raises(EvidenceError): load_evidence(path)
    doc = synthetic_evidence()
    doc['recordings'][0]['unknown'] = 1
    assert validate_evidence(doc, synthetic_indexes(doc))
