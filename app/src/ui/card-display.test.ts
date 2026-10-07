import { expect, it } from 'vitest';
import { getCardDisplay } from './card-display';

it.each([
  { cardId: 'constructor', expected: { label: 'constructor', name: 'constructor', letter: 'C' } },
  { cardId: 'toString', expected: { label: 'toString', name: 'toString', letter: 'T' } },
  { cardId: 'unknown-card', expected: { label: 'unknown-card', name: 'unknown-card', letter: 'U' } },
])('shows a literal fallback for uncatalogued card $cardId', ({ cardId, expected }) => {
  expect(getCardDisplay(cardId)).toEqual(expected);
});
