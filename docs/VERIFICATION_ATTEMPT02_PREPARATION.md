# Attempt02 — preparation and human-review stopping boundary

Preparation: 2026-10-06; final checks: 2026-10-07.
Status: **WAITING_HUMAN_REVIEW**, not training complete.
Starting local HEAD `68398ffc7cca521bc0964df47320400dbc2f1bb2`, branch
`codex/module-2b2b-multiclass-infrastructure`; main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.

The user's relayed independent verdict is
`TWO_CLASS_SMOKE_ATTEMPT01_VALID_BUT_INSUFFICIENT`. The old checkpoint and first
evaluation are retained; no real model rerun occurred during this preparation.

## Actual preparation

- The pinned GT v1 and Training Dataset Lock v1 load successfully through the
  unchanged Attempt01 loader. Dataset SHA remains
  `582dc30d3e418aebf09adfed931742627c29a1f3da1a19ae24c165621cc58e39`;
  GT SHA remains `f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1`.
- Original TRAIN exported categories, object IDs, integer bboxes and source PNG
  hashes were checked against all six frozen labels. Skeleton=0/Witch=1. Four
  original/ROI sanity overlays were generated and visually inspected; no swap
  or export misalignment found. This is a sanity check, not new human GT.
- Fixed ROI from TRAIN geometry: `[0,H//8,W,H*31//40]`, half-open pixel xyxy;
  432x960 becomes `[0,120,432,744]`, crop 432x624. It excludes top/bottom UI;
  full horizontal width conservatively retains outer playable lanes, with some
  side decoration still present. No DEV prediction informed the ROI.
- Reviewed existing TRAIN-only survey images to select candidates. Eight
  positive candidate frames: 158,160,161,162,163,164,165,166 seconds.
  Eight candidate negatives: 5,10,15,75,90,95,100,105 seconds. These are proposed
  absences, not confirmed negative training labels. No other match imagery was
  viewed for candidate selection. Match04 is only a future DEV_TUNE role.
- Reused 12 existing PNGs; extracted only four new requested frames
  (158,161,162,166s) using the unmodified Module1/2A1 preparation pipeline,
  actual PTS aligned and report status success. All seven prior index/report
  sets plus this new set were loaded with the unchanged strict loader.
- Self-contained human-review packet has 16 originals, 16 marked review images,
  16 ROI views, 21 context crops, two contact sheets, exact PTS/source/frame
  metadata, fixed config, original sanity overlays, review CSV and return
  template. Six original boxes remain confirmed; 15 new boxes are explicitly
  pending drafts. Two old frames retain original exhaustive confirmation;
  14 frame coverages/negative decisions remain pending.
- New Witch sightings propose the old continuous Witch episode identity.
  Left-lane small-unit identity/source and post-163s spawned-wave continuity
  are marked pending; no new independent card deployment is inferred.

ZIP: `Module_2B2B_Attempt02_TRAIN_Human_Review.zip` (private local ignored output),
23,411,740 bytes, 84 members. SHA:
`7e7a1d9d50d9ec4de1d7b5dbe6a5049ca041cd64737265f966b7e8446ba51972`.
ZIP CRC and every copied member SHA were checked against the source bundle.
No automatic upload, original MP4, model weight, DEV image or model prediction
is included in this human-review packet. Private images/GT remain Git-ignored.

## Verification

Actual maintained regression (working directory `tools/offline_video`):
`../../.venv/Scripts/python.exe -m pytest -q --tb=short`, with JUnit output
to the private preparation directory: **908 passed / 3 existing Windows
symlink-permission skips**, exit 0, 1039.57 seconds. The process-bound awake
guard was released normally. No real-model experiment was part of this suite.

Final helper regression, from repository root:
`./.venv/Scripts/python.exe -m pytest tools/smoke_training/tests tools/smoke_training_attempt02/tests -q --tb=short`,
with separate JUnit output: **146 passed**, exit 0, 24.79 seconds. This includes
26 unchanged historical smoke tests and 120 new tests (91 data/ROI/coverage
contract tests plus 29 private-profile, safe-object-ID and exact-export-binding
tests). The two suite results are separate runs, not a single combined run.

Fresh `pip check` in both the offline and independent model environments exits
0, `No broken requirements found.` Installed package inventories match the
Attempt01 post-run baseline (only explicitly allowed editable checkout Git
references are normalized); all 160 pinned official YOLOX source files and the
existing official pretrained weight remain unchanged. No installation, download
or model import/execution was performed for these checks.

Read-only after-check verified **32,217 protected historical file hashes
unchanged**, including original recordings, old private evidence/locks/exports,
Attempt01 checkpoint/predictions and legacy code. The inventory also includes
historical synthetic fixtures; file counts do not represent natural matches or
independent deployments. All **32,143 private protected paths remain ignored**;
zero private/generated media files are tracked. The pinned v1 GT/Dataset Lock
and original six TRAIN labels were revalidated without modifying them. No
expanded GT/data lock or Attempt02 model-run artifact has been created.

The actual review ZIP still has the recorded SHA/size, 84 unique members and
valid CRC. Separate read-only packet audit verified all 83 manifest-listed
member hashes, 69 HTML references, PNG integrity, source-byte parity and ROI
pixel crops. A public-doc audit checked 69 local Markdown links; scoped secret
and private-media scans found no accidental source paths, raw source-media
hashes, credentials or tracked images. `git diff --check` passes. Public
source uses a required ignored runtime profile rather than private filenames.

New safety regressions enforce private source-profile separation, safe object
IDs before any crop path is created, and each exact frozen object once on its
correct exported image. Synthetic defect tests failed before the corrections
and pass afterward. These preparation fixes did not regenerate or alter the
actual review packet. Existing public Module1/2A1/2A2 and Attempt01 model-run
code is unchanged.

Receipts, raw output and JUnit stay in the ignored preparation directory:
`attempt02-legacy-regression.*`, `attempt02-final-helper-tests.*`,
`legacy-regression.xml`, `preparation-tests-final.xml`, and
`final-preparation-verification.json`. Git remains on the starting local HEAD
above, with 11 intended public source/test/document files changed or added;
this preparation handoff has not staged, committed, pushed or merged them.

## Not run / remaining prerequisite

New human review, expanded GT/data freeze, Attempt02 model instantiation,
pretrained transfer, 300-step CUDA training, checkpoint and DEV_TUNE evaluation:
**Not Run — new exact human-confirmed positive/negative coverage is missing**.
No new training-ready lock, Model Lock, Tiny experiment, model installation,
weight download, blind testing, Attempt03, Module3, push or main merge.

Next action: ChatGPT reviews the packet and returns object/group decisions plus
selected-class exhaustive coverage and explicit zero-target confirmations. Only
then freeze a new immutable snapshot and continue the already-authorized fixed
[Attempt02 protocol](PHASE_C_ATTEMPT02_PROTOCOL.md). Preserve old v1 locks and
Attempt01 results byte-for-byte; report insufficient evidence rather than train
unconfirmed labels or unreviewed background.
