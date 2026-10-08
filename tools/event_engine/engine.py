"""Pure deterministic Oracle logic. No detector, file I/O or Event GT dependency."""
from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from hashlib import sha256
from itertools import groupby
import json
import math


RULE_VERSION = 'oracle-card-rules-v1'
RULES = {
    'visual.unit.witch': {'card_id': 'witch', 'kind': 'direct'},
    'visual.unit.flying_machine': {'card_id': 'flying_machine', 'kind': 'direct'},
    'visual.unit.golden_knight': {'card_id': 'golden_knight', 'kind': 'direct'},
    'visual.unit.minion': {'card_id': 'minions', 'kind': 'grouped', 'minimum_new_units': 2, 'expected_units': 3},
    'visual.unit.royal_hog': {'card_id': 'royal_hogs', 'kind': 'grouped', 'minimum_new_units': 2, 'expected_units': 4},
}
CONFIG = {'track_gap_seconds': 7.5, 'confirmation_window_seconds': 7.5,
          'minimum_iou': .05, 'center_distance_pixels': 90., 'diagonal_multiplier': 2.,
          'group_birth_window_seconds': 2.5, 'group_distance_pixels': 120.,
          'grouped_motion_pixels_per_second': 90.}


def stable_id(prefix, value):
    return prefix + sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()[:24]


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_observations(rows):
    if not isinstance(rows, list):
        raise ValueError('observation array required')
    required = {'observation_id','match_id','timestamp','visual_class','bbox','owner','form','origin_kind','source'}
    optional = {'appearance_group_id','confidence'}
    seen, human, geometry = set(), {}, set()
    for r in rows:
        if not isinstance(r, dict) or not required <= set(r) or set(r) - required - optional:
            raise ValueError('invalid observation fields')
        if any(not isinstance(r[k],str) or not r[k] or len(r[k])>200 for k in ('observation_id','match_id','visual_class','source')):
            raise ValueError('invalid observation identity')
        if r['observation_id'] in seen:
            raise ValueError('duplicate observation identity')
        seen.add(r['observation_id'])
        if not _number(r['timestamp']) or r['timestamp']<0:
            raise ValueError('invalid observation timestamp')
        b=r['bbox']
        if not isinstance(b,list) or len(b)!=4 or not all(_number(v) for v in b) or not (0<=b[0]<b[2] and 0<=b[1]<b[3]):
            raise ValueError('invalid observation bbox')
        if r['owner'] not in {'opponent','own','unknown'} or r['form'] not in {'normal','evolved','unknown'} or r['origin_kind'] not in {'primary','spawned','secondary','unknown'}:
            raise ValueError('invalid observation metadata')
        position=(r['match_id'],r['timestamp'],r['visual_class'],r['owner'],tuple(b))
        if position in geometry:
            raise ValueError('identical same-frame boxes cannot establish distinct units')
        geometry.add(position)
        if 'confidence' in r and r['confidence'] is not None and (not _number(r['confidence']) or not 0<=r['confidence']<=1):
            raise ValueError('invalid optional observation confidence')
        g=r.get('appearance_group_id')
        if g is not None:
            if not isinstance(g,str) or not g or len(g)>200 or g.startswith('unresolved-observation:'):
                raise ValueError('observation token is not a human identity')
            if r['source']!='human_gt_continuity':
                raise ValueError('appearance identity requires confirmed human continuity source')
            key=(r['match_id'],g)
            semantics=(r['visual_class'],r['owner'],r['form'],r['origin_kind'])
            if key in human and human[key]!=semantics:
                raise ValueError('contradictory human appearance group')
            human[key]=semantics


def _center(box):
    return ((box[0]+box[2])/2,(box[1]+box[3])/2)


def _distance(a,b):
    return math.dist(_center(a),_center(b))


def _iou(a,b):
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection
    return intersection/union


@dataclass
class Track:
    track_id: str
    rows: list[dict] = field(default_factory=list)
    group: str | None = None

    @property
    def first(self): return self.rows[0]
    @property
    def last(self): return self.rows[-1]
    @property
    def human(self): return self.first.get('appearance_group_id')


@dataclass
class GroupedCardEpisode:
    episode_id: str
    card_id: str
    owner: str
    member_track_ids: list[str]
    first_seen: float
    last_seen: float
    emitted_event_id: str
    state: str = 'active'


def _association(track, row):
    a=track.last
    if any(a[k]!=row[k] for k in ('match_id','visual_class','owner','form','origin_kind')):
        return None
    human=row.get('appearance_group_id')
    if track.human or human:
        return (0,0.,0.) if track.human==human else None
    gap=row['timestamp']-a['timestamp']
    if not 0<gap<=CONFIG['track_gap_seconds']:
        return None
    iou=_iou(a['bbox'],row['bbox']); distance=_distance(a['bbox'],row['bbox'])
    diagonal=max(math.hypot(b[2]-b[0],b[3]-b[1]) for b in (a['bbox'],row['bbox']))
    budget=max(CONFIG['center_distance_pixels'],CONFIG['diagonal_multiplier']*diagonal)
    rule=RULES.get(row['visual_class'])
    if rule and rule['kind']=='grouped':
        # Sampling gap bounds motion, not time since a card event. Existing
        # tracks remain one-to-one; exhausted tracks cannot absorb new units.
        budget=max(budget,CONFIG['grouped_motion_pixels_per_second']*gap)
    if iou>=CONFIG['minimum_iou'] or distance<=budget:
        return (1,-iou,distance)
    return None


def _eligible(row):
    return row['owner']=='opponent' and row['origin_kind'] not in {'spawned','secondary'} and row['visual_class'] in RULES


def _direct_identity(track):
    return stable_id('appearance-', [track.first['match_id'],track.human]) if track.human else track.track_id


def replay(observations):
    """Replay all observations; timestamps are first-seen, not confirmation latency.

    Human IDs are trusted continuity input supplied only by the separate adapter.
    No birth/absence proof is claimed for an initially already-visible track.
    """
    validate_observations(observations)
    ordered=sorted(observations,key=lambda r:(r['match_id'],r['timestamp'],r['observation_id']))
    tracks, groups, confirmation, episodes = [], {}, {}, {}
    for (match,time), frame_iter in groupby(ordered,key=lambda r:(r['match_id'],r['timestamp'])):
        frame=list(frame_iter); used_tracks=set(); used_rows=set()
        edges=[]
        for ti,track in enumerate(tracks):
            for ri,row in enumerate(frame):
                score=_association(track,row)
                if score is not None:
                    edges.append((score,track.track_id,row['observation_id'],ti,ri))
        for _,_,_,ti,ri in sorted(edges):
            if ti in used_tracks or ri in used_rows: continue
            tracks[ti].rows.append(frame[ri]); used_tracks.add(ti); used_rows.add(ri)
        newborn=[]
        for ri,row in enumerate(frame):
            if ri not in used_rows:
                track=Track(stable_id('track-', [row['match_id'],row['observation_id']]),[row])
                tracks.append(track); newborn.append(track)
        for track in newborn:
            row=track.first; rule=RULES.get(row['visual_class'])
            if not _eligible(row) or rule['kind']!='grouped': continue
            options=[]
            for gid,members in groups.items():
                anchor=members[0].first
                same=all(anchor[k]==row[k] for k in ('match_id','visual_class','owner','form'))
                if gid in episodes:
                    # A confirmed episode owns its members. Genuinely new
                    # tracks must qualify a separate group, even immediately.
                    # A trusted shared human identity instead proves that a
                    # newly visible member already belongs to this episode.
                    if same and track.human and members[0].human==track.human:
                        options.append(gid)
                    continue
                identities=members[0].human==track.human
                if same and identities and 0<=time-anchor['timestamp']<=CONFIG['group_birth_window_seconds'] and all(_distance(m.first['bbox'],row['bbox'])<=CONFIG['group_distance_pixels'] for m in members):
                    options.append(gid)
            gid=min(options) if options else stable_id('appearance-', [row['match_id'],row['observation_id']])
            groups.setdefault(gid,[]).append(track); track.group=gid
        # A broken single-unit track is not independent entity evidence. Only
        # simultaneous distinct boxes/tracks can confirm this Oracle group.
        for gid,members in groups.items():
            if members[0].first['match_id']!=match: continue
            rule=RULES[members[0].first['visual_class']]
            visible=sum(t.last['timestamp']==time for t in members)
            if gid not in episodes and visible>=rule['minimum_new_units']:
                confirmation.setdefault(gid,time)
                episodes[gid]=GroupedCardEpisode(
                    gid,rule['card_id'],members[0].first['owner'],
                    [t.track_id for t in members],members[0].first['timestamp'],time,
                    stable_id('event-',[RULE_VERSION,match,gid]))
            if gid in episodes:
                episode=episodes[gid]
                episode.member_track_ids=[t.track_id for t in members]
                episode.last_seen=max(t.last['timestamp'] for t in members)
                episode.state=('active' if visible else 'occluded'
                               if time-episode.last_seen<=CONFIG['track_gap_seconds'] else 'closed')
        for track in tracks:
            row=track.first; rule=RULES.get(row['visual_class'])
            if not _eligible(row) or rule['kind']!='direct': continue
            distinct={r['timestamp'] for r in track.rows if r['timestamp']-row['timestamp']<=CONFIG['confirmation_window_seconds']}
            if track.human or len(distinct)>=2:
                confirmation.setdefault(_direct_identity(track),time)
    events, candidates=[] , []
    identity_members={}
    for track in tracks:
        row=track.first; rule=RULES.get(row['visual_class'])
        if track.group: continue
        gid=_direct_identity(track)
        identity_members.setdefault(gid,[]).append(track)
    for gid,members in identity_members.items():
        row=members[0].first;rule=RULES.get(row['visual_class'])
        level='STRONG' if gid in confirmation else 'MEDIUM' if _eligible(row) else 'WEAK'
        candidates.append(_candidate(gid,members,rule,level,confirmation.get(gid)))
    for gid,members in sorted(groups.items()):
        candidates.append(_candidate(gid,members,RULES[members[0].first['visual_class']],
                                     'STRONG' if gid in confirmation else 'MEDIUM',confirmation.get(gid)))
    for c in candidates:
        if c['evidence_level']!='STRONG': continue
        events.append({key:c[key] for key in ('match_id','card_id','timestamp','confirmed_at','form','evidence_level',
                                             'source_observation_ids','source_appearance_groups','rule_version')} |
                      {'event_id':stable_id('event-', [RULE_VERSION,c['match_id'],c['candidate_id']])})
    key=lambda r:(r['match_id'],r['timestamp'],r.get('event_id',r.get('candidate_id')))
    events.sort(key=key); candidates.sort(key=key)
    return {'schema':'oracle_event_replay_v1','rule_version':RULE_VERSION,'config':dict(CONFIG),
            'registry':deepcopy(RULES),'events':events,'candidates':candidates,
            'tracks':[{'track_id':t.track_id,'appearance_group_id':t.human,'spawn_group_id':t.group,
                       'observation_ids':[r['observation_id'] for r in t.rows],
                       'first_seen':t.first['timestamp'],'last_seen':t.last['timestamp']} for t in tracks],
            'grouped_episodes':[dict(episode_id=e.episode_id,card_id=e.card_id,owner=e.owner,
                                    member_track_ids=list(e.member_track_ids),first_seen=e.first_seen,
                                    last_seen=e.last_seen,emitted_event_id=e.emitted_event_id,state=e.state)
                                for e in sorted(episodes.values(),key=lambda e:e.episode_id)],
            'limitations':{'offline_retrospective':True,'onset_proven':False,'detector_performance':False,
                           'cross_match_validation':False,'unobserved_is_negative':False}}


def _candidate(gid, tracks, rule, level, confirmed_at):
    rows=sorted([r for t in tracks for r in t.rows],key=lambda r:(r['timestamp'],r['observation_id']))
    first=rows[0]
    return {'candidate_id':gid,'match_id':first['match_id'],'card_id':None if rule is None else rule['card_id'],
            'timestamp':first['timestamp'],'confirmed_at':confirmed_at,'form':first['form'],
            'owner':first['owner'],'evidence_level':level,'rule_version':RULE_VERSION,
            'kind':None if rule is None else rule['kind'],'new_unit_count':len(tracks),
            'expected_units':None if rule is None else rule.get('expected_units'),
            'source_observation_ids':[r['observation_id'] for r in rows],
            'source_appearance_groups':sorted({t.human or t.group or t.track_id for t in tracks}),
            'reason':'qualified_continuity_or_new_group' if level=='STRONG' else
                     'insufficient_continuity_or_units' if level=='MEDIUM' else 'owner_origin_or_mapping_guard'}
