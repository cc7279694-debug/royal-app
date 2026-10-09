"""Mechanical diagnostics, never tracking/owner accuracy without physical GT."""
from collections import defaultdict
import math
from statistics import median

from tools.event_engine.engine import CONFIG, RULES

def _indexed(rows):
    out={r['observation_id']:r for r in rows}
    if len(out)!=len(rows): raise ValueError('duplicate observation id')
    return out

def _chains(rows, tracks):
    indexed=_indexed(rows); seen=set(); result=[]
    for track in tracks:
        chain=[]
        for oid in track['observation_ids']:
            if oid not in indexed: raise ValueError('unknown track observation')
            if oid in seen: raise ValueError('multiple track assignment')
            seen.add(oid)
            row=indexed[oid]
            if row['visual_class'] in RULES: chain.append(row)
        if chain:
            if len({(r['match_id'],r['visual_class']) for r in chain})!=1:
                raise ValueError('cross-match/class track')
            chain.sort(key=lambda r:(r['timestamp'],r['observation_id']))
            if len({r['timestamp'] for r in chain})!=len(chain):
                raise ValueError('multiple observations per track/frame')
            result.append((track['track_id'],chain))
    return result

def _center(b): return ((b[0]+b[2])/2,(b[1]+b[3])/2)

def _possible_continuation(a,b):
    gap=b['timestamp']-a['timestamp']
    if not 0<gap<=CONFIG['track_gap_seconds']: return False
    diag=max(math.hypot(x['bbox'][2]-x['bbox'][0],x['bbox'][3]-x['bbox'][1]) for x in (a,b))
    budget=max(CONFIG['center_distance_pixels'],CONFIG['diagonal_multiplier']*diag)
    if RULES[b['visual_class']]['kind']=='grouped': budget=max(budget,CONFIG['grouped_motion_pixels_per_second']*gap)
    return math.dist(_center(a['bbox']),_center(b['bbox']))<=budget

def _summary(rows, chains):
    sizes=[len(c) for _,c in chains]
    assigned={r['observation_id'] for _,c in chains for r in c}
    ambiguous_boundary=unique_boundary=0
    for tid,c in chains:
        options=[old for old,other in chains if old!=tid and _possible_continuation(other[-1],c[0])]
        unique_boundary+=len(options)==1;ambiguous_boundary+=len(options)>1
    start=min((r['timestamp'] for r in rows),default=None)
    end=max((r['timestamp'] for r in rows),default=None)
    return {'raw_observation_count':len(rows),'track_count':len(chains),
        'assigned_observation_count':len(assigned),'unassigned_observation_count':len(rows)-len(assigned),
        'assigned_fraction':len(assigned)/len(rows) if rows else None,
        'track_starts_per_100_raw_observations':100*len(chains)/len(rows) if rows else None,
        'singleton_count':sum(n==1 for n in sizes),
        'singleton_fraction':sum(n==1 for n in sizes)/len(sizes) if sizes else None,
        'observations_per_track_median':median(sizes) if sizes else None,
        'track_span_seconds_median':median(c[-1]['timestamp']-c[0]['timestamp'] for _,c in chains) if chains else None,
        'possible_unique_continuation_boundaries':unique_boundary,
        'possible_ambiguous_continuation_boundaries':ambiguous_boundary,
        'initial_visible_track_count':sum(c[0]['timestamp']==start for _,c in chains),
        'final_visible_track_count':sum(c[-1]['timestamp']==end for _,c in chains)}

def track_metrics(rows, tracks):
    """Fixed raw denominator and assignment coverage prevent deletion-as-improvement."""
    chains=_chains(rows,tracks)
    selected=[r for r in rows if r['visual_class'] in RULES]
    scoped=defaultdict(list)
    for r in selected: scoped[r['match_id'],r['visual_class']].append(r)
    details=[]
    for (match,cls),part in sorted(scoped.items()):
        cs=[(tid,c) for tid,c in chains if (c[0]['match_id'],c[0]['visual_class'])==(match,cls)]
        details.append({'match_id':match,'visual_class':cls}|_summary(part,cs))
    # Potential continuation must never span match or class in aggregate.
    total=_summary(selected,[])
    total.update({'track_count':len(chains),'assigned_observation_count':sum(len(c) for _,c in chains),
        'unassigned_observation_count':len(selected)-sum(len(c) for _,c in chains),
        'assigned_fraction':sum(len(c) for _,c in chains)/len(selected) if selected else None,
        'track_starts_per_100_raw_observations':100*len(chains)/len(selected) if selected else None,
        'singleton_count':sum(len(c)==1 for _,c in chains),
        'singleton_fraction':sum(len(c)==1 for _,c in chains)/len(chains) if chains else None,
        'observations_per_track_median':median(len(c) for _,c in chains) if chains else None,
        'track_span_seconds_median':median(c[-1]['timestamp']-c[0]['timestamp'] for _,c in chains) if chains else None})
    for key in ('possible_unique_continuation_boundaries','possible_ambiguous_continuation_boundaries','initial_visible_track_count','final_visible_track_count'):
        total[key]=sum(x[key] for x in details)
    return total|{'by_match_class':details,'true_fragmentation_measured':False,
        'true_id_switches_measured':False,'continuation_is_hypothesis_not_identity':True}

def owner_metrics(raw, experimental, reference_tracks):
    """Compare on identical owner-agnostic ByteTrack links, not 3B owner-gated IDs."""
    a,b=_indexed(raw),_indexed(experimental)
    if set(a)!=set(b): raise ValueError('owner comparison observation set differs')
    for oid,r in a.items():
        if any(r[k]!=b[oid][k] for k in ('match_id','visual_class','bbox','timestamp')):
            raise ValueError('owner comparison geometry/time differs')
    chains=_chains(raw,reference_tracks)
    links=[(c[i-1]['observation_id'],c[i]['observation_id']) for _,c in chains for i in range(1,len(c))]
    selected=[oid for oid,r in a.items() if r['visual_class'] in RULES]
    def summarize(indexed):
        transitions=defaultdict(int)
        flip=kk=0
        for prev,cur in links:
            x,y=indexed[prev]['owner'],indexed[cur]['owner'];transitions[x+'->'+y]+=1
            if x!='unknown' and y!='unknown': kk+=1;flip+=x!=y
        return {'known_flip_count':flip,'known_known_link_count':kk,'reference_link_count':len(links),
            'known_known_link_coverage':kk/len(links) if links else None,
            'unknown_observation_count':sum(indexed[oid]['owner']=='unknown' for oid in selected),
            'unknown_fraction':sum(indexed[oid]['owner']=='unknown' for oid in selected)/len(selected) if selected else None,
            'transitions':dict(sorted(transitions.items()))}
    return {'raw':summarize(a),'experimental':summarize(b),
        'reference':'same owner-agnostic ByteTrack hypothesis links',
        'owner_accuracy_measured':False,'unknown_is_abstention':True}
