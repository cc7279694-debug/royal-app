# Module 2A — Offline Evidence and Annotation Preparation

Date: 2026-10-03. Status: **Proposed design; implementation not authorized.**
The user requested this design and its accompanying implementation plan together.
Module 1 is accepted; this document does not claim Module 2A is implemented.

## 1. Goal, scope and safety

Prepare trustworthy local evidence for a one-card offline experiment. Answer which
parts of a supplied recording are usable, which opponent card is a defensible
target, and whether independent match data are sufficient. The user's eventual
goal is information without obstructing game input; this stage runs after play on
local recordings and has no contact with the game. No zero-ban-risk promise.

Only explicitly supplied files may be read. No private-directory discovery,
uploads, accounts, cloud, game process access, traffic interception, synthetic
input, AccessibilityService, bots, Android capture, or overlays. Live analysis
remains disabled behind the specific official-permission and project-approval
gate in PROJECT.md. No external models, media, datasets or ML packages are added.
No app framework or database is selected by this Python experiment.

## 2. Module responsibilities

| Stage | Owns | Does not own |
| --- | --- | --- |
| 2A | Manual match boundaries, card inventory, occurrence evidence, boxes, negatives, split manifest, sufficiency | Inference or training |
| 2B | One selected class, timestamped visual Observation, independent-match evaluation | Confirmed events, cycle or elixir |
| 3 | Multi-frame confirmation, spatial/time deduplication, ownership evidence, OpponentCardPlayed | Treating each detection as a play |

A manually reviewed annotation is ground truth for evaluation, not a runtime
OpponentCardPlayed event. Module 2B observes visible objects, including continuing
units; only Module 3 can emit confirmed gameplay events. Never infer owner solely
from current screen half: opponent units cross the river.

## 3. Current read-only evidence

Repository source, tests and all seven context documents were read. Before the
authorized merge, the pinned environment reran 47 pytest tests successfully;
pip check, whitespace checks, tracked-file/media and targeted secret scans passed.
Local and remote accepted branch were exactly
`e30ca01fb7a70a0f3bfc14e4fb838dd7ff0da491`; main was its ancestor. Main was
fast-forwarded and pushed to that commit, without deleting or rewriting branches.

Exactly the supplied MP4 was examined, not other private files. Its metadata is
448 x 960, H.264, 273.166333 seconds; the last display timestamp is
273.133333 seconds. The existing Module 1 extractor produced a 5-second whole-file
survey, 0.5-second candidate windows and selected 0.1-second boundary/spawn windows.
All successful exports and contact sheets are ignored local outputs. Contact
sheet thumbnails/crops aided inspection only; original full-size PNGs remain the
coordinate source. No recognition code was written or run.

### Match and non-match ranges

There is one observed match, with pre-match screens and a visible ending. At
23.6 seconds the card-selection overlay still obscures the arena; at 23.7–23.9 it
transitions away; 24.0 is the first sampled unobstructed battlefield. At 268.0
play is still visible, and 268.1 shows tower destruction/crown-result UI. Use the
conservative usable battlefield interval **[24.0, 268.1)** seconds. These are
manual display-boundary measurements at 0.1-second sampling, not hidden game-start
times or frame-exact event timestamps. The earlier battle clock is partly behind
selection UI; do not derive start_seconds from its countdown.

The recording covers pre-match through outcome, but full-match eligibility must
still be explicitly reviewed in 2A: confirm no early deployment was hidden by
the selection transition, no edits/speed changes and no missing combat interval.
Current count is one match, never two; even if it passes completeness review it
cannot satisfy the independent-match gate alone.

Conservative non-match intervals: [0,24.0) menu/loading/selection/transition;
[268.1,273.133333] outcome/result/system UI. At 271.5 result transition and
272.5 system UI are visible. Boundaries must be refined or marked uncertain in
actual annotations; do not label uncertain target-containing frames as negative.
Game emotes/UI sometimes obstruct the battlefield and require exclusion notes.

### Opponent inventory and target recommendation

The strongest manually identified candidate is **Inferno Dragon / 地狱飞龙**:
green armored flying unit, wings and sustained beam, opponent-colored level/bar,
new spawn evidence followed by movement. At least four separate episodes were
reviewed with absence-before/spawn/continued-visibility context, approximately
66, 113, 133 and 212 seconds. The local review retains sample brackets and PNG
references, not a fabricated frame-exact deployment time. This is a lower bound,
not a complete count of all deployments. Later dragon appearances are not added
to the count without the same review. Thus the current **four-occurrence target
selection gate passes**, but the Module 2B data gate fails.

Other visual candidates: Skeleton Army / 骷髅军团 (mass skeletons), Bats / 蝙蝠
(small flying group), and Goblin Barrel / 哥布林飞桶 (landing/spawn group near
our tower). They are preliminary inventory, not a verified complete eight-card
deck. Small groups, spells and particle-only appearances are poor initial targets.
An additional green mechanical/armed unit is unresolved and must stay unknown.
Own Bomber, Cannon, Knight, hand icons and tower units must not enter the enemy
inventory merely because they are visible. Hog Rider is not assumed or selected.

Recommend inferno_dragon for the first annotation exercise, not an accepted model
class yet. Recheck normal/evolution identity and ownership at full resolution;
ambiguous variants must not be silently merged into the verified class. If this
review invalidates any of the four episodes, reassess the selection gate.

## 4. Manual evidence workflow

1. Inspect only supplied files and verify the input hash before/after processing.
   Assign opaque recording_id; keep source path and hash in a local descriptor.
2. Reuse Module 1 extract_frames to sample every 5 seconds and the final actual
   display frame. Contact pages contain at most 12 full-frame thumbnails, labeled
   with actual PTS-normalized time. No thumbnail is an annotation coordinate space.
3. Human reviews match start/end, completeness, perspective and interference;
   record brackets and uncertainty. No automatic match-boundary detection.
4. Inventory possible opponent cards with context. Rank troop/building candidates
   by distinctness, sustained visibility, repeat plays and confusability. Select
   only after at least four distinct manually verified deployments in the current
   recording. Persistent frames of one unit count once, never once per PNG.
5. Around each candidate use 0.5-second sampling; refine onset with 0.1-second
   sampling and inspect full PNGs. Record last absence, first spawn evidence and
   visible start/end. Uncertain owner/card/onset means ambiguous, not verified.
6. Assign unique play_id to each independently reviewed deployment. Label 3–5
   visible key frames spanning appearance/motion/occlusion; annotate tight visible
   body-and-wing boxes, excluding beam, shadow, level text and spawn timer. Mark
   severe occlusion ambiguous rather than inventing the concealed extent.
7. Record reviewed target-absent battlefield and non-match negative intervals;
   retain menus/results/system UI locally, never share them publicly.
8. Validate structure, references, PTS, bounds, review state and evidence files.
   Build a whole-match split and sufficiency report. Missing data are a valid
   blocked-for-experiment outcome, not a reason to fabricate labels.

All times: `(raw_pts * time_base) - (origin_pts * origin_time_base)`, using exact
fractions internally. Average FPS and game countdown never replace this rule.
Extraction misses/errors remain explicit and cannot be used as successful frames.

## 5. Versioned local JSON contract (proposed v1)

Root keys: schema_version=1, recordings[], match_segments[], target_card (object
or null), occurrences[], frame_annotations[], negative_intervals[], evaluation_frames[],
evaluation_protocol (object or null), split_manifest (object or null).
Reject unknown root/entity fields; allow the documented optional
fields below. Strict JSON rejects duplicate keys, NaN/Infinity and wrong types;
bool is not an integer. JSON inputs are limited to 16MiB. IDs are opaque nonempty
strings, unique within their entity. FrameAnnotation uniqueness uses annotation_id;
frame_id references an export and may be shared by boxes for different plays.
Strings in notes never trigger actions.

| Entity | Required fields and meaning |
| --- | --- |
| RecordingDescriptor | schema_version=1, recording_id, source_sha256 (64 lowercase hex), width/height (positive encoded pixel integers), duration_seconds (positive finite metadata value or null), time_base (positive rational object), origin_pts (integer), origin_time_base, last_frame_seconds (finite >=0), rotation_degrees (0/90/180/270), orientation (portrait/landscape/square displayed orientation), perspective (own_bottom/opponent_bottom/unknown) |
| MatchSegment | segment_id, recording_id, match_group_id, start_seconds, end_seconds, perspective, validation_status, capture_complete (bool), boundary_uncertainty_seconds (finite >=0), notes |
| TargetCard | card_id, display_name, selection_reason, ambiguity_notes, variant (normal/known_evolution/unknown) |
| CardOccurrence | play_id, recording_id, card_id, owner=opponent, deployment_time_seconds, deployment_lower_seconds, deployment_upper_seconds, visible_start_seconds, visible_end_seconds, match_segment_id, manual_verification_status, evidence_frame_ids (>=3 for verified), notes |
| FrameAnnotation | annotation_id, frame_id, recording_id, play_id, timestamp_seconds, raw_pts, time_base, image_path (local relative PNG reference), image_width/image_height (positive displayed pixels), normalized_bbox={x,y,width,height}, annotation_source=manual, review_status |
| NegativeInterval | negative_id, recording_id, start_seconds, end_seconds, reason (target_absent/menu/loading/selection/result/system_ui/transition), match_segment_id (ID or null), non_match (bool), review_status |
| EvaluationFrame | frame_id (successful export ID), recording_id, timestamp_seconds, raw_pts, time_base, image_path, image_width/image_height, match_segment_id (ID or null), review_status, target_present (bool), frame_annotation_ids[], negative_id (ID or null) |
| EvaluationProtocol | schema_version=1, sample_rate_fps=5, iou_threshold=0.5, confidence_threshold (finite [0,1], selected from development only), window_extension_seconds=2.0, go_min_recall=0.8, go_max_fp_per_minute=1.0, go_max_non_match_fp=0, go_min_median_iou=0.5, go_max_median_delay_seconds=1.0 |
| SplitManifest | schema_version=1, target_card_id, assignments=[{match_group_id,split}], recording_assignments=[{recording_id,split}], non_match_assignments=[{negative_id,split}], test_locked (bool), evidence_sha256 (hash of canonical evidence JSON excluding split_manifest), locked_at (UTC ISO8601 or null), independence_reviewed (bool), notes |

Each rational is `{numerator: positive integer, denominator: positive integer}`;
origin_time_base may differ from stream time_base and annotation frame time_base.
Validation statuses are draft/verified/ambiguous/rejected. Unknown perspective or
variant may be retained but cannot satisfy a verified-target gate.

Rules:

- Use half-open match/negative intervals [start,end); visible frame intervals are
  inclusive. Bound all times by last_frame_seconds, not nominal container duration.
  A last-frame negative endpoint may equal last_frame_seconds; that final frame
  is assigned explicitly as a non-match frame rather than silently lost.
- `0 <= segment.start < segment.end <= last_frame_seconds`; for a play,
  segment.start <= lower <= deployment_time <= upper <= visible_start <=
  visible_end < segment.end. deployment_time is first supported spawn evidence,
  not guaranteed exact card-tap time; preserve its uncertainty bracket.
- Every annotation refers to a real successful Module 1 export, one recording,
  one occurrence and its containing segment. timestamp must fall within that
  occurrence's visible range. Rational-derived time must match timestamp within
  1e-6 seconds; raw PTS/time_base/origin are required, even when FPS is available.
- Coordinates use the full, rotation-corrected PNG. x/y in [0,1], width/height in
  (0,1]; x+width and y+height <=1. Reject clipping, coercion and silent swapping.
  Conversion from a reviewed pixel rectangle divides by displayed width/height;
  crop offsets must be restored first. Rotation swaps encoded dimensions at 90/270.
- No duplicate (play_id, raw_pts, time_base) annotation. Multiple separately
  verified units may share a frame but do not multiply deployment counts.
- Verified occurrences need >=3 verified frame references and an absence/spawn
  narrative in notes. Software checks format; a human confirms distinct plays.
  Same-card overlapping visible intervals are possible, not automatically duplicates.
- Non-match=true requires null match_segment_id and a non-match reason; false
  requires a valid segment and target_absent. Reviewed negative intervals must
  not overlap verified target visibility or an ambiguous possible-target interval.
- Source paths are a separate local `sources.json` map recording_id -> absolute
  source file. No absolute private source path in public docs or exported indexes.
  image_path resolves inside an allowed ignored evidence run, never a URL, UNC,
  traversal, symlink/junction escape, or arbitrary private-directory search.
- EvaluationFrame shares the export frame_id (it need not be a positive annotation).
  Require exactly one review for every successful 5FPS held-out/non-match export;
  raw timestamp/path/dimensions must agree with its index. target_present=true
  requires all visible target boxes referenced by annotation_id as verified FrameAnnotations and
  null negative_id. target_present=false requires no boxes and a verified
  covering NegativeInterval. Incomplete/ambiguous reviews or extraction misses
  block readiness, not label-free false-negative counting. FrameAnnotation IDs
  may be referenced here without creating a second annotation of that object.
- evaluation_protocol may stay null during preparation; first freeze requires
  all its fields. Experiment thresholds are a proposed fixed protocol in this
  design, not measurements. Evaluation protocol is included in evidence_digest.
- Version upgrades require explicit conversion into a new file; unknown versions
  fail. Do not overwrite recordings, previous evidence or a locked split.

Public source in a future approved 2A may contain rules and entirely synthetic
examples only. Real descriptors, hashes, notes and labels remain private.

## 6. Annotation tooling comparison

**B — recommended proposed default:** existing Module 1 frames plus small local
index, pixel-box conversion, validation and sufficiency helpers. Human reviews
original images and enters reviewed coordinates in a local JSON draft; Codex
can assist transcription, but only human-reviewed boxes become verified. Low
volume makes this viable without a GUI. No new dependency, installation, license
or upload path. If manual coordinate entry proves too slow, revisit A separately.

**A — mature standalone local annotator:** faster interactive boxes and familiar
exports, but installation, format mapping and privacy/license verification are
additional work. No concrete third-party tool is selected or recommended for
installation here. Before selecting one, record official source, exact version
and license, standalone-only use/no copied code, offline behavior and upload/
telemetry/model-download controls, Windows isolated install/uninstall, and any
distribution implications. Test with synthetic images without network before
private footage. A tool's license does not license the game's assets.

**C — custom full annotation GUI:** rejected for this PoC; highest maintenance
cost with no demonstrated unmet need. No GUI tasks in the accompanying plan.

## 7. Private data, storage and provenance

Recording inputs stay at user-selected paths. All evidence/media/annotations/
hashes/manifests/contact sheets are under local_data/ or outputs/, already ignored.
New output runs are exclusive, fail on existing files; no automatic cleanup.
No SQLite, migration, repository business layer or backup infrastructure is
needed for this disposable evidence experiment. Original media stay untouched.
Public commits contain only design/state documents this round. Future public
tests contain generated geometric/color images, not cropped game assets.

Three data routes:

- A: own supplied recordings, recommended. Closest to real resolution/UI, clear
  user permission to read locally, but small/manual/overfitting-prone. Ownership
  of a recording is not proof of permission to redistribute Supercell imagery.
- B: external datasets, future provenance-gated only. On 2026-10-03 the official
  [dataset README](https://github.com/wty-yy/Clash-Royale-Detection-Dataset/blob/31b4151fedb1b914e99c3c122c16dca61cb2b905/README.md)
  was read as text via GitHub API; repository metadata declares MIT, and README
  describes YouTube/self-recorded video origins. This establishes a need for
  separate rights review, not blanket usability. Verify code license, each media
  origin, uploader's right to sublicense, game-asset rights, training/model
  publication/redistribution permissions, third-party video terms and independent
  weights license. No images, repository clone, dataset or model were downloaded.
- C: traditional template matching, possible future controlled baseline only.
  Pose, scale, direction, animation, occlusion and effects make it brittle; not a
  final system. User footage used for templates belongs to training, never test.

Project license remains undecided. Reference ideas do not authorize unlicensed
source copying; this design imports no third-party source or assets.

## 8. Split isolation and minimum evidence gates

Gate A, target choice: >=4 distinct manually verified opponent plays in the
current recording, distinctive troop/building, sustained visible frames, resolved
variant. No forced Hog Rider, spell/small-swarm/tower/icon or one-off target.

Gate B, Module 2B: >=2 independent complete matches, >=6 verified target opponent
plays total, >=1 whole held-out match with >=2 plays; reviewed menu/result/system
negative ranges; valid reviewed annotations; test locked before any training.
These are executable-PoC minima, not reliability certification.

match_group_id is manually assigned to the same underlying match even for
re-recordings/crops; hashes detect identical files, not semantic duplicates.
All frames, occurrences, recordings/re-encodes of a match stay in one split.
For initial simplicity, each source recording also stays in one split (multiple
matches in one file are co-assigned). Non-match negatives inherit that recording's
split, including otherwise-unassigned files. Reject cross-split shared hashes,
match groups, recordings or frames. Different filenames are not independence.

At the two-match minimum use one development/train match and one test match;
no independent validation score is claimed. Pre-register parameters or use
training-only internal tuning, clearly labeled non-independent. Prefer >=3
independent matches for train/validation/test; validation tuning never uses test.
Lock the reviewed canonical evidence hash, target, assignments and evaluation
protocol before training. Changing annotations, target or split invalidates lock
and requires an explicit new reviewed experiment; never tune repeatedly on test.

Current data: four conservatively counted plays in one observed match; no
independent held-out match, no finalized boxes or split lock. **Insufficient for
2B.** Minimum useful next input after planning approval: one additional independent
complete match with >=2 unambiguous opponent Inferno Dragon deployments, normal
speed, full portrait battlefield, pre-match through outcome, no cuts. Reusing or
re-encoding this match does not count. If completeness/variant review fails,
replace or add recordings until both gates actually pass. No recording required
from the user during this planning round.

## 9. Prospective Module 2B evaluation (not implemented by 2A)

Pre-register one-class evaluation on whole locked matches at 5 FPS, preserving
actual PTS-selected sample times and extraction misses. Freeze confidence and
IoU thresholds using development data only. Default prospective IoU match >=0.5.
Manually label each reviewed test frame in 2A before locking; evaluate all sampled
frames, not only selected successful screenshots. Later dense test labeling is
a new reviewed evidence revision if not already present in the lock.

For each human occurrence, deployment window is
[deployment_lower_seconds, min(visible_end_seconds, deployment_upper_seconds+2.0)].
Detection coverage succeeds if >=1 correct spatially matched candidate appears
in that window. Missed windows are deployment FN, successful ones coverage TP;
these are evaluation summaries, NOT generated deployment events. Report raw
coverage TP/FN and recall, earliest matched candidate delay relative to the
human point AND uncertainty bounds (median/p95/max), and all missed play IDs.

Separately report frame/box TP/FP/FN against reviewed boxes with one-to-one IoU
matching; unmatched detections are FP, unmatched visible boxes FN. Repeated
correct detections of a continuing unit remain frame TP, not false extra plays.
Report outside-target-visibility FP boxes, FP/minute over all evaluated minutes,
non-match FP and FP/minute separately, IoU distribution, confidence distributions
for TP/FP, similar-unit confusions, own-unit errors, occlusion and stage breakdown.
Annotations of one object cannot conceal a second object's missed detection.
No confidence probability calibration claim; retain raw denominators and counts.

Prospective decision rule, frozen before 2B:

- **Go to a separately approved Module 3 design**, not live play: coverage recall
  >=0.80, FP/minute <=1.0, zero non-match FP, median matched IoU >=0.5, median
  earliest-candidate delay <=1.0 second; no leakage, unreadable labels or unresolved
  owner/variant. Show counts: with just two held-out plays 0.80 means both detected.
- **Revise**: gates/provenance valid but one performance threshold misses; report
  cases, change only development evidence/parameters, and obtain a fresh untouched
  held-out match before judging an adjusted method. No silent test retuning.
- **Stop**: insufficient/invalid data, leakage, ambiguous target, unavailable rights,
  or a proposed live/control capability. Report exact missing conditions.

These thresholds are proposed experimental acceptance criteria, not predictions.
PoC success cannot establish generalized accuracy, phone performance or account safety.

## 10. Error behavior, acceptance and verification

Missing source/PTS/image, malformed JSON, bad references/bounds, hash mismatch,
unresolved perspective, no target, partial extraction, unsafe output and unlocked
split yield explicit reasons. Invalid input fails; valid but insufficient evidence
returns a structured insufficient report, not a crash or synthetic successes.
No automatic repair, silent discard, owner guessing, destructive overwrite or
promotion from draft to verified. New runs preserve incomplete prior outputs.

Future 2A is complete when the local workflow, validation and sufficiency report
are reproducible with synthetic tests and actual user evidence, including a
correct insufficient result. 2B readiness is a separate decision. Test version,
types, references, rational timestamps/nonzero origins/VFR/rotation, coordinates,
duplicates, uncertainty, negative conflicts, split leakage, gate thresholds,
file protection and CLI exit codes. No game screenshots in public fixtures.

This planning round verified existing tests and evidence only. Schema validation,
annotation tooling, split freezing, sufficiency implementation and detector/model
evaluation are **not run because not implemented**. No Android/TypeScript/build
changes are part of these documents. Self-review must check requirements coverage,
privacy, leakage, target assumptions and Observation/event separation before commit.

## 11. Explicit non-goals and handoff

No product code, ML installation/inference/training, external media import,
automatic boundaries, complete-deck claim, custom GUI, app UI, database, Android,
capture/HUD, card cost/cycle/elixir or runtime deployment event in this task.
Read the accompanying plan; implementation requires a separate user approval.
Proposed tool/target/evaluation choices remain reviewable, not accepted decisions.
