import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { App } from '../App';
import { DiscoveryHud } from './Discovery';
import { EventHistory } from './EventHistory';
import { getCardDisplay } from './card-display';

it('labels all verified Oracle cards in the existing discovery UI', () => {
  expect(['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions']
    .map(id => getCardDisplay(id).name)).toEqual(['女巫', '皇家野猪', '飞行器', '黄金骑士', '亡灵']);
});

it('renders an explicit offline Oracle HUD without claiming mock or live detection', () => {
  const html = renderToStaticMarkup(createElement(DiscoveryHud, { cardIds: ['witch'], source: 'recorded_oracle' }));
  expect(html).toContain('离线 Oracle 回放');
  expect(html).toContain('1/8');
  expect(html).not.toContain('仅模拟事件');
});

it('displays recorded event source and actual engine timestamp rather than simulated labels', () => {
  const html = renderToStaticMarkup(createElement(EventHistory, { events: [
    { eventId: 'engine-witch', cardId: 'witch', timestamp: 32, confidence: null, source: 'recorded_oracle' },
  ], source: 'recorded_oracle' }));
  expect(html).toContain('00:32');
  expect(html).toContain('来源：离线 Oracle');
  expect(html).not.toContain('来源：模拟');
});

it('keeps the existing mock mode and offers a separate recorded mode initially at zero', () => {
  const html = renderToStaticMarkup(createElement(App));
  expect(html).toContain('模拟模式');
  expect(html).toContain('Recorded 模式');
  expect(html).toContain('播放模拟事件');
  expect(html).toContain('0/8');
  expect(html).toContain('真实游戏 HUD 已关闭');
});
