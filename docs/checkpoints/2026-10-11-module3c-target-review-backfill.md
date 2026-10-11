# Module3C Target Card — Field review backfill and precise review handoff

## Goal and authorized boundary

Import user-attested ChatGPT suggestions by original object/match/frame identity,
freeze an independent partial-review Snapshot, then prepare only GB07-01 and
FC06 precise-review displays. Baseline `65004237885edf447ea185fd3c01ad7e7288af0a`,
branch `codex/module3c-target-card-discovery`. Public delta is four memory documents
only. No production code/tests/schema/database/engine/Android or dependency changes.
One-off conversion/display helpers, tests, sources, labels and outputs stay private
and Git ignored, following the previous partial-review workflow.

## Input integrity and confirmation

Suggestion archive has4 members,8,251 bytes, SHA-256
`cbfcede2e550fb06506c2dd183fd5b62a95c2bde2f28dee369409e7098a3b58e`.
Source lite-v2 archive SHA-256
`cb775b3dee81d665baf4637cdaa0455d8a7aed9e6b83e3f3478e327b55ddc92d`.
Both ZIPs pass CRC; source bundle manifest and source binding checks pass.
36 unique object rows exactly match
source ID/match/frame/PTS/time/bbox/teacherclass/teacherowner;16 candidate IDs,
matches/cards/windows exactly match original candidate records. No row-number
binding, missing/foreign/duplicate IDs or content corrections. Suggestion prose
is retained as data, not executed instructions.

Confirmation source: reviewer=`user`, review_basis=`chatgpt_visual_review`,
confirmation_source=`user_attestation_based_on_chatgpt_visual_review`;
actual_human_confirmation/human_review_attested true for the supported scope.
ChatGPT is not a human reviewer. Neither this import nor the internal Codex
read-only audit adds any new visual or pixel-level confirmation.

## Frozen partial result

Private immutable Snapshot:
`outputs/module3c-target-human-review/snapshot-v1/module3c.target_field_human_review_snapshot.v1.json`.
File SHA-256 `733aef78d771eb16a1c96f1977d5ddf34351df44ff9013185565e5471f06f7bd`.
Canonical semantic digest
`baf1b7ed1e2baccc77fdad7308dc9e0259bba88fe4ff4539db557e2c0f567248`.
File SHA hashes actual serialized bytes; digest excludes its own field.
Both archive content and reconstructed field-scoped semantics are checked at
validation; recomputing a digest cannot legitimise added GT/Negative/identity.
Directory/files are exclusive-created; existing versions cannot be overwritten.
Return ZIP bytes, source rows, suggestions, CSV views and receipt are preserved.

|Outcome|Count / scope|
|---|---|
|Firecracker visual_class+owner support|9 object references,06=8 and08=1|
|Airborne barrel visual_class support|6; actual card/owner/deployment unknown|
|Confirmed class/owner cells|15+9=24|
|Mapping-only rejection decisions|11, not full-object rejection or absence|
|Other objects|9 pending,TO031 unknown|
|Unverified bbox|36|
|Unknown actual visual_class / owner|21 /27|
|Unknown form/origin/physical identity|36 each|
|Pending card-play windows / coverage|16 /63|
|Complete-object GT / training boxes / Negative / new plays|0 /0 /0 /0|

TO005/TO019 teacher owner=own survives beside reviewed opponent. Six barrel
references are `visual.projectile.airborne_barrel`, not confirmed Goblin Barrel.
TO001/TO008 target mapping is unsupported; TO031 remains unknown, not another
confirmed mounted card. All16 windows are unconfirmed; no new event timestamps,
independent deployment counts, event-engine input or OpponentCardPlayed.
All21 source frames remain nonexhaustive; no class-specific Negative is created.

## Minimal precise review jobs

Private base: `outputs/module3c-target-human-review/precise-review-v1/`.

|Job|ZIP|Bytes|SHA-256|
|---|---|---:|---|
|GB07-01|`Module_3C_GB07_01_Precise_Human_Review_v1.zip`|14,916,834|`5f99e8d1111b135e98bd1c8b9acf11f262ed3953dd8991f819e76a46aed960e2`|
|FC06|`Module_3C_FC06_Precise_Human_Review_v1.zip`|12,835,749|`e9e174e7e3e755cffc7f87c240b24fa372e745a8518a91785f9752d1e8ff7b15`|

GB07-01:13 existing6FPS lossless source frames for5.5–7.5s request range,
actual5.523–7.500s;5 native examples at fixed indices0/3/6/9/12,22 ZIP members.
Contact sheet, native original/annotated JPG, lossless arena PNG, frame/object/
deployment/missing-box review tables and manifest. Flight/landing/small units are
reviewable pixels, not a confirmed card/owner/onset/source relationship.

FC06:8 observation references/8 frames,33 ZIP members. Source-only extraction
uses the unchanged Module1 extractor once with exact original PTS fractions;
all8 results have identical rawPTS/timebase/time and zero error. Original full
1200x2670 PNGs/report stay local, excluded from the lightweight ZIP. Native arena
JPG original/annotated pairs, lossless context crops,2 contact sheets and object/
coverage/missing-box/possible-continuity tables are included. TO016/TO017 potential
continuity is pending, no merge. Eight observations do not mean eight physical
units or independent plays.08/TO026 excluded;08 remains exposed retained evaluation,
not training/tuning or a strict blind source.

Coordinates: source1200x2670; arena ROI `[0,534,1200,2309]`, display1200x1775.
Arena x=source x, y=source y-534. Object crop offsets/bbox translations are explicit;
contact sheets are display-only, never bbox source coordinates. Native JPG quality95
is lossy, context crop PNG lossless. Original candidate boxes remain UNVERIFIED.
Each crop-sheet tile gives its actual display scale. Crop exterior, unresolved
targets, rejects and missing objects do not become Negative.

## Actual verification

Private converter tests:59 passed; display/export tests:23 passed, total82 passed
with no skips in the final combined run. Tests first reproduced missing-helper
failures and a nonfinite1e999 parse defect; final tests cover exact input IDs,
digest-preserving semantic tampering, deterministic ordering, exclusive versions,
non-promotion,08 exclusion, ROI/crop/PTS/frame identity and pending coverage.

Fresh preannotation51 passed and formal event engine84 passed. Offline-video full
suite passes908/3 existing Windows symlink-privilege skips, exit0, in1668.76s.
Together with82 private tests,1125 passed/3 skipped; all runs exit0. Actual command,
stdout and JUnit receipts are private under `verification-v1/`.
Offline environment pip check passes. No model installation, inference, training,
threshold tuning or environment modification. JS/Android build Not Run: unchanged.

Snapshot rebuilt/read back; archive/member hashes/CRC and byte identity checked.
FC8 exact source frames and lossless crops verified; GB13 original PNG identities
and5 lossless arena crops verified. Independent internal audit reconstructed all
native JPG/annotations in memory and matched ZIP bytes. Two contact sheets viewed
for legibility only, not for additional class/bbox GT confirmation.

Fresh protection readback passes:5,595 existing private files (including all4
source recordings and old locks/results) have identical before/after hashes.
All230 baseline tracked files are checked; only the three authorized existing
memory documents differ, with this one new checkpoint. No unapproved source/App/
engine modifications. All95 private files present at the final audit are Git ignored,
including the supplied return ZIP; no media/weights/data paths are tracked.
Main stays `602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`. Diff check passes.
All97 local document links resolve; diff/privacy and exact four-document scope
are checked before local commit. No push or merge is authorized.

## Limits and handoff

This is field-level review completion, not a training lock, detector score,
cross-match event validation or source authenticity certificate. Hog Rider has0
confirmed boxes. All36 exact boxes still need pixel review;16 independent plays
are unknown. All old locks/predictions/results,3B engine and Android remain intact.
Next only: independent human precise review of GB07-01 and FC06, then a separate
authorized return; do not auto-confirm, train, push/merge or enter another module.
