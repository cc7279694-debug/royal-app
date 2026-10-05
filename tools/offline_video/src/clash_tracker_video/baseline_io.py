"""Private offline baseline orchestration with explicit data/split bindings."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

import av
import cv2
import numpy as np
from PIL import Image

from . import pipeline
from .baseline import (Config, Template, artifact_sha, crop, evaluate, final_threshold,
                       fine_windows, make_artifact, merge_events, rank_events, score_frame,
                       reference_model_parameters)
from .evidence_contract import EvidenceError, load_evidence
from .evidence_prepare import file_hash, load_indexes, new_output, safe_path, write_json, _reference
from .experiment_development import require_development
from .experiment_lock import canonical_bytes, freeze_model, load_lock


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def default_config_document():
    return Config().document()


def development_context(lock_path, index_paths, source):
    development = load_lock(lock_path)
    if development['lock_type'] != 'development':
        raise EvidenceError('Development lock required.')
    draft = development['payload']['draft']
    paths = [safe_path(p,private=True) for p in index_paths]
    indexes = load_indexes(paths)
    if canonical_bytes(require_development(draft,indexes)) != canonical_bytes(development['payload']):
        raise EvidenceError('Current disk indexes conflict with frozen development evidence.')
    source = safe_path(source,private=True)
    recording = indexes[draft['identity']['recording_id']]['recording']
    if source.suffix.lower() != '.mp4' or file_hash(source) != recording['source_sha256']:
        raise EvidenceError('Source does not match the frozen development recording.')
    selected = next(c for c in draft['candidates'] if c['candidate_id']==draft['selection']['candidate_id'])
    plays = sorted(selected['evidence']['occurrences'],key=lambda p:p['deployment_time_seconds'])
    if len(plays)!=2 or len(selected['evidence']['frame_annotations'])!=6:
        raise EvidenceError('First baseline protocol requires exactly two plays and six frozen boxes.')
    image_paths = {}
    for path in paths:
        index = load_evidence(path)
        for f in index['frames']:
            if f['status']=='success':
                image_paths.setdefault(f['frame_id'],_reference(path.parent,f['image_path']))
    templates = {}
    for play in plays:
        group = []
        for annotation in selected['evidence']['frame_annotations']:
            if annotation['play_id'] != play['play_id']: continue
            with Image.open(image_paths[annotation['frame_id']]) as image:
                pixels = crop(np.array(image.convert('RGB')),annotation['normalized_bbox'])
            group.append(Template(annotation['annotation_id'],play['play_id'],annotation['frame_id'],pixels))
        if len(group)!=3: raise EvidenceError('Exactly three references per independent play required.')
        templates[play['play_id']] = group
    target = {k:draft['selection'][k] for k in ('card_id','form')}
    return dict(development=development,source=source,recording=recording,plays=plays,
                templates=templates,target=target)


def _frames(source):
    """Use the existing decoder/geometry checks, without changing Module 1."""
    with av.open(str(pipeline._input(source))) as container:
        stream = pipeline._stream(container)
        previous = origin = geometry = None
        for frame in container.decode(stream):
            rotation = pipeline._validate_frame(frame)
            raw = pipeline._timestamp(frame)
            if previous is not None and raw<=previous: raise EvidenceError('Invalid scan timeline.')
            current = (frame.width,frame.height,rotation)
            if origin is None:
                origin=raw; geometry=current
                pipeline._video_info(source,container,stream,frame)
            elif current!=geometry: raise EvidenceError('Changing scan geometry.')
            previous=raw
            yield raw-origin,frame,rotation
        if origin is None: raise EvidenceError('No scan frames.')


def _rgb(frame,rotation):
    image=frame.to_image()
    if rotation:
        image=image.transpose({90:Image.Transpose.ROTATE_90,180:Image.Transpose.ROTATE_180,
                               270:Image.Transpose.ROTATE_270}[rotation])
    return np.array(image.convert('RGB'))


def scan_video(source, templates, config):
    """Whole-file coarse scan, then pixel-selected fine windows. No GT argument."""
    cv2.setNumThreads(1)
    cv2.setRNGSeed(0)
    coarse=[]
    next_target=Fraction(0); step=Fraction(1)/Fraction(str(config.fps))
    last=None
    for time,frame,rotation in _frames(source):
        last=time
        if time>=next_target:
            result=score_frame(_rgb(frame,rotation),templates,config)
            result.update(timestamp_seconds=float(time),raw_pts=frame.pts,time_base=str(frame.time_base))
            coarse.append(result)
            while next_target<=time: next_target+=step
    # Coarse proposals use score-ordered temporal suppression, NOT transitive
    # event grouping: one long coarse plateau must not collapse every fine seed.
    seeds=[]
    for observation in sorted((o for o in coarse if o['score'] is not None
            and o['score']>=config.proposal_floor),key=lambda o:(-o['score'],o['timestamp_seconds'])):
        time=observation['timestamp_seconds']
        if all(abs(time-prior)>config.merge_seconds for prior in seeds): seeds.append(time)
        if len(seeds)==config.coarse_seeds: break
    windows=fine_windows(seeds,float(last),config.fine_seconds)
    fine=[]
    for time,frame,rotation in _frames(source):
        if any(start<=float(time)<=end for start,end in windows):
            result=score_frame(_rgb(frame,rotation),templates,config)
            result.update(timestamp_seconds=float(time),raw_pts=frame.pts,time_base=str(frame.time_base))
            fine.append(result)
    unique={(o['raw_pts'],o['time_base']):o for o in coarse+fine}
    return dict(observations=sorted(unique.values(),key=lambda o:o['timestamp_seconds']),
                coarse_frames=len(coarse),fine_frames=len(fine),fine_windows=windows,
                last_frame_seconds=float(last))


def freeze_then_evaluate(path,ranking,hidden_loader):
    write_json(path,{'ranking':ranking})
    frozen=load_evidence(path)['ranking']
    return evaluate(frozen,hidden_loader())


def _git_commit():
    # No result-dependent edits after the first experiment are allowed.
    def git(*args):
        try:
            return subprocess.check_output(['git',*args],cwd=PROJECT_ROOT,
                stderr=subprocess.PIPE,text=True).strip()
        except (subprocess.CalledProcessError,OSError) as exc:
            raise EvidenceError('Cannot verify committed baseline code.') from exc
    tracked=git('diff','--name-only','HEAD','--','tools/offline_video')
    untracked=git('ls-files','--others','--exclude-standard','tools/offline_video')
    if tracked or untracked: raise EvidenceError('Commit baseline implementation before a real experiment.')
    return git('rev-parse','HEAD')


def _screenshots(source, rankings, destination):
    by_pts={}
    for label,ranking in rankings.items():
        for event in ranking[:5]:
            key=(event['peak']['raw_pts'],event['peak']['time_base'])
            by_pts.setdefault(key,[]).append(f'{label}-rank-{event["rank"]}.png')
    for _,frame,rotation in _frames(source):
        for name in by_pts.get((frame.pts,str(frame.time_base)),[]):
            with (destination/name).open('xb') as f:
                Image.fromarray(_rgb(frame,rotation)).save(f,format='PNG')


def crossval(context, output, config=Config()):
    if config.document()!=default_config_document():
        raise EvidenceError('Real experiment must use the a priori protocol configuration.')
    git=_git_commit()
    out=new_output(output)
    write_json(out/'protocol.json',dict(config=config.document(),git_commit=git,
        development_lock_sha256=context['development']['sha256'],target=context['target']))
    rankings={}; scan_summaries={}
    plays=context['plays']
    for label,reference in zip(('a_to_b','b_to_a'),plays):
        print(f'Scanning development fold {label}.',flush=True)
        scan=scan_video(context['source'],context['templates'][reference['play_id']],config)
        if scan['last_frame_seconds'] != context['recording']['last_frame_seconds']:
            raise EvidenceError('Actual scan end differs from the frozen recording.')
        ranking=rank_events(merge_events(scan['observations'],window=config.merge_seconds,
            floor=config.proposal_floor),source_interval=(reference['deployment_lower_seconds'],reference['visible_end_seconds']))
        write_json(out/f'{label}-scan.json',scan)
        write_json(out/f'{label}-ranking.json',dict(ranking=ranking))
        rankings[label]=ranking
        scan_summaries[label]={k:v for k,v in scan.items() if k!='observations'}
    # BOTH scan/rank files have been exclusively persisted before hidden scoring.
    results=[]
    for label,hidden in zip(('a_to_b','b_to_a'),reversed(plays)):
        ranking=load_evidence(out/f'{label}-ranking.json')['ranking']
        results.append(dict(fold=label,**evaluate(ranking,hidden)))
    passed=all(r['pass'] for r in results)
    report=dict(status='2B1_CROSSVAL_PASS' if passed else '2B1_BASELINE_INSUFFICIENT',
        folds=results,top_five={label:r[:5] for label,r in rankings.items()},
        scan=scan_summaries,git_commit=git,config=config.document(),
        development_lock_sha256=context['development']['sha256'],
        ranking_sha256={label:file_hash(out/f'{label}-ranking.json') for label in rankings},
        protocol_sha256=file_hash(out/'protocol.json'),
        temporal_proxy_only=True,unknown_is_negative=False,other_forms_are_negative=False)
    _screenshots(context['source'],rankings,out)
    if file_hash(context['source']) != context['recording']['source_sha256']:
        raise EvidenceError('Source changed during the experiment.')
    write_json(out/'crossval.json',report)
    return report


def require_crossval(report):
    final_threshold(report['folds'])
    return report


def require_protocol(report, crossval_path, context):
    path=safe_path(Path(crossval_path).parent/'protocol.json',private=True)
    protocol=load_evidence(path)
    expected=dict(config=default_config_document(),git_commit=report['git_commit'],
        development_lock_sha256=context['development']['sha256'],target=context['target'])
    if (file_hash(path)!=report['protocol_sha256'] or protocol!=expected
            or report['config']!=protocol['config']):
        raise EvidenceError('Cross-validation differs from its prefrozen fixed protocol.')


def verify_artifact(artifact,expected_sha,templates):
    if artifact_sha(artifact)!=expected_sha:
        raise EvidenceError('Baseline artifact digest mismatch.')
    if artifact['templates'] != [t.document() for t in sorted(templates,key=lambda t:t.template_id)]:
        raise EvidenceError('Baseline reference pixels differ from the artifact.')
    config=Config(**{**artifact['config'],'roi':tuple(artifact['config']['roi']),
        'scales':tuple(artifact['config']['scales'])})
    expected=make_artifact(artifact['development_lock_sha256'],artifact['target'],
        templates,config,artifact['threshold'],artifact['git_commit'])
    if artifact!=expected:
        raise EvidenceError('Baseline artifact differs from actual runtime semantics.')


def verify_model_semantics(artifact,model):
    payload=model['payload']
    baseline=payload.get('baseline',{})
    pairs=[(artifact.get('threshold'),payload.get('confidence_threshold')),
           (artifact.get('git_commit'),payload.get('git_commit')),
           (artifact.get('target'),payload.get('target')),
           (artifact.get('development_lock_sha256'),payload.get('development_lock_sha256'))]
    pairs.extend((artifact.get(k),baseline.get(k)) for k in
        ('config','templates','score_method','event_merge','threshold_derivation','opencv_version','evaluation_protocol_version'))
    if (payload.get('artifact_type')!='reference_template_matcher'
            or any(a!=b for a,b in pairs)):
        raise EvidenceError('Detector artifact and Model Lock semantics conflict.')


def build_baseline(context, crossval_path, output):
    report=load_evidence(safe_path(crossval_path,private=True)); require_crossval(report)
    git=_git_commit()
    if report['git_commit']!=git or report['development_lock_sha256']!=context['development']['sha256']:
        raise EvidenceError('Cross-validation code/data reference mismatch.')
    require_protocol(report,crossval_path,context)
    for label,hidden in zip(('a_to_b','b_to_a'),reversed(context['plays'])):
        path=safe_path(Path(crossval_path).parent/f'{label}-ranking.json',private=True)
        if file_hash(path)!=report['ranking_sha256'][label]: raise EvidenceError('Frozen ranking changed.')
        observed=evaluate(load_evidence(path)['ranking'],hidden)
        if observed!={k:v for k,v in report['folds'][0 if label=='a_to_b' else 1].items() if k!='fold'}:
            raise EvidenceError('Cross-validation evaluation changed.')
    config=Config(**{**report['config'],'roi':tuple(report['config']['roi']),'scales':tuple(report['config']['scales'])})
    templates=[t for group in context['templates'].values() for t in group]
    threshold=final_threshold(report['folds'])
    artifact=make_artifact(context['development']['sha256'],context['target'],templates,config,threshold,git)
    out=new_output(output)
    # Canonical bytes ARE the artifact file bytes: the model hash is not an
    # unrelated digest of a differently formatted JSON representation.
    with (out/'minions_reference_baseline_v1.json').open('xb') as handle:
        handle.write(canonical_bytes(artifact))
    scan=scan_video(context['source'],templates,config)
    ranked=rank_events(merge_events(scan['observations'],window=config.merge_seconds,floor=threshold))
    write_json(out/'final-development.json',dict(ranking=ranked,scan=scan,
        evaluation=[evaluate(ranked,p) for p in context['plays']],development_only=True))
    now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    contract=dict(schema_version=1,experiment_id=context['development']['experiment_id'],freeze_version=1,
        created_at=now,development_lock_sha256=context['development']['sha256'],target=context['target'],
        git_commit=git,model_sha256=artifact_sha(artifact),development_session_id='module2b1_development',
        test_pixels_unseen=True,precise_test_gt_unseen=True,
        **reference_model_parameters(context['recording'],config),
        confidence_threshold=threshold,evaluation_protocol_version=1,
        artifact_type='reference_template_matcher',baseline=dict(artifact_sha256=artifact_sha(artifact),
            config=config.document(),templates=artifact['templates'],score_method=artifact['score_method'],
            event_merge=artifact['event_merge'],threshold_derivation=artifact['threshold_derivation'],
            opencv_version=artifact['opencv_version'],evaluation_protocol_version=1))
    model=freeze_model(contract,context['development'],out/'locks')
    verify_model_semantics(artifact,model)
    if file_hash(context['source'])!=context['recording']['source_sha256']:
        raise EvidenceError('Source changed while building the baseline.')
    return dict(status='MODEL_LOCKED',artifact_sha256=artifact_sha(artifact),model_lock_sha256=model['sha256'])


class Parser(argparse.ArgumentParser):
    def error(self,message): raise EvidenceError('Invalid baseline arguments.')


def cli_main(argv=None):
    parser=Parser(description='Offline development-only template baseline; no gameplay interaction.')
    subs=parser.add_subparsers(dest='command',required=True,parser_class=Parser)
    for name in ('crossval','build'):
        p=subs.add_parser(name); p.add_argument('source'); p.add_argument('--development',required=True)
        p.add_argument('--indexes',nargs='+',required=True); p.add_argument('--output',required=True)
        if name=='build': p.add_argument('--crossval',required=True)
    p=subs.add_parser('validate-lock'); p.add_argument('model'); p.add_argument('--development',required=True)
    p.add_argument('--artifact',required=True); p.add_argument('--source',required=True); p.add_argument('--indexes',nargs='+',required=True)
    try:
        args=parser.parse_args(argv)
        context=development_context(args.development,args.indexes,args.source)
        if args.command=='crossval':
            result=crossval(context,args.output); print(result['status']); return 0 if result['status']=='2B1_CROSSVAL_PASS' else 3
        if args.command=='build':
            result=build_baseline(context,args.crossval,args.output); print(result['status']); return 0
        model=load_lock(args.model,context['development'])
        artifact=load_evidence(safe_path(args.artifact,private=True))
        templates=[t for group in context['templates'].values() for t in group]
        verify_artifact(artifact,model['payload']['model_sha256'],templates)
        if file_hash(safe_path(args.artifact,private=True))!=model['payload']['model_sha256']:
            raise EvidenceError('Artifact file bytes differ from Model Lock.')
        verify_model_semantics(artifact,model)
        print('Baseline and Model Lock valid.'); return 0
    except (EvidenceError,pipeline.VideoError,OSError,ValueError,TypeError,KeyError,
            AttributeError,OverflowError,RecursionError,av.FFmpegError,cv2.error):
        print('Invalid baseline command or local frozen evidence.',file=sys.stderr); return 2


if __name__=='__main__':
    raise SystemExit(cli_main())
