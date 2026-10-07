"""Synthetic supervision/freeze regression tests; no private gameplay inputs."""
from copy import deepcopy
import importlib
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'smoke_training'))
from smoke_data import canonical
from PIL import Image


def api():
    # A missing implementation is a named feature failure, not collection error.
    try:
        return importlib.import_module('expanded_data')
    except ModuleNotFoundError:
        pytest.fail('Attempt02 expanded supervision and immutable snapshot API not implemented')


def synthetic_review():
    times = [5, 10, 15, 75, 90, 95, 100, 105, 158, 160, 161, 162, 163, 164, 165, 166]
    frames = [{'frame_id': f'f_{t}', 'timestamp_seconds': t, 'underlying_match_id': 'natural_match_01',
               'split': 'TRAIN', 'image_size': [432, 960], 'image_sha256': 'a'*64,
               'source_image_relative_to_repo': f'outputs/source/{t}.png', 'source_index': 'outputs/source/index.json',
               'raw_pts': t*90000, 'time_base': {'numerator': 1, 'denominator': 90000},
               'source_sha256': 'b'*64, 'source_recording': 'local_data/example.mp4',
               'recording_id': 'development_01', 'positive_object_ids': [],
               'review_state': 'confirmed' if t in (163,164) else 'pending_human_review'} for t in times]
    witch='draft_m01_witch_episode_01'; left='a02_m01_skeleton_left_continuity_pending'
    wave='a02_m01_skeleton_spawn_wave_02_pending'; old='draft_m01_skeleton_episode_01'
    placements=[(1,158,'unit.witch',witch),(2,160,'unit.witch',witch),(3,160,'unit.skeleton',left),
                (4,161,'unit.witch',witch),(5,161,'unit.skeleton',left),(6,162,'unit.witch',witch),
                (7,162,'unit.skeleton',left),(8,165,'unit.witch',witch),(9,165,'unit.skeleton',wave),
                (10,165,'unit.skeleton',wave),(11,165,'unit.skeleton',wave),(12,166,'unit.witch',witch),
                (13,166,'unit.skeleton',wave),(14,166,'unit.skeleton',wave),(15,166,'unit.skeleton',wave)]
    objects=[]
    for number,t,name,group in placements:
        objects.append({'object_id':f'a02_draft_{number:02}', 'frame_id':f'f_{t}',
                        'underlying_match_id':'natural_match_01', 'visual_class':name,
                        'class_id': 0 if name=='unit.skeleton' else 1, 'bbox_xywh_pixels':[100+number,250,20,30],
                        'appearance_group_id':group, 'owner':'opponent','form':'unknown',
                        'origin_kind':'spawned' if group==wave else 'unknown',
                        'source_relationship':f'spawned_from:{witch}' if group==wave else None,
                        'review_state':'pending_human_review','is_skeleton_card_deployment':False})
    prior=[]
    for number in range(1,7):
        name='unit.witch' if number in (1,6) else 'unit.skeleton'; t=164 if number==6 else 163
        prior.append({'object_id':f'draft_object_{number:02}','frame_id':f'f_{t}',
                      'underlying_match_id':'natural_match_01','visual_class':name,
                      'bbox_xywh_pixels':[200+number,280,20,30], 'appearance_group_id':witch if name=='unit.witch' else old,
                      'owner':'opponent','form':'unknown', 'origin_kind':'unknown' if name=='unit.witch' else 'spawned',
                      'source_relationship':None if name=='unit.witch' else f'spawned_from:{witch}',
                      'review_state':'confirmed'})
    objects+=deepcopy(prior)
    for f in frames: f['positive_object_ids']=[o['object_id'] for o in objects if o['frame_id']==f['frame_id']]
    groups=[{'appearance_group_id':g,'underlying_match_id':'natural_match_01','visual_class':name,
             'origin_kind':origin,'source_relationship':source,'independent_deployment_confirmed':False}
            for g,name,origin,source in [(witch,'unit.witch','unknown',None),(left,'unit.skeleton','unknown',None),
                                       (wave,'unit.skeleton','spawned',f'spawned_from:{witch}'),
                                       (old,'unit.skeleton','spawned',f'spawned_from:{witch}')]]
    parent_groups=deepcopy([g for g in groups if g['appearance_group_id'] in (old,witch)])
    for g in parent_groups:
        g.update(review_state='accepted',decision='accept',continuity_confirmed=True,
                 source_relationship_confirmed=True if g['origin_kind']=='spawned' else None,
                 independent_deployment_confirmed=g['visual_class']=='unit.witch')
    devframes=[]; devobjects=[]
    for t in (68,72):
        f=deepcopy(frames[12]); f.update(frame_id=f'dev_{t}',timestamp_seconds=t,
                underlying_match_id='natural_match_04',split='DEV_VAL',source_image_relative_to_repo=f'outputs/dev/{t}.png',
                complete_frame_supervision_coverage=t==68,positive_object_ids=[])
        devframes.append(f)
    for number in range(7,12):
        name='unit.witch' if number in (7,11) else 'unit.skeleton'; t=72 if number==11 else 68
        o=deepcopy(prior[0]); o.update(object_id=f'draft_object_{number:02}',frame_id=f'dev_{t}',
                underlying_match_id='natural_match_04',visual_class=name)
        devobjects.append(o)
    for f in devframes: f['positive_object_ids']=[o['object_id'] for o in devobjects if o['frame_id']==f['frame_id']]
    parent={'gt_snapshot':{'frames':[deepcopy(f) for f in frames if f['timestamp_seconds'] in (163,164)]+devframes,
            'positive_objects':prior+devobjects,'groups':parent_groups},
            'provenance':{'source_type':'user_recorded_gameplay','intended_use':'private_local_research_poc',
                          'external_upload':False,'redistribution':False,'rights_clearance':'unverified',
                          'user_training_authorized':True}}
    decisions=[]
    for o in objects[:15]:
        rejected=o['object_id'] in {'a02_draft_07','a02_draft_09','a02_draft_10','a02_draft_11'}
        decisions.append({'object_id':o['object_id'],'decision':'reject' if rejected else 'confirm',
                          'uncertain_reason':'ambiguous' if rejected else None,'corrected_visual_class':None,
                          'corrected_bbox_xywh_pixels':None, 'owner':'opponent','form':'unknown',
                          'origin_kind':o['origin_kind'],'source_relationship':o['source_relationship'],
                          'appearance_group_id':o['appearance_group_id']})
    coverages=[]
    for f in frames:
        t=f['timestamp_seconds']
        if t in (163,164): continue
        complete=t not in (162,165)
        coverages.append({'frame_id':f['frame_id'],'exhaustive_for_selected_classes':complete,
                          'negative_confirmed':t<158,'remaining_unknown_regions':'none_material' if complete else 'ambiguous_small_unit',
                          'additional_objects':[]})
    group_decisions=[{'appearance_group_id':g['appearance_group_id'], 'decision':'accept',
                     'continuity_confirmed':True,'source_relationship_confirmed':g['origin_kind']=='spawned' or None,
                     'independent_deployment_confirmed':None if g['visual_class']=='unit.witch' else False} for g in groups]
    human={'status':'ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED','confirmation_source':'user_relayed_chatgpt',
           'reviewer':'ChatGPT, relayed by user','review_packet_sha256':'c'*64,
           'user_authorization_scope':'private_local_research_poc','objects':decisions,
           'group_decisions':group_decisions,'frame_coverage_confirmations':coverages}
    review={'frames':frames,'source_bindings':[],'class_schema':{'unit.skeleton':0,'unit.witch':1}}
    draft={'objects':objects,'groups':groups}
    bindings={'parent_dataset_sha256':'d'*64,'parent_gt_sha256':'e'*64,'review_packet_sha256':'c'*64,
              'human_return_sha256':'f'*64,'references':{}}
    return review,draft,human,parent,bindings


def assembled():
    return api().assemble_snapshot(*synthetic_review())


def test_accepted_objects_preserved_but_partial_frames_never_enter_loss():
    p=assembled()
    assert len(p['train_frames'])==16
    assert len(p['accepted_objects'])==17
    assert len(p['rejected_objects'])==4
    assert len(p['standard_train_frame_ids'])==14
    assert p['partial_frame_ids']==['f_162','f_165']
    assert p['counts']['TRAIN']=={'images':14,'negative_images':8,'positive_images':6,'unit.skeleton':9,'unit.witch':6}


def test_old_annotations_and_appearance_identity_are_not_rewritten():
    review,draft,human,parent,bindings=synthetic_review(); p=api().assemble_snapshot(review,draft,human,parent,bindings)
    old={o['object_id']:o for o in parent['gt_snapshot']['positive_objects'] if o['underlying_match_id']=='natural_match_01'}
    for o in p['accepted_objects']:
        if o['object_id'] in old:
            assert all(o[k]==v for k,v in old[o['object_id']].items())
    witch=next(g for g in p['groups'] if g['visual_class']=='unit.witch')
    assert witch['independent_deployment_confirmed'] is True
    assert p['confirmed_train_witch_deployments']==1
    assert p['skeleton_card_deployments']==0


@pytest.mark.parametrize('mutation', ['class_swap','duplicate_frame','duplicate_object','missing_decision','negative_unconfirmed',
                                      'partial_claimed_complete','rejected_claimed_negative','match_leak','training_scope_absent',
                                      'negative_partial','bbox_changed','extra_deployment'])
def test_invalid_review_cannot_qualify_standard_supervision(mutation):
    review,draft,human,parent,bindings=synthetic_review()
    if mutation=='class_swap':review['class_schema']={'unit.skeleton':1,'unit.witch':0}
    if mutation=='duplicate_frame':review['frames'].append(deepcopy(review['frames'][0]))
    if mutation=='duplicate_object':draft['objects'].append(deepcopy(draft['objects'][0]))
    if mutation=='missing_decision':human['objects'].pop()
    if mutation=='negative_unconfirmed':human['frame_coverage_confirmations'][0]['negative_confirmed']=None
    if mutation=='partial_claimed_complete':human['frame_coverage_confirmations'][-2]['exhaustive_for_selected_classes']=True
    if mutation=='rejected_claimed_negative':human['frame_coverage_confirmations'][-2]['negative_confirmed']=True
    if mutation=='match_leak':review['frames'][0]['underlying_match_id']='natural_match_04'
    if mutation=='training_scope_absent':human['user_authorization_scope']=None
    if mutation=='negative_partial':human['frame_coverage_confirmations'][0]['exhaustive_for_selected_classes']=False
    if mutation=='bbox_changed':human['objects'][0]['corrected_bbox_xywh_pixels']=[1,2,3,4]
    if mutation=='extra_deployment':human['group_decisions'][1]['independent_deployment_confirmed']=True
    with pytest.raises(ValueError): api().assemble_snapshot(review,draft,human,parent,bindings)


def test_snapshot_is_order_independent_and_dev_is_never_training():
    inputs=synthetic_review(); a=api().assemble_snapshot(*inputs)
    inputs[0]['frames'].reverse(); inputs[1]['objects'].reverse(); inputs[2]['objects'].reverse()
    b=api().assemble_snapshot(*inputs)
    assert canonical(a)==canonical(b)
    assert {f['split'] for f in a['dev_tune_snapshot']['frames']}=={'DEV_TUNE'}
    assert a['counts']['DEV_TUNE']=={'images':2,'unit.skeleton':3,'unit.witch':2}


def test_semantic_validator_rejects_class_swap_and_partial_addition():
    p=assembled(); p['class_schema']['unit.skeleton']=1
    with pytest.raises(ValueError):api().validate_snapshot(p)


def test_recomputed_counts_do_not_trust_stale_summary():
    p=assembled(); o=next(o for o in p['accepted_objects'] if o['object_id']=='a02_draft_03')
    o.update(visual_class='unit.witch',class_id=1)
    # Bind new annotation digest too: the count check must independently reject.
    from data_contract import annotation_digest
    f=next(f for f in p['train_frames'] if f['frame_id']==o['frame_id'])
    next(r for r in p['frame_reviews'] if r['frame_id']==f['frame_id'])['annotation_sha256']=annotation_digest(f,[o for o in p['accepted_objects'] if o['frame_id']==f['frame_id']])
    with pytest.raises(ValueError):api().validate_snapshot(p)


@pytest.fixture
def private_fixture(tmp_path,monkeypatch):
    subprocess.run(['git','init','-q'],cwd=tmp_path,check=True,capture_output=True)
    (tmp_path/'.gitignore').write_text('outputs/\nlocal_data/\n',encoding='utf-8')
    p=assembled()
    for f in p['train_frames']+p['dev_tune_snapshot']['frames']:
        path=tmp_path/f['source_image_relative_to_repo'];path.parent.mkdir(parents=True,exist_ok=True)
        Image.new('RGB',(432,960),(f['timestamp_seconds'],50,100)).save(path)
    # Parent has a deliberately authorized pinned SHA in production; replace
    # only reconstruction for synthetic artifact IO, not supervision/geometry.
    monkeypatch.setattr(api(),'build_snapshot',lambda root,**refs:deepcopy(p))
    # The shared private_path gate is exercised in separate path/privacy tests.
    # Resolve its already ignored synthetic roots once, avoiding hundreds of Git
    # subprocesses when the contract under test is pixel/annotation consistency.
    from smoke_data import private_path
    private_path(tmp_path,tmp_path/'outputs/export')
    def synthetic_private_path(root,path):
        path=Path(path);path=path if path.is_absolute() else Path(root)/path
        assert '..' not in path.parts and path.relative_to(root).parts[0] in ('outputs','local_data')
        return path
    monkeypatch.setattr(api(),'private_path',synthetic_private_path)
    return tmp_path,p


def test_freeze_roundtrip_is_deterministic_and_cannot_overwrite(private_fixture):
    root,p=private_fixture; output=root/'outputs/locks/v2.json'
    envelope=api().freeze_snapshot(root,output,p); before=output.read_bytes()
    assert envelope['freeze_version']==2
    assert api().load_expanded(root,output)==p
    second=root/'outputs/locks/second.json';api().freeze_snapshot(root,second,p)
    assert second.read_bytes()==before
    with pytest.raises(FileExistsError):api().freeze_snapshot(root,output,p)
    assert output.read_bytes()==before


@pytest.mark.parametrize('rehash',[False,True])
def test_tampered_lock_is_rejected_even_if_envelope_rehashed(private_fixture,rehash):
    root,p=private_fixture;path=root/'outputs/locks/v2.json'; envelope=api().freeze_snapshot(root,path,p)
    envelope['payload']['accepted_objects'][0]['bbox_xywh_pixels'][0]+=1
    if rehash:
        envelope['snapshot_sha256']=sha256(canonical(envelope['payload'])).hexdigest()
        envelope['digest']=sha256(canonical({k:v for k,v in envelope.items() if k!='digest'})).hexdigest()
    path.write_bytes(canonical(envelope))
    with pytest.raises(ValueError):api().load_expanded(root,path)


def test_export_roi_boxes_negatives_and_partial_isolation(private_fixture):
    root,p=private_fixture; folder=root/'outputs/export'
    manifest=api().export_expanded(root,p,folder,'1'*64)
    train=json.loads((folder/'annotations/train.json').read_text())
    dev=json.loads((folder/'annotations/dev_tune.json').read_text())
    assert len(train['images'])==14 and len(train['annotations'])==15
    assert len(dev['images'])==2 and len(dev['annotations'])==5
    assert {a['category_id'] for a in train['annotations']}=={0,1}
    assert all(i['height']==624 and i['width']==432 for i in train['images']+dev['images'])
    assert {i['timestamp_seconds'] for i in train['images']}=={5,10,15,75,90,95,100,105,158,160,161,163,164,166}
    assert {a['object_id'] for a in train['annotations']}.isdisjoint({'a02_draft_06','a02_draft_07','a02_draft_08','a02_draft_09','a02_draft_10','a02_draft_11'})
    a=next(a for a in train['annotations'] if a['object_id']=='a02_draft_01')
    assert a['bbox']==[101,130,20,30]
    assert a['gt_metadata']['bbox_xywh_pixels']==[101,250,20,30]
    assert all(not i['standard_full_frame_loss_allowed'] for i in dev['images'])
    assert sum(i['negative_confirmed'] for i in train['images'])==8
    assert manifest['counts']['TRAIN']['negative_images']==8
    assert api().validate_export(root,folder)==manifest
    with pytest.raises(ValueError):api().export_expanded(root,p,folder,'1'*64)


@pytest.mark.parametrize('mutation',['class_swap','duplicate_object','wrong_image','bbox_shift','partial_frame','rejected_object','extra_file','image_pixels'])
def test_export_verifier_rejects_semantic_changes_even_with_updated_hashes(private_fixture,mutation):
    root,p=private_fixture;folder=root/'outputs/export';m=api().export_expanded(root,p,folder,'1'*64)
    path=folder/'annotations/train.json';data=json.loads(path.read_text())
    if mutation=='class_swap': data['categories'][0]['id']=1
    if mutation=='duplicate_object': data['annotations'][1]['object_id']=data['annotations'][0]['object_id']
    if mutation=='wrong_image':data['annotations'][0]['image_id']=1
    if mutation=='bbox_shift':data['annotations'][0]['bbox'][1]+=1
    if mutation=='partial_frame':data['images'][0]['frame_id']='f_162'
    if mutation=='rejected_object':data['annotations'][0]['object_id']='a02_draft_07'
    if mutation=='extra_file':(folder/'extra.txt').write_text('not inventoried')
    if mutation=='image_pixels':Image.new('RGB',(432,624),'red').save(folder/data['images'][0]['file_name'])
    path.write_bytes(canonical(data))
    from smoke_data import file_sha
    for relative in m['files']:m['files'][relative]=file_sha(folder/relative)
    m['digest']=sha256(canonical({k:v for k,v in m.items() if k!='digest'})).hexdigest()
    (folder/'manifest.json').write_bytes(canonical(m))
    with pytest.raises(ValueError):api().validate_export(root,folder)


@pytest.mark.parametrize('mutation',[None,'bundle_manifest_changed','member_changed','unlisted_member','duplicate_member'])
def test_packet_manifest_and_all_members_bind_the_actual_reviewed_bundle(tmp_path,mutation):
    from smoke_data import file_sha
    root=tmp_path;bundle=root/'bundle';bundle.mkdir();packet=root/'review.zip'
    member=b'original reviewed object metadata'
    (bundle/'object.json').write_bytes(member)
    manifest={'files':{'object.json':sha256(member).hexdigest()}}
    (bundle/'manifest.json').write_bytes(canonical(manifest))
    with zipfile.ZipFile(packet,'w') as archive:
        archive.writestr('manifest.json',canonical(manifest))
        archive.writestr('object.json',b'tampered' if mutation=='member_changed' else member)
        if mutation=='unlisted_member':archive.writestr('extra.json',b'not in review inventory')
        if mutation=='duplicate_member':
            with pytest.warns(UserWarning):archive.writestr('object.json',member)
    if mutation=='bundle_manifest_changed':
        manifest['new_unreviewed_field']=True
        (bundle/'manifest.json').write_bytes(canonical(manifest))
    if mutation is None:
        api().validate_packet_bundle(bundle,packet,manifest)
    else:
        with pytest.raises(ValueError):api().validate_packet_bundle(bundle,packet,manifest)
    p=assembled(); p['standard_train_frame_ids'].append('f_162')
    with pytest.raises(ValueError):api().validate_snapshot(p)
