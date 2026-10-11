import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import type { AssistedEvidence, AssistedPacket, CandidateOwner } from '../assisted/contract';
import { AssistedSource } from '../assisted/import';
import { getConfirmedDiscovery, type AssistedAction, type CandidateReview } from '../assisted/review-state';
import { getAssistedSessionController } from '../assisted/session-controller';
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
  const [controller] = useState(getAssistedSessionController);
  const saved = useSyncExternalStore(controller.subscribe, controller.getSnapshot, controller.getSnapshot);
  const { state } = saved;
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [replacement, setReplacement] = useState<AssistedPacket | null>(null);
  const [confirmation, setConfirmation] = useState<'replace' | 'restart' | null>(null);
  const confirmationDialog = useRef<HTMLDialogElement>(null);
  const token = useRef(0);
  useEffect(() => { void controller.initialize(); }, [controller]);
  useEffect(() => () => { token.current += 1; }, []);
  useEffect(() => {
    const dialog = confirmationDialog.current;
    if (confirmation && dialog && !dialog.open) dialog.showModal();
  }, [confirmation]);
  const busy = importing || saved.phase !== 'ready' || confirmation !== null;
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
      if (controller.getSnapshot().state.packet) {
        setReplacement(packet);
        setConfirmation('replace');
      } else {
        await controller.importPacket(packet);
        if (currentToken === token.current) setSelectedId(null);
      }
    } catch {
      if (currentToken === token.current) setImportError('候选文件无效或截图校验失败。请导入专用本地 JSON（最大 24 MiB）；原审核记录已保留。');
    } finally {
      if (currentToken === token.current) setImporting(false);
    }
  }

  function onAction(action: AssistedAction) {
    if (busy) return;
    let manualId: string | null = null;
    if (action.type === 'manual') {
      let suffix = state.rows.length + 1;
      while (state.rows.some(item => item.candidateId === `manual:${suffix}`)) suffix++;
      manualId = `manual:${suffix}`;
    }
    void controller.applyAction(action).then(() => {
      if (manualId && controller.getSnapshot().state.rows.some(item => item.candidateId === manualId)) setSelectedId(manualId);
    });
  }

  async function confirmReplacement() {
    const choice = confirmation;
    const packet = replacement;
    setConfirmation(null);
    setReplacement(null);
    setImportError(null);
    if (choice === 'restart') await controller.restart();
    else if (choice === 'replace' && packet) await controller.importPacket(packet);
    setSelectedId(null);
  }

  return <div className="assisted-panel" aria-label="离线 Assisted 候选审核">
    <section className="replay-panel">
      <label className="replay-import">导入本地候选 JSON<input type="file" accept=".json,application/json" disabled={busy} onChange={event => {
        const file = event.currentTarget.files?.[0]; event.currentTarget.value = ''; if (file) void importFile(file);
      }} /></label>
      <p className="replay-status" role="status">{importing ? '正在验证本地候选与截图' : saved.phase === 'loading' ? '正在恢复上次审核' : state.packet ? `${state.packet.match_id} · ${state.packet.candidates.length} 条检测器候选` : '等待本地候选文件'}</p>
      <p className="session-save-status" role="status" aria-live="polite">{saved.phase === 'saving' ? '正在保存，请等待完成' : saved.phase === 'error' ? '本机存储异常 · 原有文件保留' : saved.phase === 'loading' ? '正在检查本机审核记录' : state.packet ? `已保存到本机 · 审核版本 ${saved.revision}` : '本机尚无审核会话'}</p>
      <p className="replay-note">最多 24 MiB。候选、审核与截图仅保存到本机，重新打开 App 可继续上次审核。所有新导入项先为待确认；切换模式不会清空审核。</p>
      <p className="replay-note">请等待显示“已保存到本机”后退出。卸载 App、清除应用数据或设备损坏仍可能丢失记录；本功能不等于备份。</p>
      <p className="replay-note">检测器候选不是已确认出牌。截图是局部抽样，未发现不等于不存在；不连接游戏，不生成出牌、循环或圣水结论。</p>
      {state.packet ? <p className="replay-note">原始 {state.packet.summary.total_match_candidates} 条候选，本包导出 {state.packet.summary.exported_candidates} 条，排除 {state.packet.summary.excluded_candidates} 条。来源哈希用于绑定，不是真实性认证。</p> : null}
      <button className="mode-button" type="button" disabled={!state.packet || busy} onClick={() => setConfirmation('restart')}>重新开始当前审核</button>
      {confirmation ? <dialog ref={confirmationDialog} className="session-confirmation" role="alertdialog" aria-modal="true" aria-labelledby="session-confirm-title" onCancel={event => {
        event.preventDefault(); setConfirmation(null); setReplacement(null);
      }}>
        <h2 id="session-confirm-title">{confirmation === 'replace' ? '替换当前审核？' : '重新开始当前审核？'}</h2>
        <p>{confirmation === 'replace' ? '新文件将替换当前审核会话，已有确认、排除、更正和手动补漏不会带入。' : '当前候选与截图保留，所有审核恢复待确认，手动补漏记录移除。'}</p>
        <p>取消会保留全部当前进度。</p>
        <div className="review-actions">
          <button className="mode-button" type="button" autoFocus onClick={() => { setConfirmation(null); setReplacement(null); }}>取消</button>
          <button className="demo-button primary-button" type="button" onClick={() => { void confirmReplacement(); }}>{confirmation === 'replace' ? '确认替换审核' : '确认重新开始'}</button>
        </div>
      </dialog> : null}
      {importError ? <p className="event-error" role="alert">{importError}</p> : null}
      {saved.error ? <div className="event-error" role="alert"><p>{saved.error}</p>
        <button className="mode-button" type="button" onClick={() => { void controller.retryRestore(); }}>重试恢复已保存审核</button>
        <p>失败的操作未计入已保存结果；不会自动清空或覆盖异常文件。</p>
      </div> : null}
    </section>
    <DiscoveryHud cardIds={discovery.cardIds} source="assisted" />
    <DiscoverySlots {...discovery} confirmed />
    {state.packet ? <>
      <p className="review-counts" role="status">待确认 {state.rows.length - confirmed - excluded} · 已确认记录 {confirmed} · 已排除 {excluded}</p>
      <fieldset className="assisted-workspace" disabled={busy}>
        <label className="assisted-field">查看候选<select value={row?.candidateId ?? ''} onChange={event => setSelectedId(event.currentTarget.value)}>
          {state.rows.map(item => <option key={item.candidateId} value={item.candidateId}>{item.timestamp.toFixed(2)}s · {getCardDisplay(item.cardId ?? 'Unknown').name} · {statusNames[item.status]}</option>)}
        </select></label>
        {row ? <>
          <CandidateEditor key={`${saved.sessionId}:${row.candidateId}:${row.cardId}:${row.owner}`} row={row} onAction={onAction} />
          {row.raw?.evidence_ids.map((evidenceId, index) => {
            const image = screenshotMap.get(evidenceId);
            return image ? <details key={evidenceId} className="evidence-details" open={index === 0}><summary>查看证据 {index + 1} · {image.timestamp.toFixed(3)} 秒</summary><CandidateEvidence key={evidenceId} evidence={image} /></details> : null;
          })}
        </> : null}
        <ManualCandidate key={saved.sessionId} onAction={onAction} />
      </fieldset>
      <section className="review-records" aria-label="候选审核记录"><h2>候选审核记录</h2>
        <ol>{state.rows.map(item => <li key={item.candidateId}><button type="button" disabled={busy} onClick={() => setSelectedId(item.candidateId)}>
          <span>{item.timestamp.toFixed(2)}s · {getCardDisplay(item.cardId ?? 'Unknown').name}</span>
          <span>{ownerNames[item.owner]} · {statusNames[item.status]} · {item.decisionSource === 'manual' ? '手动' : item.decisionSource === 'user_choice' ? '人工选择' : '检测器原候选'}</span>
        </button></li>)}</ol>
      </section>
    </> : null}
    {state.error ? <p className="event-error" role="alert">{state.error}</p> : null}
  </div>;
}
