import { createHash } from 'node:crypto';

// A synthetic one-pixel grey JPEG, generated locally; no gameplay pixels.
export const syntheticJpeg = '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD1KiiigD//2Q==';

export function makePacket() {
  return {
    schema: 'offline_assisted_candidates_v1', packet_id: 'packet-test', match_id: 'match-test',
    provenance: {
      recording_sha256: 'a'.repeat(64), prediction_sha256: 'b'.repeat(64),
      config_sha256: 'c'.repeat(64), replay_sha256: 'd'.repeat(64),
      engine_rule_version: 'test-v1', input_source: 'katacr_prediction', event_gt_used_as_input: false,
    },
    candidates: [{
      candidate_id: 'candidate-a', card_id: 'witch' as string | null, owner: 'opponent', timestamp: 1,
      confirmed_at: 1.5 as number | null, confidence: 0.8 as number | null,
      evidence_level: 'STRONG', kind: 'direct' as string | null,
      source_observation_ids: ['observation-a'], source_appearance_groups: ['appearance-a'],
      evidence_ids: ['evidence-a'], reason: 'source detector proposal',
    }],
    evidence: [{
      evidence_id: 'evidence-a', frame_id: 'frame-a', timestamp: 1, raw_pts: 1000,
      time_base: '1/1000', source_width: 1, source_height: 1,
      bboxes: [[0, 0, 1, 1]], image_data_url: `data:image/jpeg;base64,${syntheticJpeg}`,
      image_sha256: createHash('sha256').update(Buffer.from(syntheticJpeg, 'base64')).digest('hex'),
    }],
    summary: {
      total_match_candidates: 3, exported_candidates: 1, excluded_candidates: 2,
      exclusion_reasons: { owner_guard: 1, unsupported_card: 1, insufficient_evidence: 0 },
      raw_candidate_inventory_sha256: 'e'.repeat(64),
      evidence_frame_selection: 'first_middle_last_of_candidate_observations',
      confidence_semantics: 'maximum source detector confidence; not calibrated event probability',
      image_display_semantics: 'native source JPEG; detector boxes unverified',
      coverage_semantics: 'partial candidate selection; not exhaustive match coverage',
    },
  };
}
