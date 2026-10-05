"""Disk/integration guardrails; synthetic video, never private match imagery."""
import importlib
from copy import deepcopy
from fractions import Fraction
import json

import av
import numpy as np
from PIL import Image
import pytest

from clash_tracker_video.evidence_contract import EvidenceError
from clash_tracker_video.experiment_lock import make_development_lock, freeze_model, validate_lock
from experiment_fixtures import development_fixture
from lock_fixtures import model_fixture
from test_experiment_cli import disk


def api():
    try:
        return importlib.import_module('clash_tracker_video.baseline_io')
    except ModuleNotFoundError:
        pytest.fail('Module 2B-1 disk adapter is not implemented')


def clip(path):
    # Achromatic synthetic pattern survives YUV420 chroma subsampling; this
    # tests detection, not an incorrect assumption of lossless RGB video.
    gray = np.random.default_rng(8).integers(0,255,(12,12,1),dtype=np.uint8)
    pattern = np.repeat(gray,3,axis=2)
    with av.open(str(path),'w') as c:
        s = c.add_stream('libx264',rate=10)
        s.width,s.height,s.pix_fmt = 64,64,'yuv420p'
        s.time_base = s.codec_context.time_base = Fraction(1,1000)
        s.options = {'bf':'0','crf':'0'}
        for i in range(31):
            rgb = np.zeros((64,64,3),np.uint8)
            if 10 <= i < 14: rgb[30:42,25:37] = pattern
            f = av.VideoFrame.from_image(Image.fromarray(rgb)); f.pts = i*100; f.time_base=Fraction(1,1000)
            for p in s.encode(f): c.mux(p)
        for p in s.encode(): c.mux(p)
    return pattern


def test_actual_coarse_fine_scan_pts_and_no_hidden_input(tmp_path):
    b = api()
    from clash_tracker_video.baseline import Config,Template
    source = tmp_path/'synthetic.mp4'; p=clip(source)
    config = Config(roi=(0.,0.,1.,1.),scales=(1.,),working_scale=1.,proposal_floor=.5)
    result = b.scan_video(source,[Template('a','A','f',p)],config)
    assert result['coarse_frames'] == 13
    assert result['fine_frames'] > 13
    assert any(1 <= o['timestamp_seconds'] <= 1.3 and o['score'] > .8 for o in result['observations'])
    assert all(Fraction(o['raw_pts'])*Fraction(o['time_base']) == Fraction(str(o['timestamp_seconds']))
               for o in result['observations'])


def test_scan_candidates_repeat_without_ground_truth(tmp_path):
    b=api()
    from clash_tracker_video.baseline import Config,Template
    source=tmp_path/'synthetic.mp4'; p=clip(source)
    cfg=Config(roi=(0.,0.,1.,1.),scales=(1.,),working_scale=1.)
    a=b.scan_video(source,[Template('a','A','f',p)],cfg)
    assert a == b.scan_video(source,[Template('a','A','f',p)],cfg)


def test_exclusive_rank_freeze_then_hidden_loader(tmp_path):
    b=api()
    from clash_tracker_video.baseline import merge_events,rank_events
    from test_baseline import observation
    ranked=rank_events(merge_events([observation(10)]))
    path=tmp_path/'rank.json'
    def hidden():
        assert path.exists()
        assert json.loads(path.read_text())['ranking'] == ranked
        return dict(play_id='B',deployment_time_seconds=10)
    assert b.freeze_then_evaluate(path,ranked,hidden)['pass']
    with pytest.raises(FileExistsError): b.freeze_then_evaluate(path,ranked,hidden)


def test_fail_result_cannot_build_artifact():
    with pytest.raises(EvidenceError):
        api().require_crossval({'folds':[{'pass':True},{'pass':False}]})


def test_artifact_tamper_and_reference_template_tamper_rejected():
    b=api()
    from clash_tracker_video.baseline import Config,Template,make_artifact,artifact_sha
    p=np.random.default_rng(7).integers(0,255,(12,12,3),dtype=np.uint8)
    t=Template('a','A','f',p)
    artifact=make_artifact('a'*64,dict(card_id='minions',form='normal'),[t],Config(),.7,'b'*40)
    b.verify_artifact(artifact,artifact_sha(artifact),[t])
    changed=deepcopy(artifact); changed['threshold']=.6
    with pytest.raises(EvidenceError): b.verify_artifact(changed,artifact_sha(artifact),[t])
    p[0,0]=0
    with pytest.raises(EvidenceError): b.verify_artifact(artifact,artifact_sha(artifact),[t])


def test_legacy_model_contract_still_accepted(tmp_path,monkeypatch):
    api()
    from clash_tracker_video import experiment_lock
    monkeypatch.setattr(experiment_lock,'PROJECT_ROOT',tmp_path)
    draft,indexes=development_fixture(); dev=make_development_lock(draft,indexes)
    assert freeze_model(model_fixture(dev),dev,tmp_path/'outputs/locks')['lock_type']=='model'


def reference_contract():
    draft,indexes=development_fixture(); dev=make_development_lock(draft,indexes)
    contract=model_fixture(dev)
    contract['artifact_type']='reference_template_matcher'
    contract['sampling']['fps']=4.
    contract['input']=dict(width=32,height=24,crop=dict(x=0.,y=.12,width=1.,height=.73),
        resize='stretch',interpolation='bilinear',preprocess=dict(color_order='RGB',
        dtype='uint8',scale=1.,mean=[0,0,0],std=[1,1,1]))
    contract['nms']=dict(enabled=False,iou_threshold=0)
    contract['postprocess']=dict(version='transitive_adjacent_support_gap',
        class_agnostic_nms=False,max_detections=5)
    contract['baseline']={'artifact_sha256':contract['model_sha256'],'config':api().default_config_document(),
        'templates':[{'template_id':'t','play_id':'play0','frame_id':'frame0_0','width':20,'height':20,'crop_rgb_sha256':'c'*64}],
        'score_method':'RGB_TM_CCOEFF_NORMED','event_merge':'transitive_adjacent_support_gap',
        'threshold_derivation':'min_two_held_out_true_event_peak_scores','opencv_version':'4.13.0',
        'evaluation_protocol_version':1}
    return dev,contract


def test_reference_model_extension_is_closed_bound_and_backward_compatible(tmp_path,monkeypatch):
    b=api()
    from clash_tracker_video import experiment_lock
    monkeypatch.setattr(experiment_lock,'PROJECT_ROOT',tmp_path)
    dev,contract=reference_contract()
    model=freeze_model(contract,dev,tmp_path/'outputs/locks')
    assert validate_lock(model,dev)['payload']['artifact_type']=='reference_template_matcher'


@pytest.mark.parametrize('change',[('artifact_sha256','f'*64),('score_method','anything'),
                                 ('event_merge','bins'),('evaluation_protocol_version',2)])
def test_reference_contract_inconsistent_extension_rejected(tmp_path,monkeypatch,change):
    api()
    from clash_tracker_video import experiment_lock
    monkeypatch.setattr(experiment_lock,'PROJECT_ROOT',tmp_path)
    dev,contract=reference_contract(); contract['baseline'][change[0]]=change[1]
    with pytest.raises(EvidenceError): freeze_model(contract,dev,tmp_path/'outputs/locks')


@pytest.mark.parametrize('args',[['crossval'],['crossval','private-invalid-file'],['validate-lock','private-invalid-file']])
def test_cli_bad_input_exit_two_without_path_disclosure(args,capsys):
    b=api()
    assert b.cli_main(args)==2
    assert 'private-invalid-file' not in capsys.readouterr().err


def test_disk_context_checks_source_and_frozen_snapshot(disk):
    b=api()
    from clash_tracker_video.evidence_prepare import load_indexes
    from clash_tracker_video.experiment_lock import freeze_development,lock_filename
    root,draft,_,index=disk
    dev=freeze_development(draft,load_indexes([index]),root/'locks')
    lock=root/'locks'/lock_filename(dev)
    ctx=b.development_context(lock,[index],root/'synthetic.mp4')
    assert len(ctx['templates']) == 2
    assert sorted(len(g) for g in ctx['templates'].values()) == [3,3]
    wrong=root/'wrong.mp4'; wrong.write_bytes(b'not the frozen video')
    with pytest.raises(EvidenceError): b.development_context(lock,[index],wrong)
    before=lock.read_bytes()
    with pytest.raises(EvidenceError): b.development_context(lock,[],root/'synthetic.mp4')
    assert lock.read_bytes()==before


def test_model_artifact_metadata_cannot_disagree_with_model_lock():
    b=api()
    from clash_tracker_video.baseline import Config,Template,make_artifact
    artifact=make_artifact('a'*64,{'card_id':'minions','form':'normal'},
        [Template('a','A','f',np.ones((12,12,3),np.uint8))],Config(),.7,'b'*40)
    model={'payload':{'baseline':{'config':Config().document()},'confidence_threshold':.6}}
    with pytest.raises(EvidenceError):
        b.verify_model_semantics(artifact,model)


def test_build_gate_refuses_fail_before_creating_output(disk,monkeypatch):
    b=api()
    from clash_tracker_video.evidence_prepare import write_json
    root,*_=disk
    # This constructor performs the PASS gate before accessing context or creating output.
    report=root/'fail.json'; write_json(report,{'folds':[{'pass':False},{'pass':False}]})
    def no_git(): pytest.fail('FAIL reached model-building code')
    monkeypatch.setattr(b,'_git_commit',no_git)
    with pytest.raises(EvidenceError): b.build_baseline({},report,root/'output')
    assert not (root/'output').exists()


@pytest.mark.parametrize('path,value',[
    (('input','width'),123),(('input','height'),123),
    (('input','resize'),'letterbox'),(('input','interpolation'),'nearest'),
    (('input','preprocess','color_order'),'BGR'),(('input','preprocess','dtype'),'float32'),
    (('input','preprocess','scale'),1/255),(('input','preprocess','mean'),[1,0,0]),
    (('input','preprocess','std'),[2,1,1]),(('nms','enabled'),True),
    (('nms','iou_threshold'),.5),(('postprocess','version'),'other'),
    (('postprocess','class_agnostic_nms'),True),(('postprocess','max_detections'),99)])
def test_reference_model_cannot_claim_different_runtime_parameters(tmp_path,monkeypatch,path,value):
    from clash_tracker_video import experiment_lock
    monkeypatch.setattr(experiment_lock,'PROJECT_ROOT',tmp_path)
    dev,contract=reference_contract()
    node=contract
    for key in path[:-1]: node=node[key]
    node[path[-1]]=value
    with pytest.raises(EvidenceError): freeze_model(contract,dev,tmp_path/'outputs/locks')


def test_code_freeze_guard_independent_of_current_directory(tmp_path,monkeypatch):
    import subprocess
    b=api()
    root=tmp_path/'repo'; nested=root/'tools/offline_video'; nested.mkdir(parents=True)
    def git(*args):
        return subprocess.check_output(['git','-c','user.name=Synthetic Test',
            '-c','user.email=synthetic@example.invalid',*args],cwd=root,text=True).strip()
    git('init','--quiet')
    source=nested/'synthetic.py'; source.write_text('before\n')
    git('add','.'); git('commit','--quiet','-m','synthetic fixture')
    monkeypatch.setattr(b,'PROJECT_ROOT',root,raising=False)
    monkeypatch.chdir(nested)
    assert b._git_commit()==git('rev-parse','HEAD')
    source.write_text('after\n')
    with pytest.raises(EvidenceError): b._git_commit()


def test_build_configuration_bound_to_prefrozen_protocol(disk):
    b=api()
    from clash_tracker_video.evidence_prepare import write_json,file_hash
    root,*_=disk
    context={'development':{'sha256':'a'*64},'target':{'card_id':'synthetic_card','form':'normal'}}
    protocol=dict(config=b.default_config_document(),git_commit='b'*40,
        development_lock_sha256='a'*64,target=context['target'])
    path=root/'protocol.json'; write_json(path,protocol)
    report={**protocol,'protocol_sha256':file_hash(path)}
    b.require_protocol(report,root/'crossval.json',context)
    changed=deepcopy(report); changed['config']['fps']=8.
    with pytest.raises(EvidenceError): b.require_protocol(changed,root/'crossval.json',context)
    changed=deepcopy(report); changed['protocol_sha256']='c'*64
    with pytest.raises(EvidenceError): b.require_protocol(changed,root/'crossval.json',context)
    # Updating both metadata documents is not permission to change fixed settings.
    protocol['config']['fps']=8.
    path.write_text(json.dumps(protocol))
    changed={**protocol,'protocol_sha256':file_hash(path)}
    with pytest.raises(EvidenceError): b.require_protocol(changed,root/'crossval.json',context)


def test_git_failure_is_path_free_evidence_error(monkeypatch,capsys):
    import subprocess
    b=api()
    def broken(*args,**kwargs):
        raise subprocess.CalledProcessError(128,args[0],stderr='private-local-path')
    monkeypatch.setattr(b.subprocess,'check_output',broken)
    with pytest.raises(EvidenceError,match='Cannot verify committed baseline code'):
        b._git_commit()
    assert 'private-local-path' not in capsys.readouterr().err


@pytest.mark.parametrize('field,value',[('artifact_version',2),('artifact_type','other'),
    ('preprocessing','BGR_float32'),('orb',{'ranking_weight':1}),('numpy_version','other')])
def test_artifact_recomputed_hash_cannot_hide_runtime_semantic_change(field,value):
    b=api()
    from clash_tracker_video.baseline import Config,Template,make_artifact,artifact_sha
    templates=[Template('a','A','f',np.ones((12,12,3),np.uint8))]
    artifact=make_artifact('a'*64,{'card_id':'synthetic_card','form':'normal'},templates,Config(),.7,'b'*40)
    artifact[field]=value
    with pytest.raises(EvidenceError): b.verify_artifact(artifact,artifact_sha(artifact),templates)
