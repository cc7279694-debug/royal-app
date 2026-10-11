import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { App } from '../App';
import { AssistedReview, CandidateEvidence, CandidateEditor } from './AssistedReview';
import { AssistedSource } from '../assisted/import';
import { createAssistedState } from '../assisted/review-state';
import { makePacket } from '../assisted/test-fixture';
import { DiscoveryHud, DiscoverySlots } from './Discovery';
import { getCardDisplay } from './card-display';

it('offers Assisted alongside unchanged Mock and Recorded and explains local recovery', () => {
  const app = renderToStaticMarkup(createElement(App));
  expect(app).toContain('Assisted 模式');
  expect(app).toContain('Recorded 模式');
  expect(app).toContain('播放模拟事件');
  const panel = renderToStaticMarkup(createElement(AssistedReview));
  expect(panel).toContain('导入本地候选 JSON');
  expect(panel).toContain('重新打开');
  expect(panel).toContain('24 MiB');
});

it('renders native evidence with source-coordinate candidate boxes and an explicit unverified label', async () => {
  const packet = await AssistedSource.fromJSON(makePacket());
  const html = renderToStaticMarkup(createElement(CandidateEvidence, { evidence: packet.evidence[0]! }));
  expect(html).toContain('检测器候选框（未经GT确认）');
  expect(html).toContain('data:image/jpeg;base64,');
  expect(html).toContain('width:100%');
  expect(html).toContain('frame-a');
});

it('renders pending review actions without inventing a card-play event', async () => {
  const packet = await AssistedSource.fromJSON(makePacket());
  const row = createAssistedState(packet).rows[0]!;
  const html = renderToStaticMarkup(createElement(CandidateEditor, { row, onAction: () => undefined }));
  expect(html).toContain('确认对手卡牌');
  expect(html).toContain('排除候选');
  expect(html).toContain('应用修正');
  expect(html).toContain('待确认');
  expect(html).not.toContain('已确认出牌');
});

it('escapes external detector reason text in the actual reviewer UI', async () => {
  const input = makePacket();
  input.candidates[0]!.reason = '<script>alert(1)</script>';
  const row = createAssistedState(await AssistedSource.fromJSON(input)).rows[0]!;
  const html = renderToStaticMarkup(createElement(CandidateEditor, { row, onAction: () => undefined }));
  expect(html).toContain('&lt;script&gt;');
  expect(html).not.toContain('<script>');
});

it('labels Assisted cards as human confirmation and keeps new display names independent of detector support', () => {
  const hud = renderToStaticMarkup(createElement(DiscoveryHud, { cardIds: ['firecracker'], source: 'assisted' }));
  const slots = renderToStaticMarkup(createElement(DiscoverySlots, { cardIds: ['firecracker'], overflowCardIds: [], confirmed: true }));
  expect(hud).toContain('已确认');
  expect(hud).toContain('人工确认');
  expect(hud).not.toContain('离线 Oracle 回放');
  expect(slots).toContain('已确认的对手卡组');
  expect(['hog_rider', 'goblin_barrel', 'firecracker'].map(id => getCardDisplay(id).name)).toEqual(['野猪骑士', '哥布林飞桶', '烟花炮手']);
});

it('blocks candidate import until recovery completes rather than overwriting saved progress', () => {
  const panel = renderToStaticMarkup(createElement(AssistedReview));
  expect(panel).toMatch(/<input[^>]*type="file"[^>]*disabled/);
});

it('offers restart of the current review without the old immediate-clear reset control', () => {
  const panel = renderToStaticMarkup(createElement(AssistedReview));
  expect(panel).toContain('重新开始当前审核');
  expect(panel).not.toContain('重置 Assisted');
});
