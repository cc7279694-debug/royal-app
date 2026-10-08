import {
  createTrackerState, trackerReducer, type OpponentCardPlayed,
} from '../domain/tracker';

const cards = new Set(['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions']);

export interface RecordedDemo {
  readonly events: readonly OpponentCardPlayed[];
  readonly excludedUnscoredEventCount: number;
  readonly replaySha256: string;
  readonly evaluationSha256: string;
}

function objectWithKeys(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error('Invalid recorded demo');
  }
  const record = value as Record<string, unknown>;
  if (Object.keys(record).length !== keys.length || !keys.every(key => Object.hasOwn(record, key))) {
    throw new Error('Invalid recorded demo');
  }
  return record;
}

/** Local replay only. Selection happens in the offline exporter, not in the engine or App. */
export class RecordedEventSource {
  static fromDemoJSON(payload: unknown): RecordedDemo {
    const demo = objectWithKeys(payload, ['schema', 'selection', 'timeline', 'source',
      'excludedUnscoredEventCount', 'events']);
    const source = objectWithKeys(demo.source, ['replaySha256', 'evaluationSha256']);
    const hashPattern = /^[a-f0-9]{64}$/;
    if (demo.schema !== 'recorded_oracle_demo_v1' || demo.selection !== 'verified_scored_only'
      || demo.timeline !== 'engine_first_seen_seconds'
      || typeof source.replaySha256 !== 'string' || !hashPattern.test(source.replaySha256)
      || typeof source.evaluationSha256 !== 'string' || !hashPattern.test(source.evaluationSha256)
      || typeof demo.excludedUnscoredEventCount !== 'number'
      || !Number.isSafeInteger(demo.excludedUnscoredEventCount) || demo.excludedUnscoredEventCount < 0
      || !Array.isArray(demo.events) || demo.events.length === 0 || demo.events.length > 5000) {
      throw new Error('Invalid recorded demo');
    }
    const events = this.fromJSON({ schema: 'recorded_oracle_events_v1', events: demo.events });
    if (events.some(row => row.timestamp > 86400)) throw new Error('Abnormal replay timestamp');
    return Object.freeze({ events, excludedUnscoredEventCount: demo.excludedUnscoredEventCount,
      replaySha256: source.replaySha256, evaluationSha256: source.evaluationSha256 });
  }

  static async fromFile(file: File): Promise<RecordedDemo> {
    if (file.size === 0 || file.size > 2 * 1024 * 1024) throw new Error('Invalid replay file size');
    return this.fromDemoJSON(JSON.parse((await file.text()).replace(/^\uFEFF/, '')));
  }

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
