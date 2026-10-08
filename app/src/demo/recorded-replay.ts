import type { OpponentCardPlayed } from '../domain/tracker';
import { RecordedEventSource } from './recorded-event-source';

export type ReplaySpeed = 1 | 4;
export interface ReplaySnapshot {
  readonly status: 'ready' | 'playing' | 'paused' | 'complete';
  readonly elapsed: number;
  readonly speed: ReplaySpeed;
  readonly events: readonly OpponentCardPlayed[];
}

/** Offline virtual time only. The caller owns scheduling and supplies validated Oracle events. */
export class RecordedReplay {
  private readonly source: readonly OpponentCardPlayed[];
  private readonly duration: number;
  private status: ReplaySnapshot['status'] = 'ready';
  private elapsedMilliseconds = 0;
  private speed: ReplaySpeed = 1;
  private events: readonly OpponentCardPlayed[] = Object.freeze([]);
  private nextEvent = 0;
  private lastClock: number | null = null;

  constructor(
    events: readonly OpponentCardPlayed[],
    private readonly clock: () => number = () => performance.now(),
  ) {
    this.source = RecordedEventSource.fromJSON({ schema: 'recorded_oracle_events_v1', events });
    this.duration = this.source.at(-1)?.timestamp ?? 0;
  }

  snapshot(): ReplaySnapshot {
    return Object.freeze({
      status: this.status,
      elapsed: this.status === 'complete' ? this.duration : this.elapsedMilliseconds / 1_000,
      speed: this.speed, events: this.events,
    });
  }

  tick(): ReplaySnapshot {
    if (this.status !== 'playing') return this.snapshot();

    const now = this.clock();
    if (!Number.isFinite(now)) return this.snapshot();
    if (this.lastClock === null) {
      this.lastClock = now;
    } else if (now >= this.lastClock) {
      // Keep clock arithmetic in milliseconds so repeated small ticks do not round a due event down.
      this.elapsedMilliseconds = Math.min(
        this.duration * 1_000, this.elapsedMilliseconds + (now - this.lastClock) * this.speed,
      );
      this.lastClock = now;
    }
    this.emitDueEvents();
    return this.snapshot();
  }

  start(): ReplaySnapshot {
    if (this.status === 'ready') this.beginPlaying();
    return this.snapshot();
  }

  pause(): ReplaySnapshot {
    if (this.status === 'playing') {
      this.tick();
      if (this.status === 'playing') this.status = 'paused';
      this.lastClock = null;
    }
    return this.snapshot();
  }

  resume(): ReplaySnapshot {
    if (this.status === 'paused') this.beginPlaying();
    return this.snapshot();
  }

  restart(): ReplaySnapshot {
    this.elapsedMilliseconds = 0;
    this.events = Object.freeze([]);
    this.nextEvent = 0;
    this.beginPlaying();
    return this.snapshot();
  }

  setSpeed(speed: ReplaySpeed): ReplaySnapshot {
    if (speed !== 1 && speed !== 4) throw new Error('Unsupported recorded replay speed');
    this.tick();
    this.speed = speed;
    return this.snapshot();
  }

  private beginPlaying(): void {
    const now = this.clock();
    this.lastClock = Number.isFinite(now) ? now : null;
    this.status = 'playing';
    this.emitDueEvents();
  }

  private emitDueEvents(): void {
    while (this.nextEvent < this.source.length) {
      const event = this.source[this.nextEvent];
      if (!event || event.timestamp * 1_000 > this.elapsedMilliseconds) break;
      this.nextEvent += 1;
    }
    if (this.events.length !== this.nextEvent) {
      this.events = Object.freeze(this.source.slice(0, this.nextEvent));
    }
    if (this.nextEvent === this.source.length) {
      this.status = 'complete';
      this.lastClock = null;
    }
  }
}
