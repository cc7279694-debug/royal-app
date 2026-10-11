import { expect, it } from 'vitest';
import { AssistedSource } from './import';
import { assistedReducer, createAssistedState, getConfirmedDiscovery } from './review-state';
import { makePacket } from './test-fixture';

async function loaded() { return createAssistedState(await AssistedSource.fromJSON(makePacket())); }

it('loads every detector candidate pending and never enters the confirmed deck on import', async () => {
  const state = await loaded();
  expect(state.rows[0]?.status).toBe('pending');
  expect(state.rows[0]?.decisionSource).toBeNull();
  expect(getConfirmedDiscovery(state)).toEqual({ cardIds: [], overflowCardIds: [] });
});

it('confirms only an explicit opponent card and keeps the original prediction', async () => {
  const state = assistedReducer(await loaded(), { type: 'confirm', candidateId: 'candidate-a' });
  expect(getConfirmedDiscovery(state).cardIds).toEqual(['witch']);
  expect(state.rows[0]?.decisionSource).toBe('user_choice');
  expect(state.rows[0]?.raw?.card_id).toBe('witch');
});

it('removes corrected or excluded decisions immediately and requires a fresh confirmation', async () => {
  const confirmed = assistedReducer(await loaded(), { type: 'confirm', candidateId: 'candidate-a' });
  const corrected = assistedReducer(confirmed, { type: 'correct', candidateId: 'candidate-a', cardId: 'firecracker', owner: 'opponent' });
  expect(getConfirmedDiscovery(corrected).cardIds).toEqual([]);
  expect(corrected.rows[0]?.raw?.card_id).toBe('witch');
  const again = assistedReducer(corrected, { type: 'confirm', candidateId: 'candidate-a' });
  expect(getConfirmedDiscovery(again).cardIds).toEqual(['firecracker']);
  expect(getConfirmedDiscovery(assistedReducer(again, { type: 'exclude', candidateId: 'candidate-a' })).cardIds).toEqual([]);
});

it.each(['own', 'unknown'] as const)('never confirms %s ownership', async owner => {
  const corrected = assistedReducer(await loaded(), { type: 'correct', candidateId: 'candidate-a', cardId: 'witch', owner });
  const state = assistedReducer(corrected, { type: 'confirm', candidateId: 'candidate-a' });
  expect(state.rows[0]?.status).toBe('pending');
  expect(state.error).not.toBeNull();
  expect(getConfirmedDiscovery(state).cardIds).toEqual([]);
});

it('retains unknown manual additions for review without treating them as a card', async () => {
  const state = assistedReducer(await loaded(), { type: 'manual', cardId: null, owner: 'unknown', timestamp: 2 });
  expect(state.rows[1]?.decisionSource).toBe('manual');
  expect(state.rows[1]?.raw).toBeNull();
  const confirmation = assistedReducer(state, { type: 'confirm', candidateId: state.rows[1]!.candidateId });
  expect(getConfirmedDiscovery(confirmation).cardIds).toEqual([]);
});

it('deduplicates confirmed cards while retaining repeated manual candidate records', async () => {
  let state = assistedReducer(await loaded(), { type: 'confirm', candidateId: 'candidate-a' });
  state = assistedReducer(state, { type: 'manual', cardId: ' Witch ', owner: 'opponent', timestamp: 5 });
  state = assistedReducer(state, { type: 'confirm', candidateId: state.rows[1]!.candidateId });
  expect(state.rows).toHaveLength(2);
  expect(getConfirmedDiscovery(state).cardIds).toEqual(['witch']);
  expect(state.rows[1]?.decisionSource).toBe('manual');
});

it('rejects unknown sentinel IDs, markup, invalid times and stale row IDs without modifying accepted rows', async () => {
  const initial = assistedReducer(await loaded(), { type: 'confirm', candidateId: 'candidate-a' });
  for (const cardId of ['unknown', '<script>', 'a'.repeat(65)]) {
    const state = assistedReducer(initial, { type: 'manual', cardId, owner: 'opponent', timestamp: 2 });
    expect(state.rows).toEqual(initial.rows);
    expect(state.error).not.toBeNull();
  }
  expect(assistedReducer(initial, { type: 'manual', cardId: 'witch', owner: 'opponent', timestamp: -1 }).rows).toEqual(initial.rows);
  expect(assistedReducer(initial, { type: 'confirm', candidateId: 'missing' }).rows).toEqual(initial.rows);
});

it('caps confirmed visible cards at eight while retaining overflow and resets reviews on reimport', async () => {
  let state = await loaded();
  for (let i = 1; i <= 10; i++) {
    state = assistedReducer(state, { type: 'manual', cardId: `card_${i}`, owner: 'opponent', timestamp: i });
    state = assistedReducer(state, { type: 'confirm', candidateId: state.rows.at(-1)!.candidateId });
  }
  expect(getConfirmedDiscovery(state)).toEqual({ cardIds: ['card_1', 'card_2', 'card_3', 'card_4', 'card_5', 'card_6', 'card_7', 'card_8'], overflowCardIds: ['card_9', 'card_10'] });
  const reimported = assistedReducer(state, { type: 'load', packet: state.packet! });
  expect(reimported.rows).toHaveLength(1);
  expect(getConfirmedDiscovery(reimported).cardIds).toEqual([]);
  expect(assistedReducer(state, { type: 'reset' }).packet).toBeNull();
});
