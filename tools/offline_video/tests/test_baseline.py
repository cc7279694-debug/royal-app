"""Real synthetic pixels and hand-computed temporal/ranking expectations."""
from copy import deepcopy
import importlib
from fractions import Fraction

import numpy as np
import pytest

from clash_tracker_video.evidence_contract import EvidenceError


def api():
    # RED explicitly asserts the missing capability instead of collection errors.
    try:
        return importlib.import_module('clash_tracker_video.baseline')
    except ModuleNotFoundError:
        pytest.fail('Module 2B-1 baseline capability is not implemented')


def pattern():
    return np.random.default_rng(37).integers(0, 255, (20, 20, 3), dtype=np.uint8)


def observation(t, score=.8, x=10):
    return dict(timestamp_seconds=t, raw_pts=int(t * 1000), time_base='1/1000',
                score=score, template_id='template_a', scale=1.,
                location={'x': x, 'y': 20, 'width': 20, 'height': 20},
                orb={'good_matches': 0})


def test_crop_rounding_and_boundaries():
    b = api()
    image = np.arange(8 * 10 * 3, dtype=np.uint8).reshape(8, 10, 3)
    result = b.crop(image, dict(x=.1, y=.25, width=.3, height=.5))
    assert np.array_equal(result, image[2:6, 1:4])
    result[:] = 0
    assert image[2:6, 1:4].any()  # independent crop, no source mutation


@pytest.mark.parametrize('box', [dict(x=-.1,y=0,width=.2,height=.2),
    dict(x=0,y=0,width=0,height=.2), dict(x=.9,y=0,width=.2,height=.2)])
def test_reject_invalid_crop(box):
    with pytest.raises(EvidenceError):
        api().crop(pattern(), box)


def test_multiscale_winner_and_full_image_coordinates():
    b = api()
    import cv2
    p = pattern()
    image = np.random.default_rng(38).integers(0, 255, (100, 100, 3), dtype=np.uint8)
    enlarged = cv2.resize(p, (25, 25), interpolation=cv2.INTER_LINEAR)
    image[60:85, 50:75] = enlarged
    config = b.Config(roi=(0.,.1,1.,.8), scales=(1.,1.25), working_scale=1.)
    result = b.score_frame(image, [b.Template('a', 'play_a', 'frame_a', p)], config)
    assert result['scale'] == 1.25
    assert result['score'] > .999
    assert result['location'] == dict(x=50,y=60,width=25,height=25)


def test_roi_excludes_fixed_ui_but_not_bottom_battlefield():
    b = api()
    p = pattern()
    image = np.zeros((100, 100, 3), np.uint8)
    image[:20,:20] = p
    image[60:80,50:70] = p
    result = b.score_frame(image, [b.Template('a','A','f',p)],
        b.Config(roi=(0.,.25,1.,.6), scales=(1.,), working_scale=1.))
    assert result['location']['y'] == 60


def test_constant_and_oversize_templates_are_skipped():
    b = api()
    templates = [b.Template('a','A','a',np.full((20,20,3),128,np.uint8)),
                 b.Template('b','A','b',np.zeros((400,400,3),np.uint8))]
    result = b.score_frame(pattern(), templates, b.Config(roi=(0.,0.,1.,1.),working_scale=1.))
    assert result['score'] is None
    assert result['skipped_scales'] == 10


def test_orb_no_descriptors_and_no_ranking_weight():
    b = api()
    diagnostic = b.orb_diagnostic(np.zeros((10,10,3),np.uint8), np.zeros((10,10,3),np.uint8))
    assert diagnostic['good_matches'] == 0
    original = [observation(1,.6), observation(5,.9)]
    changed = deepcopy(original)
    changed[0]['orb']['good_matches'] = 10000
    assert [e['peak']['timestamp_seconds'] for e in b.rank_events(b.merge_events(original))] == [5,1]
    assert [e['peak']['timestamp_seconds'] for e in b.rank_events(b.merge_events(changed))] == [5,1]


def test_continuous_support_over_two_seconds_remains_one_event():
    events = api().merge_events([observation(t) for t in (0,1,2,3,4,5)])
    assert len(events) == 1
    assert events[0]['first']['timestamp_seconds'] == 0
    assert events[0]['last_seconds'] == 5


def test_two_seconds_inclusive_merge_but_gap_over_two_splits():
    events = api().merge_events([observation(1), observation(3), observation(5.001)])
    assert len(events) == 2


def test_peak_and_first_hit_are_distinct_and_rank_deterministic():
    b = api()
    events = b.merge_events([observation(1,.7),observation(2.5,.9),observation(6,.9)])
    ranked = b.rank_events(events)
    assert ranked[0]['first']['timestamp_seconds'] == 1
    assert ranked[0]['peak']['timestamp_seconds'] == 2.5
    assert [e['rank'] for e in ranked] == [1,2]


@pytest.mark.parametrize('first,want', [(9.999,False),(10,True),(12,True),(12.001,False)])
def test_hidden_hit_inclusive_after_spawn_window(first,want):
    b = api()
    ranked = b.rank_events(b.merge_events([observation(first)]))
    result = b.evaluate(ranked, {'play_id':'B','deployment_time_seconds':10})
    assert result['pass'] is want


def test_early_event_cannot_be_rescued_by_later_peak():
    b = api()
    ranked = b.rank_events(b.merge_events([observation(9,.6),observation(10.5,.99)]))
    assert b.evaluate(ranked,dict(play_id='B',deployment_time_seconds=10))['pass'] is False


def test_source_exclusion_before_top_five_only_reference_visible_interval():
    b = api()
    observations = [observation(1,.99), *[observation(t,.8) for t in (5,9,13,17,21,25)]]
    ranked = b.rank_events(b.merge_events(observations), source_interval=(.9,2))
    assert len(ranked[:5]) == 5
    assert ranked[0]['first']['timestamp_seconds'] == 5
    assert b.evaluate(ranked,dict(play_id='B',deployment_time_seconds=25))['rank'] == 6
    assert not b.evaluate(ranked,dict(play_id='B',deployment_time_seconds=25))['pass']


def test_hidden_evaluation_cannot_change_frozen_ranking():
    b = api()
    ranked = b.rank_events(b.merge_events([observation(1),observation(5)]))
    before = deepcopy(ranked)
    b.evaluate(ranked,dict(play_id='B',deployment_time_seconds=1))
    b.evaluate(ranked,dict(play_id='B',deployment_time_seconds=99))
    assert ranked == before


def test_coarse_first_frame_after_each_target_exact_pts():
    b = api()
    got = b.coarse_select([Fraction(0),Fraction(1,10),Fraction(3,10),Fraction(6,10)], 4)
    assert got == [0,2,3]


def test_fine_windows_are_fixed_clipped_and_gt_free():
    assert api().fine_windows([.2,3], 4, 1) == [(0.,1.2),(2.,4.)]


def test_threshold_uses_only_two_held_out_true_scores():
    b = api()
    folds = [{'pass':True,'true_event_score':.7}, {'pass':True,'true_event_score':.8}]
    assert b.final_threshold(folds) == .7
    folds[1]['pass'] = False
    with pytest.raises(EvidenceError):
        b.final_threshold(folds)


def test_artifact_determinism_and_key_semantic_digest_changes():
    b = api()
    template = b.Template('a','A','frame',pattern())
    args = ('a'*64, {'card_id':'minions','form':'normal'}, [template], b.Config(), .7, 'b'*40)
    artifact = b.make_artifact(*args)
    assert b.artifact_sha(artifact) == b.artifact_sha(b.make_artifact(*args))
    for name,value in [('threshold',.71),('development_lock_sha256','c'*64),('git_commit','d'*40)]:
        changed = deepcopy(artifact); changed[name] = value
        assert b.artifact_sha(changed) != b.artifact_sha(artifact)


@pytest.mark.parametrize('field,value', [('fps',0),('scales',()),('merge_seconds',-1),
    ('working_scale',float('nan')),('proposal_floor',1.1),('roi',(0.,.2,1.,1.)),('top_k',6)])
def test_invalid_config_rejected(field,value):
    with pytest.raises(EvidenceError):
        api().Config(**{field:value})
