from copy import deepcopy
import pytest

from clash_tracker_video.evidence_contract import EvidenceError, validate_evidence
from clash_tracker_video.evidence_review import normalize_box, make_frame_annotation, review_evidence
from evidence_fixtures import synthetic_evidence, synthetic_indexes


def test_full_box_and_manual_draft():
    assert normalize_box((10,20,30,40),(100,200)) == dict(x=.1,y=.1,width=.3,height=.2)
    doc = synthetic_evidence(1)
    entry = synthetic_indexes(doc)['synthetic']['frames'][0]
    annotation = make_frame_annotation(entry,annotation_id='a',recording_id='synthetic',play_id='play0',rect=(1,2,3,4))
    assert annotation['review_status'] == 'draft'
    assert annotation['raw_pts'] == 6000
    assert annotation['annotation_source'] == 'manual'


@pytest.mark.parametrize('rect', [(-1,0,1,1),(0,0,0,1),(0,0,1,-1),(0,0,101,1),
    (False,0,1,1),(0,0,float('nan'),1),(0,0,float('inf'),1),(99,0,2,1)])
def test_bad_box(rect):
    with pytest.raises(EvidenceError): normalize_box(rect,(100,200))


@pytest.mark.parametrize('field,value', [('status','miss'),('raw_pts',None),('time_base',None),('image_width',None),('frame_id',None)])
def test_bad_export(field,value):
    entry = synthetic_indexes(synthetic_evidence(1))['synthetic']['frames'][0]
    entry[field] = value
    with pytest.raises(EvidenceError): make_frame_annotation(entry,annotation_id='a',recording_id='synthetic',play_id='play0',rect=(1,2,3,4))


@pytest.mark.parametrize('plays,candidate', [(4,True),(3,False),(1,False),(0,False)])
def test_counts_and_single_recording_insufficient(plays,candidate):
    doc = synthetic_evidence(plays)
    original = deepcopy(doc)
    report = review_evidence(doc,synthetic_indexes(doc))
    assert report['status'] == 'insufficient'
    assert report['candidate_gate'] is candidate
    assert report['experiment_gate'] is False
    assert report['counts']['verified_plays'] == plays
    assert report['counts']['annotated_key_frames'] == plays*3
    assert report['coverage_gaps'] == []
    assert doc == original


def test_unknown_gap_not_negative_and_terminal_endpoint():
    doc = synthetic_evidence(1)
    del doc['negative_intervals'][0]
    report = review_evidence(doc,synthetic_indexes(doc))
    assert report['coverage_gaps'] == [dict(recording_id='synthetic',match_segment_id='match',start_seconds=0.0,end_seconds=1.0)]
    # Full terminal negative includes the last frame; removing it leaves a real gap.
    doc = synthetic_evidence(1)
    doc['negative_intervals'].pop()
    assert review_evidence(doc,synthetic_indexes(doc))['coverage_gaps'] == [dict(
        recording_id='synthetic',match_segment_id=None,start_seconds=19.0,end_seconds=20.0)]


def test_ambiguous_not_candidate_or_reviewed_positive():
    doc = synthetic_evidence()
    doc['target_card']['variant'] = 'unknown'
    for p in doc['occurrences']: p['manual_verification_status'] = 'ambiguous'
    report = review_evidence(doc,synthetic_indexes(doc))
    assert report['candidate_gate'] is False
    assert report['counts']['verified_plays'] == 0
    assert len(report['coverage_gaps']) == 4


def test_stale_report_is_advisory():
    doc = synthetic_evidence()
    doc['preparation_report'] = dict(status='insufficient',candidate_gate=False,experiment_gate=True,
        counts=dict(recordings=100,reviewed_complete_segments=100,verified_plays=100,annotated_key_frames=100),reasons=[],coverage_gaps=[])
    report = review_evidence(doc,synthetic_indexes(doc))
    assert report['experiment_gate'] is False
    assert report['candidate_gate'] is True
    assert report['counts']['recordings'] == 1


def test_unboxed_time_within_reviewed_interval_is_not_gap():
    doc = synthetic_evidence(1)
    assert review_evidence(doc,synthetic_indexes(doc))['coverage_gaps'] == []


def test_invalid_box_and_unknown_identity_do_not_pass():
    doc = synthetic_evidence()
    doc['frame_annotations'][0]['normalized_bbox']['width'] = 2
    report = review_evidence(doc,synthetic_indexes(doc))
    assert report['status']=='invalid'
    assert report['candidate_gate'] is False
    assert report['experiment_gate'] is False


def test_manual_perspective_and_duplicate_export_alias():
    doc = synthetic_evidence(1)
    indexes = synthetic_indexes(doc)
    indexes['synthetic']['recording']['perspective'] = 'unknown'
    entry = indexes['synthetic']['frames'][0]
    entry['_aliases'] = [entry['image_path'],'exports/alternate.png']
    doc['frame_annotations'][0]['image_path'] = 'exports/alternate.png'
    assert validate_evidence(doc,indexes) == []


def test_duplicate_export_cannot_add_third_timestamp():
    doc = synthetic_evidence(1)
    indexes = synthetic_indexes(doc)
    indexes['synthetic']['frames'].append(deepcopy(indexes['synthetic']['frames'][0]))
    doc['frame_annotations'][2].update({k:v for k,v in doc['frame_annotations'][1].items() if k!='annotation_id'})
    assert review_evidence(doc,indexes)['status'] == 'invalid'
