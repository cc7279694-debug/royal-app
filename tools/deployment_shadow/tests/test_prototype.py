"""Synthetic behavior checks: catch unsupported second plays and lost uncertainty."""
import copy
import importlib
import json
import random

import pytest

from tools.event_engine.engine import replay


@pytest.fixture
def shadow():
    try:
        return importlib.import_module('tools.deployment_shadow.prototype').run_shadow
    except ImportError:
        def missing_behavior(*_args):
            pytest.fail('Shadow deployment reasoning is not implemented yet')
        return missing_behavior


def units(time, xs, *, cls='visual.unit.royal_hog', owner='opponent',
          origin='unknown', form='unknown', tag='a', match='m'):
    return [dict(observation_id=f'{match}-{tag}-{time}-{i}', match_id=match,
                 timestamp=time, visual_class=cls, bbox=[x, 20, x+20, 50],
                 owner=owner, form=form, origin_kind=origin,
                 source='synthetic_observation') for i, x in enumerate(xs)]


def frames(rows, extra=()):
    return [dict(match_id=m, timestamp=t) for m, t in sorted(
        {(r['match_id'], r['timestamp']) for r in rows} | set(extra))]


def staged():
    return units(0, [20, 45]) + units(1, [22, 47, 70, 95])


def test_staged_two_then_four_keeps_one_provisional_event_and_full_second_candidate(shadow):
    # Break caught: treating newly found member tracks as an automatic second play.
    rows = staged()
    baseline = replay(rows)
    assert len(baseline['events']) == 2
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert result['events'][0]['timestamp'] == 0
    assert result['events'][0]['shadow_status'] == 'PROVISIONAL'
    assert result['events'][0]['not_confirmed_card_play'] is True
    second = next(c for c in result['candidates'] if c['timestamp'] == 1)
    assert second['shadow_status'] == 'UNRESOLVED'
    assert second['disposition'] == 'possible_late_member'
    assert second['baseline_event'] == baseline['events'][1]
    assert second in result['unresolved']
    assert len(result['groups']) == 1
    assert len(result['groups'][0]['possible_member_track_ids']) == 4
    assert result['groups'][0]['membership_proven'] is False


def test_moving_group_with_sparse_frames_retains_late_members(shadow):
    # Break caught: comparing against original positions instead of recent motion.
    rows = units(0, [20, 45]) + units(2.5, [150, 175, 200, 225])
    rows += units(7.5, [500, 525, 550, 575])
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert len(result['groups'][0]['possible_member_track_ids']) == 4
    assert len(result['baseline_replay']['tracks']) == 4


def test_far_new_cohort_is_supported_while_old_members_remain_visible(shadow):
    # Break caught: blanket merging or a card cooldown swallowing distant births.
    rows = units(0, [20, 45]) + units(1, [22, 47])
    rows += units(1, [400, 425], tag='far')
    result = shadow(rows, frames(rows))
    assert [e['timestamp'] for e in result['events']] == [0, 1]
    assert len(result['groups']) == 2
    assert result['events'][1]['evidence_basis']['separation'] == 'spatially_separate_cohort'
    assert all(e['estimated_deployment_timestamp'] is None for e in result['events'])


def test_recent_sampled_non_detection_supports_fresh_cohort_but_not_physical_onset(shadow):
    # Break caught: ignoring frame coverage or upgrading sampled absence to truth.
    rows = units(0, [20, 45]) + units(.25, [22, 47])
    rows += units(8, [22, 47]) + units(8.25, [24, 49])
    result = shadow(rows, frames(rows, [('m', 4), ('m', 6), ('m', 7.5)]))
    assert [e['timestamp'] for e in result['events']] == [0, 8]
    evidence = result['events'][1]['evidence_basis']
    assert evidence['separation'] == 'sampled_non_detection_not_proven_absence'
    assert evidence['absence_frame_timestamps'] == [6, 7.5]
    assert evidence['physical_absence_proven'] is False
    assert result['events'][1]['estimated_deployment_timestamp'] is None


def test_track_expiry_alone_does_not_prove_a_second_play(shadow):
    # Break caught: promoting track-gap expiry to positive deployment evidence.
    rows = units(0, [20, 45]) + units(.25, [22, 47]) + units(8, [22, 47])
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert result['unresolved'][0]['disposition'] == 'ambiguous_overlap'


def test_close_later_cohort_remains_unresolved_when_same_play_cannot_be_proven(shadow):
    # Break caught: calling all nearby later detections established late members.
    rows = units(0, [20, 45]) + units(3, [22, 47, 80, 105])
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert result['unresolved'][0]['disposition'] == 'ambiguous_overlap'
    assert result['unresolved'][0]['baseline_event_id'] is not None


def test_expected_count_overflow_does_not_lose_or_promote_candidates(shadow):
    # Break caught: using expected capacity to erase extras or create another play.
    rows = units(0, [20, 45]) + units(1, [22, 47, 70, 95, 120, 145])
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert len(result['groups'][0]['possible_member_track_ids']) == 6
    assert result['groups'][0]['expected_units'] == 4
    assert result['groups'][0]['capacity_exceeded'] is True
    assert len(result['candidates']) == len(result['baseline_replay']['candidates'])
    assert {c['baseline_event_id'] for c in result['candidates'] if c['baseline_event_id']} == {
        e['event_id'] for e in result['baseline_replay']['events']}


@pytest.mark.parametrize('metadata', [dict(owner='own'), dict(owner='unknown'),
    dict(origin='spawned'), dict(origin='secondary'),
    dict(cls='visual.unit.skeleton'), dict(form='evolved')])
def test_guarded_observations_are_retained_without_qualified_shadow_events(shadow, metadata):
    # Break caught: silently coercing own/unknown/spawned/evolved/unsupported rows.
    rows = units(0, [20, 45], **metadata) + units(1, [22, 47], **metadata)
    result = shadow(rows, frames(rows))
    assert result['events'] == []
    assert result['candidates']
    assert all(c['shadow_status'] == 'UNRESOLVED' for c in result['candidates'])


@pytest.mark.parametrize('owner', ['own', 'unknown'])
def test_owner_flicker_prevents_unsafe_promotion_and_retains_conflict_ids(shadow, owner):
    # Break caught: using a later opponent label as proof over overlapping conflict.
    rows = units(0, [20, 45], owner=owner)
    rows += units(.25, [21, 46]) + units(.5, [22, 47])
    result = shadow(rows, frames(rows))
    assert result['baseline_replay']['events']
    assert result['events'] == []
    qualified = next(c for c in result['candidates'] if c['baseline_event_id'])
    assert qualified['disposition'] == 'identity_conflict'
    assert set(qualified['conflict_observation_ids']) == {'m-a-0-0', 'm-a-0-1'}


def test_direct_event_time_is_original_first_seen_with_confirmation_separate(shadow):
    # Break caught: scoring with confirmation or inventing a corrected onset.
    rows = units(30.5, [20], cls='visual.unit.witch')
    rows += units(30.75, [21], cls='visual.unit.witch')
    result = shadow(rows, frames(rows))
    event = result['events'][0]
    assert event['timestamp'] == event['first_seen_timestamp'] == 30.5
    assert event['confirmed_at'] == event['confirmation_timestamp'] == 30.75
    assert event['estimated_deployment_timestamp'] is None
    assert event['evidence_basis']['physical_onset_proven'] is False
    assert event['event_id'] == result['baseline_replay']['events'][0]['event_id']
    assert result['time_evidence'][0]['comparison_timestamp'] == 30.5


def test_deterministic_shuffled_input_preserves_source_and_baseline(shadow):
    # Break caught: order-sensitive grouping or in-place annotation of source data.
    rows = staged() + units(.5, [300], cls='visual.unit.witch', match='n')
    rows += units(.75, [301], cls='visual.unit.witch', match='n')
    sampled = frames(rows)
    pristine = copy.deepcopy((rows, sampled))
    result = shadow(rows, sampled)
    shuffled = copy.deepcopy(rows)
    random.Random(12).shuffle(shuffled)
    assert shadow(shuffled, list(reversed(sampled))) == result
    assert (rows, sampled) == pristine
    assert result['baseline_replay'] == replay(rows)
    assert json.loads(json.dumps(result, allow_nan=False)) == result


@pytest.mark.parametrize('addition', [dict(gt_timestamp=1), dict(duplicate=True),
    dict(appearance_group_id='human-answer'), dict(expected_card_id='royal_hogs')])
def test_answer_fields_cannot_enter_shadow_generation(shadow, addition):
    # Break caught: answer leakage changing a GT-free event-generation API.
    rows = units(0, [20, 45])
    rows[0].update(addition)
    with pytest.raises(ValueError):
        shadow(rows, frames(rows))


def test_human_continuity_source_is_rejected_even_without_extra_fields(shadow):
    rows = units(0, [20, 45])
    rows[0]['source'] = 'human_gt_continuity'
    with pytest.raises(ValueError):
        shadow(rows, frames(rows))


def test_missing_observation_frame_is_not_silently_assumed_covered(shadow):
    rows = staged()
    with pytest.raises(ValueError):
        shadow(rows, [dict(match_id='m', timestamp=0)])


def test_frame_answer_fields_are_rejected(shadow):
    with pytest.raises(ValueError):
        shadow([], [dict(match_id='m', timestamp=0, negative=True)])


def test_empty_input_is_valid_and_explicitly_experimental(shadow):
    result = shadow([], [])
    assert result['events'] == result['candidates'] == result['groups'] == []
    assert result['limitations']['production_replacement'] is False
    assert result['limitations']['unobserved_is_negative'] is False


def test_same_timestamp_overlapping_baseline_cohorts_remain_inspectable(shadow):
    # Break caught: no strictly-earlier member observation causing a max() crash.
    rows = units(0, [20, 100, 145, 170])
    assert len(replay(rows)['events']) == 2
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    assert result['unresolved'][0]['disposition'] == 'ambiguous_overlap'
    assert result['unresolved'][0]['first_seen_timestamp'] == 0
    assert result['unresolved'][0]['baseline_event'] is not None


def test_unknown_same_class_sample_blocks_claim_of_sampled_non_detection(shadow):
    # Break caught: treating guarded visual detections as negative/empty frames.
    rows = units(0, [20, 45]) + units(.25, [22, 47])
    rows += units(7.5, [200], owner='unknown') + units(8, [22, 47])
    result = shadow(rows, frames(rows, [('m', 6)]))
    assert len(result['events']) == 1
    later = next(c for c in result['candidates'] if c['timestamp'] == 8)
    assert later['disposition'] == 'ambiguous_overlap'


def test_only_distant_conflicting_owner_does_not_override_supported_identity(shadow):
    # Break caught: checking only class/time while ignoring conflicting geometry.
    rows = units(0, [20], cls='visual.unit.witch')
    rows += units(.25, [21], cls='visual.unit.witch')
    rows += units(.25, [400], cls='visual.unit.witch', owner='own', tag='own')
    result = shadow(rows, frames(rows))
    assert len(result['events']) == 1
    qualified = next(c for c in result['candidates'] if c['baseline_event_id'])
    assert qualified['conflict_observation_ids'] == []


def test_later_owner_conflict_is_retrospective_uncertainty_without_time_shift(shadow):
    # Break caught: retaining continuity as safe after later overlapping conflict.
    rows = units(0, [20], cls='visual.unit.witch')
    rows += units(.25, [21], cls='visual.unit.witch')
    rows += units(6, [22], cls='visual.unit.witch')
    rows += units(6.25, [22], cls='visual.unit.witch', owner='own', tag='own')
    result = shadow(rows, frames(rows))
    qualified = next(c for c in result['candidates'] if c['baseline_event_id'])
    assert result['events'] == []
    assert qualified['disposition'] == 'identity_conflict'
    assert qualified['first_seen_timestamp'] == 0
    assert qualified['confirmation_timestamp'] == .25
    assert qualified['conflict_observation_ids'] == ['m-own-6.25-0']


def test_real_frame_metadata_is_accepted_without_affecting_time(shadow):
    rows = units(0, [20, 45])
    sampled = [dict(match_id='m', timestamp=0, sample_index=0, raw_pts=0,
                    time_base='1/90000', prediction_count=2)]
    result = shadow(rows, sampled)
    assert result['events'][0]['timestamp'] == 0


@pytest.mark.parametrize('source', ['human_gt', 'event_gt', 'oracle'])
def test_other_answer_sources_cannot_enter_even_with_clean_fields(shadow, source):
    rows = units(0, [20, 45])
    rows[0]['source'] = source
    with pytest.raises(ValueError):
        shadow(rows, frames(rows))
