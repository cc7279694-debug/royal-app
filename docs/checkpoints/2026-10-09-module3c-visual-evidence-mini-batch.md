# Module3C Visual Evidence Dataset Mini-Batch

Date:2026-10-09. Scope: private human-review preparation only.
Baseline:`1873ccf96617ca02804c0b3627687f5a4e557ce6`.
Branch:`codex/module3c-visual-gt-mini-batch`; main remains3D `602dd0f...`.

## What was prepared

| Underlying match / window | Fixed cadence | Frames |
|---|---|---:|
| natural_match_01 / Royal Hogs74–82s | 0.5s inclusive | 17 |
| natural_match_01 / Minions114–130s | 1s inclusive | 17 |
| natural_match_03 / combat52–57s | 1s inclusive | 6 |

Selection was frozen before selected-window model comparison. Unchanged
Module1/2A1 producer decodes new source frames and strictly reloads export
reports/indexes. Every frame carries canonical ID, source SHA, actual PTS,
rational time base, source origin, resolution and lossless PNG/RGB hashes.
Original MP4s and extracted lossless PNGs stay local. JPGs are full-size,
unretouched-content lossy previews, not a claim of byte-identical originals.

Repository modifications:README, CURRENT_STATE, DEVELOPMENT_PLAN and DECISIONS
are updated; this checkpoint is added. No tracked source/test/config files or
dependencies are changed and nothing deleted. Private generation/check helpers,
new extraction/export reports and the review artifacts remain Git ignored.
Data/storage changes are only new local files: no SQLite, schema, migration,
business repository, persistent App storage or backup change.

49 assistant source-pixel object proposals,39 identity/group relationship
proposals and31 unknown regions remain draft/pending. Actual class/bbox/identity/
group fields stay empty and actual owner/visibility/occlusion unknown. Royal
RH1..RH4 are tentative distinct physical identities and AP-RH1..4 appearances;
DG-RH01 is a separate shared-group hypothesis. Later crowded crossings are
not forced back onto those identities. No count-derived deployment timestamp.

Review supports confirming/rejecting/correcting class, bbox, owner, identity,
appearance, deployment relationship, marking unknown and adding missing boxes.
Per-frame/class coverage must be declared independently. Confirmed GT0,
Negative0; no new GT/Training Lock. This is not sufficient training volume.

## Private review artifacts

Folder:`outputs/module3c-visual-gt-mini-batch/review-v4/`.
ZIP:`outputs/module3c-visual-gt-mini-batch/Module_3C_Visual_GT_Mini_Batch_Review_v4.zip`.
SHA-256:`d580554e67b093e36bb55eeac45d90ffda5912bdd0d764f5cc30703eb038f94f`.
Size:18,199,036 bytes (about17.36MiB).

- `index.html`: local frame review links;40 raw and40 annotated JPGs.
- Five continuous `contact-sheets/*.jpg`;`royal-hogs-continuity.jpg`.
- `object-candidates.csv`,`frame-review.csv`,`relationship-review.csv`,
  `deployment-groups.csv`,`unknown-regions.csv`,`add-missing-objects.csv`.
- `model-auxiliary.json`,`detector-comparison.csv`,
  `model-sample-summary.csv`,`DETECTOR_DIFFERENCE_SUMMARY.md`.
- `frames.json`,`manifest.json`,`HUMAN_REVIEW.md`,`EVALUATION_PROTOCOL.md`;
  frozen selection/draft receipts. Every archive member is hash-bound.

Only this bounded packet is intended for user-chosen private ChatGPT review.
It retains game account/interface text; it is NOT anonymized. No original
videos, third-party weights, prior GT locks or absolute host paths are in ZIP.
Previous presentation revisions are retained;40 selected frames and49 draft
boxes never changed between revisions. Display-only revisions improved diagram
readability, separated visibility proposals, cleared disjoint auxiliary box
links and clarified tracking/evaluation/privacy instructions, not GT or rules.

## Detector and independent evaluation boundaries

Existing frozen3C1 detector and original engine outputs,3C4 ByteTrack sidecar
and owner/cohort diagnostics are read-only auxiliaries, not annotations.
Same-class draft comparisons are NOT one-to-one Human GT scoring.12 Royal
draft boxes and15 Minion draft boxes have overlapping same-class predictions;
owner suggestion conflicts3/1 are prompts for review, not error rates.
Original/MOT/episode/cohort IDs stay algorithmic hypotheses.

Third-match52–57s has real opposing units, including an own-colored entity
above the river. Unclear class/identity remains unknown. No prediction cache
exists for that window: Not Run, not FN. Its prior general development exposure
makes it a separate-match diagnostic, NOT blind or cross-match acceptance.
Old0–20s matchmaking prefix and truncatedmatch02 are preserved, not test/negative.

Evaluation protocol is fixed before human GT confirmation: class-correct
IoU>=0.5, one-to-one maximum-cardinality then total-IoU matching, owner excluded
from matching. Detection gaps and true physical continuity/ID switches are
separate; tracking matched requires valid algorithm ID. Owner coverage and
conditional accuracy/joint recall, group-link coverage and accuracy/recall,
visible-arrival interval error are separate. Unknown and unreviewed do not
enter false-positive/Negative denominators. No exact server/player spawn time,
whole-match FP/min, event accuracy or generic training readiness is claimed.
All formal metrics null until human return. No new inference/tracking timing;
historical3C4 component timings are explicitly historical.

## Actual checks

Artifact validator:34 named readback checks PASS, including40 PTS/dimension/
PNG/RGB hashes, strict Module2A1 report/index reload, bounded pending boxes and
relations, unknown/non-negative state, independent clip coverage, ZIP CRC/exact
membership/member SHA, relative private-safe text paths and five JPG sheets.
2705 old material files and220 protected tracked files remain hash-identical;
491 enumerated new private output files ignored, none tracked at artifact receipt;
final check includes the receipt/log files:493/493 ignored.132 documentation
links checked with0 missing; diff check clean. Private/video/weights/key file
queries against Git tracked paths return no entries.

Targeted existing regression commands from repository root:

```powershell
.\.venv\Scripts\python.exe -B -m pytest tools/offline_video/tests/test_evidence_prepare.py tools/offline_video/tests/test_evidence_contract.py tools/offline_video/tests/test_evidence_review.py -q --tb=short -rs -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pytest tools/preannotation/tests/test_bundle.py tools/preannotation/tests/test_contract.py -q --import-mode=importlib --tb=short -rs -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pip check
```

Results:164 passed/1 existing Windows symlink-permission skip;48 passed;
`No broken requirements found.` No test or production source changes.

Then the complete existing offline-video suite ran from `tools/offline_video`:

```powershell
& 'E:\CODEX\royal app\.venv\Scripts\python.exe' -B -m pytest -q --tb=short -rs -p no:cacheprovider
```

Fresh result:908 passed,3 skipped in1104.14s (18min24s), exit0. Skips:
`test_evidence_prepare.py:105`, `test_multiclass_dataset.py:387` and
`test_training_dataset.py:464`, all existing Windows symlink privilege issues.
The164 targeted tests are a subset of908, NOT additional independent tests.
Combined complete offline suite plus48 proposal tests:956 distinct passed/3 skips.

Private check-helper diagnostics retained: first v3 check was launched before
archive completion (missing manifest); second reached a false ignore-name
comparison caused by Windows CRLF in text stdin. Actual outputs were ignored.
Byte/NUL Git path transport was reproduced and fixed ONLY in private checker;
v4 full artifact readback passed. No evidence or `.gitignore` change to pass.

App/JS/Android, experimental tracker suites, model environment/weights/inference/
training/engine/event evaluation:Not Run; no corresponding code/environment
changed. No database/schema/migration/repository/dependency or network change.

## Next stage must inherit

Stop at `MODULE_3C_VISUAL_GT_REVIEW_READY`. User uploads the small private packet
or standalone JPG/CSV files to ChatGPT, then explicitly attests returned human
decisions. Do not call ChatGPT a human reviewer. Only then may the appropriate
visual GT fields become confirmed and eligible visual metrics be computed.
No promotion of3C-3/3C-4, training, engine/App integration, push or main merge.
