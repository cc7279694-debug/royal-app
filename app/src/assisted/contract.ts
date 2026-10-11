export type CandidateOwner = 'own' | 'opponent' | 'unknown';
export type SourceBBox = readonly [number, number, number, number];

export interface AssistedCandidate {
  readonly candidate_id: string;
  readonly card_id: string | null;
  readonly owner: CandidateOwner;
  readonly timestamp: number;
  readonly confirmed_at: number | null;
  readonly confidence: number | null;
  readonly evidence_level: 'STRONG' | 'MEDIUM' | 'WEAK';
  readonly kind: 'direct' | 'grouped' | null;
  readonly source_observation_ids: readonly string[];
  readonly source_appearance_groups: readonly string[];
  readonly evidence_ids: readonly string[];
  readonly reason: string;
}

export interface AssistedEvidence {
  readonly evidence_id: string;
  readonly frame_id: string;
  readonly timestamp: number;
  readonly raw_pts: number;
  readonly time_base: string;
  readonly source_width: number;
  readonly source_height: number;
  readonly bboxes: readonly SourceBBox[];
  readonly image_data_url: string;
  readonly image_sha256: string;
}

export interface AssistedPacket {
  readonly schema: 'offline_assisted_candidates_v1';
  readonly packet_id: string;
  readonly match_id: string;
  readonly provenance: {
    readonly recording_sha256: string;
    readonly prediction_sha256: string;
    readonly config_sha256: string;
    readonly replay_sha256: string;
    readonly engine_rule_version: string;
    readonly input_source: 'katacr_prediction';
    readonly event_gt_used_as_input: false;
  };
  readonly candidates: readonly AssistedCandidate[];
  readonly evidence: readonly AssistedEvidence[];
  readonly summary: {
    readonly total_match_candidates: number;
    readonly exported_candidates: number;
    readonly excluded_candidates: number;
    readonly exclusion_reasons: {
      readonly owner_guard: number;
      readonly unsupported_card: number;
      readonly insufficient_evidence: number;
    };
    readonly raw_candidate_inventory_sha256: string;
    readonly evidence_frame_selection: 'first_middle_last_of_candidate_observations';
    readonly confidence_semantics: string;
    readonly image_display_semantics: string;
    readonly coverage_semantics: string;
  };
}
