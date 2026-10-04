# Current State

Last verified: 2026-10-04.

## Current stage

- Module 1: completed, accepted and integrated into main.
- Module 2A1: formally accepted at
  `98037ceba81683ad1a2c214bada30a10f2f3f69e`; acceptance and ff-only main
  integration published at `3ad657f2c9190f4e389ccd035682becd12d0c51c`.
- Module 2A2 Independent Evidence & Experiment Lock: separately authorized
  2026-10-04; infrastructure implemented and verified on its feature branch.
  Final review's blocking finding is fixed and scoped re-review passed;
  real evidence/lock phase remains incomplete.
- Real experiment: user reconfirms all four natural replay recordings cover full
  matches and explicitly supersedes the result-screen completeness gate. Use
  user_confirmed completion provenance and the actual file-end boundary; absence
  of victory/defeat UI is not incompleteness. Resume the first original-order
  input using its existing rough review. Precise evidence/target remain pending.
  All sources, prior exclusions and first survey/rough review are retained.
  No actual Development Data Lock or DEV_LOCKED result.
- Module 2B, Module 3, Android, HUD and realtime remain closed and unstarted.

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
Last infrastructure post-fix full suite: 385 passed, one known Windows symlink
permission skip; not rerun during the subsequent recording-only intake.
Dependency check, compile check and no-index wheel build passed; dependencies
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

## Current recording intake

- User confirms four distinct new natural whole-match replays, normal speed,
  unedited, not the historical Inferno Dragon match; the current statement resolves
  the old missing-result gate by a new definition, not by rewriting past images.
- Complete replay now means user confirms full-match coverage; last actual decoded
  frame is the evaluable end. Record completion_attestation=user_confirmed and
  terminal_result_screen_present independently. Missing result UI alone never
  blocks freeze. Technical corruption/undecodability, obvious mid-match truncation,
  missing key battle content or explicit human incompleteness still reject.
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
- No dependency/database/cloud/model/runtime networking/Android/game-input change.
  No automatic selection, evolution, cycle or elixir. Model runtime and project
  license remain undecided.
- Live analysis/HUD require applicable explicit Supercell permission and separate
  approval. Passive capture/risk acceptance cannot substitute. Never promise
  zero ban risk.

## Git and next step

Feature: `feat/module-2a2-experiment-lock`, from
`3ad657f2c9190f4e389ccd035682becd12d0c51c`. Focused local feature commits only;
no push, main merge, PR, release, rebase or branch deletion. Preserve the 2A1 branch.
Exact final commit belongs to Git and the handoff.

Continue first-source PTS-aligned deployment/key-frame review and manual candidate
comparison under the user's authorized amendment. Preserve unknowns; only freeze
if >=2 clear independent deployments of one known form pass all existing checks.
Do not skip to a more convenient source, re-record for result UI, edit old evidence,
or treat human completeness as target/negative annotation. Stop at a truthful
DEV_LOCKED or unresolved evidence blocker; final 2A2 acceptance remains separate,
and no model/test work or next module is opened.

See [2A2 verification](VERIFICATION_M2A2.md),
[blind protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md),
[contracts](MODULE_2A2_CONTRACTS.md), [roadmap](DEVELOPMENT_PLAN.md),
[historical 2A1 verification](VERIFICATION_M2A1.md).
