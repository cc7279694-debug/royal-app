import {
  createTrackerState, trackerReducer, type OpponentCardPlayed,
} from '../domain/tracker';

const cards = new Set(['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions']);

/** Explicit offline adapter only. Not wired into the mock UI or any game capture. */
export class RecordedEventSource {
  static fromJSON(payload: unknown): readonly OpponentCardPlayed[] {
    if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
      throw new Error('Invalid recorded Oracle packet');
    }
    const packet = payload as Record<string, unknown>;
    if (Object.keys(packet).length !== 2 || packet.schema !== 'recorded_oracle_events_v1'
      || !Array.isArray(packet.events)) throw new Error('Invalid recorded Oracle packet');

    let state = createTrackerState();
    const seen = new Set<string>();
    for (const input of packet.events as unknown[]) {
      if (typeof input !== 'object' || input === null || Array.isArray(input)) {
        throw new Error('Invalid recorded Oracle event');
      }
      const event = input as Record<string, unknown>;
      if (event.source !== 'recorded_oracle' || typeof event.cardId !== 'string'
        || !cards.has(event.cardId) || typeof event.eventId !== 'string'
        || seen.has(event.eventId)) throw new Error('Invalid or duplicate recorded Oracle event');
      state = trackerReducer(state, { type: 'event', event: input });
      if (state.error) throw new Error(state.error.message);
      seen.add(event.eventId);
    }
    return Object.freeze([...state.events]);
  }
}
