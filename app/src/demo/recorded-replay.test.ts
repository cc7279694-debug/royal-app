import { describe, expect, it } from 'vitest';
import {
  createTrackerState, getDiscovery, trackerReducer, type OpponentCardPlayed,
} from '../domain/tracker';
import { RecordedReplay, type ReplaySpeed } from './recorded-replay';

function recorded(eventId: string, cardId: string, timestamp: number): OpponentCardPlayed {
  return { eventId, cardId, timestamp, confidence: null, source: 'recorded_oracle' };
}

const fiveCards: readonly OpponentCardPlayed[] = [
  recorded('recorded-01', 'witch', 1),
  recorded('recorded-02', 'royal_hogs', 2),
  recorded('recorded-03', 'flying_machine', 3),
  recorded('recorded-04', 'golden_knight', 4),
  recorded('recorded-05', 'minions', 5),
];

function fakeClock(initial = 0) {
  let now = initial;
  return { read: () => now, set: (milliseconds: number) => { now = milliseconds; } };
}

describe('recorded replay timeline', () => {
  it('keeps all future source events out of the initial ready snapshot', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);

    expect(replay.snapshot()).toEqual({ status: 'ready', elapsed: 0, speed: 1, events: [] });
    clock.set(20_000);
    expect(replay.tick()).toEqual({ status: 'ready', elapsed: 0, speed: 1, events: [] });
  });

  it('reveals five known cards only as their respective timestamps become due', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    expect(replay.start()).toEqual({ status: 'playing', elapsed: 0, speed: 1, events: [] });

    const checkpoints = [
      { ms: 999, elapsed: .999, status: 'playing', ids: [] },
      { ms: 1_000, elapsed: 1, status: 'playing', ids: ['recorded-01'] },
      { ms: 2_000, elapsed: 2, status: 'playing', ids: ['recorded-01', 'recorded-02'] },
      { ms: 3_000, elapsed: 3, status: 'playing', ids: ['recorded-01', 'recorded-02', 'recorded-03'] },
      { ms: 4_000, elapsed: 4, status: 'playing', ids: ['recorded-01', 'recorded-02', 'recorded-03', 'recorded-04'] },
      { ms: 5_000, elapsed: 5, status: 'complete', ids: ['recorded-01', 'recorded-02', 'recorded-03', 'recorded-04', 'recorded-05'] },
    ];
    for (const checkpoint of checkpoints) {
      clock.set(checkpoint.ms);
      const snapshot = replay.tick();
      expect(snapshot.elapsed).toBeCloseTo(checkpoint.elapsed);
      expect(snapshot.status).toBe(checkpoint.status);
      expect(snapshot.events.map(event => event.eventId)).toEqual(checkpoint.ids);
    }
  });

  it('emits each exact-boundary event once even across repeated ticks', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_000);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['recorded-01']);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['recorded-01']);
    clock.set(1_001);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['recorded-01']);
  });

  it('emits a one-second event exactly after ten small hundred-millisecond ticks', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    for (let milliseconds = 100; milliseconds <= 900; milliseconds += 100) {
      clock.set(milliseconds);
      expect(replay.tick().events).toEqual([]);
    }
    clock.set(1_000);
    expect(replay.tick().elapsed).toBe(1);
    expect(replay.snapshot().events.map(event => event.eventId)).toEqual(['recorded-01']);
  });

  it('includes all coarse-tick events in timestamp then event-ID order', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay([
      recorded('tie-b', 'minions', 2),
      recorded('late', 'golden_knight', 4),
      recorded('tie-a', 'royal_hogs', 2),
      recorded('early', 'witch', 1),
    ], clock.read);
    replay.start();
    clock.set(3_000);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['early', 'tie-a', 'tie-b']);
    clock.set(80_000);
    expect(replay.tick()).toMatchObject({ status: 'complete', elapsed: 4 });
    expect(replay.snapshot().events.map(event => event.eventId)).toEqual(['early', 'tie-a', 'tie-b', 'late']);
    clock.set(90_000);
    expect(replay.tick()).toMatchObject({ status: 'complete', elapsed: 4 });
  });

  it('retains repeated plays in history while the tracker discovers one card slot', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay([
      recorded('witch-01', 'witch', 1), recorded('witch-02', 'witch', 3),
    ], clock.read);
    replay.start();
    clock.set(3_000);
    const snapshot = replay.tick();
    const state = snapshot.events.reduce(
      (current, event) => trackerReducer(current, { type: 'event', event }), createTrackerState(),
    );

    expect(state.events.map(event => event.eventId)).toEqual(['witch-01', 'witch-02']);
    expect(getDiscovery(state).cardIds).toEqual(['witch']);
    expect(state.error).toBeNull();
  });

  it('starts a timestamp-zero event immediately but does not leak it while ready', () => {
    const replay = new RecordedReplay([recorded('at-zero', 'witch', 0)]);
    expect(replay.snapshot().events).toEqual([]);
    expect(replay.start()).toEqual({
      status: 'complete', elapsed: 0, speed: 1,
      events: [recorded('at-zero', 'witch', 0)],
    });
  });

  it('completes an empty valid source without inventing an event', () => {
    const replay = new RecordedReplay([]);
    expect(replay.start()).toEqual({ status: 'complete', elapsed: 0, speed: 1, events: [] });
    expect(replay.restart()).toEqual({ status: 'complete', elapsed: 0, speed: 1, events: [] });
  });

  it('snapshot reads do not advance the timeline without a tick', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(2_000);
    expect(replay.snapshot()).toMatchObject({ elapsed: 0, events: [] });
    expect(replay.tick()).toMatchObject({ elapsed: 2 });
  });
});

describe('recorded replay controls', () => {
  it('settles playback on pause then resumes without counting paused wall time', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_500);
    expect(replay.pause()).toMatchObject({ status: 'paused', elapsed: 1.5 });
    clock.set(12_000);
    expect(replay.tick()).toMatchObject({ status: 'paused', elapsed: 1.5 });
    expect(replay.resume()).toMatchObject({ status: 'playing', elapsed: 1.5 });
    clock.set(12_500);
    expect(replay.tick()).toMatchObject({ status: 'playing', elapsed: 2 });
    expect(replay.snapshot().events.map(event => event.eventId)).toEqual(['recorded-01', 'recorded-02']);
  });

  it('start and resume do not reanchor an already playing replay', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(500);
    replay.start();
    replay.resume();
    clock.set(1_000);
    expect(replay.tick().elapsed).toBe(1);
  });

  it('only restart can play again after completion', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(20_000);
    replay.tick();
    expect(replay.start()).toMatchObject({ status: 'complete', elapsed: 5 });
    expect(replay.resume()).toMatchObject({ status: 'complete', elapsed: 5 });
    expect(replay.pause()).toMatchObject({ status: 'complete', elapsed: 5 });
    expect(replay.restart()).toEqual({ status: 'playing', elapsed: 0, speed: 1, events: [] });
    clock.set(21_000);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['recorded-01']);
  });

  it('restart clears a paused history and preserves the selected playback speed', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.setSpeed(4);
    replay.start();
    clock.set(500);
    replay.pause();
    clock.set(40_000);
    expect(replay.restart()).toEqual({ status: 'playing', elapsed: 0, speed: 4, events: [] });
    clock.set(40_250);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['recorded-01']);
    expect(replay.snapshot().elapsed).toBe(1);
  });

  it('keeps virtual time continuous when switching between normal and four-times speed', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_000);
    expect(replay.setSpeed(4)).toMatchObject({ status: 'playing', elapsed: 1, speed: 4 });
    clock.set(1_500);
    expect(replay.tick().elapsed).toBe(3);
    clock.set(1_750);
    expect(replay.setSpeed(1)).toMatchObject({ status: 'playing', elapsed: 4, speed: 1 });
    clock.set(2_750);
    expect(replay.tick()).toMatchObject({ status: 'complete', elapsed: 5, speed: 1 });
  });

  it('changing speed during a pause does not consume paused time', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_000);
    replay.pause();
    clock.set(9_000);
    expect(replay.setSpeed(4)).toMatchObject({ status: 'paused', elapsed: 1, speed: 4 });
    replay.resume();
    clock.set(9_250);
    expect(replay.tick().elapsed).toBe(2);
  });

  it('preserves a precise boundary when speed changes after multiple small ticks', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    for (let milliseconds = 100; milliseconds <= 900; milliseconds += 100) {
      clock.set(milliseconds);
      replay.tick();
    }
    replay.setSpeed(4);
    clock.set(925);
    expect(replay.tick().elapsed).toBe(1);
    expect(replay.snapshot().events.map(event => event.eventId)).toEqual(['recorded-01']);
  });

  it('preserves a precise boundary across pause and resume after multiple small ticks', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    for (let milliseconds = 100; milliseconds <= 900; milliseconds += 100) {
      clock.set(milliseconds);
      replay.tick();
    }
    replay.pause();
    clock.set(3_000);
    replay.resume();
    clock.set(3_100);
    expect(replay.tick().elapsed).toBe(1);
    expect(replay.snapshot().events.map(event => event.eventId)).toEqual(['recorded-01']);
  });

  it('does not pause or resume a source before its first start', () => {
    const replay = new RecordedReplay(fiveCards);
    expect(replay.pause()).toMatchObject({ status: 'ready', elapsed: 0, events: [] });
    expect(replay.resume()).toMatchObject({ status: 'ready', elapsed: 0, events: [] });
  });

  it('rejects unsupported speeds before they can affect the replay', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(500);
    expect(() => replay.setSpeed(2 as ReplaySpeed)).toThrow();
    expect(replay.snapshot()).toMatchObject({ elapsed: 0, speed: 1 });
    clock.set(1_000);
    expect(replay.tick().elapsed).toBe(1);
  });
});

describe('recorded replay boundary integrity', () => {
  it('ignores backward samples without counting the recovered interval twice', () => {
    const clock = fakeClock(1_000);
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(2_000);
    expect(replay.tick().elapsed).toBe(1);
    clock.set(1_500);
    expect(replay.tick().elapsed).toBe(1);
    clock.set(2_500);
    expect(replay.tick().elapsed).toBe(1.5);
  });

  it('ignores nonfinite samples and continues from the last finite clock value', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_000);
    expect(replay.tick().elapsed).toBe(1);
    for (const value of [Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY]) {
      clock.set(value);
      expect(replay.tick()).toMatchObject({ status: 'playing', elapsed: 1 });
    }
    clock.set(2_000);
    expect(replay.tick().elapsed).toBe(2);
  });

  it('anchors at the first finite clock value after a nonfinite start', () => {
    const clock = fakeClock(Number.NaN);
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.start();
    clock.set(1_000);
    expect(replay.tick().elapsed).toBe(0);
    clock.set(2_000);
    expect(replay.tick().elapsed).toBe(1);
  });

  it('caps extremely large finite clock gaps at the final recorded timestamp', () => {
    const clock = fakeClock();
    const replay = new RecordedReplay(fiveCards, clock.read);
    replay.setSpeed(4);
    replay.start();
    clock.set(Number.MAX_VALUE);
    expect(replay.tick()).toMatchObject({ status: 'complete', elapsed: 5 });
    expect(replay.snapshot().events).toHaveLength(5);
  });

  it('detaches source data and keeps earlier snapshots immutable when playback advances', () => {
    const clock = fakeClock();
    const mutableEvent = { ...recorded('source-a', 'witch', 1) };
    const input = [mutableEvent, recorded('source-b', 'minions', 3)];
    const replay = new RecordedReplay(input, clock.read);
    mutableEvent.cardId = 'golden_knight';
    mutableEvent.timestamp = 50;
    input.push(recorded('injected', 'flying_machine', 2));
    replay.start();
    clock.set(1_000);
    const earlier = replay.tick();
    expect(earlier.events).toEqual([recorded('source-a', 'witch', 1)]);
    expect(Object.isFrozen(earlier)).toBe(true);
    expect(Object.isFrozen(earlier.events)).toBe(true);
    expect(Object.isFrozen(earlier.events[0])).toBe(true);
    clock.set(3_000);
    expect(replay.tick().events.map(event => event.eventId)).toEqual(['source-a', 'source-b']);
    expect(earlier.elapsed).toBe(1);
    expect(earlier.events.map(event => event.eventId)).toEqual(['source-a']);
  });

  it.each([
    { label: 'mock source', input: [{ ...recorded('unsupported', 'witch', 1), source: 'mock', confidence: 1 }] },
    { label: 'invented confidence', input: [{ ...recorded('bad-confidence', 'witch', 1), confidence: .9 }] },
    { label: 'negative timestamp', input: [recorded('bad-time', 'witch', -1)] },
    { label: 'unsupported card', input: [recorded('bad-card', 'skeletons', 1)] },
    { label: 'duplicate IDs', input: [recorded('duplicate', 'witch', 1), recorded('duplicate', 'witch', 1)] },
    { label: 'null event', input: [null] },
    { label: 'null source', input: null },
  ])('rejects $label at the parser boundary', ({ input }) => {
    expect(() => new RecordedReplay(input as unknown as readonly OpponentCardPlayed[])).toThrow();
  });
});
