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

const demo = {
  schema: 'recorded_oracle_demo_v1', selection: 'verified_scored_only',
  timeline: 'engine_first_seen_seconds',
  source: { replaySha256: 'a'.repeat(64), evaluationSha256: 'b'.repeat(64) },
  excludedUnscoredEventCount: 4,
  events: [event, { ...event, eventId: 'event-b', cardId: 'minions', timestamp: 20 }],
};

it('imports only the explicitly prepared verified-demo envelope, not the raw Oracle projection', async () => {
  const { RecordedEventSource } = await import('./recorded-event-source');
  const parsed = RecordedEventSource.fromDemoJSON(demo);
  expect(parsed.events.map(row => row.eventId)).toEqual(['event-a', 'event-b']);
  expect(parsed.excludedUnscoredEventCount).toBe(4);
  expect(parsed.replaySha256).toBe('a'.repeat(64));
  expect(Object.isFrozen(parsed.events)).toBe(true);
  expect(() => RecordedEventSource.fromDemoJSON({ schema: 'recorded_oracle_events_v1', events: [event] })).toThrow();
});

it.each([
  { ...demo, selection: 'all_engine_outputs' },
  { ...demo, timeline: 'event_gt_seconds' },
  { ...demo, source: { replaySha256: 'not-a-hash', evaluationSha256: 'b'.repeat(64) } },
  { ...demo, excludedUnscoredEventCount: -1 },
  { ...demo, events: [] },
  { ...demo, events: [event, event] },
  { ...demo, events: [{ ...event, timestamp: Number.NaN }] },
  { ...demo, events: [{ ...event, timestamp: Infinity }] },
  { ...demo, events: [{ ...event, timestamp: 86400.001 }] },
  { ...demo, events: [{ ...event, cardId: 'cannon' }] },
  { ...demo, events: [{ ...event, eventId: '' }] },
  { ...demo, events: [{ ...event, source: 'mock' }] },
  { ...demo, unknownField: true },
])('rejects invalid demo metadata and abnormal events before loading any state', async payload => {
  const { RecordedEventSource } = await import('./recorded-event-source');
  expect(() => RecordedEventSource.fromDemoJSON(payload)).toThrow();
});

it('reads a local UTF-8 JSON file without a network or filesystem plugin', async () => {
  const { RecordedEventSource } = await import('./recorded-event-source');
  const file = new File([JSON.stringify(demo)], 'offline.json', { type: 'application/json' });
  expect((await RecordedEventSource.fromFile(file)).events.map(row => row.timestamp)).toEqual([12, 20]);
});

it('rejects malformed and oversized local files', async () => {
  const { RecordedEventSource } = await import('./recorded-event-source');
  await expect(RecordedEventSource.fromFile(new File(['{broken'], 'broken.json'))).rejects.toThrow();
  await expect(RecordedEventSource.fromFile(new File(['x'.repeat(2 * 1024 * 1024 + 1)], 'large.json'))).rejects.toThrow();
});
