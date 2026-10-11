import { expect, it } from 'vitest';
import { AssistedSource } from './import';
import { getConfirmedDiscovery } from './review-state';
import { AssistedSessionController } from './session-controller';
import { AssistedSessionRepository, SessionStoreError } from './session-repository';
import type { ReplaceSessionInput, SaveSessionInput, SessionStore } from './session-repository';
import type { StoredSession } from './session';
import { makePacket } from './test-fixture';

class TransactionStore implements SessionStore {
  value: StoredSession | null = null;
  fault: 'load' | 'replace' | 'save' | null = null;
  reads = 0;
  saveGate: (() => Promise<void>) | null = null;
  async load() { this.reads++; if (this.fault === 'load') throw new Error('read failure'); return structuredClone(this.value); }
  async replace(input: ReplaceSessionInput) {
    if (this.fault === 'replace') throw new Error('replace failure');
    if ((this.value?.sessionId ?? null) !== input.expectedSessionId || (this.value?.revision ?? null) !== input.expectedRevision)
      throw new SessionStoreError('CONFLICT', 'stale replacement');
    this.value = structuredClone(input.session);
  }
  async save(input: SaveSessionInput) {
    if (this.saveGate) await this.saveGate();
    if (this.fault === 'save') throw new Error('save failure');
    if (this.value?.sessionId !== input.sessionId || this.value.revision !== input.expectedRevision)
      throw new SessionStoreError('CONFLICT', 'stale revision');
    this.value = structuredClone({ ...this.value, revision: input.revision, updatedAt: input.updatedAt, reviews: input.reviews });
  }
}

async function fixture(store = new TransactionStore()) {
  let sequence = 0;
  const controller = new AssistedSessionController(new AssistedSessionRepository(store), {
    now: () => `2026-10-11T00:00:${String(sequence).padStart(2, '0')}.000Z`,
    uuid: () => `12345678-1234-4234-8234-${String(++sequence).padStart(12, '0')}`,
  });
  const packet = await AssistedSource.fromJSON(makePacket());
  return { controller, store, packet };
}

it('initializes once across repeated subscribers and restores saved choices after recreation', async () => {
  const { controller, store, packet } = await fixture();
  const first = controller.initialize();
  const second = controller.initialize();
  expect(first === second).toBe(true);
  await first;
  expect(store.reads).toBe(1);
  await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  const reopened = (await fixture(store)).controller;
  await reopened.initialize();
  expect(reopened.getSnapshot().phase).toBe('ready');
  expect(getConfirmedDiscovery(reopened.getSnapshot().state).cardIds).toEqual(['witch']);
  expect(reopened.getSnapshot().revision).toBe(2);
});

it('blocks imports and edits after a read failure until an explicit successful reload', async () => {
  const { controller, store, packet } = await fixture();
  store.fault = 'load';
  await controller.initialize();
  expect(controller.getSnapshot()).toMatchObject({ phase: 'error', sessionId: null });
  expect(controller.getSnapshot().error).not.toBeNull();
  await controller.initialize();
  expect(store.reads).toBe(1);
  await controller.importPacket(packet);
  expect(store.value).toBeNull();
  store.fault = null;
  await controller.retryRestore();
  await controller.importPacket(packet);
  expect(store.value?.reviews[0]?.status).toBe('pending');
});

it('publishes committed review state only after the transaction settles and serializes edits', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  expect(controller.getSnapshot().phase).toBe('ready');
  let release: () => void = () => {};
  const gate = new Promise<void>(resolve => { release = resolve; });
  let started: () => void = () => {};
  const atStorage = new Promise<void>(resolve => { started = resolve; });
  store.saveGate = () => { started(); return gate; };
  const confirmation = controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  await atStorage;
  const exclusion = controller.applyAction({ type: 'exclude', candidateId: 'candidate-a' });
  expect(controller.getSnapshot().phase).toBe('saving');
  expect(getConfirmedDiscovery(controller.getSnapshot().state).cardIds).toEqual([]);
  expect(store.value?.reviews[0]?.status).toBe('pending');
  release(); await confirmation; await exclusion;
  expect(controller.getSnapshot().revision).toBe(3);
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('excluded');
  expect(store.value?.reviews[0]?.status).toBe('excluded');
});

it('keeps confirmed cards visible after a save failure then reloads the last committed audit', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  store.fault = 'save';
  await controller.applyAction({ type: 'exclude', candidateId: 'candidate-a' });
  expect(controller.getSnapshot().phase).toBe('error');
  expect(controller.getSnapshot().revision).toBe(2);
  expect(getConfirmedDiscovery(controller.getSnapshot().state).cardIds).toEqual(['witch']);
  store.fault = null;
  await controller.retryRestore();
  expect(controller.getSnapshot().phase).toBe('ready');
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('confirmed');
});

it('keeps packet and reviews when replacement or restart fails', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  const originalId = controller.getSnapshot().sessionId;
  const different = makePacket(); different.match_id = 'different';
  store.fault = 'replace';
  await controller.importPacket(await AssistedSource.fromJSON(different));
  expect(controller.getSnapshot().sessionId).toBe(originalId);
  expect(controller.getSnapshot().state.packet?.match_id).toBe('match-test');
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('confirmed');
  store.fault = null; await controller.retryRestore(); store.fault = 'replace';
  await controller.restart();
  expect(controller.getSnapshot().phase).toBe('error');
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('confirmed');
});

it('restarts reviews as a new revision-one session without deleting the packet', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  await controller.applyAction({ type: 'manual', cardId: 'firecracker', owner: 'opponent', timestamp: 4 });
  const originalId = controller.getSnapshot().sessionId;
  const originalJson = store.value?.packetJson;
  await controller.restart();
  expect(controller.getSnapshot().sessionId).not.toBe(originalId);
  expect(controller.getSnapshot().revision).toBe(1);
  expect(controller.getSnapshot().state.rows).toHaveLength(1);
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('pending');
  expect(store.value?.packetJson).toBe(originalJson);
});

it('requires explicit reload after a stale revision and preserves the newer committed choice', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  const other = (await fixture(store)).controller; await other.initialize();
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  await other.applyAction({ type: 'exclude', candidateId: 'candidate-a' });
  expect(other.getSnapshot().phase).toBe('error');
  expect(store.value?.reviews[0]?.status).toBe('confirmed');
  await other.retryRestore();
  expect(other.getSnapshot().revision).toBe(2);
  expect(other.getSnapshot().state.rows[0]?.status).toBe('confirmed');
});

it('cannot route load/reset actions around the guarded replacement workflow', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  await controller.applyAction({ type: 'reset' });
  await controller.applyAction({ type: 'load', packet });
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('confirmed');
  expect(controller.getSnapshot().revision).toBe(2);
  expect(store.value?.reviews[0]?.status).toBe('confirmed');
});

it('keeps validation errors local and never commits invalid choices', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'manual', cardId: 'unknown', owner: 'opponent', timestamp: 4 });
  expect(controller.getSnapshot().state.error).not.toBeNull();
  expect(controller.getSnapshot().phase).toBe('ready');
  expect(controller.getSnapshot().state.rows).toHaveLength(1);
  expect(store.value?.revision).toBe(1);
});

it('offers bound stable subscription methods that stop notifying after unsubscribe', async () => {
  const { controller, packet } = await fixture();
  const getSnapshot = controller.getSnapshot;
  const subscribe = controller.subscribe;
  const initial = getSnapshot();
  expect(initial).toBe(getSnapshot());
  let notices = 0;
  const unsubscribe = subscribe(() => { notices++; });
  await controller.initialize();
  expect(notices).toBeGreaterThan(0);
  unsubscribe(); const previous = notices;
  await controller.importPacket(packet);
  expect(notices).toBe(previous);
  expect(getSnapshot().state.packet?.packet_id).toBe('packet-test');
});

it('retains the last good display on corrupt reload and never replaces the corrupt durable record', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  store.value = { ...store.value!, reviews: [] };
  await controller.retryRestore();
  expect(controller.getSnapshot().phase).toBe('error');
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('confirmed');
  await controller.importPacket(packet);
  expect(store.value.reviews).toEqual([]);
});

it('conditions restart on the newest committed revision after queued edits', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  const edit = controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  const restart = controller.restart();
  await Promise.all([edit, restart]);
  expect(controller.getSnapshot().phase).toBe('ready');
  expect(controller.getSnapshot().state.rows[0]?.status).toBe('pending');
  expect(controller.getSnapshot().revision).toBe(1);
  expect(store.value?.sessionId).toBe(controller.getSnapshot().sessionId);
});

it('does not discard the old audit when replacing against a stale session revision', async () => {
  const { controller, store, packet } = await fixture();
  await controller.initialize(); await controller.importPacket(packet);
  const other = (await fixture(store)).controller; await other.initialize();
  await controller.applyAction({ type: 'confirm', candidateId: 'candidate-a' });
  await other.restart();
  expect(other.getSnapshot().phase).toBe('error');
  expect(store.value?.reviews[0]?.status).toBe('confirmed');
  await other.retryRestore();
  expect(other.getSnapshot().state.rows[0]?.status).toBe('confirmed');
});
