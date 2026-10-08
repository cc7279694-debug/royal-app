import importlib
import json

import pytest

from tools.preannotation.bundle import file_sha, write_json


def prepare(tmp_path):
    source = tmp_path / 'video.mp4'
    source.write_bytes(b'synthetic source bytes')
    config = {'underlying_match_id': 'synthetic-match', 'source_dimensions_wh': [100, 100],
              'source_origin_seconds_exact': '0', 'source_recording': str(source), 'source_sha256': file_sha(source)}
    cfg = tmp_path / 'config.json'
    write_json(cfg, config)
    predictions = tmp_path / 'predictions.json'
    write_json(predictions, {'config_sha256': file_sha(cfg), 'frames': [
        {'sample_index': i, 'raw_pts': i, 'time_base': '1/4', 'timestamp_seconds': i / 4,
         'detections': [{'class': 'witch', 'confidence': .8, 'bbox_xyxy_original': [1, 1, 10, 20],
                         'owner_prediction': 'opponent', 'owner_channel': 1}]} for i in range(2)]})
    return {'sources': [{'predictions': str(predictions), 'config': str(cfg),
                         'prediction_sha256': file_sha(predictions), 'config_sha256': file_sha(cfg)}]}


def run(config, out):
    return importlib.import_module('tools.detector_events.cli').replay_files(config, out)


def test_seals_actual_predictions_and_generated_events_without_event_truth(tmp_path):
    sources = prepare(tmp_path)
    out = tmp_path / 'run'
    result = run(sources, out)
    assert result['event_count'] == 1
    from tools.event_engine.cli import verify_artifacts
    verify_artifacts(out)
    event = json.loads((out / 'opponent-card-played.json').read_text())['events'][0]
    assert event['timestamp'] == 0 and event['confirmed_at'] == .25
    assert json.loads((out / 'source-summary.json').read_text())['event_gt_used_as_input'] is False
    with pytest.raises(ValueError): run(sources, out)


def test_rejects_event_gt_source_or_hash_mutation_before_writing(tmp_path):
    sources = prepare(tmp_path)
    sources['gt_lock'] = 'do not read'
    with pytest.raises(ValueError): run(sources, tmp_path / 'one')
    assert not (tmp_path / 'one').exists()
    del sources['gt_lock']
    sources['sources'][0]['prediction_sha256'] = '0' * 64
    with pytest.raises(ValueError): run(sources, tmp_path / 'two')
    assert not (tmp_path / 'two').exists()


def test_own_or_unknown_predictions_produce_no_confirmed_events(tmp_path):
    sources = prepare(tmp_path)
    path = tmp_path / 'predictions.json'
    data = json.loads(path.read_text())
    for frame in data['frames']:
        frame['detections'][0].update(owner_prediction='unknown', owner_channel=None)
    path.write_text(json.dumps(data))
    sources['sources'][0]['prediction_sha256'] = file_sha(path)
    assert run(sources, tmp_path / 'run')['event_count'] == 0
