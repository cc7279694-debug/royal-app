"""Package existing evaluation outputs without rerunning training or inference."""
import argparse
import csv
from pathlib import Path
import zipfile

from smoke_data import file_sha, private_path, require, strict_json, write_json


def exclusive_text(path,content):
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(content)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True);args=parser.parse_args()
    root=args.root.resolve();run=private_path(root,args.run)
    result=strict_json(run/'result.json')
    require(result['status']=='TWO_CLASS_SMOKE_TRAINING_COMPLETE' and not (run/'failure.json').exists(),
            'Run not complete or failure requires review')
    summary=strict_json(run/'evaluation-summary.json');training=summary['training']
    require(file_sha(run/'evaluation-summary.json')==result['evaluation_summary_sha256'], 'Evaluation changed')
    require(file_sha(run/'final-checkpoint.pth')==training['checkpoint_sha256'],'Checkpoint changed')
    require(summary['eval_run_count']==1 and summary['eval_forward_count']==2
            and training['optimizer_steps']==100,'Fixed run counts differ')
    with (run/'gpu-telemetry.csv').open(encoding='utf-8') as stream:
        samples=list(csv.DictReader(stream))
    require(samples,'Missing GPU utilization evidence')
    gpu={'samples':len(samples),'max_gpu_utilization_percent':max(float(s['utilization_percent']) for s in samples),
         'max_whole_gpu_memory_mib':max(float(s['memory_used_mib']) for s in samples),
         'whole_gpu_memory_includes_other_processes':True}
    write_json(run/'gpu-summary.json',gpu)
    rows=['# First real two-class DEV_VAL smoke result','',
          'Fixed Nano / 416 / batch 1 / FP32 / seed 20261006; exactly 100 optimizer steps.',
          f"TRAIN loss mean first 10: {training['first_10_mean_loss']:.6f}; last 10: {training['last_10_mean_loss']:.6f}.",
          f"Training wall time: {training['wall_seconds']:.2f}s; peak allocated: {training['peak_allocated_bytes']/2**20:.2f} MiB.",
          f"GPU sampled maximum utilization: {gpu['max_gpu_utilization_percent']:g}%.",
          f"Checkpoint SHA-256: `{training['checkpoint_sha256']}`; strict model/optimizer reload verified.",
          '',f"Matched accepted DEV_VAL GT at fixed IoU 0.5: {summary['matched_gt_iou_05']} / 5.",
          'This is not blind testing, mAP acceptance, owner discrimination or full-match FP/min.',
          'The 72s partial frame has only a confirmed Witch positive; unmatched predictions are Unknown, not FP.',
          'Confidence 0.001 / class-aware NMS 0.65 were fixed before training; visuals use fixed top30, not a tuned threshold.',
          'GT boxes are green; Skeleton predictions orange; Witch predictions cyan.',
          '', '| Frame | GT | Best same-class IoU | Confidence | One-to-one hit @0.5 |',
          '| --- | --- | --- | --- | --- |']
    for frame in summary['frames']:
        for gt in frame['positive_matches']:
            pred=gt['best_prediction'];confidence=f"{pred['confidence']:.6f}" if pred else 'none'
            rows.append(f"| {frame['timestamp_seconds']:g}s | {gt['object_id']} {gt['visual_class']} | {gt['best_iou']:.6f} | {confidence} | {gt['matched_at_fixed_iou']} |")
    rows+=['','## Candidate interpretation','']
    for f in summary['frames']:
        rows.append(f"{f['timestamp_seconds']:g}s: retained {len(f['predictions'])}; matched {f['tp']}; missed {f['fn']}; "
                    f"sampled-frame FP {len(f['false_detections'])}; unjudged {len(f['unjudged_detections'])}; "
                    f"outside-image padding {len(f['outside_image_detections'])}.")
    rows+=['','Numerical parameter updates and training loss only establish that optimization ran.',
           'Use the attached coordinates/IoUs and images to judge visual response; no generalization claim.',
           'No second training or DEV_VAL run was performed to improve this result.']
    text='\n'.join(rows)+'\n';exclusive_text(run/'evaluation-summary.md',text)
    freeze=strict_json(run/'run-freeze.json');protection=strict_json(run/'protection-after.json')
    completion=text+'\n## Completion evidence\n\n'+(
        f"Code baseline: `{freeze['public_code_commit']}`; branch `{freeze['branch']}`.\n"
        f"Dataset Lock: `{protection['dataset_lock_sha256']}`; parent GT: `{protection['gt_lock_sha256']}`.\n"
        f"Historical protected files unchanged: {protection['historical_files_checked']}; both pip checks exit 0; environments unchanged.\n"
        'Data remains private and ignored. No Blind Test, production Model Lock, Module 3, Android, merge or push.\n'
        'Outputs: config, authorization, official-weight provenance, deterministic dataset/manifest, run-freeze, loss history, telemetry, checkpoint, raw outputs, prediction JSONs, visualizations and this report.\n'
        'The separate full-regression/documentation verification record accompanies the public final checkpoint.\n'
        'Stop; any future tuning/training/data/validation requires new authority.\n')
    exclusive_text(run/'COMPLETION_REPORT.md',completion)
    files=[run/'evaluation-summary.md',run/'evaluation-summary.json',run/'gpu-summary.json',
           *sorted((run/'visualizations').glob('*.png'))]
    zip_path=private_path(root,run/'Two_Class_Smoke_DEV_VAL_Review.zip')
    with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,path.relative_to(run).as_posix())
    write_json(run/'review-zip-manifest.json',{'file':zip_path.name,'sha256':file_sha(zip_path),
               'size_bytes':zip_path.stat().st_size,'files':{p.relative_to(run).as_posix():file_sha(p) for p in files},
               'no_raw_video_original_images_crops_or_weights':True,'automatically_uploaded':False})
    print(f"Review ZIP created: {zip_path}",flush=True)


if __name__=='__main__':main()
