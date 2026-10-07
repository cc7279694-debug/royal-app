"""Read-only Human visual GT adapter. Does not import or read Event GT."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from tools.preannotation.contract import bbox, bundle_digest, digest, require
from .engine import validate_observations


MAX_JSON = 16*1024*1024


def read_json(path):
    path=Path(path)
    require(path.is_file() and path.stat().st_size<=MAX_JSON, 'missing or oversized Oracle metadata')
    def pairs(rows):
        result={}
        for k,v in rows:
            require(k not in result,'duplicate Oracle JSON key');result[k]=v
        return result
    def invalid(_): raise ValueError('non-finite Oracle JSON number')
    def decimal(s):
        value=float(s);require(math.isfinite(value),'non-finite Oracle JSON number');return value
    value=json.loads(path.read_text('utf-8'),object_pairs_hook=pairs,parse_constant=invalid,parse_float=decimal)
    require(isinstance(value,dict),'Oracle JSON object required')
    return value


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def _attestation(s):
    require(s.get('actual_human_confirmation') is True and s.get('human_review_attested') is True
            and s.get('reviewer')=='user' and s.get('review_basis')=='chatgpt_visual_review'
            and s.get('confirmation_source')=='user_attestation_based_on_chatgpt_visual_review',
            'explicit user visual-review attestation required')


def multiclass_observations(bundle, annotations, supplement, *, match_id):
    _attestation(supplement)
    expected=bundle_digest(bundle)
    require(annotations.get('bundle_sha256')==expected and supplement.get('bundle_sha256')==expected,
            'visual source bundle binding mismatch')
    frames={}; metadata=[]
    origin=Fraction(bundle['source_origin_seconds_exact'])
    for f in bundle['frames']:
        require(f['frame_id'] not in frames,'duplicate source frame')
        require(type(f['raw_pts']) is int and Fraction(f['time_base'])>0,'invalid frame PTS')
        t=float(f['raw_pts']*Fraction(f['time_base'])-origin)
        require(t==f['source_relative_seconds'] and t>=0,'frame PTS/time mismatch')
        frames[f['frame_id']]=(f,t)
        metadata.append({'frame_id':f['frame_id'],'match_id':match_id,'recording_id':bundle['recording_id'],
                         'timestamp':t,'raw_pts':f['raw_pts'],'time_base':f['time_base'],
                         'absence_is_negative':False})
    boxes=annotations['positive_boxes']; seen=set(); group_times={}; identities={}
    for row in boxes:
        require(row['object_id'] not in seen,'duplicate accepted object'); seen.add(row['object_id'])
        require(row['human_confirmed'] is True and row['decision']=='accepted','only confirmed human visuals may enter Oracle')
        require(row['recording_id']==bundle['recording_id'] and row['frame_id'] in frames,'object recording/frame mismatch')
        f,t=frames[row['frame_id']]; bbox(row['bbox_xyxy'],f['width'],f['height'])
        identity=supplement['object_identity_semantics'][row['object_id']]
        require(identity['appearance_id']==row['appearance_id'],'human identity metadata mismatch')
        identities[row['object_id']]=identity
        g=row['appearance_id']
        if (identity.get('identity_status')=='user_group_assignment' and
            identity.get('scope')=='user_confirmed_appearance_group' and
            (identity.get('continuity_asserted') is True or g in supplement.get('explicit_user_appearance_groups',[]))):
            group_times.setdefault(g,set()).add(t)
    observations=[]
    for row in boxes:
        g=row['appearance_id']; strong=len(group_times.get(g,set()))>=2
        observations.append({'observation_id':row['object_id'],'match_id':match_id,
            'timestamp':frames[row['frame_id']][1],'visual_class':row['visual_class'],
            'bbox':list(row['bbox_xyxy']),'owner':row['owner'],'form':row['form'],
            'origin_kind':row['origin'],'appearance_group_id':g if strong else None,'confidence':None,
            'source':'human_gt_continuity' if strong else 'human_gt'})
    validate_observations(observations)
    observations.sort(key=lambda r:(r['match_id'],r['timestamp'],r['observation_id']))
    return observations, {'frame_count':len(frames),'box_count':len(boxes),'frames':metadata,
                          'unreviewed_is_negative':False,'teacher_confidence_used':False,
                          'identity_policy':'only human-continuity groups with multiple source times; observation tokens omitted'}


def _member(root, name):
    require(isinstance(name,str) and bool(name) and ':' not in name and '\\' not in name
            and not Path(name).is_absolute() and '..' not in Path(name).parts,'unsafe visual lock member')
    p=root/name
    require(p.resolve().is_relative_to(root.resolve()),'visual lock member escaped source root')
    return p


def load_multiclass_source(lock_path, *, expected_sha):
    lock_path=Path(lock_path); require(file_sha(lock_path)==expected_sha,'visual lock SHA mismatch')
    lock=read_json(lock_path);_attestation(lock)
    require(lock['lock_digest_sha256']==digest({k:v for k,v in lock.items() if k!='lock_digest_sha256'}),
            'visual lock semantic digest mismatch')
    for name,h in lock['files'].items():
        require(file_sha(_member(lock_path.parent,name))==h,'visual lock member SHA mismatch')
    root=lock_path.parent
    a=read_json(root/'reviewed-annotations.json');s=read_json(root/'confirmation-supplement.json')
    # The private lock directory's sibling contains the immutable source bundle.
    bundle_root=lock_path.parent.parents[2]/lock['bundle_directory']
    b=read_json(bundle_root/'bundle.json')
    require(file_sha(bundle_root/'manifest.json')==lock['source_bundle_manifest_file_sha256'],
            'source bundle manifest SHA mismatch')
    require(bundle_digest(b)==lock['bundle_sha256'],'source bundle content differs from visual lock')
    rows,meta=multiclass_observations(b,a,s,match_id=lock['underlying_match_id'])
    meta.update(lock_sha256=expected_sha,scope='multiclass_human_visual_gt',
                source_metadata_sha256={'annotations':file_sha(root/'reviewed-annotations.json'),
                                        'supplement':file_sha(root/'confirmation-supplement.json')})
    return rows,meta


def _fraction(value):
    return Fraction(value['numerator'],value['denominator'])


def load_legacy_smoke_source(lock_path, *, expected_sha):
    """All existing accepted legacy visual objects, not a selection by event truth."""
    require(file_sha(lock_path)==expected_sha,'legacy visual lock SHA mismatch')
    lock=read_json(lock_path); gt=lock['payload']
    require(lock['gt_semantic_sha256']==digest(gt),'legacy GT semantic binding mismatch')
    require(lock['digest']==digest({k:v for k,v in lock.items() if k!='digest'}),'legacy lock digest mismatch')
    sources={r['recording_id']:r['recording_metadata'] for r in gt['source_bindings']}
    frames={f['frame_id']:f for f in gt['frames']};require(len(frames)==len(gt['frames']),'duplicate legacy frame')
    groups={g['appearance_group_id']:g for g in gt['groups']}
    times={};frame_meta=[]
    for f in frames.values():
        meta=sources[f['recording_id']]
        t=float(f['raw_pts']*_fraction(f['time_base'])-meta['origin_pts']*_fraction(meta['origin_time_base']))
        require(t==f['timestamp_seconds'],'legacy PTS mismatch'); times[f['frame_id']]=t
        frame_meta.append({'frame_id':f['frame_id'],'match_id':f['underlying_match_id'],'timestamp':t,
                           'recording_id':f['recording_id'],'absence_is_negative':False})
    rows=[]
    for row in gt['positive_objects']:
        require(row['review_state']=='confirmed' and row['frame_id'] in frames,'unconfirmed legacy visual')
        f=frames[row['frame_id']];group=groups[row['appearance_group_id']]
        require(row['underlying_match_id']==f['underlying_match_id'] and row['recording_id']==f['recording_id'],
                'legacy match/recording identity mismatch')
        x,y,w,h=row['bbox_xywh_pixels']; b=[x,y,x+w,y+h];bbox(b,*f['image_size'])
        continuity=group['continuity_confirmed'] is True
        cls='visual.'+row['visual_class'].replace('-','_')
        rows.append({'observation_id':'legacy-'+row['object_id'],'match_id':row['underlying_match_id'],
            'timestamp':times[row['frame_id']],'visual_class':cls,'bbox':b,'owner':row['owner'],
            'form':row['form'],'origin_kind':row['origin_kind'],'appearance_group_id':row['appearance_group_id'] if continuity else None,
            'confidence':None,'source':'human_gt_continuity' if continuity else 'human_gt'})
    validate_observations(rows)
    return rows,{'frame_count':len(frames),'box_count':len(rows),'frames':frame_meta,
                 'lock_sha256':expected_sha,'scope':'legacy_confirmed_visual_continuity_regression',
                 'deployment_assertions_used':False,'unreviewed_is_negative':False}
