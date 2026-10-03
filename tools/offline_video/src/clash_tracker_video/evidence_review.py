"""Manual box helpers and conservative current-recording sufficiency."""
from fractions import Fraction

from .evidence_contract import EvidenceError, STATUS, number, rational, valid_type, seconds, validate_evidence


def normalize_box(rect: tuple[float,float,float,float], image_size: tuple[int,int]) -> dict[str,float]:
    if (not isinstance(rect,(tuple,list)) or len(rect)!=4 or not all(number(v) for v in rect)
            or not isinstance(image_size,(tuple,list)) or len(image_size)!=2
            or any(type(v) is not int or v<=0 for v in image_size)):
        raise EvidenceError('Invalid full-image rectangle or displayed size.')
    x,y,w,h = rect
    iw,ih = image_size
    if x<0 or y<0 or w<=0 or h<=0 or x+w>iw or y+h>ih:
        raise EvidenceError('Rectangle outside full displayed image; no clipping performed.')
    return dict(x=x/iw,y=y/ih,width=w/iw,height=h/ih)


def make_frame_annotation(entry, *, annotation_id: str, recording_id: str, play_id: str,
                          rect: tuple[float,float,float,float], review_status: str = 'draft'):
    if (entry.get('status')!='success' or type(entry.get('raw_pts')) is not int
            or not valid_type(entry.get('frame_id'),'id') or not valid_type(entry.get('image_path'),'png')
            or not valid_type(entry.get('timestamp_seconds'),'seconds')
            or review_status not in STATUS or not all(valid_type(v,'id') for v in (annotation_id,recording_id,play_id))):
        raise EvidenceError('Successful original export and explicit manual status required.')
    rational(entry.get('time_base'))
    box = normalize_box(rect,(entry.get('image_width'),entry.get('image_height')))
    result = {k:entry[k] for k in ('frame_id','timestamp_seconds','raw_pts','image_path','image_width','image_height')}
    result['time_base'] = dict(entry['time_base'])
    result.update(annotation_id=annotation_id,recording_id=recording_id,play_id=play_id,
                  normalized_bbox=box,annotation_source='manual',review_status=review_status)
    return result


def review_evidence(doc, indexes):
    errors = validate_evidence(doc,indexes)
    counts = dict(recordings=0,reviewed_complete_segments=0,verified_plays=0,annotated_key_frames=0)
    if errors:
        return dict(status='invalid',candidate_gate=False,experiment_gate=False,counts=counts,reasons=errors,coverage_gaps=[])
    recordings = {r['recording_id']:r for r in doc['recordings']}
    segments = {s['segment_id']:s for s in doc['match_segments']}
    verified = [p for p in doc['occurrences'] if p['manual_verification_status']=='verified']
    ids = {aid for p in verified for aid in p['evidence_annotation_ids']}
    annotations = [a for a in doc['frame_annotations'] if a['annotation_id'] in ids and a['review_status']=='verified']
    counts.update(recordings=len(recordings),reviewed_complete_segments=sum(
        s['validation_status']=='verified' and s['capture_complete'] and s['perspective']!='unknown' for s in segments.values()),
        verified_plays=len(verified),annotated_key_frames=len({(a['play_id'],a['raw_pts']*rational(a['time_base'])) for a in annotations}))
    per_recording = {rid:sum(p['recording_id']==rid for p in verified) for rid in recordings}
    candidate = doc['target_card'] is not None and doc['target_card']['variant']!='unknown' and any(n>=4 for n in per_recording.values())
    gaps = []
    for rid,r in recordings.items():
        intervals = []
        last = seconds(r['last_frame_seconds'])
        for p in verified:
            if p['recording_id']==rid:
                intervals.append((seconds(p['visible_start_seconds']),seconds(p['visible_end_seconds']),False))
        for n in doc['negative_intervals']:
            if n['recording_id']==rid and n['review_status']=='verified':
                end = seconds(n['end_seconds'])
                intervals.append((seconds(n['start_seconds']),end,end==last))
        cursor = Fraction(0)
        raw_gaps = []
        terminal_covered = False
        for start,end,closed in sorted(intervals):
            if start>cursor: raw_gaps.append((cursor,start))
            cursor = max(cursor,end)
            terminal_covered |= closed
        if cursor<last: raw_gaps.append((cursor,last))
        elif not terminal_covered: raw_gaps.append((last,last))
        for start,end in raw_gaps:
            cuts = sorted({start,end} | {seconds(s[k]) for s in segments.values() if s['recording_id']==rid
                                          for k in ('start_seconds','end_seconds') if start<seconds(s[k])<end})
            pieces = list(zip(cuts,cuts[1:])) if start<end else [(start,end)]
            for left,right in pieces:
                sid = next((s['segment_id'] for s in segments.values() if s['recording_id']==rid
                            and seconds(s['start_seconds'])<=left<seconds(s['end_seconds'])),None)
                gaps.append(dict(recording_id=rid,match_segment_id=sid,start_seconds=float(left),end_seconds=float(right)))
    reasons = ['Independent complete-match evidence and separately approved 2A2 are required; no split/freeze implemented.']
    if len(recordings)<2: reasons.append('Only one or zero recording; at least two independent complete matches needed for 2B.')
    if len(verified)<6: reasons.append('Fewer than six verified target plays; held-out complete match with two plays still required.')
    if not candidate: reasons.append('Current candidate gate not met: need four reviewed opponent plays in one recording.')
    if gaps: reasons.append('Unknown timeline gaps remain; they are not negatives.')
    if any(p['manual_verification_status'] in {'draft','ambiguous'} for p in doc['occurrences']):
        reasons.append('Unresolved candidate occurrences remain.')
    if not counts['reviewed_complete_segments']: reasons.append('No reviewed complete match segment.')
    return dict(status='insufficient',candidate_gate=bool(candidate),experiment_gate=False,counts=counts,reasons=reasons,coverage_gaps=gaps)
