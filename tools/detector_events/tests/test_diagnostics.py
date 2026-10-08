"""Synthetic post-score reporting checks; no pixels, private GT or inference."""
from copy import deepcopy
import importlib

import pytest

from tools.event_engine.engine import replay
from tools.event_engine.evaluation import evaluate


def build(stream, result, evaluation, gt):
    try:
        module = importlib.import_module('tools.detector_events.diagnostics')
    except ImportError:
        pytest.fail('Post-score detector diagnostics are not implemented')
    return module.build_diagnostics(stream, result, evaluation, gt)


def truth():
    positives = [('02', 'witch', 31.5), ('05', 'royal_hogs', 75.5),
                 ('06', 'flying_machine', 78.), ('07', 'golden_knight', 102.5),
                 ('08', 'minions', 116.)]
    dedupe = [('04', 'm1', 'golden_knight', 49., 55.),
              ('09', 'm1', 'minions', 124., 130.),
              ('12', 'm4', 'witch', 69., 75.)]
    unresolved = [('01', 'm1', 'minions', 11.5, 17.5),
                  ('03', 'm1', 'golden_knight', 41.5, 47.5),
                  ('10', 'm1', 'witch', 160., 166.),
                  ('11', 'm4', 'witch', 65., 71.)]
    windows = [{'candidate_id': 'candidate_' + cid, 'underlying_match_id': match,
                'card_id': card, 'context': {'start_seconds': start, 'end_seconds': end}}
               for cid, match, card, start, end in dedupe + unresolved]
    return {'schema': 'deployment_event_gt_lock_v1',
            'confirmed_events': [{'event_gt_id': 'event-gt-candidate_' + cid,
                                  'candidate_id': 'candidate_' + cid,
                                  'underlying_match_id': 'm1', 'card_id': card,
                                  'approximate_timestamp': timestamp}
                                 for cid, card, timestamp in positives],
            'continuity_dedupe_outcomes': [
                {'candidate_id': 'candidate_' + cid, 'underlying_match_id': match}
                for cid, match, _, _, _ in dedupe],
            'unresolved_candidates': [
                {'candidate_id': 'candidate_' + cid, 'underlying_match_id': match,
                 'evaluable': False, 'uncertainty_reason': 'deployment_onset_outside_review_window'}
                for cid, match, _, _, _ in unresolved],
            'source_plan': {'candidates': windows}}


def observation(identity, timestamp, visual='witch', *, match='m1', owner='opponent',
                x=20., origin='unknown'):
    return {'observation_id': identity, 'match_id': match, 'timestamp': timestamp,
            'visual_class': 'visual.unit.' + visual, 'bbox': [x, 20., x + 20., 50.],
            'owner': owner, 'form': 'unknown', 'origin_kind': origin,
            'source': 'katacr_prediction', 'confidence': .8}


def stream_for(observations, *, frame_times=None):
    if frame_times is None:
        frame_times = {'m1': [0., 31.5, 34., 49., 55., 75.5, 78., 80.5,
                              102.5, 105., 116., 118.5, 124., 130., 180.],
                       'm4': [0., 65., 69., 75., 80.]}
    for row in observations:
        frame_times.setdefault(row['match_id'], []).append(row['timestamp'])
    frames = [{'match_id': match, 'timestamp': timestamp, 'sample_index': index}
              for match, times in frame_times.items()
              for index, timestamp in enumerate(sorted(set(times)))]
    indices = {(frame['match_id'], frame['timestamp']): frame['sample_index'] for frame in frames}
    labels = {'flying_machine': 'flying-machine', 'golden_knight': 'golden-knight',
              'royal_hog': 'royal-hog'}
    bindings = []
    for row in observations:
        short = row['visual_class'].removeprefix('visual.unit.')
        owner = row['owner']
        bindings.append({'observation_id': row['observation_id'], 'match_id': row['match_id'],
                         'timestamp': row['timestamp'], 'sample_index': indices[(row['match_id'], row['timestamp'])],
                         'excluded_identical_box': False,
                         'raw_prediction': {'class': labels.get(short, short),
                                            'owner_prediction': owner,
                                            'owner_channel': {'own': 0, 'opponent': 1}.get(owner),
                                            'confidence': row['confidence'],
                                            'bbox_xyxy_original': row['bbox']},
                         'uncertainty': {'owner_channel_consistent': owner != 'unknown'}})
    return {'schema': 'detector_visual_stream_v1', 'observations': observations,
            'frames': frames, 'bindings': bindings}


def report_for(observations, *, frame_times=None):
    stream = stream_for(observations, frame_times=frame_times)
    result = replay(observations)
    gt = truth()
    scoring = evaluate(result['events'], gt)
    return build(stream, result, scoring, gt)


def positive(report, card):
    return next(row for row in report['positives'] if row['card_id'] == card)


def codes(row):
    return {item['code'] for item in row['miss_diagnosis']}


def test_preserves_exact_frozen_hit_and_actual_confirmation_delay():
    report = report_for([observation('a', 32.), observation('b', 34.5)])
    witch = positive(report, 'witch')
    assert witch['hit'] is True
    assert witch['first_appearance_delay'] == .5
    assert witch['confirmation_delay'] == 3.
    assert witch['score_outcome'] == 'hit'
    assert witch['raw_class_prediction_count'] == 1
    assert witch['engine_owner_distribution'] == {'opponent': 1}
    assert witch['miss_diagnosis'] == []
    assert report['positive_hits'] == 1 and report['positive_total'] == 5
    assert report['limitations']['real_time_latency_validated'] is False


@pytest.mark.parametrize('owner', ['own', 'unknown'])
def test_owner_guard_is_reported_as_inference_without_box_verified_model_claim(owner):
    report = report_for([observation('a', 32., owner=owner), observation('b', 33., owner=owner)])
    witch = positive(report, 'witch')
    assert witch['hit'] is False
    assert witch['raw_class_prediction_count'] == 2
    assert witch['engine_owner_distribution'] == {owner: 2}
    assert witch['related_candidates'][0]['evidence_level'] == 'WEAK'
    assert witch['related_candidates'][0]['reason'] == 'owner_origin_or_mapping_guard'
    assert 'owner_guard' in codes(witch)
    assert all(item['inference_only'] for item in witch['miss_diagnosis'])
    assert report['limitations']['gt_box_model_validation_performed'] is False


def test_single_direct_prediction_cannot_be_reported_as_confirmed_play():
    witch = positive(report_for([observation('a', 32.)]), 'witch')
    assert witch['hit'] is False
    assert witch['related_candidates'][0]['evidence_level'] == 'MEDIUM'
    assert 'insufficient_temporal_continuity' in codes(witch)


def test_single_group_member_does_not_claim_group_card_evidence():
    minions = positive(report_for([observation('a', 117., 'minion')]), 'minions')
    assert minions['hit'] is False
    assert minions['related_candidates'][0]['new_unit_count'] == 1
    assert 'insufficient_group_or_tracking_support' in codes(minions)


def test_first_seen_before_gt_is_a_scored_miss_even_with_later_visual_support():
    witch = positive(report_for([observation('a', 31.), observation('b', 32.)]), 'witch')
    assert witch['hit'] is False
    assert witch['raw_class_prediction_count'] == 1
    assert witch['related_events'][0]['timestamp'] == 31.
    assert 'event_timestamp_outside_score_window' in codes(witch)


def test_no_target_prediction_is_only_a_possible_classification_or_visibility_gap():
    witch = positive(report_for([observation('a', 32., 'skeleton')]), 'witch')
    assert witch['hit'] is False and witch['raw_class_prediction_count'] == 0
    assert witch['other_visual_class_counts'] == {'visual.unit.skeleton': 1}
    assert 'possible_classification_or_visibility_gap' in codes(witch)
    assert all(item['inference_only'] for item in witch['miss_diagnosis'])


def test_missing_match_zero_dedupe_output_is_uncovered_not_evidence_pass():
    report = report_for([], frame_times={'m1': [0., 180.]})
    row = next(item for item in report['dedupe'] if item['candidate_id'] == 'candidate_12')
    assert row['new_event_count'] == 0
    assert row['score_outcome'] == 'pass'
    assert row['coverage']['status'] == 'missing_match'
    assert row['evidence_outcome'] == 'not_covered'
    assert row['coverage_qualified_pass'] is False
    assert report['dedupe_covered_total'] == 2


@pytest.mark.parametrize('times, expected', [([50., 54.], 'partial_span'), ([0., 40.], 'outside_span')])
def test_partial_or_outside_dedupe_span_cannot_claim_pass(times, expected):
    report = report_for([], frame_times={'m1': times, 'm4': [0., 80.]})
    row = report['dedupe'][0]
    assert row['coverage']['status'] == expected
    assert row['evidence_outcome'] == 'not_covered'
    assert row['coverage_qualified_pass'] is False


def test_covered_dedupe_uses_inclusive_frame_span_without_certifying_absence():
    report = report_for([], frame_times={'m1': [49., 55., 124., 130.], 'm4': [69., 75.]})
    assert all(row['coverage_qualified_pass'] for row in report['dedupe'])
    assert report['dedupe_covered_total'] == 3
    assert all(row['coverage']['continuous_coverage_certified'] is False for row in report['dedupe'])


def test_explicit_dedupe_emissions_are_the_only_known_no_play_false_emissions():
    report = report_for([observation('a', 49., 'golden_knight'),
                         observation('b', 50., 'golden_knight')])
    assert report['dedupe'][0]['new_event_count'] == 1
    assert report['dedupe'][0]['evidence_outcome'] == 'fail'
    assert report['known_no_play_false_emissions'] == 1
    assert report['full_timeline_fp_per_minute'] is None


def test_positive_extra_duplicate_remains_failure_even_when_scorer_lists_it_unscored():
    rows = [observation('a', 32., x=20.), observation('b', 32., x=500.),
            observation('c', 33., x=20.), observation('d', 33., x=500.)]
    report = report_for(rows)
    assert report['positive_hits'] == 1 and report['positive_duplicates'] == 1
    assert report['formal_scoring_passed'] is False
    assert len(report['positive_duplicate_events']) == 1
    duplicate = report['positive_duplicate_events'][0]
    assert duplicate['classification'] == 'positive_duplicate_failure'
    assert duplicate['also_present_in_unscored'] is True
    assert duplicate['event_id'] in report['unscored_overlap_with_positive_duplicates']
    assert report['known_no_play_false_emissions'] == 0


def test_four_unresolved_candidates_never_enter_false_negative_or_negative_counts():
    report = report_for([observation('a', 12.), observation('b', 13.)])
    assert len(report['unresolved']) == 4
    assert all(row['false_negative_counted'] is False and row['negative_evidence'] is False
               for row in report['unresolved'])
    assert report['positive_misses'] == 5
    assert report['known_no_play_false_emissions'] == 0
    assert report['unscored_events'][0]['reason'] == 'unresolved_review_window'
    assert report['full_timeline_fp_per_minute'] is None


def test_raw_duplicate_predictions_are_counted_separately_from_engine_observations():
    rows = [observation('a', 32.)]
    stream = stream_for(rows)
    duplicate = deepcopy(stream['bindings'][0])
    duplicate.update(observation_id='excluded-duplicate', excluded_identical_box=True)
    stream['bindings'].append(duplicate)
    result = replay(rows)
    gt = truth()
    report = build(stream, result, evaluate(result['events'], gt), gt)
    witch = positive(report, 'witch')
    assert witch['raw_class_prediction_count'] == 2
    assert witch['observation_count'] == 1
    assert witch['excluded_identical_raw_prediction_count'] == 1


def test_unlocatable_binding_is_disclosed_and_not_guessed_across_matches():
    stream = stream_for([])
    stream['bindings'].append({'observation_id': 'excluded-duplicate', 'sample_index': 0,
                               'excluded_identical_box': True,
                               'raw_prediction': {'class': 'witch', 'owner_prediction': 'opponent'},
                               'uncertainty': {'owner_channel_consistent': True}})
    result = replay([])
    gt = truth()
    report = build(stream, result, evaluate([], gt), gt)
    assert report['raw_binding_coverage']['unlocated_binding_count'] == 1
    assert report['raw_binding_coverage']['counts_complete'] is False
    assert all(row['raw_class_prediction_count'] == 0 for row in report['positives'])


def test_report_does_not_mutate_stream_frozen_results_scoring_or_truth():
    stream = stream_for([observation('a', 32.), observation('b', 33.)])
    result = replay(stream['observations'])
    gt = truth()
    scoring = evaluate(result['events'], gt)
    inputs = deepcopy((stream, result, scoring, gt))
    report = build(stream, result, scoring, gt)
    report['unresolved'][0]['candidate_id'] = 'changed report only'
    report['positives'][0]['matched_event_id'] = 'changed report only'
    assert (stream, result, scoring, gt) == inputs
