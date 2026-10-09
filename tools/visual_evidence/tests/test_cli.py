import importlib
import json
from pathlib import Path
import pytest

def cli():
    try: return importlib.import_module('tools.visual_evidence.cli')
    except ImportError: pytest.fail('visual evidence CLI not implemented')

def test_invalid_private_input_does_not_disclose_path_or_create_output(tmp_path,capsys):
    path=tmp_path/'PRIVATE_USER.json';path.write_text('{invalid')
    assert cli().main(['replay','--input',str(path),'--sha','0'*64,'--baseline',str(path),'--baseline-sha','0'*64,'--tracker-source',str(tmp_path),'--output',str(tmp_path/'out')])==2
    assert 'PRIVATE_USER' not in capsys.readouterr().out and not (tmp_path/'out').exists()

@pytest.mark.parametrize('text',['{"a":1,"a":2}','{"a":NaN}','{"a":1e999}','[]'])
def test_strict_json_refuses_corruption(tmp_path,text):
    p=tmp_path/'x';p.write_text(text)
    with pytest.raises(ValueError): cli().read_stream(p)

def test_generation_api_has_no_gt_argument():
    import inspect
    assert not any('gt' in k for k in inspect.signature(cli().run_files).parameters)
    source=Path(cli().__file__).read_text()
    assert 'deployment_review' not in source and 'event_engine.evaluation' not in source

def test_current_engine_is_not_allowed_human_id_bridge():
    source=Path(cli().__file__).read_text()
    assert "human_gt_continuity" not in source

def test_exact_projected_duplicates_are_traceable_not_negative():
    a={'observation_id':'a','match_id':'m','timestamp':0,'visual_class':'visual.unit.witch','owner':'unknown','bbox':[1,1,3,3]}
    rows,excluded=cli().engine_projection([dict(a,observation_id='z'),a])
    assert [r['observation_id'] for r in rows]==['a']
    assert excluded==[{'observation_id':'z','kept_observation_id':'a','reason':'identical_geometry_after_owner_abstention','negative':False}]
