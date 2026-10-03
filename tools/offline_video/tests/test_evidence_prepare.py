from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import subprocess
import os

import av
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


def test_alpha_content_conflict(root):
    video = make_video(root/'in.mp4')
    a,b = root/'outputs/a',root/'outputs/b'
    ep.prepare_evidence(video,a,recording_id='sample',times=[0])
    ep.prepare_evidence(video,b,recording_id='sample',times=[0])
    image_path = b/'exports/frame_0000.png'
    with Image.open(image_path) as original:
        changed = original.convert('RGBA')
        changed.putalpha(0)
    changed.save(image_path)
    with pytest.raises(EvidenceError,match='conflict'): ep.load_indexes([a/'index.json',b/'index.json'])


def test_huge_index_pts_returns_evidence_error(root):
    video = make_video(root/'in.mp4')
    run = root/'outputs/run'
    index = ep.prepare_evidence(video,run,recording_id='sample')
    entry = index['frames'][0]
    entry['raw_pts'] = 10**400
    entry['frame_id'] = ep.frame_id('sample',entry['raw_pts'],ep.rational(entry['time_base']))
    (run/'index.json').write_text(json.dumps(index))
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


def test_huge_index_seconds_returns_evidence_error(root):
    video = make_video(root/'in.mp4')
    run = root/'outputs/run'
    index = ep.prepare_evidence(video,run,recording_id='sample')
    index['recording']['last_frame_seconds'] = 10**400
    (run/'index.json').write_text(json.dumps(index))
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.skipif(os.name!='nt',reason='Windows junction only')
def test_actual_windows_junction_escape(root):
    target = root/'outside'
    target.mkdir()
    (root/'outputs').mkdir()
    link = root/'outputs/junction'
    result = subprocess.run(['cmd','/c','mklink','/J',str(link),str(target)],capture_output=True)
    assert result.returncode == 0
    assert link.is_junction()
    video = make_video(root/'input.mp4')
    with pytest.raises(EvidenceError): ep.prepare_evidence(video,link/'run',recording_id='sample')
    assert not (target/'run').exists()


@pytest.fixture
def export_pair(root):
    """Real producer output; mutations below touch only synthetic temporary files."""
    video = make_video(root/'input.mp4')
    run = root/'outputs/pair'
    index = ep.prepare_evidence(video,run,recording_id='sample',times=[0,.1])
    report = json.loads((run/index['export_report']).read_text(encoding='utf-8'))
    return run,index,report


def save_pair(run,index,report):
    (run/'index.json').write_text(json.dumps(index),encoding='utf-8')
    (run/index['export_report']).write_text(json.dumps(report),encoding='utf-8')


def test_load_indexes_rejects_requested_time_mismatch(export_pair):
    run,index,report = export_pair
    index['frames'][0]['requested_seconds'] = 1000
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


def test_load_indexes_rejects_consistently_forged_time(export_pair):
    run,index,report = export_pair
    index['frames'][0]['requested_seconds'] = 1000
    report['results'][0]['requested_time_seconds'] = 1000
    report['results'][0]['error_seconds'] = -1000
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('content',[
    b'\xffprivate-content',b'[]',b'{"report_format_version":2}',
    b'{"status":"success","status":"partial"}',b'{"x":NaN}',
    b'{"x":Infinity}',b'{"x":1e400}',b'{"x":'+b'9'*400+b'}',
])
def test_report_parsing_rejected(export_pair,content):
    run,index,_ = export_pair
    (run/index['export_report']).write_bytes(content)
    with pytest.raises(EvidenceError) as error: ep.load_indexes([run/'index.json'])
    assert str(run) not in str(error.value)
    assert 'private-content' not in str(error.value)


@pytest.mark.parametrize('change',['remove','add','reorder','other_run'])
def test_report_pairing_rejected(export_pair,change):
    run,index,report = export_pair
    if change=='remove': report['results'].pop()
    elif change=='add': report['results'].append(report['results'][0].copy())
    elif change=='reorder': report['results'].reverse()
    else:
        other = run.parent/'other'
        ep.prepare_evidence(run.parents[1]/'input.mp4',other,recording_id='sample',times=[.01,.11])
        report = json.loads((other/'exports/report.json').read_text())
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('field,value',[
    ('requested_time_seconds',.01),('actual_time_seconds',.01),('raw_pts',1),
    ('time_base','1/10'),('output_width',63),('output_height',47),
    ('image','frame_0001.png'),('reason','outside_100ms_tolerance'),
    ('error_seconds',.01),('raw_time_seconds',.01),('status','miss'),
    ('raw_pts',True),('requested_time_seconds',False),('time_base','-1/-1000'),
    ('time_base',{'numerator':1,'denominator':1000}),
    ('time_base','1/0'),
])
def test_report_shared_fields_rejected(export_pair,field,value):
    run,index,report = export_pair
    report['results'][0][field] = value
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('section,field,value',[
    ('video','width',63),('video','rotation_degrees',90),('video','duration_seconds',10),
    ('timeline','origin_pts',1),('timeline','origin_time_base','1/10'),
    ('timeline','origin_seconds',.01),('timeline','selection','nearest'),
    ('timeline','basis','FPS'),('timeline','tolerance_seconds',.101),
    ('root','status','partial'),('root','report_format_version',True),
    ('video','stream_index',False),('video','warnings','bad'),
])
def test_report_metadata_rejected(export_pair,section,field,value):
    run,index,report = export_pair
    (report if section=='root' else report[section])[field] = value
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('delta',[-.000001,.101,.100001])
def test_consistently_forged_delay_rejected(root,delta):
    # Real .1s candidate, with coherent fields on both sides but invalid delay.
    pts = (0,101,200) if delta==.101 else (0,200,300) if delta==.100001 else (0,100,200)
    video = make_video(root/'input.mp4',pts)
    run = root/'outputs/forged'
    index = ep.prepare_evidence(video,run,recording_id='sample',times=[.2 if delta==.100001 else .1])
    report = json.loads((run/index['export_report']).read_text())
    request = index['frames'][0]['timestamp_seconds']-delta
    index['frames'][0]['requested_seconds'] = request
    report['results'][0].update(requested_time_seconds=request,error_seconds=delta)
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('pts,times,status,frames',[
    ((0,100,200),[0,.1],'success',2),
    ((0,200,300),[.1],'success',1),  # exactly 100ms, inclusive
    ((0,201,300),[.1],'partial',1), # candidate retained, no image
    ((0,100,200),[0,10],'partial',2),
    ((0,100,200),[10,11],'partial',2),
    ((5000,5070,5210,5500),[0,.06,.2,.5],'success',4),
    ((0,100,200),[F(1,30)],'success',1),
])
def test_legal_export_time_states(root,pts,times,status,frames):
    video = make_video(root/'input.mp4',pts,rotation=90)
    run = root/'outputs/legal'
    index = ep.prepare_evidence(video,run,recording_id='sample',times=times)
    assert index['status']==status
    merged = ep.load_indexes([run/'index.json'])
    assert len(merged['sample']['frames'])==frames
    for f in merged['sample']['frames']:
        if f['status']=='miss': assert f['image_path'] is None


def test_equivalent_bases_null_duration_and_negative_origin(export_pair):
    run,index,report = export_pair
    report['video']['duration_seconds'] = index['recording']['duration_seconds'] = None
    base = F(report['timeline']['origin_time_base'])
    report['timeline'].update(origin_pts=-int(1/base),origin_seconds=-1.0)
    index['recording']['origin_pts'] = -int(1/base)
    report['timeline']['origin_time_base'] = f'{base.numerator*2}/{base.denominator*2}'
    for f,r in zip(index['frames'],report['results']):
        tb = ep.rational(f['time_base'])
        f['raw_pts'] -= int(1/tb)
        r['raw_pts'] = f['raw_pts']
        r['raw_time_seconds'] -= 1
        r['time_base'] = f'{tb.numerator*2}/{tb.denominator*2}'
        f['frame_id'] = ep.frame_id('sample',f['raw_pts'],tb)
    save_pair(run,index,report)
    assert len(ep.load_indexes([run/'index.json'])['sample']['frames'])==2


@pytest.mark.parametrize('bad',[False,True])
def test_duplicate_frame_requests_checked_before_merge(root,bad):
    video = make_video(root/'input.mp4')
    run = root/'outputs/duplicates'
    index = ep.prepare_evidence(video,run,recording_id='sample',times=[.01,.02])
    report = json.loads((run/index['export_report']).read_text())
    if bad:
        index['frames'][1]['requested_seconds'] = 1000
        report['results'][1].update(requested_time_seconds=1000,error_seconds=-999.9)
        save_pair(run,index,report)
        with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])
    else:
        frames = ep.load_indexes([run/'index.json'])['sample']['frames']
        assert len(frames)==1
        assert len(frames[0]['_aliases'])==2


@pytest.mark.parametrize('kind',['error','success_miss','partial_success','miss_image','error_row','empty','unordered'])
def test_contradictory_export_states_rejected(export_pair,kind):
    run,index,report = export_pair
    if kind=='error': report['status']=index['status']='error'
    elif kind=='partial_success': report['status']=index['status']='partial'
    elif kind=='empty': report['results']=[]; index['frames']=[]
    elif kind=='unordered': report['results'].reverse(); index['frames'].reverse()
    else:
        status='error' if kind=='error_row' else 'miss'
        report['results'][0].update(status=status,reason='outside_100ms_tolerance')
        index['frames'][0].update(status=status,reason='outside_100ms_tolerance')
        if kind!='miss_image':
            for field in ('image_path','image_width','image_height'): index['frames'][0][field]=None
            for field in ('image','output_width','output_height'): report['results'][0][field]=None
        if kind=='error_row': report['status']=index['status']='partial'
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.parametrize('image',['../../outside.png','/absolute.png','https://private.invalid/frame.png','same/frame_0000.png'])
def test_report_image_paths_rejected(export_pair,image):
    run,index,report = export_pair
    (run/'exports/same').mkdir()
    Image.new('RGB',(64,48),'black').save(run/'exports/same/frame_0000.png')
    report['results'][0]['image'] = image
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


@pytest.mark.skipif(os.name!='nt',reason='Windows junction only')
def test_report_image_junction_rejected(export_pair):
    run,index,report = export_pair
    outside=run.parents[1]/'outside'
    outside.mkdir()
    Image.new('RGB',(64,48),'black').save(outside/'frame_0000.png')
    link=run/'exports/link'
    assert subprocess.run(['cmd','/c','mklink','/J',str(link),str(outside)],capture_output=True).returncode==0
    report['results'][0]['image']='link/frame_0000.png'
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])


def test_native_nonterminating_last_frame_roundtrip(root):
    # make_video's millisecond clock cannot encode exactly 1/30s. This narrow
    # real fixture uses the same codec/geometry with a 30Hz rational clock.
    video=root/'thirty.mp4'
    with av.open(str(video),'w') as container:
        stream=container.add_stream('libx264',rate=30)
        stream.width,stream.height=64,48
        stream.pix_fmt='yuv420p'
        stream.time_base=stream.codec_context.time_base=F(1,30)
        stream.options={'bf':'0','crf':'0'}
        for pts in (0,1):
            frame=av.VideoFrame.from_image(Image.new('RGB',(64,48),'red'))
            frame.pts,frame.time_base=pts,F(1,30)
            for packet in stream.encode(frame): container.mux(packet)
        for packet in stream.encode(): container.mux(packet)
    run=root/'outputs/thirty'
    index=ep.prepare_evidence(video,run,recording_id='sample')
    assert index['recording']['last_frame_seconds']==float(F(1,30))
    assert len(ep.load_indexes([run/'index.json'])['sample']['frames'])==2


@pytest.mark.parametrize('kind',['backwards_success','backwards_miss','skipped_known_candidate'])
def test_cross_request_candidate_contradictions_rejected(root,kind):
    video=make_video(root/'input.mp4',(0,200,210,300))
    run=root/'outputs/order'
    index=ep.prepare_evidence(video,run,recording_id='sample',times=[.11,.21])
    report=json.loads((run/index['export_report']).read_text(encoding='utf-8'))
    if kind!='skipped_known_candidate':
        index['frames'].reverse()
        report['results'].reverse()
    targets=[.01,.02] if kind=='backwards_miss' else [.11,.12]
    delays=[.20,.18] if kind=='backwards_miss' else [.10,.08] if kind=='backwards_success' else [.09,.09]
    for i in range(2):
        f,e=index['frames'][i],report['results'][i]
        f['requested_seconds']=e['requested_time_seconds']=targets[i]
        e['error_seconds']=delays[i]
        if kind=='backwards_miss':
            f.update(status='miss',reason='outside_100ms_tolerance',image_path=None,image_width=None,image_height=None)
            e.update(status='miss',reason='outside_100ms_tolerance',image=None,output_width=None,output_height=None)
    if kind=='backwards_miss': index['status']=report['status']='partial'
    save_pair(run,index,report)
    with pytest.raises(EvidenceError): ep.load_indexes([run/'index.json'])
