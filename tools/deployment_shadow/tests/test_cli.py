"""Exercise exclusive sealed replay without exposing Event GT to generation."""
import json
import subprocess
import sys
from pathlib import Path

from tools.event_engine.cli import write_artifacts, verify_artifacts
from tools.event_engine.engine import replay


ROOT = Path(__file__).resolve().parents[3]


def source(tmp_path):
    rows = [dict(observation_id=f'w{i}', match_id='synthetic-match', timestamp=t,
        visual_class='visual.unit.witch', bbox=[20,20,40,60], owner='opponent',
        form='unknown', origin_kind='unknown', source='synthetic_observation') for i,t in enumerate([1.,1.25])]
    frames=[dict(match_id='synthetic-match', timestamp=t) for t in [0.,.25,.5,.75,1.,1.25]]
    folder=tmp_path/'source'
    write_artifacts(folder, {'detector-visual-stream.json': {'observations':rows,'frames':frames},
        'replay.json': replay(rows)})
    return folder


def run(folder, out, *extra):
    return subprocess.run([sys.executable,'-B','-m','tools.deployment_shadow',
        '--replay',str(folder),'--output',str(out),*extra], cwd=ROOT, text=True,capture_output=True)


def test_cli_seals_provisional_events_and_keeps_baseline_separate(tmp_path):
    folder=source(tmp_path); before={p.name:p.read_bytes() for p in folder.iterdir()}
    out=tmp_path/'shadow'
    result=run(folder,out)
    assert result.returncode==0, result.stdout+result.stderr
    verify_artifacts(out)
    baseline=json.loads((out/'baseline-replay.json').read_text())
    assert baseline==json.loads((folder/'replay.json').read_text())
    event=json.loads((out/'opponent-card-played.json').read_text())['events'][0]
    assert event['timestamp']==1. and event['confirmed_at']==1.25
    assert event['shadow_status']=='PROVISIONAL' and event['not_confirmed_card_play'] is True
    summary=json.loads((out/'source-summary.json').read_text())
    assert summary['event_gt_used_as_input'] is False
    assert summary['production_replacement'] is False
    assert before=={p.name:p.read_bytes() for p in folder.iterdir()}
    second=run(folder,out)
    assert second.returncode==2
    assert str(tmp_path) not in second.stdout+second.stderr


def test_cli_rejects_changed_input_before_creating_output(tmp_path):
    folder=source(tmp_path)
    (folder/'replay.json').write_text('{}')
    out=tmp_path/'shadow'
    result=run(folder,out)
    assert result.returncode==2
    assert not out.exists()
    assert str(tmp_path) not in result.stdout+result.stderr


def test_cli_rejects_gt_input_and_cannot_overwrite_source(tmp_path):
    folder=source(tmp_path)
    before={p.name:p.read_bytes() for p in folder.iterdir()}
    result=run(folder,tmp_path/'new','--gt-lock',str(tmp_path/'private.json'))
    assert result.returncode==2
    assert not (tmp_path/'new').exists()
    assert str(tmp_path) not in result.stdout+result.stderr
    result=run(folder,folder)
    assert result.returncode==2
    assert before=={p.name:p.read_bytes() for p in folder.iterdir()}


def test_cli_rejects_self_consistent_but_wrong_baseline(tmp_path):
    folder=source(tmp_path)
    stream=json.loads((folder/'detector-visual-stream.json').read_text())
    other=tmp_path/'other'
    write_artifacts(other, {'detector-visual-stream.json':stream,'replay.json':replay([])})
    result=run(other,tmp_path/'shadow')
    assert result.returncode==2
    assert not (tmp_path/'shadow').exists()


def test_sealed_detector_stream_larger_than_oracle_gt_limit_is_supported(tmp_path):
    # Actual detector streams include binding rows and exceed the GT loader cap.
    folder=source(tmp_path)
    stream=json.loads((folder/'detector-visual-stream.json').read_text())
    stream['bindings']=[{'synthetic_padding':'x'*(17*1024*1024)}]
    large=tmp_path/'large'
    write_artifacts(large, {'detector-visual-stream.json':stream,
        'replay.json':json.loads((folder/'replay.json').read_text())})
    result=run(large,tmp_path/'shadow')
    assert result.returncode==0, result.stdout+result.stderr
    assert len(json.loads((tmp_path/'shadow/opponent-card-played.json').read_text())['events'])==1


def test_stream_size_guard_rejects_oversize_before_parsing(tmp_path):
    folder=source(tmp_path)
    stream=folder/'detector-visual-stream.json'
    with stream.open('wb') as f:
        f.seek(64*1024*1024)
        f.write(b' ')
    # Update the seal to distinguish size rejection from hash rejection.
    from tools.event_engine.oracle import file_sha
    manifest=json.loads((folder/'manifest.json').read_text())
    manifest['files'][stream.name]=file_sha(stream)
    (folder/'manifest.json').write_text(json.dumps(manifest))
    result=run(folder,tmp_path/'shadow')
    assert result.returncode==2 and not (tmp_path/'shadow').exists()
