# Three target cards — Source rescreen and human-review preparation

## Goal / scope

User-fixed Hog Rider, Goblin Barrel, Firecracker discovery from same05..08 natural
recordings. Baseline `fef67ad650b073bda379a6abb6218bc32c38d582`, branch
`codex/module3c-target-card-discovery`. Private artifact preparation plus four
public memory documents only. No production/test/schema/database/Android edits.
Old GT/field reviews/Attempt01/02/KataCR benchmark/Oracle and failed experiments
are retained; their old target-specific gaps are not current collection gates.

## Fresh source and proposal evidence

Same intake identities/order and source SHAs as previous3C6 checkpoint. Each source
hash verified; full SDR/rotation/geometry/corruption/PTS checks to EOF repeated in
existing offline environment:2522/2919/2361/1511 frames, total9,313. User-complete
attestation/boundary checks inherited unchanged; byte/decode consistency is not
forensic no-edit authentication. No source modification or new recording.

Fixed BEFORE inference: whole-file2FPS, same KataCR v0.7.13 dual weights/pinned
code36ceb9fc..., replay ROI `[24,534,1176,2309]`,576x896 CUBIC canvas,imgsz896,
batch1 FP32 CUDA0,conf0.1,NMS0.7/combined0.6/max300/inherited UI filter.
2% horizontal crop can miss edges; full-width review pixels allow missing-box
addition. No model downloads/training, dataset use, threshold tuning or GT inputs.
Existing MIT-root/modified-YOLO AGPL/unverified game-weight rights caveats remain;
private proposals only, not redistribution or APK assets.

|Match|Whole-file sampled scenes|Mean dual-model inference(ms)|Scan wall(s)|
|---|---:|---:|---:|
|05|208|331.40 including warm-up|108.34|
|06|241|299.57|118.14|
|07|195|301.95|99.45|
|08|125|303.39|64.27|

769 scenes, all35 survey pages actually visually inspected by parallel analysts;
native representative/context frames also viewed. This is sampled pixel survey,
not a full continuous human replay or complete presence/absence inventory.
GTX1050Ti CUDA actually used; peak allocated approx554MiB warm-up/488MiB later.
Each process denied3 library outbound attempts; no successful outbound call,
not an OS sandbox guarantee. Scan/config/source fingerprints retained privately.

Initial v1 scan failed at first frame before inference/images because model-env
PyAV14.2 lacks `VideoFrame.color_trc`, required by offline tool. Preserved failure.
No installation/upgrade: fresh full-video validation in existing PyAV19.0.1 env,
source SHA binding, then existing model env checks corruption/PTS/geometry on
identical verified source bytes. Compatibility wrapper only; same inference
configuration/weights and formal extractor. Successful v2 is not a tuned rerun.

211 additional source-only6FPS context frames, no extra detector pass:06 barrel
22.5–26.5;07 flights4.5–8.5/28.5–32.5/44.5–48.5/86.5–90.5;08 ambiguous
target44–52 and barrel-confound32–38. First frame at/after request within100ms.
Full native PNG/report/index and full context sheets retained privately.

## Discovery versus card play

Actual observation class/owner/form/origin/identity/source_card unknown/null;
raw teacher class/owner/confidence stays separate. No full-object Human GT or
verified bbox, no exact deployment time or independent-event count.

-05: no target pixel-supported window found in sampled survey. High teacher
  Hog/Barrel guesses map to humanoids, bridge/flame or empty floor. Unknown
  presence, never whole-video Negative.
-06: six Firecracker birth/appearance contexts near21.507,43.035,
  57.510→58.008,83.527→84.020,93.540,106.500. Bomber17/51 and golden-armored
  sword76 are separate confounds. Red markers/clocks support hypotheses only;
  do not equate six locators with six confirmed independent plays.
-06: five airborne cylinder-flight locators22.5–26.5/45.5–49/69.5–73/
  89.5–93/96–100. Projectile route/arrival and Goblin-source relationship require
  human context confirmation. Standalone Goblins cannot infer a barrel.
-07: five separated airborne barrel windows near6/30/46/73.5/88. Four6FPS
  contexts show upper/redking→lower/bluelefttower flight, distinct from separate
  ground Log and vertical rectangular delivery. Three show red Goblin successors,
  late88 interception obscures successors. These support opponent/card hypotheses,
  not Human GT. Earliest sampled visibility brackets are not actual throw time.
-08: Firecracker presence26–34; Hog-labeled44–52 ambiguous bulky humanoid versus
  pig/rider;34s barrel tag confounded by tower/crown effects. No confirmed Hog
  training source; visual presence conflict has no admitted CardPlayCandidate.

Six previous Firecracker object IDs C6O012/016/018/021/023/055 and six locator
IDs C6D038..042/083 reused as pending references with source hashes. Audit found
no newly attested Witch/Firecracker backfill, so no confirmation fabricated or
rollback performed. All prior evidence stays unchanged.

`VisualObservation.proposals` and `CardPlayCandidate.pending` are independent
discovery artifacts, not event-engine input. Sixteen CardPlayCandidate hypotheses
contain flight/birth evidence and source links; no timestamp correction, emitted
OpponentCardPlayed, confirmed card-play or independence. Appearance/track/group
identity still unconfirmed. Human review can accept/reject/correct/merge/mark
unknown/add missing boxes and review class-specific coverage separately.

## Lightweight review package

`outputs/module3c-target-discovery/v2/Module_3C_Target_Card_Discovery_Human_Review_Lite_v2.zip`
19,135,637 bytes (<20,000,000); SHA-256
`cb775b3dee81d665baf4637cdaa0455d8a7aed9e6b83e3f3478e327b55ddc92d`.

21 native arena original/annotated JPG pairs (3/9/5/4 per match),36 pending teacher
boxes,63 pending class-coverage rows;7 paired contact sheets,19 sequence sheets,
24 dense context sheets/211 source samples;candidate/observation/source tables,
object/event/correction/missing-box forms, unknowns and six previous references.
No raw video or weights; all private/ignored, no automatic upload.

Crop `[0,534,1200,2309]`; original pairs remain1200x1775; bbox stays full-source
1200x2670. Subtract534 from y for display only; exterior unknown/unreviewed,
never Negative. JPEG displays are lossy, not approved pixel-precise labels.
Initial presentation ZIP23,435,433 bytes exceeded20MB; it remains unchanged.
Lite-v2 byte-preserves65 members including all native pairs/data;43 sequence/
dense contact JPGs re-encoded quality55 only, same dimensions/selection/boxes/
states. Native full context pictures remain available locally for close inspection.

05/06/07 discovery only;08 remains exposed retained evaluation with no training
or tuning, not strict blind. File-relative PTS is not game clock; replay x1/x2
varies. Source=user_recorded_gameplay; intended_use=private_local_discovery_and_review,
rights_clearance=unverified, training_qualified=false. Zero new GT, qualified
training boxes, Negative or OpponentCardPlayed. No inference-performance score.

## Verification / omissions

Fresh scoped regressions:preannotation51, event engine84, offline video CLI/
pipeline47 passed, total182 passed/0 skipped. Both existing offline and KataCR
environment dependency checks pass. Historical-material/source/model protection,
actual PTS/bbox/source/frame linkage, pending-state/Negative guards, packet
manifest/member SHA/CRC, native-pair preservation, Git ignore/private tracked
file and diff/link checks recorded privately. No human labels were created.
4,230 existing material hashes and226 existing non-memory tracked file hashes
unchanged; all4 new source MP4 hashes unchanged. These are protection counts,
not training-data counts.724 target/confound observation proposals from22,050
raw teacher boxes remain unconfirmed, not724 actual target objects or plays.

Full project suite, JS/Android build, strict detector/event scoring, model training
Not Run: public delta is documents only and pending pixels cannot be scoring GT.
Initial compatibility and oversized-presentation failures are disclosed above,
not hidden as successful checks. No failures repaired through evidence mutation.

## Handoff

Manual independent review of light ZIP: verify target identities, owner/form,
exact boxes/missing objects/coverage, then flight and new-versus-continuing
appearance before counting plays or approving data use. No claim cross-match
generalization; Hog development source remains unresolved. Local commit and stop;
no push/merge, training, official engine/App changes or real-game integration.
