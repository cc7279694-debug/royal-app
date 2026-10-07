# Module 3A — Deployment Event GT verification

## Current checkpoint: explicit user return and Event GT Lock v1

Date:2026-10-07. The latest user request authorizes only recording the supplied
human-attested outcomes, creating a new Deployment Event GT Lock v1, validating
it and stopping. Public baseline:
`5179569bef0773379715b4c2b0c191ce08ba64f0`; branch
`codex/module3a-deployment-event-gt`. No automatic tracker/event engine, model,
App/game integration, push or main merge is authorized.

### Actual frozen result

| Candidate | Attested result | Approximate time | Type / relationship |
| --- | --- | --- | --- |
| 02 | opponent Witch | 31.5s | direct |
| 05 | opponent Royal Hogs | 75.5s | grouped, one event |
| 06 | opponent Flying Machine | 78.0s | direct |
| 07 | opponent Golden Knight | 102.5s | direct |
| 08 | opponent Minions | 116.0s | grouped, one event |
| 04 | no new play, continuity | not a new onset | continuity with unresolved03 |
| 09 | no new play, duplicate | not a new onset | merges into confirmed08 |
| 12 | no new play, continuity | not a new onset | continuity with unresolved11 |
| 01/03/10/11 | unresolved / non-evaluable | not confirmed | deployment_onset_outside_review_window |

Totals:5 confirmed events (3 direct /2 grouped),3 continuity/dedupe outcomes
(2 continuity /1 merge),4 unresolved,0 Negative. All five events have
owner=opponent, form=unknown, evaluable=true and confidence=human_confirmed.
Confirmed events cover **only natural_match_01**; reviewed windows also cover04
but do not confirm its onset. Continuity03/11 does not resolve their onset or
mint an event. Unresolved outcomes are not no-play or detection Negative.

The lock's embedded human return explicitly records reviewer=user,
actual_human_confirmation=true, human_review_attested=true,
review_basis=chatgpt_visual_review and
confirmation_source=user_attestation_based_on_chatgpt_visual_review.
ChatGPT is the review basis, not the human reviewer. These are authoritative
user-returned annotations; this run does not re-judge the visual review.

New ignored path:
`outputs/module3a/event-gt-lock-v1/deployment_event_gt.lock.v1.json`.
File SHA256:
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
Canonical lock digest (excluding its own digest field):
`f7709ba45189546df5a74991ce88c8d1911eec337640d68623f651377540eacd`.
Separate new `human-return.v1.json` SHA256:
`ec9600df9bd669d656f5c383e42767c929a40ef5e3dae299c5b5f798c32cd0fd`.
Original source-plan byte SHA:
`f62813c54765e0f506a64654544c9d8efa501fc2aeacfc6507d0f47195ed20cc`;
semantic source-plan digest:
`87dfad2a5d7d6ee1ff20ee20445649d3c9b83832124bb91df7e92a77781b5aff`.

Fresh source-check, exclusive freeze/readback and separate revalidation all
exit0. A second same-path freeze raises FileExistsError; file SHA stays unchanged.
Caller checks all six referenced visual-GT/lock file SHAs against the original
plan, plus the plan byte SHA and semantic digest. All five user-corrected times
fall inside their original contexts and each has an existing exact-PTS context
frame. This is alignment of **approximate annotations**, not a fabricated
last-absent/first-visible deployment interval. No video is re-decoded or re-extracted.
Receipts: `outputs/module3a/event-gt-lock-verification-v1/`.

### New manual utility and fresh checks

Only `event_gt.py` and its tests are new code. `bundle.py` and the original blank
template remain pending-only and unchanged. The new validator requires a complete
one-decision-per-candidate partition, exact user attestation, supported opponent
mapping and explicit confirmed fields; continuity may point at an earlier
unresolved candidate, but duplicate merge requires an earlier confirmed event
in the same underlying match. Derived events/outcomes, limitations and digest
are rebuilt on validation. Exclusive creation also rejects a renamed sibling
with the same source/version identity; JSON size/duplicate-key/non-finite and
symlink/junction/path boundaries are checked. This is an annotation-only v1 API,
not a tracker, detector, input-control mechanism or production Model Lock.

TDD missing-feature RED was observed before code (84 failures/1 skip), then
GREEN. Source-boundary, official Mortar-class and canonical hyphen-name issues
were each reproduced before their small new-tool fixes. The first real source
check rejected underscore canonical names used by the new validator; this was
fixed to match frozen `unit.golden-knight`, `unit.flying-machine`,
`unit.royal-hog`, `unit.skeleton-barrel`, without editing evidence. Four positive
regressions were observed failing before that fix. Initial joint collection
without importlib stopped on existing duplicate `test_bundle.py` basenames;
the scoped run below uses importlib and changed no legacy tests or packages.
These earlier failures are preserved, not presented as passing checks.

Fresh root-run commands and actual results:

| Command (existing `.venv` unless noted) | Result |
| --- | --- |
| `python -m pytest tools/deployment_review/tests tools/preannotation/tests -q --import-mode=importlib --tb=short -rs` | 178passed /1skipped, exit0 |
| `python -m pytest tools/smoke_training/tests -q --tb=short` | 26passed, exit0 |
| `python -m pytest tools/smoke_training_attempt02/tests -q --tb=short` | 174passed, exit0 |
| `node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs` | 8passed /0failed, exit0 |
| `npm.cmd test -- --run`, cwd `app` | 43passed across3files, exit0 |
| `python -m pip check`; `git diff --check` | both exit0 |

Totals:378 maintained Python tests passed/1 Windows symlink-creation permission
skip;51 JavaScript tests passed. These smoke-training suites are contract
regressions, not new real training or inference runs. Actual outputs/commands are
under `event-gt-lock-verification-v1/final-checks-v1/`; TDD evidence is in
`code-checks-event-gt-tdd.md`. The independent Codex read-only code/source review
found no remaining Critical/Important blocker to this authorized local freeze;
it is not ChatGPT independent visual review or detector performance acceptance.

Not Run this checkpoint: the approximately28-minute maintained offline-video
full suite (previous execution below is historical, not a fresh result), model
training/inference, Android build/device retest, broader cross-match/real-game
validation. Module1/2A1 production code, extractor, prepare/validate/review,
dependencies, environments and App are not changed by this separate utility.

### Preservation and limits

Fresh bounded before/after preservation PASS, exit0:1786 existing files retain
identical hashes (1397 previously fixed files plus389 retained3A artifacts).
This includes all four original MP4s, old visual/experiment locks, Attempt01/02,
benchmark assets, original review ZIP and lightweight supplement. Old3A directory
membership is identical;1806 combined private paths are Git ignored at the AFTER
check and tracked private files0. New outputs/receipts remain ignored; no existing
Evidence or original blank return is rewritten. No SQLite, migration, cloud,
model/package installation or runtime permission change.

Final scoped document/privacy audit: exactly7 public files,91 local links with
0broken,0credential-pattern hits,412 current3A private files ignored at that
check,0tracked private files. Old bundle/offline-video/App diffs are empty and
main remains unchanged. Later new private completion receipts are also checked
for ignore status before stopping.

The digest checks consistency, not independently authenticating raw source
assets or proving human identity. Supplied source byte SHA must be verified by
the caller, as done here. Exclusive/path safeguards are local application checks,
not an OS-level concurrency/isolation or tamper-proof guarantee.
No cross-match event validation, detector accuracy, full-match event coverage,
8-card/cycle/evolution/elixir completion is claimed. About10–20 candidate/event
ambition cannot justify inventing events beyond the explicit5-event return.
Stop after this checkpoint; do not automatically enter Module3B.

## Preserved historical preparation verification (before user confirmation)

Date:2026-10-07. Scope: current user's candidate-bundle stop, not event-engine
implementation or completed Event GT. Baseline
`cba41106a711405e9e0e8bd6bf08cd450259b878`; feature branch
`codex/module3a-deployment-event-gt`; no push/main integration.

## Actual prepared material

-12 curator-selected pending windows, source01 chronological10 then source04
  chronological2; source02/03 remain in the original intake inventory with
  explicit evidence gaps. Source02 stays truncated/training-excluded. Neither
  omitted matches nor times become Negative. Source04 is DEV_TUNE, not blind.
-5 provisional card identities: Witch, Golden Knight, Flying Machine, Minions,
  Royal Hogs.6 direct /3 grouped /3 uncertain. Three windows are deliberate
  duplicate/continuity challenges; no12-event or independent-event claim.
-Each window has±3s source context, a local presentation-only MP4, a contact
  sheet and original-resolution PNG links.12 MP4s each decode145 frames;
  143 unique PNGs /156 references /20 accepted visual-object references.
-173 ZIP members:172 manifest-bound files plus manifest. ZIP89,747,387bytes,
  SHA256 `b56efe6ccb8757faa647250af2010212e63587a5a79f4c9f5372521f43f0462e`.
  Folder `outputs/module3a/deployment-event-human-review-v1/`; archive
  `outputs/module3a/Module_3A_Deployment_Event_Human_Review_v1.zip`.
-`event-review.csv` and `human-return.template.json` remain blank/pending,
  human_review_attested=false, reviewer empty. Manual review supports confirm,
  reject, uncertain, merge_duplicate and card/owner/time/form corrections plus
  last-absent/first-visible, uncertainty and notes.

No candidate is an OpponentCardPlayed. Confirmed events0; Negative0; Event GT
Lock not created. Original83-box/9-class human visual GT remains unchanged.
Own Mortar/Skeleton Barrel are excluded from opponent candidates; Cannon and
Barbarian Barrel stay visual-only/null mapping; Witch-spawned Skeleton is not a
Skeletons-card event. Grouping and duplicate hints remain manual questions.

## Executed package/evidence checks

Private generation helper uses the unchanged Module1 extractor once per needed
recording, unioning requests:122 for01,21 for04, all success. Exact origin is
reconstructed from origin_pts×origin_time_base; source times are PTS×time_base
minus origin. Clip re-encoding does not establish timing truth. No new detector,
tracker, training or UI operation runs.

The first private presentation run mistakenly requested an absent report field
`origin_seconds_exact` after completing01's frame export. It stopped before any
clip/package was generated. The helper now reconstructs the exact origin from
the existing Module1 fields; the122 successful exported frames/report were
preserved and reused, not unnecessarily extracted again. Old evidence unchanged.

Fresh main-process read-only audit exits0: all ZIP actual bytes match the manifest
and directory; CRC/member set/count pass; six visual-source/lock SHA bindings
pass; two annotations bind to their respective lock members and old smoke GT
equals its lock payload;20 references match accepted object/frame/recording/
appearance/bbox/owner/form. Current strengthened validator accepts the real
pending plan; CSV/JSON both contain12 pending rows, no event/Negative/attestation.
Receipt: `outputs/module3a/preparation-v1/bundle-audit-v1.json`.

An independent Codex code reviewer additionally decoded original01/04 and
matched all143 PNG raw PTS/time_base/origin and RGB pixels to the source video,
and decoded all12 clips without corruption. This is source/presentation
verification, **not** ChatGPT independent visual review, human confirmation of
card identity/owner/continuity/new deployment or account-safety permission.

## Tests and verification status

New presentation tests were observed RED before implementation (21 failures
for missing packager), then GREEN. Review-exposed archive races, owner/reference,
recording identity, truth claims, source-ID and source-SHA boundaries were each
reproduced by failing tests before fixes. Latest targeted run:

```powershell
.\.venv\Scripts\python.exe -m pytest tools/deployment_review/tests -q --tb=short
```

32passed, exit0. These are synthetic contract/presentation tests, not confirmed
event accuracy. No tracker/model/Android behavior is added.

The initial bare root `pytest` exited1 with8 collection errors: ignored archived
duplicate test modules, isolated upstream YOLOX tests requiring absent torch,
and cross-project duplicate test basenames. An importlib-mode root retry exited1
with18 legacy fixture import errors. Neither reached assertion execution. These
failed collection attempts are disclosed, not called passing regression and not
fixed by deleting tests, modifying old code or installing model dependencies.

Fresh maintained suites ran separately using existing per-project imports:

| Suite / actual command | Result |
| --- | --- |
| `.venv` Python `-m pytest -q --tb=short`, cwd `tools/offline_video` | 908passed /3skipped, exit0,1714.49s |
| `.venv` Python `-m pytest tools/preannotation/tests -q --tb=short` | 51passed, exit0 |
| `.venv` Python `-m pytest tools/deployment_review/tests -q --tb=short` | 32passed, exit0 |
| `.venv` Python `-m pytest tools/smoke_training/tests -q --tb=short` | 26passed, exit0 |
| `.venv` Python `-m pytest tools/smoke_training_attempt02/tests -q --tb=short` | 174passed, exit0 |
| `node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs` | 8passed /0failed, exit0 |
| `npm.cmd test -- --run`, cwd `app` | 43passed across3files, exit0 |
| `.venv` Python `-m pip check`; `git diff --check` | both exit0 |

Total maintained Python1191passed /3skipped; JavaScript51passed. No assertion
failure. Historical totals are not substituted for these new actual runs.
Original logs are retained under `outputs/module3a/preparation-v1/checks-v1/`.
After successful Node tests, the private check wrapper could not print Node's
checkmark through Windows GBK and raised UnicodeEncodeError. It did not corrupt
results; only still-unrun App/pip/diff checks were resumed with ASCII-safe
logging in `checks-final-v1/`, exit0, preserving all completed original logs.
This logging issue did not trigger video regeneration, GT changes or retraining.
The3 skips were separately rerun with `-rs`: OS denies symlink creation,
Windows symlink privilege unavailable (WinError1314), and Windows symlink
privilege unavailable. All3 remain skips, exit0; existing junction tests ran in
the full suite. No skip/dependency policy was changed for this task.

## Protection and privacy

Fresh BEFORE/AFTER bounded audit exits0/PASS:1397 fixed existing files retain
identical hashes and13 bounded directory memberships retain exact members.
This includes the four original MP4s, both multiclass visual locks and retained
historical locks, Attempt01/02 results, benchmark/model assets and selected
upstream code. It is not a new whole-environment32,217-file byte audit.
All three environments keep package counts13/22/41, fresh pip check/freeze
exit0, and raw before→after package inventories/Python/pip versions identical.
No packages or model environment were installed/changed.

An older receipt's offline editable Git ref followed the already-verified
docs-only cbc6dd7→cba4110 checkpoint, with no package change. Initial strict-raw
FAIL is preserved; a new explicit old-ref normalization verifies only that
historical delta. The new3A before→after comparison is raw/strict, not relaxed.

AFTER receipt SHA256
`b6110b0158cb1a653f54b5d834aa5c2271cf08942fcd498c4aa812e746db796d`;
`outputs/module3a/protection-v1/protection-after-verified.json`.
At that check1739 combined private paths were ignored; tracked private/media0.
A fresh AFTER audit, run after all maintained regressions finished, also passes:
1397 unchanged fixed files,13 unchanged directory memberships, all four source
MP4s/old locks unchanged, three raw before/after environment inventories equal,
1755 combined private paths ignored and tracked private/media0. Final receipt:
`outputs/module3a/protection-v1/protection-after-verified-final.json`, SHA256
`514cdb822b76169f73696ed2ca8ee01824b393551aef40ffaf0d472d788bbbab`.
The later read-only document/privacy check verifies94 relative links/0broken,
credential patterns0 and358 current new-module private files ignored. Counts
grow only as new ignored verification receipts are written; historical material
is not overwritten. Final documentation and completion receipts are checked
again before the local checkpoint.

Fresh-context Codex branch/package review: no remaining Critical/Important
issues after test-backed fixes. It verifies presentation/source consistency,
not human deployment truth, and does not replace ChatGPT/user event review.

## Limits and stop

Candidate visual anchors may be after the actual deployment.±3s may fail to
contain onset; a reviewer must mark uncertain/request wider context rather than
confirm a play from persistent screenshots.12 windows do not guarantee10–20
confirmed events. Minion/Royal Hog unit-class mappings are not unique card-play
proof. Form remains unknown; match/recording aliases are retained, not treated as
new matches. Full-match event coverage, exact onset and grouping are unreviewed.

The reusable tool checks manual-input/file consistency, not raw-video authenticity
or independently proving source GT acceptance; this run separately verifies its
locked source references and media. Human return is a draft interchange, no
import/freeze command. Later return validation and Event GT Lock need explicit
human attestation; no Module3B, training, production Model Lock, game input,
state machine, capture/overlay or real-game HUD is enabled. APK not rebuilt or
phone-retested. No new package, database, migration or cloud dependency.
