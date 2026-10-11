import type { AssistedState } from './review-state';
import { restoreStoredSession, updateStoredSession } from './session';
import type { RestoredSession, StoredReview, StoredSession } from './session';

export interface ReplaceSessionInput {
  readonly session: StoredSession;
  readonly expectedSessionId: string | null;
  readonly expectedRevision: number | null;
}
export interface SaveSessionInput {
  readonly sessionId: string;
  readonly expectedRevision: number;
  readonly revision: number;
  readonly updatedAt: string;
  readonly reviews: readonly StoredReview[];
}
export interface SessionStore {
  load(): Promise<StoredSession | null>;
  replace(input: ReplaceSessionInput): Promise<void>;
  save(input: SaveSessionInput): Promise<void>;
}

export class SessionStoreError extends Error {
  constructor(readonly code: 'CONFLICT' | 'UNAVAILABLE', message: string) { super(message); }
}

export class AssistedSessionRepository {
  constructor(private readonly store: SessionStore) {}
  async load(): Promise<RestoredSession | null> {
    const session = await this.store.load();
    return session === null ? null : restoreStoredSession(session);
  }
  async replace(session: StoredSession, expected: StoredSession | null): Promise<void> {
    await restoreStoredSession(session);
    await this.store.replace({ session, expectedSessionId: expected?.sessionId ?? null, expectedRevision: expected?.revision ?? null });
  }
  async save(current: StoredSession, state: AssistedState, updatedAt: string): Promise<StoredSession> {
    const next = updateStoredSession(current, state, updatedAt);
    await this.store.save({ sessionId: current.sessionId, expectedRevision: current.revision,
      revision: next.revision, updatedAt: next.updatedAt, reviews: next.reviews });
    return next;
  }
}
