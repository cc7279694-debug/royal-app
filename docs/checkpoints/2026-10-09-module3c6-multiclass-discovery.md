# Module3C6 — New recordings and multiclass discovery

## Goal and scope

Execute the user's revised task: ingest four complete user recordings, discover
actual visual/card candidates, recommend2–4 next targets and prepare a small
independent review bundle. Not Royal/Minion-specialized collection, training or
full-card recognition. Baseline `1eda1a43fa7193eb8620ff2b7314b555c85a7787`,
branch `codex/module3c6-multiclass-discovery`; main unchanged `602dd0f...`.

## Four source registrations

Sources are private in `素材/`, now explicitly Git ignored. Fixed filename
ascending order4934→4935→4936→4937 was chosen before predictions, not by card
quality; capture chronology is not independently verified. Stable match IDs
05..08 remain separate from `rec-<first20 source SHA>` recording IDs.

| Match | Filename | Bytes | Metadata duration(s) | Last actual PTS(s) | Decoded frames |
|---|---|---:|---:|---:|---:|
|05|1000074934.mp4|47,782,252|103.969|103.927|2,522|
|06|1000074935.mp4|57,739,005|120.352|120.311|2,919|
|07|1000074936.mp4|45,181,695|97.325|97.284|2,361|
|08|1000074937.mp4|28,077,575|62.293|62.252|1,511|

All HEVC1200x2670, rotation0; average FPS24.2572/24.2539/24.2589/24.2563.
All9,313 frames fully decoded to EOF; increasing PTS; max inter-frame gaps
44/44/43/44ms. Actual origin/last raw PTS and rational time base retained privately,
not reconstructed from FPS. Full source SHA-256:

```text
05 6b6a658db38f3323ec65cfb4439773542b749f3abcfeff7219fd00f0eb7e2d8c
06 0e8f746e1d01eb8b959bf40370a4fa7e73b389b2ac8555a651741d4534bf06a0
07 6c27a0a00b66a1e6d29267f48f2ca7a8f0736d98c43aef2df27f4772358a6e36
08 be448704cc8f1061fc91965f9d70792669e3d7c1f75e98a2727a79d77d3ed480
```

All4 source hashes unique and different from5 actual historical recordings
(retained01..04 plus historical Inferno), freshly checked. Independent-match
status uses user report plus distinct boundary match contexts, not hash-only
authenticity. All12 first/middle/last images were viewed and all4 end in result
UI; no visible mid-battle end conflict. `completion_attestation=user_confirmed`,
terminal result screen=true. Full decode/PTS and boundary images do not prove
absence of internal edits or duplicate re-encoding. Personal names remain private.
Source has unspecified pixel aspect metadata; preserved encoded dimensions.

Early replay controls visibly change/show x1/x2; purple elixir x2 is distinct.
All candidate times use source-relative PTS, NOT game-clock or an assumed constant
speed. No newly confirmed play onset. User-reported no Royal Hogs/Minions is not
exhaustive Negative, and a few contrary teacher guesses remain unconfirmed.

## Existing detector reused once

Private pinned KataCR36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8; source clean.
Existing environment Python3.12.4 / Torch2.2.2+cu118 / TorchVision0.17.2+cu118 /
Ultralytics8.1.24 / OpenCV4.9.0.80 reused. Existing two official-source research
weights v0.7.13 verified unchanged; no installation, downloads, dataset use or
training. Prior root MIT / modified YOLOv8 AGPL and unverified asset/weight rights
caveats remain; private proposals only, no redistribution or APK integration.

Fixed BEFORE inference: replay ROI `[24,534,1176,2309]`,576x896 CUBIC canvas,
imgsz896,0.5FPS source PTS (each2s),batch1 FP32 CUDA0,conf0.1,per-model NMS0.7,
max300 and combined class-agnostic NMS0.6, inherited UI filter. CUBIC versus
upstream LINEAR is disclosed; the2% horizontal crop can miss edge units. Native
review images retain full width so missed edge targets can be added manually.
No GT, tracker or event engine imports/data inputs. Model train/val/track denied.
Two inherited configuration prose keys (`layout`, `visualization_keyframes`) are
stale/nonexecuted. Actual replay source_layout/ROI/full-file2s sampling take
precedence; the sealed inputs are retained unchanged with explicit errata.
Network calls denied in inference process;3 library outbound attempts were
blocked, no successful outbound call. This is not a claim of OS sandbox isolation.

| Match | Samples | Mean model time(ms) | Full scan wall(s) |
|---|---:|---:|---:|
|05|52|472.04 including warm-up|55.67|
|06|61|314.09|51.96|
|07|49|314.69|42.37|
|08|32|316.43|26.98|

GTX1050Ti CUDA parameters and GPU query recorded; peak allocated memory approx
554MiB warm-up/488MiB later. These are offline discovery speed measurements,
not Android real-time performance.194 sampled scenes,5,412 raw boxes,108 raw
labels including UI/towers/effects/hallucinations;686 raw temporal bursts are
review locators, NEVER independent deployments. Mean includes dual detector/NMS;
wall also includes decode and file/protection overhead.

Runtime source fingerprints are preserved rather than hidden: scan process
loaded private driver v1. A display-only survey function/CLI was added while the
same scan ran;05/06/07 markers fingerprint v1,08 marker fingerprints display-
extended v2. Preserved exact source SHAs and identical `scan` AST hash prove
inference code/config unchanged; no repeated scan. Details in private
`runtime-source-binding.v1.json`, both scripts retained. Production code unchanged.

## Distribution and recommended targets

Analyst pixel survey viewed19 contact pages/194 sampled battle scenes (not a
continuous human replay).36 per-match tentative rows/30 visual candidate names
produce95 curated review windows, NOT95 independent plays. Actual independent
counts and onsets unknown until source-context/human review. Top-hand card UI
does not establish a battlefield deployment. Sparse sampling can miss fast spells,
spawn and obscured targets; non-detection is never absence.
Integer context windows are approximate nominal-sample locators, not precise
inclusive onset intervals; exact selected times are in frame CSV/raw PTS.

| Match | More useful primary candidates | Important caveats |
|---|---|---|
|05|Magic Archer; Skeleton King-like; P.E.K.K.A-like; Bandit/ram-like|new appearance/model conflicts; old versus new units unresolved; released barbarians secondary|
|06|Firecracker; Knight-like; Bomber-like|small/edge targets; ordinary/evolved/Monk confusion; green spawn cohorts not settled card plays|
|07|Witch; barrel-projectile candidates; own Executioner-like|skeleton cohorts can be spawned; projectile card/owner uncertain; cross-river owner not position rule|
|08|Witch; Firecracker; Mega Knight|early caster class unknown; Monk-like/structure source uncertain; held out of training/tuning|

Recommend **2** primary classes for the next review:

- `visual.unit.witch`:07 three separated contexts18–22/42–48/78–82s,
  08 one44–58s context. Existing accepted01/04 Witch references can be audited
  for later reuse without lock mutation. Form stays unknown; skeleton companions
  never become Skeleton card deployments.4 locators !=4 verified independent plays.
- `visual.unit.firecracker`:06 five contexts22–24/44/58–64/84–86/94–96s,
  08 one26–34s.58s has tentative birth-clock/light evidence. A single surviving
  unit may explain multiple contexts;6 locators !=6 independent plays. Precise
  native-pixel boxes and owner/class/exhaustive review are necessary.

Other classes retained, not discarded; Cannon-like source-card mapping null.
No model confidence count establishes data qualification. All newly displayed
owner/form/origin actual fields unknown, teacher hypotheses separate; canonical
card mapping unset. No Human reviewer attestation, new visual GT, events or
Negative. No use of old49 partial-field boxes as complete supervision.

## Private lightweight review deliverable

Directory `outputs/module3c6/discovery-v1/human-review-lite-v3/`;
ZIP `Module_3C6_Multiclass_Discovery_Review_Lite_v3.zip` in same run root.
14,231,654 bytes, SHA-256
`485bca2e93aa06f12fba91060910d19fdec218ce45bd09cf169a3bdfd11a81cd`.
18 selected exact-source-PTS scenes (4/5/5/4 per match);18 original native arena
JPG crops plus18 annotated counterparts,6 contact sheets;71 pending candidate
boxes,36 pending class-coverage rows, object correction/missing-object forms,
distribution/candidate windows/recommendations/intake/manifest/README.

Full native exports1200x2670 preserved in private `human-review-v1/`; initial
full-image ZIP24,018,913 bytes exceeded the20MiB check and is retained, not the
delivered packet. Lightweight display derivative uses existing pixels only,
native1200x1775 arena crop `[0,534,1200,2309]`, without re-decoding, resize, bbox,
selection or status changes. Source bbox uses full1200x2670 xyxy; display-local
y=source y-534. JPEG is lossy review presentation, not approved training pixels.
Manifest/members/ZIP CRC/SHA and coordinate metadata checked. No video/weights
included. Package remains private/ignored and is not automatically uploaded.
Read-only peer review identified two presentation caveats, not detector changes.
V2 preserves all53 lite-v1 member bytes and adds3 small scope/errata files;
coverage-scope binds18 frames to the displayed arena rectangle, whose exterior
remains unreviewed/not Negative. Config errata binds untouched prediction/config
SHAs and explains the inherited stale prose.71 boxes/18 frame selection/36 pending
coverage states unchanged. Superseded oversized/lite-v1 presentations retained.
Before delivery, raw-output reread found one manually summarized locator was
wrong:07 teacher minion guesses occur32.032/56.023s, both own low-confidence,
not14–16s. V3 corrects just that analyst CSV interval/reason and preserves source
predictions, object CSV, review states and all images. The span denotes two
isolated guesses, not continuous presence or confirmed class; correction record
and prior versions retained. Read REVIEW_SCOPE.md with REVIEW.md.

## Data use and preserved history

Source type user_recorded_gameplay; intended use private_local_discovery_and_review;
external upload=false, redistribution=false, rights clearance=unverified,
training qualified=false. User confirmation of completeness/absence is not
class/owner/box/independent-event or legal-rights confirmation.

05/06/07 development discovery;08 retained evaluation candidate selected before
inference, no training/tuning. All have content-discovery exposure;08 is NOT strict
blind. Later split/qualification requires whole-match/source isolation.
08 participates in target selection; it is an exposed exploratory retained
evaluation source, not an independent target-selection/prospective test. If
Firecracker lacks distinct DEV support after precise review, disclose the gap
or freeze an explicitly exploratory two-source protocol; no optimistic training
claim or adjacent-frame leak. Do not request more movies before this review.

Old3C5 decision SHA23b816f... and field Snapshot SHAda432cec... unchanged;
all old video/GT locks, Attempt01/02, benchmark, Oracle FAIL/PASS and3C experiments
preserved. No3B parameters/rules/scoring/App/environment changes.3914 existing
material-file hashes are the protection baseline, not a count of new dataset items.

## Fresh verification and explicit omissions

```text
.venv/Scripts/python.exe -m pytest tools/preannotation/tests -q --tb=short
51 passed in7.61s; exit0 (JUnit saved)
.venv/Scripts/python.exe -m pytest tools/event_engine/tests -q --tb=short
84 passed in0.79s; exit0 (JUnit saved)
# cwd tools/offline_video
../../.venv/Scripts/python.exe -m pytest tests/test_cli.py tests/test_pipeline.py -q --tb=short
47 passed in7.55s; exit0 (JUnit saved)
Total182 passed/0 skipped; scoped regressions, NOT complete project suite.
offline .venv pip check:exit0, No broken requirements found.
existing KataCR venv pip check:exit0, No broken requirements found.
```

Two preliminary combined test invocations failed collection due to duplicate
test_cli module names and cross-directory conftest import; no assertion failure.
Correct established separate-module commands passed; no production/test changes
or test deletion. Initial oversize ZIP check failed as above and was remedied by
presentation-only lighter derivative, not changing evidence to force acceptance.

Private verifier checks old material/source/model hashes, unchanged tracked
production, config/PTS/source-bound frames and every pending-state/Negative guard,
manifest/ZIP integrity, ignore/tracked media, Markdown links and Git diff.
Detailed receipts `verification-final.v1.json` (lite-v1) and
`verification-final-v2.v1.json` and `verification-final-v3.v1.json` (delivered
supplement), plus post-commit Git receipt,
remain ignored. Full offline suite, JS tests/build, Android/GPU training tests,
strict detection/event scoring Not Run: no relevant implementation changes,
unconfirmed pixels cannot serve as scoring GT. No new production unit tests added.

Public delta only `.gitignore`,CURRENT_STATE,DEVELOPMENT_PLAN,DECISIONS and this
checkpoint; private artifact helpers/proposals/images are not committed.

## Handoff

Upload lightweight ZIP manually for independent visual review. Confirm exact
class/owner/bbox, selected-class coverage/missing objects, then inspect onset and
continuity before counting independent deployments and approving later data use.
No Human GT/training lock created; training data remains unqualified. Local commit
and stop; no push/merge, training, event engine, App or live game work.
