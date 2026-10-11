import type { AssistedPacket } from './contract';
import { AssistedSource } from './import';
import { createPlatformStore } from './platform-store';
import { assistedReducer, createAssistedState } from './review-state';
import type { AssistedAction, AssistedState } from './review-state';
import { createStoredSession } from './session';
import type { StoredSession } from './session';
import { AssistedSessionRepository } from './session-repository';

export interface SessionSnapshot {
  readonly state: AssistedState;
  readonly phase: 'loading' | 'ready' | 'saving' | 'error';
  readonly sessionId: string | null;
  readonly revision: number | null;
  readonly error: string | null;
}
export interface SessionControllerOptions { readonly now?: () => string; readonly uuid?: () => string; }

export class AssistedSessionController {
  private snapshot: SessionSnapshot = Object.freeze({ state: createAssistedState(), phase: 'loading', sessionId: null, revision: null, error: null });
  private session: StoredSession | null = null;
  private readonly listeners = new Set<() => void>();
  private queue = Promise.resolve();
  private initialization: Promise<void> | null = null;
  private readonly now: () => string;
  private readonly uuid: () => string;
  constructor(private readonly repository: AssistedSessionRepository, options: SessionControllerOptions = {}) {
    this.now = options.now ?? (() => new Date().toISOString());
    this.uuid = options.uuid ?? (() => crypto.randomUUID());
  }
  readonly getSnapshot = (): SessionSnapshot => this.snapshot;
  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  };
  readonly initialize = (): Promise<void> => this.initialization ??= this.enqueue(() => this.restore());
  readonly retryRestore = (): Promise<void> => this.enqueue(() => this.restore());
  readonly importPacket = async (packet: AssistedPacket): Promise<void> => {
    await this.initialize();
    return this.enqueue(async () => {
      if (this.snapshot.phase !== 'ready') return;
      this.publish(this.snapshot.state, 'saving');
      const validated = await AssistedSource.fromJSON(packet);
      await this.replace(createAssistedState(validated));
    });
  };
  readonly applyAction = async (action: AssistedAction): Promise<void> => {
    await this.initialize();
    return this.enqueue(async () => {
      if (this.snapshot.phase !== 'ready') return;
      if (action.type === 'load' || action.type === 'reset') {
        this.publish({ ...this.snapshot.state, error: '请使用导入或重新开始操作。' }, 'ready');
        return;
      }
      const state = assistedReducer(this.snapshot.state, action);
      if (state.error !== null || this.session === null) {
        this.publish(state, 'ready');
        return;
      }
      this.publish(this.snapshot.state, 'saving');
      const updatedAt = this.now();
      this.session = await this.repository.save(this.session, state, updatedAt < this.session.updatedAt ? this.session.updatedAt : updatedAt);
      this.publish(state, 'ready');
    });
  };
  readonly restart = async (): Promise<void> => {
    await this.initialize();
    return this.enqueue(async () => {
      if (this.snapshot.phase !== 'ready' || this.snapshot.state.packet === null) return;
      this.publish(this.snapshot.state, 'saving');
      await this.replace(createAssistedState(this.snapshot.state.packet));
    });
  };

  private enqueue(operation: () => Promise<void>): Promise<void> {
    const result = this.queue.then(async () => {
      try { await operation(); }
      catch (error) {
        const detail = error instanceof Error ? error.message : '本地存储不可用。';
        this.publish(this.snapshot.state, 'error', `未能完成本地保存或恢复，已保留最后可靠状态。${detail} 请重试恢复最后提交的审核记录。`);
      }
    });
    this.queue = result;
    return result;
  }

  private async restore(): Promise<void> {
    this.publish(this.snapshot.state, 'loading');
    const restored = await this.repository.load();
    this.session = restored?.session ?? null;
    this.publish(restored?.state ?? createAssistedState(), 'ready');
  }

  private async replace(state: AssistedState): Promise<void> {
    const next = await createStoredSession(state, this.uuid(), this.now());
    await this.repository.replace(next, this.session);
    this.session = next;
    this.publish(state, 'ready');
  }

  private publish(state: AssistedState, phase: SessionSnapshot['phase'], error: string | null = null): void {
    this.snapshot = Object.freeze({ state, phase, sessionId: this.session?.sessionId ?? null,
      revision: this.session?.revision ?? null, error });
    for (const listener of this.listeners) listener();
  }
}

let controller: AssistedSessionController | null = null;
export function getAssistedSessionController(): AssistedSessionController {
  return controller ??= new AssistedSessionController(new AssistedSessionRepository(createPlatformStore()));
}
