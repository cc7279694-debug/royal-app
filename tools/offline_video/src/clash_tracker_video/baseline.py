"""Transparent development-only visual proposals; never confirmed card plays.

Scanner inputs contain pixels/templates/configuration only. Hidden deployment
metadata is a separate, post-ranking evaluation input, never a search hint.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import math

import cv2
import numpy as np

from .evidence_contract import EvidenceError
from .experiment_lock import canonical_bytes


@dataclass(frozen=True)
class Config:
    roi: tuple = (0., .12, 1., .73)
    scales: tuple = (.85, .925, 1., 1.075, 1.15)
    fps: float = 4.
    fine_seconds: float = 1.
    merge_seconds: float = 2.
    working_scale: float = .5
    proposal_floor: float = .55
    coarse_seeds: int = 24
    top_k: int = 5

    def __post_init__(self):
        numeric = (self.fps, self.fine_seconds, self.merge_seconds, self.working_scale,
                   self.proposal_floor, *self.scales, *self.roi)
        if (any(type(x) not in (int, float) or not math.isfinite(x) for x in numeric)
                or not self.scales or any(x <= 0 for x in self.scales)
                or min(self.fps,self.fine_seconds,self.merge_seconds,self.working_scale) <= 0
                or self.working_scale > 1 or not 0 <= self.proposal_floor <= 1
                or type(self.coarse_seeds) is not int or self.coarse_seeds < 1
                or type(self.top_k) is not int or self.top_k != 5):
            raise EvidenceError('Invalid fixed baseline configuration.')
        _box(dict(zip(('x','y','width','height'),self.roi)))

    def document(self):
        return {k:list(v) if isinstance(v,tuple) else v for k,v in asdict(self).items()}


def _box(box):
    if type(box) is not dict or set(box) != {'x','y','width','height'}:
        raise EvidenceError('Invalid normalized baseline box.')
    x,y,w,h = (box[k] for k in ('x','y','width','height'))
    if (any(type(v) not in (int,float) or not math.isfinite(v) for v in (x,y,w,h))
            or min(x,y) < 0 or min(w,h) <= 0 or x+w > 1+1e-12 or y+h > 1+1e-12):
        raise EvidenceError('Baseline box outside full image.')
    return x,y,w,h


def crop(image, box):
    x,y,w,h = _box(box)
    height,width = image.shape[:2]
    left,top = math.floor(x*width),math.floor(y*height)
    right,bottom = min(width,math.ceil((x+w)*width)),min(height,math.ceil((y+h)*height))
    if right <= left or bottom <= top:
        raise EvidenceError('Empty baseline crop.')
    return image[top:bottom,left:right].copy()


@dataclass(frozen=True)
class Template:
    template_id: str
    play_id: str
    frame_id: str
    pixels: np.ndarray

    def document(self):
        return dict(template_id=self.template_id,play_id=self.play_id,frame_id=self.frame_id,
                    width=self.pixels.shape[1],height=self.pixels.shape[0],
                    crop_rgb_sha256=sha256(self.pixels.tobytes()).hexdigest())


def orb_diagnostic(reference, candidate):
    orb = cv2.ORB_create(nfeatures=64,edgeThreshold=8,patchSize=15)
    k1,d1 = orb.detectAndCompute(cv2.cvtColor(reference,cv2.COLOR_RGB2GRAY),None)
    k2,d2 = orb.detectAndCompute(cv2.cvtColor(candidate,cv2.COLOR_RGB2GRAY),None)
    good = 0
    if d1 is not None and d2 is not None and len(d2) >= 2:
        pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d1,d2,k=2)
        good = sum(len(pair)==2 and pair[0].distance < .75*pair[1].distance for pair in pairs)
    return dict(reference_keypoints=len(k1),candidate_keypoints=len(k2),
                reference_descriptor=d1 is not None,candidate_descriptor=d2 is not None,
                good_matches=int(good),match_ratio=good/len(k1) if k1 else 0.)


def score_frame(image, templates, config):
    """Maximum RGB NCC across fixed template scales; ORB never changes score."""
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise EvidenceError('Baseline requires RGB uint8 pixels.')
    height,width = image.shape[:2]
    work_width,work_height = max(1,round(width*config.working_scale)),max(1,round(height*config.working_scale))
    work = cv2.resize(image,(work_width,work_height),interpolation=cv2.INTER_LINEAR)
    roi_box = dict(zip(('x','y','width','height'),config.roi))
    region = crop(work,roi_box)
    rx,ry = math.floor(config.roi[0]*work_width),math.floor(config.roi[1]*work_height)
    best = None
    skipped = 0
    for template in sorted(templates,key=lambda t:t.template_id):
        for scale in config.scales:
            tw,th = max(1,round(template.pixels.shape[1]*config.working_scale*scale)),max(1,round(template.pixels.shape[0]*config.working_scale*scale))
            if tw > region.shape[1] or th > region.shape[0]:
                skipped += 1; continue
            reference = cv2.resize(template.pixels,(tw,th),interpolation=cv2.INTER_LINEAR)
            if np.var(reference.astype(np.float32),axis=(0,1)).sum() < 1e-6:
                skipped += 1; continue
            values = cv2.matchTemplate(region,reference,cv2.TM_CCOEFF_NORMED)
            values[~np.isfinite(values)] = -1
            _,score,_,location = cv2.minMaxLoc(values)
            if best is None or score > best['score']:
                lx,ly = location
                best = dict(score=float(max(-1.,min(1.,score))),template_id=template.template_id,
                    scale=float(scale),location=dict(x=round((lx+rx)*width/work_width),
                    y=round((ly+ry)*height/work_height),width=round(tw*width/work_width),
                    height=round(th*height/work_height)),
                    orb=orb_diagnostic(reference,region[ly:ly+th,lx:lx+tw]))
    if best is None:
        best = dict(score=None,template_id=None,scale=None,location=None,orb=None)
    best['skipped_scales'] = skipped
    return best


def merge_events(observations, *, window=2., floor=.55):
    """Adjacent supported observations are one transitive candidate, not a play.

    A long uninterrupted appearance is never divided into fixed two-second bins.
    Without tracking, a >window evidence gap can still split one physical play;
    this limitation is reported rather than calling all proposals independent GT.
    """
    selected = [deepcopy(o) for o in observations if o['score'] is not None and o['score'] >= floor]
    selected.sort(key=lambda o:(o['timestamp_seconds'],o['raw_pts'],o['template_id']))
    groups = []
    for item in selected:
        if not groups or item['timestamp_seconds']-groups[-1][-1]['timestamp_seconds'] > window:
            groups.append([])
        groups[-1].append(item)
    result = []
    for group in groups:
        peak = min(group,key=lambda o:(-o['score'],o['timestamp_seconds'],o['template_id'],o['scale']))
        result.append(dict(first=group[0],peak=peak,score=peak['score'],
                           last_seconds=group[-1]['timestamp_seconds'],support_count=len(group)))
    return result


def rank_events(events, *, source_interval=None):
    selected = deepcopy(events)
    if source_interval is not None:
        start,end = source_interval
        selected = [e for e in selected if not (e['first']['timestamp_seconds'] < end and e['last_seconds'] >= start)]
    selected.sort(key=lambda e:(-e['score'],e['first']['timestamp_seconds'],e['peak']['template_id']))
    for rank,event in enumerate(selected,1):
        event['rank'] = rank
    return selected


def evaluate(ranked, hidden):
    """Post-freeze temporal proxy, NOT an automatic spatial/identity GT verdict."""
    onset = hidden['deployment_time_seconds']
    hits = [e for e in ranked if onset <= e['first']['timestamp_seconds'] <= onset+2.]
    event = min(hits,key=lambda e:e['rank']) if hits else None
    return dict(play_id=hidden['play_id'],**{
        'pass':event is not None and event['rank']<=5,
        'rank':event['rank'] if event else None,
        'delay_seconds':event['first']['timestamp_seconds']-onset if event else None,
        'true_event_score':max(e['score'] for e in hits) if hits else None,
        'temporal_proxy_only':True})


def coarse_select(timestamps, fps):
    next_target = Fraction(0)
    step = Fraction(1,1)/Fraction(str(fps))
    result = []
    for i,time in enumerate(timestamps):
        if time >= next_target:
            result.append(i)
            while next_target <= time:
                next_target += step
    return result


def fine_windows(seeds, last, radius):
    intervals = sorted((max(0.,t-radius),min(last,t+radius)) for t in seeds)
    merged = []
    for start,end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0],max(end,merged[-1][1]))
        else:
            merged.append((start,end))
    return merged


def final_threshold(folds):
    if len(folds)!=2 or any(f.get('pass') is not True or f.get('true_event_score') is None for f in folds):
        raise EvidenceError('Both held-out folds must pass before building a baseline.')
    return min(f['true_event_score'] for f in folds)


def reference_model_parameters(recording, config):
    """Describe the actual fixed scanner, not generic neural-model options."""
    w,h = recording['width'],recording['height']
    if recording['rotation_degrees'] in (90,270): w,h = h,w
    return dict(input=dict(width=max(1,round(w*config.working_scale)),
        height=max(1,round(h*config.working_scale)),
        crop=dict(zip(('x','y','width','height'),config.roi)),
        resize='stretch',interpolation='bilinear',preprocess=dict(color_order='RGB',
        dtype='uint8',scale=1.,mean=[0,0,0],std=[1,1,1])),
        sampling=dict(fps=config.fps,start_seconds=0),
        nms=dict(enabled=False,iou_threshold=0),
        postprocess=dict(version='transitive_adjacent_support_gap',
        class_agnostic_nms=False,max_detections=5))


def make_artifact(development_sha, target, templates, config, threshold, git_commit):
    return dict(artifact_version=1,artifact_type='reference_template_matcher',
        development_lock_sha256=development_sha,target=deepcopy(target),
        templates=[t.document() for t in sorted(templates,key=lambda t:t.template_id)],
        opencv_version=cv2.__version__,numpy_version=np.__version__,config=config.document(),
        score_method='RGB_TM_CCOEFF_NORMED',preprocessing='uint8_RGB_bilinear_working_scale',
        event_merge='transitive_adjacent_support_gap',orb=dict(nfeatures=64,edge_threshold=8,
            patch_size=15,ratio=.75,ranking_weight=0),threshold=threshold,
        threshold_derivation='min_two_held_out_true_event_peak_scores',git_commit=git_commit,
        evaluation_protocol_version=1)


def artifact_sha(artifact):
    return sha256(canonical_bytes(artifact)).hexdigest()
