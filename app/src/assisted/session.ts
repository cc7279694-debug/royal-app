import type { AssistedPacket, CandidateOwner } from './contract';
import { AssistedSource } from './import';
import type { AssistedState, CandidateReview } from './review-state';

export interface StoredReview {
  readonly candidateId: string;
  readonly cardId: string | null;
  readonly owner: CandidateOwner;
  readonly timestamp: number;
  readonly status: 'pending' | 'confirmed' | 'excluded';
  readonly decisionSource: 'user_choice' | 'manual' | null;
  readonly isManual: boolean;
}

export interface StoredSession {
  readonly formatVersion: 1;
  readonly sessionId: string;
  readonly revision: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly packetSha256: string;
  readonly packetJson: string;
  readonly reviews: readonly StoredReview[];
}

export interface RestoredSession {
  readonly session: StoredSession;
  readonly state: AssistedState;
}

const packetLimit = 24 * 1024 * 1024;
const envelopeKeys = ['formatVersion', 'sessionId', 'revision', 'createdAt', 'updatedAt', 'packetSha256', 'packetJson', 'reviews'];
const reviewKeys = ['candidateId', 'cardId', 'owner', 'timestamp', 'status', 'decisionSource', 'isManual'];

function invalid(): never { throw new Error('本地审核记录损坏或版本不受支持，原记录已保留。'); }

function record(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return invalid();
  const row = value as Record<string, unknown>;
  if (Object.keys(row).length !== keys.length || !keys.every(key => Object.hasOwn(row, key))) return invalid();
  return row;
}

function validDate(value: unknown): value is string {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value)
    && Number.isFinite(Date.parse(value)) && new Date(value).toISOString() === value;
}

function validateMetadata(session: Record<string, unknown>): void {
  if (session.formatVersion !== 1 || typeof session.sessionId !== 'string'
    || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(session.sessionId)
    || typeof session.revision !== 'number' || !Number.isSafeInteger(session.revision) || session.revision < 1
    || !validDate(session.createdAt) || !validDate(session.updatedAt)
    || session.updatedAt < session.createdAt) return invalid();
}

export async function packetDigest(packetJson: string): Promise<string> {
  const bytes = new TextEncoder().encode(packetJson);
  if (bytes.byteLength === 0 || bytes.byteLength > packetLimit) return invalid();
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
}

function rebuildReviews(packet: AssistedPacket, values: unknown): readonly CandidateReview[] {
  if (!Array.isArray(values) || values.length > 5000 || values.length < packet.candidates.length) return invalid();
  const originals = new Map(packet.candidates.map(candidate => [candidate.candidate_id, candidate]));
  const reviews = new Map<string, CandidateReview>();
  const manuals: CandidateReview[] = [];
  for (const value of values) {
    const row = record(value, reviewKeys);
    if (typeof row.candidateId !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/.test(row.candidateId)
      || reviews.has(row.candidateId) || typeof row.isManual !== 'boolean'
      || (row.cardId !== null && (typeof row.cardId !== 'string' || row.cardId === 'unknown' || !/^[a-z][a-z0-9_]{0,63}$/.test(row.cardId)))
      || (row.owner !== 'own' && row.owner !== 'opponent' && row.owner !== 'unknown')
      || typeof row.timestamp !== 'number' || !Number.isFinite(row.timestamp) || row.timestamp < 0 || row.timestamp > 86400
      || (row.status !== 'pending' && row.status !== 'confirmed' && row.status !== 'excluded')
      || (row.decisionSource !== null && row.decisionSource !== 'manual' && row.decisionSource !== 'user_choice')) return invalid();
    const raw = originals.get(row.candidateId) ?? null;
    if (row.isManual) {
      if (raw !== null || !/^manual:[1-9]\d*$/.test(row.candidateId) || row.decisionSource !== 'manual') return invalid();
    } else {
      if (raw === null || row.timestamp !== raw.timestamp || row.decisionSource === 'manual') return invalid();
      if (row.decisionSource === null && (row.status !== 'pending' || row.cardId !== raw.card_id || row.owner !== raw.owner)) return invalid();
    }
    if (row.status === 'confirmed' && (row.owner !== 'opponent' || row.cardId === null || row.decisionSource === null)) return invalid();
    if (row.status === 'excluded' && row.decisionSource === null) return invalid();
    const review: CandidateReview = Object.freeze({ candidateId: row.candidateId, raw,
      cardId: row.cardId as string | null, owner: row.owner, timestamp: row.timestamp,
      status: row.status, decisionSource: row.decisionSource });
    reviews.set(row.candidateId, review);
    if (row.isManual) manuals.push(review);
  }
  if (packet.candidates.some(candidate => !reviews.has(candidate.candidate_id))) return invalid();
  return Object.freeze([...packet.candidates.map(candidate => reviews.get(candidate.candidate_id)!), ...manuals]);
}

export function serializeReviews(state: AssistedState): readonly StoredReview[] {
  if (!state.packet) return invalid();
  const originals = new Map(state.packet.candidates.map(candidate => [candidate.candidate_id, candidate]));
  const reviews = state.rows.map(row => {
    if (row.raw !== null && row.raw !== originals.get(row.candidateId)) return invalid();
    return Object.freeze({ candidateId: row.candidateId, cardId: row.cardId, owner: row.owner,
      timestamp: row.timestamp, status: row.status, decisionSource: row.decisionSource, isManual: row.raw === null });
  });
  rebuildReviews(state.packet, reviews);
  return Object.freeze(reviews);
}

export async function createStoredSession(state: AssistedState, sessionId: string, now: string): Promise<StoredSession> {
  if (!state.packet) return invalid();
  const packetJson = JSON.stringify(state.packet);
  const session: StoredSession = { formatVersion: 1, sessionId, revision: 1, createdAt: now, updatedAt: now,
    packetSha256: await packetDigest(packetJson), packetJson, reviews: serializeReviews(state) };
  validateMetadata(record(session, envelopeKeys));
  return Object.freeze(session);
}

export function updateStoredSession(current: StoredSession, state: AssistedState, updatedAt: string): StoredSession {
  if (!state.packet || JSON.stringify(state.packet) !== current.packetJson
    || !validDate(updatedAt) || updatedAt < current.updatedAt) return invalid();
  const session = Object.freeze({ ...current, revision: current.revision + 1, updatedAt, reviews: serializeReviews(state) });
  validateMetadata(record(session, envelopeKeys));
  return session;
}

export async function restoreStoredSession(payload: unknown): Promise<RestoredSession> {
  const envelope = record(payload, envelopeKeys);
  validateMetadata(envelope);
  if (typeof envelope.packetJson !== 'string' || envelope.packetJson.length > packetLimit
    || typeof envelope.packetSha256 !== 'string' || !/^[a-f0-9]{64}$/.test(envelope.packetSha256)
    || await packetDigest(envelope.packetJson) !== envelope.packetSha256) return invalid();
  const packet = await AssistedSource.fromJSON(JSON.parse(envelope.packetJson));
  const state: AssistedState = Object.freeze({ packet, rows: rebuildReviews(packet, envelope.reviews), error: null });
  const session: StoredSession = Object.freeze({ formatVersion: 1, sessionId: envelope.sessionId as string,
    revision: envelope.revision as number, createdAt: envelope.createdAt as string, updatedAt: envelope.updatedAt as string,
    packetJson: envelope.packetJson, packetSha256: envelope.packetSha256, reviews: serializeReviews(state) });
  return Object.freeze({ session, state });
}
