# Current State

Last verified: 2026-10-11.

## Current checkpoint — Target-card field review frozen; precise review pending

User attests the supplied ChatGPT visual suggestions as the confirmation basis.
Reviewer is **user**, not ChatGPT; only explicitly supported fields/target-mapping
decisions are confirmed. Source ZIP/CSV and original detector predictions remain
unchanged. Binding checks cover all36 object IDs, match/frame/PTS/teacher/bbox
references and all16 original candidate windows; no CSV row-number matching.

New immutable private Snapshot v1:
`outputs/module3c-target-human-review/snapshot-v1/module3c.target_field_human_review_snapshot.v1.json`.
SHA-256 `733aef78d771eb16a1c96f1977d5ddf34351df44ff9013185565e5471f06f7bd`.
Validated by rebuilding the exact field-scoped result from SHA-bound source and
suggestion archives, not by trusting a recomputed digest alone.

- Firecracker:9 class+opponent field confirmations (8 in06,1 in08).
  TO005/TO019 teacher owner=own is retained beside reviewed opponent.
- Airborne barrel:6 generic visual-class confirmations; Goblin Barrel remains
  a hypothesis, actual card/owner/independent deployment unknown.
- 11 target-mapping rejection decisions;9 objects stay pending and TO031 unknown.
  Hog Rider confirmed boxes remain0. Rejection never becomes Negative.
- 36 bbox remain unverified; all identity/form/origin/onsets unconfirmed.
 16 event candidates and63 coverage rows remain pending; complete-object GT,
 qualified training boxes, Negative and new OpponentCardPlayed all0.

Only two new precise-review jobs are prepared under
`outputs/module3c-target-human-review/precise-review-v1/`: GB07-01 flight/arrival/
small-unit context5.5–7.5s (13 existing6FPS source frames,5 native examples), and
FC06 bbox/missing-box/continuity/coverage (8 observation refs/8 source frames,
not8 independent units or plays). Native JPG/crop PNG and source/display offsets
are provided; boxes are UNVERIFIED.08 is excluded from FC06 and still exposed
retained evaluation, never training/tuning or strict blind.

No production code/tests/schema, event engine, Android, detector weights or
environment changes. No inference/training; no push/merge. Local baseline
`65004237885edf447ea185fd3c01ad7e7288af0a`, branch
`codex/module3c-target-card-discovery`; main remains `602dd0f...`.
Next: independent precise human review of these two small jobs only; do not
automatically confirm boxes, infer Goblin Barrel plays, train or enter another
module. See [backfill checkpoint](checkpoints/2026-10-11-module3c-target-review-backfill.md).

## Preserved preceding checkpoint — Three target cards / pending discovery review

User priorities now **Hog Rider, Goblin Barrel, Firecracker**. Local rescreen/
review preparation from `fef67ad650b073bda379a6abb6218bc32c38d582` on
`codex/module3c-target-card-discovery`; no training, new Human GT or card events.
Witch/Royal Hogs/Minions and all old evidence/locks/results remain historical,
not deleted or current priority gates. Main remains published3D `602dd0f...`.

Same four05..08 sources verified unchanged and fully decoded again:9,313 frames.
Fixed whole-file2FPS source-PTS scan covers769 sampled scenes, not only the old18
review pictures. All35 source survey pages reviewed;211 extra source-only6FPS
context samples support projectile/spawn review. No new model/dependency/runtime
installation, thresholds or event rules. One initial decoder compatibility failure
before any prediction is preserved; source-bound prevalidation used existing envs.

| Priority | Pixel-supported discovery, still pending | Main gap |
|---|---|---|
|Hog Rider|08 teacher44–52s window conflicts with bulky humanoid;05..07 guesses are confounded|no confirmed pig+rider source; absence remains unknown|
|Goblin Barrel|06 five /07 five separated flight locators|card/owner, impact/successors and independent deployment/onset not Human-confirmed|
|Firecracker|06 six birth/appearance contexts;08 presence26–34s|exact bbox/owner/form, identity, missing boxes and independent plays|

Six prior Firecracker object IDs and six locators were found pending; no new
attested Witch/Firecracker return was located. Reuse their IDs/source bindings,
not a fabricated confirmation. Actual class/owner/form/origin/identity remain
unknown, teacher attributes separate. Sixteen pending CardPlayCandidate hypotheses
have flight/birth-context evidence, not sixteen confirmed independent plays.
Hog08 presence conflict is visual-only, not a confirmed deployment candidate.

Private ZIP `outputs/module3c-target-discovery/v2/Module_3C_Target_Card_Discovery_Human_Review_Lite_v2.zip`:
19,135,637 bytes; SHA-256
`cb775b3dee81d665baf4637cdaa0455d8a7aed9e6b83e3f3478e327b55ddc92d`.
21 native arena JPG pairs,36 pending teacher boxes,63 pending coverage rows,
7 paired contact sheets,19 continuity sheets,24 dense-context sheets/211 samples,
observation/candidate tables and correction/missing-box forms. Oversized v1 retained;
lite changes contact-sheet JPEG quality only, not native pairs/metadata/boxes.

05..07 development discovery only;08 stays exposed retained evaluation, never
training/tuning or strict blind. File PTS is not game clock/replay speed. Crop
`[0,534,1200,2309]`, full-source bbox1200x2670; exterior unknown/nonnegative.
New Human GT, qualified training boxes, Negative and OpponentCardPlayed all0.
Next: independent human review of target class/owner/bbox, flight and continuity;
do not train or request extra source collection before reviewing these candidates.
See [target discovery checkpoint](checkpoints/2026-10-10-module3c-target-card-discovery.md).

## Preserved preceding checkpoint — Module3C6 discovery (prior priorities superseded)

Local discovery/review preparation is complete from baseline
`1eda1a43fa7193eb8620ff2b7314b555c85a7787` on
`codex/module3c6-multiclass-discovery`. No training or new Human GT; main stays
published3D `602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.
The current task supersedes Royal Hogs/Minions-specific source collection, not
its historical evidence.3C-3/3C-4 are not promoted;3B/App/old locks are unchanged.

Four user-provided recordings are registered as independent-match candidates
`natural_match_05` through08, separately bound to stable SHA-derived recording
IDs. Filename-ascending intake order was fixed before class discovery; it is
not a verified capture chronology. All4 decode completely (9,313 source frames),
have increasing actual PTS and no large timestamp gaps. All12 opening/middle/end
boundary images were viewed: opening/VS and terminal result UI support the user
completion attestation; no visible boundary truncation conflict. This is not
forensic proof of no internal edits. All4 differ bytewise from each other and
5 historical source files; distinct visible match contexts support separate
matches, but SHA alone does not prove underlying-match independence.

Existing private KataCR source/env/weights reused without installation, download
or training. One fixed0.5-FPS replay-layout scan:194 samples,5,412 raw proposals,
108 raw labels including UI/effects/errors, NOT108 actual cards. Analyst source
survey:19 contact pages covering194 sampled scenes. The curated36 per-match
rows/30 candidate visual names and95 review windows are tentative discovery
locators, NOT confirmed classes or independent deployment/card-play counts.
All independent counts/onsets still require context review. Detector absence
and user-reported no Royal Hogs/Minions are not exhaustive Negative evidence.

Recommend2 next primary visual targets for review, not training admission:

| Target | New match support (tentative) | Main gap |
|---|---|---|
|Witch|07 /08;3+1 review windows|exact boxes, class/form/owner, spawn and continuity review|
|Firecracker|06 /08;5+1 review windows|small/edge targets, late discovery vs new plays, exact coverage|

Old accepted Witch references may be audited/reused later without overwriting
locks. Knight-like, Mega Knight, Magic Archer, other primary-looking targets,
structures and secondary cohorts remain future candidates; no card identity is
inferred from hand UI alone. Cannon-like source mapping stays unset. All newly
displayed bbox/class/owner/form/origin/group fields remain pending/unconfirmed.

Private review ZIP:
`outputs/module3c6/discovery-v1/Module_3C6_Multiclass_Discovery_Review_Lite_v3.zip`.
14,231,654 bytes (13.57MiB); SHA-256
`485bca2e93aa06f12fba91060910d19fdec218ce45bd09cf169a3bdfd11a81cd`.
18 representative source-PTS frames,6 contact sheets,71 pending teacher bbox,
36 pending class-coverage rows, correction/missing-box forms and distribution
tables. Native-resolution battlefield crops preserve explicit source rectangle
`[0,534,1200,2309]`; CSV bbox remains full-source1200x2670, subtract534 from y
for crop display. Original full-size exports remain private; no extra extraction
for the lightweight derivative. JPEG/crop presentation is not pixel-confirmed GT.
The lightweight supplement adds explicit coverage scope (crop exterior remains unreviewed/nonnegative)
and errata for two inherited, nonexecuted configuration prose fields; predictions,
boxes, chosen frames, pending states and frozen configs remain unchanged.
V3 also corrects a hand-written analyst locator against unchanged raw predictions:
07 teacher Minion guesses are isolated32.032/56.023s, not14–16s or continuous units.

05/06/07 development discovery;08 reserved before inference as retained
evaluation candidate and not available for training/tuning.08 has discovery
exposure, therefore not strict blind. Replay controls show x1/x2 in early frames.
08 is not an independent target-selection/prospective test, only an exposed
exploratory retained evaluation candidate.
File-relative PTS is not game clock and no constant replay-speed conversion is
assumed. Whole-match isolation remains required for later splits.

Fresh scoped tests182 passed/0 skipped:51 preannotation,84 event engine,47
offline pipeline/CLI. Offline and existing KataCR dependency checks pass.
Source/old-material/manifest/ZIP/privacy/link/diff checks preserve3,914 material
files,224 existing tracked sources and all4 new MP4s; recorded in the
[discovery checkpoint](checkpoints/2026-10-09-module3c6-multiclass-discovery.md).
Full-suite/JS/Android/YOLOX training checks Not Run (no corresponding changes).
The initial combined test invocation hit collection naming/import errors; the
established per-module commands passed without modifying tests or production.

Next: upload the small private bundle manually for independent visual review;
confirm precise class/owner/bbox, missing objects and class-specific coverage,
then inspect candidate onset/continuity before counting independent deployments.
No current training dataset or experiment is qualified. No reinstated Royal/
Minion quota, no additional footage request before this review. Stop after local
commit; no push/merge, model training, engine/App or live-game changes.

## Preserved checkpoint — Module3C5 BBox review decision backfill

Historical task below; its Royal/Minion-specific next-step request is superseded
by the current3C6 multiclass discovery authorization, not an active prerequisite.

Decision-only backfill is complete from local `e65ae283...` on
`codex/module3c5-detector-improvement-a`; detector training admission is still
**Blocked**. No new detector improvement, training/inference/metrics rerun.
Main remains published3D;3C-3/3C-4 are not promoted and3B/App stay unchanged.

Reviewer is `user`, review basis `chatgpt_visual_review`, confirmation source
`user_attestation_based_on_chatgpt_visual_review`. The attestation confirms the
review decisions, NOT exact pixel boxes, physical identity or exhaustive coverage.
ChatGPT is not a human reviewer.

Six explicit-ID associations are `duplicate_review_candidate`:O009/O010/O012/
O017/O019/O020. Same-frame/class/match/time and descriptive bbox overlap support
possible links to prior accepted GT, not proof of the same physical object.
No irreversible merge or additional training box. O011/O018/O021 remain pending;
O017/O018 owner remains unknown. All9 candidate boxes remain unverified.
The19 old accepted references and16 pending class-coverage rows remain intact;
new training-qualified boxes0, new Negative0, no exhaustive-region claim.

New immutable private decision record:
`outputs/module3c5/decision-backfill-v1/bbox-review-decisions.v1.json`.
Byte SHA-256:
`23b816f67b277f49a55b07320290ce6101c79a482282edff5b035ff6971c3742`.
This is a separate review-decision record, not a Human GT or Training Dataset Lock.

Version-deduplicated existing accepted bbox records:105 (83 multiclass plus22
Witch/Skeleton, including partial-frame boxes). This is not105 trainable boxes.
Royal Hog5/3 frames and Minion28/12 frames (33 boxes) all come from match01;
multiclass locks remain annotation-only/training-unqualified. Minion has8
single-class exhaustive positive frames; Royal Hog has0. Joint two-target
exhaustive frames proven0, eligible target Negative0, qualified target standard
training frames0. Old8 Witch/Skeleton negatives do not qualify for these targets.

The field Snapshot SHA remains
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.
All49 bbox remain unverified; class/owner confirmation never promotes boxes.
Older8 provisional boxes and6 combination/group boxes also are not new unit GT.

Preserved private minimal review ZIP:8 existing lossless PNG frames and two contact sheets,
19 prior accepted bbox references plus9 unverified drafts (overlap, not28 new
objects),16 pending target-region coverage rows and missing-box/correction forms.
No new GT or Negative, no training/evaluation split or data lock. Royal currently
has only one confirmed deployment-source window; Minion has two historical
deployment sources in the same match, not33 independent observations. Other
matches lack finalized target GT. Original-order03/04 source inspection viewed
30 existing contact sheets (159+107=266 sampled frames), including combat, and
located no clearly identifiable additional Royal Hogs cohort/deployment support.
This is analyst inspection of sampled material, NOT whole-video absence proof,
new human GT or Negative. Crowded/small details stay unknown. Match02 remains
truncated/excluded; match03/04 prior development exposure is disclosed, not blind.

Next: precise bbox/identity review for unresolved candidates/possible duplicates,
explicit16-row two-class region coverage, and original-video/human evidence for
an independent Royal Hogs source (minimal additional natural footage if needed).
The sampled03/04 check did not resolve that source gap. Never split adjacent
frames of one deployment across TRAIN/DEV/
RETAINED_EVAL or claim cross-match/blind validation from reviewed match03. Freeze
source-isolated assignments before the sole authorized model experiment; no new
4-match/8-deployment quota is imposed.

Fresh scoped regressions135 passed/0 skipped (51 preannotation +84 event engine);
offline and existing YOLOX pip checks pass. Existing actual human returns still
validate exit0 at44/39 accepted boxes, training-qualified=false. Private decision
readback checks reject unsafe promotion/merge/ID/coverage changes. Protection and
privacy checks verify3904 existing material hashes and225 unchanged tracked files;
new private outputs remain Git ignored. Receipts are retained with the new record. GPU qualification
is historical, not rerun. Full-suite/model/Android builds Not Run.
See [backfill checkpoint](checkpoints/2026-10-09-module3c5-bbox-review-backfill.md)
and the preserved [data admission checkpoint](checkpoints/2026-10-09-module3c5-detector-data-admission.md).
Stop after local documentation commit; no push/merge/training.

## Preserved checkpoint — Module3C field-level human review freeze

User attested the ChatGPT field-level suggestions for immutable Mini-Batch v4.
Reviewer is `user`, review basis `chatgpt_visual_review`, confirmation source
`user_attestation_based_on_chatgpt_visual_review`; ChatGPT is not a human reviewer.
Local baseline `552ddaf1e47c941fc4723d8b054b16e53cde4273`, same feature branch;
main remains published3D. No promotion of3C-3/3C-4 or new event rules.

Independent Field-Level Human Review Snapshot v1 and four returned CSVs are
private/Git ignored, exclusively created instead of using the full-object GT
importer. Byte SHA-256:
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.
Source v4 and suggestions ZIP/member hashes, exact candidate IDs, match/recording
and PTS bindings, user attestation and all original suggestions are retained.

49 objects:22 confirmed class,34 owner,12 presence cells (68), plus4 group-context
cells only.72 confirmed object-field cells,418 unknown cells,49 unverified bbox
cells; these counts are NOT independent objects/events. Class unknown27, owner
unknown15, global physical ID unknown49. All objects remain
`full_object_human_confirmed=false`; form/origin/global identity/deployment time
are not inferred.13 supported third-match continuity links exist separately,
without assigning global IDs or implying new deployments.

39 relations:13 confirmed continuity,9 tentative Minion identity,8 unknown Royal
Hog identity,9 confirmed same-visual-cohort links. Two visual cohorts have4/3
members; membership is not a deployment event. Suggested arrival intervals are
tentative, never exact card-play times. All40 frames nonexhaustive/nonnegative;
F32–F34 flying units still incompletely reviewed. Negative0; new events0.
Unverified boxes block strict detector scoring and training eligibility.

No old source, draft, GT Lock, predictions, engine/rules/scorer, App, dependency
or model environment is modified. Fresh validation/check details and limitations
are in the [field-level freeze checkpoint](checkpoints/2026-10-09-module3c-field-level-review-freeze.md).
Fresh328 tests passed/1 existing Windows symlink skip (27 mutation subtests
separate);31 artifact checks pass.3198 protected materials and220 tracked
sources unchanged; dependency/diff/link/privacy checks pass. No full offline
suite or model/App/build rerun is claimed for this document/private-file change.
Stop after local documentation commit; no push/main merge, inference, training,
new scoring, Android or live game. A next stage requires separate authorization.

## Preserved checkpoint — Module3C visual evidence mini-batch review preparation

Authorized from local `1873ccf96617ca02804c0b3627687f5a4e557ce6` on
`codex/module3c-visual-gt-mini-batch`. Main remains published3D `602dd0f...`.
The user explicitly declines promotion of3C-3/3C-4 experimental strategies;
do not add event rules. This stage prepares inspectable pixels and pending
identity/owner/group candidates, not confirmed visual GT or model acceptance.

Frozen40 samples: match01 Royal Hogs74–82s at0.5s (17), match01 Minions114–130s
at1s (17), match03 actual combat52–57s at1s (6). Underlying match and recording
identities remain separate. Third-match scene is battlefield combat, not the
old matchmaking prefix; reserved as a separate-match diagnostic, NOT blind
because earlier general development exposure is disclosed. Match02 stays
truncated/excluded without deletion or conversion to Negative.

Private review packet has40 raw JPG previews/40 corresponding annotated JPGs,
5 original-pixel contact sheets, a four-member Royal Hogs diagram,49 object
candidate rows,39 pending relationships and31 unknown-region rows. The four
physical member hypotheses are distinct from the shared deployment hypothesis;
later crossings/occlusion leave identity unknown. No card-play onset is inferred
from count. Actual class/bbox/identity/group fields are empty, owner unknown;
all proposals require human confirmation, correction or addition of missing
objects. Confirmed GT0, Negative0, no new lock or training qualification.

Only existing model/track outputs are auxiliary; no new inference or tracking.
Disjoint model boxes are not shown as object associations. Match03 selected
window has no cached predictions and is not counted as a miss. Detection,
fragmentation/ID-switch, owner coverage AND accuracy, group-link coverage and
timing definitions are fixed for future independently confirmed visual GT;
all current formal values null. Valid track ID is required for tracking match.

34 artifact readback checks pass;2705 previous materials and220 protected
tracked files are hash-identical. Artifact receipt checks491 enumerated private
files; final privacy check493/493 ignored and none tracked. Complete offline
suite908 pass/3 existing Windows symlink skips; original-pixel/proposal contracts
48 pass (956 distinct tests combined). Pip check passes. No production code,
dependency, storage,
App/Android, original source/GT/scorer/engine/historical-result change.
See [review packet and fresh verification](checkpoints/2026-10-09-module3c-visual-evidence-mini-batch.md).
Stop at `MODULE_3C_VISUAL_GT_REVIEW_READY`; await user/ChatGPT review. Do not
claim visual identity accuracy, training sufficiency or runtime capability.

## Preserved checkpoint — Module3C4 parallel visual evidence experiment

Authorized from local `f3cd570ae759f6998a3045971c0c4d475ec9372e` on
`codex/module3c4-visual-evidence`; main stays published3D `602dd0f...`.
Only official pinned ByteTrack is tried, using existing frozen model detections;
no new detector/training/App/runtime game integration. Original3B, GT, scorer,
rules and old3C1/3C3 results remain immutable.

Sole actual same-input scoring is4/5 (baseline2/5), duplicate0 (baseline1), exit3.
Royal Hogs is missed, so duplicate0 is abstention, not validated grouping.10
outputs/6 unscored remain. Three newly matched direct entities become eligible
later because owner consensus/fragmentation changes the input; onset improvement
is not proven. All raw observation IDs/PTS/bboxes/confidence remain unchanged.

Five-class fixed denominator792: ByteTrack66 tracks/35 singletons versus
original61/13; assignment678/792. Owner flips52→0 on identical owner-agnostic
links, known-known coverage69.28%, unknown335/792 (42.30%). No physical identity
or owner GT, hence no accuracy/true fragmentation claim. Four stable Royal
member identities are not established; a two-track cohort is only a hypothesis.

An independently fixed diagnostic prefix of third recording (80 samples/301
proposals) is matchmaking UI, with0 five-rule-class observations. It cannot
test tracking/generalization; preserve without moving the window after results.
Prior general data exposure is disclosed; not a blind test.

Standalone tracking environment has NumPy1.26.4/SciPy1.13.1/LAP0.5.13; original
environments unchanged. Source/notice/license bytes stay ignored/private and
hash-bound. MOT IDs never become trusted human continuity; only owner/source
projection enters unchanged3B. Context region/motion never decide map-half owner.
Diagnostic-only earliest-member/span defect was reproduced synthetically and
reconciled as v2; all33337 owner/evidence projections equal sealedv1, no new
detector/tracker/engine/score run. No parameter-driven rerun.

Fresh checks:1553 passed/4 existing Windows symlink-permission skips
(new tracker75/0, related570/1, offline908/3). All three dependency checks and
diff check pass.2580 existing material files and156 old non-document sources
remain hash-identical;7546 private files are ignored and none tracked.
App/Android checks are Not Run because those systems were not changed.

See [fresh verification and recommendations](VERIFICATION_MODULE3C4.md) and
[historical checkpoint](checkpoints/2026-10-09-module3c4-visual-evidence.md).
Stop after local commit. Do not promote, push/merge, train or start the next
module. Next recommendation is small reviewed visual identity/owner support
plus battlefield-scene qualification, not another event-rule loop.

## Preserved checkpoint — Module 3C-3 experimental deployment / spawn Shadow

Authorized from local diagnosis commit
`bbcd0917493e8d04aa8a61bc74d3da4d2941b376` on
`codex/module3c3-deployment-spawn-shadow`. Module3C-2 is closed by the user's
explicit decision, not automatic detector acceptance. Production3B engine,
adapter, tracker/Episode/rules, GT and one-sided scoring remain unchanged.

One scored same-input Shadow experiment: baseline2/5 hits and1 duplicate becomes
0/5 hits and0 duplicates, with2 PROVISIONAL outputs and2337 UNRESOLVED candidates.
Twelve of14 original emitted events, including both Royal Hogs episodes and the
previous Minions hit, abstain due to overlapping identity/owner conflicts.
Actual Shadow groups are empty: reduced duplication comes from withholding both
Hog events, NOT validated group association. Do not replace the production engine.
All original candidates/events and IDs/times remain in the diagnostic output.

First-seen, confirmation and estimated deployment fields are separate. Algorithmic
deployment estimates are null. Four actual source-video windows support the three
early target detections and one four-Hog arrival; adjacent PTS frames bound visible
arrival cues, not exact player release/server spawn or new human GT. These notes
never supply algorithm answers. Original early misses remain misses.

Synthetic tests exercise staged discovery, moving/temporarily missing members,
owner flicker, genuine separate second groups and ambiguous overlaps. No long
cooldown, GT identity/duplicate injection or timing-window change. An initial
unscored IO abort (49MB detector stream versus the old16MB Oracle loader) was
fixed only in the independent Shadow CLI; policy remained exactly frozen.
Both the abort and the sole subsequent scored FAIL are retained.

Fresh complete Python regression:1478 passed/4 existing Windows permission skips
(related370/1, offline908/3, smoke200). Both pip checks pass; no installation,
model inference/training, App/Android build, persistent storage or old lock change.
Private source-pixel sheets, sealed experiment, timeline and review index remain
ignored under `outputs/module3c3/`. See
[verification and checks](VERIFICATION_MODULE3C3.md) and
[checkpoint](checkpoints/2026-10-09-module3c3-shadow-prototype.md).

Stop after the local commit; no push/main merge or next-module work. A subsequent
decision should prioritize visual identity/owner reliability and birth-related
evidence, not another same-GT rule-tuning loop. No live-game authority is granted.

## Preserved checkpoint — Module 3C-2 frozen detector failure diagnosis

Latest explicit authority is diagnosis/minimal proven-defect repair only, from
local3C-1 `b146a4f81a31d33e73d72cfcc49c33721608f9e9` on new feature
`codex/module3c2-detector-failure-diagnosis`. No deterministic adapter/PTS/track
implementation violation explaining the observed failures was established;
production code, parameters, rules, scorer and GT remain unchanged. Do not
describe this as a detector repair/PASS or as independent ChatGPT acceptance.

All1523 frames/33337 predictions retain exact raw→observation coordinates,
class/owner/confidence and PTS. Three missed events first appear at30.5/77.75/
102.25s, confirm at30.75/78/102.75s, versus approximateGT31.5/78/102.5s.
Their stable tracks begin at those exact first-seen times. Frozen scoring is
one-sided and uses first-seen, not confirmation. Physical onset and whether an
early box is the correct GT entity remain unproven; no shift/window change.

Royal Hogs produces two different two-member episodes at75.75/76.0 and76.75/
77.25s. Three then four same-frame opponent observations exhaust two then three
existing tracks, yielding new tracks and a second episode. No same-episode
reemission or avoidable association-cardinality failure was demonstrated.
Late member discovery versus real new deployment is not established by these
fields. GT-free subset/synthetic replays expose a known policy ambiguity:
new track IDs are insufficient birth evidence, not an automatic grounds for
merging or increasing cooldown. Owner flicker is a visual identity risk, not
proven physical continuity or a mapping inversion.

Fresh full related contracts:331 passed/1 existing Windows symlink skip; both
dependency checks pass. Original predictions replay without new inference;
observations/tracks/episodes/candidates/events are byte-identical to3C-1, and
all scoring fields except run-manifest binding agree:2/5 hits,1 duplicate,
3 zero-output dedupe windows,12 unscored outputs. Four unresolved stay
non-negative; match04 candidate12 (69–75s) has zero Witch predictions and
cannot demonstrate continuity. This is not a full-match absence claim.
No full-match FP/min or cross-match-generalization claim.

Read-only diagnostics/new replay/evaluation and test receipts remain ignored
under `outputs/module3c2/`; no new persistent storage/schema/dependency or APK.
See [diagnosis and fresh verification](VERIFICATION_MODULE3C2.md) and
[checkpoint](checkpoints/2026-10-09-module3c2-detector-diagnosis.md).
Stop after a local documentation commit. No push/main merge, training,
Android/live integration or automatic next step. Recommended follow-up is
independent diagnosis review, not immediate retraining or GT-tuned repair.

## Preserved checkpoint — Module 3C-1 real detector baseline

Authorized on2026-10-08 from published main
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`; feature
`codex/module3c1-detector-event-baseline`. Actual retained KataCR predictions from
complete match01, then match04, feed the unchanged3B engine.1523 actual PTS samples,
33337 observations,2339 candidates,14 emitted events. No Human-GT identities,
Event GT inputs, training, downloads, Android/App or live-game changes.

Frozen scoring is a valid **FAIL** (exit3):2/5 positives,1 Royal Hogs duplicate,
0 explicit no-new-play false emissions. Three dedupe windows are sampled and each
has0 new event, but candidate12 has0 Witch predictions: not evidence of Witch
continuity. Three fixed-window misses have earlier same-class first-seen outputs
(-1/-0.25/-0.25s), not zero visual support; no GT/scoring adjustment.12 inherited
unscored outputs include the Royal Hogs duplicate, whose failure remains counted.
Four unresolved windows stay non-negative; full-match FP/min cannot be computed.

Raw owner is unvalidated model output, origin/form unknown. Existing engine STRONG
does not establish a true deployment or calibrated confidence. About3.2FPS steady
model inference; not realtime/phone/cross-match validation. Model-vs-engine causes
are separated as observed mechanics vs unproven physical explanations.

Prediction, replay and evaluation versions are sealed separately; post-score
timeline,12 redacted contact sheets and finite track/Episode forensic evidence
remain local/ignored. Fresh final regression:1439 Python passed/4 existing permission
skips (offline908/3, contracts331/1, smoke200); App102/Node8 and both pip checks pass.
2165 old material files and144 old non-document sources remain byte-identical.
Diff/privacy/manifest checks pass; no dependency or storage/schema change.
See [actual baseline and limitations](VERIFICATION_MODULE3C1.md).

Stopping point is the local baseline review packet, not detector acceptance.
No push/main merge, automatic tuning or
repair, training, App hookup, Module4/cycle/elixir/live-game/next module.

## Preserved checkpoint — Module 3D accepted real-device closeout

On2026-10-08 the user explicitly confirms personally completing the new APK's
Android physical-device acceptance: `MODULE_3D_REAL_DEVICE_ACCEPTED`. Confirmed
scope is local Oracle JSON import,0/8→5/8, start/pause/continue/restart,1×/4×,
retained Mock and exclusion of the four unscored outputs from the confirmed deck.
Reviewer/confirmation source is the user; this is not a new Codex physical-phone
test. Phone model/OS, device-side APK hash, performance and broader compatibility
are not supplied and are not invented.

Authorized closeout starts from implementation
`cf9d2995ac6d206ad57c40ce24b72538e3584af4` on the existing feature branch. Only
acceptance/status/checkpoint documentation changes; event engine, App source,
GT locks, Oracle results and private demo stay unchanged. Fresh full regression,
build, artifact/privacy/hash and Git checks precede ff-only main merge and push;
retain `codex/module3d-offline-recorded-replay`. Publication/ref evidence and actual
fresh closeout results are appended to
[Module3D verification](VERIFICATION_MODULE3D_OFFLINE.md).

Accepted APK remains SHA256
`52450eda8b0cbd6ff7dd27fb003fd6668e4d038366386ca4ec336f6c14052dc0`, private path
`outputs/module3d-offline/clash-tracker-recorded-event-debug.apk`. Private demo JSON
remains SHA256`bdefd0876d7b6b61d7aa63dc309eaaa6399e56435696929fa4e301348372b029`.
All artifacts and raw test receipts are local/ignored, not public assets.

Fresh final checks:1402 Python passed/4 existing permission skips;102 App and8 Node
tests passed; build/dependencies/signature/permissions/diff/privacy/protection pass.
Initial isolated-child timeout is preserved; same-test and full rerun pass without
changing code/test rules. No production source changed. The accepted APK is intact;
fresh rebuild is separately traced, not claimed byte-identical or phone-retested.

Stopping point: **Module3D accepted release checkpoint; no active next module**. See
[accepted checkpoint](checkpoints/2026-10-08-module3d-offline-replay-accepted.md).
No next module is authorized or started. This remains offline retrospective replay,
not detector/cross-match/live-game/cycle/evolution/elixir capability or permission.

## Preserved checkpoint — Module 3D-Offline Recorded Event Replay

The user's2026-10-08 authorization starts from published main/origin/main
`293e26e00c2d2418fc78f2b2177f7780197d37f6`, on
`codex/module3d-offline-recorded-replay` in the existing checkout. Implemented:
prepared local JSON import, strict validation, chronological automatic playback,
start/pause/resume/restart and1×/4×; separate original Mock mode. Repeated card plays
extend history without consuming another deck slot. App visibility loss pauses;
imports/history are deliberately in memory and reset on cold restart.

Only the five scored engine outputs from frozen repair replay/evaluation are
selected by the separate offline exporter. Real engine IDs/first-seen times are
retained: Witch32s, Royal Hogs77s, Flying Machine79.5s, Golden Knight104.5s,
Minions117s. Four unscored outputs are excluded from the prepared demo, not
deleted, reclassified as Negative or filtered inside the engine. Engine/card rules,
scoring, visual/Event GT locks, originalFAIL and repair outputs remain unchanged.
Witch's actual confirmation delay remains3s; playback is retrospective, not a
real-time/detector/cross-match performance claim.

The private ignored demo export is
`outputs/module3d-offline/verified-oracle-demo-v1/recorded-oracle-demo.json`, SHA256
`bdefd0876d7b6b61d7aa63dc309eaaa6399e56435696929fa4e301348372b029`.
It is not compiled into the APK or tracked. Generic raw nine-event packets are
not accepted by the App's demo importer. The metadata is provenance, not signed
authentication of arbitrary edited imports. No new dependency, SQLite/schema,
persistent repository or native permission is introduced.

Fresh App tests and rendered browser interaction pass. An isolated task-owned
API37 emulator verified actual native DocumentsUI JSON import and Android-clock
0/8→5/8, pause/resume/restart/source separation and Mock. New Debug APK delivery
and complete regression/protection evidence are recorded in
[Module3D verification](VERIFICATION_MODULE3D_OFFLINE.md).

**Stopping point:** `MODULE_3D_OFFLINE_REPLAY_READY`; this new APK's physical-phone
acceptance is pending user installation. No main merge/push, detector mode,
Module4/cycle/evolution/elixir, training, capture or real-game HUD. Next task is
only the user's offline new-APK smoke acceptance, not automatic next-module work.

## Preserved checkpoint — Module 3B accepted Oracle closeout

The user reports ChatGPT's independent repair acceptance:
`MODULE_3B_ORACLE_ENGINE_REPAIR_ACCEPTED — PASS WITH NOTES`, reviewing
`60494187aff7e3afc578c477212d963265460a46` through
`8abe6ee534653100066a44f45034c93a8b61ad6a`. This records the user's explicit
acceptance; this closeout does not claim to run another ChatGPT review.

The sealed result is5/5 positives each once and3/3 explicit dedupe windows.
Two mandatory retained notes:4 emitted events are unresolved/unscored, not
validated card plays or Negative; Witch confirmed_at34.5s versus GT31.5s is a
3s actual confirmation delay. Its first appearance32s is retrospective and
does not prove real-time latency. This remains an Oracle-only result whose five
accepted positives cover one match, not detector performance, cross-match
validation or full-match FP certification.

Authorized closeout: documentation-only acceptance recording, fresh full owned
regressions/dependency/diff/privacy/protection checks, a Conventional Commit,
ff-only main integration and main push while retaining the feature branch.
Tracking/episode/card parameters, sources, GT locks, original FAIL and all repair
versions remain unchanged. Fresh closeout regression:1370 Python passed/4 existing
Windows permission skips (offline908/3 in962.81s; contracts262/1; smoke200/0),
59 JavaScript passed, TypeScript/build/pip check exit0. Protection confirms1977
existing material hashes and138 non-document source files unchanged,100 relative
links valid, no credential patterns or tracked private media/GT/weights.
This documentation-only acceptance commit is the authorized main publication
checkpoint; exact release SHA and local/remote ref confirmation are in Git and
ignored `outputs/module3b-closeout/` receipts. No history rewrite or branch removal.
Publication is confirmed only when local main, origin/main and the retained
feature branch resolve to the publication commit, with remote readback recorded
in private receipts.
See [verification](VERIFICATION_MODULE3B.md).

Next possible task is Android offline RecordedEventSource playback, requiring
separate authorization and explicit handling of unscored outputs. No App/UI/APK change,
detector mode, Module4, card-cycle/elixir or live-game capability is authorized
or implemented in this closeout. Stop after publication.

## Preserved checkpoint — Module 3B Grouped Event Dedupe Repair

Current authorization is the minimal grouped repair, not detector mode or a new
Module3B plan. Baseline `60494187aff7e3afc578c477212d963265460a46`, same feature
branch `codex/module3b-oracle-event-engine`. Original FAIL outputs are unchanged.

Final same-stream Oracle replay/evaluation exits0/0:5/5 positives each once,
dedupe04/09/12 all0. The frozen94-observation stream is byte-identical; Event GT,
card registry/minimum units, first event timestamps/IDs and scoring are unchanged.
Minions continuation observations now extend the original event's evidence.

GroupedCardEpisode records deterministic members, first/last seen, emitted ID and
active/occluded/closed tracking state. Motion allowance uses actual elapsed gap
with fixed90px/s bound and original box budget;7.5s gap ceiling remains unchanged.
This is geometry/sampling continuity, not elapsed-card cooldown or a proven
physical motion limit. Fresh tracks can form a new episode while old units live.
Trusted human appearance continuity can restore previously unseen members.

No detector/training, new frames/GT, App changes, next module, main merge or push.
Fresh checks:1370 Python passed/4 permission skips;59 JavaScript passed;
TypeScript/build/pip check exit0;1884 old file hashes unchanged; diff/privacy and
103-link checks passed. Fresh verification and protection receipts are under ignored
`outputs/module3b-repair/`; completion details in
[verification](VERIFICATION_MODULE3B.md). Stop for independent review. Oracle
PASS does not establish real-time latency, deployment-onset proof, cross-match
generalization or full-match FP rate. Unknown remains unscored, not Negative.

## Preserved checkpoint — original Module 3B fixed replay FAIL

Latest2026-10-07 authorization accepts3A and explicitly permits only the3B
detector-independent Oracle engine. Baseline
`d4c5b94625dda49dfb1af2c1b5c8d4851751650a`; branch
`codex/module3b-oracle-event-engine`, same checkout. Event GT byteSHA remains
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`,
fresh load_lock exit0. All old visual/event locks and experiments are preserved.

Pure deterministic tracking/grouping and five versioned card rules are present.
Human visual adapter and Event GT scorer are separate: replay uses all83 accepted
multiclass boxes/48 frames plus a separately declared legacy11-object/4-frame
visual continuity regression. Event GT never selects or corrects engine inputs.
Unresolved observation tokens are not entity IDs; old spawned Skeleton stays a
visual unit and cannot emit a Skeleton card play.

Fixed replay/evaluation exits0/3:5/5 positive hits, but explicit no-new windows
04/09/12 produce0/1/0. The127s Minions continuation incorrectly becomes a new
group/event, so status is `MODULE_3B_ORACLE_ENGINE_FAIL`, **not** Module3B accepted.
Eleven total outputs include five unscored observations in unknown/unreviewed
time; no false-positive negatives or full-match rate are fabricated.

First appearance and confirmed_at are recorded separately: Witch32s/34.5s versus
GT31.5s. Offline retrospective hit is not <=2.5s real-time confirmation. Genuine
human continuity overrides gaps; geometric continuity remains insufficient on
this sparse input. No real-result-based parameter tuning or GT changes.

Offline recorded JSON adapter works without fake probabilities (confidence=null).
The App UI/mock buttons and installed APK remain unchanged/unwired. No detector,
training, fresh frames/annotations, 8-card/cycle/elixir, capture, overlay, live
game, push/main merge or next module. Fresh checks:1356 Python passes/4 skips,
59 JavaScript passes, App TypeScript/build and dependency check exit0;1814 old
material hashes unchanged, privacy/diff/link checks passed. Local-only checkpoint
and final Git receipt are recorded in the private completion report; see
[actual3B evidence](VERIFICATION_MODULE3B.md). Stop for
ChatGPT/user review of FAIL; do not automatically repair using Event GT answers.

## Preserved accepted checkpoint — Module 3A user-attested Event GT locked

The user's latest2026-10-07 request explicitly attests the returned ChatGPT
context-review decisions and authorizes a new Deployment Event GT Lock v1.
This return-validation checkpoint starts at
`5179569bef0773379715b4c2b0c191ce08ba64f0`; branch
`codex/module3a-deployment-event-gt` in the existing checkout.

New private artifacts: `outputs/module3a/event-gt-lock-v1/human-return.v1.json`
and `deployment_event_gt.lock.v1.json` in the same directory. The exclusive v1
lock was read back and revalidated, exit0; overwrite refusal was also verified.
Lock file SHA256:
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
Canonical lock digest:
`f7709ba45189546df5a74991ce88c8d1911eec337640d68623f651377540eacd`.

The12 original candidates now have a separate complete user-attested partition:
5 confirmed card plays (3 direct /2 grouped),3 continuity/dedupe outcomes,
4 unresolved/non-evaluable candidates,0 Negative. Confirmed02 Witch31.5s,
05 Royal Hogs75.5s,06 Flying Machine78s,07 Golden Knight102.5s,08 Minions116s:
all opponent, form=unknown, human_confirmed and evaluable=true. Timestamps are
approximate human annotations, not fabricated exact deployment bounds.

04 is continuity with unresolved03;12 is continuity with unresolved11. Neither
resolves onset or mints an event.09 merges into confirmed08.01/03/10/11 keep
`deployment_onset_outside_review_window`, never no-play Negative. The lock records
actual_human_confirmation=true, human_review_attested=true, reviewer=user,
review_basis=chatgpt_visual_review and
confirmation_source=user_attestation_based_on_chatgpt_visual_review.
ChatGPT is not the human reviewer.

Confirmed events cover only natural_match_01. Reviewed windows also included04,
but its onset remains unresolved; no cross-match event validation, detector
performance, full-match event coverage,8-card/cycle/elixir completion is claimed.
Own/unknown-owner, null card mappings and Witch-spawned Skeleton do not become
opponent card-play GT. The original pending plan/blank template,89MB context
bundle, lightweight supplement and all existing visual locks remain unchanged.
The original01→02→03→04 inventory is preserved;02 remains truncated/training
excluded,03 has no selected confirmed anchor,04 remains DEV_TUNE/not blind.

The new tool is manual annotation validation/freeze only; bundle.py, Module1/2A1
extractor/prepare/validate/review, detector/training environments and App remain
unchanged. Existing83-box/9-class visual GT is retained separately, not rewritten
as event GT. [Actual verification](VERIFICATION_MODULE3A.md) records fresh tests,
private-source checks and preservation. Stop here for acceptance; Module3B needs
separate authorization. No training, App/game integration, capture, overlay,
main merge or push.

## Preserved checkpoint — Milestone 2 closed within the authorized scope

On2026-10-07 the user explicitly confirms batch02's ChatGPT visual-review
suggestions and reports the six physical-phone mock smoke checks passed.
Closeout starts at `cbc6dd7872d05bef48e2a157c5a1a2e608564584` on
`codex/milestone2-apk-and-first-gt`. Public changes are documentation only;
existing tool/schema, App behavior, environments and historical results stay unchanged.

TaskA2 is now USER_ATTESTED_VISUAL_GT_FROZEN:24 inspected frames72..129.5s,
39 accepted boxes on21 frames,7 classes this batch,0 rejects and452 pending.
Counts: Minion13, Flying Machine8, Royal Hog5, Golden Knight5, Mortar4,
Cannon3, Barbarian Barrel visual1. The last three new class identities relative
to batch01 are Royal Hog, Flying Machine and Barbarian Barrel visual.
Reviewer=user; actual_human_confirmation=true, human_review_attested=true,
review_basis=chatgpt_visual_review,
confirmation_source=user_attestation_based_on_chatgpt_visual_review.
ChatGPT is not a human reviewer. Original bboxes are accepted unchanged;
form/origin stay unknown; Cannon and Barbarian Barrel mappings stay null.
Four human owner overrides retain the unchanged raw teacher owner=own separately.

New exclusive annotation-only revision:
`outputs/milestone1/milestone2-second-multiclass-human-gt-v1/`.
Lock `second_multiclass_human_gt.snapshot_lock.v1.json`, file SHA256
`4a2bf638855d18b6d00ddc35738c3b4f2cdc5a460837364989e552d169d986f8`;
canonical digest `3d2434359155d7fc8ce35ffa530e4be8950250beb2f43bd6557b88c375868195`.
It SHA-binds9 member files, exact PTS/source/predictions/packet, return,
attestation, coverage/identity supplement, review CSVs and first-lock reference.
The first lock SHA remains
`7d4a9a7fafd627f1fbf82f73db3d66232163e5aac14dbdc8f5996c2c0b3a9dae`.
Both revisions are preserved, not merged into a Training Dataset.

Only9 explicitly attested class/frame coverage rows are recorded:3 exhaustive
positive Minion rows117/119.5/122s and6 unresolved/positive-only rows
(Royal Hog77/79.5/82s; Minion84.5/124.5/127s). Accepting other boxes does not
invent exhaustive absence. Five explicit continuous appearance groups are
retained;18 Minion/Royal Hog tokens identify observations only, not independent
entities/deployments. No cross-batch identity inference or primary/spawned-role
assertion is made. Eligible class-specific negatives and card plays remain0.

Cumulative:48 inspected chronological sourceframes from one underlying match,
83 accepted boxes on44 sourceframes,9 confirmed visual classes,7 unique non-null
canonical mappings,932 pending proposals and2 historical rejects. Teacher labels
are not class counts. This is annotation progress, not model quality, training
readiness, cross-match generalization or automatic card recording.
training_qualified=false; ordinary_training_export_allowed=false.
Match02 remains mid-match truncated and excluded from training/Negative.

TaskB2: `REAL_DEVICE_SMOKE_TEST_PASSED`, **user-reported** installation, launch,
Witch mock, Balloon mock,2/8 and Reset0/8. No agent phone retest or new ADB
operation was performed. Phone model/Android version, detailed touch/layout,
cold-start/restart and performance remain unreported, not invented passes.
APK SHA stays `774ed13e2ac69690330cf126084aee15b19ecf676e579a1872eaa7e37ea6bb0d`;
no rebuild/product/permission changes, live detector, Clash Royale connection
or real-game HUD. Historical device-pending reports are preserved.

Fresh scoped regression:59 Python tests (51 tool +8 private transcription/logging)
and8 Node reviewer/UI tests passed. Existing CLI validate/import exit0; forbidden
overwrite exit2 leaves new GT bytes unchanged; lock/member readback passes.
See [closeout verification](VERIFICATION_MILESTONE2.md) for protection and limits.
Next: stop for milestone handoff. A future offline visual-observation→confirmed
card-play bridge requires separate authorization; do not start Module3, training,
new permissions, real HUD, main integration or push.

## Preserved checkpoint — Milestone 2: first Debug APK and first GT batch

On2026-10-07 the user accepts Milestone1 and authorizes only two bounded tasks:
build the unchanged mock App into a Debug APK using minimum official Android
tooling, and prepare the first small chronological multiclass review batch.
No new product design, training, real-game connection/HUD, main merge or push.

TaskB1: inspect/install isolated necessary JDK/SDK/platform/build/platform-tools,
keep Gradle managed by the existing wrapper, sync/build Debug, inspect package
permissions/signature/SHA, and perform minimal startup on an available test target.
Do not silently treat static package checks or host Web preview as device launch.
No release signing or capture/overlay/Accessibility/game automation is authorized.

TaskA1: reuse existing proposal/correction tooling; first24 fixed-stride frames
from original match01. Five corrections, selected-class exhaustive review,
Unknown/reject protection and spawned/secondary semantics remain unchanged.
The user chose ChatGPT independent review followed by explicit user confirmation.
That confirmation has now been received and imported truthfully as user-attested
visual GT; it does not qualify this new batch for training. Source02 remains
truncated/training-excluded.

Branch `codex/milestone2-apk-and-first-gt`, baseline
`97d87d875e97b847e79fd00433a79d779e9abd1c`.

TaskB1 is verified complete: unchanged mock App Debug APK, SHA256
`774ed13e2ac69690330cf126084aee15b19ecf676e579a1872eaa7e37ea6bb0d`,
at ignored `outputs/milestone2/clash-tracker-simulated-debug.apk`.
Official isolated Temurin21.0.12.1+1 / SDK36 rev2 / build-tools35.0.0 /
platform-tools37.0.1 / Gradle8.14.3 built successfully. Existing API37 emulator
installed/launched the APK and exercised 0/8→1/8→2/8→Reset0/8→replay1/8;
no physical-phone test or performance qualification is claimed. Merged APK has
only AndroidX's own signature receiver permission, no capture/overlay/Internet/
Accessibility permission. The pre-existing unrelated App was restored, not
modified or cleared. No public App source/dependency change was needed.

TaskA1's first confirmed batch is now frozen: 24 inspected first-match frames,
44 accepted boxes on23 frames, 2 rejects and480 remaining pending/unknown
proposals. Six visual classes are confirmed: Minion15, Skeleton Barrel6,
Mortar10, Witch6, Golden Knight2, Cannon-like structure5. Five non-null canonical
mappings are retained; Cannon mapping is null and its source card unknown.
All accepted form/origin fields remain unknown. No bbox/label correction or
missing box is invented. There are38 class-specific coverage records:
32 exhaustive positive rows and6 unresolved/positive-only rows, zero eligible
class-specific negatives and zero confirmed card plays.

The user explicitly attests the ChatGPT visual-review suggestions as their
confirmation basis: actual_human_confirmation=true, human_review_attested=true,
reviewer=user, review_basis=chatgpt_visual_review,
confirmation_source=user_attestation_based_on_chatgpt_visual_review. ChatGPT is
not represented as a human reviewer. Exact decisions and extra attestation facts
are in separate SHA-bound private files; the strict return schema is unchanged.

New exclusive annotation-only revision:
`outputs/milestone1/milestone2-first-multiclass-human-gt-v1/`.
Lock: `first_multiclass_human_gt.snapshot_lock.v1.json`, file SHA256
`7d4a9a7fafd627f1fbf82f73db3d66232163e5aac14dbdc8f5996c2c0b3a9dae`;
canonical lock digest
`82f27b0905d5a597a2564e37926470497b92b0a16cc353a02f2b1e01e192ad93`.
It binds the unchanged source bundle/packet/predictions, exact PTS/frame metadata,
return, user attestation, annotations, coverage/identity supplement and review CSVs.
It is not a Training Dataset, Model or Test Lock: training_qualified=false and
ordinary_training_export_allowed=false. No new training or blind split is assigned.

Only the four user-specified appearance assignments are recorded (two Skeleton
Barrel groups, one continuous Mortar and one Cannon-like group). Unconfirmed
Minion/Witch/Golden Knight cross-frame identity uses explicitly observation-only
unresolved tokens, not new entities, independent appearances or deployments.
Do not count appearance_groups length as independent events or infer primary/
spawned roles from canonical mappings. Missing/occluded evidence remains unresolved.
Review packet images may show player UI and remain private, never public assets.
Next action: stage acceptance; stop without training, Module3 or a new milestone.
Fresh commands, artifacts, limitations and checks are in
[Milestone2 verification](VERIFICATION_MILESTONE2.md).

Old locks, Attempts01/02, benchmark, Milestone1 bundles and Python environments
must stay unchanged. No automatic later module or model training.

## Accepted Milestone 1 checkpoint — local correction and simulated App

The user explicitly authorizes these two independent tasks on 2026-10-07:
KataCR predictions as pending local proposals with separate human correction,
and a React/TypeScript/Capacitor mock-event App with an App-internal HUD.
Both scoped implementations and verification are complete; user acceptance was
explicitly relayed2026-10-07. At that checkpoint this was tool/mock-UI completion,
not detector accuracy, reviewed real GT, training readiness or a device-tested
Android APK. The later bounded APK build is recorded above.
See the [bounded design](superpowers/specs/2026-10-07-preannotation-and-simulated-app-design.md)
and [implementation plan](superpowers/plans/2026-10-07-preannotation-and-simulated-app.md).

Use original recording order; match02 stays mid-match truncated and training
ineligible. Accept/reject/relabel/bbox correction/manual missing objects must
remain separate from teacher predictions. Per-class exhaustive coverage requires
human attestation; Unknown/rejected/unmarked areas do not become Negative.
10–20 classes is a goal, not a quota or an automatic training-readiness gate.
No new training or Dataset Lock. Mock Witch/Balloon events alone drive discovery
2/8; no detector, capture, game connection, cross-app permission, card-cycle,
evolution or elixir implementation. Live gameplay and HUD stay Gated.

Branch: `codex/milestone1-data-and-simulated-app`, initial baseline
`17242b717de91a69b1a6d65511c10c0857337b1b`; no push/main merge authorized.
Old locks, fine-tuning attempts, benchmark and environments remain protected.

Verified deliverables:

- Additive `tools/preannotation/`: separate immutable predictions, human return
  and exclusive revision; accept/reject/relabel/correct/add, class-specific
  coverage and continuity metadata. Real match01 demonstration: 12 exact-PTS
  source frames / 272 pending proposals; no real human GT was imported.
- Synthetic browser demonstration exercised all five actions, download,
  validate/import exit0, four simulated positives, no negatives and no card plays.
  Frame loading/failure guards and one-read return snapshot binding were repaired
  and approved in scoped code re-review.
- Mock App: play/reset/replay, 0/8→1/8→2/8, mobile/desktop screenshots, strict
  mock-only event boundary. Web build and Capacitor Android sync passed; at that
  checkpoint no APK build ran because the required toolchain was absent.
- Fresh maintained offline regression: 908 passed / 3 existing permission skips;
  new review-tool Python 51 passed / Node8 passed; App43 tests, strict TypeScript,
  production build and npm audit0. All32,217 historical files,160 old YOLOX source
  files and all three existing Python package inventories unchanged.

See [completion/verification](VERIFICATION_MILESTONE1.md). Its prior stopping
point is preserved; the newly authorized minimum Android tooling and small GT
review batch are described above. No automatic training, push or merge.

## Preserved checkpoint — existing detector fixed benchmark executed; visual review pending

The user relayed ChatGPT's formal acceptance
`ATTEMPT02_VALID_BUT_DATA_LIMITED`. Self-trained two-class fine-tuning is paused;
no Attempt03, confidence-threshold/optimizer-step change or additional Skeleton
annotation is authorized. Keep the exact Attempt01/02 results, snapshots, locks,
spawned-unit relationships and historical specialist validators unchanged.

The result ZIP could not be read in ChatGPT's extraction environment. This
acceptance is based on the reported statistics, not a completed independent
per-image or code review, and does not qualify a usable detector. ROI, training
data, input size and optimizer budget changed together, so the comparison cannot
establish an isolated causal explanation.

The authorized **Existing Multiclass Detector Local Benchmark** completed its
one fixed confidence0.1 dual-detector CUDA run in a separate environment. Input
is the original first retained `natural_match_01`, not blind: 240 frames at
4FPS, PTS12..71.75s in the half-open12..72s range. Dual inference median310.05ms,
P95 332.99ms, wall97.88s; Torch peak allocated553.83MiB. These offline local
measurements do not qualify real-time or mobile execution.

Raw9287 proposals became5404 combined;86 fixed-UI proposals were removed,
leaving5318. The84 proposal labels include towers/UI/noise, not84 verified
visual classes or cards. Outputs await independent ChatGPT manual visual review;
no verified detection accuracy, generalization or model adoption is claimed.
No confidence tuning, repeat, tracking, card event or training occurred.

Fresh historical helper regression:200passed/0failed,316.18s; the maintained
908-test suite was NOT rerun for this benchmark. All32,217 protected historical
files and160 original YOLOX source files remain unchanged. Both original
environment pip checks exit0 and package inventories are unchanged.
Root MIT does not override modified Ultralytics AGPL obligations. Weight/game
asset rights remain `unverified`; private local authority is not legal
clearance, redistribution or release permission. The published detector1
v0.7.13 filename contains internal train name v0.7.12. This wrapper explicitly
uses CUBIC; the upstream positional resize actually uses LINEAR, so preprocessing
is not claimed byte-identical. Both limitations are disclosed, not patched by
rerunning the fixed benchmark. See [benchmark verification](VERIFICATION_EXISTING_MULTICLASS_BENCHMARK.md).

Historical benchmark branch: `codex/existing-multiclass-local-benchmark`. Main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`; no push or merge. Next: manual
visual review of the preserved outputs, not automatic model adoption or a new
module. At that checkpoint no training, Module3, Android or live-game feature
was authorized; the current mock-only App authorization is stated above.

Primary/secondary refer to future visual-observation semantic responsibilities,
not directly to card events. A Witch detection still requires a separate,
confirmed deployment/event boundary before `OpponentCardPlayed`; spawned
Skeleton stays a visual unit and cannot imply a Skeleton card deployment.

## Preserved Attempt02 checkpoint — fixed run completed; valid but data limited

The user relayed ChatGPT acceptance of Attempt01 as
`TWO_CLASS_SMOKE_ATTEMPT01_VALID_BUT_INSUFFICIENT`, and explicitly authorized
one new Nano 640 / batch1 / FP32 / 300-step Attempt02. Its single real run and
single two-frame DEV_TUNE evaluation have now completed. `natural_match_01` remains TRAIN;
`natural_match_04` is now DEV_TUNE, not blind or independent testing. Do not
retroactively edit the historical locked DEV_VAL fields or Attempt01 outputs.

Original TRAIN sanity passed: two PNGs and all six boxes match the frozen v1
and actual Attempt01 export, Skeleton=0/Witch=1. Fixed ROI `[0,120,432,744]`
is identical for TRAIN/DEV_TUNE. On 2026-10-07 the user relayed ChatGPT's
`ATTEMPT02_TRAIN_HUMAN_REVIEW_CONFIRMED`: 11 new confirmed objects, four
rejected; all original bboxes accepted. Standard TRAIN is 14 frames / 15 boxes:
eight exhaustive negatives and six exhaustive positives (Witch 6, Skeleton 9).
The two partial 162s/165s frames and their confirmed Witch boxes stay archived
in the new 16-frame / 17-object snapshot but cannot enter ordinary loss.
Rejected objects/Unknown are not Negative. Old episode and source relationships
are retained; expanding frames does not create independent deployments.

The unchanged strict loader has validated eight existing report/index sets,
195 original requests. Expanded v2 snapshot SHA is
`f25c54e6dfc578a6d9edd69c2adfa712fb79fa5c924b25a7ad6999951707c1c2`;
lock and exact ROI export validate exit0. TRAIN overlays inspected, no class swap.
Fresh helper regression: 200 passed; full maintained regression908passed/3
existing Windows symlink-permission skips, exit0 (2079.70s). Before-run protection confirms 32,217 old
hashes unchanged, 32,143 private paths ignored, both pip checks exit0 and no
environment/source change. Fresh after-run check again confirms32,217 historical
files unchanged/32,143private paths ignored, all160YOLOX source files unchanged,
both pip checks exit0, and new GT/export/config unchanged and valid.
The real run froze clean local commit `361a2e4c074195ebc3c42e1b5a1e951884cd82b8`;
exactly300CUDA steps,126positive GPU assignments/174negative steps, zero CPU
fallback, checkpoint strict round-trip passed. Training184.20s, first/last14-step
mean loss11.571084/1.910648, peak Torch allocation322.22MiB. Final checkpoint SHA
`8423fbe8be74302b65b163ec6701d69bde865df950b20eb469597e6de7b67811`.
DEV_TUNE matches2/5 (Witch2/2, Skeleton0/3); Witch confidence0.001086/0.004371
is still extremely low. Complete68s has15FP; partial72s has4unjudged, notFP.
This is a valid bounded experiment with insufficient usable detection, not
accuracy acceptance. No result-driven parameter change, rerun or Attempt03.

The completed local results ZIP (931274bytes,8members,CRC/manifest/hashes checked)
and all original results remain preserved. Its former result-review waiting
boundary is superseded by the user's statistics-based acceptance above; do not
claim independent visual/code review. Do not request new recordings, reset old
locks, train drafts, retune from DEV, retry Attempt03 or enter Module3.
See [protocol](PHASE_C_ATTEMPT02_PROTOCOL.md) and
[preparation verification](VERIFICATION_ATTEMPT02_PREPARATION.md).
Actual confirmed-data/run evidence: [Attempt02 verification](VERIFICATION_ATTEMPT02.md).

## Preserved historical checkpoint — Attempt01 completed and accepted insufficient

The authorized YOLOX-Nano 416 / batch 1 / FP32 run completed exactly 100
optimizer steps on the GTX 1050 Ti, followed by one two-frame DEV_VAL evaluation.
Clean historical baseline: `b75819db3bc2c542eede1b28ac854049f7ba3acc`;
actual frozen run code: `bfc834dfc197d21528cf410591a41f53ab844fc3`.
Training took 40.20s; first/last ten-step mean losses 11.925852 / 2.136085;
100 CUDA assignments, zero CPU fallback, 320 parameter tensors changed.
Strict model/optimizer checkpoint reload passed. Peak allocated VRAM 117.61 MiB.
DEV_VAL fixed-IoU matches: **1/5**, one Witch at IoU 0.644608 but confidence
0.001066; all three Skeleton positives and the other Witch missed. This is a
weak low-score localization response, not reliable detection or generalization.
Complete 68s frame: 77 sampled-frame FP at the pre-fixed low confidence gate;
partial 72s: 30 unmatched unjudged, one outside-image padding candidate, no FP
claim. No threshold selection, second evaluation or additional training occurred.
See [Phase C verification](VERIFICATION_PHASE_C.md). The user's newly relayed
ChatGPT review accepted the insufficient result; no push or main integration.
Historical prohibitions below apply
to their earlier stage, not retrospectively to this authorized experiment.

Public artifact identities, explicitly authorized for publication now:

- Smoke GT Lock v1 file SHA-256:
  `f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1`.
- Training Dataset Lock v1 file SHA-256:
  `582dc30d3e418aebf09adfed931742627c29a1f3da1a19ae24c165621cc58e39`.

Artifacts, original frames, annotations and dataset exports remain ignored and
private. Their historical authorization flags remain unchanged; a separate
Phase C run contract carries the current training/official-weight authority.
Only official YOLOX COCO Nano release weights were used after recording
provenance. No third-party Clash Royale data/weights, Tiny experiment,
Blind Test, production Model Lock, Module 3 or Android/live feature is allowed.
New TRAIN GT drafts are separately authorized for Attempt02 review only; do not
alter this old v1 snapshot. See [old fixed smoke protocol](PHASE_C_SMOKE_PROTOCOL.md).

## Completed data checkpoint — private local 2-Class Training Dataset Lock v1

Status: **TWO_CLASS_TRAINING_DATASET_LOCKED — exclusive v1 creation/readback
and dataset-stage verification completed; stop before Phase C**. The current request
uses only the existing **2-Class
Smoke GT Lock v1**, its **11 confirmed boxes (four Witch / seven Skeleton)**,
`unit.witch` / `unit.skeleton`, match 01 / TRAIN and match 04 / DEV_VAL.
The separate private local **2-Class Training Dataset Lock v1**
(`two_class_training_dataset_lock`) has been exclusively created, referencing
the unchanged parent `two_class_smoke_gt_lock`.
Actual dedicated readiness and validate-lock/readback both exit 0; the retained
receipt records `TWO_CLASS_TRAINING_READY` and `training_qualified=true` only
within the approved internal scope. Protection confirms **1,462 existing files
unchanged**, the original GT v1 unchanged, and legacy source/tests/dependencies
unchanged. Lock, canonical digests and source hashes remain in private receipts.
Fresh joint private training-lock/original-GT tests: **65 passed** (40 new
training-adapter tests + 25 original GT tests), exit 0, 14.66s. Fresh full
maintained regression: **908 passed / 3 existing Windows symlink-permission
skips**, exit 0, 1052.47s; JUnit confirms zero failures/errors and no GUI skips.
Pip check and the scoped documentation diff check pass. This completed data
snapshot does not qualify a full production training pipeline or model accuracy.

Training-use provenance must record `source_type=user_recorded_gameplay`,
`intended_use=private_local_research_poc`, `user_training_authorized=true`,
`external_upload=false`, `redistribution=false`, and
`rights_clearance=unverified`. In this scope `training_qualified` means only
that the project's internal private local research PoC gate has passed. It is
not legal clearance, Supercell permission, commercial-use approval or a grant
of external upload/redistribution rights. The frozen GT-only v1 retains its
original `training_qualified=false`; passed qualification belongs only to the
new separate training snapshot after checked media binding/readiness.

Preserve owner/form/origin, the spawned-from relationships, group counts and
Unknown/rejection semantics. Freeze all 11 boxes/four frames, with default
complete selected-class supervision restricted to three frames/10 boxes. The
72s Witch positive remains `positive_only_requires_unknown_safe_consumer`:
standard full-frame loss/metrics are prohibited by default, and Unknown regions
cannot become background. Sampled GT cannot certify full-timeline absence or
FP/min. This round does not train, download weights, run real detector
inference, create a Model Lock or enter Phase C/later modules. No production
schema, 2A2/2B-1 contract, original 3–5-class gate, split or old lock is changed.
At that historical GT-return checkpoint, staging, commit, push or merge was
not authorized. Later phase authorizations and current Git boundaries are
recorded separately above; this sentence is not the active phase gate.

The ordinary-Minions four-match/eight-play target-recheck route and its outputs
are **superseded / historical**, retained as evidence. Their shortfall is not
the current product goal or a prerequisite for this two-class smoke snapshot.
See [current scope verification](VERIFICATION_M2B2B.md) and the
[historical target recount](VERIFICATION_M2B2_DATA.md).

## Superseded historical work — ordered retained-recording target recount

That bounded user instruction resolves source 02: there is no later clip, and actual
EOF still shows 0:52 with active battle. A new private pending-dataset revision
marks it **excluded: mid-match truncation, not usable in Training Dataset**.
Its recording, images, labels and earlier attestations remain preserved; it is
not Negative. This is not a requirement for a victory/defeat result screen.

Source 03 then source 04 receive bounded ordinary-Minions evidence review in
original intake order, using existing material only: **159 / 107 sampled frames,
18 / 12 contact sheets**, plus nine/seven original-image checks. Neither adds a
confirmed ordinary Minions deployment. This is sampled visual review by Codex,
not new ChatGPT GT, full-video playback or proof of full-timeline absence.
Unobserved/occluded regions remain Unknown; no frame or box adds an event.

Historical confirmed target support stays **one match / two independent plays**;
the historical confirmation gap against that request's four/eight gate is **three
matches / six plays**. Six historical individual boxes were accepted in a
ChatGPT review relayed by the user; no exhaustive per-frame unit GT has been
imported into the old specialist contract. Its checked native readiness remains
**zero eligible matches / zero eligible plays**, `valid=true`,
`training_data_ready=false`, CLI exit 3. No Training Dataset Lock was created
by that historical recount.
This bounded recount does not restore Minions as a fixed product standard or
roll back the multiclass route, Smoke GT Lock, old 2A2 lock or accepted 2B-1 FAIL.
No new extraction, model install/execution, training or Model Lock in that recount.
See [ordered-recount verification](VERIFICATION_M2B2_DATA.md).

## Preserved completed Phase B Model Environment Qualification

Completed environment checkpoint: **MODEL_ENVIRONMENT_QUALIFIED;
TWO_CLASS_SMOKE_GT_LOCKED; training_qualified=false at that stage; no Training
Dataset Lock or formal training in that stage**. Current data-lock authorization
is recorded above and does not retroactively change the environment result.
The user's separate Phase B authorization permits isolated installation and
synthetic optimizer/checkpoint probes, not real gameplay training. Windows 11
build 26200 / Python 3.12.4 / GTX 1050 Ti 4096 MiB / driver 582.28 / capability 6.1
actually execute CUDA, rather than relying on the driver name. PyTorch
2.7.1+cu118, TorchVision 0.22.1+cu118, runtime CUDA 11.8, cuDNN 90100 and
unmodified official YOLOX source 0.3.0 at
`6ddff4824372906469a7fae2dc3206c7aa4bbaee` are isolated under ignored outputs.

Nano 416 / batch 1 / FP32 passes three real synthetic loss/backward/optimizer
steps; Tiny batch 1 and optional Nano batch 2 each pass one step, after Nano's
baseline. All pass strict model/optimizer checkpoint round-trip (output difference
0), inference, CUDA NMS, finite gradients and nonzero parameter updates. No CPU
assignment fallback. Peak PyTorch allocator allocated/reserved MiB:
Nano b1 **122.31 / 134**, Tiny b1 **147.93 / 182**, Nano b2 **219.25 / 234**.
These exclude CUDA context, driver/WDDM and other applications; not whole-card
peak measurements or a real-dataset memory guarantee. No real GT/pixels or
pretrained weights are used; anonymous toy tensors only.

Fresh Phase B maintained regression: **908 passed / 3 existing Windows permission
skips**, exit 0, 1179.22 seconds. Private probe contract tests: **16 passed**.
Both environments' pip checks pass; all 22 model distributions have pinned
versions and recorded source/license metadata. YOLOX is source-path integration,
not a pip distribution with rewritten dependencies. Its required model-operation
imports are tested; the full official Trainer/real COCO pipeline/export/mobile
stack is not installed or qualified. Original `.venv` freeze is identical.
Scoped protection: **1,398 existing files unchanged**, including source/tests,
recordings, GT lock and old 2A2/2B-1 artifacts. Python audit counters show zero
network attempts or forbidden repository opens during model probes; they do not
provide OS/native-code sandbox isolation.

Recommended later baseline, once training gates and authorization pass: Nano
416 / batch 1 / FP32. Optional batch 2 passes this synthetic check but must be
remeasured with the actual data pipeline. That stage stopped for acceptance; environment success
does not authorize dataset training, weights download or the next module.

## Preserved 2-Class Smoke confirmed GT freeze

The prior user authorization established a separate Witch + Skeleton smoke milestone, with match
01 / TRAIN and match 04 / DEV_VAL. Owner remains GT metadata, not a detector
class; no own-support or owner-discrimination success is claimed. Witch form
may remain unknown when its visual identity is confirmed separately. Spawned
Skeletons are visual units, not Skeleton card deployments. Existing 3–5-class
schemas, readiness gates, splits and locks are unchanged.

The user relays ChatGPT verdict **TWO_CLASS_SMOKE_HUMAN_REVIEW_CONFIRMED** for
the exact small review ZIP. Objects 01–11 are confirmed, object 12 is rejected
as too ambiguous, and original bbox coordinates are unchanged. A new ignored
human-return/CSV presentation revision records **11 positive boxes (four Witch,
seven Skeleton), one rejection, four accepted appearance groups and four frames**.
Match 01 uses 163/164s; match 04 uses 68/72s. Witch form remains unknown, as do
the Skeleton forms. Confirmation attribution is ChatGPT review explicitly relayed
by the user, not a new independently retrieved reply or fabricated review time.

Each match has one human-confirmed independent Witch deployment group; repeated
frames do not add events. Both Skeleton groups have confirmed spawned-from-Witch
relationships and zero independent Skeleton card deployments. Individual
entity/source-card/causal-root IDs are not inferred. The 163/164/68-second frames
are reported exhaustive only for the two selected classes. The 72-second frame
remains partial/Unknown; its Witch positive is retained, rejected Skeleton12 is
not a negative, and the frame is not complete-supervision background. Sampled
GT does not establish full-timeline absence or a false-positive time denominator.

The separate **2-Class Smoke GT Lock v1** now freezes this reviewed Development
GT. It is an exclusive private `two_class_smoke_gt_lock` snapshot, verified by
a scoped one-off structure/relationship/media binder, not the old native training
readiness or blind Test GT Lock. Canonical semantic and envelope SHA-256 digests,
version identity, source PTS/PNG/report/index hashes and final-review attribution
are retained. No prior lock is overwritten. At that GT-only stage a Training
Dataset Lock still required separate training-use qualification; the frozen
`training_qualified=false` could not create a ready-for-training lock. The current
user authorization defines the separate private local PoC scope above, without
promoting the old GT lock or making a legal authorization conclusion.

Fresh private GT/immutability/presentation tests: **25 passed**, exit 0. GT
readback, final CSV/human-return consistency and **1,303 protected existing files
unchanged** are verified. The original reviewed ZIP and pending draft remain
unchanged; the final presentation supersedes display-only remnants without
altering locked GT. Visibility/occlusion are user-authorized local quality metadata,
not values invented as separately supplied by ChatGPT. Fresh pip check passes.
Fresh full maintained regression: **908 passed / 3 existing Windows permission
skips**, exit 0, 1289.98 seconds; no failures or GUI errors. The initial root-level
collection attempt included archived test copies and exited 2; rerunning the
unchanged official suite with its package configuration resolves that command-scope
issue without deleting packets or modifying tests. No production source/test/dependency change,
re-extraction, model use, weights, training or Phase B during that GT-only step.

The GT-only snapshot stays unchanged. Training-use provenance and Training Dataset
Lock now follow the separate current authorization above; the completed Phase B
only qualified the synthetic environment described above. The GT freeze itself
is not detector success or training permission. See
[latest verification](VERIFICATION_M2B2B.md). No commit, push or main integration.

## Preserved earlier human review material

That earlier authorized step was human review preparation only, with no new production
features. The user's returned review of matches 01/02 is retained separately as
a non-GT handoff: six historical Minion boxes are reported accepted, Witch form
remains unknown, summoned Skeleton observations are not direct-card deployments,
and match 02 is now excluded for confirmed mid-match truncation, with its
concrete EOF evidence retained. Time-separated
Witch sightings are not automatically promoted to independent deployments.
The existing pending draft (75 frames / eight boxes), old review bundle, 2A2
Lock and accepted 2B-1 FAIL remain byte-unchanged.

In original source order, a new ignored standalone review bundle now prepares
match 03 / TRAIN: **159 frames, 18 contact sheets**, then match 04 / DEV_VAL:
**107 frames, 12 contact sheets**. Total: **266 unique PTS frames / 30 review
contact sheets**, comprising 242 newly extracted fixed two-second samples and
24 reused unique technical boundary frames. No content-based frame selection,
class guessing, prelabels or new confirmed groups. Every human object field is
blank; existing completion attestations are retained, not newly qualified.
Sampling and absent boxes do not prove absence or full-timeline GT coverage.
The new ZIP and review index are verified; 645 relevant protected originals
remain unchanged. This run does not repeat the historical full regression suite.

The user reports having returned match 03/04 review and authorizes the separate
two-class smoke scope above; that high-level handoff does not confirm the new
precise boxes/groups. The historical zero-qualified result under the unchanged
3–5-class gates is not rewritten as a pass. Original material is retained.
See the latest [review-preparation verification](VERIFICATION_M2B2B.md).

## Historical Phase A implementation and unchanged 3–5-class rules

The user reports independent plan review PHASE_A_AUTHORIZED_WITH_SIMPLIFICATION
and authorizes Phase A only. Current branch:
`codex/module-2b2b-multiclass-infrastructure`, starting at local documentation
HEAD `d8a34a127e1507998fa0528d7d18bf244bb9001d` (not old main). The existing
directory and fixed environment are retained. No push or main integration.

Final owner gate: every selected class needs independently confirmed opponent
support in TRAIN and DEV_VAL; the entire 3–5-class collection needs at least one
selected class with additional own support in both splits. Other own subgroups
remain not_qualified / not_evaluated, without claims of bidirectional validation.
Unknown owner cannot become opponent or Negative. Scale Coverage Gate,
whole-match splits, provenance and immutable versions are unchanged.

Task 1 closed multiclass contract and terminal-frame compatibility repairs are
verified and independently reviewed. Final maintained regression: 778 passed /
two known Windows symlink-permission skips, exit 0, no GUI errors or skips.
Pip/diff checks passed; 22,939 originals unchanged and all private files ignored.
Task 2 candidate/scale/readiness is verified and locally committed at
`f72420e1b6578a161fef622d764b2ee71c6b2a6d`. On the user's explicit continuation,
the unchanged complete suite ran with a process-bound temporary system-awake
request: **822 passed / 2 existing Windows symlink-permission skips**, exit 0;
JUnit confirms zero failures/errors. The sleep request was released, with no
permanent power-policy change or display-awake requirement. Fresh pip and
working/staged diff checks pass; **22,939 original private files unchanged,
27,028 current private files ignored**, legacy source/tests/config unchanged.
The earlier child-process timeout and subsequent sleep-interrupted run remain
separate historical receipts, not erased or retrospectively called passing.
No legacy test, timeout, plugin or dependency was changed to obtain the fresh pass.
Task 3 checked binding and immutable locks are verified and locally committed at
`48452bf2c8fa91a4a2c5dafce25cd78dcb844ccb`: 315 compatibility tests passed /
3 Windows symlink-permission skips; independent re-review approved. Fresh
protection confirms 22,939 unchanged originals and 27,070 private files ignored.
Task 4 manual multiclass annotation is verified and locally committed at
`d70c0afe1b364484b4eb877ab6c2f7de48a07c5c`: 83 new/inherited GUI tests pass,
zero skips/errors; independent frozen review approved the repaired state/input
guards. Protection confirms 22,939 unchanged originals, 27,112 private files
ignored and legacy unchanged. Task 5 checked export/separate CLI is verified and
locally committed at `377831aedde90db23879911535f7391f2f505b42`: 115 new/inherited
CLI tests pass, zero failures/errors/skips, original protection passes and frozen
code reviews approved. Only an EOF blank-line cleanup followed that focused run;
the final combined maintained suite passes on the committed clean snapshot.
Task 6 new ignored handoff retains four original-order recordings, 75 reused
frames, two historical Minions groups and eight individual boxes all pending.
Checked binding covers 302 references; zero multiclass candidates qualify.
Actual `validate-dataset` and `scale-report` return native exit 3: valid but
PROVENANCE_INSUFFICIENT / SIZE_COVERAGE_INSUFFICIENT with owner/data reasons.
The six new handoff files stayed unchanged across both read-only commands.
No real Scale Snapshot/Dataset Lock/export is attempted on this insufficient
data. Final protection passes: **22,939 original files unchanged, 28,450 current
private files Git-ignored**, legacy source/tests/config unchanged; source videos,
old 2A2 lock and 2B-1 FAIL remain protected. Fresh pip passes. Record the local
report checkpoint and stop; no push, merge or Phase B.
Fresh baseline: 680 passed / two known Windows symlink-permission skips, exit 0;
pip check passed. All 22,939 pre-existing files under outputs/local_data have a
protected SHA-256 inventory; initial Git privacy check passed. These are baseline
checks, not proof that the new implementation is complete or data is ready.
See [Phase A verification](VERIFICATION_M2B2B.md) for task evidence as it becomes
verified. Phase B, torch/torchvision/YOLOX installation, weights, training, Model
Lock, blind-test work, Module 3 and Android/live functions remain prohibited.

## Inherited accepted 2B-2A design and planning checkpoint

On 2026-10-05 the user paused the ordinary-Minions 4-match / 8-deployment
specialist data route. The product targets multiple visual types dynamically
present in each match; Minions is historical evidence and one future class, not
the fixed standard. Preserve the existing contracts, annotation/lock tools,
private pending data, 2A2 Development Lock and accepted 2B-1 FAIL without edits.

Historical design branch: `codex/module-2b2a-taxonomy-audit`, from the local data-preparation
checkpoint `f0b424a0aa78079840ecc665e362023ee81042ce`. The old local feature branch
is retained. Accepted main remains `8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.
No push/main integration is authorized.

The user reports ChatGPT independent design acceptance of review commit
`cec8abc35fce2438d149fe4b68b203650cb835e4` on 2026-10-05:
`MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT`. This is the supplied acceptance
instruction, not a new ChatGPT retrieval or independent rerun in this session.
Taxonomy/provenance/observation-event-card separation, unknown handling, match
splits, model comparison and the PoC protocol are retained. Public game assets
stay reference_only; Nano/Tiny/Faster are unqualified candidates, not a locked model.

Scale Coverage Gate is now a design requirement: freeze the policy and all
basically eligible mobile candidates' Development-only size statistics before
class selection. The 3-5 classes must include one relative-small mobile class
and one medium/large mobile class. Original bbox width/height/short-side pixels
and normalized-area distributions, grouped class scores and cutpoints must be
reported; ties cannot be split by card name. Missing support produces
SIZE_COVERAGE_INSUFFICIENT and requires original-order Development material,
not a lower standard or fixed-Minions expansion. Its new pure validator is
implemented; real data qualification and checked freeze remain pending.

See [research and primary sources](research/2026-10-05-multiclass-dataset-taxonomy-audit.md)
and [accepted amended design](superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md).
The 2B-2A design stage is closed with this amendment; no recognition success is claimed.
The independently reviewed and now Phase-A-approved
[Module 2B-2B implementation plan](superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md).
It separates Phase A schema/readiness/data preparation and immutable dataset
freeze from separately authorized Phase B model-environment qualification.
At that design checkpoint Phase A was authorized and Phase B had not begun.
The separately completed Phase B and current smoke lock scope are recorded above.
The preceding documentation-only stage did not prepare data, install models,
download weights, train, infer or create Model Locks/Android/live functionality.
The historical Minions readiness checks still exist unchanged; do not use them
as the new multiclass gate or bypass them by editing old locks.

Historical research-stage checks at cec8abc: all six changed files are Markdown; no source/test/
configuration/private-data diff. Local documentation links checked (44, none
broken); pip check exit 0, no broken requirements; diff check passed. Read-only
before/after SHA-256 inventories agree for all 22,243 existing files in outputs/
and local_data/; all 22,243 remain ignored, zero private/media/weight files tracked.
Local main, origin/main and a read-only remote-main query all retain the accepted
baseline above. Full pytest was Not Run in this documentation-only stage; the
680/2 result below belongs to the preceding implementation checkpoint. Model/GPU/
mobile evaluation is Not Run. Fresh amendment/plan checks and their exact scope
are in [design closeout verification](VERIFICATION_M2B2A.md); historical results
are not presented as fresh runs. Local commit/status are reported from Git at
handoff, not fabricated as a self-referential SHA in this file.

## Paused Module 2B-2 data preparation — inherited checkpoint

The earlier approved data-preparation design/plan is retained as history.
It is not the current continuation instruction. Its local branch is
`codex/module-2b2-data-preparation`; no Training Dataset Lock was reached.

- Tasks 1/2: closed multi-match individual-unit schema, independent readiness,
  grouped LOMO ownership, checked media/label binding and exclusive dataset-lock
  APIs implemented and separately reviewed. Latest Task 2 regression: 583 passed,
  two Windows symlink-privilege skips; dependency/diff/protection checks passed.
- Task 3: additive manual unit annotation tool verified, with runtime limitations. A full run
  exposed an intermittent native Tk initialization error (629 passed, two skips,
  one error). Its cause is unknown, not hidden by a skip or claimed repaired.
  Fresh-process real-GUI scenarios now retain errors and original assertions;
  focused tests: 52 passed, no skips. Full regression: 635 passed / two Windows
  symlink skips, no GUI skips/errors. Protection passed. Separate review found a
  forward-only navigation bug: invalid review could advance and strand saves.
  Minimal fix at `6f34af3` passes 55 focused and 638 full tests / two permission
  skips; scoped re-review approved and all protected files unchanged.
- Task 4a: checked CLI committed at `a62bb72`, 34 focused tests passed; independent
  review approved. Task 4b started, but initial binding rejected a legal rounded
  final-frame timestamp before any real draft write. Same-cause new-layer repair
  at `192d6ec` passes covering tests and 431 targeted regressions / two permission
  skips; independent repair review approved. Old evidence is not changed.
- Task 4b: all four sources fully decoded technically in original order. Actual
  checked pending drafts are additive; latest CLI validation exits 3 (valid, not
  ready). Eight first-source original representative frames are reused; 64 new
  two-second locator frames for source 2 remain pending. No automatic GT/boxes.
  Historical target confirmation: one match/two ordinary Minions deployments.
  New training eligibility: zero matches/zero plays, because individual-unit
  frames have not been exhaustively human-reviewed. Total pending frames 72,
  unit boxes zero, unknown intervals six, certified absent duration zero.
- Historical bounded recount resolves the earlier stopping point: source 2 is
  **excluded for mid-match truncation** after explicit user confirmation that
  no later clip exists. Earlier attestation and original files are preserved;
  no result-screen rule is introduced. Source 3/4 sampled target review is
  completed in original order with zero newly confirmed ordinary deployments,
  not proof of absence or exhaustive GT. Both stay pending for native training
  qualification, never Negative. That specialist route produced no Training
  Dataset Lock; its outputs are superseded / historical.
- Stage-end maintained regression: 680 passed / two known Windows symlink
  permission skips in 391.67s, exit 0; no GUI skips/errors. Fresh pip check exit 0,
  no broken requirements. Detailed verification and remaining limitations are in
  the stage verification document, not an assertion of dataset readiness.
  Stage-end protection: all 16,745 originals unchanged; 22,239 private files
  ignored, none tracked; baseline sources/tests/config unchanged; diff check 0.

The old implemented contract requires >=4 independent target-positive natural
matches AND >=8 confirmed opponent minions/normal deployments with reviewed unit
evidence. This is historical code behavior, not a continuing product data goal.
Unknown/other-form content is not negative; sparse negative frames never certify
FP/min time. Preserve the old Development Lock and accepted 2B-1 FAIL byte-for-byte.
See [data verification](VERIFICATION_M2B2_DATA.md),
[unit dataset contract](MODULE_2B2_DATASET_CONTRACT.md), and the approved
[plan](superpowers/plans/2026-10-05-module-2b2-data-preparation.md).
Those unfinished reviews and the former completeness conflict remain recorded;
the current smoke task does not continue them or ask for more Minions recordings. No claim
is made that remaining sources lack targets. The new schema/PoC design is accepted;
its Phase A implementation and later qualification retain their separate evidence above.

## Accepted Module 2B-1 baseline — historical closeout

On 2026-10-05 the user reports formal ChatGPT independent acceptance at
`585c3d95c832a1a86fce28ca822bc69d3646430f`, with
`MODULE_2B1_INSUFFICIENT_ACCEPTED`. This records the user's acceptance instruction;
the closeout session did not retrieve a new ChatGPT verdict or re-review private
footage. The accepted conclusion is an insufficient fixed lightweight template
baseline, not successful recognition or cross-match reliability.
Real result remains 2B1_BASELINE_INSUFFICIENT: both folds fail the fixed Top5/2s
gate. A-to-B has no retained candidate; B-to-A retains one whose first support
is 4.75s late. No Model Lock/final baseline was built and no tuning/rerun followed.
The accepted minions/normal Development Lock and original failed evidence remain
unchanged. That closeout covered four-document acceptance recording, fresh full
regression/dependency/diff/privacy/protection checks, a documentation commit and
ff-only main publication, retaining `feat/module-2b1-minions-visual-baseline`.
Fresh maintained-suite regression: 474 passed/1 skipped in 55.48s; pip check passed.
Diff/privacy/ignore checks passed. All 10231 originally protected files plus 145
saved experiment/Review Packet files (10376 total) remain byte-identical; original
fold results and protocol bindings are unchanged. No source/test/config change.
The following 2A2 history describes its acceptance boundary, not a veto of the
new scoped data-preparation authorization. At that closeout, independent testing,
2B-2, Module 3, Android and live functionality were unapproved. Its ff-only main
integration and push authorization applied only to that historical closeout;
the paused 2B-2 slice and current design closeout/planning authorize neither publication nor training.
See [fixed 2B-1 protocol](MODULE_2B1_PROTOCOL.md).

## Current stage

- Module 1: completed, accepted and integrated into main.
- Module 2A1: formally accepted at
  `98037ceba81683ad1a2c214bada30a10f2f3f69e`; acceptance and ff-only main
  integration published at `3ad657f2c9190f4e389ccd035682becd12d0c51c`.
- Module 2A2 Independent Evidence & Experiment Lock: separately authorized
  2026-10-04; infrastructure implemented and verified on its feature branch.
  Formally user accepted on 2026-10-04 at
  `69162023b87b71209f8dec9ebc9af69d4bfda944`, after the independent-review
  completion-boundary repair. First-source real evidence/lock remains DEV_LOCKED.
  That acceptance instruction authorized documentation, ff-only main
  integration and publication, not Module 2B. Formal acceptance is recorded from
  that user instruction; this session did not retrieve another ChatGPT response.
- Historical 2A2 experiment: the user attested all four natural replay recordings
  cover full matches and explicitly superseded the result-screen completeness gate.
  Source 2's conflicting completeness is now resolved as mid-match truncation
  with no later clip; it is excluded from training use. The old attestation is
  preserved historically, not new proof. Use
  user_confirmed completion provenance and the actual file-end boundary; absence
  of victory/defeat UI is not incompleteness. The first original-order input was
  completed using its existing rough review. The user corrected two deployments to
  normal Minions (three units), not Minion Horde. Target minions/normal is frozen
  with two independent verified plays and six original key-frame boxes.
  All sources, prior exclusions and first survey/rough review are retained.
  One actual exclusive version-one Development Data Lock exists locally;
  readiness/freeze/lock validation exit 0 and digest reload/recomputation agree.
- The 2B-1 acceptance did not itself open another module. The former Minions-only
  2B-2 preparation route remains paused. Its later design-closeout-only boundary
  is historical, superseded by the explicit multiclass Phase A Tasks 1–6
  authorization above. The historical Task 2 regression stop was superseded by
  the user's stable continuation: Tasks 2 and 3 are now locally committed;
  Tasks 4/5 are committed; Task 6 read-only checks show insufficient data,
  and the final combined maintained regression passes (908/3).
  Independent blind testing, training, Module 3, Android, HUD and realtime
  remain closed.
- Module 2B-1: formally accepted as insufficient at `585c3d9...`; the fixed
  experiment and review are complete, but neither fold passed. Acceptance of a
  failed feasibility result does not open Model Lock or the next module.
- Completed two-class data-lock step: explicit private local research PoC training-use
  authorization for the frozen 11-box GT; separate Training Dataset Lock is
  exclusively created, dedicated readiness/readback exit 0 and internal
  `training_qualified=true`. Fresh joint private tests pass 65/0 skips and the
  full maintained regression passes 908/3 existing permission skips, exit 0.
  That step performed no real training or weights download. The new Phase C
  authorization led to the completed Attempt01 training chain, independently
  accepted as valid but insufficient. Attempt02 also completed and is now
  accepted as valid but data limited, based on statistics rather than completed
  independent image/code review. Fine-tuning is paused; the active bounded
  existing-detector benchmark execution/visual-review boundary is recorded at the top.
  Historical 4/8 and original 3–5-class readiness results
  are retained in their original scopes, not applied to this smoke snapshot.

## Inherited verified capabilities

Module 1 reads local MP4 metadata and exports original PNGs using actual
PTS/time_base relative to the first displayed frame, inclusive 100ms tolerance.
It preserves sources/outputs and reports success/miss/error. The accepted user
recording was decoded and checked; not a guarantee for all phone formats.

Module 2A1 prepare/validate/review retain strict v1 evidence, report/index pairing
before frame merging, PNG metadata/content checks, manual onset/visibility and
3-5 original key-frame boxes per verified play. Its review still always sets
experiment_gate=false. Its four-play candidate rule is historical behavior,
not the new 2A2 development threshold.

Fresh pre-2A2 baseline: 223 passed, one Windows symlink permission skip; pip check
passed. Real Windows junction tests run. Private evidence revalidated: four
reports, 533 requests, 402 unique successful frames; validate 0 / review 3; four
plays, 12 boxes, eight gaps; candidate true, experiment false, insufficient.
All 591 explicit existing files, including source MP4, matched their earlier hashes.
No extraction/playback/label change; only a new ignored machine review report.

## Module 2A2 implementation

Separate development contract/readiness, immutable SHA-256/versioned lock chain,
future Model/Test GT contracts and private experiment CLI are implemented.
TDD fixes and scoped re-review closed contradictory evolved equipment and weak
snapshot types. Task 1/2/3 reviews passed. Final whole-branch review identified
cross/incomplete-segment accumulation; the new adapter now requires exactly one
complete shared match segment. Scoped re-review confirmed the finding addressed,
with no new Critical/Important issue or out-of-scope observation.
Fresh acceptance-integration full suite: 406 passed, one known Windows
symlink permission skip; pip check passed. Earlier compile check and no-index
wheel build passed; those build checks were not rerun this session. Dependencies
and all existing Module 1/2A1 production/tests are unchanged. Full evidence and
limits are recorded in [2A2 verification](VERIFICATION_M2A2.md).

Approved rules: one NEW natural complete unedited development replay, full human
review, manual target selection from actual opponent cards, >=2 clear independent
deployments of a single known normal/evolved form. Unknown/other forms and gaps
are not negatives. Evolution is manual ground truth or unknown, never estimated.
No eligible target means NOT_READY, not a lowered threshold.

Flow: Development Lock -> separately approved 2B -> Model Lock before test pixels/
precise GT -> first qualifying independent natural test replay (>=1 locked-form
play) -> new annotation session -> Test GT Lock before any inference.
Underlying match, not recording filename/hash, is the split identity.
Historical Inferno Dragon evidence is regression-only, not the first new target.

## Historical recording intake and accepted 2A2 boundary

- User confirms four distinct new natural whole-match replays, normal speed,
  unedited, not the historical Inferno Dragon match; the current statement resolves
  the old missing-result gate by a new definition, not by rewriting past images.
- Complete replay now means user confirms full-match coverage; last actual decoded
  frame is the evaluable end. Record completion_attestation=user_confirmed and
  terminal_result_screen_present independently. Missing result UI alone never
  blocks freeze. Technical corruption/undecodability, obvious mid-match truncation,
  missing key battle content or explicit human incompleteness still reject.
- For user_confirmed development drafts, every candidate's unique shared complete
  segment must start at relative zero and end exactly at recording.last_frame_seconds.
  Unknown prefix/suffix labels cannot excuse a shortened segment. New readiness,
  construction and loaded-lock validation enforce this without changing legacy v1.
  Existing real version-one lock already satisfies both boundaries; it revalidates
  unchanged and no new freeze version was needed. All 901 protected existing files,
  including that lock and the source recordings, retain their pre-repair hashes.
- Original intake array remains fixed. Source one is the first usable continuation;
  no re-sorting or card/difficulty/quality-based source selection. Byte hashes do
  not prove match independence. All four have had prior boundary pixel exposure;
  none is selected or qualified for prospective independent blind testing.
- Existing first prepare/report/index remains valid: 37 successful unique frames
  and four contact pages. Its actual measured last frame supplies the endpoint;
  no ending UI is fabricated, no original survey/rough-review file overwritten.
- User already watched the first file in full, own-bottom view, with five card/form
  entries and 12 approximate independent deployments. The list is not exhaustive;
  one form and dense combat remain unknown. These times locate precision work,
  not verified onset intervals, exact boxes or automatically negative coverage.
- Historical first/second incomplete classifications and third/fourth result-boundary
  failures are superseded solely as result-screen requirements. Existing factual
  technical/image observations and all old private sidecars remain untouched.
- Fresh pre-change protection: all 96 current-recording files and 591 historical
  2A1 files checked, 687 distinct protected files unchanged. First report/index
  loaded again; supplements/attestation/drafts use new ignored paths only.
- First-source precise review: seven report/index pairs, 191 raw requests and
  188 unique successful frames. These include the reused 37-frame survey and
  154 new locator/identity/visibility/key requests; three overlapping requests
  merge after strict request/content checks, not before. No old export regenerated
  or replaced. Other original-order sources were not re-inspected for target quality.
- User explicitly confirms both corrected ordinary Minions deployments after a
  targeted original-image question. Four actual candidate bundles retain Cannon,
  Flying Machine and Witch as unknown form/unqualified; original misidentified
  Horde/Cart/Golden Knight hypotheses remain in local history and frozen rationale.
  Only selected Minions qualifies: two clear independent verified plays, six boxes.
- Capture segment covers the whole evaluable file from first actual PTS through
  last actual PTS, including opening UI as unknown, not a cut battle prefix or
  negative. Positive visibility uses conservative reviewed windows, not exact
  death/full-lifetime claims. Three explicit unknown intervals and six recomputed
  per-candidate gaps remain; zero verified negatives. All evolution progress unknown.
- Actual CLI for all four candidate bundles: validate 0, review 3; v1 candidate
  and experiment gates false / status insufficient. Separate 2A2 readiness 0
  gives DEV_VALIDATED, freeze 0 gives DEV_LOCKED, validate-lock 0; canonical digest
  recomputation and repeated reload match. Old 2A1 candidate remains true and its
  533 requests/402 frames/four plays/12 boxes/eight gaps remain unchanged.

## Limits and unchanged gates

- Match identity, natural provenance, complete viewing, first qualifying test and
  non-exposure to predictions remain human attestations, not software proof.
- Digest/schema consistency is not source authenticity, tamper-proof storage or
  OS isolation. Stored metadata can be checked without decoding; disk freeze
  must still load and verify explicitly supplied reports/indexes/PNGs.
- Historical eight unknown intervals are not negative labels. One match proves
  neither detector accuracy nor cross-match generalization or live safety.
- Nested old advisory gap validation remains 2A1 debt; new bundles are closed and
  recompute gaps. No unrelated old-module patch is authorized.
- Duplicate frame/bbox annotations within one GT play under different IDs remain
  a deferred minor limitation; future metrics must reject/deduplicate them.
  No current GT box-count threshold or metric relies on this annotation count.
- Candidate capability values use a manually checked current public catalog;
  absence-based capability is an inference, not an authenticated complete rules
  registry or future guarantee. Equipment, charge, rules and progression remain
  unknown/null. Freeze correction must create a new version, never edit the lock.
- Six selected boxes describe the three-unit deployment group, not single-unit
  tracking; split-lane group rectangles include intervening space. This is a
  disclosed PoC data-design limitation, not recognition accuracy.
- The 2B-1 adapter loads both development occurrences and reference crops before
  scanning. Each scan/rank uses only its active reference and fixed settings;
  hidden scoring follows both ranking writes. This is function-input separation,
  not delayed hidden-metadata loading or OS/session isolation. The Review Packet
  disclosed the stronger historical protocol wording; no protocol/code rewrite
  or new experiment is part of accepting this insufficient result.
- Module 2A2 itself made no dependency/database/cloud/model/runtime networking/
  Android/game-input change. The separate 2B-1 adds only optional pinned OpenCV/
  NumPy and development scanning; no database, cloud, neural model or game input.
  No automatic selection, evolution, cycle or elixir. Model runtime and project
  license remain undecided.
- Live analysis/HUD require applicable explicit Supercell permission and separate
  approval. Passive capture/risk acceptance cannot substitute. Never promise
  zero ban risk.

## Historical 2B-1 Git and accepted stopping point

Pre-2B-1 accepted main baseline: `48136affd470a39feb9815f19e1dbd207ffc14ca`.
Frozen experiment code: `41d30c6893376b811c98d72442edfd52222f0733`.
Independently accepted review checkpoint: `585c3d95c832a1a86fce28ca822bc69d3646430f`.
The documentation-only closing commit on `feat/module-2b1-minions-visual-baseline`
is the publication checkpoint; exact commit and remote publication state are
verified from Git refs and the local closeout receipts, not a self-referential
SHA in this file. That main integration was ff-only. The feature branch, accepted
2A1/2A2 branches and every private evidence file were retained; no PR, Release,
force push, rebase, history rewrite or branch deletion was part of that closeout.
These historical instructions do not authorize current 2B-2 main integration.

That closeout stopped after acceptance publication. The later specialist 2B-2
data-only authorization remains paused; its route is historical and superseded
by the preserved two-class smoke experiments and the current separately
authorized existing-detector benchmark above;
do not automatically tune or train. Module 2A2 remains
accepted at
DEV_LOCKED. Both folds failed, so Model Lock stays closed. No new source, Test GT Lock,
independent test or later module begins without separate authorization.
Preserve every source, old rough
review, prior exclusion and new lock; corrections use another freeze version.
Do not turn full-match attestation or uncovered visibility into negative labels.

See [2A2 verification](VERIFICATION_M2A2.md),
[2B-1 verification](VERIFICATION_M2B1.md),
[blind protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md),
[contracts](MODULE_2A2_CONTRACTS.md), [roadmap](DEVELOPMENT_PLAN.md),
[historical 2A1 verification](VERIFICATION_M2A1.md).
