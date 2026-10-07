import copy
import importlib

import pytest


@pytest.fixture
def replay():
    try:
        return importlib.import_module('tools.event_engine.engine').replay
    except ImportError:
        pytest.fail('Oracle replay behavior is not implemented yet')


def obs(i, t, cls='visual.unit.witch', *, owner='opponent', origin='unknown',
        group=None, x=20, y=20, form='unknown', match='m1'):
    return dict(observation_id=str(i), match_id=match, timestamp=t,
                visual_class=cls, bbox=[x, y, x+20, y+30], owner=owner,
                form=form, origin_kind=origin, appearance_group_id=group,
                source='human_gt_continuity' if group else 'human_gt')


def test_same_witch_twenty_observations_one_event(replay):
    r = replay([obs(i, i*.5, x=20+i) for i in range(20)])
    assert len(r['events']) == 1
    assert r['events'][0]['timestamp'] == 0
    assert r['events'][0]['confirmed_at'] == .5
    assert len(r['events'][0]['source_observation_ids']) == 20


def test_lone_observation_only_candidate(replay):
    r = replay([obs('a', 1)])
    assert r['events'] == []
    assert r['candidates'][0]['evidence_level'] == 'MEDIUM'


def test_human_continuity_group_is_strong(replay):
    assert len(replay([obs('a', 1, group='human-witch')])['events']) == 1


def test_geometry_occlusion_reconnects(replay):
    assert len(replay([obs('a', 0), obs('b', 2.5), obs('c', 7.5, x=40)])['events']) == 1


def test_human_identity_survives_long_gap(replay):
    assert len(replay([obs('a', 0, group='g'), obs('b', 80, group='g')])['events']) == 1


def test_two_distinct_witches_even_same_time(replay):
    r = replay([obs('a', 0, x=10), obs('b', 0, x=300),
                obs('c', 1, x=12), obs('d', 1, x=302)])
    assert len(r['events']) == 2


def test_different_human_groups_not_cooldown_merged(replay):
    assert len(replay([obs('a', 0, group='g1'), obs('b', 1, group='g2')])['events']) == 2


@pytest.mark.parametrize('owner', ['own', 'unknown'])
def test_owner_guard(replay, owner):
    r = replay([obs('a', 0, owner=owner), obs('b', 1, owner=owner)])
    assert r['events'] == []
    assert r['candidates'][0]['evidence_level'] == 'WEAK'


@pytest.mark.parametrize('cls,origin', [('visual.unit.skeleton','spawned'),
                                     ('visual.unit.witch','spawned'),
                                     ('visual.unit.witch','secondary')])
def test_spawned_secondary_guard(replay, cls, origin):
    assert replay([obs('a', 0, cls, origin=origin), obs('b', 1, cls, origin=origin)])['events'] == []


@pytest.mark.parametrize('cls', ['visual.structure.cannon', 'visual.barbarian_barrel',
                               'visual.unit.barbarian_barrel', 'visual.structure.mortar'])
def test_observe_only_and_out_of_first_registry(replay, cls):
    assert replay([obs('a', 0, cls), obs('b', 1, cls)])['events'] == []


def test_three_minions_one_event(replay):
    r = replay([obs(i, 0, 'visual.unit.minion', x=20+25*i) for i in range(3)])
    assert len(r['events']) == 1
    assert r['events'][0]['card_id'] == 'minions'
    assert r['events'][0]['confirmed_at'] == 0


def test_two_minions_continue_one_group(replay):
    stream = [obs(f'{t}-{i}', t, 'visual.unit.minion', x=20+25*i+t) for t in (0,1,3,6) for i in range(2)]
    assert len(replay(stream)['events']) == 1


def test_single_minion_repeated_does_not_count_multiple_units(replay):
    assert replay([obs(i, i, 'visual.unit.minion', x=20+i) for i in range(4)])['events'] == []


def test_new_group_after_gap_can_emit_second(replay):
    r = replay([obs(f'{t}-{i}', t, 'visual.unit.minion', x=20+25*i) for t in (0,1,30,31) for i in range(2)])
    assert len(r['events']) == 2


def test_close_time_far_apart_minions_do_not_group(replay):
    assert replay([obs('a', 0, 'visual.unit.minion'), obs('b', 0, 'visual.unit.minion', x=350)])['events'] == []


def test_royal_hogs_multi_unit_one_event(replay):
    assert [e['card_id'] for e in replay([obs(i, 0, 'visual.unit.royal_hog', x=20+25*i) for i in range(4)])['events']] == ['royal_hogs']


def test_deterministic_ids_and_shuffle(replay):
    stream=[obs('a',0),obs('b',1),obs('c',2)]
    assert replay(stream) == replay(list(reversed(stream)))
    assert replay(stream)['events'][0]['event_id'].startswith('event-')


def test_no_input_mutation(replay):
    stream=[obs('a',0),obs('b',1)]; saved=copy.deepcopy(stream)
    replay(stream)
    assert stream == saved


@pytest.mark.parametrize('field,value', [('timestamp',float('nan')),('timestamp',-1),
                                      ('owner','enemy'),('bbox',[0,0,0,1]),('confidence',2)])
def test_invalid_inputs_rejected(replay, field, value):
    row=obs('a',0); row[field]=value
    with pytest.raises(ValueError): replay([row])


def test_duplicate_observation_id_refused(replay):
    with pytest.raises(ValueError): replay([obs('a',0),obs('a',1)])


def test_match_isolation(replay):
    assert len(replay([obs('a',0,group='g'),obs('b',0,group='g',match='m2')])['events']) == 2


def test_form_isolation(replay):
    assert replay([obs('a',0,form='normal'),obs('b',1,form='evolved')])['events'] == []


def test_contradictory_human_group_rejected(replay):
    with pytest.raises(ValueError):
        replay([obs('a',0,group='g'),obs('b',1,group='g',owner='own')])


def test_identical_boxes_cannot_pretend_to_be_distinct_units(replay):
    with pytest.raises(ValueError):
        replay([obs('a',0,'visual.unit.minion'),obs('b',0,'visual.unit.minion')])


def test_result_cannot_mutate_frozen_registry(replay):
    r=replay([]);r['registry']['visual.unit.minion']['minimum_new_units']=1
    assert replay([obs('a',0,'visual.unit.minion')])['events']==[]


def test_same_human_appearance_multiple_same_frame_boxes_one_event(replay):
    r=replay([obs('a',0,group='g',x=10),obs('b',0,group='g',x=300),
              obs('c',2,group='g',x=15),obs('d',2,group='g',x=305)])
    assert len(r['events'])==1
    assert r['events'][0]['source_observation_ids']==['a','b','c','d']


def test_broken_single_unit_track_cannot_be_two_new_units(replay):
    r=replay([obs('a',0,'visual.unit.minion',x=20),obs('b',1,'visual.unit.minion',x=115)])
    assert r['events']==[]


def test_group_can_confirm_only_after_two_new_tracks_coexist(replay):
    r=replay([obs('a',0,'visual.unit.minion',x=20),obs('b',1,'visual.unit.minion',x=115),
              obs('c',2,'visual.unit.minion',x=20),obs('d',2,'visual.unit.minion',x=115)])
    assert len(r['events'])==1 and r['events'][0]['confirmed_at']==2
