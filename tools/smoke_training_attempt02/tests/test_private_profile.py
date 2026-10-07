"""Anonymous artifact preparation profiles: media identities stay ignored."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def profile(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    (tmp_path/'.gitignore').write_text('/outputs/\n/local_data/\n',encoding='utf-8')
    (tmp_path/'outputs').mkdir(); (tmp_path/'local_data').mkdir()
    p = {'old_run':'outputs/old-run','dataset_lock':'outputs/lock.json',
         'source_recording':'local_data/synthetic.mp4','source_sha256':'a'*64,
         'index_paths':['outputs/synthetic-index.json'], 'recording_id':'development_01',
         'underlying_match_id':'natural_match_01'}
    path=tmp_path/'outputs/private-profile.json'
    path.write_text(json.dumps(p),encoding='utf-8')
    return tmp_path,path,p


def call(root,path):
    module=importlib.import_module('prepare_review')
    assert hasattr(module,'load_profile'), 'Ignored runtime source-profile loader missing'
    return module.load_profile(root,path)


def test_source_identity_only_loaded_from_ignored_runtime_profile(profile):
    root,path,p=profile
    assert call(root,path)==p


@pytest.mark.parametrize('key,value', [
    ('source_recording','../private.mp4'), ('source_recording','public.mp4'),
    ('source_sha256','not-a-sha'), ('index_paths',[]), ('index_paths',['public/index.json']),
    ('underlying_match_id','natural_match_04'), ('recording_id','other_recording')])
def test_profile_rejects_unsafe_or_other_match_sources(profile,key,value):
    root,path,p=profile;p[key]=value;path.write_text(json.dumps(p),encoding='utf-8')
    with pytest.raises(ValueError): call(root,path)


def test_preparation_code_does_not_embed_private_media_bindings():
    for name in ('prepare_review.py','build_review_bundle.py'):
        source=(Path(__file__).resolve().parents[1]/name).read_text(encoding='utf-8')
        assert 'local_data/recordings/' not in source
        assert 'outputs/module2a2/' not in source
        assert 'SOURCE_SHA =' not in source


@pytest.mark.parametrize('identity', ['../../escape', '../escape', '/escape', 'a/b',
    'a\\b', 'a:b', '', '.', 'NUL', 'CON', 'COM1', 'x'*100])
def test_crop_identity_cannot_escape_bundle_or_use_device_name(identity):
    module=importlib.import_module('build_review_bundle')
    assert hasattr(module,'validate_object_id'), 'Safe crop identity validator missing'
    with pytest.raises(ValueError): module.validate_object_id(identity)


def test_safe_crop_identity_retained():
    module=importlib.import_module('build_review_bundle')
    assert hasattr(module,'validate_object_id'), 'Safe crop identity validator missing'
    assert module.validate_object_id('synthetic_object_01')=='synthetic_object_01'


@pytest.fixture
def export_fixture():
    frames={'synthetic_a':{'frame_id':'synthetic_a'},'synthetic_b':{'frame_id':'synthetic_b'}}
    objects={'synthetic_object_a':{'object_id':'synthetic_object_a','frame_id':'synthetic_a',
        'visual_class':'unit.skeleton','bbox_xywh_pixels':[10,20,6,12]},
        'synthetic_object_b':{'object_id':'synthetic_object_b','frame_id':'synthetic_b',
        'visual_class':'unit.witch','bbox_xywh_pixels':[30,40,12,20]}}
    data={'images':[{'id':1,'frame_id':'synthetic_a'},{'id':2,'frame_id':'synthetic_b'}],
          'categories':[{'id':0,'name':'unit.skeleton'},{'id':1,'name':'unit.witch'}],
          'annotations':[{'object_id':'synthetic_object_a','image_id':1,'category_id':0,'bbox':[10,20,6,12]},
                         {'object_id':'synthetic_object_b','image_id':2,'category_id':1,'bbox':[30,40,12,20]}]}
    return frames,objects,data


def check_export(fixture):
    module=importlib.import_module('prepare_review')
    assert hasattr(module,'validate_train_export'), 'Complete per-frame export validator missing'
    frames,objects,data=fixture
    return module.validate_train_export(data,frames,objects)


def test_valid_train_export_ids_and_frame_mapping_pass(export_fixture):
    assert check_export(export_fixture) is None


@pytest.mark.parametrize('defect',['duplicate_object','wrong_image','duplicate_image_id',
    'duplicate_frame_id','duplicate_category','class_swap'])
def test_duplicate_or_wrong_frame_export_labels_rejected(export_fixture,defect):
    from copy import deepcopy
    frames,objects,data=export_fixture
    if defect=='duplicate_object': data['annotations'][1]=deepcopy(data['annotations'][0])
    if defect=='wrong_image': data['annotations'][0]['image_id']=2
    if defect=='duplicate_image_id': data['images'][1]['id']=1
    if defect=='duplicate_frame_id': data['images'][1]['frame_id']='synthetic_a'
    if defect=='duplicate_category': data['categories'].append(deepcopy(data['categories'][0]))
    if defect=='class_swap': data['annotations'][0]['category_id']=1
    with pytest.raises(ValueError): check_export((frames,objects,data))
