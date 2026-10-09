"""Synthetic behavior tests: no pixels, model, game-state truth or Event GT."""
from copy import deepcopy
from importlib import import_module

import pytest


def observation(oid, time, *, owner='opponent', track_class='visual.unit.witch',
                bbox=None, match='match-a'):
    return {'observation_id': oid, 'match_id': match, 'timestamp': time,
            'visual_class': track_class, 'bbox': bbox or [10., 10., 30., 30.],
            'owner': owner, 'form': 'unknown', 'origin_kind': 'unknown',
            'confidence': .9, 'source': 'synthetic_observation'}


def assignment(row, track='track-a', ambiguous=False):
    return {'observation_id': row['observation_id'], 'track_id': track,
            'association_ambiguous': ambiguous}


def run(rows, assignments=None, **kwargs):
    policy = import_module('tools.visual_evidence.policy')
    return policy.run_policy(rows, assignments or [assignment(r) for r in rows], **kwargs)


def track_rows(track, first=0., *, owner='opponent', x=10., match='match-a',
               track_class='visual.unit.minion'):
    rows = [observation(f'{match}-{track}-{i}', first + i * .25, owner=owner,
                        bbox=[x, 10., x + 20., 30.], match=match,
                        track_class=track_class) for i in range(3)]
    return rows, [assignment(r, track) for r in rows]


def combined(*parts):
    return [r for rows, _ in parts for r in rows], [a for _, assignments in parts for a in assignments]


def test_owner_waits_for_three_distinct_observations():
    rows = [observation(f'o{i}', i * .25) for i in range(3)]
    result = run(rows)
    assert [r['owner'] for r in result['observations']] == ['unknown', 'unknown', 'opponent']
    assert result['owner_evidence'][-1]['history_votes'] == ['opponent'] * 3
    assert result['owner_evidence'][-1]['first_seen_timestamp'] == 0.
    assert result['owner_evidence'][-1]['confirmation_timestamp'] == .5


def test_conflict_abstains_instead_of_majority_owner():
    owners = ['own', 'opponent', 'opponent', 'opponent']
    rows = [observation(f'o{i}', i * .25, owner=o) for i, o in enumerate(owners)]
    result = run(rows)
    assert [r['owner'] for r in result['observations']] == ['unknown', 'unknown', 'unknown', 'opponent']
    assert result['owner_evidence'][2]['owner_reason'] == 'conflicting_owner_predictions'


def test_unknown_current_and_unknown_history_are_never_converted():
    owners = ['opponent', 'opponent', 'unknown', 'opponent', 'opponent', 'opponent']
    rows = [observation(f'o{i}', i * .25, owner=o) for i, o in enumerate(owners)]
    result = run(rows)
    assert [r['owner'] for r in result['observations']] == ['unknown'] * 5 + ['opponent']
    assert result['owner_evidence'][2]['owner_reason'] == 'raw_owner_unknown'


def test_ambiguous_and_unassigned_association_remain_unknown():
    rows = [observation(f'o{i}', i * .25) for i in range(5)]
    assignments = [assignment(r) for r in rows]
    assignments[2] = assignment(rows[2], ambiguous=True)
    assignments[4] = assignment(rows[4], track=None)
    result = run(rows, assignments)
    assert [r['owner'] for r in result['observations']] == ['unknown'] * 5
    assert result['owner_evidence'][2]['owner_reason'] == 'association_ambiguous'
    assert result['owner_evidence'][4]['owner_reason'] == 'unassigned_track'


def test_region_crossing_does_not_invert_known_owner():
    rows = [observation(f'o{i}', i * .25, owner='own',
                        bbox=[10., y, 30., y + 20.])
            for i, y in enumerate([10., 45., 75.])]
    result = run(rows, source_dimensions_wh={'match-a': [100, 100]})
    assert result['observations'][-1]['owner'] == 'own'
    context = result['owner_evidence'][-1]
    assert context['initial_region'] == 'upper'
    assert context['current_region'] == 'lower'
    assert context['region_crossing'] is True
    assert context['first_bbox_relative'] == [.1, .1, .3, .3]


def test_jump_and_reacquisition_are_context_only_flags():
    rows = [observation('o0', 0.), observation('o1', .25),
            observation('o2', 1.25, bbox=[300., 10., 320., 30.])]
    result = run(rows)
    assert result['observations'][-1]['owner'] == 'opponent'
    context = result['owner_evidence'][-1]
    assert context['reacquisition_context'] is True
    assert context['contradictory_jump_context'] is True
    assert context['velocity_pixels_per_second'] == [290., 0.]


def test_projection_preserves_raw_evidence_and_never_human_identity():
    rows = [observation(f'o{i}', i * .25) for i in range(3)]
    original = deepcopy(rows)
    result = run(rows)
    assert rows == original
    for raw, projected in zip(original, result['observations']):
        assert set(projected) == set(raw)
        assert projected['source'] == 'katacr_bytetrack_shadow'
        assert {k: v for k, v in projected.items() if k not in {'owner', 'source'}} == {
            k: v for k, v in raw.items() if k not in {'owner', 'source'}}
        assert 'appearance_group_id' not in projected
    assert result['owner_evidence'][0]['raw_owner'] == 'opponent'
    assert result['groups'] == []


def test_late_member_joins_existing_cohort_once():
    rows, assignments = combined(track_rows('a'), track_rows('b', .5, x=40.),
                                 track_rows('c', 1., x=70.))
    rows += [observation('c-later', 1.75, bbox=[70., 10., 90., 30.],
                         track_class='visual.unit.minion')]
    assignments += [assignment(rows[-1], 'c')]
    result = run(rows, assignments)
    assert len(result['groups']) == 1
    assert result['groups'][0]['member_track_ids'] == ['a', 'b', 'c']
    assert result['groups'][0]['confirmed_card_play'] is False
    assert 'events' not in result


def test_old_survivors_and_genuinely_separate_births_can_form_second_cohort():
    rows, assignments = combined(track_rows('a'), track_rows('b', 0., x=40.),
                                 track_rows('new-a', 5., x=250.),
                                 track_rows('new-b', 5., x=280.))
    rows += [observation('old-survivor', 5.25, bbox=[40., 10., 60., 30.],
                         track_class='visual.unit.minion')]
    assignments += [assignment(rows[-1], 'b')]
    result = run(rows, assignments)
    assert len(result['groups']) == 2
    assert sorted(g['member_track_ids'] for g in result['groups']) == [['a', 'b'], ['new-a', 'new-b']]
    assert all(g['confirmed_card_play'] is False for g in result['groups'])


def test_simultaneous_multiple_compatible_cohorts_are_unresolved():
    rows, assignments = combined(track_rows('a', x=0.), track_rows('b', x=200.),
                                 track_rows('c', x=100.))
    result = run(rows, assignments)
    assert len(result['groups']) == 2
    member = next(m for m in result['group_membership'] if m['track_id'] == 'c')
    assert member['status'] == 'UNRESOLVED'
    assert member['reason'] == 'multiple_compatible_cohorts'
    assert member['group_id'] is None
    assert all(g['status'] == 'UNRESOLVED' for g in result['groups'])


@pytest.mark.parametrize('visual,capacity', [('visual.unit.minion', 3), ('visual.unit.royal_hog', 4)])
def test_capacity_overflow_does_not_create_a_new_confirmed_play(visual, capacity):
    rows, assignments = combined(*[track_rows(f't{i}', x=10. + i * 10., track_class=visual)
                                   for i in range(capacity + 1)])
    result = run(rows, assignments)
    assert len(result['groups']) == 1
    assert len(result['groups'][0]['member_track_ids']) == capacity
    overflow = next(m for m in result['group_membership'] if m['track_id'] == f't{capacity}')
    assert overflow['status'] == 'UNRESOLVED'
    assert overflow['reason'] == 'compatible_cohort_at_capacity'


def test_opposite_owner_candidate_near_cohort_is_unresolved():
    rows, assignments = combined(track_rows('a'), track_rows('b', x=40., owner='own'))
    result = run(rows, assignments)
    assert len(result['groups']) == 1
    member = next(m for m in result['group_membership'] if m['track_id'] == 'b')
    assert member['status'] == 'UNRESOLVED'
    assert member['reason'] == 'cohort_owner_conflict'
    assert result['groups'][0]['status'] == 'UNRESOLVED'


def test_existing_member_owner_conflict_marks_cohort_unresolved():
    rows, assignments = track_rows('a')
    rows.append(observation('a-conflict', .75, owner='own', track_class='visual.unit.minion'))
    assignments.append(assignment(rows[-1], 'a'))
    result = run(rows, assignments)
    assert result['groups'][0]['status'] == 'UNRESOLVED'
    assert result['group_membership'][0]['reason'] == 'conflicting_owner_predictions'


def test_deterministic_order_and_match_isolation():
    rows, assignments = combined(track_rows('a'), track_rows('a', match='match-b', owner='own'))
    expected = run(rows, assignments)
    assert run(list(reversed(rows)), list(reversed(assignments))) == expected
    assert len(expected['groups']) == 2
    assert sorted((g['match_id'], g['owner']) for g in expected['groups']) == [
        ('match-a', 'opponent'), ('match-b', 'own')]


def test_same_frame_votes_cannot_manufacture_three_frame_consensus():
    rows = [observation(f'o{i}', 0.) for i in range(3)]
    rows[1]['bbox'] = [40., 10., 60., 30.]
    rows[2]['bbox'] = [70., 10., 90., 30.]
    with pytest.raises(ValueError, match='one observation per track and timestamp'):
        run(rows)


def test_human_continuity_input_and_bad_sidecar_are_rejected():
    row = observation('o', 0.)
    row.update(appearance_group_id='human-a', source='human_gt_continuity')
    with pytest.raises(ValueError, match='human identity'):
        run([row])
    valid = observation('valid', 0.)
    with pytest.raises(ValueError, match='association bindings'):
        run([valid], [assignment(valid), assignment(valid)])


def test_abstention_collisions_retain_all_raw_ids_for_root_engine_projection():
    rows = [observation('a', 0., owner='opponent'), observation('b', 0., owner='own')]
    result = run(rows, [assignment(rows[0], 'track-a'), assignment(rows[1], 'track-b')])
    assert [r['observation_id'] for r in result['observations']] == ['a', 'b']
    assert [r['owner'] for r in result['observations']] == ['unknown', 'unknown']
    assert [e['raw_owner'] for e in result['owner_evidence']] == ['opponent', 'own']


def test_future_observations_do_not_change_prior_owner_evidence():
    rows = [observation(f'o{i}', i * .25) for i in range(3)]
    prefix = run(rows)
    extended = run(rows + [observation('future', .75, owner='own')])
    assert extended['observations'][:3] == prefix['observations']
    assert extended['owner_evidence'][:3] == prefix['owner_evidence']


def test_spatially_separated_births_inside_spawn_window_form_separate_cohorts():
    rows, assignments = combined(track_rows('a'), track_rows('b', .25, x=250.))
    result = run(rows, assignments)
    assert len(result['groups']) == 2
    assert sorted(g['member_track_ids'] for g in result['groups']) == [['a'], ['b']]


@pytest.mark.parametrize('bad', [None, [], [{'observation_id': 'o', 'track_id': '', 'association_ambiguous': False}],
                                [{'observation_id': 'o', 'track_id': 'a', 'association_ambiguous': 1}]])
def test_missing_or_malformed_associations_are_rejected(bad):
    policy = import_module('tools.visual_evidence.policy')
    with pytest.raises(ValueError, match='association bindings'):
        policy.run_policy([observation('o', 0.)], bad)


def test_invalid_original_observations_remain_invalid():
    row = observation('o', 0., owner='unrecognized')
    with pytest.raises(ValueError, match='invalid observation metadata'):
        run([row])


def test_delayed_owner_consensus_updates_earliest_group_time_without_moving_anchor():
    anchor = track_rows('anchor', .25, x=110.)
    early_rows = [observation('early-unknown', 0., owner='unknown',
                              track_class='visual.unit.minion', bbox=[210., 10., 230., 30.])]
    early_rows += [observation(f'early-known-{i}', .75 + i * .25,
                              track_class='visual.unit.minion', bbox=[210., 10., 230., 30.])
                   for i in range(3)]
    early = early_rows, [assignment(r, 'early') for r in early_rows]
    rows, assignments = combined(anchor, early, track_rows('later-member', 1.5, x=10.))
    result = run(rows, assignments)
    assert len(result['groups']) == 1
    group = result['groups'][0]
    assert group['first_seen_timestamp'] == 0.
    assert group['anchor_first_seen_timestamp'] == .25
    assert group['anchor_track_id'] == 'anchor'
    assert group['anchor_bbox'] == [110., 10., 130., 30.]
    assert group['member_first_seen'] == {'anchor': .25, 'early': 0., 'later-member': 1.5}


def test_member_birth_span_cannot_extend_both_sides_of_anchor_window():
    anchor = track_rows('anchor', 2.5, x=10.)
    early_rows = [observation('early-unknown', 0., owner='unknown',
                              track_class='visual.unit.minion', bbox=[40., 10., 60., 30.])]
    early_rows += [observation(f'early-known-{i}', 3.25 + i * .25,
                              track_class='visual.unit.minion', bbox=[40., 10., 60., 30.])
                   for i in range(3)]
    early = early_rows, [assignment(r, 'early') for r in early_rows]
    rows, assignments = combined(anchor, early, track_rows('late', 5., x=70.))
    result = run(rows, assignments)
    assert len(result['groups']) == 1
    group = result['groups'][0]
    assert group['member_track_ids'] == ['anchor', 'early']
    assert group['member_first_seen'] == {'anchor': 2.5, 'early': 0.}
    late = next(m for m in result['group_membership'] if m['track_id'] == 'late')
    assert late['group_id'] is None
    assert late['status'] == 'UNRESOLVED'
    assert late['reason'] == 'cohort_birth_span_exceeded'
    assert next(r for r in result['observations'] if r['observation_id'] == 'match-a-late-2')['owner'] == 'opponent'
