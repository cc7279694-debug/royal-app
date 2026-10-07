import importlib

import pytest


def evaluate(events,gt):
    try: m=importlib.import_module('tools.event_engine.evaluation')
    except ImportError: pytest.fail('Post-replay Event GT scorer is not implemented')
    return m.evaluate(events,gt)


def truth():
    return {'confirmed_events':[{'event_gt_id':'gt1','candidate_id':'c1','underlying_match_id':'m1',
        'card_id':'witch','approximate_timestamp':10}],
        'continuity_dedupe_outcomes':[{'candidate_id':'c3','underlying_match_id':'m1'}],
        'unresolved_candidates':[{'candidate_id':'c2','underlying_match_id':'m1'}],
        'source_plan':{'candidates':[
            {'candidate_id':'c2','underlying_match_id':'m1','card_id':'witch','context':{'start_seconds':20,'end_seconds':26}},
            {'candidate_id':'c3','underlying_match_id':'m1','card_id':'witch','context':{'start_seconds':27,'end_seconds':33}}]}}


def event(i,t,card='witch',match='m1'):
    return {'event_id':i,'match_id':match,'card_id':card,'timestamp':t,'confirmed_at':t+1,'evidence_level':'STRONG'}


@pytest.mark.parametrize('t,hit',[(9.99,False),(10,True),(12.5,True),(12.500001,False)])
def test_hit_window_boundary(t,hit):
    assert evaluate([event('e',t)],truth())['positives'][0]['hit'] is hit


def test_two_events_in_positive_window_fail_duplicate():
    result=evaluate([event('a',10),event('b',11)],truth())
    assert result['positive_hits']==1 and result['positive_duplicates']==1 and not result['passed']


def test_unresolved_events_unscored_not_fp():
    r=evaluate([event('a',10),event('b',22)],truth())
    assert r['passed'] and r['unscored_events'][0]['event_id']=='b'
    assert r['unscored_events'][0]['reason']=='unresolved_review_window'


def test_no_new_window_fails_for_same_card():
    r=evaluate([event('a',10),event('b',29)],truth())
    assert not r['passed'] and r['dedupe_outcomes'][0]['new_event_count']==1


def test_other_card_in_dedupe_window_not_a_duplicate_of_target():
    assert evaluate([event('a',10),event('b',29,'minions')],truth())['passed']


def test_wrong_match_or_card_not_hit():
    assert evaluate([event('a',10,match='m2'),event('b',10,'minions')],truth())['positive_hits']==0


def test_three_named_dedupe_windows_and_five_positive_fixture():
    gt=truth();gt['confirmed_events']=[];gt['continuity_dedupe_outcomes']=[];gt['source_plan']['candidates']=[]
    cards=['witch','royal_hogs','flying_machine','golden_knight','minions']
    for i,c in enumerate(cards):
        gt['confirmed_events'].append({'event_gt_id':f'g{i}','candidate_id':f'c{i}','underlying_match_id':'m1','card_id':c,'approximate_timestamp':i*10})
    for i,cid in enumerate(['candidate_04','candidate_09','candidate_12']):
        gt['continuity_dedupe_outcomes'].append({'candidate_id':cid,'underlying_match_id':'m1'})
        gt['source_plan']['candidates'].append({'candidate_id':cid,'underlying_match_id':'m1','card_id':'witch','context':{'start_seconds':100+i*10,'end_seconds':105+i*10}})
    r=evaluate([event(f'e{i}',i*10+1,c) for i,c in enumerate(cards)],gt)
    assert r['passed'] and r['positive_hits']==5
    assert [r['new_event_count'] for r in r['dedupe_outcomes']]==[0,0,0]


def test_overlapping_gt_windows_are_matched_before_duplicate_count():
    gt=truth();gt['confirmed_events'].append({'event_gt_id':'gt2','candidate_id':'c4',
        'underlying_match_id':'m1','card_id':'witch','approximate_timestamp':11.5})
    r=evaluate([event('a',11.5),event('b',13)],gt)
    assert r['positive_hits']==2 and r['positive_duplicates']==0 and r['passed']


def test_reversed_gt_order_does_not_lose_valid_one_to_one_match():
    gt=truth();gt['confirmed_events'].insert(0,{'event_gt_id':'gt2','candidate_id':'c4',
        'underlying_match_id':'m1','card_id':'witch','approximate_timestamp':11.5})
    r=evaluate([event('a',11.5),event('b',13)],gt)
    assert r['positive_hits']==2 and r['passed']
