from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

import pytest
from PIL import Image
from conftest import make_video
from clash_tracker_video import evidence_prepare as ep
from clash_tracker_video.evidence_contract import EvidenceError


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(ep, 'PROJECT_ROOT', tmp_path)
    return tmp_path


@pytest.mark.parametrize('last,want', [(F(10),[F(0),F(5),F(10)]),
    (F('10.1'),[F(0),F(5),F(10),F('10.1')]),
    (F('10.000000000001'),[F(0),F(5),F(10),F('10.000000000001')])])
def test_exact_default_dedup(last, want):
    assert ep.default_times(last) == want


def test_vfr_rotated_and_contacts(root):
    video = make_video(root / 'input.mp4', (5000,5070,5210,5500), rotation=90)
    before = hashlib.sha256(video.read_bytes()).hexdigest()
    run = root / 'outputs' / 'one'
    index = ep.prepare_evidence(video, run, recording_id='vfr', times=[0,.06,.2,.5])
    assert [f['timestamp_seconds'] for f in index['frames']] == [0,.07,.21,.5]
    assert index['recording']['origin_pts'] != 0
    assert index['recording']['orientation'] == 'portrait'
    assert (index['frames'][0]['image_width'],index['frames'][0]['image_height']) == (48,64)
    with Image.open(run / index['contact_pages'][0]) as page:
        assert page.size == (672, 1008)
    assert hashlib.sha256(video.read_bytes()).hexdigest() == before
    assert json.loads((run / 'index.json').read_text()) == index
    assert index['schema_version'] == 1


def test_default_last_and_partial(root):
    video = make_video(root / 'in.mp4')
    a = ep.prepare_evidence(video, root/'outputs/a', recording_id='sample')
    assert [f['timestamp_seconds'] for f in a['frames']] == [0,.3]
    b = ep.prepare_evidence(video, root/'outputs/b', recording_id='sample', times=[0,10])
    assert b['status'] == 'partial'
    assert b['frames'][1]['status'] == 'miss'
    assert b['frames'][1]['image_path'] is None


def test_stable_frame_merge_and_content_conflict(root):
    video = make_video(root/'in.mp4')
    a = root/'outputs/a'
    b = root/'outputs/b'
    ep.prepare_evidence(video,a,recording_id='sample',times=[0,.1])
    ep.prepare_evidence(video,b,recording_id='sample',times=[.1])
    merged = ep.load_indexes([a/'index.json',b/'index.json'])
    assert len(merged['sample']['frames']) == 2
    assert ep.frame_id('sample',100,F(1,1000)) == ep.frame_id('sample',1000,F(1,10000))
    with (b/'exports/frame_0000.png').open('wb') as handle:
        Image.new('RGB',(64,48),'black').save(handle,format='PNG')
    with pytest.raises(EvidenceError,match='conflict'):
        ep.load_indexes([a/'index.json',b/'index.json'])


def test_index_dimension_and_recording_conflict(root):
    video = make_video(root/'in.mp4')
    run = root/'outputs/run'
    ep.prepare_evidence(video,run,recording_id='sample')
    path = run/'index.json'
    index = json.loads(path.read_text())
    index['frames'][0]['image_width'] = 63
    path.write_text(json.dumps(index))
    with pytest.raises(EvidenceError): ep.load_indexes([path])


@pytest.mark.parametrize('destination', ['outside/run','outputs/../escape','//server/share/run','https://example.com/run'])
def test_unsafe_output(root,destination):
    video = make_video(root/'in.mp4')
    target = destination if '://' in destination or destination.startswith('//') else root/destination
    with pytest.raises(EvidenceError): ep.prepare_evidence(video,target,recording_id='sample')


def test_existing_output_even_empty_and_sentinel(root):
    video = make_video(root/'in.mp4')
    run = root/'outputs/run'
    run.mkdir(parents=True)
    with pytest.raises(EvidenceError): ep.prepare_evidence(video,run,recording_id='sample')
    sentinel = run/'keep.txt'
    sentinel.write_text('keep')
    with pytest.raises(EvidenceError): ep.prepare_evidence(video,run,recording_id='sample')
    assert sentinel.read_text() == 'keep'


def test_symlink_ancestor_escape(root):
    outside = root/'outside'
    outside.mkdir()
    (root/'outputs').mkdir()
    link = root/'outputs/link'
    try: link.symlink_to(outside, target_is_directory=True)
    except OSError: pytest.skip('OS denies symlink creation')
    video = make_video(root/'in.mp4')
    with pytest.raises(EvidenceError): ep.prepare_evidence(video,link/'run',recording_id='sample')
    assert not (outside/'run').exists()


def test_write_failure_safe(root,monkeypatch):
    video = make_video(root/'in.mp4')
    original = Path.open
    def denied(path,*args,**kwargs):
        if path.suffix == '.png': raise PermissionError('private-path-must-not-leak')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',denied)
    with pytest.raises(EvidenceError) as error: ep.prepare_evidence(video,root/'outputs/run',recording_id='sample')
    assert 'private-path-must-not-leak' not in str(error.value)


def test_contacts_paginated(root):
    video = make_video(root/'long.mp4', tuple(range(0,1300,100)))
    index = ep.prepare_evidence(video,root/'outputs/run',recording_id='sample',times=[i/10 for i in range(13)])
    assert len(index['contact_pages']) == 2
    with Image.open(root/'outputs/run'/index['contact_pages'][0]) as page:
        assert page.size == (672,2016)
