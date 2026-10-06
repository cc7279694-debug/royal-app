"""Portable, narrow data/evaluation helpers for the approved Phase C snapshot.

No model imports or historical schema changes. All artifacts stay Git-ignored.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import subprocess

DATASET_SHA = '582dc30d3e418aebf09adfed931742627c29a1f3da1a19ae24c165621cc58e39'
GT_SHA = 'f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1'
CLASS_SCHEMA = {'unit.skeleton': 0, 'unit.witch': 1}
MATCH_SPLITS = {'natural_match_01': 'TRAIN', 'natural_match_04': 'DEV_VAL'}
WEIGHT_URL = 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth'
UPSTREAM_COMMIT = '6ddff4824372906469a7fae2dc3206c7aa4bbaee'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def file_sha(path):
    h = sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def strict_json(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, 'Duplicate JSON key')
            obj[key] = value
        return obj
    def constant(_):
        raise ValueError('Non-finite JSON number')
    require(Path(path).stat().st_size <= 32 * 1024 * 1024, 'JSON input too large')
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=constant)


def write_json(path, value):
    with Path(path).open('xb') as output:
        output.write(canonical(value) + b'\n')


def private_path(root, path):
    root = Path(root).resolve()
    path = Path(path)
    require('..' not in path.parts, 'Traversal is not allowed')
    if not path.is_absolute():
        path = root / path
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise ValueError('Artifact outside repository') from None
    require(relative.parts and relative.parts[0] in ('outputs', 'local_data'),
            'Only private local artifact directories are allowed')
    for ancestor in [path, *path.parents]:
        require(not ancestor.is_symlink() and not ancestor.is_junction(), 'Linked artifact path')
        if ancestor == root:
            break
    result = subprocess.run(['git', 'check-ignore', '--', relative.as_posix()], cwd=root,
                            capture_output=True, check=False)
    require(result.returncode == 0, 'Artifact must be Git-ignored')
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', relative.as_posix()],
                             cwd=root, capture_output=True, check=False)
    require(tracked.returncode != 0, 'Tracked artifact is forbidden')
    return path


def default_config():
    return {'model': 'yolox-nano', 'input': 416, 'batch': 1, 'precision': 'FP32',
            'seed': 20261006, 'optimizer_steps': 100, 'learning_rate': 0.001,
            'momentum': 0.9, 'nesterov': True, 'weight_decay': 0.0005,
            'augmentation': 'none', 'scheduler': 'none', 'sample_order': 'alternating_fixed',
            'confidence': 0.001, 'nms_iou': 0.65, 'matching_iou': 0.5,
            'visualization_top_k': 30, 'dev_val_evaluation_count': 1,
            'class_schema': CLASS_SCHEMA, 'dataset_sha256': DATASET_SHA,
            'upstream_commit': UPSTREAM_COMMIT, 'unknown_unmatched': 'unjudged',
            'is_production_model_lock': False}


def validate_config(config):
    require(canonical(config) == canonical(default_config()), 'Fixed smoke configuration changed')


def validate_weight_url(url):
    require(url == WEIGHT_URL, 'Only the verified official Nano release URL is allowed')


def transfer_mapping(target,source):
    """Reject every incompatibility except the explicitly new two-class head."""
    skipped={f'head.cls_preds.{i}.{part}' for i in range(3) for part in ('weight','bias')}
    require(set(target)==set(source) and skipped <= set(target),'Pretrained key set differs')
    for key in target:
        want,got=tuple(target[key].shape),tuple(source[key].shape)
        if key in skipped:
            require(want[0]==2 and got[0]==80 and want[1:]==got[1:],'Unexpected class predictor shape')
        else:
            require(want==got,'Unexpected non-class parameter shape')
    return {key:source[key] for key in target if key not in skipped},sorted(skipped)


def load_locked(root, path):
    path = private_path(root, path)
    require(file_sha(path) == DATASET_SHA, 'Only the authorized frozen Dataset Lock is accepted')
    lock = strict_json(path)
    require(lock['kind'] == 'two_class_training_dataset_lock', 'Wrong dataset kind')
    require(lock['digest'] == sha256(canonical({k:v for k,v in lock.items() if k!='digest'})).hexdigest(),
            'Envelope digest mismatch')
    p = lock['payload']
    require(lock['dataset_semantic_sha256'] == sha256(canonical(p)).hexdigest(), 'Semantic digest mismatch')
    parent = private_path(root, p['smoke_gt_lock_reference']['path'])
    require(file_sha(parent) == GT_SHA == p['smoke_gt_lock_reference']['file_sha256'], 'Parent GT changed')
    require(strict_json(parent)['payload'] == p['gt_snapshot'], 'Parent snapshot conflict')
    require(p['training_qualified'] is True and p['rights_clearance']=='unverified', 'Scope not qualified')
    for binding in p['gt_snapshot']['source_bindings']:
        for kind in ('index','report'):
            require(file_sha(private_path(root,binding[kind+'_path']))==binding[kind+'_sha256'],
                    'Original binding changed')
    validate_payload(root,p)
    return p


def validate_payload(root, p):
    require(p['class_schema']==CLASS_SCHEMA and p['split_unit']=='underlying_match', 'Class/split contract changed')
    frames=p['gt_snapshot']['frames']; objects=p['gt_snapshot']['positive_objects']
    require(len(frames)==4 and len({f['frame_id'] for f in frames})==4, 'Four unique frozen frames required')
    require(len(objects)==11 and {o['object_id'] for o in objects}=={f'draft_object_{i:02}' for i in range(1,12)},
            'Exactly eleven accepted objects required')
    by_frame={f['frame_id']:f for f in frames}
    supervision={s['frame_id']:s for s in p['supervision']}
    require(set(supervision)==set(by_frame), 'Coverage must bind every frame')
    from PIL import Image
    for f in frames:
        require(MATCH_SPLITS.get(f['underlying_match_id'])==f['split'], 'Underlying match crosses split')
        source=private_path(root,f['source_image_relative_to_repo'])
        require(source.is_file() and file_sha(source)==f['image_sha256'], 'Frozen image changed')
        with Image.open(source) as image:
            require(list(image.size)==f['image_size'], 'Image size differs from frozen GT')
        s=supervision[f['frame_id']]
        require(s['unlabeled_regions_are_negative'] is False, 'Unknown cannot be negative')
        complete=f['complete_frame_supervision_coverage']
        require(s['standard_full_frame_loss_allowed'] is complete
                and s['standard_full_frame_metrics_allowed'] is complete, 'Coverage permission conflict')
        if f['split']=='TRAIN':
            require(complete is True, 'Partial/Unknown frame cannot enter standard training')
        require(set(f['positive_object_ids'])=={o['object_id'] for o in objects if o['frame_id']==f['frame_id']},
                'Frame/object references conflict')
    for o in objects:
        require(o['frame_id'] in by_frame and o['visual_class'] in CLASS_SCHEMA and o['review_state']=='confirmed',
                'Unconfirmed/unknown class object')
        f=by_frame[o['frame_id']]
        require(o['underlying_match_id']==f['underlying_match_id'], 'Object match conflicts')
        x,y,w,h=o['bbox_xywh_pixels'];width,height=f['image_size']
        require(all(type(v) is int for v in (x,y,w,h)) and x>=0 and y>=0 and w>0 and h>0
                and x+w<=width and y+h<=height, 'GT bbox outside original image')
    counts=Counter((by_frame[o['frame_id']]['split'],o['visual_class']) for o in objects)
    require(counts=={('TRAIN','unit.witch'):2,('TRAIN','unit.skeleton'):4,
                     ('DEV_VAL','unit.witch'):2,('DEV_VAL','unit.skeleton'):3}, 'Locked class counts conflict')
    require(Counter(f['split'] for f in frames)=={'TRAIN':2,'DEV_VAL':2}, 'Locked frame counts conflict')


def export_dataset(root,p,directory,lock_sha):
    validate_payload(root,p)
    directory=private_path(root,directory)
    require(not directory.exists(), 'Export is immutable and cannot overwrite')
    directory.mkdir(parents=True)
    frames=sorted(p['gt_snapshot']['frames'],key=lambda f:(f['split'],f['timestamp_seconds'],f['frame_id']))
    objects={o['object_id']:o for o in p['gt_snapshot']['positive_objects']}
    supervision={s['frame_id']:s for s in p['supervision']}
    manifest={'dataset_lock_sha256':lock_sha,'class_schema':CLASS_SCHEMA,
              'split_unit':'underlying_match','negative_evidence':[],
              'fp_time_denominator_seconds':None,'files':{},'counts':{},'frames':[]}
    (directory/'annotations').mkdir()
    for split,file in [('TRAIN','train.json'),('DEV_VAL','dev_val.json')]:
        data={'images':[],'annotations':[],
              'categories':[{'id':index,'name':name} for name,index in CLASS_SCHEMA.items()]}
        (directory/'images'/split).mkdir(parents=True)
        count={'images':0,'unit.witch':0,'unit.skeleton':0}
        for f in [f for f in frames if f['split']==split]:
            image_id=len(data['images'])+1; fid=f['frame_id']
            rel=f'images/{split}/{fid}.png'
            source=private_path(root,f['source_image_relative_to_repo'])
            with source.open('rb') as src, (directory/rel).open('xb') as dst:
                shutil.copyfileobj(src,dst)
            require(file_sha(directory/rel)==f['image_sha256'], 'PNG copy differs')
            record={'id':image_id,'file_name':rel,'width':f['image_size'][0],'height':f['image_size'][1],
                    'frame_id':fid,'timestamp_seconds':f['timestamp_seconds'],
                    'underlying_match_id':f['underlying_match_id'],'split':split,
                    **deepcopy(supervision[fid])}
            data['images'].append(record);count['images']+=1
            for oid in sorted(f['positive_object_ids']):
                o=objects[oid];bbox=o['bbox_xywh_pixels']
                data['annotations'].append({'id':len(data['annotations'])+1,'image_id':image_id,
                    'category_id':CLASS_SCHEMA[o['visual_class']],'bbox':bbox,'area':bbox[2]*bbox[3],
                    'iscrowd':0,'object_id':oid,'gt_metadata':deepcopy(o)})
                count[o['visual_class']]+=1
            manifest['frames'].append({'image':rel,'source_binding':deepcopy(f),
                                        'supervision':deepcopy(supervision[fid])})
            manifest['files'][rel]=file_sha(directory/rel)
        rel=f'annotations/{file}';write_json(directory/rel,data)
        manifest['files'][rel]=file_sha(directory/rel);manifest['counts'][split]=count
    write_json(directory/'manifest.json',manifest)
    return manifest


def verify_export(root,directory):
    directory=private_path(root,directory);m=strict_json(directory/'manifest.json')
    require(m['dataset_lock_sha256']==DATASET_SHA and m['class_schema']==CLASS_SCHEMA,'Wrong exported snapshot')
    for rel,digest in m['files'].items():
        require(file_sha(private_path(root,directory/rel))==digest,'Export changed after freeze')
    return m


def letterbox(image,size):
    import cv2
    import numpy as np
    height,width=image.shape[:2];ratio=min(size/height,size/width)
    scaled=cv2.resize(image,(int(width*ratio),int(height*ratio)),interpolation=cv2.INTER_LINEAR)
    output=np.full((size,size,3),114,dtype=np.uint8)
    output[:scaled.shape[0],:scaled.shape[1]]=scaled
    return np.ascontiguousarray(output.transpose(2,0,1),dtype=np.float32),ratio


def loss_targets(annotations,ratio):
    import numpy as np
    require(bool(annotations),'Frozen TRAIN image requires accepted positives')
    values=[]
    for a in annotations:
        x,y,w,h=a['bbox'];values.append([a['category_id'],(x+w/2)*ratio,(y+h/2)*ratio,w*ratio,h*ratio])
    return np.asarray([values],dtype=np.float32)


def train_batches(data):
    require(len(data['images'])==2, 'Exactly two frozen TRAIN images required')
    batches=[]
    for image in data['images']:
        require(image['split']=='TRAIN' and image['standard_full_frame_loss_allowed'] is True,
                'Only complete TRAIN frames can enter loss')
        labels=[a for a in data['annotations'] if a['image_id']==image['id']]
        require(bool(labels),'TRAIN frame lacks accepted positives')
        batches.append((image,labels))
    return batches


def decode_detections(rows,ratio,width,height):
    names={i:name for name,i in CLASS_SCHEMA.items()};values=[]
    for row in rows:
        require(len(row)==7 and all(math.isfinite(float(v)) for v in row), 'Invalid detection')
        x1,y1,x2,y2,obj,cls,index=row
        require(int(index)==index and int(index) in names,'Unknown detector class')
        box=[max(0,min(width,x1/ratio)),max(0,min(height,y1/ratio)),
             max(0,min(width,x2/ratio)),max(0,min(height,y2/ratio))]
        values.append({'visual_class':names[int(index)],'class_index':int(index),
                       'confidence':float(obj*cls),'objectness':float(obj),
                       'class_probability':float(cls),'bbox_xyxy':box,
                       'outside_original_image':box[2]<=box[0] or box[3]<=box[1]})
    return sorted(values,key=lambda p:p['confidence'],reverse=True)


def claim_attempt(path,receipt):
    """Exclusive marker is retained even on failure: no implicit real rerun."""
    write_json(path,receipt)


def iou_xyxy(a,b):
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=max(0,a[2]-a[0])*max(0,a[3]-a[1])+max(0,b[2]-b[0])*max(0,b[3]-b[1])-intersection
    return intersection/union if union>0 else 0.0


def evaluate_frame(gt,predictions,complete,iou_threshold):
    outside=[p for p in predictions if p.get('outside_original_image',False)]
    predictions=[p for p in predictions if not p.get('outside_original_image',False)]
    positive_matches=[];pairs=[]
    for gi,g in enumerate(gt):
        x,y,w,h=g['bbox'];box=[x,y,x+w,y+h]
        overlaps=[(iou_xyxy(box,p['bbox_xyxy']),pi) for pi,p in enumerate(predictions)
                  if p['visual_class']==g['visual_class']]
        best=max(overlaps,key=lambda pair:(pair[0],predictions[pair[1]]['confidence']),default=(0,None))
        positive_matches.append({'object_id':g['object_id'],'visual_class':g['visual_class'],
                                 'gt_bbox_xywh':g['bbox'],'best_iou':best[0],
                                 'matched_at_fixed_iou':False,'matched_prediction_index':None,
                                 'best_prediction':predictions[best[1]] if best[1] is not None else None})
        pairs.extend((score,predictions[pi]['confidence'],gi,pi) for score,pi in overlaps if score>=iou_threshold)
    used_gt,used_predictions=set(),set()
    for score,confidence,gi,pi in sorted(pairs,reverse=True):
        if gi not in used_gt and pi not in used_predictions:
            used_gt.add(gi);used_predictions.add(pi)
            positive_matches[gi]['matched_at_fixed_iou']=True
            positive_matches[gi]['matched_prediction_index']=pi
    remaining=[dict(p,prediction_index=i) for i,p in enumerate(predictions) if i not in used_predictions]
    return {'positive_matches':positive_matches,'tp':len(used_gt),'fn':len(gt)-len(used_gt),
            'false_detections':remaining if complete else [],
            'unjudged_detections':[] if complete else remaining,
            'outside_image_detections':outside,
            'precision':len(used_gt)/len(predictions) if complete and predictions else None,
            'complete_selected_class_coverage':complete,'fp_time_denominator_seconds':None}
