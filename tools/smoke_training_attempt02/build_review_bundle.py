"""Create a new immutable, TRAIN-only draft review packet from explicit choices.

Drawing proposed boxes does not confirm them. Zero proposed boxes is NOT an
absence label. No model, training, expanded lock, or evaluation is performed.
"""
import argparse
from copy import deepcopy
import csv
import html
from pathlib import Path
import re
import shutil
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw

from prepare_review import (CLASS_SCHEMA, DATASET_SHA, GT_SHA, contact_sheet, font,
                            save_image, load_profile)
from smoke_data import canonical, file_sha, load_locked, private_path, require, strict_json, write_json
from data_contract import annotation_digest, bbox_to_roi, fixed_roi, qualify_frame
from clash_tracker_video.evidence_prepare import load_indexes


POSITIVE_TIMES = [158, 160, 161, 162, 163, 164, 165, 166]
NEGATIVE_CANDIDATE_TIMES = [5, 10, 15, 75, 90, 95, 100, 105]


def validate_object_id(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}',value)
            and value.upper() not in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),
                                      *(f'LPT{i}' for i in range(1,10))}, 'Unsafe crop object identity')
    return value


def build(root, preparation, draft_path, profile):
    preparation = private_path(root, preparation)
    sanity = strict_json(preparation / 'train-sanity.json')
    require(sanity['status'] == 'TRAIN_SANITY_CHECK_PASSED', 'Original TRAIN export must be checked first')
    payload = load_locked(root, root / profile['dataset_lock'])
    source_path=profile['source_recording']; source_sha=profile['source_sha256']
    frozen_source = next(f['source_sha256'] for f in payload['gt_snapshot']['frames'] if f['underlying_match_id']=='natural_match_01')
    require(file_sha(root / source_path) == source_sha == frozen_source, 'TRAIN source changed')
    indexes = [root / rel for rel in profile['index_paths']] + [preparation / 'new-sampling/index.json']
    merged = load_indexes(indexes)
    require(set(merged) == {'development_01'}, 'Do not read other matches')
    records = {}
    bindings = []
    for index_path in indexes:
        index = strict_json(index_path)
        report = index_path.parent / index['export_report']
        bindings.append({'index':index_path.relative_to(root).as_posix(), 'index_sha256':file_sha(index_path),
                         'report':report.relative_to(root).as_posix(), 'report_sha256':file_sha(report)})
        for f in index['frames']:
            if f['status'] == 'success':
                records.setdefault(f['timestamp_seconds'], dict(f,
                    source_image_relative_to_repo=(index_path.parent/f['image_path']).relative_to(root).as_posix(),
                    source_index=index_path.relative_to(root).as_posix()))
    require(all(t in records for t in POSITIVE_TIMES+NEGATIVE_CANDIDATE_TIMES), 'Requested real PTS frame missing')
    proposals = strict_json(private_path(root, draft_path))
    require(proposals['kind'] == 'codex_visual_drafts_not_human_confirmed'
            and proposals['model_used'] is False, 'Only explicit visual drafts')
    proposed = proposals['objects']
    for o in proposed: validate_object_id(o['object_id'])
    require(all(o['timestamp_seconds'] in POSITIVE_TIMES for o in proposed), 'Draft source outside chosen TRAIN frames')
    bundle = private_path(root, preparation/'human-review-bundle')
    bundle.mkdir(exist_ok=False)
    for name in ('originals', 'review-images', 'roi', 'crops', 'contact-sheets'):
        (bundle/name).mkdir()
    original_gt = payload['gt_snapshot']
    old_frames = {f['timestamp_seconds']:f for f in original_gt['frames'] if f['split']=='TRAIN'}
    old_objects = original_gt['positive_objects']
    frames, objects = [], []
    all_times = sorted(POSITIVE_TIMES + NEGATIVE_CANDIDATE_TIMES)
    for number, time in enumerate(all_times, 1):
        r = records[time]; fid = r['frame_id']; prior = old_frames.get(time)
        source = private_path(root, r['source_image_relative_to_repo'])
        image_rel = f'originals/{fid}.png'
        shutil.copyfile(source, bundle/image_rel)
        require(file_sha(bundle/image_rel)==file_sha(source), 'Copied original PNG differs')
        with Image.open(source) as image:
            original = image.convert('RGB')
        size = list(original.size); roi = fixed_roi(size)
        annotated = original.copy(); d = ImageDraw.Draw(annotated)
        d.rectangle(roi, outline='cyan', width=2)
        here = [deepcopy(o) for o in old_objects if prior and o['frame_id']==fid]
        for o in here:
            o.update(class_id=CLASS_SCHEMA[o['visual_class']], annotation_source='unchanged_human_confirmed_GT_v1',
                     confirmed_by='ChatGPT (original user-relayed review)', is_skeleton_card_deployment=False)
        for o in proposed:
            if o['timestamp_seconds'] != time: continue
            item = deepcopy(o)
            item.update(frame_id=fid, underlying_match_id='natural_match_01', recording_id='development_01',
                class_id=CLASS_SCHEMA[item['visual_class']], review_state='pending_human_review',
                state='draft', confirmed_by=None, annotation_source='Codex_visual_proposal_not_final_GT',
                entity_id=None, deployment_id=None, is_skeleton_card_deployment=False)
            here.append(item)
        require(len({o['object_id'] for o in here})==len(here), 'Duplicate object identity')
        for o in here:
            box = o['bbox_xywh_pixels']; x,y,w,h = box
            require(all(type(v) is int for v in box), 'Draft GT must use integer xywh')
            o['bbox_xywh_roi'] = bbox_to_roi(box, size)
            color = '#ff6262' if o['visual_class']=='unit.skeleton' else '#5dff8b'
            d.rectangle((x,y,x+w,y+h), outline=color, width=2)
            d.text((max(0,x-30),max(120,y-14)), f"{o['object_id']} c{o['class_id']}", fill=color, font=font(9))
            crop_rel = f"crops/{validate_object_id(o['object_id'])}.png"
            save_image(bundle/crop_rel, original.crop((max(0,x-16),max(0,y-16),min(size[0],x+w+16),min(size[1],y+h+16))))
            o['context_crop'] = crop_rel
        d.text((4,125), f"m01 | TRAIN | {time:.3f}s | {'OLD CONFIRMED' if prior else 'PENDING REVIEW'}", fill='white', font=font(11))
        review_rel = f'review-images/{fid}.png'; roi_rel = f'roi/{fid}.png'
        save_image(bundle/review_rel, annotated); save_image(bundle/roi_rel, annotated.crop(tuple(roi)))
        role = 'positive_proposal' if time in POSITIVE_TIMES else 'negative_candidate_NOT_GT'
        if prior: role = 'confirmed_positive_GT_v1'
        frame = {'review_frame_id':f'a02_frame_{number:02}', 'frame_id':fid,
                 'underlying_match_id':'natural_match_01', 'recording_id':'development_01', 'split':'TRAIN',
                 'timestamp_seconds':time, 'raw_pts':r['raw_pts'], 'time_base':r['time_base'],
                 'source_recording':source_path, 'source_sha256':source_sha, 'source_index':r['source_index'],
                 'source_image_relative_to_repo':r['source_image_relative_to_repo'],
                 'image_sha256':file_sha(source), 'image_size':size, 'roi_xyxy':roi,
                 'original_image':image_rel, 'review_image':review_rel, 'roi_image':roi_rel,
                 'review_state':'confirmed' if prior else 'pending_human_review', 'sampling_role':role,
                 'exhaustive_for_selected_classes':True if prior else None,
                 'remaining_unknown_regions':'none_material' if prior else 'pending_selected_class_exhaustive_review',
                 'negative_confirmed':False if prior else None,
                 'positive_object_ids':[o['object_id'] for o in here],
                 'unknown_not_negative':True, 'standard_training_loss_allowed':bool(prior),
                 'coverage_source':'unchanged_GT_v1' if prior else None}
        frame['draft_annotation_sha256'] = annotation_digest(frame, here)
        frames.append(frame); objects.extend(here)
    require(len(frames)==16 and len({f['frame_id'] for f in frames})==16, 'Sixteen distinct source PTS frames required')
    require(len({o['object_id'] for o in objects})==len(objects), 'Object identity collision')
    for i in range(0,len(frames),8):
        contact_sheet(frames[i:i+8], bundle/f'contact-sheets/sheet-{i//8+1:02}.png', bundle, image_key='review_image')
    groups = proposals['group_proposals']
    write_json(bundle/'draft-annotations.json', {'objects':objects, 'groups':groups, 'state':'mixed_old_confirmed_and_new_drafts',
        'new_drafts_human_confirmed':False, 'spawned_skeleton_is_skeleton_card_deployment':False})
    write_json(bundle/'review-index.json', {'frames':frames, 'class_schema':CLASS_SCHEMA, 'selected_classes_exhaustive_scope':'both owners in fixed ROI',
        'source_bindings':bindings, 'model_used':False, 'training_started':False})
    write_json(bundle/'human-return-template.json', {
        'status':'pending_human_review', 'reviewer':None, 'confirmation_source':None,
        'review_packet_sha256':'use_ZIP_SHA_from_packaging_receipt_not_self_referential',
        'objects':[{'object_id':o['object_id'], 'decision':None, 'corrected_bbox_xywh_pixels':None,
                    'corrected_visual_class':None, 'owner':None, 'form':None, 'origin_kind':None,
                    'appearance_group_id':None, 'source_relationship':None, 'visibility':None, 'occlusion':None,
                    'uncertain_reason':None} for o in objects if o['review_state']!='confirmed'],
        'group_decisions':[{'appearance_group_id':g['appearance_group_id'], 'decision':None,
                            'continuity_confirmed':None, 'source_relationship_confirmed':None,
                            'independent_deployment_confirmed':None} for g in groups],
        'frame_coverage_confirmations':[{'frame_id':f['frame_id'], 'exhaustive_for_selected_classes':None,
                                        'remaining_unknown_regions':None, 'negative_confirmed':None,
                                        'additional_objects':[]} for f in frames if f['review_state']!='confirmed']})
    fields = ['review_frame_id','frame_id','timestamp_seconds','sampling_role','exhaustive_for_selected_classes','negative_confirmed','remaining_unknown_regions']
    with (bundle/'frame-review.csv').open('x',encoding='utf-8',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
        writer.writerows({k:f[k] for k in fields} for f in frames)
    config = {'model':'yolox-nano','input':640,'batch':1,'precision':'FP32','optimizer_steps':300,'seed':20261006,
        'learning_rate':0.001,'momentum':0.9,'nesterov':True,'weight_decay':0.0005,'augmentation':'none','scheduler':'none',
        'confidence':0.001,'nms_iou':0.65,'matching_iou':0.5,'visualization_top_k':30,'dev_tune_evaluation_count':1,
        'class_schema':CLASS_SCHEMA,'split_roles':{'natural_match_01':'TRAIN','natural_match_04':'DEV_TUNE'},
        'roi_rule':'[0,H//8,W,H*31//40] half-open pixel xyxy','roi_for_source':[0,120,432,744],
        'training_started':False,'training_ready_expanded_lock_created':False,'production_model_lock':False,
        'official_weight_sha256':'cd28f55fbbc1829f99d9ac9b38a16d259a22889739c8728ea877610201feff7b',
        'parent_GT_sha256':GT_SHA,'parent_training_dataset_sha256':DATASET_SHA}
    write_json(bundle/'attempt02-fixed-config.json',config)
    shutil.copyfile(preparation/'train-sanity.json',bundle/'train-sanity.json')
    for p in preparation.glob('sanity-*.png'): shutil.copyfile(p,bundle/p.name)
    instructions = '''# Attempt02 TRAIN review — pending, not training-ready

16 frames: 8 positive proposals (including 2 unchanged confirmed v1 frames),
8 candidate negatives. Only natural_match_01 is present. No DEV image or model
prediction was consulted in selection. No training/inference has occurred.

Skeleton=0, Witch=1. Original bbox coordinates are integer xywh at 432x960.
Fixed battlefield crop is [0,120,432,744], same rule later for DEV_TUNE.
The copied old 163s/164s six boxes remain confirmed and unchanged. All new boxes
are Codex visual DRAFTS, not ChatGPT confirmation. Empty proposed annotations are
not evidence of absence. Do not train until the 14 pending frames are reviewed.

For EVERY new frame, inspect the unmodified full PNG and the marked ROI. Confirm
or correct/add every Witch and Skeleton in the ROI, including either owner.
Record exhaustive_for_selected_classes, remaining_unknown_regions and explicit
negative_confirmed for zero-target frames. A rejected ambiguous proposed box
does not become background; if any relevant Unknown remains, mark the frame
partial and do not qualify it for standard training loss.

For each proposed/additional object record confirm/correct/reject, original-image
bbox, visual_class, owner, form, origin_kind, appearance_group_id, relationship,
visibility/occlusion and uncertain_reason. Unknown form is allowed. Group IDs
are proposals: confirm continuity across adjacent frames or correct grouping.
The continuous Witch is proposed to retain the old Witch episode identity.
Skeleton before/after 163s may be different spawned waves; their temporal
relationship needs review, not per-frame automatic event counting. No new
independent deployment is claimed. Skeleton spawn is never a Skeleton card play.

Use human-return-template.json or an equivalent textual answer. Refer to the
actual ZIP SHA from the separately returned packaging receipt. Reviewer and
review time stay null until a genuine return; no manufactured ChatGPT verdict.
After factual review, freeze a new expanded snapshot (never overwrite v1), then
the already-authorized fixed Nano640/300-step run may proceed. No Attempt03.

Private local PoC only. No automatic upload or redistribution. Game rights
remain unverified; a GT label or user authorization is not legal clearance.
'''
    (bundle/'HUMAN_REVIEW.md').write_text(instructions,encoding='utf-8')
    rows = []
    for f in frames:
        rows.append('<section><h2>'+html.escape(f"{f['review_frame_id']} | {f['timestamp_seconds']}s | {f['sampling_role']}")+ '</h2>'
            +f'<p>match: natural_match_01 | frame: {f["frame_id"]} | PTS: {f["raw_pts"]} | source: {html.escape(source_path)}</p>'
            +f'<a href="{f["original_image"]}">Unmodified original</a> | <a href="{f["roi_image"]}">ROI</a>'
            +f'<br><img src="{f["review_image"]}" width="432">'
            +''.join(f'<p>{html.escape(o["object_id"])}: {html.escape(o["visual_class"])} / {o["review_state"]} / {o["bbox_xywh_pixels"]} / {html.escape(o["appearance_group_id"])}</p><img src="{o["context_crop"]}">' for o in objects if o['frame_id']==f['frame_id'])+'</section>')
    (bundle/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Attempt02 TRAIN Human Review</title><style>body{font:16px sans-serif;background:#161b23;color:white;margin:24px}a{color:#72d9ff}section{border-top:1px solid #666;margin:32px 0;padding-top:16px}</style><h1>Pending TRAIN review, NOT final GT</h1><p>See HUMAN_REVIEW.md and human-return-template.json. No training has occurred.</p>'+''.join(rows),encoding='utf-8')
    manifest = {'kind':'attempt02_train_human_review_bundle', 'state':'WAITING_HUMAN_REVIEW',
        'preparation_head':subprocess_head(root), 'class_schema':CLASS_SCHEMA, 'frames':16,
        'positive_candidate_frames':8,'negative_candidate_frames':8,'prior_confirmed_frames':2,'pending_frame_coverage':14,
        'prior_confirmed_boxes':sum(o['review_state']=='confirmed' for o in objects),
        'draft_boxes':sum(o['review_state']!='confirmed' for o in objects),'contact_sheets':2,
        'underlying_matches':['natural_match_01'],'dev_images_included':0,'model_used':False,'real_training_started':False,
        'attempt01_bytes_preserved':True,'parent_gt_sha256':GT_SHA,'parent_dataset_sha256':DATASET_SHA,
        'provenance':{'source_type':'user_recorded_gameplay','intended_use':'private_local_research_poc',
            'external_upload':False,'redistribution':False,'rights_clearance':'unverified',
            'expanded_GT_human_confirmation_pending':True},
        'files':{p.relative_to(bundle).as_posix():file_sha(p) for p in sorted(bundle.rglob('*')) if p.is_file()}}
    write_json(bundle/'manifest.json',manifest)
    archive = private_path(root, preparation/'Module_2B2B_Attempt02_TRAIN_Human_Review.zip')
    with archive.open('xb') as raw:
        with ZipFile(raw,'w',compression=ZIP_DEFLATED) as z:
            for path in sorted(bundle.rglob('*')):
                if path.is_file(): z.write(path,path.relative_to(bundle).as_posix())
    with ZipFile(archive) as z:
        require(z.testzip() is None,'ZIP corrupt')
        require(set(z.namelist())==set(manifest['files'])|{'manifest.json'},'ZIP file membership differs')
        for rel,digest in manifest['files'].items():
            from hashlib import sha256
            require(sha256(z.read(rel)).hexdigest()==digest,'ZIP/source hash differs')
    write_json(preparation/'review-packaging-receipt.json', {'zip_path':archive.relative_to(root).as_posix(),
        'zip_sha256':file_sha(archive),'zip_bytes':archive.stat().st_size,'zip_members':len(manifest['files'])+1,
        'all_member_hashes_match':True,'review_status':'pending_human_review','training_started':False,'counts':{
        k:manifest[k] for k in ('frames','draft_boxes','prior_confirmed_boxes','contact_sheets','pending_frame_coverage')}})
    print(f"Human review bundle: {archive}; 16 frames, {manifest['draft_boxes']} draft boxes, 6 old confirmed; not training-ready.")


def subprocess_head(root):
    import subprocess
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--preparation',type=Path,required=True)
    parser.add_argument('--drafts',type=Path,required=True)
    parser.add_argument('--profile',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve()
    build(root,args.preparation,args.drafts,load_profile(root,args.profile))
