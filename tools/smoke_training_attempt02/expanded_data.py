"""Bounded Attempt02 snapshot and ROI export, without model dependencies.

Human decisions are supplied separately and bound to the immutable review ZIP.
Digests establish consistency, not authenticity or legal rights clearance.
The older GT/Dataset Locks and extractors are never overwritten or extended.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
import sys
import zipfile

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'smoke_training'))
from smoke_data import (canonical, file_sha, load_locked, private_path, require,
                        strict_json, write_json)
from data_contract import CLASS_SCHEMA, annotation_digest, bbox_to_roi, fixed_roi, qualify_frame, validate_class_schema


def _unique(rows, key, message):
    require(isinstance(rows, list) and all(isinstance(r, dict) and isinstance(r.get(key), str) for r in rows), message)
    require(len({r[key] for r in rows}) == len(rows), message)
    return {r[key]: r for r in rows}


def _safe_name(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,100}', value) is not None,
            'Unsafe artifact identity')
    require(value.split('.')[0].upper() not in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]},
            'Reserved artifact identity')
    return value


def _sorted_frames(rows):
    return sorted(rows, key=lambda f: (f['timestamp_seconds'], f['frame_id']))


def assemble_snapshot(review_index, drafts, human, parent, bindings):
    """Pure normalization of exact current review decisions; no inferred review.

Old TRAIN annotations/coverage inherit the parent. Every new object and frame
requires an explicit user-relayed human decision. Accepted partial-frame boxes
stay in the snapshot but cannot enter ordinary background training loss.
"""
    validate_class_schema(review_index['class_schema'])
    require(human.get('status') == 'ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED'
            and human.get('confirmation_source') == 'user_relayed_chatgpt'
            and isinstance(human.get('reviewer'), str) and bool(human['reviewer'].strip()),
            'Explicit attributed human return required')
    require(human.get('review_packet_sha256') == bindings['review_packet_sha256'], 'Wrong review packet binding')
    require(human.get('user_authorization_scope') == 'private_local_research_poc', 'Current local training scope required')
    frames = _unique(deepcopy(review_index['frames']), 'frame_id', 'Duplicate or invalid review frame')
    all_objects = _unique(deepcopy(drafts['objects']), 'object_id', 'Duplicate or invalid review object')
    parent_gt = parent['gt_snapshot']
    old_frames = {f['frame_id']: f for f in parent_gt['frames'] if f['split'] == 'TRAIN'}
    old_objects = {o['object_id']: o for o in parent_gt['positive_objects'] if o['underlying_match_id'] == 'natural_match_01'}
    decisions = _unique(human['objects'], 'object_id', 'Duplicate or invalid object decision')
    coverage = _unique(human['frame_coverage_confirmations'], 'frame_id', 'Duplicate frame coverage decision')
    require(set(decisions) == set(all_objects) - set(old_objects), 'Each new draft needs exactly one decision')
    require(set(coverage) == set(frames) - set(old_frames), 'Each new frame needs exactly one coverage decision')
    require(set(old_frames) <= set(frames) and set(old_objects) <= set(all_objects), 'Parent TRAIN identities missing')
    accepted, rejected = [], []
    for oid, o in sorted(all_objects.items()):
        require(o['frame_id'] in frames, 'Object references unknown frame')
        if oid in old_objects:
            require(all(o.get(k) == value for k, value in old_objects[oid].items()), 'Prior confirmed object changed')
        else:
            d = decisions[oid]
            require(d.get('corrected_visual_class') in (None, o['visual_class'])
                    and d.get('corrected_bbox_xywh_pixels') in (None, o['bbox_xywh_pixels']),
                    'This review accepts original boxes/classes only')
            require(d.get('decision') in ('confirm', 'reject'), 'Unconfirmed object decision')
            if d['decision'] == 'reject':
                reason = d.get('uncertain_reason') or d.get('reason')
                require(isinstance(reason, str) and bool(reason.strip()), 'Rejected proposal needs a reason')
                o.update(review_state='rejected', state='rejected', reject_reason=reason,
                         is_negative=False, confirmation_source=human['confirmation_source'])
                rejected.append(o)
                continue
            for key in ('owner','form','origin_kind','source_relationship','appearance_group_id'):
                require(key in d and d[key] is not None or key == 'source_relationship', 'Confirmed metadata missing')
                o[key] = d.get(key)
            o.update(review_state='confirmed', state='confirmed', confirmed_by=human['reviewer'],
                     confirmation_source=human['confirmation_source'], uncertain_reason=None)
        o['class_id'] = CLASS_SCHEMA[o['visual_class']]
        o['bbox_xywh_roi'] = bbox_to_roi(o['bbox_xywh_pixels'], frames[o['frame_id']]['image_size'])
        accepted.append(o)
    draft_groups = _unique(deepcopy(drafts['groups']), 'appearance_group_id', 'Duplicate appearance group')
    group_decisions = _unique(human['group_decisions'], 'appearance_group_id', 'Duplicate group decision')
    require(set(draft_groups) == set(group_decisions), 'Every group needs a decision or explicit parent inheritance')
    parent_groups = {g['appearance_group_id']: g for g in parent_gt['groups'] if g['underlying_match_id'] == 'natural_match_01'}
    groups = []
    for gid, draft in sorted(draft_groups.items()):
        d = group_decisions[gid]
        if d.get('decision') == 'inherit_parent':
            require(gid in parent_groups, 'Only confirmed parent groups may be inherited')
            g = deepcopy(parent_groups[gid])
        else:
            require(d.get('decision') == 'accept', 'Unconfirmed appearance group')
            g = deepcopy(parent_groups.get(gid, draft))
            for key in ('continuity_confirmed','source_relationship_confirmed','independent_deployment_confirmed'):
                if d.get(key) is not None: g[key] = d[key]
            if gid not in parent_groups:
                require(g.get('independent_deployment_confirmed') is False, 'Expanded frames cannot invent deployments')
            else:
                require(g.get('independent_deployment_confirmed') == parent_groups[gid]['independent_deployment_confirmed'],
                        'Old deployment confirmation cannot change')
            g.update(decision='accept', review_state='accepted')
            if d.get('note') is not None: g['notes'] = d['note']
        g['positive_object_ids'] = sorted(o['object_id'] for o in accepted if o['appearance_group_id'] == gid)
        require(bool(g['positive_object_ids']), 'Accepted group lacks confirmed positives')
        if g['origin_kind'] == 'spawned':
            require(g.get('source_relationship_confirmed') is True, 'Spawned relationship needs human confirmation')
        else:
            require(g.get('continuity_confirmed') is True, 'Non-spawned appearance continuity needs confirmation')
        groups.append(g)
    reviews, standard, partial = [], [], []
    for fid, f in frames.items():
        require(f['underlying_match_id'] == 'natural_match_01' and f['split'] == 'TRAIN', 'TRAIN match isolation violated')
        if fid in old_frames:
            prior = old_frames[fid]
            for key in ('frame_id','image_sha256','image_size','raw_pts','time_base','underlying_match_id','timestamp_seconds'):
                require(f[key] == prior[key], 'Parent frame binding changed')
            c = {'exhaustive_for_selected_classes':True, 'negative_confirmed':False,
                 'remaining_unknown_regions':'none_material'}
            require(prior.get('complete_frame_supervision_coverage', True) is True, 'Prior TRAIN frame incomplete')
        else:
            c = coverage[fid]
            require(c.get('additional_objects') == [], 'Additional annotations were not reviewed in this packet')
        complete = c.get('exhaustive_for_selected_classes')
        require(type(complete) is bool and type(c.get('negative_confirmed')) is bool, 'Explicit frame coverage/negative decision needed')
        f_objects = [o for o in accepted if o['frame_id'] == fid]
        f_rejected = [o for o in rejected if o['frame_id'] == fid]
        require(c['negative_confirmed'] == (not bool(f_objects)) and (not c['negative_confirmed'] or complete),
                'Unknown or partial cannot become a negative')
        require(not complete or not f_rejected, 'Rejected regions cannot enter standard background loss')
        unknown = c.get('remaining_unknown_regions')
        require((complete and unknown == 'none_material') or (not complete and isinstance(unknown,str) and unknown not in ('','none_material')),
                'Coverage and material Unknown conflict')
        f.update(positive_object_ids=sorted(o['object_id'] for o in f_objects), review_state='confirmed',
                 exhaustive_for_selected_classes=complete, negative_confirmed=c['negative_confirmed'],
                 remaining_unknown_regions=unknown, roi_xyxy=fixed_roi(f['image_size']),
                 standard_full_frame_loss_allowed=complete, standard_training_loss_allowed=complete,
                 complete_frame_supervision_coverage=complete, unknown_not_negative=True)
        review = {'review_id':f'Attempt02:{fid}', 'reviewer':human['reviewer'], 'review_kind':'human_relayed_chatgpt',
                  'review_state':'confirmed','frame_id':fid,'image_sha256':f['image_sha256'],
                  'annotation_sha256':annotation_digest(f,f_objects), 'selected_classes_exhaustive':list(CLASS_SCHEMA),
                  'material_unknown':not complete,'roi_xyxy':fixed_roi(f['image_size']),
                  'negative_confirmed':c['negative_confirmed']}
        reviews.append(review)
        (standard if complete else partial).append(fid)
    dev_frames = _sorted_frames(deepcopy([f for f in parent_gt['frames'] if f['split'] == 'DEV_VAL']))
    for f in dev_frames:
        f.update(split='DEV_TUNE', standard_full_frame_loss_allowed=False,
                 standard_full_frame_metrics_allowed=f['complete_frame_supervision_coverage'],
                 roi_xyxy=fixed_roi(f['image_size']))
    dev_objects = sorted(deepcopy([o for o in parent_gt['positive_objects'] if o['underlying_match_id'] == 'natural_match_04']), key=lambda o:o['object_id'])
    p = {'kind':'attempt02_expanded_gt_snapshot', 'schema_version':1, 'class_schema':deepcopy(CLASS_SCHEMA),
         'split_unit':'underlying_match', 'match_splits':{'natural_match_01':'TRAIN','natural_match_04':'DEV_TUNE'},
         'train_frames':_sorted_frames(list(frames.values())), 'accepted_objects':accepted,'rejected_objects':rejected,
         'groups':groups,'frame_reviews':sorted(reviews,key=lambda r:r['frame_id']),
         'standard_train_frame_ids':sorted(standard),'partial_frame_ids':sorted(partial),
         'dev_tune_snapshot':{'frames':dev_frames,'objects':dev_objects},
         'provenance_scope':deepcopy(parent['provenance']), 'rights_clearance':'unverified',
         'training_qualification_scope':'clash_tracker_private_local_research_poc_gate_only',
         'training_qualified':True,'is_blind_test_dataset':False,'is_production_model_lock':False,
         'owner_discrimination_qualified':False, 'unknown_unmatched':'unjudged',
         'fp_time_denominator_seconds':None,'human_review':deepcopy(human),
         **deepcopy(bindings)}
    # Stable ordering applies to all unordered decision arrays, not just labels.
    for field,key in [('objects','object_id'),('group_decisions','appearance_group_id'),('frame_coverage_confirmations','frame_id')]:
        p['human_review'][field] = sorted(p['human_review'][field],key=lambda r:r[key])
    counts = Counter(o['visual_class'] for o in accepted if o['frame_id'] in standard)
    p['counts']={'TRAIN':{'images':len(standard),'negative_images':sum(not frames[f]['positive_object_ids'] for f in standard),
                         'positive_images':sum(bool(frames[f]['positive_object_ids']) for f in standard),**dict(counts)},
                 'DEV_TUNE':{'images':len(dev_frames),**dict(Counter(o['visual_class'] for o in dev_objects))}}
    p['confirmed_train_witch_deployments'] = sum(g['visual_class']=='unit.witch' and g['independent_deployment_confirmed'] is True for g in groups)
    p['skeleton_card_deployments'] = sum(g['visual_class']=='unit.skeleton' and g['independent_deployment_confirmed'] is True for g in groups)
    validate_snapshot(p)
    return p


def validate_snapshot(p):
    """Validate the bounded supervision semantics; file bindings are separate."""
    validate_class_schema(p['class_schema'])
    frames = _unique(p['train_frames'],'frame_id','Duplicate TRAIN frame')
    objects = _unique(p['accepted_objects'],'object_id','Duplicate accepted object')
    rejected = _unique(p['rejected_objects'],'object_id','Duplicate rejected object')
    reviews = _unique(p['frame_reviews'],'frame_id','Duplicate frame review')
    require(len(frames)==16 and len(objects)==17 and len(rejected)==4 and not set(objects)&set(rejected), 'Expanded GT identity/count conflict')
    standard=set(p['standard_train_frame_ids']); partial=set(p['partial_frame_ids'])
    require(len(standard)==len(p['standard_train_frame_ids'])==14 and len(partial)==len(p['partial_frame_ids'])==2
            and not standard&partial and standard|partial==set(frames) and set(reviews)==set(frames), 'Standard/partial frame partition differs')
    require({frames[f]['timestamp_seconds'] for f in partial}=={162,165}, 'Confirmed partial frames cannot become background')
    for fid,f in frames.items():
        _safe_name(fid)
        require(f['underlying_match_id']=='natural_match_01' and f['split']=='TRAIN', 'TRAIN match leak')
        ids={oid for oid,o in objects.items() if o['frame_id']==fid}
        require(ids==set(f['positive_object_ids']) and len(ids)==len(f['positive_object_ids']), 'Frame/object coverage conflict')
        require(f['standard_full_frame_loss_allowed'] is (fid in standard), 'Background-loss permission conflict')
        for oid in ids:
            _safe_name(oid)
            o=objects[oid]
            require(o['class_id']==CLASS_SCHEMA[o['visual_class']] and type(o['class_id']) is int
                    and o['review_state']=='confirmed' and o['owner']=='opponent' and o['form']=='unknown', 'Confirmed class/metadata conflict')
            require(o['bbox_xywh_roi']==bbox_to_roi(o['bbox_xywh_pixels'],f['image_size']), 'ROI annotation conflict')
        if fid in standard:
            require(not any(o['frame_id']==fid for o in rejected.values()), 'Rejected region cannot become Negative')
            qualify_frame(f,[objects[oid] for oid in sorted(ids)],reviews[fid])
        else:
            require(reviews[fid]['material_unknown'] is True and f['negative_confirmed'] is False, 'Partial Unknown lost')
    require(p['counts']['TRAIN']=={'images':14,'negative_images':8,'positive_images':6,'unit.skeleton':9,'unit.witch':6}, 'TRAIN qualification/count conflict')
    actual_counts=Counter(o['visual_class'] for o in objects.values() if o['frame_id'] in standard)
    actual_train={'images':len(standard),'negative_images':sum(not frames[f]['positive_object_ids'] for f in standard),
                  'positive_images':sum(bool(frames[f]['positive_object_ids']) for f in standard),**dict(actual_counts)}
    require(actual_train==p['counts']['TRAIN'], 'Actual standard supervision counts differ')
    require(p['counts']['DEV_TUNE']=={'images':2,'unit.skeleton':3,'unit.witch':2}, 'DEV_TUNE count conflict')
    dev=p['dev_tune_snapshot']; dfs=_unique(dev['frames'],'frame_id','Duplicate DEV frame'); dos=_unique(dev['objects'],'object_id','Duplicate DEV object')
    require(len(dfs)==2 and len(dos)==5 and not set(dfs)&set(frames), 'DEV identity/count conflict')
    require(Counter(o['visual_class'] for o in dos.values())=={'unit.skeleton':3,'unit.witch':2}, 'Actual DEV class counts differ')
    require(all(f['underlying_match_id']=='natural_match_04' and f['split']=='DEV_TUNE'
                and f['standard_full_frame_loss_allowed'] is False for f in dfs.values()), 'DEV_TUNE must never enter TRAIN')
    require(p['confirmed_train_witch_deployments']==1 and p['skeleton_card_deployments']==0, 'Frame expansion cannot inflate deployments')
    groups=_unique(p['groups'],'appearance_group_id','Duplicate group identity')
    require(len(groups)==4, 'Expected inherited and expanded appearance groups')
    for gid,g in groups.items():
        ids={oid for oid,o in objects.items() if o['appearance_group_id']==gid}
        require(ids and ids==set(g['positive_object_ids']) and len(ids)==len(g['positive_object_ids']), 'Group/object references differ')
        require(g['underlying_match_id']=='natural_match_01' and all(objects[oid]['visual_class']==g['visual_class'] for oid in ids), 'Group class/match conflict')
        require(type(g['independent_deployment_confirmed']) is bool, 'Group deployment confirmation must be explicit')
    require(sum(g['visual_class']=='unit.witch' and g['independent_deployment_confirmed'] for g in groups.values())==1
            and not any(g['visual_class']=='unit.skeleton' and g['independent_deployment_confirmed'] for g in groups.values()), 'Actual group deployment counts differ')
    scope=p['provenance_scope']
    require(scope.get('source_type')=='user_recorded_gameplay' and scope.get('intended_use')=='private_local_research_poc'
            and scope.get('user_training_authorized') is True and scope.get('external_upload') is False
            and scope.get('redistribution') is False and scope.get('rights_clearance')=='unverified', 'Private provenance scope differs')
    return p


def _bundle_file(root,bundle,relative):
    require(isinstance(relative,str) and not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'Unsafe bundle path')
    return private_path(root,bundle/relative)


def validate_packet_bundle(bundle,packet,manifest):
    """Bind the actual reviewed ZIP to its unchanged local presentation files."""
    try:
        with zipfile.ZipFile(packet) as archive:
            entries=archive.infolist(); names=[entry.filename for entry in entries]
            require(len(names)==len(set(names)) and set(names)==set(manifest['files'])|{'manifest.json'},
                    'Reviewed ZIP member inventory conflict')
            require(sum(entry.file_size for entry in entries)<=512*1024*1024
                    and all(entry.file_size<=32*1024*1024 for entry in entries), 'Reviewed ZIP bounds exceeded')
            require(archive.read('manifest.json')==(Path(bundle)/'manifest.json').read_bytes(),
                    'Local bundle differs from actual reviewed ZIP manifest')
            for relative,digest in manifest['files'].items():
                require(sha256(archive.read(relative)).hexdigest()==digest, 'Reviewed ZIP member differs from bound manifest')
    except (zipfile.BadZipFile,KeyError) as error:
        raise ValueError('Invalid reviewed ZIP') from error


def build_snapshot(root,bundle_path,human_return_path,parent_dataset_lock_path):
    """Read-only bind current human return, packet, original files and parent."""
    root=Path(root).resolve(); bundle=private_path(root,bundle_path)
    hr=private_path(root,human_return_path); parent_path=private_path(root,parent_dataset_lock_path)
    parent=load_locked(root,parent_path); human=strict_json(hr)
    packet=private_path(root,human['review_packet_path'])
    require(file_sha(packet)==human['review_packet_sha256'], 'Review ZIP bytes changed')
    manifest=strict_json(bundle/'manifest.json')
    validate_packet_bundle(bundle,packet,manifest)
    for rel,digest in manifest['files'].items():
        require(file_sha(_bundle_file(root,bundle,rel))==digest, 'Original review bundle changed')
    require(manifest['parent_dataset_sha256']==file_sha(parent_path)
            and manifest['parent_gt_sha256']==parent['smoke_gt_lock_reference']['file_sha256'], 'Review parent lock changed')
    review=strict_json(bundle/'review-index.json'); drafts=strict_json(bundle/'draft-annotations.json')
    bindings={'parent_dataset_sha256':file_sha(parent_path),'parent_gt_sha256':manifest['parent_gt_sha256'],
              'human_return_sha256':file_sha(hr),'review_packet_sha256':file_sha(packet),
              'references':{'bundle_path':bundle.relative_to(root).as_posix(),'human_return_path':hr.relative_to(root).as_posix(),
                            'parent_dataset_lock_path':parent_path.relative_to(root).as_posix()},
              'review_manifest_sha256':file_sha(bundle/'manifest.json'), 'source_bindings':deepcopy(review['source_bindings'])}
    p=assemble_snapshot(review,drafts,human,parent,bindings)
    for binding in p['source_bindings']:
        for kind in ('index','report'):
            require(file_sha(private_path(root,binding[kind]))==binding[kind+'_sha256'], 'Original index/report changed')
    for f in p['train_frames']+p['dev_tune_snapshot']['frames']:
        image=private_path(root,f['source_image_relative_to_repo'])
        require(file_sha(image)==f['image_sha256'], 'Original frame changed')
        with Image.open(image) as img: require(list(img.size)==f['image_size'], 'Original dimensions changed')
    return p


def freeze_snapshot(root,path,payload):
    """Exclusive deterministic v2 snapshot; never overwrite either old/new lock."""
    path=private_path(root,path); validate_snapshot(payload)
    rebuilt=build_snapshot(root,**payload['references'])
    require(canonical(rebuilt)==canonical(payload), 'Snapshot differs from bound human return')
    envelope={'kind':'attempt02_expanded_gt_lock','freeze_version':2,
              'snapshot_sha256':sha256(canonical(payload)).hexdigest(),'payload':deepcopy(payload)}
    envelope['digest']=sha256(canonical(envelope)).hexdigest()
    path.parent.mkdir(parents=True,exist_ok=True)
    write_json(path,envelope)
    return envelope


def load_expanded(root,path):
    lock=strict_json(private_path(root,path))
    require(lock['kind']=='attempt02_expanded_gt_lock' and lock['freeze_version']==2, 'Wrong expanded lock kind/version')
    require(lock['digest']==sha256(canonical({k:v for k,v in lock.items() if k!='digest'})).hexdigest(), 'Expanded lock digest mismatch')
    p=lock['payload']
    require(lock['snapshot_sha256']==sha256(canonical(p)).hexdigest(), 'Expanded snapshot digest mismatch')
    rebuilt=build_snapshot(root,**p['references'])
    require(canonical(rebuilt)==canonical(p), 'Expanded lock conflicts with bound human/source data')
    return p


def _coco(p,split):
    frames=p['train_frames'] if split=='TRAIN' else p['dev_tune_snapshot']['frames']
    objects=p['accepted_objects'] if split=='TRAIN' else p['dev_tune_snapshot']['objects']
    if split=='TRAIN': frames=[f for f in frames if f['frame_id'] in p['standard_train_frame_ids']]
    data={'images':[],'annotations':[],'categories':[{'id':index,'name':name} for name,index in CLASS_SCHEMA.items()]}
    by_object={o['object_id']:o for o in objects}
    for f in _sorted_frames(frames):
        fid=_safe_name(f['frame_id']); left,top,right,bottom=fixed_roi(f['image_size'])
        record={'id':len(data['images'])+1,'file_name':f'images/{split}/{fid}.png',
                'width':right-left,'height':bottom-top,'frame_id':fid,'timestamp_seconds':f['timestamp_seconds'],
                'underlying_match_id':f['underlying_match_id'],'split':split,'original_image_size':f['image_size'],
                'source_image_relative_to_repo':f['source_image_relative_to_repo'],
                'roi_xyxy':[left,top,right,bottom],'negative_confirmed':f.get('negative_confirmed',False),
                'standard_full_frame_loss_allowed':split=='TRAIN',
                'standard_full_frame_metrics_allowed':f['complete_frame_supervision_coverage'],
                'unlabeled_regions_are_negative':False,'unknown_unmatched':'unjudged'}
        data['images'].append(record)
        for oid in sorted(f['positive_object_ids']):
            o=by_object[oid]; bbox=bbox_to_roi(o['bbox_xywh_pixels'],f['image_size'])
            data['annotations'].append({'id':len(data['annotations'])+1,'image_id':record['id'],
                  'object_id':oid,'category_id':CLASS_SCHEMA[o['visual_class']],'bbox':bbox,
                  'area':bbox[2]*bbox[3],'iscrowd':0,'gt_metadata':deepcopy(o)})
    return data


def export_expanded(root,payload,directory,lock_sha):
    validate_snapshot(payload)
    require(canonical(build_snapshot(root,**payload['references']))==canonical(payload), 'Unbound expanded export')
    require(isinstance(lock_sha,str) and re.fullmatch('[0-9a-f]{64}',lock_sha), 'Lock SHA required')
    directory=private_path(root,directory)
    require(not directory.exists(), 'Expanded export is immutable')
    directory.mkdir(parents=True)
    manifest={'kind':'attempt02_roi_export','expanded_lock_sha256':lock_sha,
              'snapshot':deepcopy(payload),'class_schema':deepcopy(CLASS_SCHEMA),
              'counts':deepcopy(payload['counts']),'files':{},'fp_time_denominator_seconds':None}
    by_frame={f['frame_id']:f for f in payload['train_frames']+payload['dev_tune_snapshot']['frames']}
    (directory/'annotations').mkdir()
    for split,name in [('TRAIN','train.json'),('DEV_TUNE','dev_tune.json')]:
        data=_coco(payload,split); (directory/'images'/split).mkdir(parents=True)
        for image in data['images']:
            f=by_frame[image['frame_id']]; path=directory/image['file_name']
            with Image.open(private_path(root,f['source_image_relative_to_repo'])) as original:
                with path.open('xb') as output: original.convert('RGB').crop(fixed_roi(f['image_size'])).save(output,format='PNG')
            manifest['files'][image['file_name']]=file_sha(path)
        rel=f'annotations/{name}';write_json(directory/rel,data);manifest['files'][rel]=file_sha(directory/rel)
    manifest['digest']=sha256(canonical(manifest)).hexdigest()
    write_json(directory/'manifest.json',manifest)
    return validate_export(root,directory)


def validate_export(root,directory):
    directory=private_path(root,directory); m=strict_json(directory/'manifest.json')
    require(m['digest']==sha256(canonical({k:v for k,v in m.items() if k!='digest'})).hexdigest(), 'Export manifest digest mismatch')
    p=m['snapshot'];validate_snapshot(p)
    require(canonical(build_snapshot(root,**p['references']))==canonical(p), 'Export snapshot no longer matches human/parent binding')
    validate_class_schema(m['class_schema']);require(m['counts']==p['counts'],'Export count conflict')
    expected_files=set();by_frame={f['frame_id']:f for f in p['train_frames']+p['dev_tune_snapshot']['frames']}
    for split,name in [('TRAIN','train.json'),('DEV_TUNE','dev_tune.json')]:
        rel=f'annotations/{name}';expected_files.add(rel);expected=_coco(p,split)
        require(strict_json(directory/rel)==expected, 'Exact exported image/annotation/GT metadata mismatch')
        for image in expected['images']:
            rel=image['file_name'];expected_files.add(rel);f=by_frame[image['frame_id']]
            with Image.open(private_path(root,f['source_image_relative_to_repo'])) as original, Image.open(private_path(root,directory/rel)) as actual:
                want=original.convert('RGB').crop(fixed_roi(f['image_size']))
                require(actual.mode=='RGB' and actual.size==want.size and actual.tobytes()==want.tobytes(), 'Export is not exact fixed-ROI original pixels')
    require(set(m['files'])==expected_files, 'Export file inventory conflict')
    for rel,digest in m['files'].items():
        require(file_sha(private_path(root,directory/rel))==digest, 'Exported artifact changed')
    actual={f.relative_to(directory).as_posix() for f in directory.rglob('*') if f.is_file()}
    require(actual==expected_files|{'manifest.json'}, 'Unlisted artifact in expanded export')
    return m
