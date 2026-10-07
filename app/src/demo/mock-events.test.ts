import { expect, it } from 'vitest';
import { createTrackerState, getDiscovery, trackerReducer } from '../domain/tracker';
import { mockEvents } from './mock-events';

it('advances the actual demonstration stream to Witch then Balloon and resets for replay', () => {
  let state = createTrackerState();
  expect(mockEvents).toHaveLength(2);

  state = trackerReducer(state, { type: 'event', event: mockEvents[0] });
  expect(getDiscovery(state).cardIds).toEqual(['witch']);
  expect(state.events.map((event) => [event.source, event.timestamp])).toEqual([['mock', 12]]);

  state = trackerReducer(state, { type: 'event', event: mockEvents[1] });
  expect(getDiscovery(state).cardIds).toEqual(['witch', 'balloon']);
  expect(state.events.map((event) => [event.source, event.timestamp])).toEqual([
    ['mock', 12], ['mock', 28],
  ]);
  expect(state.error).toBeNull();

  const reset = trackerReducer(state, { type: 'reset' });
  const replay = trackerReducer(reset, { type: 'event', event: mockEvents[0] });
  expect(getDiscovery(replay).cardIds).toEqual(['witch']);
});
