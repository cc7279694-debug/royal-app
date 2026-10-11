"""Synthetic-video contract tests: no private GT/model/recording inputs."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib
import json
from pathlib import Path

import av
from PIL import Image
import pytest

from tools.detector_events.cli import replay_files


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True), encoding='utf-8')


@pytest.fixture
def frozen(tmp_path):
    source = tmp_path / 'synthetic.mp4'
    with av.open(str(source), 'w') as container:
        stream = container.add_stream('mpeg4', rate=4)
        stream.width, stream.height, stream.pix_fmt = 640, 96, 'yuv420p'
        for index in range(5):
            frame = av.VideoFrame.from_image(Image.new('RGB', (640, 96), (index * 30, 70, 90)))
            frame.pts, frame.time_base = index, Fraction(1, 4)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    with av.open(str(source)) as container:
        decoded = list(container.decode(video=0))
    origin = decoded[0].pts * decoded[0].time_base
    config = tmp_path / 'config.json'
    write(config, {'underlying_match_id': 'synthetic-match', 'source_dimensions_wh': [640, 96],
                   'source_origin_seconds_exact': str(origin), 'source_recording': str(source),
                   'source_sha256': sha(source)})
    frames = []
    for index, frame in enumerate(decoded):
        items = []
        if index in (0, 1, 3, 4):
            left = 8 if index < 2 else 400
            items.append({'class': 'witch', 'confidence': .8 + index * .01,
                          'bbox_xyxy_original': [left, 16, left + 30, 70],
                          'owner_prediction': 'opponent', 'owner_channel': 1})
        else:
            for label, owner, channel, left in [('witch', 'own', 0, 200),
                                               ('witch', 'unknown', None, 300),
                                               ('skeleton', 'opponent', 1, 450)]:
                items.append({'class': label, 'confidence': .6,
                              'bbox_xyxy_original': [left, 16, left + 30, 70],
                              'owner_prediction': owner, 'owner_channel': channel})
        frames.append({'sample_index': index, 'raw_pts': frame.pts,
                       'time_base': str(frame.time_base), 'timestamp_seconds': float(frame.pts * frame.time_base - origin),
                       'detections': items})
    predictions = tmp_path / 'predictions.json'
    write(predictions, {'config_sha256': sha(config), 'frames': frames})
    replay = tmp_path / 'replay'
    replay_files({'sources': [{'predictions': str(predictions), 'config': str(config),
                              'prediction_sha256': sha(predictions), 'config_sha256': sha(config)}]}, replay)
    return {'source': source, 'config': config, 'replay': replay, 'match': 'synthetic-match',
            'output': tmp_path / 'export'}


def module():
    return importlib.import_module('tools.assisted_tracking.exporter')


def export(frozen, **changes):
    args = {**frozen, **changes}
    return module().export_packet(args['replay'], args['config'], args['source'], args['match'], args['output'])


def test_exports_candidate_identity_and_repeated_cards_without_confirmation(frozen):
    packet = export(frozen)
    assert packet['schema'] == 'offline_assisted_candidates_v1'
    assert [row['card_id'] for row in packet['candidates']] == ['witch', 'witch']
    assert [row['timestamp'] for row in packet['candidates']] == [0, .75]
    assert packet['summary']['total_match_candidates'] == 5
    assert packet['summary']['excluded_candidates'] == 3
    assert packet['summary']['exclusion_reasons'] == {'owner_guard': 2, 'unsupported_card': 1, 'insufficient_evidence': 0}
    assert packet['candidates'][0]['confidence'] == .81
    assert 'decision' not in packet['candidates'][0]
    assert set(packet) == {'schema', 'packet_id', 'match_id', 'provenance', 'candidates', 'evidence', 'summary'}
    replay = json.loads((frozen['replay'] / 'replay.json').read_text())
    assert {row['candidate_id'] for row in packet['candidates']} <= {row['candidate_id'] for row in replay['candidates']}
    assert module().validate_packet(packet) == packet
    assert (frozen['output'] / 'candidates.json').is_file()
    assert (frozen['output'] / 'contact-sheet.jpg').is_file()


def test_deterministic_export_exact_pts_and_readonly_sources(frozen):
    paths = [frozen['source'], frozen['config'], *frozen['replay'].iterdir()]
    before = {str(path): sha(path) for path in paths}
    first = export(frozen)
    second = export(frozen, output=frozen['output'].with_name('second'))
    assert first == second
    assert before == {str(path): sha(path) for path in paths}
    assert sorted(row['timestamp'] for row in first['evidence']) == [0, .25, .75, 1]
    for evidence in first['evidence']:
        assert float(Fraction(evidence['raw_pts']) * Fraction(evidence['time_base'])) == evidence['timestamp']
        assert [evidence['source_width'], evidence['source_height']] == [640, 96]
    old_sha = sha(frozen['output'] / 'candidates.json')
    with pytest.raises(ValueError):
        export(frozen)
    assert sha(frozen['output'] / 'candidates.json') == old_sha


@pytest.mark.parametrize('member', ['replay.json', 'detector-visual-stream.json', 'source-summary.json'])
def test_rejects_changed_frozen_hash_before_output(frozen, member):
    with (frozen['replay'] / member).open('a') as handle:
        handle.write(' ')
    with pytest.raises(ValueError):
        export(frozen)
    assert not frozen['output'].exists()


def test_rejects_stale_recording_before_decode(frozen):
    with frozen['source'].open('ab') as handle:
        handle.write(b'changed')
    with pytest.raises(ValueError):
        export(frozen)
    assert not frozen['output'].exists()


def test_rejects_prediction_file_changed_after_frozen_replay(frozen):
    with (frozen['config'].parent / 'predictions.json').open('a') as handle:
        handle.write(' ')
    with pytest.raises(ValueError):
        export(frozen)
    assert not frozen['output'].exists()


def test_support_frame_limit_uses_first_middle_last_not_gt_window(frozen):
    predictions_path = frozen['config'].parent / 'predictions.json'
    predictions = json.loads(predictions_path.read_text())
    # A third real synthetic source sample supports the first track; preserve
    # other own/unknown/unmapped rows rather than creating candidate answers.
    predictions['frames'][2]['detections'].append({
        'class': 'witch', 'confidence': .82, 'bbox_xyxy_original': [8, 16, 38, 70],
        'owner_prediction': 'opponent', 'owner_channel': 1})
    write(predictions_path, predictions)
    new_replay = frozen['replay'].with_name('three-support-replay')
    replay_files({'sources': [{'predictions': str(predictions_path), 'config': str(frozen['config']),
                              'prediction_sha256': sha(predictions_path), 'config_sha256': sha(frozen['config'])}]}, new_replay)
    packet = export(frozen, replay=new_replay)
    indexed = {row['evidence_id']: row for row in packet['evidence']}
    assert [indexed[eid]['timestamp'] for eid in packet['candidates'][0]['evidence_ids']] == [0, .25, .5]
    assert packet['candidates'][0]['confidence'] == .82


def reseal(frozen, member, data):
    path = frozen['replay'] / member
    write(path, data)
    manifest_path = frozen['replay'] / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['files'][member] = sha(path)
    write(manifest_path, manifest)


def test_rejects_conflicting_source_binding_even_resealed(frozen):
    summary = json.loads((frozen['replay'] / 'source-summary.json').read_text())
    summary['sources'][0]['config_sha256'] = '0' * 64
    reseal(frozen, 'source-summary.json', summary)
    with pytest.raises(ValueError):
        export(frozen)


def test_rejects_source_pts_not_equal_to_observation_timestamp(frozen):
    stream = json.loads((frozen['replay'] / 'detector-visual-stream.json').read_text())
    stream['frames'][0]['raw_pts'] += 1
    reseal(frozen, 'detector-visual-stream.json', stream)
    with pytest.raises(ValueError):
        export(frozen)
    assert not frozen['output'].exists()


def test_rejects_gt_input_or_mislabeled_origin(frozen):
    summary = json.loads((frozen['replay'] / 'source-summary.json').read_text())
    summary['event_gt_used_as_input'] = True
    reseal(frozen, 'source-summary.json', summary)
    with pytest.raises(ValueError):
        export(frozen)


def test_gt_files_are_never_read(frozen):
    # Malformed adjacent GT cannot affect generation, even with a suggestive name.
    (frozen['replay'].parent / 'deployment_event_gt.lock.v1.json').write_text('not json')
    packet = export(frozen)
    assert packet['provenance']['event_gt_used_as_input'] is False
    assert 'gt_timestamp' not in json.dumps(packet)


def test_rejects_gt_manifest_member_before_opening_it(frozen, monkeypatch):
    gt_path = frozen['replay'] / 'event-gt-lock.json'
    gt_path.write_text('{"answer": "do not read"}')
    manifest_path = frozen['replay'] / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['files'][gt_path.name] = sha(gt_path)
    write(manifest_path, manifest)
    original_sha = module().file_sha

    def guarded_sha(path):
        if Path(path) == gt_path:
            pytest.fail('GT member was opened during generation')
        return original_sha(path)

    monkeypatch.setattr(module(), 'file_sha', guarded_sha)
    with pytest.raises(ValueError):
        export(frozen)
    assert not frozen['output'].exists()


def test_rejects_unbound_evidence_and_forged_summary_count(frozen):
    packet = export(frozen)
    changed = deepcopy(packet)
    changed['candidates'][0]['evidence_ids'] = ['unbound-id']
    with pytest.raises(ValueError):
        module().validate_packet(changed)
    changed = deepcopy(packet)
    changed['summary']['exported_candidates'] += 1
    with pytest.raises(ValueError):
        module().validate_packet(changed)


def test_packet_parser_rejects_unsupported_claims_and_corrupt_image(frozen):
    packet = export(frozen)
    changed = deepcopy(packet)
    changed['candidates'][0]['decision'] = 'confirmed'
    with pytest.raises(ValueError):
        module().validate_packet(changed)
    changed = deepcopy(packet)
    changed['evidence'][0]['image_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        module().validate_packet(changed)


def test_cli_sanitizes_private_paths_and_rejects_unsafe_output(frozen, capsys):
    code = module().main(['--replay', str(frozen['replay']), '--config', str(frozen['config']),
                          '--source', str(frozen['source']), '--match', frozen['match'],
                          '--output', str(frozen['replay'] / 'new')])
    assert code == 2
    output = capsys.readouterr().out
    assert str(frozen['source'].parent) not in output
    assert not (frozen['replay'] / 'new').exists()
