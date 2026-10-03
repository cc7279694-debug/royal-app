"""Private indexes and contact previews reusing Module 1 unchanged."""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path, PureWindowsPath

import av
from PIL import Image, ImageDraw

from . import pipeline
from .evidence_contract import EvidenceError, SCHEMAS, load_evidence, valid_type, rational, seconds

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def safe_path(value, *, private=False):
    text = str(value)
    if '://' in text or text.startswith(('//','\\\\')) or '..' in PureWindowsPath(text).parts:
        raise EvidenceError('Only explicit local paths without traversal are accepted.')
    path = Path(value).absolute()
    for ancestor in [path, *path.parents]:
        if ancestor.is_symlink() or ancestor.is_junction():
            raise EvidenceError('Links and junctions are unsupported.')
    if private and not any(path.is_relative_to(PROJECT_ROOT / folder) for folder in ('outputs','local_data')):
        raise EvidenceError('Evidence must stay in project outputs or local_data.')
    return path


def new_output(value, *, directory=True):
    path = safe_path(value, private=True)
    if path.exists(): raise EvidenceError('Output must be exclusively new.')
    path.parent.mkdir(parents=True, exist_ok=True)
    if directory: path.mkdir(exist_ok=False)
    return path


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''): result.update(chunk)
    return result.hexdigest()


def write_json(path, doc):
    with Path(path).open('x',encoding='utf-8') as handle:
        json.dump(doc,handle,ensure_ascii=False,indent=2,allow_nan=False)
        handle.write('\n')


def frame_id(recording_id, raw_pts, time_base):
    value = raw_pts * time_base
    identity = f'{recording_id}\0{value.numerator}/{value.denominator}'
    return 'f_' + hashlib.sha256(identity.encode('utf-8')).hexdigest()[:32]


def default_times(last: Fraction):
    return sorted({Fraction(t) for t in range(0,int(last)+1,5)} | {last})


def _scan(source):
    origin = previous = None
    origin_pts = origin_base = None
    dimensions = None
    with av.open(str(source)) as container:
        stream = pipeline._stream(container)
        for frame in container.decode(stream):
            rotation = pipeline._validate_frame(frame)
            time = pipeline._timestamp(frame)
            current = (frame.width,frame.height,rotation)
            if previous is not None and (time <= previous or current != dimensions):
                raise EvidenceError('Invalid timeline or changing displayed geometry.')
            if origin is None:
                origin,origin_pts,origin_base,dimensions = time,frame.pts,frame.time_base,current
            previous = time
    if origin is None: raise EvidenceError('No display frames.')
    return origin_pts,origin_base,previous-origin


def _base(value):
    return dict(numerator=value.numerator,denominator=value.denominator)


def _contacts(output, frames):
    paths = []
    successful = [f for f in frames if f['status']=='success']
    (output/'contacts').mkdir()
    for offset in range(0,len(successful),12):
        batch = successful[offset:offset+12]
        page = Image.new('RGB',(672,((len(batch)+2)//3)*504),'#eeeeee')
        draw = ImageDraw.Draw(page)
        for i,entry in enumerate(batch):
            x,y = (i%3)*224,(i//3)*504
            with Image.open(output/entry['image_path']) as original:
                preview = original.copy()
                preview.thumbnail((224,480))
                page.paste(preview,(x+(224-preview.width)//2,y))
            draw.text((x+3,y+482),f"PTS {entry['timestamp_seconds']:.6f}s",fill='black')
        relative = f'contacts/page_{offset//12:04d}.png'
        with (output/relative).open('xb') as handle: page.save(handle,format='PNG')
        paths.append(relative)
    return paths


def prepare_evidence(source: Path, output: Path, *, recording_id: str, times=None):
    if not isinstance(recording_id,str) or not re.fullmatch('[A-Za-z0-9_-]{1,80}',recording_id):
        raise EvidenceError('Use an anonymous ASCII recording ID (1–80 characters).')
    try:
        source = safe_path(source)
        safe_path(output,private=True)
        info = pipeline.inspect_video(source)
        before = file_hash(source)
        origin_pts,origin_base,last = _scan(source)
        targets = default_times(last) if times is None else pipeline._times(times)
        destination = new_output(output)
        report = pipeline.extract_frames(source,targets,destination/'exports')
        w,h = info['width'],info['height']
        dw,dh = (h,w) if info['rotation_degrees'] in (90,270) else (w,h)
        recording = dict(recording_id=recording_id,source_sha256=before,width=w,height=h,
                         duration_seconds=info['duration_seconds'],time_base=_base(origin_base),
                         origin_pts=origin_pts,origin_time_base=_base(origin_base),last_frame_seconds=float(last),
                         rotation_degrees=info['rotation_degrees'],
                         orientation='portrait' if dh>dw else 'landscape' if dw>dh else 'square',perspective='unknown')
        frames = []
        for entry in report['results']:
            tb = Fraction(entry['time_base']) if entry['time_base'] is not None else None
            frames.append(dict(frame_id=frame_id(recording_id,entry['raw_pts'],tb) if tb else None,
                               requested_seconds=entry['requested_time_seconds'],timestamp_seconds=entry['actual_time_seconds'],
                               raw_pts=entry['raw_pts'],time_base=_base(tb) if tb else None,
                               image_path='exports/'+entry['image'] if entry['image'] else None,
                               image_width=entry['output_width'],image_height=entry['output_height'],
                               status=entry['status'],reason=entry['reason']))
        pages = _contacts(destination,frames)
        if file_hash(source) != before: raise EvidenceError('Input integrity changed during preparation.')
        index = dict(schema_version=1,recording=recording,export_report='exports/report.json',
                     frames=frames,contact_pages=pages,status=report['status'])
        write_json(destination/'index.json',index)
        return index
    except (pipeline.VideoError,av.FFmpegError,OSError,ValueError) as exc:
        raise EvidenceError('Local preparation failed; input/output preserved; use a new run.') from exc


def _reference(run, relative):
    if not isinstance(relative,str) or '\\' in relative or ':' in relative or relative.startswith('/'):
        raise EvidenceError('Unsafe index reference.')
    result = safe_path(run/relative,private=True)
    if not result.is_relative_to(run): raise EvidenceError('Index reference escapes supplied run.')
    if not result.is_file(): raise EvidenceError('Missing index reference.')
    return result


def load_indexes(paths):
    """Check explicitly supplied runs and merge true frame identities, never requests."""
    merged = {}
    try:
        for supplied in paths:
            path = safe_path(supplied,private=True)
            index = load_evidence(path)
            if set(index) != {'schema_version','recording','export_report','frames','contact_pages','status'} or type(index['schema_version']) is not int or index['schema_version'] != 1:
                raise EvidenceError('Invalid index fields/version.')
            r = index['recording']
            if not isinstance(r,dict) or set(r)!=set(SCHEMAS['recordings']) or any(not valid_type(r[k],v) for k,v in SCHEMAS['recordings'].items()):
                raise EvidenceError('Invalid index recording.')
            if not isinstance(index['frames'],list) or not isinstance(index['contact_pages'],list) or index['status'] not in {'success','partial'}:
                raise EvidenceError('Invalid index arrays/status.')
            _reference(path.parent,index['export_report'])
            for contact in index['contact_pages']: _reference(path.parent,contact)
            rid = r['recording_id']
            if rid in merged and merged[rid]['recording'] != r: raise EvidenceError('Recording metadata conflict.')
            target = merged.setdefault(rid,dict(recording=r,frames=[]))
            seen = {f['frame_id']:f for f in target['frames'] if f['status']=='success'}
            for f in index['frames']:
                if not isinstance(f,dict) or set(f) != {'frame_id','requested_seconds','timestamp_seconds','raw_pts','time_base','image_path','image_width','image_height','status','reason'}:
                    raise EvidenceError('Invalid index frame fields.')
                if not valid_type(f['requested_seconds'],'seconds') or f['status'] not in {'success','miss','error'}:
                    raise EvidenceError('Invalid index frame status/time.')
                if f['status'] != 'success':
                    if any(f[k] is not None for k in ('image_path','image_width','image_height')):
                        raise EvidenceError('Unsuccessful export has image metadata.')
                    target['frames'].append(f.copy()); continue
                if (type(f['raw_pts']) is not int or not valid_type(f['timestamp_seconds'],'seconds')
                        or not valid_type(f['image_path'],'png') or f['reason'] is not None):
                    raise EvidenceError('Invalid successful export.')
                tb = rational(f['time_base'])
                if f['frame_id'] != frame_id(rid,f['raw_pts'],tb): raise EvidenceError('Unstable frame identity.')
                time = f['raw_pts']*tb-r['origin_pts']*rational(r['origin_time_base'])
                if abs(time-seconds(f['timestamp_seconds'])) > Fraction(1,1000000) or time < 0 or float(time)>r['last_frame_seconds']:
                    raise EvidenceError('Index timestamp conflict.')
                size = (r['height'],r['width']) if r['rotation_degrees'] in (90,270) else (r['width'],r['height'])
                if (f['image_width'],f['image_height']) != size or any(type(f[k]) is not int for k in ('image_width','image_height')):
                    raise EvidenceError('Index dimensions conflict.')
                image_path = _reference(path.parent,f['image_path'])
                with Image.open(image_path) as image:
                    if image.format!='PNG' or image.size!=size: raise EvidenceError('PNG geometry conflict.')
                    pixel_hash = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
                entry = f.copy()
                entry['_content_hash'] = pixel_hash
                entry['_aliases'] = [f['image_path']]
                prior = seen.get(f['frame_id'])
                if prior is not None:
                    identity_fields = ('raw_pts','time_base','timestamp_seconds','image_width','image_height','_content_hash')
                    if any(prior[k]!=entry[k] for k in identity_fields): raise EvidenceError('Duplicate frame metadata/content conflict.')
                    if f['image_path'] not in prior['_aliases']: prior['_aliases'].append(f['image_path'])
                else:
                    target['frames'].append(entry)
                    seen[f['frame_id']] = entry
        return merged
    except (OSError,ValueError,TypeError,KeyError,Image.DecompressionBombError) as exc:
        raise EvidenceError('Cannot load local index/image references.') from exc
