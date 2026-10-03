from pathlib import Path
import subprocess
import sys
import uuid
import json
import pytest
from clash_tracker_video.evidence_prepare import prepare_evidence


def run(*args):
    return subprocess.run([sys.executable,'-m','clash_tracker_video.evidence_cli',*map(str,args)],
                          capture_output=True,text=True,encoding='utf-8')


def output():
    return Path(__file__).resolve().parents[3]/'outputs'/'synthetic-evidence-tests'/uuid.uuid4().hex


def test_prepare_exit_and_private_path(video):
    result = run('prepare',video,'--recording-id','synthetic','--times',0,10,'--output',output())
    assert result.returncode == 3
    assert str(video) not in result.stdout + result.stderr
    assert 'Traceback' not in result.stderr


def test_bad_input_is_path_free():
    private = 'https://private.invalid/video.mp4'
    result = run('prepare',private,'--recording-id','synthetic','--output',output())
    assert result.returncode == 2
    assert private not in result.stdout + result.stderr


def test_validate_invalid_and_unknown_command():
    result = run('validate','missing-private-evidence.json','--indexes','missing-private-index.json')
    assert result.returncode == 2
    assert 'missing-private' not in result.stdout + result.stderr
    assert run('freeze').returncode == 2


def test_three_commands_real_synthetic(video):
    root = output()
    index = prepare_evidence(video,root,recording_id='synthetic')
    doc = dict(schema_version=1,recordings=[index['recording']],match_segments=[],target_card=None,
               occurrences=[],frame_annotations=[],negative_intervals=[])
    path = root/'evidence.json'
    path.write_text(json.dumps(doc),encoding='utf-8')
    assert run('validate',path,'--indexes',root/'index.json').returncode == 0
    report = root/'review.json'
    result = run('review',path,'--indexes',root/'index.json','--output',report)
    assert result.returncode == 3
    assert json.loads(report.read_text())['experiment_gate'] is False
    assert run('review',path,'--indexes',root/'index.json','--output',report).returncode == 2


@pytest.mark.parametrize('kind',['report','seconds'])
def test_malformed_report_and_huge_seconds_exit_two(video,kind):
    root = output()
    index = prepare_evidence(video,root,recording_id='synthetic')
    doc = dict(schema_version=1,recordings=[index['recording']],match_segments=[],target_card=None,
               occurrences=[],frame_annotations=[],negative_intervals=[])
    path = root/'evidence.json'
    if kind == 'report':
        doc['preparation_report'] = dict(status=[],candidate_gate=False,experiment_gate=False,
            counts=dict(recordings=0,reviewed_complete_segments=0,verified_plays=0,annotated_key_frames=0),reasons=[],coverage_gaps=[])
    else:
        doc['recordings'][0]['last_frame_seconds'] = 10**400
    path.write_text(json.dumps(doc),encoding='utf-8')
    result = run('validate',path,'--indexes',root/'index.json')
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr
    assert str(path) not in result.stderr
