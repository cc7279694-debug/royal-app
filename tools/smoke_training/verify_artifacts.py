"""Read-only checks of original artifacts/environments; write new receipts only."""
import argparse
from pathlib import Path
import re
import subprocess

from smoke_data import DATASET_SHA, GT_SHA, file_sha, private_path, require, strict_json, write_json


def packages(interpreter):
    check=subprocess.run([str(interpreter),'-m','pip','check'],capture_output=True)
    require(check.returncode==0,'Dependency check failed')
    freeze=subprocess.check_output([str(interpreter),'-m','pip','freeze','--all'])
    return {'pip_check_exit':check.returncode,'pip_check_output':check.stdout.decode('utf-8').strip(),
            'packages':sorted(freeze.decode('utf-8').splitlines())}


def check_inventory(root, inventory):
    """Batch Git hygiene checks, retaining every hash and link/path check."""
    root=Path(root).resolve();paths={};private=set();public=set()
    for rel,digest in inventory.items():
        relative=Path(rel)
        require(not relative.is_absolute() and '..' not in relative.parts
                and (relative.parts[0] in ('outputs','local_data') or relative.as_posix().startswith('tools/offline_video/')),
                'Invalid protected inventory path')
        path=root/relative
        for ancestor in [path,*path.parents]:
            require(not ancestor.is_symlink() and not ancestor.is_junction(),'Linked protected path')
            if ancestor==root:break
        paths[relative.as_posix()]=(path,digest)
        (private if relative.parts[0] in ('outputs','local_data') else public).add(relative.as_posix())
    if private:
        ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=root,
                               input=('\n'.join(sorted(private))+'\n').encode('utf-8'),capture_output=True)
        require(ignored.returncode==0 and set(ignored.stdout.decode('utf-8').splitlines())==private,
                'Every private protected artifact must remain ignored')
    tracked=subprocess.check_output(['git','ls-files'],cwd=root).decode('utf-8').splitlines()
    require(not ({p.casefold() for p in private}&{p.casefold() for p in tracked}),'Private protected artifact tracked')
    require({p.casefold() for p in public}<={p.casefold() for p in tracked},'Legacy source no longer tracked')
    require(all(file_sha(path)==digest for path,digest in paths.values()),'Historical evidence protection failed')
    return len(paths)


def same_environment(before,after,allowed_git_refs):
    """pip freeze embeds editable checkout HEAD; it is not a package upgrade."""
    pattern=re.compile(r'^(-e git\+https://github\.com/cc7279694-debug/royal-app\.git@)([0-9a-f]{40})(#egg=clash_tracker_video&subdirectory=tools(?:\\|%5[Cc])offline_video)$')
    def normalized(value):
        result=dict(value);lines=[]
        for line in value['packages']:
            match=pattern.fullmatch(line)
            if match and match.group(2) in allowed_git_refs:
                line=match.group(1)+'<approved-local-checkout-commit>'+match.group(3)
            lines.append(line)
        result['packages']=sorted(lines);return result
    return normalized(before)==normalized(after)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True);parser.add_argument('--model-python',type=Path,required=True)
    parser.add_argument('--stage',choices=['before','after'],required=True)
    args=parser.parse_args();root=args.root.resolve();run=private_path(root,args.run)
    old=strict_json(private_path(root,args.inventory))['sha256_before']
    checked=check_inventory(root,old)
    lock=private_path(root,args.lock);require(file_sha(lock)==DATASET_SHA,'Dataset Lock changed')
    parent=private_path(root,strict_json(lock)['payload']['smoke_gt_lock_reference']['path'])
    require(file_sha(parent)==GT_SHA,'Parent GT changed')
    result={'stage':args.stage,'historical_files_checked':checked,'historical_files_unchanged':True,
            'gt_lock_sha256':file_sha(parent),'dataset_lock_sha256':file_sha(lock),
            'original_media_unchanged':True,
            'offline_environment':packages(root/'.venv/Scripts/python.exe'),
            'model_environment':packages(args.model_python)}
    if args.stage=='after':
        before=strict_json(run/'protection-before.json')
        refs=set(subprocess.check_output(['git','rev-list','b75819db3bc2c542eede1b28ac854049f7ba3acc..HEAD'],
                                         cwd=root).decode('utf-8').splitlines())
        refs.add('b75819db3bc2c542eede1b28ac854049f7ba3acc')
        require(same_environment(before['offline_environment'],result['offline_environment'],refs)
                and before['model_environment']==result['model_environment'],'Environment changed')
        result['environment_packages_unchanged']=True
        result['editable_checkout_commit_reference_changed_only']=before['offline_environment']!=result['offline_environment']
        result['approved_local_commit_refs']=sorted(refs)
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
