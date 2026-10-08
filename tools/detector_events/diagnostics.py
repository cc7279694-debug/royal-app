"""Post-score evidence diagnostics, never an engine input or a replacement scorer.

The supplied stream/replay/evaluation/GT are previously validated snapshots.
Frame endpoints describe the sampled input span, not certified absence time.
No pixels or files are opened, and all inputs remain unchanged.
"""
from collections import Counter
from copy import deepcopy

from .adapter import LABELS


def _distribution(values):
    return dict(sorted(Counter(values).items()))


def _coverage(frames, match_id, start, end):
    times = sorted(frame['timestamp'] for frame in frames if frame['match_id'] == match_id)
    first, last = (times[0], times[-1]) if times else (None, None)
    spans = bool(times) and first <= start and end <= last
    status = ('missing_match' if not times else 'covered_span' if spans else
              'outside_span' if last < start or first > end else 'partial_span')
    return {'match_id': match_id, 'window_start': start, 'window_end': end,
            'first_frame': first, 'last_frame': last, 'status': status,
            'sampled_span_contains_window': spans,
            'frames_in_window': sum(start <= time <= end for time in times),
            'continuous_coverage_certified': False}


def _raw_rows(stream, observations):
    rows, unlocated = [], []
    for binding in stream['bindings']:
        raw = binding['raw_prediction']
        observation = observations.get(binding['observation_id'])
        match = binding.get('match_id', observation['match_id'] if observation else None)
        timestamp = binding.get('timestamp', observation['timestamp'] if observation else None)
        if match is None or timestamp is None:
            possible = [frame for frame in stream['frames']
                        if frame['sample_index'] == binding['sample_index']
                        and (match is None or frame['match_id'] == match)]
            if len(possible) == 1:
                match, timestamp = possible[0]['match_id'], possible[0]['timestamp']
        if match is None or timestamp is None:
            unlocated.append(binding['observation_id'])
            continue
        label = raw['class']
        visual = (observation['visual_class'] if observation else
                  LABELS.get(label, 'visual.other.' + label.replace('-', '_')))
        consistent = binding.get('uncertainty', {}).get('owner_channel_consistent') is True
        raw_owner = raw.get('owner_prediction') or 'missing'
        engine_owner = (observation['owner'] if observation else
                        raw_owner if consistent and raw_owner in {'opponent', 'own'} else 'unknown')
        rows.append({'observation_id': binding['observation_id'], 'match_id': match,
                     'timestamp': timestamp, 'visual_class': visual,
                     'raw_owner': raw_owner, 'engine_owner': engine_owner,
                     'excluded_identical_box': binding.get('excluded_identical_box') is True})
    return rows, {'located_binding_count': len(rows), 'unlocated_binding_count': len(unlocated),
                  'unlocated_observation_ids': unlocated, 'counts_complete': not unlocated}


def _window_evidence(raw_rows, observations, match_id, classes, start, end):
    in_window = [row for row in raw_rows
                 if row['match_id'] == match_id and start <= row['timestamp'] <= end]
    selected = [row for row in in_window if row['visual_class'] in classes]
    admitted = [row for row in observations.values() if row['match_id'] == match_id
                and row['visual_class'] in classes and start <= row['timestamp'] <= end]
    return {'raw_class_prediction_count': len(selected), 'observation_count': len(admitted),
            'raw_owner_distribution': _distribution(row['raw_owner'] for row in selected),
            'engine_owner_distribution': _distribution(row['engine_owner'] for row in selected),
            'excluded_identical_raw_prediction_count': sum(row['excluded_identical_box'] for row in selected),
            'other_visual_class_counts': _distribution(row['visual_class'] for row in in_window
                                                       if row['visual_class'] not in classes)}, admitted


def _related_candidates(result, match_id, card_id, admitted, start, end):
    identities = {row['observation_id'] for row in admitted}
    related = [row for row in result['candidates']
               if row['match_id'] == match_id and row['card_id'] == card_id
               and (start <= row['timestamp'] <= end
                    or identities.intersection(row['source_observation_ids']))]
    keys = ('candidate_id', 'timestamp', 'confirmed_at', 'owner', 'kind', 'evidence_level',
            'reason', 'new_unit_count', 'expected_units', 'source_observation_ids')
    return [{key: deepcopy(row[key]) for key in keys} for row in related]


def _miss_diagnosis(positive, admitted, raw_counts_complete):
    if positive['hit']:
        return []
    diagnoses = []

    def note(code, detail):
        diagnoses.append({'code': code, 'inference_only': True, 'detail': detail})

    if not positive['coverage']['sampled_span_contains_window']:
        note('prediction_sampling_does_not_span_score_window',
             'Missing/partial input span prevents assigning this miss to model quality.')
    if not raw_counts_complete:
        note('raw_binding_location_incomplete',
             'Some raw predictions cannot be assigned to a match/time; counts are incomplete.')
    if positive['raw_class_prediction_count'] == 0 and raw_counts_complete:
        note('possible_classification_or_visibility_gap',
             'No target-class raw prediction in this window; no GT-box correspondence was checked.')
    if admitted and not any(row['owner'] == 'opponent' for row in admitted):
        note('owner_guard', 'All admitted target observations are own/unknown; owner truth is unvalidated.')
    if admitted and any(row['owner'] == 'opponent' for row in admitted) and not any(
            row['owner'] == 'opponent' and row['origin_kind'] not in {'spawned', 'secondary'}
            for row in admitted):
        note('origin_guard', 'Explicit spawned/secondary observations are guarded; no spawn truth was checked.')
    for candidate in positive['related_candidates']:
        if candidate['evidence_level'] == 'MEDIUM':
            code = ('insufficient_group_or_tracking_support' if candidate['kind'] == 'grouped'
                    else 'insufficient_temporal_continuity')
            if not any(item['code'] == code for item in diagnoses):
                note(code, 'The frozen candidate lacks STRONG confirmation; the physical deployment cause is unresolved.')
    if any(not positive['score_window_start'] <= row['timestamp'] <= positive['score_window_end']
           for row in positive['related_events']):
        note('event_timestamp_outside_score_window',
             'Related engine first-seen time is outside the fixed match window; exact onset is not established.')
    if not diagnoses:
        note('unresolved_class_owner_tracking_or_timing_cause',
             'Supplied metadata does not establish one root cause; visual GT boxes were not evaluated.')
    return diagnoses


def build_diagnostics(stream: dict, result: dict, evaluation: dict, gt: dict) -> dict:
    """Explain sealed frozen scoring using raw input and engine evidence only.

    GT is read here only after scoring; it supplies evaluation identities/windows.
    This function neither replays predictions nor changes the supplied score.
    """
    observations = {row['observation_id']: row for row in stream['observations']}
    raw_rows, raw_coverage = _raw_rows(stream, observations)
    classes = {}
    for visual, rule in result['registry'].items():
        classes.setdefault(rule['card_id'], set()).add(visual)
    truth = {row['event_gt_id']: row for row in gt['confirmed_events']}
    positives, positive_window_ids = [], set()
    chosen = {row['matched_event_id'] for row in evaluation['positives'] if row['matched_event_id'] is not None}
    for scored in evaluation['positives']:
        row = deepcopy(scored)
        match = truth[row['event_gt_id']]['underlying_match_id']
        start = row['gt_timestamp'] + evaluation['hit_window_seconds'][0]
        end = row['gt_timestamp'] + evaluation['hit_window_seconds'][1]
        details, admitted = _window_evidence(raw_rows, observations, match,
                                             classes.get(row['card_id'], set()), start, end)
        candidates = _related_candidates(result, match, row['card_id'], admitted, start, end)
        identities = {identity for candidate in candidates for identity in candidate['source_observation_ids']}
        related_events = [deepcopy(event) for event in result['events']
                          if event['match_id'] == match and event['card_id'] == row['card_id']
                          and (start <= event['timestamp'] <= end
                               or identities.intersection(event['source_observation_ids']))]
        positive_window_ids.update(event['event_id'] for event in related_events
                                   if start <= event['timestamp'] <= end)
        row.update(details, match_id=match, score_outcome='hit' if row['hit'] else 'miss',
                   score_window_start=start, score_window_end=end,
                   coverage=_coverage(stream['frames'], match, start, end),
                   related_candidates=candidates, related_events=related_events)
        row['miss_diagnosis'] = _miss_diagnosis(row, admitted, raw_coverage['counts_complete'])
        positives.append(row)

    dedupe = []
    matches = {row['candidate_id']: row['underlying_match_id'] for row in gt['continuity_dedupe_outcomes']}
    for scored in evaluation['dedupe_outcomes']:
        row = deepcopy(scored)
        match, start, end = matches[row['candidate_id']], row['start_seconds'], row['end_seconds']
        coverage = _coverage(stream['frames'], match, start, end)
        details, _ = _window_evidence(raw_rows, observations, match, classes.get(row['card_id'], set()), start, end)
        qualifies = coverage['sampled_span_contains_window'] and row['new_event_count'] == 0
        row.update(details, match_id=match, coverage=coverage,
                   score_outcome='pass' if row['new_event_count'] == 0 else 'fail',
                   evidence_outcome=('fail' if row['new_event_count'] else 'pass' if qualifies else 'not_covered'),
                   coverage_qualified_pass=qualifies)
        dedupe.append(row)

    unscored = deepcopy(evaluation['unscored_events'])
    unscored_ids = {row['event_id'] for row in unscored}
    duplicate_ids = positive_window_ids - chosen
    duplicates = [{**deepcopy(event), 'classification': 'positive_duplicate_failure',
                   'also_present_in_unscored': event['event_id'] in unscored_ids}
                  for event in result['events'] if event['event_id'] in duplicate_ids]
    unresolved = [{**deepcopy(row), 'scoring_role': 'unresolved_non_evaluable',
                   'false_negative_counted': False, 'negative_evidence': False,
                   'unscored_event_ids': [event['event_id'] for event in unscored
                                          if row['candidate_id'] in event['unresolved_candidates']]}
                  for row in gt['unresolved_candidates']]
    return {'schema': 'detector_event_diagnostics_v1', 'positives': positives, 'dedupe': dedupe,
            'positive_hits': evaluation['positive_hits'], 'positive_total': evaluation['positive_total'],
            'positive_misses': evaluation['positive_total'] - evaluation['positive_hits'],
            'positive_duplicates': evaluation['positive_duplicates'], 'positive_duplicate_events': duplicates,
            'dedupe_covered_total': sum(row['coverage']['sampled_span_contains_window'] for row in dedupe),
            'dedupe_total': len(dedupe), 'unresolved': unresolved, 'unscored_events': unscored,
            'unscored_overlap_with_positive_duplicates': sorted(unscored_ids & duplicate_ids),
            'known_no_play_false_emissions': evaluation['explicit_dedupe_failures'],
            'full_timeline_fp_per_minute': None, 'formal_scoring_passed': evaluation['passed'],
            'coverage_qualified_passed': evaluation['passed'] and all(row['coverage_qualified_pass'] for row in dedupe),
            'raw_binding_coverage': raw_coverage,
            'limitations': {'post_score_only': True, 'gt_box_model_validation_performed': False,
                            'miss_causes_are_inferences': True, 'owner_is_unvalidated_prediction': True,
                            'frame_span_is_not_absence_certification': True, 'unresolved_is_negative': False,
                            'real_time_latency_validated': False, 'cross_match_positive_validation': False}}
