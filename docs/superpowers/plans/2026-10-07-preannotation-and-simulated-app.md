# Offline pre-annotation and simulated App implementation plan

> For agentic workers: implement the two tasks with subagent-driven-development,
> scoped review, and test-driven-development. The user already authorized design
> followed directly by implementation; no further plan-approval pause is needed.

**Goal:** deliver a local proposal→human-correction workflow and a mock-only App.
**Architecture:** additive Python/browser review bundle plus independent typed
React event consumer; no integration with live gameplay or training.
**Tech stack:** existing Python/PyAV/Pillow, self-contained HTML/JS; React,
TypeScript, Vite, Tailwind, Capacitor, local Node test/build tooling.
**Spec:** [design](../specs/2026-10-07-preannotation-and-simulated-app-design.md).

## Global Constraints

- Predictions and human GT are separate. Unknown, rejected proposals and unmarked
  areas do not become Negative. Class coverage requires explicit human review.
- Original recording order; natural_match_02 stays training-ineligible/truncated.
- 10–20 classes is a target only; no training, old-gate rewrite or new Dataset Lock.
- Preserve all old locks, Attempt01/02, KataCR benchmark and existing environments.
- App accepts only mock events; no detector/game connection, capture, cross-app
  overlay permission, Accessibility, input control, cycle/evolution/elixir logic.
- Local bundled runtime; private artifacts ignored; no push or main merge.

## Task 1: local proposal / human correction tool

**Owned paths:** `tools/preannotation/` only.

- [x] RED: contract tests for deterministic IDs, class-specific coverage, all five
  edit operations, bounds, unknown/reject protection, group continuity, no false
  human provenance, immutable imports and original-order/truncated inventory.
- [x] GREEN: implement a strict versioned proposal/human-return contract, KataCR
  adapter, source-PTS frame binding/export, local browser reviewer and exclusive
  revision save/import. Keep functionality separate from old readiness/locks.
- [x] Add CLI prepare/validate/import/demo operations, self-contained local review
  page, and minimal README. Use existing dependencies; no model installation.
- [x] Run focused tests and synthetic correction round-trip; record exact results
  in ignored `outputs/milestone1/task-a-report.md`. Do not commit: parent owns Git.

## Task 2: simulated React / Capacitor App

**Owned paths:** `app/` only. Parent owns root ignore and project documentation.

- [x] RED: typed mock event consumer tests for validation, idempotency, distinct
  cards, eight-slot limit, reset and future-source rejection.
- [x] GREEN: implement decoupled interface/reducer, fixed mock events Witch and
  Balloon, accessible single-screen UI and App-internal HUD. No persisted data.
- [x] Pin minimal dependencies and package lock, generate/sync Android source;
  record package versions/licenses and local build-tool availability.
- [x] Run tests, type check and production build; record evidence in ignored
  `outputs/milestone1/task-b-report.md`. Do not commit: parent owns Git.

## Integration and final verification

- [x] Review both implementation diffs; fix concrete issues via task implementers.
- [x] Build a new real match-01 pending review bundle from existing predictions;
  exercise synthetic correction import, inspect browser review and mock App.
- [x] Save actual mobile screenshots and test the play/reset/error flows.
- [x] Full offline regression, old/new dependency checks, diff/privacy checks and
  historical file/environment protection. No real inference rerun or training.
- [x] Update CURRENT_STATE, DECISIONS, DEVELOPMENT_PLAN, README and verification
  evidence. Commit public sources only to the focused branch; do not push/merge.
- [x] Deliver two separate results and accurate Android build status; stop.
