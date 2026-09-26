# Repository Instructions

These instructions apply to the entire repository.

## Priority

Work must favor correctness, account safety, user experience, maintainability,
simplicity, and verifiable evidence. Do not increase scope or complexity merely
because a technique may be useful later.

## Context Loading

Before meaningful work, read in this order:

1. `AGENTS.md`
2. `PROJECT.md`
3. `docs/CURRENT_STATE.md`
4. relevant entries in `docs/DECISIONS.md`
5. `docs/DEVELOPMENT_PLAN.md`
6. relevant code, tests, configuration, and Git state

The repository is long-term memory; chat is temporary. When documentation and
implementation conflict, inspect executable reality and repair the documentation
within the authorized task.

## Current Safety Rules

- Only user-provided recordings and approved test footage may be analyzed.
- Do not modify, hook, inject into, or read memory from Clash Royale.
- Do not intercept game traffic or emulate its protocol.
- Do not use AccessibilityService or synthetic input to control the game.
- Do not create bots, automated card placement, or strategy execution.
- Do not implement live online-match analysis or overlays unless a future task
  explicitly passes the policy and project approval gate.
- Never describe a calculated elixir value as exact hidden game state.

## Architecture Rules

- Keep frame processing, detection, deployment tracking, and game-state
  inference as separate responsibilities.
- Visual detections are observations, not confirmed card-play events.
- Only confirmed `OpponentCardPlayed` events may update card history, cycle, or
  elixir estimates.
- Prefer local processing. Add a network or cloud dependency only for a proven
  requirement and isolate it from core functionality.
- Do not lock the project to a model runtime before the offline proof of concept
  provides evidence.

## Module Discipline

- Execute one module from `docs/DEVELOPMENT_PLAN.md` at a time.
- Do not begin the next module before the current module has been verified and
  reported for user acceptance.
- Keep every module independently understandable, testable, and committable.
- Update `docs/CURRENT_STATE.md` after verified material progress.
- Record only durable architectural or product decisions in
  `docs/DECISIONS.md`.

## Data and Repository Hygiene

- Do not commit match recordings, extracted gameplay frames, generated datasets,
  model weights, credentials, signing keys, or personal account information.
- Verify the license and provenance of code, models, datasets, and assets before
  adding them.
- Do not copy source from a repository without a compatible explicit license.
- Avoid unrelated formatting, dependency upgrades, refactors, and generated
  artifacts.

## Git Workflow

- Use a focused feature branch for each module; do not develop directly on
  `main`.
- Use Conventional Commits with a scope or description matching the module.
- Before committing, inspect status and diff, run proportionate checks, and scan
  for secrets and accidental binary/data files.
- Push only the current feature branch when authorized. Never force-push, merge
  `main`, delete remote branches, or publish a release without explicit approval.

## Completion Evidence

Do not claim a module is complete without reporting:

1. implemented behavior or documents;
2. added, modified, and deleted files;
3. data/storage changes, if any;
4. checks actually run and checks not run;
5. known issues and unresolved risks;
6. branch, commit, and push status;
7. the next planned module.
