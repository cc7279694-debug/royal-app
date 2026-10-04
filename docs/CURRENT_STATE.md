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
- Real experiment: WAITING_FOR_DEVELOPMENT_MATCH. No new natural development
  replay supplied; no actual Development Data Lock or DEV_LOCKED result.
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
Fresh post-fix full suite: 385 passed, one known Windows symlink permission skip.
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

Infrastructure checkpoint complete; await a NEW natural replay at
`local_data/recordings/development_01.mp4`. Record battle-history replay from
opening through result at normal speed, no edits. Do not preselect a card or
arrange the opponent. Missing footage blocks DEV_LOCKED and final 2A2 acceptance.

See [2A2 verification](VERIFICATION_M2A2.md),
[blind protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md),
[contracts](MODULE_2A2_CONTRACTS.md), [roadmap](DEVELOPMENT_PLAN.md),
[historical 2A1 verification](VERIFICATION_M2A1.md).
