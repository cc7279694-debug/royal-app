import { getCardDisplay } from './card-display';

interface DiscoveryProps {
  readonly cardIds: readonly string[];
  readonly overflowCardIds: readonly string[];
}

export function DiscoveryHud({ cardIds, source = 'mock' }: Pick<DiscoveryProps, 'cardIds'> & {
  readonly source?: 'mock' | 'recorded_oracle';
}) {
  const names = cardIds.map((cardId) => getCardDisplay(cardId).name).join(' · ');

  return (
    <section className="discovery-hud" aria-label={source === 'mock' ? 'App 内部模拟 HUD' : 'App 内部离线 Oracle HUD'}>
      <p className="hud-metric" role="status" aria-live="polite" aria-atomic="true">
        <span>已发现</span>
        <strong>{cardIds.length}/8</strong>
      </p>
      <div className="hud-description">
        <p className="hud-names">{names || (source === 'mock' ? '等待模拟事件' : '等待离线事件')}</p>
        <p className="hud-source">{source === 'mock' ? '仅模拟事件 · 未连接游戏' : '离线 Oracle 回放 · 未连接游戏'}</p>
      </div>
    </section>
  );
}

export function DiscoverySlots({ cardIds, overflowCardIds }: DiscoveryProps) {
  return (
    <section className="discovery-section" aria-labelledby="discovery-heading">
      <div className="section-heading">
        <h2 id="discovery-heading">已发现的兵种</h2>
        <span className="section-count">{cardIds.length} / 8</span>
      </div>
      <ol className="discovery-slots grid grid-cols-4 gap-2.5" aria-label="八个发现卡槽">
        {Array.from({ length: 8 }, (_, index) => {
          const cardId = cardIds[index];
          const card = cardId ? getCardDisplay(cardId) : undefined;
          return (
            <li
              key={index}
              className={`discovery-slot ${card ? 'is-discovered' : 'is-empty'}`}
              aria-label={`卡槽 ${index + 1}：${card ? card.name : '未发现'}`}
            >
              <span className="slot-letter" aria-hidden="true">{card?.letter ?? '—'}</span>
              {card ? <span className="slot-label">{card.label}</span> : null}
            </li>
          );
        })}
      </ol>
      {overflowCardIds.length > 0 ? (
        <p className="overflow-notice" role="status">
          已达到 8 种上限，另有 {overflowCardIds.length} 种保留在事件记录中：
          {overflowCardIds.map((cardId) => getCardDisplay(cardId).name).join('、')}。
        </p>
      ) : null}
    </section>
  );
}
