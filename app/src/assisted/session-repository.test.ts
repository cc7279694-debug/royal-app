import { expect, it } from 'vitest';
import { AssistedSource } from './import';
import { assistedReducer, createAssistedState, getConfirmedDiscovery } from './review-state';
import { createStoredSession } from './session';
import type { StoredSession } from './session';
import { AssistedSessionRepository, SessionStoreError } from './session-repository';
import type { ReplaceSessionInput, SaveSessionInput, SessionStore } from './session-repository';
import { makePacket } from './test-fixture';
import { isStrictJsonValue } from './indexeddb-store';

// The fault boundary is the external transaction, not the domain or repository.
class TransactionStore implements SessionStore {
  value: StoredSession | null = null;
  fault: 'load' | 'replace' | 'save' | null = null;
  async load() { if (this.fault === 'load') throw new Error('disk read failed'); return this.value; }
  async replace(input: ReplaceSessionInput) {
    if (this.fault === 'replace') throw new Error('disk commit failed');
    if ((this.value?.sessionId ?? null) !== input.expectedSessionId || (this.value?.revision ?? null) !== input.expectedRevision)
      throw new SessionStoreError('CONFLICT', 'stale session');
    this.value = structuredClone(input.session);
  }
  async save(input: SaveSessionInput) {
    if (this.fault === 'save') throw new Error('disk commit failed');
    if (this.value?.sessionId !== input.sessionId || this.value.revision !== input.expectedRevision)
      throw new SessionStoreError('CONFLICT', 'stale revision');
    this.value = structuredClone({ ...this.value, revision: input.revision, updatedAt: input.updatedAt, reviews: input.reviews });
  }
}

async function fixture() {
  const state = createAssistedState(await AssistedSource.fromJSON(makePacket()));
  const session = await createStoredSession(state, '12345678-1234-4234-8234-123456789abc', '2026-10-11T00:00:00.000Z');
  const store = new TransactionStore();
  return { state, session, store, repository: new AssistedSessionRepository(store) };
}

it('saves only mutable reviews and restores a source-bound audit through the repository', async () => {
  const { repository, store, state, session } = await fixture();
  await repository.replace(session, null);
  const saved = await repository.save(session, assistedReducer(state, { type: 'confirm', candidateId: 'candidate-a' }), '2026-10-11T00:00:01.000Z');
  expect(saved.revision).toBe(2);
  expect(store.value?.packetJson).toBe(session.packetJson);
  expect(store.value?.packetSha256).toBe(session.packetSha256);
  expect(getConfirmedDiscovery((await repository.load())!.state).cardIds).toEqual(['witch']);
});

it('rejects stale edits instead of overwriting a newer committed review', async () => {
  const { repository, state, session } = await fixture();
  await repository.replace(session, null);
  await repository.save(session, assistedReducer(state, { type: 'confirm', candidateId: 'candidate-a' }), '2026-10-11T00:00:01.000Z');
  await expect(repository.save(session, assistedReducer(state, { type: 'exclude', candidateId: 'candidate-a' }), '2026-10-11T00:00:02.000Z')).rejects.toThrow('stale');
  expect((await repository.load())?.state.rows[0]?.status).toBe('confirmed');
});

it('protects existing sessions from unconditioned or stale replacement', async () => {
  const { repository, state, session } = await fixture();
  await repository.replace(session, null);
  const replacement = await createStoredSession(state, '87654321-4321-4321-8321-cba987654321', '2026-10-11T00:00:01.000Z');
  await expect(repository.replace(replacement, null)).rejects.toThrow('stale');
  await repository.replace(replacement, session);
  expect((await repository.load())?.session.sessionId).toBe('87654321-4321-4321-8321-cba987654321');
});

it('preserves the prior audit when saving or replacing fails', async () => {
  const { repository, store, state, session } = await fixture();
  await repository.replace(session, null);
  store.fault = 'save';
  await expect(repository.save(session, assistedReducer(state, { type: 'confirm', candidateId: 'candidate-a' }), '2026-10-11T00:00:01.000Z')).rejects.toThrow('commit');
  store.fault = 'replace';
  await expect(repository.replace(session, session)).rejects.toThrow('commit');
  store.fault = null;
  expect((await repository.load())?.session.revision).toBe(1);
  expect((await repository.load())?.state.rows[0]?.status).toBe('pending');
});

it('reports read errors and corruption instead of treating them as an empty database', async () => {
  const { repository, store, session } = await fixture();
  store.fault = 'load';
  await expect(repository.load()).rejects.toThrow('read');
  store.fault = null;
  store.value = { ...session, reviews: [] };
  await expect(repository.load()).rejects.toThrow();
  expect(store.value.reviews).toEqual([]);
});

it('rejects packet replacement and invalid metadata through the review-save path', async () => {
  const { repository, session } = await fixture();
  await repository.replace(session, null);
  const different = makePacket(); different.match_id = 'different-match';
  const state = createAssistedState(await AssistedSource.fromJSON(different));
  await expect(repository.save(session, state, '2026-10-11T00:00:01.000Z')).rejects.toThrow();
  await expect(repository.save(session, state, 'not-a-date')).rejects.toThrow();
  expect((await repository.load())?.state.packet?.match_id).toBe('match-test');
});

it.each([
  ['NaN', { decisionSource: NaN }],
  ['Infinity', { decisionSource: Infinity }],
  ['undefined', { decisionSource: undefined }],
  ['Date', { updatedAt: new Date('2026-10-11T00:00:00.000Z') }],
  ['boxed string', { updatedAt: new String('2026-10-11T00:00:00.000Z') }],
  ['sparse array', { reviews: new Array(1) }],
  ['ignored array property', { reviews: Object.assign([], { hidden: true }) }],
  ['non-plain object', { reviews: new Map() }],
] as const)('rejects %s before JSON equality can disguise durable corruption', (_label, value) => {
  expect(isStrictJsonValue(value)).toBe(false);
});

it('allows complete JSON session primitives without losing nullable review fields', () => {
  expect(isStrictJsonValue({ formatVersion: 1, reviews: [{ decisionSource: null, timestamp: 1.5,
    candidateId: 'candidate-a', isManual: false, cardId: null, owner: 'unknown', status: 'pending' }],
    createdAt: '2026-10-11T00:00:00.000Z', packetJson: '{"source": "本地"}' })).toBe(true);
});
