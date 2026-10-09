# Module3C5 — BBox Review Decision Backfill

## Goal and verified delta

Record the explicit user-attested treatment of9 review candidates from unchanged
8-frame review material; check existing03/04 for independent Royal Hogs support.
Baseline:`e65ae2833e3f2c3fba6af6f7b608b67c1841f69a`.
Branch:`codex/module3c5-detector-improvement-a`. This task completes decision
backfill, NOT detector improvement or training readiness.

Reviewer=`user`, review_basis=`chatgpt_visual_review`, confirmation_source=
`user_attestation_based_on_chatgpt_visual_review`; actual_human_confirmation and
human_review_attested=true only for these decisions. ChatGPT is not human reviewer.
The attestation does not confirm boxes, physical identity or exhaustive coverage.

## Explicit-ID decisions, not merges

| Candidate | Possible prior GT reference | Treatment |
|---|---|---|
|O009|p-a2c55c9c1fd52be6484a3cd4|duplicate_review_candidate|
|O010|p-a0c94beb3d1d87bb16853eee|duplicate_review_candidate|
|O012|p-544fbf9edae49bed29e57f0d|duplicate_review_candidate|
|O017|p-bf28c4a6445f0d9139a9b534|duplicate_review_candidate; owner unknown|
|O019|p-251bcbd6bd3a0e93690b0589|duplicate_review_candidate|
|O020|p-7b7603db9add35949ce1c3ba|duplicate_review_candidate|

All six links resolve exactly to existing accepted references in the same source
frame, match, class and time. Descriptive IoU/coordinates are preserved privately,
without a merge threshold; overlap/review does not independently establish the
same physical object. Associations stay tentative, merged_into=null, no added GT.

- O011:possible fourth Royal Hog; precise bbox and independent-object check needed.
- O018:crowded/occluded; class, owner, identity and bbox unconfirmed. Owner unknown.
- O021:possible third-Minions duplicate, clock obstruction; dedupe/box review needed.

All9 boxes remain unverified, full-object confirmation=false. No irreversible
merge, no coordinate correction guessed, no source label upgraded.19 prior
accepted references remain untouched.16 class-region rows (8 frames x2 targets)
remain pending and nonnegative. New training-qualified boxes0, Negative0,
new confirmed bbox0, new card-play GT0; no selected-class exhaustive claim.
Historical Minion-only coverage is retained but cannot become joint coverage.

## Independent Royal Hogs source check

Inspected in original match order using existing source contact sheets:

| Match | Existing samples | Sheets | File-end boundary |
|---|---:|---:|---:|
|natural_match_03|159|18|285.2916666666667s|
|natural_match_04|107|12|202.41666666666666s|

All30 sheets/266 samples were viewed, not merely metadata searched. Combat is
present; the old matchmaking-only03 prefix is not substituted for validation.
No clearly identifiable independent Royal Hogs cohort was located at sheet scale.
Other armored/upright units, purple large units, drill contexts, large green
humanoids, flying/wheeled entities are not silently labeled Royal Hogs. Crowded
or small ambiguous details stay unknown; no training GT is created by this audit.

These are samples, not a new full-video human review:whole-video target absence
is unknown. A visually similar unit is not a target deployment; adjacent frames
and different members cannot inflate deployment-source counts. Extra confirmed
Royal source0:known support is still one deployment source in match01. No
cross-match/previously-unseen/blind claim;03/04 have prior development exposure.
Match02 remains mid-match truncated/excluded and is neither deleted nor Negative.

## Private outputs and immutable bindings

New exclusive directory:`outputs/module3c5/decision-backfill-v1/`.
Primary:`bbox-review-decisions.v1.json`.
Byte SHA-256:`23b816f67b277f49a55b07320290ce6101c79a482282edff5b035ff6971c3742`.

It includes9 explicit-ID decisions with original/proposed fields,6 links and
descriptive geometry,19 exact old-reference rows,16 pending coverage rows,
source-audit provenance and training blockers. CSVs, source-check JSON,
manifest and readback/protection receipts stay private/Git ignored. It is a
decision-only record, not a production Schema change, GT Lock or Dataset Lock.
Do not feed it through the complete-object GT importer.

Original review ZIP SHA remains:
`f785a7b1000beb42ef359835d5bc8dad392f980b6edf789a0278ca3a7600232a`.
Field Snapshot SHA remains:
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.
Old visual GT/Event GT/locks, source recordings/images, proposals, Attempt01/02,
Oracle FAIL/PASS and3C experiment results are preserved, not rewritten.

## Fresh checks and explicit omissions

```text
.venv/Scripts/python.exe -m pytest tools/preannotation/tests -q --tb=short
51 passed in43.11s; exit0
.venv/Scripts/python.exe -m pytest tools/event_engine/tests -q --tb=short
84 passed in21.88s; exit0
```

135 scoped tests passed, zero skips. Two new JUnit files retain full results.
Offline and existing YOLOX pip check both exit0/No broken requirements; no install.
Existing actual first/second human-return CLI validates exit0 at44/39 accepted
boxes with training_qualified=false. Private decision readback rejects15 mutated
copies covering false reviewer/attestation, bbox/full-object/identity/training
promotion, merge/link/ID/coordinate drift, exhaustive and Negative promotion.
No original evidence was altered for tests. Manifest/source-binding/protection,
privacy/ignore, local document links and Git difference checks accompany receipts.
Fresh readback validates3904 protected pre-existing material hashes and225
unchanged tracked files (only the two current status/plan documents are allowed
to differ). The original ZIP, both multiclass locks,49-box Field Snapshot and
Event GT remain intact. All new review records/helpers/images remain ignored;
no private media, labels, locks or weights are tracked. Read-only peer review
also verifies the9 exact bindings,19 reference projections and16 coverage rows.

Full maintained suite/model/training/inference/metrics/Android/JS build:Not Run;
decision-only task, production code/tests/environments unchanged. No retraining,
GT/box extraction, new weights or split/data lock. GPU evidence is historical,
not requalified. No benchmark or after-engine metrics were rerun.

## Changes and next action

Public changes only:CURRENT_STATE, DEVELOPMENT_PLAN and this checkpoint.
No SQLite/migration/storage/Schema, engine/scorer/rules or Android modification.
Local Conventional Commit only; no push or merge; main stays published3D.

Data admission is still Blocked:finish pixel/identity and16 class coverage
reviews, confirm a real independent Royal Hogs source with original context,
then qualify/freeze target data use and source-isolated TRAIN/DEV/RETAINED_EVAL.
Minimum new natural material only if existing context cannot establish support;
no fabricated source or restored4-match/8-deployment quota. No automatic training
or further event-rule experiment follows this handoff.
