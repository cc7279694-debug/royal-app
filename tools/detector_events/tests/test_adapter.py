from copy import deepcopy
import importlib

import pytest


def inputs():
    return ({'config_sha256': 'a' * 64, 'frames': [
        {'sample_index': 0, 'timestamp_seconds': 1., 'raw_pts': 10, 'time_base': '1/10',
         'detections': [{'class': 'witch', 'confidence': .6, 'bbox_xyxy_original': [1, 2, 20, 30],
                         'owner_prediction': 'opponent', 'owner_channel': 1, 'form': 'unknown'}]}]},
        {'underlying_match_id': 'match-a', 'source_dimensions_wh': [100, 100], 'source_origin_seconds_exact': '0'})


def convert(data=None, config=None):
    module = importlib.import_module('tools.detector_events.adapter')
    default, cfg = inputs()
    return module.convert_predictions(default if data is None else data, cfg if config is None else config,
                                      prediction_sha='b' * 64, config_sha='a' * 64)


def test_prediction_keeps_geometry_time_confidence_without_human_identity():
    result = convert()
    row = result['observations'][0]
    assert (row['timestamp'], row['visual_class'], row['bbox'], row['confidence']) == (1., 'visual.unit.witch', [1, 2, 20, 30], .6)
    assert (row['source'], row['owner'], row['form'], row['origin_kind']) == ('katacr_prediction', 'opponent', 'unknown', 'unknown')
    assert 'appearance_group_id' not in row
    assert result['event_gt_used_as_input'] is False


@pytest.mark.parametrize('owner,channel', [('unknown', None), ('opponent', 0), ('opponent', 2), (None, 1)])
def test_uncertain_owner_is_not_filled_from_geometry_or_truth(owner, channel):
    data, cfg = inputs()
    data['frames'][0]['detections'][0].update(owner_prediction=owner, owner_channel=channel)
    assert convert(data, cfg)['observations'][0]['owner'] == 'unknown'


def test_prediction_group_and_card_hints_cannot_become_human_continuity():
    data, cfg = inputs()
    data['frames'][0]['detections'][0].update(appearance_group_id='gt-answer', source_card='witch', origin_kind='primary')
    result = convert(data, cfg)
    assert 'appearance_group_id' not in result['observations'][0]
    assert result['observations'][0]['origin_kind'] == 'unknown'
    assert result['bindings'][0]['raw_prediction']['appearance_group_id'] == 'gt-answer'


def test_spawned_or_unknown_class_never_maps_directly_to_a_card():
    data, cfg = inputs()
    data['frames'][0]['detections'][0]['class'] = 'skeleton'
    from tools.event_engine.engine import replay
    assert replay(convert(data, cfg)['observations'])['events'] == []


@pytest.mark.parametrize('mutation', ['binding', 'time', 'box', 'confidence', 'order'])
def test_rejects_corrupt_bound_prediction_input(mutation):
    data, cfg = inputs()
    row = data['frames'][0]['detections'][0]
    if mutation == 'binding': data['config_sha256'] = 'c' * 64
    if mutation == 'time': data['frames'][0]['timestamp_seconds'] = 5
    if mutation == 'box': row['bbox_xyxy_original'] = [0, 0, 101, 10]
    if mutation == 'confidence': row['confidence'] = float('nan')
    if mutation == 'order': data['frames'].append(deepcopy(data['frames'][0]))
    with pytest.raises(ValueError): convert(data, cfg)


def test_two_real_prediction_frames_feed_unchanged_engine_and_emit_once():
    data, cfg = inputs()
    second = deepcopy(data['frames'][0])
    second.update(sample_index=1, timestamp_seconds=1.25, raw_pts=125, time_base='1/100')
    data['frames'].append(second)
    from tools.event_engine.engine import replay
    result = replay(convert(data, cfg)['observations'])
    assert len(result['events']) == 1
    assert (result['events'][0]['card_id'], result['events'][0]['timestamp'], result['events'][0]['confirmed_at']) == ('witch', 1., 1.25)


def test_identical_boxes_cannot_multiply_grouped_units():
    data, cfg = inputs()
    row = data['frames'][0]['detections'][0]
    row['class'] = 'minion'
    data['frames'][0]['detections'].append(deepcopy(row))
    result = convert(data, cfg)
    from tools.event_engine.engine import replay
    assert len(result['observations']) == 1
    assert result['identical_box_duplicates'] == 1
    assert replay(result['observations'])['events'] == []


def test_nonzero_pts_origin_is_reconstructed_without_using_event_time():
    data, cfg = inputs()
    cfg['source_origin_seconds_exact'] = '5/3'
    data['frames'][0].update(raw_pts=8, time_base='1/3')
    result = convert(data, cfg)
    assert result['observations'][0]['timestamp'] == 1.
    assert result['bindings'][0]['timestamp'] == 1.


def test_evolved_label_is_not_silently_coerced_into_normal_card():
    data, cfg = inputs()
    data['frames'][0]['detections'][0].update(**{'class': 'witch-evolution', 'form': 'evolved'})
    result = convert(data, cfg)
    row = result['observations'][0]
    assert (row['visual_class'], row['form']) == ('visual.other.witch_evolution', 'evolved')
    from tools.event_engine.engine import replay
    assert replay(result['observations'])['events'] == []


def test_empty_detection_frames_preserve_sampling_coverage_not_negative_truth():
    data, cfg = inputs()
    data['frames'][0]['detections'] = []
    result = convert(data, cfg)
    assert result['observations'] == []
    assert len(result['frames']) == 1
    assert result['unknown_is_negative'] is False
