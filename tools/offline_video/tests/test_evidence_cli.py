from pathlib import Path
import subprocess
import sys
import uuid


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
