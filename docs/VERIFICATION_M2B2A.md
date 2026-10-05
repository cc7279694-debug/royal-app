# Module 2B-2A — Design Acceptance Amendment & Planning Handoff

Date: 2026-10-05. Documentation/planning only; no multiclass implementation.

## Acceptance source and scope

The user supplies ChatGPT's independent review verdict:
`MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT`, for review commit
`cec8abc35fce2438d149fe4b68b203650cb835e4`.
This records that instruction, not a fresh ChatGPT retrieval or second review
of the amended policy in this session. The prior frozen Review Packet is unchanged.

Taxonomy, provenance/license boundaries, observation/event/card separation,
whole-match splits, unknown handling, model comparison and test protocol remain.
The design amendment adds Scale Coverage Gate: full basically eligible mobile
Development candidate inventory, original bbox measurements, fixed relative-size
policy before class selection, small + medium/large mobile support, missing-size
stop and digest binding. The policy's tie fallback and clear-support requirement
are explicit; relative-small does not assert COCO absolute-small performance.

The next [2B-2B plan](superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md)
separates Phase A schema/readiness/manual data/Dataset Lock from separately
authorized Phase B synthetic model-environment qualification. Neither starts now.
Pretrained weights, real training, threshold changes, Model/Test GT Lock, test
inference, Module 3 and Android/live use are not authorized.

## Changed documentation

- README.md — acceptance, scale requirement and next-plan link.
- CURRENT_STATE.md — present design closeout/planning-only state; history retained.
- DECISIONS.md — durable scale-policy and stage-authorization decision.
- DEVELOPMENT_PLAN.md — 2B-2A Completed (design only), 2B-2B Planned (not started).
- Accepted multiclass spec — fixed measurable Scale Coverage Gate and lock binding.
- New 2B-2B implementation plan — additive interfaces, failing tests and phase stops.
- This verification record — scope, evidence and unrun checks.

No source/test/config/requirements/AGENTS/PROJECT/.gitignore change. No database,
migration, media extraction, annotation, dataset/old-lock edit or cloud change.
The pinned public-source audit is unchanged; no research/model claims refreshed.

## Fresh verification

Fresh checks against this seven-document change set:

| Check | Actual result |
|---|---|
| Local Markdown file links in all seven changed documents | 54 checked, 0 broken |
| `.\.venv\Scripts\python.exe -m pip check` | exit 0; `No broken requirements found.` |
| `git diff --check` | exit 0; no whitespace errors (only Git's LF/CRLF conversion notice) |
| Changed-file scope / full diff inspection | seven Markdown files only; no source/test/config/public-audit change |
| Secret/private-identifier scan of seven documents | 0 hits for token/private-key/WeChat/private-profile patterns |
| `git check-ignore --no-index --stdin -z` using UTF-8 NUL-delimited real paths | exit 0; 22,259 files ignored, 0 unignored |
| `git ls-files` for private roots/media/weights/secrets | 0 tracked files |
| Read-only before/after SHA-256 inventory of existing outputs/local_data files | 22,259 before and after, aggregate inventories identical |
| Local `main` and `origin/main` refs | both remain `8a03e288fb814d81b0a8e255b8004dbc4d0efb02` |

The initial newline-oriented ignore comparison was inconclusive because native
path rendering did not compare as raw paths; it is not used as privacy evidence.
The NUL/UTF-8 recheck above compares actual path identities, without altering
ignore configuration, private files or evidence. Hash inventories were kept in
tool memory; no new private inventory files or generated artifacts were written.
Source recordings, old Development Lock, original FAIL and frozen Review Packet
are included in the unchanged full private inventory. These hashes establish
unchanged bytes during this task, not source authenticity or human-label accuracy.

The primary agent read the full implementation plan and self-checked spec
coverage, step actionability, cross-task types/signatures, all five Review Focus
test ownerships and proportion (plan 268 lines / amended spec 281 lines).
Two scoped read-only agents inventoried reusable APIs and checked the amended
Scale Gate/status wording; no actionable contradiction remained. This is local
planning assistance, not a substitute for the future ChatGPT plan review.

Historical 680 passed / 2 skipped belongs to the paused data-preparation
checkpoint, not a fresh run here.

## Not Run and limitations

- Full pytest: Not Run, documentation-only changes; no executable behavior changed.
- New multiclass tests/readiness/Scale Coverage implementation: Not Run/not built.
- Private media/GT review, data preparation/freezes: Not Run, out of this scope.
- Model installation, weights, training, inference, GPU/ONNX/ncnn/mobile tests: Not Run.
- Acceptance is of a design, not recognition success, data readiness or environment qualification.
- Human completeness/identity/provenance remain attestations, not hash-authenticated truths.
- The new implementation plan still requires independent review and explicit phase approval.

## Git boundary

Branch: `codex/module-2b2a-taxonomy-audit`. This task begins at `cec8abc...`.
Accepted local main and origin/main remain
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`; no push/merge is performed.
Final local documentation commit and clean/dirty status are verified from Git at
handoff, not a self-referential commit claim in this document.
