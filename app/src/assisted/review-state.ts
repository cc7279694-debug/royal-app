import type { AssistedCandidate, AssistedPacket, CandidateOwner } from './contract';

export interface CandidateReview {
  readonly candidateId: string;
  readonly raw: AssistedCandidate | null;
  readonly cardId: string | null;
  readonly owner: CandidateOwner;
  readonly timestamp: number;
  readonly status: 'pending' | 'confirmed' | 'excluded';
  readonly decisionSource: 'user_choice' | 'manual' | null;
}

export interface AssistedState {
  readonly packet: AssistedPacket | null;
  readonly rows: readonly CandidateReview[];
  readonly error: string | null;
}

export type AssistedAction =
  | { readonly type: 'load'; readonly packet: AssistedPacket }
  | { readonly type: 'reset' }
  | { readonly type: 'confirm' | 'exclude' | 'pending'; readonly candidateId: string }
  | { readonly type: 'correct'; readonly candidateId: string; readonly cardId: string | null; readonly owner: CandidateOwner }
  | { readonly type: 'manual'; readonly cardId: string | null; readonly owner: CandidateOwner; readonly timestamp: number };

export function createAssistedState(packet: AssistedPacket | null = null): AssistedState {
  return { packet, rows: packet?.candidates.map(raw => Object.freeze({ candidateId: raw.candidate_id, raw,
    cardId: raw.card_id, owner: raw.owner, timestamp: raw.timestamp, status: 'pending', decisionSource: null })) ?? [], error: null };
}

function normalizeCardId(value: string | null): string | null | undefined {
  if (value === null) return null;
  const normalized = value.trim().toLowerCase().replace(/[\s-]+/g, '_');
  return normalized !== 'unknown' && /^[a-z][a-z0-9_]{0,63}$/.test(normalized) ? normalized : undefined;
}

function validOwner(value: CandidateOwner): boolean {
  return value === 'own' || value === 'opponent' || value === 'unknown';
}

export function assistedReducer(state: AssistedState, action: AssistedAction): AssistedState {
  if (action.type === 'reset') return createAssistedState();
  if (action.type === 'load') return createAssistedState(action.packet);
  if (!state.packet) return { ...state, error: '请先导入本地候选文件。' };
  if (action.type === 'manual') {
    const cardId = normalizeCardId(action.cardId);
    if (cardId === undefined || !validOwner(action.owner) || !Number.isFinite(action.timestamp)
      || action.timestamp < 0 || action.timestamp > 86400 || state.rows.length >= 5000) {
      return { ...state, error: '手动候选无效。请输入规范卡牌 ID、阵营和 0–86400 秒的时间。' };
    }
    let suffix = state.rows.length + 1;
    while (state.rows.some(row => row.candidateId === `manual:${suffix}`)) suffix++;
    const row: CandidateReview = Object.freeze({ candidateId: `manual:${suffix}`, raw: null, cardId, owner: action.owner,
      timestamp: action.timestamp, status: 'pending', decisionSource: 'manual' });
    return { ...state, rows: [...state.rows, row], error: null };
  }
  const existing = state.rows.find(row => row.candidateId === action.candidateId);
  if (!existing) return { ...state, error: '候选已不存在，请重新选择。' };
  let replacement: CandidateReview;
  const decisionSource = existing.raw ? 'user_choice' : 'manual';
  if (action.type === 'correct') {
    const cardId = normalizeCardId(action.cardId);
    if (cardId === undefined || !validOwner(action.owner)) return { ...state, error: '卡牌 ID 或阵营无效，原审核记录已保留。' };
    replacement = { ...existing, cardId, owner: action.owner, status: 'pending', decisionSource };
  } else if (action.type === 'confirm') {
    if (existing.owner !== 'opponent' || existing.cardId === null || normalizeCardId(existing.cardId) === undefined) {
      return { ...state, error: '只有已明确选择卡牌和对手阵营的候选才能进入确认卡组。' };
    }
    replacement = { ...existing, status: 'confirmed', decisionSource };
  } else {
    replacement = { ...existing, status: action.type === 'exclude' ? 'excluded' : 'pending', decisionSource };
  }
  return { ...state, rows: state.rows.map(row => row === existing ? Object.freeze(replacement) : row), error: null };
}

export function getConfirmedDiscovery(state: AssistedState): {
  readonly cardIds: readonly string[]; readonly overflowCardIds: readonly string[];
} {
  const confirmed = state.rows.filter(row => row.status === 'confirmed' && row.owner === 'opponent' && row.cardId !== null)
    .sort((a, b) => a.timestamp - b.timestamp || (a.candidateId < b.candidateId ? -1 : a.candidateId > b.candidateId ? 1 : 0));
  const unique = [...new Set(confirmed.map(row => row.cardId!))];
  return { cardIds: unique.slice(0, 8), overflowCardIds: unique.slice(8) };
}
