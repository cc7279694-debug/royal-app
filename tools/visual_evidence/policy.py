"""Online experimental visual evidence; track/cohort IDs never become human GT.

The whitelist projection feeds the immutable engine. Everything richer remains
in this diagnostic sidecar; a candidate cohort is never a confirmed card play.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import math

from tools.event_engine.engine import stable_id, validate_observations


POLICY_VERSION = 'visual-evidence-policy-v1'
POLICY = {
    'version': POLICY_VERSION,
    'owner_history_frames': 3,
    'owner_consensus': 'unanimous_last_three_distinct_sampled_observations',
    'unknown_history_breaks_consensus': True,
    'group_birth_window_seconds': 2.5,
    'group_distance_pixels': 120.,
    'reacquisition_context_gap_seconds': .5,
    'jump_context_distance_pixels': 90.,
    'jump_context_diagonal_multiplier': 2.,
    'jump_context_motion_pixels_per_second': 90.,
    'region_and_motion_decide_owner': False,
    'event_emission': False,
}
GROUPED = {'visual.unit.minion': ('minions', 3),
           'visual.unit.royal_hog': ('royal_hogs', 4)}
VISUAL_FIELDS = {'observation_id', 'match_id', 'timestamp', 'visual_class',
                 'bbox', 'owner', 'form', 'origin_kind', 'source', 'confidence'}


@dataclass
class EvidenceTrack:
    first: dict
    last: dict | None = None
    history: list[tuple[str, str]] = field(default_factory=list)
    confirmation_timestamp: float | None = None


def _center(box):
    return [(box[0] + box[2]) / 2., (box[1] + box[3]) / 2.]


def _region(box, dimensions):
    if dimensions is None:
        return None
    middle = dimensions[1] / 2.
    return 'upper' if box[3] <= middle else 'lower' if box[1] >= middle else 'crosses_midline'


def _context(track, row, dimensions):
    initial = track.first
    relative = ([initial['bbox'][i] / dimensions[i % 2] for i in range(4)]
                if dimensions is not None else None)
    start_region = _region(initial['bbox'], dimensions)
    current_region = _region(row['bbox'], dimensions)
    gap, velocity, jump = None, None, False
    if track.last is not None:
        gap = row['timestamp'] - track.last['timestamp']
        before, now = _center(track.last['bbox']), _center(row['bbox'])
        velocity = [(now[i] - before[i]) / gap for i in range(2)]
        diagonal = max(math.hypot(b[2] - b[0], b[3] - b[1])
                       for b in (track.last['bbox'], row['bbox']))
        budget = max(POLICY['jump_context_distance_pixels'],
                     POLICY['jump_context_diagonal_multiplier'] * diagonal,
                     POLICY['jump_context_motion_pixels_per_second'] * gap)
        jump = math.dist(before, now) > budget
    return {'first_bbox_relative': relative, 'initial_region': start_region,
            'current_region': current_region,
            'region_crossing': start_region in {'upper', 'lower'}
            and current_region in {'upper', 'lower'} and start_region != current_region,
            'observed_gap_seconds': gap, 'velocity_pixels_per_second': velocity,
            'contradictory_jump_context': jump,
            'reacquisition_context': gap is not None
            and gap > POLICY['reacquisition_context_gap_seconds'],
            'context_is_owner_truth': False}


def _owner(row, association, track):
    if association['track_id'] is None:
        return 'unknown', 'unassigned_track'
    if association['association_ambiguous']:
        track.history.clear()
        return 'unknown', 'association_ambiguous'
    track.history.append((row['observation_id'], row['owner']))
    track.history[:] = track.history[-POLICY['owner_history_frames']:]
    votes = [owner for _, owner in track.history]
    if row['owner'] == 'unknown':
        return 'unknown', 'raw_owner_unknown'
    if {'own', 'opponent'} <= set(votes):
        return 'unknown', 'conflicting_owner_predictions'
    if 'unknown' in votes:
        return 'unknown', 'unknown_owner_history'
    if len(votes) < POLICY['owner_history_frames']:
        return 'unknown', 'insufficient_owner_history'
    if track.confirmation_timestamp is None:
        track.confirmation_timestamp = row['timestamp']
    return votes[0], 'unanimous_owner_predictions'


def _group_member(track_id, track, row, owner, reason, groups, memberships):
    """One membership per algorithmic track, with conservative conflict flags."""
    visual = row['visual_class']
    if visual not in GROUPED:
        return
    key = (row['match_id'], track_id)
    member = memberships.setdefault(key, {
        'match_id': row['match_id'], 'track_id': track_id,
        'first_seen_timestamp': track.first['timestamp'],
        'group_id': None, 'status': 'UNRESOLVED', 'reason': reason,
        'compatible_group_ids': [], 'membership_is_physical_truth': False})
    if member['group_id'] is not None:
        if owner == 'unknown':
            member.update(status='UNRESOLVED', reason=reason)
            group = next(g for g in groups if g['group_id'] == member['group_id'])
            group['status'] = 'UNRESOLVED'
            group['uncertainty_reasons'] = sorted(set(group['uncertainty_reasons']) | {reason})
        return
    if owner == 'unknown':
        member.update(status='UNRESOLVED', reason=reason)
        return
    compatible = [g for g in groups if g['match_id'] == row['match_id']
                  and g['visual_class'] == visual
                  and abs(track.first['timestamp'] - g['anchor_first_seen_timestamp'])
                  <= POLICY['group_birth_window_seconds']
                  and math.dist(_center(track.first['bbox']), _center(g['anchor_bbox']))
                  <= POLICY['group_distance_pixels']]
    member['compatible_group_ids'] = sorted(g['group_id'] for g in compatible)
    if any(g['owner'] != owner for g in compatible):
        member.update(status='UNRESOLVED', reason='cohort_owner_conflict')
        for group in compatible:
            group['status'] = 'UNRESOLVED'
            group['uncertainty_reasons'] = sorted(set(group['uncertainty_reasons']) | {'cohort_owner_conflict'})
        return
    if len(compatible) > 1:
        member.update(status='UNRESOLVED', reason='multiple_compatible_cohorts')
        for group in compatible:
            group['status'] = 'UNRESOLVED'
            group['uncertainty_reasons'] = sorted(set(group['uncertainty_reasons']) | {'multiple_compatible_cohorts'})
        return
    if compatible:
        group = compatible[0]
        if group['status'] == 'UNRESOLVED':
            member.update(status='UNRESOLVED', reason='compatible_cohort_unresolved')
            return
        if len(group['member_track_ids']) >= group['expected_units']:
            member.update(status='UNRESOLVED', reason='compatible_cohort_at_capacity')
            return
        births = list(group['member_first_seen'].values()) + [track.first['timestamp']]
        if max(births) - min(births) > POLICY['group_birth_window_seconds']:
            member.update(status='UNRESOLVED', reason='cohort_birth_span_exceeded')
            return
        reason = 'single_compatible_cohort'
    else:
        card_id, expected = GROUPED[visual]
        group = {'group_id': stable_id('candidate-cohort-', [POLICY_VERSION,
                         row['match_id'], visual, track_id]),
                 'match_id': row['match_id'], 'visual_class': visual, 'card_id': card_id,
                 'owner': owner, 'first_seen_timestamp': track.first['timestamp'],
                 'anchor_first_seen_timestamp': track.first['timestamp'],
                 'anchor_track_id': track_id, 'member_first_seen': {},
                 'anchor_bbox': deepcopy(track.first['bbox']), 'expected_units': expected,
                 'member_track_ids': [], 'status': 'CANDIDATE', 'uncertainty_reasons': [],
                 'confirmed_card_play': False, 'membership_is_physical_truth': False}
        groups.append(group)
        reason = 'separate_unconfirmed_cohort'
    group['member_track_ids'] = sorted(group['member_track_ids'] + [track_id])
    group['member_first_seen'][track_id] = track.first['timestamp']
    group['member_first_seen'] = dict(sorted(group['member_first_seen'].items()))
    group['first_seen_timestamp'] = min(group['member_first_seen'].values())
    member.update(group_id=group['group_id'], status='ASSOCIATED', reason=reason)


def _bindings(observations, associations):
    if not isinstance(associations, list):
        raise ValueError('association bindings must be an array')
    bindings = {}
    for item in associations:
        if (not isinstance(item, dict)
                or set(item) != {'observation_id', 'track_id', 'association_ambiguous'}
                or not isinstance(item['observation_id'], str)
                or item['observation_id'] in bindings
                or type(item['association_ambiguous']) is not bool
                or item['track_id'] is not None and (
                    not isinstance(item['track_id'], str) or not item['track_id']
                    or len(item['track_id']) > 200)):
            raise ValueError('invalid association bindings')
        bindings[item['observation_id']] = item
    if set(bindings) != {r['observation_id'] for r in observations}:
        raise ValueError('association bindings must match observations exactly')
    track_frames, track_classes = set(), {}
    for row in observations:
        tid = bindings[row['observation_id']]['track_id']
        if tid is None:
            continue
        frame = (row['match_id'], tid, row['timestamp'])
        if frame in track_frames:
            raise ValueError('one observation per track and timestamp required')
        track_frames.add(frame)
        key = (row['match_id'], tid)
        if key in track_classes and track_classes[key] != row['visual_class']:
            raise ValueError('track visual class must stay consistent')
        track_classes[key] = row['visual_class']
    return bindings


def run_policy(observations, associations, *, source_dimensions_wh=None):
    """Consume only observations and algorithmic associations, in causal order.

    Unknown history interrupts consensus. Screen region/motion annotate context
    only. First confirmation is owner evidence, not a deployment timestamp.
    """
    validate_observations(observations)
    if any('appearance_group_id' in r or r['source'] == 'human_gt_continuity'
           for r in observations):
        raise ValueError('experimental policy cannot consume human identity')
    dimensions = source_dimensions_wh or {}
    if not isinstance(dimensions, dict) or any(
            not isinstance(match, str) or not isinstance(size, (list, tuple))
            or len(size) != 2 or any(type(v) is not int or v <= 0 for v in size)
            for match, size in dimensions.items()):
        raise ValueError('invalid source dimensions')
    bindings = _bindings(observations, associations)
    tracks, projected, evidence, groups, memberships = {}, [], [], [], {}
    ordered = sorted(observations, key=lambda r: (r['match_id'], r['timestamp'], r['observation_id']))
    for row in ordered:
        association = bindings[row['observation_id']]
        tid = association['track_id']
        track = (tracks.setdefault((row['match_id'], tid), EvidenceTrack(deepcopy(row)))
                 if tid is not None else EvidenceTrack(deepcopy(row)))
        owner, reason = _owner(row, association, track)
        context = _context(track, row, dimensions.get(row['match_id']))
        output = {key: deepcopy(value) for key, value in row.items() if key in VISUAL_FIELDS}
        output.update(owner=owner, source='katacr_bytetrack_shadow')
        projected.append(output)
        evidence.append({'observation_id': row['observation_id'], 'match_id': row['match_id'],
                         'timestamp': row['timestamp'], 'track_id': tid,
                         'association_ambiguous': association['association_ambiguous'],
                         'raw_owner': row['owner'], 'owner': owner, 'owner_reason': reason,
                         'history_observation_ids': [oid for oid, _ in track.history],
                         'history_votes': [vote for _, vote in track.history],
                         'first_seen_timestamp': track.first['timestamp'],
                         'confirmation_timestamp': track.confirmation_timestamp,
                         **context})
        if tid is not None:
            _group_member(tid, track, row, owner, reason, groups, memberships)
        track.last = deepcopy(row)
    # Valid original fields and IDs remain intact. Opposite raw owners on exact
    # same-frame geometry can both abstain to unknown; keep both evidence rows.
    # The separate engine adapter must canonically exclude duplicate geometry
    # and record every exclusion before unchanged 3B validates that projection.
    return {'schema': 'experimental_visual_evidence_v1', 'config': deepcopy(POLICY),
            'observations': projected, 'owner_evidence': evidence,
            'groups': sorted(groups, key=lambda g: (g['match_id'], g['first_seen_timestamp'], g['group_id'])),
            'group_membership': [memberships[k] for k in sorted(memberships)],
            'limitations': {'experimental': True, 'online_causal_evidence': True,
                            'physical_identity_proven': False, 'owner_is_prediction': True,
                            'owner_probability_available': False, 'onset_proven': False,
                            'engine_projection_requires_geometry_validation': True,
                            'unobserved_is_negative': False, 'confirmed_card_plays': 0,
                            'human_identity_used': False, 'production_replacement': False}}
