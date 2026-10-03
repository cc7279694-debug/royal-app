# Module 2A — Lightweight Offline Evidence Preparation

Date: 2026-10-03. Status: **Revised proposal; Module 2A1 not implemented**.
This revision supersedes the heavier draft at 8f613a7. The current authorization
is documentation only, not permission to implement either internal stage.

## 1. Goal and safety

Use a few reviewed original frames plus complete visibility intervals to prepare
a one-card offline experiment. Preserve the user's priorities: no obstruction
of gameplay, account safety and local processing. No running-game access and no
zero-ban-risk promise. This revision reads no new private footage.

No uploads, ML installation/model/dataset download, inference/training, custom GUI,
Android, MediaProjection, HUD, game process/network access, synthetic input,
AccessibilityService or automation. Live features remain disabled behind
PROJECT.md's specific official-permission and project-approval gate. No database,
migration or app-stack decision is needed here.

## 2. Stage boundaries

| Stage | Responsibility | Entry / exclusion |
| --- | --- | --- |
| 2A1 Current Recording Evidence | Local index/contacts, manual match/card/occurrence review, 3–5 key boxes per play, complete positive/negative intervals, validation and insufficiency report | Separate implementation approval; no split/freeze system |
| 2A2 Independent Data and Split Freeze | Independence review, train/validation/test assignments, Evaluation Protocol, canonical digest, split lock and freeze CLI | At least a second independent complete match supplied, plus separate design/plan or explicit approval; not approved now |
| 2B Single Card Detection PoC | One class, timestamped visual Observation and independent-match evaluation | Accepted evidence/frozen independent test; no events/cycle/elixir |
| 3 Deployment Event Tracking | Multi-frame confirmation, temporal/spatial deduplication, ownership evidence, then OpponentCardPlayed | Separate module; only this stage produces gameplay events |

Manual annotations are evaluation evidence, not runtime OpponentCardPlayed events.
Opponent units cross the river; screen half alone cannot establish ownership.
2A1 commands are prepare / validate / review only. No freeze command, canonical
evidence digest, split lock or Evaluation Protocol implementation in 2A1.

## 3. Existing evidence and limits

Module 1 is accepted on main at e30ca01. The previous planning task reran 47 tests
and inspected the supplied recording; that is historical evidence, not a claim
of new test execution or video review in this revision.

One supplied recording includes pre-match screens, a battlefield, a visible
outcome and system UI. Match boundaries and individual plays stay local. Complete
match eligibility still requires checking initial transition, hidden deployments,
cuts and speed changes during 2A1.

**Inferno Dragon / 地狱飞龙 remains a pending-review candidate**, not a locked class.
Earlier inspection provisionally identified at least four independent candidate
deployments, a lower bound rather than an exhaustive verified count. 2A1 must
recheck opponent ownership, variant and absence → spawn → continued visibility
before candidate_gate=true. Preliminary notes alone do not formally pass it.

Other preliminary candidates include Skeleton Army, Bats and Goblin Barrel; no
complete deck is claimed. Unresolved units stay unknown; own troops, hand icons
and towers are not opponent plays. Hog Rider is not predefined.
One observed match, no finalized boxes and no independent locked test mean
**insufficient for 2B**. Successfully completing 2A1 may still yield insufficient.

## 4. Lightweight workflow and workload

1. Reuse Module1 unchanged: every5-second survey plus last actual frame; original
   PNGs, local index and contact pages (max12 thumbnails, 3 columns, fit224x480
   preserving ratio, actual-time labels). Input SHA256 checked before/after.
2. Human watches the whole match, confirms usable boundaries/completeness/
   perspective and inventories all candidate plays and target-visible intervals.
   Contacts locate moments, not a substitute for full playback review.
3. Around plays extract at0.5s, refining onset at0.1s as needed. Record last
   confirmed absence, onset bracket/point, first appearance and visibility end.
4. Assign unique play_id per distinct deployment, not per PNG. Review identity,
   variant and owner with absence/spawn/continued-visibility evidence.
5. Box only **3–5 distinct original timestamps per verified play**, spanning
   appearance/motion/occlusion. Full rotation-corrected PNG coordinates only.
   Include visible body/wings, exclude beams/labels/shadows/timers. Ambiguity stays
   ambiguous; do not invent concealed extents.
6. Record complete target-visible intervals for all plays, reviewed target-absent
   battlefield and menu/loading/selection/result/system negatives. Unknown gaps
   and possible-target occlusion are not implicit negatives.
7. Validate structure/references/PTS/intervals/boxes, report candidate gate,
   counts, review gaps and missing prerequisites. No allocation/freeze system.

Four surviving candidate plays imply **12–20 key boxes**; re-review or additional
plays can change the total. Full playback/interval review is still necessary.
No manual EvaluationFrame for every5FPS sample and no thousand-image boxing task.
This is proposed workload, not completed labels or exhaustive per-frame truth.

Time is (raw_pts * time_base) - (origin_pts * origin_time_base), with exact
fractions internally; never frame index/average FPS or game countdown.
Extraction misses/errors remain explicit and never become successful evidence.

## 5. Simple 2A1 local v1 contract

Required root keys: recordings[], match_segments[], target_card (object or null),
occurrences[], frame_annotations[], negative_intervals[]. Optional: schema_version
(exactly1 if present; absent interpreted as v1), preparation_report. Writers emit
version1. Reject unknown fields, duplicate JSON keys, NaN/Infinity, wrong types and
bool-as-integer; load limit16MiB. evaluation_frames, evaluation_protocol,
split_manifest, test_locked and freeze objects are deferred and rejected in 2A1.
No freeze_split or canonical lock function.

| Entity | Fields |
| --- | --- |
| RecordingDescriptor | recording_id, source_sha256 (64 lowercase hex, local only), width/height (encoded pixels), duration_seconds (positive finite or null), time_base, origin_pts, origin_time_base, last_frame_seconds, rotation_degrees (0/90/180/270), orientation (displayed portrait/landscape/square), perspective |
| MatchSegment | segment_id, recording_id, start_seconds, end_seconds, perspective, validation_status, capture_complete bool, boundary_uncertainty_seconds, notes |
| TargetCard | card_id, display_name, selection_reason, ambiguity_notes, variant (normal/known_evolution/unknown) |
| CardOccurrence | play_id, recording_id, card_id, owner=opponent, last_absent_seconds, deployment_lower_seconds, deployment_time_seconds, deployment_upper_seconds, visible_start_seconds, visible_end_seconds, match_segment_id, manual_verification_status, evidence_annotation_ids[], notes |
| FrameAnnotation | annotation_id, frame_id (export reference), recording_id, play_id, timestamp_seconds, raw_pts, time_base, image_path (local relative PNG), image_width/image_height (displayed pixels), normalized_bbox={x,y,width,height}, annotation_source=manual, review_status |
| NegativeInterval | negative_id, recording_id, start_seconds, end_seconds, reason (target_absent/menu/loading/selection/result/system_ui/transition), match_segment_id (ID or null), non_match bool, review_status |

Perspective: own_bottom/opponent_bottom/unknown. Review/validation status:
draft/verified/ambiguous/rejected. IDs are nonempty and unique per entity; boxes for
different plays may share frame_id. Sizes are positive integers, relative times
finite/nonnegative. Rational time_base is positive integer numerator/denominator;
raw/origin PTS are integers. All entity fields above are required.

Validation:

- Ordinary intervals use start<=t<end. Visible end is first reviewed absent time
  after the unit, not its final visible key frame. start<end and all endpoints
  <=last_frame_seconds. An unfinished positive interval cannot prove completeness.
- **Terminal-negative exception only:** if NegativeInterval.end_seconds equals
  the exact stored last_frame_seconds, membership is start<=t<=end. Otherwise
  start<=t<end. Match/positive intervals stay half-open. Copy the actual index
  endpoint without rounding and compare rationals, not approximate equality.
  Future tests must cover inclusion/exclusion at this endpoint.
- Play bounds: segment.start<=last_absent<=lower<=deployment_time<=upper<=
  visible_start<visible_end<=segment.end. Absence is for that newly deployed
  instance, not a claim another same-card unit cannot already exist. Point time
  is supported onset evidence, not exact hidden card-tap time.
- Annotation references a successful export and its recording/play/segment;
  timestamp lies in visible interval. PTS-derived time agrees within1e-6s.
  Rotation determines displayed dimensions, never thumbnail size.
- x/y in[0,1], width/height in(0,1], sums<=1. Reject clipping/coercion and missing
  crop offsets. A verified play needs3–5 verified annotations at different
  rational actual times, reviewed opponent/variant identity and manual
  absence/spawn/visible narrative. Repeated exports/IDs for one timestamp do not
  satisfy three frames; multiple images of one play do not increase play count.
- Unknown perspective/variant prevents candidate gate. Software never promotes
  drafts or infers a deployment from boxes. Overlapping separate same-card plays
  are allowed with manual evidence, not automatically deduplicated.
- non_match=true requires null segment and a non-match reason; false requires
  valid segment and target_absent. Negatives must respect segment bounds and
  cannot overlap known or ambiguous possible-target visibility. Reviewed positive/
  negative union covers intended match time or reports gaps. An unboxed frame
  inside a reviewed interval is NOT itself an unreviewed gap.
- Source maps, if used, are separate local sources.json recording_id→supplied path.
  Images/indexes/reports resolve inside explicitly supplied ignored runs, not URL/
  UNC, traversal, symlink/junction escape or unrestricted private-directory reads.

Optional preparation_report uses section8's return fields, all required when
present. It is advisory; counts/gates are recomputed, not trusted success flags.
No migration from an older implemented schema exists; unknown versions fail.

## 6. Tools, privacy and source gates

Proposed B: existing extraction plus small JSON/box helpers and manual coordinates
at this scale. A mature local standalone annotator is an alternative if entry
proves inconvenient; before selecting one review official source/version/license,
separate-tool use/no code copying, offline/upload/telemetry/download behavior,
Windows install/uninstall and project-license impact. No tool selected/installed.
C, custom GUI, is unjustified. No SQLite/migration/cloud/backup infrastructure.

Public documents allow **anonymized aggregate conclusions only**: candidate name,
deployment count, gate status and identity-free statistics. Original filenames/
absolute paths/SHA256, player identities/tags, notifications, screenshots,
individual frame/deployment/boundary times, boxes, actual JSON, indexes and contacts
stay in local_data/ or outputs/. Remove detailed times from the current public
draft; do not rewrite historical Git commits. Future public fixtures use synthetic
geometry/colors and identities only. Exclusive new outputs; no overwrite/cleanup.

Data routes: A own supplied footage, recommended but small/manual/overfitting-prone;
B external datasets/models, separately provenance-gated; C template matching,
possible future brittle baseline, not final. The earlier
[dataset README review](https://github.com/wty-yy/Clash-Royale-Detection-Dataset/blob/31b4151fedb1b914e99c3c122c16dca61cb2b905/README.md)
recorded YouTube/self-recorded origins and MIT repository metadata, not blanket
media rights. Before external use review code, original media, uploader authority,
game assets, training/model publication/redistribution and weights licenses.
No new rights review or download here; project license remains undecided. Local
reading permission does not establish redistribution rights for game imagery.

## 7. Deferred2A2 and unchanged experiment gates

2A1 records evidence without a split system. 2A2 needs a second independent
complete match AND separate approval/design. It will review underlying match
identity, allocate train/validation/test, fix Evaluation Protocol/digest and
implement split lock/freeze. Whole matches, source recordings, their negatives,
re-recordings/crops/re-encodes and adjacent frames must stay in one split.
Different filenames do not prove independence.

Before2B: >=2 independent complete matches, >=6 verified target plays total, >=1
whole held-out match with>=2 plays, reviewed non-match negatives, valid interval/
key-box evidence and pre-training locked test. Prefer>=3 matches for separate
validation; two matches do not establish independent validation. No random-image
split or tuning on test. These minima permit a PoC, not reliability or live use.
If the four provisional plays survive review, another complete independent match
with>=2 reviewed plays may meet the numeric minimum; identity/completeness/variant
must still pass. No new footage is requested during this documentation revision.

## 8. 2A1 sufficiency and acceptance

candidate_gate: >=4 distinct verified opponent deployments in one recording,
resolved perspective/variant and section5 evidence. Favor distinctive sustained
troop/building appearances, not spells/swarms/towers/icons. Preliminary count alone
does not bypass review.

review returns {status,candidate_gate,experiment_gate,counts,reasons,coverage_gaps}.
status=invalid for invalid evidence, otherwise insufficient in2A1;
experiment_gate=false because independent-data/split approval is deferred.
counts={recordings,reviewed_complete_segments,verified_plays,annotated_key_frames}.
coverage_gaps=[{recording_id,match_segment_id,start_seconds,end_seconds}].
These detailed gaps are private. Reasons list missing numeric data, ambiguous
identity, incomplete interval review and deferred2A2 where applicable. File/segment
counts never certify independence. Stored reports cannot override recomputation.

Valid empty/draft evidence returns insufficient, not a crash. Malformed JSON,
missing PTS/image, bad references, contradictory intervals and unsafe output fail
explicitly. Partial extraction is reported, not silently filled. One recording
must yield insufficient regardless of image count.

2A1 may finish when prepare/validate/review, synthetic tests and real local
key-frame/interval review work and correctly return insufficient. It needs no
second video to finish its own scope. Tests cover nonzeroPTS/VFR/rotation, terminal
negatives, boxes/references, unique plays/frames, conflicts, paths/file protection
and Git ignore; no freeze/detector tests. No implementation exists in this revision.

## 9. Prospective lightweight2B evaluation

Desired future metrics, not2A1 code or fixed protocol. 2A2 must approve/fix protocol
before2B trains. Infer whole held-out matches at5FPS using actual PTS, with extra
inference at the3–5 key timestamps for IoU. Extra key samples do not inflate
the5FPS denominator. No per-frame manual EvaluationFrame inventory.

- Occurrence window: deployment_lower through min(visible_end, deployment_upper
  +2.0), excluding visible_end. Correct candidate in that window ->coverageTP;
  none ->occurrenceFN. Review first candidate's card/owner/instance against local
  footage; time overlap alone cannot prove a correct unit. One candidate cannot
  cover two overlapping plays. Report rawTP/FN, recall and earliest delay versus
  point and uncertainty bracket.
- Whole-matchFP: target observations outside the union of all reviewed visible
  intervals in reviewed absent/non-match regions. Unknown gaps are excluded with
  duration/count reported, not silently treated asFP. Complete interval review
  enables whole-timeline scoring. Report rawFP, FP/minute and non-matchFP/rate,
  actual sampled durations/rate and misses. Repeated false boxes count as
  observations, not deduplicated deployment events. Inside-positive unrelated/
  own-unit confusion cannot be certified away using interval metrics alone.
- BoxTP/FP/FN and IoU only on explicitly boxed key frames, one-to-one matching
  (proposedIoU>=0.5). State actual evaluated frame/box count and subset bias;
  never call this full-frame accuracy. Unboxed frames create no boxFN; continuing
  units create no extra occurrenceTP.
- Confidence distributions, similar-unit/ownership failures, timing errors and raw
  denominators; no training-only score or calibrated-probability claim.

Proposed go: occurrence recall>=0.80, reviewedFP/minute<=1.0, non-matchFP=0,
key-subset medianIoU>=0.5, median earliest delay<=1s, valid independent data and
complete reviewed intervals. These are2A2 review proposals, not predictions.
Go means separately plan3, not live use. Revise on misses using development only,
then a fresh untouched test match. Stop on insufficient/ambiguous/leaked/unlicensed
data or live/control scope.

## 10. Handoff

Read the four-task2A1 plan before separate implementation approval. 2A1 has not
started,2A2 is unapproved, Inferno Dragon remains a candidate and data remain
insufficient for2B. This revision changes documents only; no source/dependencies/
storage changes or main merge.
