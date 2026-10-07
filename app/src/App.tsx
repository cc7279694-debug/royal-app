import { useReducer } from 'react';
import { mockEvents } from './demo/mock-events';
import { createTrackerState, getDiscovery, trackerReducer } from './domain/tracker';
import { DiscoveryHud, DiscoverySlots } from './ui/Discovery';
import { EventHistory } from './ui/EventHistory';

export function App() {
  const [state, dispatch] = useReducer(trackerReducer, null, createTrackerState);
  const discovery = getDiscovery(state);
  const nextEvent = mockEvents[state.events.length];
  const playLabel = nextEvent
    ? state.events.length === 0 ? '播放模拟事件' : '播放下一个事件'
    : '模拟事件已播完';

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-row flex items-center justify-between gap-3">
          <h1>Clash Tracker</h1>
          <span className="mock-badge">模拟演示</span>
        </div>
        <p className="app-intro">先看见原型，再连接真实能力</p>
      </header>

      <DiscoveryHud cardIds={discovery.cardIds} />
      <DiscoverySlots {...discovery} />
      <EventHistory events={state.events} />

      {state.error ? <p className="event-error" role="alert">{state.error.message}</p> : null}

      <div className="demo-controls grid gap-2.5" aria-label="模拟事件控制">
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
      </div>

      <footer className="app-footer">真实游戏 HUD 已关闭</footer>
    </main>
  );
}
