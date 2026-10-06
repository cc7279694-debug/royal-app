"""Offline export and explicitly authorized official release download; no torch."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse
from urllib.request import urlopen

from smoke_data import (DATASET_SHA, GT_SHA, WEIGHT_URL, canonical, default_config,
                        export_dataset, file_sha, load_locked, private_path, require,
                        strict_json, validate_weight_url, verify_export, write_json)


def parse_release(raw):
    """gh emits UTF-8 bytes, independently of the Windows console locale."""
    return json.loads(raw.decode('utf-8'))


def preserve_json(path, value):
    if path.exists():
        require(canonical(strict_json(path)) == canonical(value), 'Existing preparation differs')
    else:
        write_json(path, value)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve();run=private_path(root,args.run)
    # An interrupted metadata preflight may resume, never replace prior artifacts.
    require(run.is_dir() and not (run/'preparation-result.json').exists(),
            'Run already prepared; do not replace any prior result')
    payload=load_locked(root,args.lock)
    if (run/'dataset').exists():
        manifest=verify_export(root,run/'dataset')
    else:
        manifest=export_dataset(root,payload,run/'dataset',DATASET_SHA)
    preserve_json(run/'training-config.json',default_config())
    preserve_json(run/'phase-c-authorization.json',{
        'source':'current_explicit_user_message','date':'2026-10-06',
        'scope':'one_2_class_nano_fixed_100_step_smoke_training_then_one_dev_val_evaluation',
        'dataset_sha256':DATASET_SHA,'gt_sha256':GT_SHA,
        'real_train_authorized':True,'official_coco_nano_download_authorized':True,
        'intended_use':'private_local_research_poc','external_upload':False,
        'redistribution':False,'rights_clearance':'unverified','is_production_model_lock':False,
        'historical_lock_flags_not_modified':True})
    pretrained=run/'pretrained'
    if pretrained.exists():
        require(not any(pretrained.iterdir()), 'Prior download/provenance cannot be overwritten')
    else:
        pretrained.mkdir()
    validate_weight_url(WEIGHT_URL)
    # The release API confirms this exact asset before any weight transfer.
    release=subprocess.run(['gh','api','repos/Megvii-BaseDetection/YOLOX/releases/tags/0.1.1rc0'],
                           capture_output=True,check=True)
    metadata=parse_release(release.stdout)
    candidates=[a for a in metadata['assets'] if a['name']=='yolox_nano.pth']
    require(metadata['tag_name']=='0.1.1rc0' and len(candidates)==1,'Official release/asset missing')
    asset=candidates[0];require(asset['browser_download_url']==WEIGHT_URL,'Nonofficial asset URL')
    provenance={
        'model':'YOLOX-Nano','upstream_repository':'https://github.com/Megvii-BaseDetection/YOLOX',
        'release_tag':'0.1.1rc0','exact_download_url':WEIGHT_URL,
        'downloaded_sha256':None,'download_status':'not_started',
        'expected_asset_size':asset['size'],'upstream_advertised_digest':asset.get('digest'),
        'upstream_code_license':'Apache-2.0','pretrained_dataset':'COCO',
        'rights_license_caveat':'Code license does not independently clear COCO source images, learned-weight rights, or game assets; local digest is not a publisher-supplied authenticity checksum.',
        'rights_clearance':'unverified','intended_use':'private_local_research_poc',
        'redistribution':False,'external_upload':False,
        'recorded_before_download_utc':datetime.now(timezone.utc).isoformat(),
    }
    write_json(pretrained/'provenance-before-download.json',provenance)
    path=pretrained/'yolox_nano.pth'
    with urlopen(WEIGHT_URL,timeout=60) as response:
        host=urlparse(response.geturl()).hostname
        require(host in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'),
                'Unexpected release redirect host; stop')
        with path.open('xb') as output:
            while chunk:=response.read(1024*1024):output.write(chunk)
    require(path.stat().st_size==asset['size'],'Release asset download is incomplete')
    provenance.update(downloaded_sha256=file_sha(path),download_status='complete',
                      downloaded_bytes=path.stat().st_size,final_redirect_host=host)
    write_json(pretrained/'provenance.json',provenance)
    write_json(run/'preparation-result.json',{
        'dataset_validate_exit':0,'counts':manifest['counts'],
        'exported_dataset_manifest_sha256':file_sha(run/'dataset/manifest.json'),
        'config_sha256':file_sha(run/'training-config.json'),
        'weight_sha256':file_sha(path),'original_lock_sha256':file_sha(args.lock),
        'original_lock_unchanged':file_sha(args.lock)==DATASET_SHA,
        'training_started':False})
    print('Prepared deterministic 2 TRAIN / 2 DEV_VAL / 11 accepted boxes; official Nano COCO weight pinned; no training executed.',flush=True)


if __name__=='__main__':
    main()
