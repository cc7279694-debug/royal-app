interface CardDisplay {
  readonly label: string;
  readonly name: string;
  readonly letter: string;
}

const cards: ReadonlyMap<string, CardDisplay> = new Map([
  ['witch', { label: 'Witch', name: '女巫', letter: 'W' }],
  ['balloon', { label: 'Balloon', name: '气球兵', letter: 'B' }],
]);

export function getCardDisplay(cardId: string): CardDisplay {
  return cards.get(cardId) ?? { label: cardId, name: cardId, letter: cardId[0]?.toUpperCase() ?? '?' };
}
