"""Synthetic guards for the one fixed run; no real pixels/model execution."""
import importlib
from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def api():
    assert importlib.util.find_spec('runtime_contract'), 'Attempt02 runtime contract missing'
    return importlib.import_module('runtime_contract')

def data():
    times=[5,10,15,75,90,95,100,105,158,160,161,163,164,166]
    images=[];annotations=[]
    groups=[[],[],[],[],[],[],[],[],[1],[1,0],[1,0],[1,0,0,0,0],[1],[1,0,0,0]]
    for i,(t,classes) in enumerate(zip(times,groups),1):
        images.append({'id':i,'frame_id':f'synthetic_{i}','timestamp_seconds':t,
                       'split':'TRAIN','underlying_match_id':'natural_match_01',
                       'standard_full_frame_loss_allowed':True,
                       'negative_confirmed':not bool(classes),'width':432,'height':624})
        for c in classes:
            annotations.append({'id':len(annotations)+1,'object_id':f'obj_{len(annotations)+1}',
                                'image_id':i,'category_id':c,'bbox':[100,100,20,30]})
    return {'images':images,'annotations':annotations}

def test_zero_gt_targets_have_explicit_batch_and_empty_object_axis():
    value=api().loss_targets([],2)
    assert value.shape==(1,0,5) and value.dtype==np.float32

def test_roi_box_scaled_to_class_center_extent():
    value=api().loss_targets([{'category_id':0,'bbox':[100,100,20,30]}],2)
    assert value.tolist()==[[[0,220,230,40,60]]]

def test_all_fourteen_frames_and_empty_negatives_retained():
    rows=api().train_batches(data())
    assert len(rows)==14 and sum(not labels for _,labels in rows)==8
    assert sum(len(labels) for _,labels in rows)==15

@pytest.mark.parametrize('bad',['partial','empty_not_confirmed','positive_negative','wrong_match','duplicate_frame','class_swap','rejected_label'])
def test_unqualified_background_or_foreign_data_rejected(bad):
    d=deepcopy(data())
    if bad=='partial':d['images'][0]['standard_full_frame_loss_allowed']=False
    if bad=='empty_not_confirmed':d['images'][0]['negative_confirmed']=None
    if bad=='positive_negative':d['images'][8]['negative_confirmed']=True
    if bad=='wrong_match':d['images'][0]['underlying_match_id']='natural_match_04'
    if bad=='duplicate_frame':d['images'][1]['frame_id']=d['images'][0]['frame_id']
    if bad=='class_swap':d['annotations'][0]['category_id']=True
    if bad=='rejected_label':d['annotations'][0]['review_state']='rejected'
    with pytest.raises(ValueError):api().train_batches(d)

def test_fixed_cycle_has_174_negative_and_126_positive_steps():
    rows=api().train_batches(data())
    counts=api().step_counts(rows)
    assert sum(counts.values())==300
    assert [counts[f'synthetic_{i}'] for i in range(1,15)]==[22]*6+[21]*8
    assert sum(counts[i['frame_id']] for i,labels in rows if labels)==126

def test_configuration_change_is_rejected_before_run():
    config=api().default_config();config['optimizer_steps']=301
    with pytest.raises(ValueError):api().validate_config(config)

def test_approved_config_remains_nano640300_no_augmentation():
    c=api().default_config();api().validate_config(c)
    assert (c['model'],c['input'],c['optimizer_steps'],c['augmentation'])==('yolox-nano',640,300,'none')

def test_export_binds_lock_file_sha_not_embedded_snapshot_object():
    manifest={'snapshot':{'schema_version':1},'expanded_lock_sha256':'a'*64}
    api().validate_export_binding(manifest,'a'*64)
    with pytest.raises(ValueError):api().validate_export_binding(manifest,'b'*64)

def test_export_without_expanded_lock_binding_rejected():
    with pytest.raises(ValueError):api().validate_export_binding({'snapshot':'a'*64},'a'*64)

def test_prediction_unscales_roi_then_restores_offset():
    ratio=640/624
    p=api().decode_predictions([[100*ratio,50*ratio,120*ratio,80*ratio,.5,.4,0]],[432,960])[0]
    assert p['bbox_xyxy']==pytest.approx([100,170,120,200])
    assert p['confidence']==pytest.approx(.2) and p['outside_original_image'] is False

def test_padding_prediction_is_retained_but_invalid_for_matching():
    p=api().decode_predictions([[450,20,460,40,.5,.4,1]],[432,960])[0]
    assert p['outside_original_image'] is True and p['valid_in_roi'] is False
    assert p['invalid_reason']=='padding_or_roi_boundary'

@pytest.mark.parametrize('row',[[1,2,3,4,.5,.4,2],[1,2,3,4,float('nan'),.4,0],[1,2,3,4,.5,.4]])
def test_invalid_raw_detections_rejected(row):
    with pytest.raises(ValueError):api().decode_predictions([row],[432,960])
