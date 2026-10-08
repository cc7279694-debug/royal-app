import type { OpponentCardPlayed } from '../domain/tracker';
import { getCardDisplay } from './card-display';

function formatTimestamp(seconds: number): string {
  const wholeSeconds = Math.floor(seconds);
  return `${Math.floor(wholeSeconds / 60).toString().padStart(2, '0')}:${(wholeSeconds % 60).toString().padStart(2, '0')}`;
}

export function EventHistory({ events, source = 'mock' }: {
  readonly events: readonly OpponentCardPlayed[];
  readonly source?: 'mock' | 'recorded_oracle';
}) {
  return (
    <section className="history-section" aria-labelledby="history-heading">
      <h2 id="history-heading">事件记录</h2>
      <div className="history-panel">
        {events.length === 0 ? (
          <div className="history-empty">
            <p>尚无事件</p>
            <p>{source === 'mock' ? '点击下方按钮开始模拟' : '导入本地 JSON 后开始离线回放'}</p>
          </div>
        ) : (
          <ol className="event-history" aria-label={source === 'mock' ? '模拟出牌事件记录' : '离线 Oracle 出牌事件记录'}>
            {events.map((event) => (
              <li className="history-row" key={event.eventId}>
                <span className="event-time">{formatTimestamp(event.timestamp)}</span>
                <span className="event-card">{getCardDisplay(event.cardId).label}</span>
                <span className="event-source">{event.source === 'mock' ? '来源：模拟' : '来源：离线 Oracle'}</span>
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}
