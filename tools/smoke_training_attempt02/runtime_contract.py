"""Fixed Attempt02 data/runtime guards; no model imports or training side effects."""
from collections import Counter
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'smoke_training'))
from smoke_data import DATASET_SHA, GT_SHA, canonical, require
from data_contract import CLASS_SCHEMA,prediction_from_letterbox

def default_config():
    return {'model':'yolox-nano','input':640,'batch':1,'precision':'FP32',
        'optimizer_steps':300,'seed':20261006,'learning_rate':.001,'momentum':.9,
        'nesterov':True,'weight_decay':.0005,'augmentation':'none','scheduler':'none',
        'confidence':.001,'nms_iou':.65,'matching_iou':.5,'visualization_top_k':30,
        'dev_tune_evaluation_count':1,'class_schema':CLASS_SCHEMA,
        'split_roles':{'natural_match_01':'TRAIN','natural_match_04':'DEV_TUNE'},
        'roi_rule':'[0,H//8,W,H*31//40] half-open pixel xyxy',
        'roi_for_source':[0,120,432,744],
        'official_weight_sha256':'cd28f55fbbc1829f99d9ac9b38a16d259a22889739c8728ea877610201feff7b',
        'parent_GT_sha256':GT_SHA,'parent_training_dataset_sha256':DATASET_SHA,
        'production_model_lock':False}

def validate_config(value):
    require(canonical(value)==canonical(default_config()),'Frozen Attempt02 configuration differs')

def validate_export_binding(manifest,lock_sha):
    require(manifest.get('expanded_lock_sha256')==lock_sha,'Wrong expanded snapshot export')

def loss_targets(labels,ratio):
    import numpy as np
    require(type(ratio) in (int,float) and math.isfinite(ratio) and ratio>0,'Invalid scale')
    rows=[]
    for label in labels:
        c=label['category_id'];x,y,w,h=label['bbox']
        require(type(c) is int and c in (0,1) and all(type(v) in (int,float)
            and math.isfinite(v) for v in (x,y,w,h)) and x>=0 and y>=0 and w>0 and h>0,
            'Invalid loss label')
        rows.append([c,(x+w/2)*ratio,(y+h/2)*ratio,w*ratio,h*ratio])
    return np.asarray(rows,dtype=np.float32).reshape(1,len(rows),5)

def train_batches(data):
    images=data['images'];annotations=data['annotations']
    require(len(images)==14 and len({i['frame_id'] for i in images})==14
        and len({i['id'] for i in images})==14,'Fourteen unique standard TRAIN frames required')
    require(len(annotations)==15 and len({a['object_id'] for a in annotations})==15,
            'Exactly fifteen distinct standard TRAIN objects required')
    require({a['image_id'] for a in annotations}<={i['id'] for i in images},'Orphan annotations')
    batches=[]
    for image in sorted(images,key=lambda i:(i['timestamp_seconds'],i['frame_id'])):
        require(image['split']=='TRAIN' and image['underlying_match_id']=='natural_match_01'
            and image['standard_full_frame_loss_allowed'] is True
            and image['width']==432 and image['height']==624,'Unqualified TRAIN source or ROI')
        labels=[a for a in annotations if a['image_id']==image['id']]
        require(type(image.get('negative_confirmed')) is bool
            and image['negative_confirmed']==(not bool(labels)),'Explicit background confirmation required')
        for label in labels:
            c=label['category_id'];x,y,w,h=label['bbox']
            require(type(c) is int and c in (0,1) and w>0 and h>0
                and x>=0 and y>=0 and x+w<=432 and y+h<=624,'Invalid ROI/class label')
            require(label.get('review_state','confirmed')=='confirmed'
                and label.get('gt_metadata',{}).get('review_state','confirmed')=='confirmed',
                'Rejected or draft object cannot enter loss')
        batches.append((image,labels))
    require(sum(not labels for _,labels in batches)==8
        and Counter(a['category_id'] for a in annotations)=={0:9,1:6},'Frozen class/negative counts differ')
    return batches

def step_counts(batches):
    return dict(Counter(batches[step%len(batches)][0]['frame_id'] for step in range(300)))

def decode_predictions(rows,original_size):
    predictions=[];names={i:c for c,i in CLASS_SCHEMA.items()}
    for row in rows:
        require(len(row)==7 and all(math.isfinite(float(v)) for v in row),'Invalid detector row')
        x1,y1,x2,y2,obj,cls,c=row
        require(int(c)==c and int(c) in names and 0<=obj<=1 and 0<=cls<=1,'Invalid detector class/score')
        geometry=prediction_from_letterbox([x1,y1,x2,y2],original_size,640)
        predictions.append({'visual_class':names[int(c)],'class_index':int(c),
            'confidence':float(obj*cls),'objectness':float(obj),'class_probability':float(cls),
            'bbox_xyxy':geometry['bbox_xyxy_original'],
            'outside_original_image':not geometry['valid_in_roi'],**geometry})
    return sorted(predictions,key=lambda p:p['confidence'],reverse=True)
