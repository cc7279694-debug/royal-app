import { createHash } from 'node:crypto';
import { expect, it } from 'vitest';
import { AssistedSource } from './import';
import { assistedReducer, createAssistedState, getConfirmedDiscovery } from './review-state';
import { createStoredSession, restoreStoredSession } from './session';
import type { StoredSession } from './session';
import { makePacket, syntheticJpeg } from './test-fixture';

const sessionId = '12345678-1234-4234-8234-123456789abc';
const now = '2026-10-11T00:00:00.000Z';

async function fixture() {
  const payload = makePacket();
  const cards = ['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions', 'royal_hogs'];
  payload.candidates = cards.map((cardId, index) => ({ ...payload.candidates[0]!,
    candidate_id: `candidate-${index + 1}`, card_id: cardId, timestamp: index + 1, confirmed_at: index + 1.5 }));
  payload.summary.total_match_candidates = 8;
  payload.summary.exported_candidates = 6;
  return createAssistedState(await AssistedSource.fromJSON(payload));
}

async function pendingSession() { return createStoredSession(await fixture(), sessionId, now); }
function withPacket(session: StoredSession, mutate: (packet: ReturnType<typeof makePacket>) => void) {
  const packet = JSON.parse(session.packetJson) as ReturnType<typeof makePacket>;
  mutate(packet);
  const packetJson = JSON.stringify(packet);
  return { ...session, packetJson, packetSha256: createHash('sha256').update(packetJson).digest('hex') };
}

it('recovers five confirmed slots, repeated rows, screenshots and separate manual/pending choices', async () => {
  let state = await fixture();
  for (let id = 1; id <= 6; id++) state = assistedReducer(state, { type: 'confirm', candidateId: `candidate-${id}` });
  state = assistedReducer(state, { type: 'manual', cardId: null, owner: 'unknown', timestamp: 20 });
  const restored = await restoreStoredSession(await createStoredSession(state, sessionId, now));
  expect(getConfirmedDiscovery(restored.state).cardIds).toEqual(['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions']);
  expect(restored.state.rows).toHaveLength(7);
  expect(restored.state.rows[5]?.cardId).toBe('royal_hogs');
  expect(restored.state.rows[6]).toMatchObject({ raw: null, status: 'pending', decisionSource: 'manual', cardId: null });
  expect(restored.state.packet?.evidence[0]?.image_data_url).toBe(`data:image/jpeg;base64,${syntheticJpeg}`);
  expect(restored.state.packet?.evidence[0]?.raw_pts).toBe(1000);
  expect(restored.state.packet?.provenance.event_gt_used_as_input).toBe(false);
});

it('recovers exclusion and correction while rebuilding immutable raw prediction and timestamp', async () => {
  let state = await fixture();
  state = assistedReducer(state, { type: 'exclude', candidateId: 'candidate-1' });
  state = assistedReducer(state, { type: 'correct', candidateId: 'candidate-2', cardId: 'firecracker', owner: 'opponent' });
  state = assistedReducer(state, { type: 'confirm', candidateId: 'candidate-2' });
  state = assistedReducer(state, { type: 'pending', candidateId: 'candidate-2' });
  const restored = await restoreStoredSession(await createStoredSession(state, sessionId, now));
  expect(restored.state.rows[0]?.status).toBe('excluded');
  expect(restored.state.rows[1]).toMatchObject({ cardId: 'firecracker', timestamp: 2, status: 'pending', decisionSource: 'user_choice' });
  expect(restored.state.rows[1]?.raw?.card_id).toBe('royal_hogs');
  expect(Object.isFrozen(restored.state.rows[1]?.raw)).toBe(true);
  expect(getConfirmedDiscovery(restored.state).cardIds).toEqual([]);
});

it.each([
  ['future version', (s: StoredSession) => ({ ...s, formatVersion: 2 })],
  ['unknown envelope field', (s: StoredSession) => ({ ...s, extra: true })],
  ['invalid UUID', (s: StoredSession) => ({ ...s, sessionId: 'session' })],
  ['zero revision', (s: StoredSession) => ({ ...s, revision: 0 })],
  ['unsafe revision', (s: StoredSession) => ({ ...s, revision: Number.MAX_SAFE_INTEGER + 1 })],
  ['noncanonical date', (s: StoredSession) => ({ ...s, createdAt: '2026-10-11' })],
  ['backwards date', (s: StoredSession) => ({ ...s, updatedAt: '2026-10-10T00:00:00.000Z' })],
  ['mismatched digest', (s: StoredSession) => ({ ...s, packetSha256: 'f'.repeat(64) })],
  ['missing row', (s: StoredSession) => ({ ...s, reviews: s.reviews.slice(1) })],
  ['duplicate row', (s: StoredSession) => ({ ...s, reviews: [...s.reviews, s.reviews[0]] })],
  ['unknown row', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], candidateId: 'missing' }, ...s.reviews.slice(1)] })],
  ['raw injection', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], raw: {} }, ...s.reviews.slice(1)] })],
  ['changed source time', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], timestamp: 2 }, ...s.reviews.slice(1)] })],
  ['changed pending without decision', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], cardId: 'firecracker' }, ...s.reviews.slice(1)] })],
  ['manual marking of original', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], isManual: true, decisionSource: 'manual' }, ...s.reviews.slice(1)] })],
  ['unreviewed confirmation', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], status: 'confirmed' }, ...s.reviews.slice(1)] })],
  ['own confirmation', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], owner: 'own', status: 'confirmed', decisionSource: 'user_choice' }, ...s.reviews.slice(1)] })],
  ['unknown card confirmation', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], cardId: null, status: 'confirmed', decisionSource: 'user_choice' }, ...s.reviews.slice(1)] })],
  ['unknown sentinel', (s: StoredSession) => ({ ...s, reviews: [{ ...s.reviews[0], cardId: 'unknown', decisionSource: 'user_choice' }, ...s.reviews.slice(1)] })],
  ['oversized review set', (s: StoredSession) => ({ ...s, reviews: Array.from({ length: 5001 }, () => s.reviews[0]) })],
  ['oversized packet', (s: StoredSession) => ({ ...s, packetJson: ' '.repeat(24 * 1024 * 1024 + 1) })],
] as const)('rejects %s instead of producing a partially recovered audit', async (_name, mutate) => {
  const rejected = await restoreStoredSession(mutate(await pendingSession())).then(() => false, () => true);
  expect(rejected).toBe(true);
});

it('revalidates screenshot content and native dimensions even when the outer packet digest matches', async () => {
  const session = await pendingSession();
  await expect(restoreStoredSession(withPacket(session, packet => { packet.evidence[0]!.image_sha256 = 'a'.repeat(64); }))).rejects.toThrow();
  await expect(restoreStoredSession(withPacket(session, packet => { packet.evidence[0]!.source_width = 2; }))).rejects.toThrow();
});

it('uses explicit manual identity when a valid source candidate ID has a manual prefix', async () => {
  const payload = makePacket();
  payload.candidates[0]!.candidate_id = 'manual:2';
  let state = createAssistedState(await AssistedSource.fromJSON(payload));
  state = assistedReducer(state, { type: 'manual', cardId: 'firecracker', owner: 'opponent', timestamp: 4 });
  state = assistedReducer(state, { type: 'confirm', candidateId: 'manual:3' });
  const restored = await restoreStoredSession(await createStoredSession(state, sessionId, now));
  expect(restored.state.rows[0]?.raw?.candidate_id).toBe('manual:2');
  expect(restored.state.rows[1]).toMatchObject({ candidateId: 'manual:3', raw: null, cardId: 'firecracker', status: 'confirmed' });
  expect(getConfirmedDiscovery(restored.state).cardIds).toEqual(['firecracker']);
});

it('binds the packet digest to UTF-8 bytes while preserving non-ASCII source explanations', async () => {
  const payload = makePacket(); payload.candidates[0]!.reason = '本地未验证预测';
  const session = await createStoredSession(createAssistedState(await AssistedSource.fromJSON(payload)), sessionId, now);
  expect(session.packetSha256).toBe(createHash('sha256').update(session.packetJson, 'utf8').digest('hex'));
  const restored = await restoreStoredSession(session);
  expect(restored.state.rows[0]?.raw?.reason).toBe('本地未验证预测');
});
