import { restoreStoredSession } from './session';
import type { StoredSession } from './session';
import { SessionStoreError } from './session-repository';
import type { ReplaceSessionInput, SaveSessionInput, SessionStore } from './session-repository';

const storeName = 'session';
const activeKey = 'active';

export function isStrictJsonValue(value: unknown): boolean {
  const ancestors = new Set<object>();
  function visit(item: unknown): boolean {
    if (item === null || typeof item === 'string' || typeof item === 'boolean') return true;
    if (typeof item === 'number') return Number.isFinite(item);
    if (typeof item !== 'object' || ancestors.has(item)) return false;
    const array = Array.isArray(item);
    if (!array && Object.getPrototypeOf(item) !== Object.prototype) return false;
    const keys = Reflect.ownKeys(item);
    if (keys.some(key => typeof key !== 'string')) return false;
    if (array && (keys.length !== item.length + 1 || !Array.from({ length: item.length }, (_, index) => Object.hasOwn(item, index)).every(Boolean))) return false;
    ancestors.add(item);
    const valid = keys.filter(key => !(array && key === 'length')).every(key => {
      const descriptor = Object.getOwnPropertyDescriptor(item, key);
      return descriptor !== undefined && descriptor.enumerable && Object.hasOwn(descriptor, 'value') && visit(descriptor.value);
    });
    ancestors.delete(item);
    return valid;
  }
  return visit(value);
}

function conflict(): never {
  throw new SessionStoreError('CONFLICT', '本地记录已被其他页面修改，请重试恢复后再操作。');
}

function unavailable(): SessionStoreError {
  return new SessionStoreError('UNAVAILABLE', '无法访问本地审核数据库，已有记录未被删除。');
}

function currentSession(value: unknown): StoredSession | null {
  if (value === undefined) return null;
  if (value === null || typeof value !== 'object' || Array.isArray(value) || !isStrictJsonValue(value)) throw unavailable();
  const session = value as Partial<StoredSession>;
  if (session.formatVersion !== 1 || typeof session.sessionId !== 'string'
    || typeof session.revision !== 'number' || !Number.isSafeInteger(session.revision) || session.revision < 1
    || typeof session.packetJson !== 'string' || typeof session.packetSha256 !== 'string'
    || !Array.isArray(session.reviews)) throw unavailable();
  return value as StoredSession;
}

export class IndexedDbSessionStore implements SessionStore {
  private connection: Promise<IDBDatabase> | null = null;
  constructor(private readonly databaseName = 'clash-tracker-assisted-review',
    private readonly factory: IDBFactory | undefined = globalThis.indexedDB) {}

  async load(): Promise<StoredSession | null> {
    const database = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = database.transaction(storeName, 'readonly');
      const request = transaction.objectStore(storeName).get(activeKey);
      transaction.oncomplete = () => {
        try { resolve(currentSession(request.result)); }
        catch (error) { reject(error); }
      };
      transaction.onabort = transaction.onerror = () => { reject(unavailable()); };
    });
  }

  async replace(input: ReplaceSessionInput): Promise<void> {
    if (input.session.revision !== 1 || (input.expectedSessionId === null) !== (input.expectedRevision === null)) throw conflict();
    await this.write(current => {
      if ((current?.sessionId ?? null) !== input.expectedSessionId || (current?.revision ?? null) !== input.expectedRevision) return conflict();
      return input.session;
    });
  }

  async save(input: SaveSessionInput): Promise<void> {
    if (!Number.isSafeInteger(input.expectedRevision) || input.expectedRevision < 1
      || !Number.isSafeInteger(input.revision) || input.revision !== input.expectedRevision + 1) throw conflict();
    await this.write(current => {
      if (current === null || current.sessionId !== input.sessionId || current.revision !== input.expectedRevision) return conflict();
      return { ...current, revision: input.revision, updatedAt: input.updatedAt, reviews: input.reviews };
    });
  }

  private async write(change: (current: StoredSession | null) => StoredSession): Promise<void> {
    // Async image/hash validation must finish before opening a read-write
    // transaction. Compare the whole snapshot inside that transaction so a
    // concurrent mutation cannot bypass validation by retaining its revision.
    const previous = await this.load();
    if (previous !== null) await restoreStoredSession(previous);
    const next = change(previous);
    await restoreStoredSession(next);
    const previousJson = JSON.stringify(previous);
    const database = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = database.transaction(storeName, 'readwrite', { durability: 'strict' });
      const store = transaction.objectStore(storeName);
      const request = store.get(activeKey);
      let failure: unknown = null;
      request.onsuccess = () => {
        try {
          if (JSON.stringify(currentSession(request.result)) !== previousJson) return conflict();
          store.put(next, activeKey);
        }
        catch (error) { failure = error; transaction.abort(); }
      };
      transaction.oncomplete = () => { resolve(); };
      transaction.onabort = transaction.onerror = () => { reject(failure ?? unavailable()); };
    });
  }

  private open(): Promise<IDBDatabase> {
    if (this.connection !== null) return this.connection;
    const connection = new Promise<IDBDatabase>((resolve, reject) => {
      if (this.factory === undefined) { reject(unavailable()); return; }
      const request = this.factory.open(this.databaseName, 1);
      let rejected = false;
      request.onupgradeneeded = event => {
        if (event.oldVersion !== 0) { request.transaction?.abort(); return; }
        request.result.createObjectStore(storeName);
      };
      request.onerror = request.onblocked = () => { rejected = true; reject(unavailable()); };
      request.onsuccess = () => {
        const database = request.result;
        if (rejected) { database.close(); return; }
        database.onversionchange = () => { database.close(); this.connection = null; };
        database.onclose = () => { this.connection = null; };
        resolve(database);
      };
    });
    this.connection = connection;
    void connection.catch(() => { if (this.connection === connection) this.connection = null; });
    return connection;
  }
}
