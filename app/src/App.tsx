import { useEffect, useReducer, useRef, useState } from 'react';
import { mockEvents } from './demo/mock-events';
import { RecordedEventSource, type RecordedDemo } from './demo/recorded-event-source';
import { RecordedReplay, type ReplaySnapshot } from './demo/recorded-replay';
import { createTrackerState, getDiscovery, trackerReducer } from './domain/tracker';
import { DiscoveryHud, DiscoverySlots } from './ui/Discovery';
import { EventHistory } from './ui/EventHistory';

export function App() {
  const [state, dispatch] = useReducer(trackerReducer, null, createTrackerState);
  const [mode, setMode] = useState<'mock' | 'recorded_oracle'>('mock');
  const [demo, setDemo] = useState<RecordedDemo | null>(null);
  const [replay, setReplay] = useState<RecordedReplay | null>(null);
  const [snapshot, setSnapshot] = useState<ReplaySnapshot | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const importToken = useRef(0);
  const activeState = mode === 'mock' ? state : (snapshot?.events ?? []).reduce(
    (current, event) => trackerReducer(current, { type: 'event', event }), createTrackerState());
  const discovery = getDiscovery(activeState);
  const nextEvent = mockEvents[state.events.length];
  const playLabel = nextEvent
    ? state.events.length === 0 ? '播放模拟事件' : '播放下一个事件'
    : '模拟事件已播完';

  useEffect(() => {
    if (mode !== 'recorded_oracle' || !replay || snapshot?.status !== 'playing') return;
    const timer = window.setInterval(() => setSnapshot(replay.tick()), 100);
    return () => window.clearInterval(timer);
  }, [mode, replay, snapshot?.status]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden && mode === 'recorded_oracle' && replay) setSnapshot(replay.pause());
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      document.removeEventListener('visibilitychange', onVisibility);
      replay?.pause();
    };
  }, [mode, replay]);

  function chooseMode(next: typeof mode) {
    if (next === mode) return;
    importToken.current += 1;
    replay?.pause();
    dispatch({ type: 'reset' });
    const replacement = demo ? new RecordedReplay(demo.events) : null;
    setReplay(replacement);
    setSnapshot(replacement?.snapshot() ?? null);
    setImporting(false);
    setImportError(null);
    setMode(next);
  }

  async function importFile(file: File) {
    const token = ++importToken.current;
    if (replay) setSnapshot(replay.pause());
    setImporting(true);
    setImportError(null);
    try {
      const loaded = await RecordedEventSource.fromFile(file);
      if (token !== importToken.current) return;
      const replacement = new RecordedReplay(loaded.events);
      setDemo(loaded);
      setReplay(replacement);
      setSnapshot(replacement.snapshot());
    } catch {
      if (token === importToken.current) {
        setImportError('回放 JSON 无效。请导入已核实事件的专用导出文件（最大 2 MB）；旧记录未被替换。');
      }
    } finally {
      if (token === importToken.current) setImporting(false);
    }
  }

  const replayStatus = snapshot ? {
    ready: '准备就绪', playing: '回放中', paused: '已暂停', complete: '回放完成',
  }[snapshot.status] : '等待导入';
  const elapsed = Math.floor(snapshot?.elapsed ?? 0);
  const timeline = `${Math.floor(elapsed / 60).toString().padStart(2, '0')}:${(elapsed % 60).toString().padStart(2, '0')}`;

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-row flex items-center justify-between gap-3">
          <h1>Clash Tracker</h1>
          <span className="mock-badge">{mode === 'mock' ? '模拟演示' : '离线 Oracle 回放'}</span>
        </div>
        <p className="app-intro">{mode === 'mock' ? '先看见原型，再连接真实能力' : '已核实事件子集 · 不识别真实游戏'}</p>
      </header>

      <div className="mode-controls" aria-label="演示模式">
        <button className="mode-button" type="button" aria-pressed={mode === 'mock'} onClick={() => chooseMode('mock')}>模拟模式</button>
        <button className="mode-button" type="button" aria-pressed={mode === 'recorded_oracle'} onClick={() => chooseMode('recorded_oracle')}>Recorded 模式</button>
      </div>

      {mode === 'recorded_oracle' ? (
        <section className="replay-panel" aria-label="离线回放控制">
          <label className="replay-import">
            导入本地回放 JSON
            <input type="file" accept=".json,application/json" disabled={importing} onChange={event => {
              const file = event.currentTarget.files?.[0];
              event.currentTarget.value = '';
              if (file) void importFile(file);
            }} />
          </label>
          <p className="replay-status" role="status">{importing ? '正在读取本地文件' : replayStatus} · <span>{timeline}</span></p>
          <div className="replay-buttons">
            <button className="demo-button primary-button" type="button" disabled={!replay || importing || snapshot?.status === 'complete'} onClick={() => {
              if (!replay) return;
              setSnapshot(snapshot?.status === 'playing' ? replay.pause() : snapshot?.status === 'paused' ? replay.resume() : replay.start());
            }}>{snapshot?.status === 'playing' ? '暂停' : snapshot?.status === 'paused' ? '继续' : '开始回放'}</button>
            <button className="demo-button reset-button" type="button" disabled={!replay || importing} onClick={() => { if (replay) setSnapshot(replay.restart()); }}>重新播放</button>
          </div>
          <div className="mode-controls speed-controls" aria-label="回放速度">
            {([1, 4] as const).map(speed => <button key={speed} className="mode-button" type="button"
              disabled={!replay || importing} aria-pressed={(snapshot?.speed ?? 1) === speed}
              onClick={() => { if (replay) setSnapshot(replay.setSpeed(speed)); }}>{speed}×</button>)}
          </div>
          <p className="replay-note">事件时间是引擎首次出现的离线定位，不是实时确认时间。Witch 的实际确认延迟仍为 3 秒。</p>
          {demo ? <p className="replay-note">已导入 {demo.events.length} 条核实事件；{demo.excludedUnscoredEventCount} 条未计分输出在导出阶段排除，不进入卡组。</p> : null}
          <p className="replay-note">切换模式会重置回放；离开 App 自动暂停。本地文件仅在内存中读取。</p>
          {importError ? <p className="event-error" role="alert">{importError}</p> : null}
        </section>
      ) : null}

      <DiscoveryHud cardIds={discovery.cardIds} source={mode} />
      <DiscoverySlots {...discovery} />
      <EventHistory events={activeState.events} source={mode} />

      {activeState.error ? <p className="event-error" role="alert">{activeState.error.message}</p> : null}

      {mode === 'mock' ? <div className="demo-controls grid gap-2.5" aria-label="模拟事件控制">
        <button
          className="demo-button primary-button"
          type="button"
          disabled={!nextEvent}
          onClick={() => {
            if (nextEvent) dispatch({ type: 'event', event: nextEvent });
          }}
        >
          {playLabel}
        </button>
        <button
          className="demo-button reset-button"
          type="button"
          disabled={state.events.length === 0 && state.error === null}
          onClick={() => dispatch({ type: 'reset' })}
        >
          重置
        </button>
      </div> : null}

      <footer className="app-footer">真实游戏 HUD 已关闭</footer>
    </main>
  );
}
