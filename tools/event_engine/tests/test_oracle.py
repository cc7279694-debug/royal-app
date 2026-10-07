import importlib

import pytest

from tools.preannotation.contract import bundle_digest


def module():
    try: return importlib.import_module('tools.event_engine.oracle')
    except ImportError: pytest.fail('Human-only Oracle adapter is not implemented')


def fixture():
    bundle={'schema':'synthetic','recording_id':'r1','source_origin_seconds_exact':'1',
            'frames':[{'frame_id':'f1','raw_pts':20,'time_base':'1/10',
                       'source_relative_seconds':1.,'width':100,'height':100},
                      {'frame_id':'f2','raw_pts':30,'time_base':'1/10',
                       'source_relative_seconds':2.,'width':100,'height':100}]}
    supplement={'actual_human_confirmation':True,'human_review_attested':True,'reviewer':'user',
                'review_basis':'chatgpt_visual_review','bundle_sha256':bundle_digest(bundle),
                'confirmation_source':'user_attestation_based_on_chatgpt_visual_review',
                'object_identity_semantics':{}}
    annotations={'bundle_sha256':bundle_digest(bundle),'positive_boxes':[]}
    for i in (1,2):
        annotations['positive_boxes'].append({'object_id':f'p{i}','frame_id':f'f{i}',
            'recording_id':'r1','visual_class':'visual.unit.witch','owner':'opponent',
            'form':'unknown','origin':'unknown','bbox_xyxy':[10,20,30,50],
            'human_confirmed':True,'decision':'accepted','appearance_id':f'unresolved-observation:p{i}',
            'raw_teacher':{'owner_prediction':'own','confidence':.99}})
        supplement['object_identity_semantics'][f'p{i}']={'appearance_id':f'unresolved-observation:p{i}',
                                                       'identity_status':'unresolved','scope':'observation_only_identity_unresolved'}
    return bundle,annotations,supplement


def test_exact_pts_and_human_override_not_teacher():
    stream,meta=module().multiclass_observations(*fixture(),match_id='m1')
    assert [r['timestamp'] for r in stream]==[1.,2.]
    assert all(r['owner']=='opponent' and r['confidence'] is None for r in stream)
    assert all(r['appearance_group_id'] is None for r in stream)
    assert meta['frame_count']==2 and meta['unreviewed_is_negative'] is False


def test_explicit_second_batch_human_group_supported_without_continuity_key():
    b,a,s=fixture()
    s['explicit_user_appearance_groups']=['human-g']
    for r in a['positive_boxes']:
        r['appearance_id']='human-g'
        s['object_identity_semantics'][r['object_id']]={'appearance_id':'human-g','identity_status':'user_group_assignment','scope':'user_confirmed_appearance_group'}
    stream,_=module().multiclass_observations(b,a,s,match_id='m1')
    assert all(r['appearance_group_id']=='human-g' and r['source']=='human_gt_continuity' for r in stream)


def test_single_observation_manual_group_not_strong():
    b,a,s=fixture();a['positive_boxes']=a['positive_boxes'][:1]
    a['positive_boxes'][0]['appearance_id']='g'
    s['object_identity_semantics']['p1']={'appearance_id':'g','identity_status':'user_group_assignment','scope':'user_confirmed_appearance_group','continuity_asserted':False}
    stream,_=module().multiclass_observations(b,a,s,match_id='m1')
    assert stream[0]['appearance_group_id'] is None


@pytest.mark.parametrize('change',['pts','duplicate_frame','duplicate_object','pending','owner','bbox','attestation','binding'])
def test_corrupt_or_unconfirmed_adapter_input_refused(change):
    b,a,s=fixture()
    if change=='pts': b['frames'][0]['source_relative_seconds']=9
    if change=='duplicate_frame': b['frames'].append(b['frames'][0])
    if change=='duplicate_object': a['positive_boxes'].append(a['positive_boxes'][0])
    if change=='pending': a['positive_boxes'][0]['human_confirmed']=False
    if change=='owner': a['positive_boxes'][0]['owner']='enemy'
    if change=='bbox': a['positive_boxes'][0]['bbox_xyxy']=[0,0,999,10]
    if change=='attestation': s['reviewer']='chatgpt'
    if change=='binding': s['bundle_sha256']='wrong'
    with pytest.raises(ValueError): module().multiclass_observations(b,a,s,match_id='m1')


def test_empty_frame_preserved_not_negative():
    b,a,s=fixture();a['positive_boxes']=[]
    stream,meta=module().multiclass_observations(b,a,s,match_id='m1')
    assert stream==[] and meta['frame_count']==2 and len(meta['frames'])==2
    assert all(f['absence_is_negative'] is False for f in meta['frames'])
