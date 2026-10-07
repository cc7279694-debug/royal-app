import importlib
import json
from pathlib import Path

import pytest


def cli():
    try: return importlib.import_module('tools.event_engine.cli')
    except ImportError: pytest.fail('Oracle artifact CLI is not implemented')


def test_invalid_private_input_has_exit_two_without_path_leak(tmp_path,capsys):
    secret=tmp_path/'PRIVATE_ACCOUNT_SECRET.json'
    secret.write_text('{bad','utf8')
    assert cli().main(['event-replay-oracle','--sources',str(secret),'--output',str(tmp_path/'out')])==2
    assert 'PRIVATE_ACCOUNT_SECRET' not in capsys.readouterr().out
    assert not (tmp_path/'out').exists()


def test_unknown_source_kind_rejects_detector(tmp_path):
    source=tmp_path/'s.json';source.write_text(json.dumps({'sources':[{'kind':'katacr','lock_path':'x','sha256':'0'*64}]}))
    assert cli().main(['event-replay-oracle','--sources',str(source),'--output',str(tmp_path/'out')])==2


def test_output_cannot_overwrite(tmp_path):
    out=tmp_path/'out';out.mkdir();(out/'keep').write_text('old')
    with pytest.raises(ValueError): cli().write_artifacts(out,{'keep':{'new':True}})
    assert (out/'keep').read_text()=='old'


def test_output_path_traversal_refused_before_directory_creation(tmp_path):
    with pytest.raises(ValueError): cli().write_artifacts(tmp_path/'out',{'../outside.json':{}})
    assert not (tmp_path/'out').exists()


def test_artifact_hashes_roundtrip_and_tamper(tmp_path):
    cli().write_artifacts(tmp_path/'out',{'observations.json':{'observations':[]},'events.json':{'events':[]}})
    m=cli().verify_artifacts(tmp_path/'out')
    assert set(m['files'])=={'observations.json','events.json'}
    (tmp_path/'out'/'events.json').write_text('{}')
    with pytest.raises(ValueError):cli().verify_artifacts(tmp_path/'out')


def test_recorded_app_projection_has_no_probability():
    record={'event_id':'event-a','match_id':'m','card_id':'witch','timestamp':1,'evidence_level':'STRONG'}
    assert cli().app_projection([record])=={'schema':'recorded_oracle_events_v1','events':[{
        'eventId':'event-a','cardId':'witch','timestamp':1,'confidence':None,'source':'recorded_oracle'}]}


def test_replay_source_does_not_accept_event_lock(tmp_path):
    p=tmp_path/'source.json';p.write_text(json.dumps({'sources':[],'event_gt_lock':'secret'}))
    assert cli().main(['event-replay-oracle','--sources',str(p),'--output',str(tmp_path/'out')])==2


def test_relative_cli_lock_is_normalized_for_strict_existing_loader(tmp_path,monkeypatch):
    from tools.deployment_review import event_gt
    monkeypatch.chdir(tmp_path)
    Path('source').mkdir();Path('source/gt.json').write_text('{}')
    cli().write_artifacts(Path('replay'),{'opponent-card-played.json':{'events':[]}})
    def loader(path):
        if not path.is_absolute():raise ValueError('strict loader requires absolute paths')
        return {'confirmed_events':[],'continuity_dedupe_outcomes':[],
                'unresolved_candidates':[],'source_plan':{'candidates':[]}}
    monkeypatch.setattr(event_gt,'load_lock',loader)
    report=cli().evaluate_replay(Path('replay'),Path('source/gt.json'),cli().file_sha('source/gt.json'),Path('grade'))
    assert report['positive_total']==0
