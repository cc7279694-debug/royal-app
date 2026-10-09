"""GT-free experimental cohort reasoning beside, never inside, the frozen engine.

All output events are PROVISIONAL observations, not OpponentCardPlayed truth.
The frame list describes sampling coverage, not verified physical absence.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import math

from tools.event_engine.engine import CONFIG, replay, stable_id, validate_observations


POLICY_VERSION = 'deployment-spawn-shadow-v1'
POLICY = {
    'version': POLICY_VERSION,
    'baseline_config': dict(CONFIG),
    'first_cohort': 'baseline_qualified_provisional',
    'nearby_within_birth_window': 'possible_late_member_unresolved',
    'other_overlap': 'unresolved_without_positive_separation',
    'separate_cohort': 'all_new_births_beyond_all_recent_member_motion_budgets',
    'sampled_absence': 'last_two_prior_sampled_frames_after_old_last_seen_no_same_class',
    'absence_final_gap_seconds': CONFIG['group_birth_window_seconds'],
    'absence_sample_gap_seconds': CONFIG['track_gap_seconds'],
    'absence_is_physical_proof': False,
    'expected_count_is_capacity_rule': False,
    'identity_conflict': 'overlapping_conflicting_metadata_within_birth_window',
    'identity_conflict_scope': 'all_candidate_source_observations_offline_retrospective',
    'timestamp_policy': 'unchanged_original_first_seen',
    'estimated_deployment_timestamp': None,
    'production_replacement': False,
}
FRAME_FIELDS = {'match_id', 'timestamp', 'sample_index', 'raw_pts', 'time_base',
                'prediction_count'}


def _validate_inputs(observations, frames):
    validate_observations(observations)
    if any('appearance_group_id' in r or r['source'] not in {
            'katacr_prediction', 'synthetic_observation'} for r in observations):
        raise ValueError('Shadow requires detector observations without human/GT identity')
    if not isinstance(frames, list):
        raise ValueError('sampled frame array required')
    keys = set()
    for frame in frames:
        if (not isinstance(frame, dict) or not {'match_id', 'timestamp'} <= frame.keys()
                or frame.keys() - FRAME_FIELDS):
            raise ValueError('invalid sampled frame fields; answers are not input')
        time = frame['timestamp']
        if (not isinstance(frame['match_id'], str) or not frame['match_id']
                or type(time) not in (int, float) or not math.isfinite(time) or time < 0):
            raise ValueError('invalid sampled frame identity/time')
        key = (frame['match_id'], time)
        if key in keys:
            raise ValueError('duplicate sampled frame')
        keys.add(key)
    if any((r['match_id'], r['timestamp']) not in keys for r in observations):
        raise ValueError('every observation requires an explicitly sampled frame')


def _center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def _distance(a, b):
    return math.dist(_center(a['bbox']), _center(b['bbox']))


def _overlap(a, b):
    aa, bb = a['bbox'], b['bbox']
    intersection = max(0, min(aa[2], bb[2]) - max(aa[0], bb[0])) * max(
        0, min(aa[3], bb[3]) - max(aa[1], bb[1]))
    union = (aa[2]-aa[0])*(aa[3]-aa[1]) + (bb[2]-bb[0])*(bb[3]-bb[1]) - intersection
    return intersection / union >= CONFIG['minimum_iou']


def _conflicts(rows, same_class):
    conflicts = set()
    for other in same_class:
        unsafe = (other['owner'] != 'opponent'
                  or other['origin_kind'] in {'spawned', 'secondary'}
                  or other['form'] == 'evolved')
        if not unsafe:
            continue
        if any(abs(r['timestamp'] - other['timestamp']) <= CONFIG['group_birth_window_seconds']
               and _overlap(r, other) for r in rows):
            conflicts.add(other['observation_id'])
    return sorted(conflicts)


def _references(group, birth, track_rows):
    references = []
    for track_id in group['possible_member_track_ids']:
        prior = [r for r in track_rows[track_id] if r['timestamp'] <= birth['timestamp']]
        if not prior:
            continue
        last = prior[-1]
        gap = birth['timestamp'] - last['timestamp']
        if gap > CONFIG['track_gap_seconds']:
            return None
        references.append((last, max(CONFIG['group_distance_pixels'],
                                    CONFIG['grouped_motion_pixels_per_second'] * gap)))
    return references or None


def _relation(group, births, track_rows, times, same_class):
    """Return positive observational separation, possible membership, or ambiguity."""
    comparisons = []
    all_far, all_near = True, True
    for birth in births:
        refs = _references(group, birth, track_rows)
        if refs is None:
            all_far = all_near = False
            continue
        distances = [{'old_observation_id': old['observation_id'],
                      'new_observation_id': birth['observation_id'],
                      'distance_pixels': _distance(old, birth),
                      'motion_budget_pixels': budget} for old, budget in refs]
        comparisons.extend(distances)
        all_far &= all(d['distance_pixels'] > d['motion_budget_pixels'] for d in distances)
        all_near &= any(d['distance_pixels'] <= d['motion_budget_pixels'] for d in distances)
    evidence = {'prior_group_id': group['group_id'], 'geometry': comparisons,
                'physical_absence_proven': False}
    if all_far:
        return 'spatially_separate_cohort', evidence
    first = min(r['timestamp'] for r in births)
    old_last = max(r['timestamp'] for tid in group['possible_member_track_ids']
                   for r in track_rows[tid] if r['timestamp'] <= first)
    prior_times = [t for t in times if t < first]
    if len(prior_times) >= 2:
        recent = prior_times[-2:]
        if (old_last < recent[0]
                and recent[1] - recent[0] <= CONFIG['track_gap_seconds']
                and first - recent[1] <= CONFIG['group_birth_window_seconds']
                and not any(r['timestamp'] in recent for r in same_class)):
            evidence['absence_frame_timestamps'] = recent
            return 'sampled_non_detection_not_proven_absence', evidence
    if all_near and first - group['first_seen_timestamp'] <= CONFIG['group_birth_window_seconds']:
        return 'possible_late_member', evidence
    return 'ambiguous_overlap', evidence


def _time_fields(candidate):
    return {'first_seen_timestamp': candidate['timestamp'],
            'confirmation_timestamp': candidate['confirmed_at'],
            'estimated_deployment_timestamp': None}


def run_shadow(observations, frames):
    """Return deterministic JSON data without GT, I/O, timestamp shifting or tuning.

    The original replay and every baseline candidate/event remain available.
    `events` is a provisional comparison subset only. Suppression is uncertainty,
    not a Negative label or evidence that a real second play did not happen.
    """
    _validate_inputs(observations, frames)
    baseline = replay(observations)
    by_id = {r['observation_id']: r for r in observations}
    by_class, frame_times = defaultdict(list), defaultdict(list)
    for row in sorted(observations, key=lambda r: (r['match_id'], r['timestamp'], r['observation_id'])):
        by_class[(row['match_id'], row['visual_class'])].append(row)
    for frame in sorted(frames, key=lambda f: (f['match_id'], f['timestamp'])):
        frame_times[frame['match_id']].append(frame['timestamp'])
    track_rows = {t['track_id']: [by_id[i] for i in t['observation_ids']]
                  for t in baseline['tracks']}
    observation_track = {r['observation_id']: tid for tid, rows in track_rows.items() for r in rows}
    event_by_candidate = {stable_id('event-', [baseline['rule_version'], c['match_id'],
                                              c['candidate_id']]): c['candidate_id']
                          for c in baseline['candidates']}
    baseline_events = {event_by_candidate[e['event_id']]: e for e in baseline['events']}
    candidates, events, groups, time_evidence = [], [], [], []
    for original in baseline['candidates']:
        candidate = deepcopy(original)
        rows = [by_id[i] for i in original['source_observation_ids']]
        first = rows[0]
        member_ids = sorted({observation_track[r['observation_id']] for r in rows})
        births = [track_rows[tid][0] for tid in member_ids]
        same_class = by_class[(first['match_id'], first['visual_class'])]
        baseline_event = baseline_events.get(original['candidate_id'])
        candidate.update(_time_fields(original))
        candidate.update(baseline_event_id=None if baseline_event is None else baseline_event['event_id'],
                         baseline_event=deepcopy(baseline_event), group_id=None,
                         shadow_status='UNRESOLVED', disposition='baseline_not_qualified',
                         conflict_observation_ids=_conflicts(rows, same_class),
                         not_confirmed_card_play=True)
        evidence = {'baseline_evidence_level': original['evidence_level'],
                    'physical_onset_proven': False, 'physical_absence_proven': False,
                    'comparison_uses_original_first_seen': True,
                    'card_identity_proven': False, 'unobserved_is_negative': False,
                    'separation': None, 'prior_group_relations': []}
        candidate['evidence_basis'] = evidence
        safe = (original['owner'] == 'opponent' and original['kind'] is not None
                and original['form'] != 'evolved'
                and all(r['origin_kind'] not in {'spawned', 'secondary'} for r in rows))
        if not safe:
            candidate['disposition'] = 'owner_origin_form_or_mapping_guard'
        elif candidate['conflict_observation_ids']:
            candidate['disposition'] = 'identity_conflict'
        elif baseline_event is not None:
            candidate.update(shadow_status='PROVISIONAL', disposition='baseline_qualified_provisional')
            if original['kind'] == 'grouped':
                priors = [g for g in groups if g['match_id'] == original['match_id']
                          and g['card_id'] == original['card_id']]
                relations = [(g, *_relation(g, births, track_rows,
                                            frame_times[first['match_id']], same_class)) for g in priors]
                evidence['prior_group_relations'] = [dict(e, relation=relation)
                                                     for _, relation, e in relations]
                overlaps = [(g, relation) for g, relation, _ in relations if relation in {
                    'possible_late_member', 'ambiguous_overlap'}]
                if overlaps:
                    candidate['shadow_status'] = 'UNRESOLVED'
                    late = [g for g, relation in overlaps if relation == 'possible_late_member']
                    if len(overlaps) == len(late) == 1:
                        group = late[0]
                        candidate.update(disposition='possible_late_member', group_id=group['group_id'])
                        group['possible_member_track_ids'] = sorted(set(
                            group['possible_member_track_ids']) | set(member_ids))
                        group['uncertain_candidate_ids'].append(original['candidate_id'])
                    else:
                        candidate['disposition'] = 'ambiguous_overlap'
                else:
                    evidence['separation'] = ('initial_baseline_qualified_cohort' if not relations else
                        'sampled_non_detection_not_proven_absence' if any(
                            r == 'sampled_non_detection_not_proven_absence' for _, r, _ in relations)
                        else 'spatially_separate_cohort')
                    absence = [e['absence_frame_timestamps'] for _, _, e in relations
                               if 'absence_frame_timestamps' in e]
                    if absence:
                        evidence['absence_frame_timestamps'] = sorted({t for ts in absence for t in ts})
                    group_id = stable_id('shadow-group-', [POLICY_VERSION, original['match_id'],
                                                          original['candidate_id']])
                    candidate['group_id'] = group_id
                    groups.append({'group_id': group_id, 'match_id': original['match_id'],
                                   'card_id': original['card_id'],
                                   'first_seen_timestamp': original['timestamp'],
                                   'confirmation_timestamp': original['confirmed_at'],
                                   'estimated_deployment_timestamp': None,
                                   'baseline_event_id': baseline_event['event_id'],
                                   'core_member_track_ids': member_ids,
                                   'possible_member_track_ids': list(member_ids),
                                   'expected_units': original['expected_units'],
                                   'uncertain_candidate_ids': [], 'membership_proven': False,
                                   'shadow_status': 'PROVISIONAL', 'evidence_basis': deepcopy(evidence)})
            if candidate['shadow_status'] == 'PROVISIONAL':
                events.append(deepcopy(baseline_event) | _time_fields(original) | {
                    'shadow_status': 'PROVISIONAL', 'not_confirmed_card_play': True,
                    'group_id': candidate['group_id'], 'evidence_basis': deepcopy(evidence)})
        candidates.append(candidate)
        time_evidence.append({'candidate_id': candidate['candidate_id'],
                              'baseline_event_id': candidate['baseline_event_id'],
                              'match_id': candidate['match_id'], **_time_fields(original),
                              'comparison_timestamp': original['timestamp'],
                              'evidence_basis': deepcopy(evidence),
                              'shadow_status': candidate['shadow_status']})
    for group in groups:
        group['capacity_exceeded'] = len(group['possible_member_track_ids']) > group['expected_units']
        group['capacity_is_evidence'] = False
    return {'schema': 'deployment_spawn_shadow_v1', 'config': deepcopy(POLICY),
            'baseline_replay': baseline, 'events': events, 'candidates': candidates,
            'unresolved': [deepcopy(c) for c in candidates if c['shadow_status'] == 'UNRESOLVED'],
            'groups': groups, 'time_evidence': time_evidence,
            'limitations': {'experimental': True, 'offline_retrospective': True,
                            'production_replacement': False, 'onset_proven': False,
                            'sampled_non_detection_is_proven_absence': False,
                            'unobserved_is_negative': False, 'confirmed_card_plays': 0,
                            'detector_performance': False, 'cross_match_validation': False}}
