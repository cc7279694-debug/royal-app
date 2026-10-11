import { describe, expect, it } from 'vitest';
import { AssistedSource } from './import';
import { makePacket, syntheticJpeg } from './test-fixture';

describe('local assisted packet boundary', () => {
  it('imports a SHA-bound synthetic JPEG and preserves raw detector provenance without a decision', async () => {
    const input = makePacket();
    const before = JSON.stringify(input);
    const packet = await AssistedSource.fromJSON(input);
    expect(packet.candidates[0]?.card_id).toBe('witch');
    expect(packet.evidence[0]?.image_data_url).toBe(`data:image/jpeg;base64,${syntheticJpeg}`);
    expect(packet.provenance.event_gt_used_as_input).toBe(false);
    expect(JSON.stringify(input)).toBe(before);
    expect(Object.isFrozen(packet.candidates[0])).toBe(true);
  });

  it('reads a local UTF-8 BOM file without a filesystem plugin', async () => {
    const packet = await AssistedSource.fromFile(new File(['\uFEFF' + JSON.stringify(makePacket())], 'offline.json'));
    expect(packet.match_id).toBe('match-test');
  });

  it.each([
    ['root confirmation claim', (p: ReturnType<typeof makePacket>) => ({ ...p, confirmed: true })],
    ['candidate reviewer claim', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], reviewer: 'human' }] })],
    ['GT input', (p: ReturnType<typeof makePacket>) => ({ ...p, provenance: { ...p.provenance, event_gt_used_as_input: true } })],
    ['wrong source', (p: ReturnType<typeof makePacket>) => ({ ...p, provenance: { ...p.provenance, input_source: 'oracle' } })],
    ['invalid hash', (p: ReturnType<typeof makePacket>) => ({ ...p, provenance: { ...p.provenance, config_sha256: 'none' } })],
    ['duplicate candidate', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [p.candidates[0], p.candidates[0]] })],
    ['duplicate evidence', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [p.evidence[0], p.evidence[0]] })],
    ['missing evidence', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], evidence_ids: ['missing'] }] })],
    ['orphan evidence', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [...p.evidence, { ...p.evidence[0], evidence_id: 'orphan' }] })],
    ['negative time', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], timestamp: -1 }] })],
    ['invalid confirmation time', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], confirmed_at: 0.5 }] })],
    ['nonfinite confidence', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], confidence: Infinity }] })],
    ['invalid owner', (p: ReturnType<typeof makePacket>) => ({ ...p, candidates: [{ ...p.candidates[0], owner: 'enemy' }] })],
    ['URL image', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], image_data_url: 'https://example.com/image.jpg' }] })],
    ['local image path', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], image_data_url: 'file:///secret.jpg' }] })],
    ['SVG image', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], image_data_url: 'data:image/svg+xml;base64,PHN2Zy8+' }] })],
    ['fake JPEG MIME', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], image_data_url: 'data:image/jpeg;base64,PHN2Zy8+' }] })],
    ['wrong image hash', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], image_sha256: '0'.repeat(64) }] })],
    ['dimension mismatch', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], source_width: 2 }] })],
    ['out-of-frame bbox', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], bboxes: [[0, 0, 2, 1]] }] })],
    ['reversed bbox', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], bboxes: [[1, 0, 0, 1]] }] })],
    ['fractional raw PTS', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], raw_pts: 1.5 }] })],
    ['zero time base', (p: ReturnType<typeof makePacket>) => ({ ...p, evidence: [{ ...p.evidence[0], time_base: '1/0' }] })],
    ['invalid counts', (p: ReturnType<typeof makePacket>) => ({ ...p, summary: { ...p.summary, exported_candidates: 10 } })],
  ])('rejects %s before any review state loads', async (_label, mutate) => {
    await expect(AssistedSource.fromJSON(mutate(makePacket()))).rejects.toThrow();
  });

  it('accepts explicit unknown card/owner and nullable detector fields as pending-capable data', async () => {
    const input = makePacket();
    input.candidates[0] = { ...input.candidates[0]!, card_id: null, owner: 'unknown', confidence: null, confirmed_at: null, kind: null };
    expect((await AssistedSource.fromJSON(input)).candidates[0]?.card_id).toBeNull();
  });

  it('rejects excess screenshot count and oversize decoded images', async () => {
    const input = makePacket();
    await expect(AssistedSource.fromJSON({ ...input, evidence: Array.from({ length: 129 }, (_, i) => ({ ...input.evidence[0], evidence_id: `e-${i}` })) })).rejects.toThrow();
    input.evidence[0]!.image_data_url = 'data:image/jpeg;base64,' + Buffer.alloc(512 * 1024 + 1).toString('base64');
    await expect(AssistedSource.fromJSON(input)).rejects.toThrow();
  });

  it('rejects empty, malformed and larger-than-24MiB files', async () => {
    await expect(AssistedSource.fromFile(new File([], 'empty.json'))).rejects.toThrow();
    await expect(AssistedSource.fromFile(new File(['{bad'], 'bad.json'))).rejects.toThrow();
    await expect(AssistedSource.fromFile(new File(['x'.repeat(24 * 1024 * 1024 + 1)], 'large.json'))).rejects.toThrow();
  });
});
