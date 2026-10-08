interface CardDisplay {
  readonly label: string;
  readonly name: string;
  readonly letter: string;
}

const cards: ReadonlyMap<string, CardDisplay> = new Map([
  ['witch', { label: 'Witch', name: '女巫', letter: 'W' }],
  ['balloon', { label: 'Balloon', name: '气球兵', letter: 'B' }],
  ['royal_hogs', { label: 'Royal Hogs', name: '皇家野猪', letter: 'R' }],
  ['flying_machine', { label: 'Flying Machine', name: '飞行器', letter: 'F' }],
  ['golden_knight', { label: 'Golden Knight', name: '黄金骑士', letter: 'G' }],
  ['minions', { label: 'Minions', name: '亡灵', letter: 'M' }],
]);

export function getCardDisplay(cardId: string): CardDisplay {
  return cards.get(cardId) ?? { label: cardId, name: cardId, letter: cardId[0]?.toUpperCase() ?? '?' };
}
