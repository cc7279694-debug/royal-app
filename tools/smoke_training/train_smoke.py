"""One authorized fixed-budget GPU smoke run; no Trainer extras or retuning.

Uses the unmodified official YOLOX model, loss, assignment and SGD builder.
Private outputs are exclusive. A start marker forbids implicit reruns on failure.
"""
import argparse
from datetime import datetime, timezone
import inspect
import os
from pathlib import Path
import random
import subprocess
import threading
import time
import traceback

from smoke_data import (CLASS_SCHEMA, DATASET_SHA, GT_SHA, UPSTREAM_COMMIT,
                        canonical, claim_attempt, decode_detections, evaluate_frame,
                        file_sha, letterbox, load_locked, loss_targets, private_path,
                        require, strict_json, train_batches, transfer_mapping,
                        validate_config, validate_weight_url, verify_export, write_json)


def git(root, *arguments):
    return subprocess.check_output(['git', *arguments], cwd=root).decode('utf-8').strip()


def to_cpu(value, torch):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {k:to_cpu(v,torch) for k,v in value.items()}
    if isinstance(value, list):
        return [to_cpu(v,torch) for v in value]
    if isinstance(value, tuple):
        return tuple(to_cpu(v,torch) for v in value)
    return value


def equal_state(a, b, torch):
    if torch.is_tensor(a):
        return torch.is_tensor(b) and torch.equal(a.cpu(),b.cpu())
    if isinstance(a, dict):
        return isinstance(b,dict) and a.keys()==b.keys() and all(equal_state(a[k],b[k],torch) for k in a)
    if isinstance(a,(list,tuple)):
        return isinstance(b,type(a)) and len(a)==len(b) and all(equal_state(x,y,torch) for x,y in zip(a,b))
    return a==b


def draw_review(image_path, output_path, gt, predictions, config, complete):
    from PIL import Image, ImageDraw
    with Image.open(image_path) as source:
        image=source.convert('RGB')
    draw=ImageDraw.Draw(image)
    for g in gt:
        x,y,w,h=g['bbox'];draw.rectangle((x,y,x+w,y+h),outline='#00ff00',width=2)
        draw.text((x,max(14,y-13)),f"GT {g['visual_class'].split('.')[-1]}",fill='#00ff00')
    drawable=[p for p in predictions if not p['outside_original_image']]
    for p in drawable[:config['visualization_top_k']]:
        color='#ff7d00' if p['class_index']==0 else '#00d9ff'
        draw.rectangle(p['bbox_xyxy'],outline=color,width=1)
        x,y,_,_=p['bbox_xyxy']
        draw.text((x,max(14,y-11)),f"{p['visual_class'].split('.')[-1]} {p['confidence']:.3f}",fill=color)
    draw.rectangle((0,0,image.width,13),fill='black')
    draw.text((2,1),'GT green | fixed top30 | '+('complete' if complete else 'partial: unmatched UNKNOWN'),fill='white')
    with output_path.open('xb') as stream:
        image.save(stream,format='PNG')


def telemetry(stop, path, errors):
    samples=0
    try:
        with path.open('x',encoding='utf-8',newline='') as log:
            log.write('timestamp,index,name,utilization_percent,memory_used_mib,memory_total_mib\n')
            while not stop.is_set():
                result=subprocess.run(['nvidia-smi','--query-gpu=timestamp,index,name,utilization.gpu,memory.used,memory.total',
                                       '--format=csv,noheader,nounits'],capture_output=True,timeout=15)
                require(result.returncode==0 and result.stdout.strip(), 'nvidia-smi failed/empty')
                lines=result.stdout.decode('utf-8')
                require(all(len(line.split(','))==6 for line in lines.strip().splitlines()),'Malformed GPU sample')
                log.write(lines);log.flush();samples+=1;stop.wait(.5)
        require(samples>0,'No GPU utilization samples')
    except Exception as exc:
        errors.append(type(exc).__name__+': '+str(exc))


def execute(root, lock, run):
    import numpy as np
    import cv2
    # Set deterministic CUDA configuration before importing/initializing torch.
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    import torch
    import torchvision
    import yolox
    from yolox.exp import get_exp
    from yolox.utils import postprocess

    require(not git(root,'status','--porcelain'), 'Commit a clean local code baseline before training')
    require(git(root,'branch','--show-current') not in ('main','master'), 'Feature branch required')
    config=strict_json(run/'training-config.json');validate_config(config)
    load_locked(root,lock)
    preparation=strict_json(run/'preparation-result.json')
    require(file_sha(run/'training-config.json')==preparation['config_sha256'],'Prepared config changed')
    require(file_sha(run/'dataset/manifest.json')==preparation['exported_dataset_manifest_sha256'],
            'Prepared export manifest changed')
    manifest=verify_export(root,run/'dataset')
    provenance=strict_json(run/'pretrained/provenance.json')
    validate_weight_url(provenance['exact_download_url'])
    weight=run/'pretrained/yolox_nano.pth'
    require(file_sha(weight)==preparation['weight_sha256']==provenance['downloaded_sha256'], 'Official weight changed')
    authority=strict_json(run/'phase-c-authorization.json')
    require(authority['real_train_authorized'] is True and authority['official_coco_nano_download_authorized'] is True
            and authority['dataset_sha256']==DATASET_SHA and authority['external_upload'] is False,
            'Current scoped authority required')
    require(torch.__version__=='2.7.1+cu118' and torchvision.__version__=='0.22.1+cu118'
            and yolox.__version__=='0.3.0','Qualified model environment changed')
    source=Path(yolox.__file__).resolve().parents[1]
    require(source.name=='YOLOX-'+UPSTREAM_COMMIT,'Wrong official YOLOX source revision')
    require(torch.cuda.is_available(),'CUDA required, CPU training is forbidden')
    device=torch.device('cuda:0');gpu=torch.cuda.get_device_properties(device)
    require('GTX 1050 Ti' in gpu.name,'Wrong qualified GPU')
    random.seed(config['seed']);np.random.seed(config['seed']);torch.manual_seed(config['seed'])
    torch.cuda.manual_seed_all(config['seed'])
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
    train=strict_json(run/'dataset/annotations/train.json')
    batches=train_batches(train)
    inputs=[]
    for image,labels in batches:
        pixels=cv2.imread(str(run/'dataset'/image['file_name']),cv2.IMREAD_COLOR)
        require(pixels is not None,'TRAIN decode failed')
        values,ratio=letterbox(pixels,config['input'])
        inputs.append((image,torch.from_numpy(values[None]).to(device),
                       torch.from_numpy(loss_targets(labels,ratio)).to(device)))
    exp=get_exp(None,'yolox-nano');exp.num_classes=2;exp.input_size=(416,416)
    exp.warmup_epochs=0;exp.basic_lr_per_img=config['learning_rate']
    exp.momentum=config['momentum'];exp.weight_decay=config['weight_decay']
    model=exp.get_model()  # Exactly once: upstream get_model resets class biases.
    pretrained=torch.load(weight,map_location='cpu',weights_only=True)
    require(isinstance(pretrained,dict) and 'model' in pretrained,'Official checkpoint lacks model state')
    filtered,skipped=transfer_mapping(model.state_dict(),pretrained['model'])
    missing=model.load_state_dict(filtered,strict=False)
    require(set(missing.missing_keys)==set(skipped) and not missing.unexpected_keys,'Transfer incomplete')
    del pretrained,filtered
    model.to(device).float();model.train();optimizer=exp.get_optimizer(1)
    require(all(g['lr']==.001 and g['momentum']==.9 and g['nesterov'] is True for g in optimizer.param_groups),
            'Optimizer differs from frozen budget')
    initial={k:v.detach().cpu().clone() for k,v in model.named_parameters()}
    assignments=[];original=model.head.get_assignments;signature=inspect.signature(original)
    def cuda_assignments(*args,**kwargs):
        binding=signature.bind(*args,**kwargs);binding.apply_defaults()
        require(binding.arguments['mode']=='gpu','Assignment CPU fallback forbidden')
        require(all(not torch.is_tensor(v) or v.is_cuda for v in binding.arguments.values()),
                'Assignment left CUDA')
        assignments.append('cuda');return original(*args,**kwargs)
    model.head.get_assignments=cuda_assignments
    freeze={'public_code_commit':git(root,'rev-parse','HEAD'),'branch':git(root,'branch','--show-current'),
            'historical_baseline_commit':'b75819db3bc2c542eede1b28ac854049f7ba3acc',
            'config':config,'config_sha256':file_sha(run/'training-config.json'),
            'dataset_manifest_sha256':file_sha(run/'dataset/manifest.json'),
            'gt_lock_sha256':GT_SHA,'dataset_lock_sha256':DATASET_SHA,
            'pretrained_sha256':file_sha(weight),'environment':{'torch':torch.__version__,
             'torchvision':torchvision.__version__,'yolox':yolox.__version__,'cuda':torch.version.cuda,
             'gpu':gpu.name,'vram_bytes':gpu.total_memory,'compute_capability':[gpu.major,gpu.minor]},
            'source_files_sha256':{p.name:file_sha(p) for p in Path(__file__).parent.glob('*.py')},
            'skipped_pretrained_keys':skipped,'loaded_pretrained_keys':len(model.state_dict())-len(skipped),
            'sample_order':[i[0]['frame_id'] for i in inputs],
            'no_dev_val_during_training':True,'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    write_json(run/'run-freeze.json',freeze)
    claim_attempt(run/'training-start.json',{'optimizer_steps':100,'freeze_sha256':file_sha(run/'run-freeze.json')})
    stop=threading.Event();monitor_errors=[]
    monitor=threading.Thread(target=telemetry,args=(stop,run/'gpu-telemetry.csv',monitor_errors),daemon=True)
    monitor.start();torch.cuda.reset_peak_memory_stats(device);torch.cuda.synchronize()
    started=time.perf_counter();losses=[]
    try:
        with (run/'loss-history.jsonl').open('xb') as log:
            for step in range(config['optimizer_steps']):
                image,x,y=inputs[step%2];optimizer.zero_grad(set_to_none=True)
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
                row={'step':step+1,'frame_id':image['frame_id'],'split':'TRAIN','gradient_l1':grad_l1,
                     'losses':{k:float(v.detach().item()) if torch.is_tensor(v) else float(v) for k,v in output.items()},
                     'elapsed_seconds':time.perf_counter()-started}
                require(all(np.isfinite(v) for v in row['losses'].values()),'Nonfinite loss component')
                losses.append(row);log.write(canonical(row)+b'\n');log.flush()
                if step==0 or (step+1)%10==0:
                    print(f"TRAIN step {step+1}/100 loss={row['losses']['total_loss']:.6f}",flush=True)
        elapsed=time.perf_counter()-started
        require(len(assignments)==100,'Every assignment must run on CUDA exactly once per step')
        changed={k:float((v.detach().cpu()-initial[k]).abs().sum().item()) for k,v in model.named_parameters()}
        require(sum(changed.values())>0,'Model parameters did not learn')
        checkpoint={'model':to_cpu(model.state_dict(),torch),'optimizer':to_cpu(optimizer.state_dict(),torch),
                    'config':config,'completed_optimizer_steps':100,
                    'freeze_sha256':file_sha(run/'run-freeze.json')}
        with (run/'final-checkpoint.pth').open('xb') as dst:torch.save(checkpoint,dst)
        restored=torch.load(run/'final-checkpoint.pth',map_location='cpu',weights_only=True)
        require(equal_state(checkpoint,restored,torch),'Checkpoint round-trip differs')
        model.load_state_dict(restored['model'],strict=True)
        optimizer.load_state_dict(restored['optimizer'])
        require(equal_state(model.state_dict(),restored['model'],torch)
                and equal_state(optimizer.state_dict(),restored['optimizer'],torch), 'Strict restore differs')
        training={'optimizer_steps':100,'train_frame_uses':{i[0]['frame_id']:50 for i in inputs},
                  'cuda_assignment_calls':len(assignments),'cpu_fallback_calls':0,
                  'wall_seconds':elapsed,'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),
                  'peak_reserved_bytes':torch.cuda.max_memory_reserved(device),
                  'changed_parameter_tensors':sum(v>0 for v in changed.values()),
                  'parameter_absolute_change':sum(changed.values()),
                  'first_10_mean_loss':sum(r['losses']['total_loss'] for r in losses[:10])/10,
                  'last_10_mean_loss':sum(r['losses']['total_loss'] for r in losses[-10:])/10,
                  'checkpoint_sha256':file_sha(run/'final-checkpoint.pth'),'checkpoint_reload_equal':True}
        write_json(run/'training-result.json',training)
        print('100 steps completed; strict checkpoint round-trip passed; starting ONLY DEV_VAL evaluation.',flush=True)
        # No test pixels or labels enter the optimizer loop above.
        dev=strict_json(run/'dataset/annotations/dev_val.json')
        claim_attempt(run/'dev-val-start.json',{'evaluation_count':1,'forward_count_expected':2,
                                               'checkpoint_sha256':training['checkpoint_sha256']})
        (run/'visualizations').mkdir();model.eval();evaluations=[]
        with torch.inference_mode():
            for image in dev['images']:
                require(image['split']=='DEV_VAL' and image['underlying_match_id']=='natural_match_04',
                        'Wrong fixed DEV_VAL split')
                path=run/'dataset'/image['file_name'];pixels=cv2.imread(str(path),cv2.IMREAD_COLOR)
                require(pixels is not None,'DEV_VAL decode failed')
                values,ratio=letterbox(pixels,416)
                raw=model(torch.from_numpy(values[None]).to(device))
                require(raw.shape==(1,3549,7) and torch.isfinite(raw).all().item(),'Invalid Nano raw outputs')
                raw_rows=raw[0].cpu().tolist()
                retained=postprocess(raw.clone(),2,config['confidence'],config['nms_iou'],class_agnostic=False)[0]
                rows=[] if retained is None else retained.cpu().tolist()
                predictions=decode_detections(rows,ratio,image['width'],image['height'])
                labels=[a for a in dev['annotations'] if a['image_id']==image['id']]
                gt=[{'object_id':a['object_id'],'visual_class':a['gt_metadata']['visual_class'],'bbox':a['bbox']} for a in labels]
                complete=image['standard_full_frame_metrics_allowed'] is True
                assessment=evaluate_frame(gt,predictions,complete,config['matching_iou'])
                record={'frame_id':image['frame_id'],'timestamp_seconds':image['timestamp_seconds'],
                        'underlying_match_id':image['underlying_match_id'],'predictions':predictions,**assessment}
                write_json(run/f"raw-{image['frame_id']}.json",{'columns':['center_x','center_y','width','height','objectness','skeleton_probability','witch_probability'],
                           'coordinate_space':'416_letterboxed','rows':raw_rows})
                write_json(run/f"prediction-{image['frame_id']}.json",record)
                draw_review(path,run/'visualizations'/f"{image['timestamp_seconds']:g}s.png",gt,predictions,config,complete)
                evaluations.append(record)
                print(f"DEV_VAL {image['timestamp_seconds']:g}s: retained={len(predictions)} TP={assessment['tp']} FN={assessment['fn']}",flush=True)
        require(len(evaluations)==2,'Exactly two fixed DEV_VAL forwards required')
        summary={'scope':'development_validation_smoke_not_blind_test','config':config,'training':training,
                 'frames':evaluations,'accepted_gt_count':5,'matched_gt_iou_05':sum(r['tp'] for r in evaluations),
                 'eval_forward_count':2,'eval_run_count':1,'mAP':None,'fp_per_minute':None,
                 'owner_discrimination_evaluated':False,'production_model_lock_created':False,
                 'partial_frame_unmatched_are_unjudged':True,'result_is_not_accuracy_acceptance':True}
        write_json(run/'evaluation-summary.json',summary)
    finally:
        stop.set();monitor.join(timeout=20)
        require(not monitor.is_alive() and not monitor_errors,'GPU monitoring failed; preserve run and report')
    write_json(run/'result.json',{'status':'TWO_CLASS_SMOKE_TRAINING_COMPLETE',
                                'training_result_sha256':file_sha(run/'training-result.json'),
                                'evaluation_summary_sha256':file_sha(run/'evaluation-summary.json')})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True);parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve();run=private_path(root,args.run)
    try:
        execute(root,args.lock,run)
    except Exception as exc:
        if not (run/'failure.json').exists():
            write_json(run/'failure.json',{'type':type(exc).__name__,'message':str(exc),
                                        'training_start_present':(run/'training-start.json').exists(),
                                        'no_implicit_retry_authorized':True})
        traceback.print_exc();raise SystemExit(2)


if __name__=='__main__':
    main()
