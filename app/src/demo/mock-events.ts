import type { OpponentCardPlayed } from '../domain/tracker';

/** Deliberately invented events: these are not observations or real deployments. */
export const mockEvents: readonly OpponentCardPlayed[] = Object.freeze([
  Object.freeze({
    eventId: 'mock-witch-01',
    cardId: 'witch',
    timestamp: 12,
    confidence: 1,
    source: 'mock',
  }),
  Object.freeze({
    eventId: 'mock-balloon-01',
    cardId: 'balloon',
    timestamp: 28,
    confidence: 1,
    source: 'mock',
  }),
]);
