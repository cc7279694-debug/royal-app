# Module3C — Precise Visual Review Backfill & Data Finalization

Date:2026-10-11. Local baseline `6f282b4f45daf73f619cba7ec20c22202201a471`.
Branch:`codex/module3c-target-card-discovery`. No push/merge.

## Delivered and preserved

Only this user-authorized bounded review is executed. No detector run, video
decode/extraction, model training, Android update, formal3B engine modification,
scoring-window change or historical GT/lock rewrite.

New private immutable Snapshot v1:
`outputs/module3c-precise-review-finalization/snapshot-v1/module3c.precise_visual_review_snapshot.v1.json`.
File SHA-256 `7bc56a8feeb42552cf0c6736de631ea373ec10b6f877c2fcc767398abbc7bb53`.
Semantic digest `3e328cec6ca5e7f83873c3338bdfbe30e97ad186e0dc2f0d3399bcef762731a8`.

Prior target Snapshot SHA remains
`733aef78d771eb16a1c96f1977d5ddf34351df44ff9013185565e5471f06f7bd`.
Prior field-level Snapshot SHA remains
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.
No old object, prediction, frame, CSV, ZIP, lock or run result is overwritten.

## Attestation versus geometry

Reviewer=user; review_basis=chatgpt_visual_review; confirmation_source=
user_attestation_based_on_chatgpt_visual_review. ChatGPT is not a human reviewer.
User attestation covers visual conclusions only, expressly not eight pixel bboxes.
Codex draft geometry has independent author/status and cannot become Human GT.

| FC06 ref | Source time(s) | Geometric review, not Human pixel confirmation |
|---|---:|---|
|TO005|21.507|clock/glow/nearby tower; exact bounds pending|
|TO007|24.028|visible target; tighter source draft[253,1073,343,1170]|
|TO015|43.035|clock/edge/tower decorations; pending|
|TO016|58.008|clock; possible continuity with TO017, identity unknown|
|TO017|60.027|visible target; tighter source draft[390,909,481,1009]|
|TO018|84.020|clock/adjacent armored target/spell overlap; pending|
|TO019|93.540|clock/glow/tower; pending|
|TO020|106.500|clock/glow/tower decorations; pending|

All8 visual_class=`visual.unit.firecracker`, reviewed owner=opponent;
form/origin/physical_identity/independent_deployment/card-play time unknown.
TO005/TO019 original teacher owner=own remains intact. Eight distinct source
frame IDs contain no duplicate within this eight-ref review scope; this is not
an exhaustive claim about all detector proposals or other battlefield targets.
TO016/TO017 continuity_candidate=true is not a new-card-play confirmation.

## GB07-01

One `VisualFlightEpisode` binds13 original samples5.523–7.500s, raw PTS/1:90000
and original PNG hashes. Eight visible-silhouette bboxes are Codex drafts;
five unresolved frames have null draft bbox, not fabricated/interpolated boxes.
Null is not Negative or target-absence proof.

User-supported fields:airborne_barrel visual class, opponent trajectory evidence,
flight continuity/landing relation and Goblin Barrel hypothesis support.
card_hypothesis_status=visually_supported_not_confirmed_GT. Actual card/owner,
physical identity, exact impact/deployment onset remain unknown; form=unknown.
independent_card_play_GT=false; bbox_verified=false; no OpponentCardPlayed.
5.523s is the first bound observation, never a deployment timestamp.

Separate Codex timing drafts, not event GT:6.676 last independently delineable
barrel;6.841 ambiguous near tower;7.007 first clear local red-level small units.
These brackets describe sampled visibility, not exact impact or causal spawn.

## Minimal handoff and qualification

`outputs/module3c-precise-review-finalization/geometry-review-v1/` contains7 native
comparison PNGs,FC06 eight-row geometry CSV,GB thirteen-row flight CSV,source/crop/
panel coordinate manifest and human-review note. Original source is1200x2670;
arena ROI[0,534,1200,2309]. Small panels are unscaled source crops; source and
display coordinates are distinct. No re-export of all historical candidates.

New pixel-verified boxes, full-object GT, training-qualified boxes, exhaustive
coverage, Negative and confirmed card events all0. No Training Dataset Lock.
This does not invalidate previously qualified historical non-target datasets.

Existing01/04 still contain unconfirmed teacher locators; source04 sampled combat
does not establish a second confirmed Firecracker deployment or a Goblin Barrel
play. Source03 has no confirmed target record, not a proven absence. Source02
is truncated/excluded; source08 is exposed retained evaluation, never training,
tuning or blind. Multiple06 frames are not multiple independently confirmed
deployments;07 flight frames are one candidate Episode. Independent sources and
pixel/coverage qualification remain outstanding, without forcing training.

## Verification

New snapshot creation and separate rebuild validation both exit0. The private
validator binds the old Snapshot and both review manifests, the21 actual source
PNGs, exact stable IDs/matches/PTS and decisions/drafts. Semantic promotion remains
rejected even after digest recalculation; an existing freeze directory cannot
be overwritten, including an empty directory. This is not authenticity proof.

Fresh scoped suites pass:33 new private-contract tests (plus39 subtests),82 prior
private-review tests,84 event-engine tests,51 preannotation tests,37 detector-event
adapter/diagnostic tests and127 deployment-review tests. Total414 passed,1 skipped;
subtests are reported separately, not counted as independent test cases.
`pip check` exits0 (No broken requirements found),`git diff --check` exits0.
Full offline-video regression separately completes with908 passed,3 skipped,
exit0 in1672.23s (0:27:52). Command from tools/offline_video:
`../../.venv/Scripts/python.exe -X utf8 -B -m pytest -q -p no:cacheprovider`.
Both sets total1,322 passed,4 skipped;39 subtests remain separate. No warning
summary was printed. Full-suite stderr was not separately captured; skip reasons
were not printed because this invocation does not use `-rs`. Its final receipt
is separate; do not rewrite the earlier scoped-check receipt.

Initial combined pytest collection encountered same-named modules across
independent directories; no assertions ran. Importlib collection then exposed
the one-off test's local-module import assumption. Final invocation separates
the existing suites into their own processes. Preserve the first failed receipt;
no product code/tests/data/environment or cache was changed to hide errors.

Protection check:all5,692 pre-existing private files retain their original hashes,
all231 tracked baseline files except the approved docs remain byte-identical,
no private data/model/image is tracked,main unchanged. At that audit point all29
new private files checked were Git ignored. Later private receipts are checked
again at finalization. All four changed-doc links pass; added public text has0
local private-path/account-marker/secret-pattern hits. Pixel comparison verifies
all8 old FC crops equal original lossless source crops, and all7 new display
original panels are native1:1 source crops with matching SHA. Human bbox
confirmation remains0; machine pixel equality is not semantic bbox attestation.

Actual commands/output receipts are private under
`outputs/module3c-precise-review-finalization/`. New private validator file SHA
`fa2450026d06e9b6334230c7c2ccfa34e873c4e1aa17060331ca5547ebcf6e5b`;
its test file SHA `8d4ce76d1afb920157b257f519e55ae18935dbd5b585404bd1ccea81ff99e163`.
They are one-off local review tools, not new production data-loader/engine code.
JS/Android build not run:neither subsystem changes in this task.

## Boundary and next step

Only four public documentation files change:CURRENT_STATE,DECISIONS,
DEVELOPMENT_PLAN and this checkpoint. All scripts,review tables/images,snapshot
and receipts remain private/Git ignored. No application schema/database or
dependency changes. No push,merge,new model or real-game access.

Stop after local commit/report. The next separately authorized step may address
the small pixel-level geometry handoff and source/coverage qualification only.
