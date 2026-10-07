"""Post-replay scorer only; reviewed unknown time is not false-positive truth."""
from __future__ import annotations


def evaluate(events, gt):
    windows={c['candidate_id']:c for c in gt['source_plan']['candidates']}
    used=set();positives=[];dedupe=[];unscored=[];duplicates=0
    # Equal-width chronological windows admit an earliest-unused matching.
    # Finish matching first; an event used by another GT is not a duplicate.
    ordered=sorted(gt['confirmed_events'],key=lambda r:(r['underlying_match_id'],r['card_id'],
                                                      r['approximate_timestamp'],r['event_gt_id']))
    positive_window_ids=set()
    for row in ordered:
        t=row['approximate_timestamp']
        hits=[e for e in events if e['match_id']==row['underlying_match_id'] and e['card_id']==row['card_id']
              and t<=e['timestamp']<=t+2.5]
        hits.sort(key=lambda e:(e['timestamp'],e['event_id']))
        eligible=[e for e in hits if e['event_id'] not in used]
        chosen=eligible[0] if eligible else None
        if chosen: used.add(chosen['event_id'])
        positive_window_ids.update(e['event_id'] for e in hits)
        positives.append({'event_gt_id':row['event_gt_id'],'candidate_id':row['candidate_id'],
            'card_id':row['card_id'],'gt_timestamp':t,'hit':chosen is not None,'matching_count':len(hits),
            'matched_event_id':None if chosen is None else chosen['event_id'],
            'first_appearance_delay':None if chosen is None else chosen['timestamp']-t,
            'confirmation_delay':None if chosen is None else chosen['confirmed_at']-t})
    duplicates=len(positive_window_ids-used)
    order={r['event_gt_id']:i for i,r in enumerate(gt['confirmed_events'])}
    positives.sort(key=lambda r:order[r['event_gt_id']])
    failures=set()
    for row in gt['continuity_dedupe_outcomes']:
        c=windows[row['candidate_id']];start=c['context']['start_seconds'];end=c['context']['end_seconds']
        hits=[e for e in events if e['match_id']==row['underlying_match_id'] and e['card_id']==c['card_id']
              and start<=e['timestamp']<=end]
        failures.update(e['event_id'] for e in hits)
        dedupe.append({'candidate_id':row['candidate_id'],'card_id':c['card_id'],
                      'start_seconds':start,'end_seconds':end,'new_event_count':len(hits),
                      'event_ids':[e['event_id'] for e in hits]})
    for e in events:
        if e['event_id'] in used or e['event_id'] in failures:continue
        overlaps=[c['candidate_id'] for c in (windows[r['candidate_id']] for r in gt['unresolved_candidates'])
                  if c['underlying_match_id']==e['match_id'] and
                  c['context']['start_seconds']<=e['timestamp']<=c['context']['end_seconds']]
        unscored.append({'event_id':e['event_id'],'match_id':e['match_id'],'card_id':e['card_id'],
                         'timestamp':e['timestamp'],'unresolved_candidates':overlaps,
                         'reason':'unresolved_review_window' if overlaps else 'unreviewed_time_or_unmatched_positive'})
    count=sum(p['hit'] for p in positives)
    return {'schema':'oracle_event_evaluation_v1','positive_hits':count,'positive_total':len(positives),
            'positive_duplicates':duplicates,'positives':positives,'dedupe_outcomes':dedupe,
            'unscored_events':unscored,'explicit_dedupe_failures':len(failures),
            'passed':bool(positives) and count==len(positives) and duplicates==0 and not failures,
            'hit_window_seconds':[0,2.5],'unresolved_is_negative':False,
            'real_time_latency_validated':False,'cross_match_positive_validation':False,
            'detector_performance':False,'full_timeline_false_positive_rate':None}
