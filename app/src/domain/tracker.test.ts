import { describe, expect, it } from 'vitest';
import {
  createTrackerState,
  getDiscovery,
  trackerReducer,
  type OpponentCardPlayed,
  type TrackerState,
} from './tracker';

const witch: OpponentCardPlayed = {
  eventId: 'mock-witch-01',
  cardId: 'witch',
  timestamp: 12,
  confidence: 1,
  source: 'mock',
};

const balloon: OpponentCardPlayed = {
  eventId: 'mock-balloon-01',
  cardId: 'balloon',
  timestamp: 28,
  confidence: 1,
  source: 'mock',
};

function consume(events: readonly unknown[]): TrackerState {
  return events.reduce<TrackerState>(
    (state, event) => trackerReducer(state, { type: 'event', event }),
    createTrackerState(),
  );
}

describe('mock card event boundary', () => {
  it('discovers Witch and Balloon as two unique cards with a real event history', () => {
    const state = consume([witch, balloon]);

    expect(state.events).toEqual([witch, balloon]);
    expect(state.error).toBeNull();
    expect(getDiscovery(state)).toEqual({
      cardIds: ['witch', 'balloon'],
      overflowCardIds: [],
    });
  });

  it('does not count repeated plays of the same card as new discoveries', () => {
    const state = consume([witch, { ...witch, eventId: 'mock-witch-02', timestamp: 40 }]);

    expect(state.events).toHaveLength(2);
    expect(getDiscovery(state).cardIds).toEqual(['witch']);
  });

  it('ignores an identical replay without replacing the state', () => {
    const once = consume([witch]);
    const twice = trackerReducer(once, { type: 'event', event: { ...witch } });

    expect(twice).toBe(once);
    expect(twice.events).toHaveLength(1);
  });

  it.each(['cardId', 'timestamp', 'confidence'] as const)(
    'rejects a conflicting duplicate event ID when %s differs',
    (field) => {
      const changes = { cardId: 'balloon', timestamp: 13, confidence: 0.5 };
      const state = consume([witch, { ...witch, [field]: changes[field] }]);

      expect(state.events).toEqual([witch]);
      expect(state.error?.code).toBe('conflicting-id');
    },
  );

  it.each(['observation', 'detector', 'live', 'manual', undefined, null])(
    'rejects future or missing source %s even for a previously consumed ID',
    (source) => {
      const state = consume([witch, { ...witch, source }]);

      expect(state.events).toEqual([witch]);
      expect(state.error?.code).toBe('unsupported-source');
    },
  );

  it.each([
    ['null payload', null],
    ['array payload', []],
    ['missing fields', { eventId: 'missing' }],
    ['empty event ID', { ...witch, eventId: '' }],
    ['whitespace event ID', { ...witch, eventId: ' mock-01' }],
    ['non-string event ID', { ...witch, eventId: 1 }],
    ['oversized event ID', { ...witch, eventId: 'a'.repeat(129) }],
    ['empty card ID', { ...witch, cardId: '' }],
    ['non-string card ID', { ...witch, cardId: 1 }],
    ['invalid card ID', { ...witch, cardId: '<script>' }],
    ['oversized card ID', { ...witch, cardId: 'a'.repeat(65) }],
    ['negative timestamp', { ...witch, timestamp: -1 }],
    ['string timestamp', { ...witch, timestamp: '12' }],
    ['NaN timestamp', { ...witch, timestamp: Number.NaN }],
    ['infinite timestamp', { ...witch, timestamp: Number.POSITIVE_INFINITY }],
    ['unsafe timestamp', { ...witch, timestamp: Number.MAX_SAFE_INTEGER + 1 }],
    ['negative confidence', { ...witch, confidence: -0.01 }],
    ['confidence above one', { ...witch, confidence: 1.01 }],
    ['NaN confidence', { ...witch, confidence: Number.NaN }],
    ['string confidence', { ...witch, confidence: '1' }],
    ['unexpected visual payload', { ...witch, bbox: [0, 0, 1, 1] }],
  ])('rejects %s without losing previously accepted events', (_label, payload) => {
    const state = consume([balloon, payload]);

    expect(state.events).toEqual([balloon]);
    expect(state.error).not.toBeNull();
    expect(getDiscovery(state).cardIds).toEqual(['balloon']);
  });

  it('accepts zero and fractional timestamps and confidence endpoints', () => {
    const state = consume([
      { ...witch, timestamp: 0, confidence: 0 },
      { ...balloon, timestamp: 0.5, confidence: 1 },
    ]);

    expect(state.events).toHaveLength(2);
    expect(state.error).toBeNull();
  });

  it('orders history and discoveries deterministically by timestamp then event ID', () => {
    const laterZ = { ...witch, eventId: 'z-later', timestamp: 40 };
    const laterA = { ...balloon, eventId: 'a-later', timestamp: 40 };
    const earlier = { ...witch, cardId: 'knight', eventId: 'earlier', timestamp: 4 };
    const reversed = consume([laterZ, laterA, earlier]);
    const ordered = consume([earlier, laterA, laterZ]);

    expect(reversed.events.map((event) => event.eventId)).toEqual([
      'earlier', 'a-later', 'z-later',
    ]);
    expect(reversed).toEqual(ordered);
    expect(getDiscovery(reversed).cardIds).toEqual(['knight', 'balloon', 'witch']);
  });

  it('caps visible discoveries at eight and retains explicit unique overflow', () => {
    const events = Array.from({ length: 10 }, (_, index) => ({
      ...witch,
      eventId: `mock-${index + 1}`,
      cardId: `card-${index + 1}`,
      timestamp: index,
    }));
    const state = consume([
      ...events,
      { ...witch, eventId: 'replay-overflow', cardId: 'card-9', timestamp: 20 },
    ]);

    expect(state.events).toHaveLength(11);
    expect(getDiscovery(state)).toEqual({
      cardIds: ['card-1', 'card-2', 'card-3', 'card-4', 'card-5', 'card-6', 'card-7', 'card-8'],
      overflowCardIds: ['card-9', 'card-10'],
    });
  });

  it('resets cards, overflow, errors and deduplication identity', () => {
    const events = Array.from({ length: 9 }, (_, index) => ({
      ...witch, eventId: `mock-${index}`, cardId: `card-${index}`, timestamp: index,
    }));
    const populated = consume([...events, null]);
    const reset = trackerReducer(populated, { type: 'reset' });

    expect(reset.events).toEqual([]);
    expect(reset.error).toBeNull();
    expect(getDiscovery(reset)).toEqual({ cardIds: [], overflowCardIds: [] });
    expect(trackerReducer(reset, { type: 'event', event: events[0] }).events).toHaveLength(1);
  });

  it('does not retain or mutate the caller-owned event object', () => {
    const incoming = { ...witch };
    const state = consume([incoming]);
    incoming.cardId = 'balloon';

    expect(state.events[0]?.cardId).toBe('witch');
    expect(getDiscovery(state).cardIds).toEqual(['witch']);
  });

  it('clears a previous input error after accepting a valid new event', () => {
    const state = consume([null, witch]);

    expect(state.events).toEqual([witch]);
    expect(state.error).toBeNull();
  });
});
