/** Timestamp is seconds on the mock timeline, not a wall-clock or hidden game state. */
export interface OpponentCardPlayed {
  readonly eventId: string;
  readonly cardId: string;
  readonly timestamp: number;
  readonly confidence: number;
  readonly source: 'mock';
}

export interface TrackerError {
  readonly code: 'invalid-event' | 'unsupported-source' | 'conflicting-id';
  readonly message: string;
}

export interface TrackerState {
  readonly events: readonly OpponentCardPlayed[];
  readonly error: TrackerError | null;
}

export type TrackerAction =
  | { readonly type: 'event'; readonly event: unknown }
  | { readonly type: 'reset' };

export function createTrackerState(): TrackerState {
  return { events: [], error: null };
}

type EventValidation =
  | { readonly ok: true; readonly event: OpponentCardPlayed }
  | { readonly ok: false; readonly error: TrackerError };

const eventFields = ['eventId', 'cardId', 'timestamp', 'confidence', 'source'];
const eventIdPattern = /^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/;
const cardIdPattern = /^[a-z][a-z0-9_-]{0,63}$/;

function validateEvent(payload: unknown): EventValidation {
  const invalid: EventValidation = {
    ok: false,
    error: { code: 'invalid-event', message: '模拟事件格式无效，已保留之前的记录。' },
  };

  if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
    return invalid;
  }

  const record = payload as Record<string, unknown>;
  if (record.source !== 'mock') {
    return {
      ok: false,
      error: { code: 'unsupported-source', message: '此演示只接受模拟事件。' },
    };
  }

  const keys = Object.keys(record);
  if (keys.length !== eventFields.length || !eventFields.every((field) => keys.includes(field))) {
    return invalid;
  }

  const { eventId, cardId, timestamp, confidence } = record;
  if (
    typeof eventId !== 'string' || !eventIdPattern.test(eventId) ||
    typeof cardId !== 'string' || !cardIdPattern.test(cardId) ||
    typeof timestamp !== 'number' || !Number.isFinite(timestamp) ||
    timestamp < 0 || timestamp > Number.MAX_SAFE_INTEGER ||
    typeof confidence !== 'number' || !Number.isFinite(confidence) ||
    confidence < 0 || confidence > 1
  ) {
    return invalid;
  }

  return {
    ok: true,
    event: Object.freeze({ eventId, cardId, timestamp, confidence, source: 'mock' }),
  };
}

function compareEvents(a: OpponentCardPlayed, b: OpponentCardPlayed): number {
  if (a.timestamp !== b.timestamp) return a.timestamp - b.timestamp;
  return a.eventId < b.eventId ? -1 : a.eventId > b.eventId ? 1 : 0;
}

export function trackerReducer(state: TrackerState, action: TrackerAction): TrackerState {
  if (action.type === 'reset') return createTrackerState();

  // Check the boundary before deduplication: an existing ID cannot authorize a new source.
  const validation = validateEvent(action.event);
  if (!validation.ok) return { ...state, error: validation.error };

  const event = validation.event;
  const previous = state.events.find((candidate) => candidate.eventId === event.eventId);
  if (previous) {
    if (
      previous.cardId === event.cardId && previous.timestamp === event.timestamp &&
      previous.confidence === event.confidence && previous.source === event.source
    ) return state;

    return {
      ...state,
      error: { code: 'conflicting-id', message: '事件 ID 冲突，已保留原始记录。' },
    };
  }

  return { events: [...state.events, event].sort(compareEvents), error: null };
}

export function getDiscovery(state: TrackerState): {
  readonly cardIds: readonly string[];
  readonly overflowCardIds: readonly string[];
} {
  const uniqueCards = [...new Set(state.events.map((event) => event.cardId))];
  return { cardIds: uniqueCards.slice(0, 8), overflowCardIds: uniqueCards.slice(8) };
}
