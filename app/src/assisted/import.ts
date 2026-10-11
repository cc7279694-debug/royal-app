import type { AssistedCandidate, AssistedEvidence, AssistedPacket, CandidateOwner, SourceBBox } from './contract';

const hashPattern = /^[a-f0-9]{64}$/;
const idPattern = /^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/;
const cardPattern = /^[a-z][a-z0-9_]{0,63}$/;
const detectorCards = new Set(['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions']);
const fileLimit = 24 * 1024 * 1024;
const imageLimit = 512 * 1024;

function invalid(): never { throw new Error('Invalid offline assisted packet'); }

function object(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return invalid();
  const record = value as Record<string, unknown>;
  if (Object.keys(record).length !== keys.length || !keys.every(key => Object.hasOwn(record, key))) return invalid();
  return record;
}

function text(value: unknown, max = 2048): string {
  if (typeof value !== 'string' || value.length === 0 || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value)) return invalid();
  return value;
}

function id(value: unknown): string {
  const valueText = text(value, 128);
  if (!idPattern.test(valueText)) return invalid();
  return valueText;
}

function hash(value: unknown): string {
  const valueText = text(value, 64);
  if (!hashPattern.test(valueText)) return invalid();
  return valueText;
}

function count(value: unknown, max = 1_000_000): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0 || value > max) return invalid();
  return value;
}

function time(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 86400) return invalid();
  return value;
}

function array(value: unknown, max: number, nonempty = false): unknown[] {
  if (!Array.isArray(value) || value.length > max || (nonempty && value.length === 0)) return invalid();
  return value as unknown[];
}

function ids(value: unknown, max: number, nonempty = false): readonly string[] {
  const values = array(value, max, nonempty).map(item => id(item));
  if (new Set(values).size !== values.length) return invalid();
  return Object.freeze(values);
}

function owner(value: unknown): CandidateOwner {
  if (value !== 'own' && value !== 'opponent' && value !== 'unknown') return invalid();
  return value;
}

function candidate(value: unknown): AssistedCandidate {
  const row = object(value, ['candidate_id', 'card_id', 'owner', 'timestamp', 'confirmed_at', 'confidence',
    'evidence_level', 'kind', 'source_observation_ids', 'source_appearance_groups', 'evidence_ids', 'reason']);
  const timestamp = time(row.timestamp);
  const confirmedAt = row.confirmed_at === null ? null : time(row.confirmed_at);
  const confidence = row.confidence;
  const cardId = row.card_id;
  if (confirmedAt !== null && confirmedAt < timestamp) return invalid();
  if (confidence !== null && (typeof confidence !== 'number' || !Number.isFinite(confidence) || confidence < 0 || confidence > 1)) return invalid();
  if (cardId !== null && (typeof cardId !== 'string' || !cardPattern.test(cardId) || !detectorCards.has(cardId))) return invalid();
  if (row.evidence_level !== 'STRONG' && row.evidence_level !== 'MEDIUM' && row.evidence_level !== 'WEAK') return invalid();
  if (row.kind !== null && row.kind !== 'direct' && row.kind !== 'grouped') return invalid();
  return Object.freeze({ candidate_id: id(row.candidate_id), card_id: cardId, owner: owner(row.owner),
    timestamp, confirmed_at: confirmedAt, confidence, evidence_level: row.evidence_level, kind: row.kind,
    source_observation_ids: ids(row.source_observation_ids, 1000, true),
    source_appearance_groups: ids(row.source_appearance_groups, 1000), evidence_ids: ids(row.evidence_ids, 3, true),
    reason: text(row.reason) });
}

function jpegDimensions(bytes: Uint8Array): readonly [number, number] {
  if (bytes.length < 12 || bytes[0] !== 0xff || bytes[1] !== 0xd8
    || bytes.at(-2) !== 0xff || bytes.at(-1) !== 0xd9) return invalid();
  let offset = 2;
  while (offset + 4 < bytes.length) {
    if (bytes[offset++] !== 0xff) return invalid();
    while (bytes[offset] === 0xff) offset++;
    const marker = bytes[offset++];
    if (marker === undefined || marker === 0xda || marker === 0xd9) return invalid();
    const length = (bytes[offset]! << 8) | bytes[offset + 1]!;
    if (length < 2 || offset + length > bytes.length) return invalid();
    if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
      if (length < 8) return invalid();
      return [(bytes[offset + 5]! << 8) | bytes[offset + 6]!, (bytes[offset + 3]! << 8) | bytes[offset + 4]!];
    }
    offset += length;
  }
  return invalid();
}

async function evidence(value: unknown): Promise<AssistedEvidence> {
  const row = object(value, ['evidence_id', 'frame_id', 'timestamp', 'raw_pts', 'time_base', 'source_width',
    'source_height', 'bboxes', 'image_data_url', 'image_sha256']);
  const width = count(row.source_width, 8192);
  const height = count(row.source_height, 8192);
  if (!width || !height || width * height > 24_000_000 || typeof row.raw_pts !== 'number' || !Number.isSafeInteger(row.raw_pts)) return invalid();
  const timeBase = text(row.time_base, 40);
  if (!/^[1-9]\d*\/[1-9]\d*$/.test(timeBase) || !timeBase.split('/').every(part => Number.isSafeInteger(Number(part)))) return invalid();
  const boxes = array(row.bboxes, 1000, true).map(valueBox => {
    const box = array(valueBox, 4);
    if (box.length !== 4 || !box.every(coordinate => typeof coordinate === 'number' && Number.isFinite(coordinate))) return invalid();
    const [x1, y1, x2, y2] = box as [number, number, number, number];
    if (x1 < 0 || y1 < 0 || x2 <= x1 || y2 <= y1 || x2 > width || y2 > height) return invalid();
    return Object.freeze([x1, y1, x2, y2]) as SourceBBox;
  });
  const dataUrl = text(row.image_data_url, Math.ceil(imageLimit / 3) * 4 + 32);
  const prefix = 'data:image/jpeg;base64,';
  if (!dataUrl.startsWith(prefix)) return invalid();
  const encoded = dataUrl.slice(prefix.length);
  if (!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded)) return invalid();
  const decoded = atob(encoded);
  if (!decoded.length || decoded.length > imageLimit || btoa(decoded) !== encoded) return invalid();
  const bytes = Uint8Array.from(decoded, char => char.charCodeAt(0));
  const [jpegWidth, jpegHeight] = jpegDimensions(bytes);
  if (jpegWidth !== width || jpegHeight !== height) return invalid();
  const imageHash = hash(row.image_sha256);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  if (Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('') !== imageHash) return invalid();
  return Object.freeze({ evidence_id: id(row.evidence_id), frame_id: id(row.frame_id), timestamp: time(row.timestamp),
    raw_pts: row.raw_pts, time_base: timeBase, source_width: width, source_height: height,
    bboxes: Object.freeze(boxes), image_data_url: dataUrl, image_sha256: imageHash });
}

export class AssistedSource {
  static async fromJSON(payload: unknown): Promise<AssistedPacket> {
    const packet = object(payload, ['schema', 'packet_id', 'match_id', 'provenance', 'candidates', 'evidence', 'summary']);
    if (packet.schema !== 'offline_assisted_candidates_v1') return invalid();
    const source = object(packet.provenance, ['recording_sha256', 'prediction_sha256', 'config_sha256', 'replay_sha256',
      'engine_rule_version', 'input_source', 'event_gt_used_as_input']);
    if (source.input_source !== 'katacr_prediction' || source.event_gt_used_as_input !== false) return invalid();
    const candidates = array(packet.candidates, 5000, true).map(candidate);
    if (new Set(candidates.map(row => row.candidate_id)).size !== candidates.length) return invalid();
    const screenshots: AssistedEvidence[] = [];
    for (const input of array(packet.evidence, 128, true)) screenshots.push(await evidence(input));
    const screenshotIds = new Set(screenshots.map(row => row.evidence_id));
    if (screenshotIds.size !== screenshots.length || new Set(screenshots.map(row => row.frame_id)).size !== screenshots.length) return invalid();
    const referenced = new Set(candidates.flatMap(row => [...row.evidence_ids]));
    if (referenced.size !== screenshotIds.size || [...referenced].some(evidenceId => !screenshotIds.has(evidenceId))) return invalid();
    const summary = object(packet.summary, ['total_match_candidates', 'exported_candidates', 'excluded_candidates', 'exclusion_reasons',
      'raw_candidate_inventory_sha256', 'evidence_frame_selection', 'confidence_semantics', 'image_display_semantics', 'coverage_semantics']);
    const exclusions = object(summary.exclusion_reasons, ['owner_guard', 'unsupported_card', 'insufficient_evidence']);
    const total = count(summary.total_match_candidates);
    const exported = count(summary.exported_candidates);
    const excluded = count(summary.excluded_candidates);
    const ownerGuard = count(exclusions.owner_guard);
    const unsupportedCard = count(exclusions.unsupported_card);
    const insufficient = count(exclusions.insufficient_evidence);
    if (exported !== candidates.length || total !== exported + excluded || excluded !== ownerGuard + unsupportedCard + insufficient
      || summary.evidence_frame_selection !== 'first_middle_last_of_candidate_observations') return invalid();
    return Object.freeze({ schema: 'offline_assisted_candidates_v1', packet_id: id(packet.packet_id), match_id: id(packet.match_id),
      provenance: Object.freeze({ recording_sha256: hash(source.recording_sha256), prediction_sha256: hash(source.prediction_sha256),
        config_sha256: hash(source.config_sha256), replay_sha256: hash(source.replay_sha256), engine_rule_version: text(source.engine_rule_version, 128),
        input_source: 'katacr_prediction', event_gt_used_as_input: false }), candidates: Object.freeze(candidates), evidence: Object.freeze(screenshots),
      summary: Object.freeze({ total_match_candidates: total, exported_candidates: exported, excluded_candidates: excluded,
        exclusion_reasons: Object.freeze({ owner_guard: ownerGuard, unsupported_card: unsupportedCard, insufficient_evidence: insufficient }),
        raw_candidate_inventory_sha256: hash(summary.raw_candidate_inventory_sha256), evidence_frame_selection: 'first_middle_last_of_candidate_observations',
        confidence_semantics: text(summary.confidence_semantics), image_display_semantics: text(summary.image_display_semantics), coverage_semantics: text(summary.coverage_semantics) }) });
  }

  static async fromFile(file: File): Promise<AssistedPacket> {
    if (file.size === 0 || file.size > fileLimit) return invalid();
    return this.fromJSON(JSON.parse((await file.text()).replace(/^\uFEFF/, '')));
  }
}
