"""Catch track fragmentation and episode swallowing of genuinely new units."""
import pytest
from tools.event_engine.engine import replay

def units(time, xs, cls='visual.unit.minion', *, offset=0, owner='opponent', origin='unknown'):
    return [dict(observation_id=f'{cls}-{time}-{offset+i}',match_id='m',timestamp=time,
                 visual_class=cls,bbox=[x,20,x+20,50],owner=owner,form='unknown',
                 origin_kind=origin,source='human_gt') for i,x in enumerate(xs)]

@pytest.mark.parametrize('cls,card',[('visual.unit.minion','minions'),('visual.unit.royal_hog','royal_hogs')])
def test_long_movement_keeps_member_identity_and_one_episode(cls,card):
    stream=[]
    for time,x in [(0,20),(2.5,90),(5,170),(7.5,280),(10,410),(12.5,560)]:
        stream+=units(time,[x,x+25,x+50],cls)
    result=replay(stream)
    assert [e['card_id'] for e in result['events']]==[card]
    assert len(result['tracks'])==3
    assert len(result['grouped_episodes'])==1
    episode=result['grouped_episodes'][0]
    assert episode['first_seen']==0 and episode['last_seen']==12.5
    assert episode['state']=='active'
    assert episode['emitted_event_id']==result['events'][0]['event_id']

def test_sampling_gap_motion_reconnects_same_minions():
    stream=units(0,[20,45,70])+units(2.5,[100,125,150])+units(7.5,[280,305,330])
    result=replay(stream)
    assert len(result['events'])==1
    assert len(result['tracks'])==3

@pytest.mark.parametrize('cls',[ 'visual.unit.minion','visual.unit.royal_hog'])
def test_old_members_present_do_not_swallow_new_coexisting_units(cls):
    stream=units(0,[20,45,70],cls)+units(1,[22,47,72],cls)+units(1,[90,115,140],cls,offset=10)
    result=replay(stream)
    assert len(result['events'])==2
    assert [e['timestamp'] for e in result['events']]==[0,1]
    episodes=result['grouped_episodes']
    assert len(episodes)==2
    assert set(episodes[0]['member_track_ids']).isdisjoint(episodes[1]['member_track_ids'])

def test_expired_first_group_new_group_can_play_again():
    result=replay(units(0,[20,45,70])+units(1,[22,47,72])+units(30,[22,47,72]))
    assert len(result['events'])==2
    assert {e['first_seen']:e['state'] for e in result['grouped_episodes']}=={0:'closed',30:'active'}

def test_episode_occlusion_state_without_extra_card_event():
    stream=units(0,[20,45,70])+units(2.5,[100,125,150])
    stream+=units(5,[350],cls='visual.structure.cannon')
    result=replay(stream)
    assert len(result['events'])==1
    assert result['grouped_episodes'][0]['state']=='occluded'
    assert result['grouped_episodes'][0]['last_seen']==2.5

@pytest.mark.parametrize('owner,origin',[('own','unknown'),('unknown','unknown'),('opponent','spawned')])
def test_guarded_groups_never_create_episode_event(owner,origin):
    result=replay(units(0,[20,45,70],owner=owner,origin=origin)+units(2.5,[200,225,250],owner=owner,origin=origin))
    assert result['events']==[]

def test_motion_gap_not_permanent_episode_cooldown():
    # New coexisting objects, not elapsed card time, establish a second play.
    result=replay(units(0,[20,45,70])+units(.5,[22,47,72])+units(.5,[95,120,145],offset=10))
    assert len(result['events'])==2
    assert result['events'][1]['timestamp']==.5

def test_confirmed_human_group_with_more_visible_members_never_reemits():
    stream=units(0,[20,45])+units(100,[20,45,70,95])
    for row in stream:
        row.update(appearance_group_id='confirmed-same-group',source='human_gt_continuity')
    result=replay(stream)
    assert len(result['events'])==1
    assert len(result['grouped_episodes'])==1
    assert len(result['grouped_episodes'][0]['member_track_ids'])==4

def test_fixed_gap_ceiling_still_allows_new_tracks_after_expiry():
    result=replay(units(0,[20,45,70])+units(7.5001,[20,45,70]))
    assert len(result['events'])==2
    assert len(result['tracks'])==6

def test_single_old_survivor_and_three_genuinely_new_tracks_allow_second_play():
    stream=units(0,[20,45,70])+units(1,[22])+units(1,[300,325,350],offset=10)
    result=replay(stream)
    assert len(result['events'])==2
    assert [e['timestamp'] for e in result['events']]==[0,1]
    assert len(result['tracks'])==6
