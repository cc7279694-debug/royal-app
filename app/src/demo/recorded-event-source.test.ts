import { expect, it } from 'vitest';
import { createTrackerState, getDiscovery, trackerReducer } from '../domain/tracker';

const event = { eventId: 'event-a', cardId: 'witch', timestamp: 12,
  confidence: null, source: 'recorded_oracle' };

async function parse(payload: unknown) {
  const { RecordedEventSource } = await import('./recorded-event-source');
  return RecordedEventSource.fromJSON(payload);
}

it('reads offline events without pretending evidence is a probability', async () => {
  const events = await parse({ schema: 'recorded_oracle_events_v1', events: [event] });
  let state = createTrackerState();
  for (const row of events) state = trackerReducer(state, { type: 'event', event: row });
  expect(state.error).toBeNull();
  expect(getDiscovery(state).cardIds).toEqual(['witch']);
  expect(state.events[0]?.source).toBe('recorded_oracle');
  expect(state.events[0]?.confidence).toBeNull();
});

it('sorts consistently and preserves input', async () => {
  const payload = { schema: 'recorded_oracle_events_v1', events: [
    { ...event, eventId: 'event-b', timestamp: 20, cardId: 'minions' }, event] };
  const original = JSON.stringify(payload);
  expect((await parse(payload)).map(row => row.eventId)).toEqual(['event-a', 'event-b']);
  expect(JSON.stringify(payload)).toBe(original);
});

it.each([
  null,
  { schema: 'recorded_oracle_events_v1', events: [{ ...event, source: 'detector' }] },
  { schema: 'recorded_oracle_events_v1', events: [{ ...event, confidence: .95 }] },
  { schema: 'recorded_oracle_events_v1', events: [{ ...event, timestamp: -1 }] },
  { schema: 'recorded_oracle_events_v1', events: [event, event] },
  { schema: 'recorded_oracle_events_v1', events: [{ ...event, cardId: 'skeletons' }] },
])('rejects invalid, duplicate or non-Oracle sources', async (payload) => {
  const { RecordedEventSource } = await import('./recorded-event-source');
  expect(() => RecordedEventSource.fromJSON(payload)).toThrow();
});
