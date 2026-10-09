# Module3C Field-Level Human Review Snapshot v1

Date:2026-10-09. Scope: authorized partial-field import/freeze and local commit.
Baseline:`552ddaf1e47c941fc4723d8b054b16e53cde4273`.
Branch:`codex/module3c-visual-gt-mini-batch`; no push/main merge.

## Verified delta

The user explicitly attested ChatGPT field-level recommendations as the basis
of their human confirmation, retaining unknowns. `reviewer=user`,
`actual_human_confirmation=true`, `human_review_attested=true`,
`review_basis=chatgpt_visual_review`,
`confirmation_source=user_attestation_based_on_chatgpt_visual_review`.
These flags apply to the supported fields/typed relationships, not complete
objects, exact boxes, exhaustive frames or card-play events. ChatGPT is not a
human reviewer. No claim this session repeated independent visual review.

The old complete-object contract cannot represent this partial return. A new
private one-off converter/checker and independent snapshot use exact object,
relation, group and display-frame IDs; each display ID is cross-bound to the
canonical frame ID, underlying match, recording, timestamp/PTS and original
proposal. Duplicate/missing/foreign IDs and mismatched source fields are rejected;
row order is not identity. Original CSV/ZIP bytes remain unchanged.

Public changes:README, CURRENT_STATE, DEVELOPMENT_PLAN, DECISIONS and this new
checkpoint only. No production source/test/schema, database/repository/migration,
dependency/environment, App/Android, detector/tracker/engine/scorer or old locks
are changed. New local files stay ignored; no third-party models/assets added.

## Private frozen files and hashes

Folder:`outputs/module3c-field-level-review/snapshot-v1/`.
Snapshot:`module3c.field_level_human_review_snapshot.v1.json`.
Byte SHA-256:
`da432cec5d25b018b69bf9f9da6c399df2859507fa30b5f68228be14d4b88aaa`.
Canonical content digest (excludes its own digest field):
`34dee7444916d867dd028551c847d75ec5c7d1b9fccb5e3e5d46dbc5a3a8f8cf`.

Input Mini-Batch v4 ZIP SHA:
`d580554e67b093e36bb55eeac45d90ffda5912bdd0d764f5cc30703eb038f94f`.
Input `Module_3C_ChatGPT_Review_Suggestions_v1.zip` SHA:
`e8d78816b356286ffaf22458ab3c7c57f144b0fc75ab282b7f8b52222f295c55`.
All five return members and original v4 manifest are hash-bound. Original return
ZIP is privately archived byte-for-byte; no archive extraction/path writes.

Other frozen files:`object-field-review.csv`, `relationship-field-review.csv`,
`visual-cohort-review.csv`, `frame-coverage-review.csv`, archived suggestions,
`freeze-receipt.json`. Every member is SHA-bound by the exclusive receipt.
Folder and file creation reject an existing version; corrections need a new
version. This is application-level immutability/digest consistency, not OS
write protection or source authenticity/legal rights certification.

## Actual statistics and semantic boundaries

49 objects across40 frames in `natural_match_01` and `natural_match_03`:

| Object field | Confirmed cells | Remaining state |
|---|---:|---|
| visual class | 22 | 27 unknown |
| owner | 34 (28 opponent,6 own) | 15 unknown |
| presence (explicit presence-only action) | 12 | Other37 not separately confirmed |
| visual cohort context only | 4 | No single-object class/owner escalation |
| bbox | 0 | All49 unverified; original coordinates retained as proposals |
| global physical ID | 0 | All49 unknown; hypotheses separately retained |

Class confirmations:Royal Hog6, Minion12, Bowler4.22+34+12=68 class/owner/presence
cells plus4 group-context cells gives72 confirmed cells, NOT72 objects. The
11-field object table also has418 unknown cells and49 unverified cells. Tentative
identity/appearance/group hypotheses remain separate from actual field values.
Full-object Human GT0; form/origin/global IDs/deployment timestamp not inferred.

39 relationships:13 third-match physical-continuity links confirmed;9 Minion
identity links tentative;8 Royal Hog identity links unknown;9 visual-cohort links
confirmed. Original `deployment_membership` proposals are preserved as source
data but returned relations are `visual_cohort_membership/same_visual_cohort`,
not actual same-deployment truth. Confirmed continuity is real supporting evidence
even though no global object ID is assigned and strict matching remains blocked.

DG-RH01 is one four-member visual cohort; DG-MI01 one three-member visual cohort.
No RH1–RH4/MI1–MI3 exact per-member IDs, actual deployment group or exact card-play
timestamp are confirmed. Suggested arrival intervals are retained as tentative
review context, not proof of absence/onset. This stage adds0 deployment/card events.

All40 frames:`selected_classes_exhaustive=false`, `eligible_negative=false`.
F32–F34 flying units and all prior unknown-region notes remain unresolved. Zero
Negative. Unknown/rejected/unlabeled regions are not background. Snapshot
`training_qualified=false`, `eligible_for_strict_detector_scoring=false`, every
`full_object_human_confirmed=false`. No detector performance or event score is
computed; all old results remain in their original scope.

## Fresh checks

Commands from repository root:

```powershell
.\.venv\Scripts\python.exe -B -m pytest outputs/module3c-field-level-review/test_field_review.py -q --tb=short -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pytest tools/preannotation/tests/test_bundle.py tools/preannotation/tests/test_contract.py -q --import-mode=importlib --tb=short -rs -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pytest tools/event_engine/tests -q --import-mode=importlib --tb=short -rs -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pytest tools/offline_video/tests/test_evidence_prepare.py tools/offline_video/tests/test_evidence_contract.py tools/offline_video/tests/test_evidence_review.py -q --tb=short -rs -p no:cacheprovider
.\.venv\Scripts\python.exe -B -m pip check
git diff --check
```

Fresh results:private field contract32 passed with27 additional mutation subtests;
existing proposal contract48 passed; formal event engine84 passed; existing
Module2A1 targeted164 passed/1 existing OS symlink-creation skip at
`test_evidence_prepare.py:105`. Combined328 distinct tests passed/1 skipped;
subtests reported separately, not inflated into independent tests. Pip check:
`No broken requirements found.`

Test mutations run only on copies/temporary directories: order invariance,
ID/source binding, each action's field scope, unknown/partial guards, no bbox
promotion, 13/9/8/9 relation semantics, no card/Negative/training escalation,
tampered digest content rejection, exclusive freeze, and changed return ZIP
rejection before any output directory. Actual snapshot construction and reload
validate PASS. Input CRC/member/SHA and original v4 file readback pass.

Two private helper issues found and repaired before actual freeze: returned CSV
image links initially retained old-folder relative paths (normalized to v4);
a newly inserted archive-change test accidentally contained the old overwrite
assertions (moved back to the proper existing-freeze test). One intermediate
private-test run failed1/passed31; final32 and all regressions pass. No real
evidence was changed to satisfy tests and no real freeze existed during failure.

Final independent readback checker:31 named checks PASS, exit0. It reloads the
ID-bound return and frozen JSON, verifies canonical digest and every frozen member
SHA, reads back all four CSVs, resolves98 object and40 frame image references,
checks exact PTS, tests existing-v1 overwrite rejection and verifies field scope.
2705 historical materials plus493 retained Mini-Batch files (3198 distinct)
retain their before hashes, including all four original MP4s, visual/Event GT
locks, Oracle FAIL/PASS and model/experiment histories.220 protected tracked
source/engine/rule/scorer/dependency files are unchanged.136 public relative links
resolve; diff check passes. All11 new private files enumerated at that receipt
are ignored and0 tracked. The receipt itself is also ignored; final precommit
privacy check includes it (12 private files). No private material is staged.
Actual receipt:`outputs/module3c-field-level-review/verification-v1.json`;
local private helpers/tests/return/CSV/snapshot remain outside Git.

Complete908-test offline suite, experimental tracking/model/JS/Android suites,
builds, inference/training/scoring:Not Run this phase. Public code/env remain
unchanged; scoped regression and immutable-source protection are the proportionate
checks. Earlier full-suite outcomes remain historical, not fresh assertions.

## Stop and inherit

Stop at `MODULE_3C_FIELD_LEVEL_REVIEW_FROZEN` after local documentation commit.
No push/merge, new engine rules, training, model replacement, App or live-game
integration. Pixel-exact bbox/identity review or any next experiment requires
separate authority. Do not feed partial snapshot into the full-object importer,
compute strict IoU/ID/owner metrics from unverified boxes, or call a cohort a play.
Prior [review preparation checkpoint](2026-10-09-module3c-visual-evidence-mini-batch.md)
and all original draft/GT/FAIL/3B/3D histories remain unchanged.
