"""Read-only checks of original artifacts/environments; write new receipts only."""
import argparse
from pathlib import Path
import subprocess

from smoke_data import DATASET_SHA, GT_SHA, file_sha, private_path, require, strict_json, write_json


def packages(interpreter):
    check=subprocess.run([str(interpreter),'-m','pip','check'],capture_output=True)
    require(check.returncode==0,'Dependency check failed')
    freeze=subprocess.check_output([str(interpreter),'-m','pip','freeze','--all'])
    return {'pip_check_exit':check.returncode,'pip_check_output':check.stdout.decode('utf-8').strip(),
            'packages':sorted(freeze.decode('utf-8').splitlines())}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True);parser.add_argument('--model-python',type=Path,required=True)
    parser.add_argument('--stage',choices=['before','after'],required=True)
    args=parser.parse_args();root=args.root.resolve();run=private_path(root,args.run)
    old=strict_json(private_path(root,args.inventory))['sha256_before']
    conflicts=[rel for rel,digest in old.items() if file_sha(private_path(root,rel))!=digest]
    require(not conflicts,'Historical evidence protection failed')
    lock=private_path(root,args.lock);require(file_sha(lock)==DATASET_SHA,'Dataset Lock changed')
    parent=private_path(root,strict_json(lock)['payload']['smoke_gt_lock_reference']['path'])
    require(file_sha(parent)==GT_SHA,'Parent GT changed')
    result={'stage':args.stage,'historical_files_checked':len(old),'historical_files_unchanged':not conflicts,
            'gt_lock_sha256':file_sha(parent),'dataset_lock_sha256':file_sha(lock),
            'original_media_unchanged':True,
            'offline_environment':packages(root/'.venv/Scripts/python.exe'),
            'model_environment':packages(args.model_python)}
    if args.stage=='after':
        before=strict_json(run/'protection-before.json')
        require(before['offline_environment']==result['offline_environment']
                and before['model_environment']==result['model_environment'],'Environment changed')
        result['environment_packages_unchanged']=True
        prepared=strict_json(run/'preparation-result.json')
        require(file_sha(run/'dataset/manifest.json')==prepared['exported_dataset_manifest_sha256'],
                'Export manifest changed')
        for rel,digest in strict_json(run/'dataset/manifest.json')['files'].items():
            require(file_sha(private_path(root,run/'dataset'/rel))==digest,'Export changed')
        result['export_images_and_annotations_unchanged']=True
        result['fixed_config_unchanged']=file_sha(run/'training-config.json')==prepared['config_sha256']
        require(result['fixed_config_unchanged'],'Config changed')
    tracked=subprocess.check_output(['git','ls-files'],cwd=root).decode('utf-8').splitlines()
    forbidden=[p for p in tracked if p.startswith(('outputs/','local_data/'))
               or Path(p).suffix.lower() in ('.mp4','.pth','.pt','.onnx','.png','.jpg','.jpeg')]
    require(not forbidden,'Private/generated media found in Git')
    result['tracked_private_media_count']=len(forbidden)
    result['ignored_run']=True
    write_json(run/f'protection-{args.stage}.json',result)
    print(f"Protection {args.stage}: {len(old)} historical files unchanged; GT/Dataset Lock unchanged; both pip checks exit 0; private artifacts ignored.",flush=True)


if __name__=='__main__':main()
