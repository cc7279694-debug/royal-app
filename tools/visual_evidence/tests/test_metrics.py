import importlib
import pytest

def module():
    try: return importlib.import_module('tools.visual_evidence.metrics')
    except ImportError: pytest.fail('visual evidence metrics not implemented')

def row(i,t,owner='opponent',cls='visual.unit.royal_hog'):
    return {'observation_id':i,'match_id':'m','timestamp':t,'visual_class':cls,
            'bbox':[10,10,20,20],'owner':owner,'confidence':.8}

def test_fragment_proxy_keeps_fixed_raw_denominator_and_unassigned():
    rows=[row('a',0),row('b',.25),row('c',.5)]
    got=module().track_metrics(rows,[{'track_id':'t','observation_ids':['a','b']}])
    assert got['raw_observation_count']==3 and got['unassigned_observation_count']==1
    assert got['track_starts_per_100_raw_observations']==pytest.approx(100/3)
    assert got['true_fragmentation_measured'] is False

def test_singleton_counts_and_scope_exclude_unsupported_classes():
    rows=[row('a',0),row('b',.25),row('ui',0,cls='visual.structure.cannon')]
    got=module().track_metrics(rows,[{'track_id':'t','observation_ids':['a']},{'track_id':'u','observation_ids':['b']},{'track_id':'x','observation_ids':['ui']}])
    assert got['track_count']==2 and got['singleton_count']==2 and got['raw_observation_count']==2

def test_owner_flip_unknown_not_successful_stability():
    raw=[row('a',0,'own'),row('b',.25,'opponent'),row('c',.5,'own')]
    exp=[dict(r,owner='unknown') for r in raw]
    m=module().owner_metrics(raw,exp,[{'track_id':'t','observation_ids':['a','b','c']}])
    assert m['raw']['known_flip_count']==2 and m['experimental']['known_flip_count']==0
    assert m['experimental']['unknown_fraction']==1 and m['experimental']['known_known_link_count']==0
    assert m['owner_accuracy_measured'] is False

def test_owner_comparison_requires_same_observation_set_and_geometry():
    raw=[row('a',0)]
    with pytest.raises(ValueError): module().owner_metrics(raw,[row('b',0)],[])
    with pytest.raises(ValueError): module().owner_metrics(raw,[dict(raw[0],timestamp=1)],[])

def test_track_metrics_rejects_duplicate_assignment():
    with pytest.raises(ValueError): module().track_metrics([row('a',0)],[{'track_id':'t','observation_ids':['a']},{'track_id':'u','observation_ids':['a']}])

def test_scope_reports_per_match_class_and_censoring():
    raw=[row('a',0),row('b',.25)]
    m=module().track_metrics(raw,[{'track_id':'t','observation_ids':['a','b']}])
    assert m['by_match_class'][0]['match_id']=='m'
    assert m['by_match_class'][0]['initial_visible_track_count']==1
    assert m['by_match_class'][0]['final_visible_track_count']==1

def test_owner_trajectory_does_not_use_current_half():
    raw=[row('a',0,'opponent'),dict(row('b',.25,'opponent'),bbox=[10,900,20,920])]
    m=module().owner_metrics(raw,raw,[{'track_id':'t','observation_ids':['a','b']}])
    assert m['raw']['known_flip_count']==0 and m['experimental']['known_known_link_count']==1
