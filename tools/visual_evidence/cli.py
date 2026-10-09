"""One parallel replay; scoring is a later, separate existing command."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import time

from tools.event_engine.engine import replay, validate_observations
from tools.event_engine.cli import write_artifacts
from tools.event_engine.oracle import file_sha
from .metrics import track_metrics, owner_metrics

MAX_STREAM_BYTES=128*1024*1024

def read_stream(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>MAX_STREAM_BYTES:
        raise ValueError('missing/oversized visual evidence')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise ValueError('duplicate visual evidence key')
            d[k]=v
        return d
    def bad(_): raise ValueError('non-finite visual evidence')
    def decimal(s):
        x=float(s)
        if not math.isfinite(x): raise ValueError('non-finite visual evidence')
        return x
    d=json.loads(path.read_text('utf-8'),object_pairs_hook=pairs,parse_constant=bad,parse_float=decimal)
    if not isinstance(d,dict): raise ValueError('visual evidence object required')
    return d

def engine_projection(rows):
    """Only exact projected geometry collisions; preserve exclusions separately."""
    seen={}; projected=[];excluded=[]
    for r in sorted(rows,key=lambda x:x['observation_id']):
        key=(r['match_id'],r['timestamp'],r['visual_class'],r['owner'],tuple(r['bbox']))
        if key in seen:
            excluded.append({'observation_id':r['observation_id'],'kept_observation_id':seen[key],
                'reason':'identical_geometry_after_owner_abstention','negative':False})
        else:
            seen[key]=r['observation_id'];projected.append(r)
    return projected,excluded

def run_files(input_path, expected_sha, baseline_path, baseline_sha, source_root, output,
              *, source_dimensions_wh=None):
    """No answer input. MOT IDs remain sidecar, never trusted human identity."""
    from .tracking import track_stream
    from .policy import run_policy, POLICY
    inputs=[Path(input_path),Path(baseline_path)]
    output=Path(output)
    for p in inputs+[Path(source_root)]:
        if output.resolve().is_relative_to(p.resolve()) or p.resolve().is_relative_to(output.resolve()):
            raise ValueError('output overlaps retained input')
    if output.exists(): raise ValueError('experimental output is immutable')
    if file_sha(inputs[0])!=expected_sha or file_sha(inputs[1])!=baseline_sha:
        raise ValueError('frozen input hash differs')
    stream=read_stream(inputs[0]);old=read_stream(inputs[1])
    if stream.get('schema')!='detector_visual_stream_v1' or not isinstance(stream.get('frames'),list):
        raise ValueError('explicit detector stream and sampled frames required')
    rows=stream.get('observations');validate_observations(rows)
    if any(r['source']!='katacr_prediction' or r.get('appearance_group_id') is not None for r in rows):
        raise ValueError('raw detector-only observations required')
    started=time.perf_counter()
    sidecar=track_stream(rows,stream['frames'],Path(source_root))
    track_seconds=time.perf_counter()-started
    started=time.perf_counter()
    policy=run_policy(rows,sidecar['associations'],source_dimensions_wh=source_dimensions_wh)
    policy_seconds=time.perf_counter()-started
    projected=policy['observations'];engine_rows,excluded=engine_projection(projected)
    validate_observations(engine_rows)
    started=time.perf_counter();result=replay(engine_rows);engine_seconds=time.perf_counter()-started
    metrics={'schema':'visual_evidence_comparison_v1',
        'baseline_tracks':track_metrics(rows,old['tracks']),
        'bytetrack_tracks':track_metrics(rows,sidecar['tracks']),
        'experimental_3b_tracks':track_metrics(rows,result['tracks']),
        'engine_projection_exact_collision_exclusions':len(excluded),
        'owner':owner_metrics(rows,projected,sidecar['tracks']),
        'ambiguous_associations':sum(r['association_ambiguous'] for r in sidecar['associations']),
        'baseline_event_count':len(old['events']),'experimental_event_count':len(result['events']),
        'group_hypotheses':len(policy['groups']),
        'speed':{'frames':len(stream['frames']),'tracking_seconds':track_seconds,
            'tracking_ms_per_sample':1000*track_seconds/len(stream['frames']) if stream['frames'] else None,
            'policy_seconds':policy_seconds,'unchanged_3b_replay_seconds':engine_seconds},
        'limitations':{'true_identity_gt_available':False,'owner_accuracy_measured':False,
            'tracker_ids_consumed_by_formal_3b':False,'groups_are_deployments':False,
            'abstention_is_success':False,'no_timestamp_shift':True}}
    meta={'schema':'visual_evidence_source_summary_v1','input_sha256':expected_sha,
        'baseline_sha256':baseline_sha,'policy':POLICY,'tracking_config':sidecar['config'],
        'tracking_source':sidecar['source'],'event_answers_used_as_input':False,
        'observation_count':len(rows),'frame_count':len(stream['frames']),
        'timestamps_geometry_confidence_preserved':all(all(a[k]==b[k] for k in ('observation_id','timestamp','bbox','confidence','origin_kind','form')) for a,b in zip(sorted(rows,key=lambda r:r['observation_id']),sorted(projected,key=lambda r:r['observation_id']),strict=True)),
        'no_training':True,'source_dimensions_wh':source_dimensions_wh,
        'no_geometric_owner_inference':True}
    for p,h in zip(inputs,[expected_sha,baseline_sha],strict=True):
        if file_sha(p)!=h: raise ValueError('input changed while replaying')
    write_artifacts(output,{'track-sidecar.json':sidecar,'owner-and-group-evidence.json':policy,
        'experimental-visual-stream.json':{'schema':'experimental_visual_stream_v1','observations':engine_rows,'frames':stream['frames'],'exact_collision_exclusions':excluded},
        'replay.json':result,'opponent-card-played.json':{'events':result['events']},
        'card-play-candidates.json':{'candidates':result['candidates']},'comparison.json':metrics,'source-summary.json':meta})
    return {'observations':len(rows),'frames':len(stream['frames']),'events':len(result['events']),
        'group_hypotheses':len(policy['groups']),'event_answers_used_as_input':False,'scored':False}

def main(argv=None):
    p=argparse.ArgumentParser(description='Offline ByteTrack evidence experiment only')
    s=p.add_subparsers(dest='command',required=True)
    q=s.add_parser('replay')
    for name in ('input','sha','baseline','baseline-sha','tracker-source','output'):
        q.add_argument('--'+name,required=True)
    q.add_argument('--source-width',type=int);q.add_argument('--source-height',type=int)
    a=p.parse_args(argv)
    try:
        if (a.source_width is None)!=(a.source_height is None): raise ValueError('dimensions pair required')
        dimensions=None
        if a.source_width is not None:
            if a.source_width<=0 or a.source_height<=0: raise ValueError('positive source dimensions required')
            matches={f['match_id'] for f in read_stream(a.input)['frames']}
            dimensions={m:[a.source_width,a.source_height] for m in matches}
        r=run_files(a.input,a.sha,a.baseline,a.baseline_sha,a.tracker_source,a.output,source_dimensions_wh=dimensions)
        print(json.dumps(r,allow_nan=False));return 0
    except (ValueError,KeyError,TypeError,OSError,ImportError,ZeroDivisionError,OverflowError):
        print('Visual evidence rejected; private paths are not disclosed.');return 2

if __name__=='__main__':raise SystemExit(main())
