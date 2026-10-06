"""Behavioral tests use only anonymous generated pixels and made-up labels."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def api():
    assert importlib.util.find_spec('smoke_data') is not None, 'Smoke data/export implementation not present'
    return importlib.import_module('smoke_data')


@pytest.fixture
def locked(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / '.gitignore').write_text('/outputs/\n', encoding='utf-8')
    out = tmp_path / 'outputs'; out.mkdir()
    frames, objects = [], []
    # Synthetic topology mirrors counts only, never actual gameplay coordinates.
    per_frame = [('TRAIN', 'natural_match_01', ['unit.witch'] + ['unit.skeleton']*4),
                 ('TRAIN', 'natural_match_01', ['unit.witch']),
                 ('DEV_VAL', 'natural_match_04', ['unit.witch'] + ['unit.skeleton']*3),
                 ('DEV_VAL', 'natural_match_04', ['unit.witch'])]
    import hashlib
    for i, (split, match, classes) in enumerate(per_frame):
        path = out / f'synthetic_{i}.png'
        Image.new('RGB', (100, 200), (i*20, 40, 80)).save(path)
        ids = []
        for cls in classes:
            oid = f'draft_object_{len(objects)+1:02}'; ids.append(oid)
            objects.append({'object_id': oid, 'frame_id': f'f_test{i}',
                            'underlying_match_id': match, 'visual_class': cls,
                            'bbox_xywh_pixels': [10,20,30,40], 'owner': 'opponent',
                            'form': 'unknown', 'origin_kind': 'spawned' if cls.endswith('skeleton') else 'unknown',
                            'appearance_group_id': f'{match}_{cls}', 'review_state': 'confirmed'})
        frames.append({'frame_id': f'f_test{i}', 'underlying_match_id': match,
                       'split': split, 'timestamp_seconds': i, 'image_size': [100,200],
                       'source_image_relative_to_repo': path.relative_to(tmp_path).as_posix(),
                       'image_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'positive_object_ids': ids, 'complete_frame_supervision_coverage': i<3})
    payload = {'class_schema': {'unit.skeleton':0, 'unit.witch':1},
               'split_unit':'underlying_match', 'training_qualified': True,
               'rights_clearance':'unverified',
               'provenance':{'source_type':'user_recorded_gameplay','intended_use':'private_local_research_poc',
                             'user_training_authorized':True,'external_upload':False,
                             'redistribution':False,'rights_clearance':'unverified'},
               'gt_snapshot': {'frames':frames,'positive_objects':objects,
                               'rejected_objects':[{'object_id':'draft_object_12'}]},
               'supervision':[{'frame_id':f['frame_id'],
                               'standard_full_frame_loss_allowed':i<3,
                               'standard_full_frame_metrics_allowed':i<3,
                               'mode':'complete_selected_classes' if i<3 else 'positive_only_requires_unknown_safe_consumer',
                               'unlabeled_regions_are_negative':False} for i,f in enumerate(frames)]}
    return tmp_path, payload


def test_new_export_retains_exact_boxes_and_coverage_without_rejected_label(locked):
    module=api(); root,p=locked
    manifest=module.export_dataset(root,p,root/'outputs/export1','fake_lock_sha')
    assert manifest['counts']=={'TRAIN':{'images':2,'unit.witch':2,'unit.skeleton':4},
                                'DEV_VAL':{'images':2,'unit.witch':2,'unit.skeleton':3}}
    data=json.loads((root/'outputs/export1/annotations/dev_val.json').read_text())
    assert [x['category_id'] for x in data['annotations']]==[1,0,0,0,1]
    assert all(x['object_id']!='draft_object_12' for x in data['annotations'])
    assert data['images'][-1]['standard_full_frame_metrics_allowed'] is False
    assert data['images'][-1]['unlabeled_regions_are_negative'] is False
    assert data['annotations'][0]['bbox']==[10,20,30,40]


def test_export_is_deterministic_and_never_overwrites(locked):
    m=api(); root,p=locked
    m.export_dataset(root,p,root/'outputs/a','same_sha')
    m.export_dataset(root,p,root/'outputs/b','same_sha')
    for file in ('annotations/train.json','annotations/dev_val.json','manifest.json'):
        assert (root/'outputs/a'/file).read_bytes()==(root/'outputs/b'/file).read_bytes()
    with pytest.raises((ValueError,FileExistsError)):
        m.export_dataset(root,p,root/'outputs/a','same_sha')


@pytest.mark.parametrize('defect',['bbox_escape','split_leak','rejected','unknown_train','changed_image','changed_class','extra_box'])
def test_invalid_frozen_inputs_cannot_export(locked,defect):
    m=api();root,p=locked
    if defect=='bbox_escape':p['gt_snapshot']['positive_objects'][0]['bbox_xywh_pixels']=[90,20,30,40]
    if defect=='split_leak':p['gt_snapshot']['frames'][2]['underlying_match_id']='natural_match_01'
    if defect=='rejected':p['gt_snapshot']['positive_objects'][0]['object_id']='draft_object_12'
    if defect=='unknown_train':p['supervision'][0]['standard_full_frame_loss_allowed']=False
    if defect=='changed_image':(root/'outputs/synthetic_0.png').write_bytes(b'bad')
    if defect=='changed_class':p['class_schema']={'unit.witch':0,'unit.skeleton':1}
    if defect=='extra_box':p['gt_snapshot']['positive_objects'].append(dict(p['gt_snapshot']['positive_objects'][0]))
    with pytest.raises(ValueError):m.export_dataset(root,p,root/'outputs/export','sha')
    assert not (root/'outputs/export').exists()


def test_output_outside_private_or_source_traversal_rejected(locked):
    m=api(); root,p=locked
    with pytest.raises(ValueError):m.export_dataset(root,p,root/'public_export','sha')
    p['gt_snapshot']['frames'][0]['source_image_relative_to_repo']='../escape.png'
    with pytest.raises(ValueError):m.export_dataset(root,p,root/'outputs/export','sha')


def test_letterbox_and_target_coordinates_preserve_top_left_xywh():
    m=api(); import numpy as np
    image=np.zeros((200,100,3),dtype=np.uint8); image[:]=[11,22,33]
    pixels,ratio=m.letterbox(image,416)
    assert pixels.shape==(3,416,416) and pixels.dtype==np.float32
    assert ratio==2.08 and pixels[:,0,0].tolist()==[11,22,33]
    assert pixels[:,0,300].tolist()==[114,114,114]
    target=m.loss_targets([{'category_id':1,'bbox':[10,20,30,40]}],ratio)
    assert target.shape==(1,1,5)
    assert target[0,0].tolist()==pytest.approx([1,52,83.2,62.4,83.2])


def test_partial_unmatched_predictions_are_unjudged_never_false_detections():
    m=api(); g=[{'object_id':'known','visual_class':'unit.witch','bbox':[10,20,30,40]}]
    preds=[{'visual_class':'unit.witch','confidence':.8,'bbox_xyxy':[10,20,40,60]},
           {'visual_class':'unit.skeleton','confidence':.9,'bbox_xyxy':[50,100,80,130]}]
    partial=m.evaluate_frame(g,preds,complete=False,iou_threshold=.5)
    assert partial['positive_matches'][0]['best_iou']==1.0
    assert partial['tp']==1 and partial['fn']==0 and partial['false_detections']==[]
    assert len(partial['unjudged_detections'])==1 and partial['precision'] is None
    full=m.evaluate_frame(g,preds,complete=True,iou_threshold=.5)
    assert len(full['false_detections'])==1 and full['precision']==.5


def test_matching_is_one_to_one_same_class_and_reports_missing_positive():
    m=api();g=[{'object_id':'a','visual_class':'unit.witch','bbox':[0,0,10,10]},
               {'object_id':'b','visual_class':'unit.witch','bbox':[0,0,10,10]}]
    p=[{'visual_class':'unit.witch','confidence':.9,'bbox_xyxy':[0,0,10,10]}]
    r=m.evaluate_frame(g,p,complete=False,iou_threshold=.5)
    assert r['tp']==1 and r['fn']==1
    assert sum(x['matched_at_fixed_iou'] for x in r['positive_matches'])==1
    p[0]['visual_class']='unit.skeleton'
    r=m.evaluate_frame(g,p,complete=False,iou_threshold=.5)
    assert r['tp']==0 and r['fn']==2 and len(r['unjudged_detections'])==1


def test_config_and_weight_source_gate_reject_expansion():
    m=api(); config=m.default_config()
    m.validate_config(config)
    for key,val in [('optimizer_steps',101),('model','yolox-tiny'),('confidence',.4),('batch',2)]:
        broken=dict(config);broken[key]=val
        with pytest.raises(ValueError):m.validate_config(broken)
    m.validate_weight_url('https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth')
    with pytest.raises(ValueError):m.validate_weight_url('https://example.com/yolox_nano.pth')


def test_transfer_excludes_only_six_80_to_two_class_prediction_keys():
    m=api();import numpy as np
    target={'backbone.weight':np.ones((4,4))}
    source={'backbone.weight':np.zeros((4,4))}
    for i in range(3):
        for part,shape in [('weight',(2,4,1,1)),('bias',(2,))]:
            key=f'head.cls_preds.{i}.{part}'
            target[key]=np.ones(shape)
            source[key]=np.ones((80,*shape[1:]))
    transferred,skipped=m.transfer_mapping(target,source)
    assert list(transferred)==['backbone.weight'] and len(skipped)==6
    source['backbone.weight']=np.ones((5,4))
    with pytest.raises(ValueError):m.transfer_mapping(target,source)
    source['backbone.weight']=np.ones((4,4));source['unexpected']=np.ones((1,))
    with pytest.raises(ValueError):m.transfer_mapping(target,source)


def test_bad_json_is_rejected_before_any_consumer(tmp_path):
    m=api();p=tmp_path/'bad.json'
    p.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError):m.strict_json(p)
    p.write_text('{"a":NaN}')
    with pytest.raises(ValueError):m.strict_json(p)


def test_export_copy_and_annotation_modifications_rejected(locked):
    m=api();root,p=locked
    m.export_dataset(root,p,root/'outputs/export',m.DATASET_SHA)
    m.verify_export(root,root/'outputs/export')
    (root/'outputs/export/annotations/train.json').write_text('{}')
    with pytest.raises(ValueError):m.verify_export(root,root/'outputs/export')


def test_official_release_utf8_metadata_does_not_use_windows_locale():
    import prepare_run
    raw='{"tag_name":"0.1.1rc0","body":"模型 release"}'.encode('utf-8')
    assert prepare_run.parse_release(raw)['body']=='模型 release'


def test_only_complete_train_split_can_reach_training_batches():
    m=api()
    images=[{'id':1,'split':'TRAIN','standard_full_frame_loss_allowed':True},
            {'id':2,'split':'TRAIN','standard_full_frame_loss_allowed':True}]
    annotations=[{'image_id':1},{'image_id':2}]
    assert len(m.train_batches({'images':images,'annotations':annotations}))==2
    images[1]['split']='DEV_VAL'
    with pytest.raises(ValueError):m.train_batches({'images':images,'annotations':annotations})
    images[1]['split']='TRAIN';images[1]['standard_full_frame_loss_allowed']=False
    with pytest.raises(ValueError):m.train_batches({'images':images,'annotations':annotations})


def test_prediction_coordinates_unletterbox_and_clip_not_gt_center():
    m=api()
    p=m.decode_detections([[20,40,100,180,.5,.8,1]],ratio=2,width=40,height=80)
    assert p[0]['bbox_xyxy']==[10,20,40,80]
    assert p[0]['visual_class']=='unit.witch' and p[0]['confidence']==pytest.approx(.4)


def test_exclusive_attempt_markers_cannot_restart_training_or_evaluation(tmp_path):
    m=api();path=tmp_path/'training-start.json'
    m.claim_attempt(path,{'steps':100})
    with pytest.raises(FileExistsError):m.claim_attempt(path,{'steps':100})
    assert json.loads(path.read_text())=={'steps':100}


def test_padding_only_candidate_is_retained_but_not_an_image_false_positive():
    m=api()
    predictions=m.decode_detections([[300,100,350,140,.8,.8,0]],ratio=2,width=100,height=200)
    assert len(predictions)==1  # Raw/NMS audit output is not silently deleted.
    result=m.evaluate_frame([],predictions,complete=True,iou_threshold=.5)
    assert result['false_detections']==[]
    assert len(result['outside_image_detections'])==1 and result['precision'] is None


def test_gpu_monitor_failure_is_recorded_not_silently_lost(tmp_path,monkeypatch):
    import train_smoke
    import threading
    def timeout(*args,**kwargs):
        raise subprocess.TimeoutExpired('nvidia-smi',15)
    monkeypatch.setattr(train_smoke.subprocess,'run',timeout)
    errors=[]
    train_smoke.telemetry(threading.Event(),tmp_path/'telemetry.csv',errors)
    assert errors


def test_batch_protection_keeps_per_file_hash_and_ignored_path_checks(locked):
    import verify_artifacts
    m=api();root,p=locked
    inventory={f['source_image_relative_to_repo']:f['image_sha256'] for f in p['gt_snapshot']['frames']}
    assert verify_artifacts.check_inventory(root,inventory)==4
    (root/'outputs/synthetic_0.png').write_bytes(b'changed')
    with pytest.raises(ValueError):verify_artifacts.check_inventory(root,inventory)
    with pytest.raises(ValueError):verify_artifacts.check_inventory(root,{'../outside':'x'})


def test_protection_includes_tracked_legacy_code_without_treating_it_as_private(locked):
    import verify_artifacts
    m=api();root,_=locked
    path=root/'tools/offline_video/src/legacy.py';path.parent.mkdir(parents=True)
    path.write_text('# preserved historical source\n',encoding='utf-8')
    subprocess.run(['git','add','tools/offline_video/src/legacy.py'],cwd=root,check=True)
    inventory={'tools/offline_video/src/legacy.py':m.file_sha(path)}
    assert verify_artifacts.check_inventory(root,inventory)==1
    path.write_text('# changed\n',encoding='utf-8')
    with pytest.raises(ValueError):verify_artifacts.check_inventory(root,inventory)


def test_only_approved_editable_checkout_commit_can_differ_not_package_version():
    import verify_artifacts
    before={'pip_check_exit':0,'pip_check_output':'ok','packages':['numpy==2.2.6',
            '-e git+https://github.com/cc7279694-debug/royal-app.git@'+'a'*40+'#egg=clash_tracker_video&subdirectory=tools%5Coffline_video']}
    after=json.loads(json.dumps(before));after['packages'][1]=after['packages'][1].replace('a'*40,'b'*40)
    assert verify_artifacts.same_environment(before,after,{'a'*40,'b'*40})
    assert not verify_artifacts.same_environment(before,after,{'a'*40})
    after['packages'][0]='numpy==2.3.0'
    assert not verify_artifacts.same_environment(before,after,{'a'*40,'b'*40})
