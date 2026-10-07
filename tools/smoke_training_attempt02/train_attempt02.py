"""One frozen Nano640 GPU run; immutable receipts prohibit implicit retries."""
import argparse
from datetime import datetime,timezone
import inspect
import os
from pathlib import Path
import random
import subprocess
import sys
import threading
import time
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'smoke_training'))
from smoke_data import (UPSTREAM_COMMIT,canonical,claim_attempt,evaluate_frame,file_sha,
    letterbox,private_path,require,strict_json,transfer_mapping,validate_weight_url,write_json)
from train_smoke import equal_state,to_cpu,telemetry
from data_contract import CLASS_SCHEMA
from expanded_data import load_expanded,validate_export
from runtime_contract import (decode_predictions,loss_targets,step_counts,train_batches,validate_config,
    validate_export_binding)

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root).decode('utf-8').strip()

def draw_review(source_path,destination,gt,predictions,complete,config):
    from PIL import Image,ImageDraw
    with Image.open(source_path) as source:image=source.convert('RGB')
    draw=ImageDraw.Draw(image)
    draw.rectangle(config['roi_for_source'],outline='#b688ff',width=2)
    for g in gt:
        x,y,w,h=g['bbox'];draw.rectangle((x,y,x+w,y+h),outline='#00ff00',width=2)
        draw.text((x,max(20,y-12)),f"GT {g['visual_class'].split('.')[-1]}",fill='#00ff00')
    for p in [p for p in predictions if p['valid_in_roi']][:config['visualization_top_k']]:
        color='#ff7d00' if p['class_index']==0 else '#00d9ff'
        draw.rectangle(p['bbox_xyxy'],outline=color,width=1)
        x,y,_,_=p['bbox_xyxy']
        draw.text((x,max(20,y-11)),f"{p['visual_class'].split('.')[-1]} {p['confidence']:.4f}",fill=color)
    draw.rectangle((0,0,image.width,16),fill='black')
    draw.text((2,2),'Attempt02 DEV_TUNE | '+('complete' if complete else 'partial: unmatched UNKNOWN'),fill='white')
    with destination.open('xb') as out:image.save(out,format='PNG')

def execute(root,lock,run):
    require(not git(root,'status','--porcelain'),'Clean committed local baseline required')
    require(git(root,'branch','--show-current') not in ('main','master'),'Feature branch required')
    require(not any((run/p).exists() for p in ('training-start.json','failure.json','result.json')),
            'Attempt02 has already started/failed/completed; preserve, never rerun')
    config=strict_json(run/'training-config.json');validate_config(config)
    payload=load_expanded(root,lock)
    manifest=validate_export(root,run/'dataset')
    preparation=strict_json(run/'preparation-result.json')
    require(file_sha(lock)==preparation['expanded_lock_sha256']
        and file_sha(run/'dataset/manifest.json')==preparation['dataset_manifest_sha256']
        and file_sha(run/'training-config.json')==preparation['config_sha256'],
        'Prepared data/config changed')
    validate_export_binding(manifest,file_sha(lock))
    authority=strict_json(run/'attempt02-authorization.json')
    require(authority['real_train_authorized'] is True and authority['external_upload'] is False
        and authority['expanded_lock_sha256']==file_sha(lock),'Scoped Attempt02 authority required')
    weight=private_path(root,preparation['pretrained_weight_path'])
    provenance=strict_json(private_path(root,preparation['pretrained_provenance_path']))
    validate_weight_url(provenance['exact_download_url'])
    require(file_sha(weight)==config['official_weight_sha256']==provenance['downloaded_sha256'],
            'Existing official weight changed')
    # CUDA determinism is configured before torch initialization, never fallback.
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    import numpy as np
    import cv2
    import torch
    import torchvision
    import yolox
    from yolox.exp import get_exp
    from yolox.utils import postprocess
    require(torch.__version__=='2.7.1+cu118' and torchvision.__version__=='0.22.1+cu118'
        and yolox.__version__=='0.3.0','Qualified environment versions changed')
    require(Path(yolox.__file__).resolve().parents[1].name=='YOLOX-'+UPSTREAM_COMMIT,
            'Wrong official source revision')
    require(torch.cuda.is_available(),'CUDA required')
    device=torch.device('cuda:0');gpu=torch.cuda.get_device_properties(device)
    require('GTX 1050 Ti' in gpu.name,'Wrong qualified GPU')
    random.seed(config['seed']);np.random.seed(config['seed']);torch.manual_seed(config['seed'])
    torch.cuda.manual_seed_all(config['seed'])
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
    train=strict_json(run/'dataset/annotations/train.json')
    batches=train_batches(train);counts=step_counts(batches)
    expected_assignments=sum(counts[image['frame_id']] for image,labels in batches if labels)
    inputs=[]
    for image,labels in batches:
        pixels=cv2.imread(str(run/'dataset'/image['file_name']),cv2.IMREAD_COLOR)
        require(pixels is not None and list(pixels.shape[:2])==[624,432],'TRAIN ROI decode failed')
        values,ratio=letterbox(pixels,640)
        inputs.append((image,torch.from_numpy(values[None]),torch.from_numpy(loss_targets(labels,ratio))))
    require(all(not x.is_cuda and not y.is_cuda for _,x,y in inputs),'Inputs must cache on CPU')
    exp=get_exp(None,'yolox-nano');exp.num_classes=2
    exp.input_size=exp.test_size=(640,640);exp.warmup_epochs=0
    exp.basic_lr_per_img=config['learning_rate'];exp.momentum=config['momentum'];exp.weight_decay=config['weight_decay']
    model=exp.get_model()  # Exactly once; do not reset learned bias on restore.
    pretrained=torch.load(weight,map_location='cpu',weights_only=True)
    filtered,skipped=transfer_mapping(model.state_dict(),pretrained['model'])
    missing=model.load_state_dict(filtered,strict=False)
    require(set(missing.missing_keys)==set(skipped) and not missing.unexpected_keys,'Transfer incomplete')
    del filtered,pretrained
    model.to(device).float();model.train();optimizer=exp.get_optimizer(1)
    require(all(g['lr']==.001 and g['momentum']==.9 and g['nesterov'] is True for g in optimizer.param_groups),
            'Optimizer differs from frozen configuration')
    initial={k:v.detach().cpu().clone() for k,v in model.named_parameters()}
    assignments=[];original=model.head.get_assignments;signature=inspect.signature(original)
    def cuda_assignments(*args,**kwargs):
        bound=signature.bind(*args,**kwargs);bound.apply_defaults()
        require(bound.arguments['mode']=='gpu','CPU assignment fallback forbidden')
        require(all(not torch.is_tensor(v) or v.is_cuda for v in bound.arguments.values()),
                'Assignment left CUDA')
        assignments.append('cuda');return original(*args,**kwargs)
    model.head.get_assignments=cuda_assignments
    freeze={'public_code_commit':git(root,'rev-parse','HEAD'),'branch':git(root,'branch','--show-current'),
        'config':config,'config_sha256':file_sha(run/'training-config.json'),
        'expanded_lock_sha256':file_sha(lock),'dataset_manifest_sha256':file_sha(run/'dataset/manifest.json'),
        'parent_gt_sha256':config['parent_GT_sha256'],
        'parent_dataset_sha256':config['parent_training_dataset_sha256'],
        'pretrained_sha256':file_sha(weight),'sample_order':[i['frame_id'] for i,_ in batches],
        'planned_frame_uses':counts,'expected_positive_cuda_assignment_calls':expected_assignments,
        'environment':{'torch':torch.__version__,'torchvision':torchvision.__version__,'yolox':yolox.__version__,
            'cuda':torch.version.cuda,'gpu':gpu.name,'vram_bytes':gpu.total_memory,
            'compute_capability':[gpu.major,gpu.minor]},
        'source_files_sha256':{p.name:file_sha(p) for p in Path(__file__).parent.glob('*.py')},
        'cpu_input_cache_bytes':sum(x.numel()*x.element_size()+y.numel()*y.element_size() for _,x,y in inputs),
        'pretrained_loaded_keys':len(model.state_dict())-len(skipped),'pretrained_skipped_keys':skipped,
        'dev_tune_during_training':False,'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    write_json(run/'run-freeze.json',freeze)
    claim_attempt(run/'training-start.json',{'optimizer_steps':300,'freeze_sha256':file_sha(run/'run-freeze.json')})
    stop=threading.Event();monitor_errors=[]
    monitor=threading.Thread(target=telemetry,args=(stop,run/'gpu-telemetry.csv',monitor_errors),daemon=True)
    monitor.start();torch.cuda.reset_peak_memory_stats(device);torch.cuda.synchronize()
    started=time.perf_counter();losses=[];actual_counts={fid:0 for fid in counts}
    try:
        with (run/'loss-history.jsonl').open('xb') as log:
            for step in range(300):
                image,cpu_x,cpu_y=inputs[step%len(inputs)]
                x=cpu_x.to(device);y=cpu_y.to(device)
                optimizer.zero_grad(set_to_none=True)
                output=model(x,y)
                require(output['total_loss'].is_cuda and torch.isfinite(output['total_loss']).item(),
                        'Nonfinite or non-CUDA loss')
                output['total_loss'].backward()
                gradients=[p.grad for p in model.parameters() if p.grad is not None]
                require(gradients and all(g.is_cuda and torch.isfinite(g).all().item() for g in gradients),
                        'Nonfinite/non-CUDA gradients')
                grad_l1=sum(g.abs().sum().item() for g in gradients)
                require(grad_l1>0,'No learning gradient')
                optimizer.step();torch.cuda.synchronize()
                row={'step':step+1,'frame_id':image['frame_id'],'split':'TRAIN',
                    'negative_confirmed':image['negative_confirmed'],'gpu_used':True,'gradient_l1':grad_l1,
                    'losses':{k:float(v.detach().item()) if torch.is_tensor(v) else float(v) for k,v in output.items()},
                    'elapsed_seconds':time.perf_counter()-started}
                require(all(np.isfinite(v) for v in row['losses'].values()),'Nonfinite loss component')
                actual_counts[image['frame_id']]+=1;losses.append(row)
                log.write(canonical(row)+b'\n');log.flush()
                del x,y,output,gradients
                if step==0 or (step+1)%25==0:
                    print(f"TRAIN step {step+1}/300 loss={row['losses']['total_loss']:.6f}",flush=True)
        elapsed=time.perf_counter()-started
        require(actual_counts==counts and len(assignments)==expected_assignments,
                'Fixed sample or CUDA assignment counts differ')
        changed={k:float((v.detach().cpu()-initial[k]).abs().sum().item()) for k,v in model.named_parameters()}
        require(sum(changed.values())>0,'Parameters did not learn')
        checkpoint={'model':to_cpu(model.state_dict(),torch),'optimizer':to_cpu(optimizer.state_dict(),torch),
            'config':config,'completed_optimizer_steps':300,'freeze_sha256':file_sha(run/'run-freeze.json')}
        with (run/'final-checkpoint.pth').open('xb') as out:torch.save(checkpoint,out)
        restored=torch.load(run/'final-checkpoint.pth',map_location='cpu',weights_only=True)
        require(equal_state(checkpoint,restored,torch),'Checkpoint round-trip differs')
        model.load_state_dict(restored['model'],strict=True);optimizer.load_state_dict(restored['optimizer'])
        require(equal_state(model.state_dict(),restored['model'],torch)
            and equal_state(optimizer.state_dict(),restored['optimizer'],torch),'Strict restore differs')
        training={'optimizer_steps':300,'train_frame_uses':actual_counts,'negative_steps':174,'positive_steps':126,
            'cuda_assignment_calls':len(assignments),'cpu_fallback_calls':0,'wall_seconds':elapsed,
            'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),
            'peak_reserved_bytes':torch.cuda.max_memory_reserved(device),
            'changed_parameter_tensors':sum(v>0 for v in changed.values()),'parameter_absolute_change':sum(changed.values()),
            'first_14_mean_loss':sum(r['losses']['total_loss'] for r in losses[:14])/14,
            'last_14_mean_loss':sum(r['losses']['total_loss'] for r in losses[-14:])/14,
            'first_10_mean_loss':sum(r['losses']['total_loss'] for r in losses[:10])/10,
            'last_10_mean_loss':sum(r['losses']['total_loss'] for r in losses[-10:])/10,
            'checkpoint_sha256':file_sha(run/'final-checkpoint.pth'),'checkpoint_reload_equal':True}
        write_json(run/'training-result.json',training)
        print('300 steps completed and checkpoint restored. Starting the ONE DEV_TUNE evaluation.',flush=True)
        # Only now read DEV_TUNE images/labels. They never enter optimizer inputs.
        dev=strict_json(run/'dataset/annotations/dev_tune.json')
        claim_attempt(run/'dev-tune-start.json',{'evaluation_count':1,'forward_count_expected':2,
            'checkpoint_sha256':training['checkpoint_sha256']})
        (run/'visualizations').mkdir();model.eval();evaluations=[]
        with torch.inference_mode():
            for image in dev['images']:
                require(image['split']=='DEV_TUNE' and image['underlying_match_id']=='natural_match_04',
                        'Wrong DEV_TUNE source')
                pixels=cv2.imread(str(run/'dataset'/image['file_name']),cv2.IMREAD_COLOR)
                require(pixels is not None and list(pixels.shape[:2])==[624,432],'DEV ROI decode failed')
                values,_=letterbox(pixels,640)
                raw=model(torch.from_numpy(values[None]).to(device))
                require(raw.shape==(1,8400,7) and torch.isfinite(raw).all().item(),'Invalid Nano640 output')
                raw_rows=raw[0].cpu().tolist()
                retained=postprocess(raw.clone(),2,config['confidence'],config['nms_iou'],class_agnostic=False)[0]
                rows=[] if retained is None else retained.cpu().tolist()
                predictions=decode_predictions(rows,image['original_image_size'])
                labels=[a for a in dev['annotations'] if a['image_id']==image['id']]
                gt=[{'object_id':a['object_id'],'visual_class':a['gt_metadata']['visual_class'],
                     'bbox':a['gt_metadata']['bbox_xywh_pixels']} for a in labels]
                complete=image['standard_full_frame_metrics_allowed'] is True
                assessment=evaluate_frame(gt,predictions,complete,.5)
                record={'frame_id':image['frame_id'],'timestamp_seconds':image['timestamp_seconds'],
                    'underlying_match_id':image['underlying_match_id'],'split':'DEV_TUNE',
                    'coordinate_space':'original_image_after_ROI_inverse','predictions':predictions,**assessment}
                write_json(run/f"raw-{image['frame_id']}.json",{'columns':['center_x','center_y','width','height',
                    'objectness','skeleton_probability','witch_probability'],'coordinate_space':'640_ROI_letterboxed','rows':raw_rows})
                write_json(run/f"prediction-{image['frame_id']}.json",record)
                original_path=private_path(root,image['source_image_relative_to_repo'])
                draw_review(original_path,run/'visualizations'/f"{image['timestamp_seconds']:g}s.png",gt,predictions,complete,config)
                evaluations.append(record)
                print(f"DEV_TUNE {image['timestamp_seconds']:g}s: retained={len(predictions)} TP={assessment['tp']} FN={assessment['fn']}",flush=True)
        require(len(evaluations)==2,'Exactly two fixed DEV_TUNE forwards required')
        write_json(run/'evaluation-summary.json',{'scope':'development_tuning_not_blind_or_independent_test',
            'config':config,'training':training,'frames':evaluations,'accepted_gt_count':5,
            'matched_gt_iou_05':sum(f['tp'] for f in evaluations),'eval_forward_count':2,'eval_run_count':1,
            'mAP':None,'fp_per_minute':None,'owner_discrimination_evaluated':False,
            'production_model_lock_created':False,'partial_frame_unmatched_are_unjudged':True,
            'result_is_not_accuracy_acceptance':True})
    finally:
        stop.set();monitor.join(timeout=20)
        require(not monitor.is_alive() and not monitor_errors,'GPU monitoring failed; preserve result and stop')
    write_json(run/'result.json',{'status':'TWO_CLASS_SMOKE_ATTEMPT02_COMPLETE',
        'training_result_sha256':file_sha(run/'training-result.json'),
        'evaluation_summary_sha256':file_sha(run/'evaluation-summary.json')})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True);parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve();run=private_path(root,args.run)
    try:execute(root,args.lock,run)
    except Exception as exc:
        if not (run/'failure.json').exists():
            write_json(run/'failure.json',{'type':type(exc).__name__,'message':str(exc),
                'training_start_present':(run/'training-start.json').exists(),'no_implicit_retry_authorized':True})
        traceback.print_exc();raise SystemExit(2)

if __name__=='__main__':main()
