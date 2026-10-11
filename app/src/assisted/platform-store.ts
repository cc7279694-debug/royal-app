import { Capacitor, registerPlugin } from '@capacitor/core';
import { IndexedDbSessionStore } from './indexeddb-store';
import type { StoredSession } from './session';
import type { ReplaceSessionInput, SaveSessionInput, SessionStore } from './session-repository';

interface NativeAssistedSessionStore {
  load(): Promise<{ readonly session: StoredSession | null }>;
  replace(input: ReplaceSessionInput): Promise<void>;
  save(input: SaveSessionInput): Promise<void>;
}

class AndroidSessionStore implements SessionStore {
  constructor(private readonly plugin: NativeAssistedSessionStore) {}
  async load(): Promise<StoredSession | null> { return (await this.plugin.load()).session; }
  async replace(input: ReplaceSessionInput): Promise<void> { await this.plugin.replace(input); }
  async save(input: SaveSessionInput): Promise<void> { await this.plugin.save(input); }
}

export function createPlatformStore(): SessionStore {
  return Capacitor.getPlatform() === 'android'
    ? new AndroidSessionStore(registerPlugin<NativeAssistedSessionStore>('AssistedSessionStore'))
    : new IndexedDbSessionStore();
}
