"""Exclusive offline artifact commands, with replay and grading kept separate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import replay
from .oracle import file_sha, read_json, load_multiclass_source, load_legacy_smoke_source


def write_artifacts(out, contents):
    out=Path(out)
    if out.exists(): raise ValueError('Oracle output already exists; select a new version')
    if any(not isinstance(name,str) or not name.endswith('.json') or '/' in name or '\\' in name
           or ':' in name or name=='manifest.json' for name in contents):
        raise ValueError('invalid Oracle artifact member')
    # Validate serializability before creating anything.
    encoded={name:json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
             for name,data in contents.items()}
    out.mkdir(parents=True,exist_ok=False)
    for name,data in encoded.items():
        with (out/name).open('x',encoding='utf-8',newline='\n') as f:f.write(data)
    manifest={'schema':'oracle_artifact_manifest_v1','files':{name:file_sha(out/name) for name in contents}}
    with (out/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest


def verify_artifacts(out):
    out=Path(out);m=read_json(out/'manifest.json')
    if m.get('schema')!='oracle_artifact_manifest_v1' or not isinstance(m.get('files'),dict):
        raise ValueError('invalid Oracle output manifest')
    for name,h in m['files'].items():
        if not isinstance(name,str) or '/' in name or '\\' in name or ':' in name or name=='manifest.json' or not name.endswith('.json'):
            raise ValueError('invalid Oracle artifact member')
        if file_sha(out/name)!=h:raise ValueError('Oracle artifact changed after replay')
    return m


def app_projection(events):
    return {'schema':'recorded_oracle_events_v1','events':[{'eventId':e['event_id'],'cardId':e['card_id'],
            'timestamp':e['timestamp'],'confidence':None,'source':'recorded_oracle'} for e in events]}


def replay_oracle(config, out):
    if set(config)!={'sources'} or not isinstance(config['sources'],list) or not config['sources']:
        raise ValueError('explicit human visual sources required; Event GT is not a replay input')
    observations=[];source_meta=[]
    for source in config['sources']:
        if set(source)!={'kind','lock_path','sha256'}:raise ValueError('invalid visual source descriptor')
        path=Path(source['lock_path'])
        if Path(out).resolve().is_relative_to(path.parent.resolve()) or path.resolve().is_relative_to(Path(out).resolve()):
            raise ValueError('output cannot overlap human visual source')
        loader={'multiclass':load_multiclass_source,'legacy_smoke_visual':load_legacy_smoke_source}.get(source['kind'])
        if loader is None:raise ValueError('unsupported source; only confirmed human visual GT accepted')
        rows,meta=loader(path,expected_sha=source['sha256']);observations.extend(rows);source_meta.append(meta)
    observations.sort(key=lambda r:(r['match_id'],r['timestamp'],r['observation_id']))
    result=replay(observations)
    stream={'schema':'human_oracle_visual_stream_v1','observations':observations,
            'sources':source_meta,'all_accepted_sources_used':True,'event_gt_used_as_input':False}
    contents={'oracle-visual-stream.json':stream,'replay.json':result,
              'card-play-candidates.json':{'candidates':result['candidates']},
              'opponent-card-played.json':{'events':result['events']},
              'recorded-app-events.json':app_projection(result['events'])}
    write_artifacts(out,contents)
    return {'observation_count':len(observations),'source_frame_count':sum(m['frame_count'] for m in source_meta),
            'event_count':len(result['events']),'candidate_count':len(result['candidates']),
            'event_gt_used_as_input':False}


def evaluate_replay(replay_dir, gt_path, expected_sha, out):
    # The Event GT import exists only on the grading side of the boundary.
    from tools.deployment_review.event_gt import load_lock
    from .evaluation import evaluate
    for source in (Path(replay_dir),Path(gt_path).parent):
        if Path(out).resolve().is_relative_to(source.resolve()) or source.resolve().is_relative_to(Path(out).resolve()):
            raise ValueError('evaluation output cannot overlap input evidence')
    verify_artifacts(replay_dir)
    if file_sha(gt_path)!=expected_sha:raise ValueError('Event GT byte SHA mismatch')
    gt=load_lock(Path(gt_path).resolve());events=read_json(Path(replay_dir)/'opponent-card-played.json')['events']
    report=evaluate(events,gt)
    report['event_gt_sha256']=expected_sha;report['replay_manifest_sha256']=file_sha(Path(replay_dir)/'manifest.json')
    timeline={'schema':'oracle_event_timeline_v1','events':events,'positive_matches':report['positives'],
              'dedupe_checks':report['dedupe_outcomes'],'unscored':report['unscored_events']}
    write_artifacts(out,{'evaluation.json':report,'timeline.json':timeline})
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description='Offline Human-GT Oracle only; no detector or game connection')
    subs=parser.add_subparsers(dest='command',required=True)
    p=subs.add_parser('event-replay-oracle');p.add_argument('--sources',required=True);p.add_argument('--output',required=True)
    p=subs.add_parser('event-evaluate');p.add_argument('--replay',required=True);p.add_argument('--gt-lock',required=True)
    p.add_argument('--gt-sha',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='event-replay-oracle':
            report=replay_oracle(read_json(args.sources),Path(args.output));code=0
        else:
            report=evaluate_replay(Path(args.replay),Path(args.gt_lock),args.gt_sha,Path(args.output))
            code=0 if report['passed'] else 3
        print(json.dumps(report,ensure_ascii=True,allow_nan=False));return code
    except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError,OverflowError):
        print('Oracle evidence rejected; no private paths are disclosed.');return 2


if __name__=='__main__':raise SystemExit(main())
