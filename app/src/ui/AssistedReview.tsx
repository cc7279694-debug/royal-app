import { useEffect, useReducer, useRef, useState } from 'react';
import type { AssistedEvidence, CandidateOwner } from '../assisted/contract';
import { AssistedSource } from '../assisted/import';
import { assistedReducer, createAssistedState, getConfirmedDiscovery, type AssistedAction, type CandidateReview } from '../assisted/review-state';
import { DiscoveryHud, DiscoverySlots } from './Discovery';
import { getCardDisplay } from './card-display';

const ownerNames = { own: '己方', opponent: '对手', unknown: 'Unknown / 未知' };
const statusNames = { pending: '待确认', confirmed: '已人工确认', excluded: '已排除' };
const suggestedIds = ['witch', 'royal_hogs', 'flying_machine', 'golden_knight', 'minions',
  'hog_rider', 'goblin_barrel', 'firecracker', 'balloon'];

function OwnerSelect({ value, onChange, label }: {
  readonly value: CandidateOwner; readonly onChange: (value: CandidateOwner) => void; readonly label: string;
}) {
  return <label className="assisted-field">{label}<select value={value} onChange={event => onChange(event.currentTarget.value as CandidateOwner)}>
    <option value="opponent">对手</option><option value="own">己方</option><option value="unknown">Unknown / 未知</option>
  </select></label>;
}

function CardSuggestions({ id }: { readonly id: string }) {
  return <datalist id={id}>{suggestedIds.map(cardId => <option key={cardId} value={cardId}>{getCardDisplay(cardId).name}</option>)}</datalist>;
}

export function CandidateEvidence({ evidence }: { readonly evidence: AssistedEvidence }) {
  const [broken, setBroken] = useState(false);
  return <figure className="candidate-evidence">
    <figcaption>检测器候选框（未经GT确认）<span>{evidence.timestamp.toFixed(3)} 秒 · {evidence.frame_id}</span></figcaption>
    {broken ? <p className="event-error" role="alert">截图无法显示；请排查文件，不要依赖缺失截图确认候选。</p> :
      <div className="evidence-image" style={{ aspectRatio: `${evidence.source_width} / ${evidence.source_height}` }}>
        <img src={evidence.image_data_url} alt={`录像证据帧 ${evidence.frame_id}，${evidence.timestamp.toFixed(3)} 秒`} loading="lazy" onError={() => setBroken(true)} />
        {evidence.bboxes.map(([x1, y1, x2, y2], index) => <span key={index} className="candidate-box" aria-hidden="true" style={{
          left: `${x1 / evidence.source_width * 100}%`, top: `${y1 / evidence.source_height * 100}%`,
          width: `${(x2 - x1) / evidence.source_width * 100}%`, height: `${(y2 - y1) / evidence.source_height * 100}%`,
        }}><span>{index + 1}</span></span>)}
      </div>}
    <p className="replay-note">原始截图 {evidence.source_width}×{evidence.source_height}；框按源像素坐标等比例展示。同帧可能有其他候选框。</p>
  </figure>;
}

export function CandidateEditor({ row, onAction }: {
  readonly row: CandidateReview; readonly onAction: (action: AssistedAction) => void;
}) {
  const [cardId, setCardId] = useState(row.cardId ?? '');
  const [selectedOwner, setSelectedOwner] = useState(row.owner);
  const normalized = cardId.trim().toLowerCase().replace(/[\s-]+/g, '_');
  const dirty = (normalized || null) !== row.cardId || selectedOwner !== row.owner;
  return <section className="candidate-editor" aria-label="候选审核">
    <div className="section-heading"><h2>{getCardDisplay(row.cardId ?? 'Unknown').name}</h2><span className={`review-status status-${row.status}`}>{statusNames[row.status]}</span></div>
    <p className="candidate-meta">{row.timestamp.toFixed(3)} 秒 · {ownerNames[row.owner]} · {row.raw ? `检测器候选 ${row.raw.evidence_level}` : '手动补漏'}</p>
    <p className="candidate-id">{row.candidateId}</p>
    {row.raw ? <div className="raw-prediction">
      <p>原预测：{row.raw.card_id ?? 'Unknown'} · {ownerNames[row.raw.owner]}</p>
      <p>检测置信度：{row.raw.confidence === null ? 'Unknown' : row.raw.confidence.toFixed(3)}（不是校准后的出牌概率）</p>
      <p>检测器理由：{row.raw.reason}</p>
    </div> : <p className="replay-note">人工添加，无检测器预测或截图；先补充明确卡牌与阵营，再自行确认。</p>}
    <div className="review-actions">
      <button className="demo-button primary-button" type="button" disabled={dirty || row.owner !== 'opponent' || row.cardId === null || row.status === 'confirmed'}
        onClick={() => onAction({ type: 'confirm', candidateId: row.candidateId })}>确认对手卡牌</button>
      <button className="demo-button reset-button" type="button" disabled={row.status === 'excluded'}
        onClick={() => onAction({ type: 'exclude', candidateId: row.candidateId })}>排除候选</button>
      <button className="mode-button" type="button" disabled={row.status === 'pending'}
        onClick={() => onAction({ type: 'pending', candidateId: row.candidateId })}>恢复待确认</button>
    </div>
    <form className="correction-form" onSubmit={event => { event.preventDefault(); onAction({ type: 'correct', candidateId: row.candidateId, cardId: normalized || null, owner: selectedOwner }); }}>
      <label className="assisted-field">修正卡牌 ID（空白表示 Unknown）<input value={cardId} list="review-card-ids" maxLength={64}
        autoCapitalize="none" autoCorrect="off" spellCheck={false} onChange={event => setCardId(event.currentTarget.value)} /></label>
      <CardSuggestions id="review-card-ids" />
      <OwnerSelect label="修正阵营" value={selectedOwner} onChange={setSelectedOwner} />
      <button className="mode-button" type="submit">应用修正</button>
      <p className="replay-note">修正保留原预测，并恢复待确认。卡牌 ID 手动输入仅代表你的选择，不代表检测器支持该卡牌。</p>
      {dirty ? <p className="replay-note">请先应用修正，再确认对手卡牌。</p> : null}
    </form>
  </section>;
}

function ManualCandidate({ onAction }: { readonly onAction: (action: AssistedAction) => void }) {
  const [cardId, setCardId] = useState('');
  const [selectedOwner, setSelectedOwner] = useState<CandidateOwner>('unknown');
  const [timestamp, setTimestamp] = useState('0');
  return <details className="manual-candidate"><summary>手动补漏 / 添加 Unknown</summary>
    <form onSubmit={event => { event.preventDefault(); onAction({ type: 'manual', cardId: cardId.trim() || null, owner: selectedOwner, timestamp: timestamp.trim() ? Number(timestamp) : NaN }); }}>
      <label className="assisted-field">手动卡牌 ID（留空保留 Unknown）<input value={cardId} list="manual-card-ids" maxLength={64}
        autoCapitalize="none" autoCorrect="off" spellCheck={false} onChange={event => setCardId(event.currentTarget.value)} /></label>
      <CardSuggestions id="manual-card-ids" />
      <OwnerSelect label="手动阵营" value={selectedOwner} onChange={setSelectedOwner} />
      <label className="assisted-field">录像时间（秒）<input type="number" min="0" max="86400" step="any" required value={timestamp} onChange={event => setTimestamp(event.currentTarget.value)} /></label>
      <button className="mode-button" type="submit">添加待确认候选</button>
      <p className="replay-note">仅添加审核记录；Unknown 和己方不会进入对手卡组。手动选择不是检测器输出。</p>
    </form>
  </details>;
}

export function AssistedReview() {
  const [state, dispatch] = useReducer(assistedReducer, null, () => createAssistedState());
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const token = useRef(0);
  useEffect(() => () => { token.current += 1; }, []);
  const discovery = getConfirmedDiscovery(state);
  const row = state.rows.find(item => item.candidateId === selectedId) ?? state.rows[0];
  const screenshotMap = new Map(state.packet?.evidence.map(item => [item.evidence_id, item]) ?? []);
  const confirmed = state.rows.filter(item => item.status === 'confirmed').length;
  const excluded = state.rows.filter(item => item.status === 'excluded').length;

  async function importFile(file: File) {
    const currentToken = ++token.current;
    setImporting(true);
    setImportError(null);
    try {
      const packet = await AssistedSource.fromFile(file);
      if (currentToken !== token.current) return;
      dispatch({ type: 'load', packet });
      setSelectedId(packet.candidates[0]?.candidate_id ?? null);
    } catch {
      if (currentToken === token.current) setImportError('候选文件无效或截图校验失败。请导入专用本地 JSON（最大 24 MiB）；原审核记录已保留。');
    } finally {
      if (currentToken === token.current) setImporting(false);
    }
  }

  function onAction(action: AssistedAction) {
    if (importing) return;
    dispatch(action);
    if (action.type === 'manual') setSelectedId(null);
  }

  return <div className="assisted-panel" aria-label="离线 Assisted 候选审核">
    <section className="replay-panel">
      <label className="replay-import">导入本地候选 JSON<input type="file" accept=".json,application/json" disabled={importing} onChange={event => {
        const file = event.currentTarget.files?.[0]; event.currentTarget.value = ''; if (file) void importFile(file);
      }} /></label>
      <p className="replay-status" role="status">{importing ? '正在验证本地候选与截图' : state.packet ? `${state.packet.match_id} · ${state.packet.candidates.length} 条检测器候选` : '等待本地候选文件'}</p>
      <p className="replay-note">最多 24 MiB，截图仅在本地内存读取。所有导入项先为待确认。重置、切换模式或重新打开 App 会清空审核，需要重新导入。</p>
      <p className="replay-note">检测器候选不是已确认出牌。截图是局部抽样，未发现不等于不存在；不连接游戏，不生成出牌、循环或圣水结论。</p>
      {state.packet ? <p className="replay-note">原始 {state.packet.summary.total_match_candidates} 条候选，本包导出 {state.packet.summary.exported_candidates} 条，排除 {state.packet.summary.excluded_candidates} 条。来源哈希用于绑定，不是真实性认证。</p> : null}
      <button className="mode-button" type="button" disabled={!state.packet && !importing} onClick={() => {
        token.current += 1; dispatch({ type: 'reset' }); setSelectedId(null); setImporting(false); setImportError(null);
      }}>重置 Assisted</button>
      {importError ? <p className="event-error" role="alert">{importError}</p> : null}
    </section>
    <DiscoveryHud cardIds={discovery.cardIds} source="assisted" />
    <DiscoverySlots {...discovery} confirmed />
    {state.packet ? <>
      <p className="review-counts" role="status">待确认 {state.rows.length - confirmed - excluded} · 已确认记录 {confirmed} · 已排除 {excluded}</p>
      <fieldset className="assisted-workspace" disabled={importing}>
        <label className="assisted-field">查看候选<select value={row?.candidateId ?? ''} onChange={event => setSelectedId(event.currentTarget.value)}>
          {state.rows.map(item => <option key={item.candidateId} value={item.candidateId}>{item.timestamp.toFixed(2)}s · {getCardDisplay(item.cardId ?? 'Unknown').name} · {statusNames[item.status]}</option>)}
        </select></label>
        {row ? <>
          <CandidateEditor key={`${row.candidateId}:${row.cardId}:${row.owner}`} row={row} onAction={onAction} />
          {row.raw?.evidence_ids.map((evidenceId, index) => {
            const image = screenshotMap.get(evidenceId);
            return image ? <details key={evidenceId} className="evidence-details" open={index === 0}><summary>查看证据 {index + 1} · {image.timestamp.toFixed(3)} 秒</summary><CandidateEvidence key={evidenceId} evidence={image} /></details> : null;
          })}
        </> : null}
        <ManualCandidate onAction={action => {
          onAction(action);
          if (action.type === 'manual') {
            let suffix = state.rows.length + 1;
            while (state.rows.some(item => item.candidateId === `manual:${suffix}`)) suffix++;
            setSelectedId(`manual:${suffix}`);
          }
        }} />
      </fieldset>
      <section className="review-records" aria-label="候选审核记录"><h2>候选审核记录</h2>
        <ol>{state.rows.map(item => <li key={item.candidateId}><button type="button" disabled={importing} onClick={() => setSelectedId(item.candidateId)}>
          <span>{item.timestamp.toFixed(2)}s · {getCardDisplay(item.cardId ?? 'Unknown').name}</span>
          <span>{ownerNames[item.owner]} · {statusNames[item.status]} · {item.decisionSource === 'manual' ? '手动' : item.decisionSource === 'user_choice' ? '人工选择' : '检测器原候选'}</span>
        </button></li>)}</ol>
      </section>
    </> : null}
    {state.error ? <p className="event-error" role="alert">{state.error}</p> : null}
  </div>;
}
