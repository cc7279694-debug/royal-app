"""Attempt02 TRAIN-only human review preparation, never a training entry point.

Reads the immutable Attempt01 snapshot; generates new ignored diagnostics only.
No detector, model inference, automatic final labels, network or installation.
"""
import argparse
from copy import deepcopy
import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'smoke_training'))
from smoke_data import (CLASS_SCHEMA, DATASET_SHA, GT_SHA, canonical, file_sha,
                        load_locked, private_path, require, strict_json, write_json)
from clash_tracker_video.evidence_prepare import load_indexes, prepare_evidence

def load_profile(root, path):
    """Load private media identities at runtime, never embed them in Git source."""
    p = strict_json(private_path(root, path))
    require(type(p) is dict and set(p)=={'old_run','dataset_lock','source_recording',
            'source_sha256','index_paths','recording_id','underlying_match_id'}, 'Invalid private profile')
    require(p['recording_id']=='development_01' and p['underlying_match_id']=='natural_match_01',
            'Only authorized TRAIN underlying match')
    digest=p['source_sha256']
    require(type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest), 'Invalid source hash')
    require(type(p['index_paths']) is list and bool(p['index_paths'])
            and all(type(v) is str for v in p['index_paths']), 'Explicit source index list required')
    for rel in [p['old_run'],p['dataset_lock'],p['source_recording'],*p['index_paths']]:
        require(type(rel) is str, 'Profile paths must be strings')
        private_path(root,rel)
    require(Path(p['source_recording']).suffix.lower()=='.mp4', 'MP4 source required')
    return p


def validate_train_export(train, images, objects):
    """Each exact GT object once, assigned to its own actual exported frame."""
    rows=train['images']; annotations=train['annotations']; categories=train['categories']
    require(len(rows)==len(images) and len({i['id'] for i in rows})==len(rows)
            and len({i['frame_id'] for i in rows})==len(rows)
            and {i['frame_id'] for i in rows}==set(images), 'Export image identities differ')
    require(len(categories)==2 and all(type(c['id']) is int for c in categories)
            and {c['id']:c['name'] for c in categories}=={v:k for k,v in CLASS_SCHEMA.items()}, 'Category IDs swapped/duplicated')
    require(len(annotations)==len(objects)
            and len({a['object_id'] for a in annotations})==len(annotations)
            and {a['object_id'] for a in annotations}==set(objects), 'Exact GT object coverage required')
    by_id={i['id']:i['frame_id'] for i in rows}
    for a in annotations:
        g=objects[a['object_id']]
        require(by_id.get(a['image_id'])==g['frame_id'], 'Export box attached to wrong image')
        require(a['bbox']==g['bbox_xywh_pixels'] and type(a['category_id']) is int
                and a['category_id']==CLASS_SCHEMA[g['visual_class']], 'Export/GT bbox or class mismatch')


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)


def save_image(path, image):
    with path.open('xb') as handle:
        image.save(handle, format='PNG')


def contact_sheet(frames, destination, root, *, columns=4, image_key='source_image_relative_to_repo'):
    thumb_width, thumb_height, label_height = 216, 480, 54
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new('RGB', (columns * thumb_width, rows * (thumb_height + label_height)), '#151922')
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        x = i % columns * thumb_width; y = i // columns * (thumb_height + label_height)
        with Image.open(root / f[image_key]) as image:
            image = image.convert('RGB'); image.thumbnail((thumb_width, thumb_height))
            sheet.paste(image, (x, y + label_height))
        label = f.get('review_frame_id', f['frame_id'][:12])
        draw.text((x + 4, y + 4), f"{label} | m01 | {f['timestamp_seconds']:.3f}s", fill='white', font=font(12))
        draw.text((x + 4, y + 24), f.get('sampling_role', 'TRAIN survey'), fill='#ffd982', font=font(12))
    save_image(destination, sheet)


def references(root, profile):
    # Every report/request is validated before deduplication by the unchanged loader.
    merged = load_indexes([root / rel for rel in profile['index_paths']])
    require(set(merged) == {'development_01'}, 'Only authorized TRAIN match indexes')
    images = {}
    for rel in profile['index_paths']:
        index = strict_json(root / rel)
        for f in index['frames']:
            if f['status'] == 'success':
                images.setdefault(f['frame_id'], dict(f, source_index=rel,
                    source_report=(Path(rel).parent / index['export_report']).as_posix(),
                    source_image_relative_to_repo=(Path(rel).parent / f['image_path']).as_posix()))
    return images


def sanity(root, destination, payload, profile):
    """Check actual old export against frozen labels before drawing diagnostics."""
    from data_contract import bbox_to_roi, fixed_roi
    old = private_path(root, profile['old_run'])
    manifest = strict_json(old / 'dataset/manifest.json')
    require(manifest['class_schema'] == CLASS_SCHEMA, 'Class index swap in old export')
    for rel, digest in manifest['files'].items():
        require(file_sha(old / 'dataset' / rel) == digest, 'Old dataset export changed')
    train = strict_json(old / 'dataset/annotations/train.json')
    gt = payload['gt_snapshot']
    images = {f['frame_id']: f for f in gt['frames'] if f['split'] == 'TRAIN'}
    objects = {o['object_id']: o for o in gt['positive_objects'] if o['frame_id'] in images}
    require(len(images) == 2 and len(objects) == 6, 'Old TRAIN identity changed')
    validate_train_export(train,images,objects)
    receipt = {'status': 'TRAIN_SANITY_CHECK_PASSED', 'class_schema': CLASS_SCHEMA,
               'original_gt_sha256': GT_SHA, 'original_dataset_sha256': DATASET_SHA,
               'checked_train_frames': 2, 'checked_train_boxes': 6, 'details': []}
    for f in sorted(images.values(), key=lambda f:f['timestamp_seconds']):
        source = root / f['source_image_relative_to_repo']
        exported = next(i for i in train['images'] if i['frame_id'] == f['frame_id'])
        require(file_sha(old / 'dataset' / exported['file_name']) == f['image_sha256'], 'Export/source image mismatch')
        with Image.open(source) as image:
            original = image.convert('RGB')
        roi = fixed_roi(list(original.size)); cropped = original.crop(tuple(roi))
        original_draw = ImageDraw.Draw(original); crop_draw = ImageDraw.Draw(cropped)
        original_draw.rectangle(roi, outline='cyan', width=2)
        details = []
        for g in objects.values():
            if g['frame_id'] != f['frame_id']: continue
            box = g['bbox_xywh_pixels']; moved = bbox_to_roi(box, list(original.size))
            x,y,w,h = box; cx,cy,cw,ch = moved
            color = '#ff6262' if g['visual_class'] == 'unit.skeleton' else '#5dff8b'
            label = f"{g['object_id'][-2:]} class {CLASS_SCHEMA[g['visual_class']]} {g['visual_class'].split('.')[1]}"
            original_draw.rectangle((x,y,x+w,y+h), outline=color, width=2)
            crop_draw.rectangle((cx,cy,cx+cw,cy+ch), outline=color, width=2)
            crop_draw.text((max(0,cx-20), max(0,cy-14)), label, fill=color, font=font(10))
            details.append({'object_id':g['object_id'], 'class_index':CLASS_SCHEMA[g['visual_class']], 'original_bbox':box, 'roi_bbox':moved})
        save_image(destination / f"sanity-{f['timestamp_seconds']:.0f}s-original.png", original)
        save_image(destination / f"sanity-{f['timestamp_seconds']:.0f}s-roi.png", cropped)
        receipt['details'].append({'frame_id':f['frame_id'], 'roi_xyxy':roi, 'objects':details})
    write_json(destination / 'train-sanity.json', receipt)
    return receipt


def preview(root, output, profile):
    output = private_path(root, output)
    # Metadata-only interrupted preflight can resume, never overwrite a result.
    require(not (output / 'historical-protection-before.json').exists()
            and not (output / 'train-sanity.json').exists(), 'Preparation already frozen')
    output.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for base in ('local_data', 'outputs', 'tools/offline_video', 'tools/smoke_training'):
        for folder, directories, files in os.walk(root / base):
            parent = Path(folder)
            directories[:] = [name for name in directories
                if name not in ('environments', '__pycache__', '.pytest_cache', 'build')
                and not name.endswith('.egg-info') and parent/name != output
                and not (parent/name).is_symlink() and not (parent/name).is_junction()]
            for name in files:
                path = parent / name
                if path.is_symlink() or path.is_junction(): continue
                rel = path.relative_to(root)
                inventory[rel.as_posix()] = file_sha(path)
    write_json(output / 'historical-protection-before.json', {'sha256_before':inventory})
    print(f'Protected {len(inventory)} existing files; excluded model environment and this new preparation directory.', flush=True)
    payload = load_locked(root, root / profile['dataset_lock'])
    frozen_source = next(f['source_sha256'] for f in payload['gt_snapshot']['frames'] if f['underlying_match_id']=='natural_match_01')
    require(file_sha(root / profile['source_recording']) == profile['source_sha256'] == frozen_source, 'Original TRAIN recording changed')
    sanity(root, output, payload, profile)
    refs = references(root, profile)
    survey = strict_json(root / profile['index_paths'][0])
    frames = [refs[f['frame_id']] for f in survey['frames'] if f['status'] == 'success']
    for i in range(0, len(frames), 12):
        contact_sheet(frames[i:i+12], output / f'survey-{i//12+1:02}.png', root)
    write_json(output / 'preview-index.json', {'frames':frames, 'match':'natural_match_01', 'model_used':False, 'human_confirmed':False})
    print(f'TRAIN sanity 2 frames / 6 boxes OK; {len(frames)} existing survey frames; no extraction or training.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    args = parser.parse_args()
    root=args.root.resolve()
    preview(root, args.output, load_profile(root,args.profile))
