# Module 2B-2 Data Preparation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** prepare and freeze independently counted, individually annotated local
development data for the learned minion detector, or report an honest data gap.

**Architecture:** add a separate multi-match/unit-box dataset layer over the
unchanged frame/index pipeline. Reference the immutable 2A2 lock; do not use its
single-match readiness or group-box schema as the new training-data contract.

**Tech Stack:** existing Python 3.12+, PyAV, Pillow, pytest; standard-library
Tkinter/JSON/hashlib. No new runtime dependency in this slice.

**Spec:** [Data preparation design](../specs/2026-10-05-module-2b2-data-preparation-design.md), a scoped implementation slice of the user's supplied Learned Minion Visual Detector design.

**Status:** user approved on 2026-10-05; task-by-task implementation and review
authorized for this data-only slice. No model training or publication. Branch:
`codex/module-2b2-data-preparation`; baseline
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.

## Global Constraints

- Minimum: 4 independent target-positive natural matches AND 8 confirmed opponent
  ordinary `minions/normal` deployments. Do not count frames, boxes or augmentation.
- Keep old Development Lock, group boxes, original sources and 2B-1 FAIL unchanged.
- Keep Module 1 and existing `prepare / validate / review` unchanged.
- Preserve original intake order; difficulty cannot justify rejecting a match.
- Full segment is exactly `0..last_frame_seconds` under user-confirmed completeness;
  `terminal_result_screen_present=false` remains legal.
- Unknown, other-form, unreviewed content and minions of other sources are never
  empty-box negatives. Unit visual class and target-card semantics stay separate.
- Training frames use visible-extent unit boxes with complete frame-level review.
- No torch/torchvision installation, weights, training, inference, Model Lock,
  blind tests, Module 3, Android/HUD, cloud uploads, push or main integration.
- Real data/revisions/new locks live only below ignored `outputs/` or `local_data/`;
  synthetic fixtures and redacted aggregates alone may enter Git.

## Review Focus

- Reencoded copies or renamed deployments must not manufacture matches/events.
- Unlabelled same-class units must not silently train as background.
- Sparse absent frames must not become certified time for FP/min.
- A copied lock or symlink/junction/path escape must not bypass exclusive versions.
- Metadata-only success must not conceal changed/missing pixels or annotations.

## File ownership

Create under `tools/offline_video/src/clash_tracker_video/`:

- `training_dataset_contract.py`: closed shapes, unit semantics and readiness.
- `training_dataset.py`: old-lock binding, deterministic folds, snapshots, freeze.
- `unit_annotation.py`: local Tk canvas; coordinate transforms and additive saves.
- `training_dataset_cli.py`: sanitized validate/freeze/validate-lock/annotate shell.

Create corresponding `test_training_dataset_contract.py`,
`test_training_dataset.py`, `test_unit_annotation.py`,
`test_training_dataset_cli.py`, and `training_dataset_fixtures.py` in the maintained
test directory. Add `docs/MODULE_2B2_DATASET_CONTRACT.md` and
`docs/VERIFICATION_M2B2_DATA.md`. Update README/CURRENT_STATE/DEVELOPMENT_PLAN/DECISIONS
only to reflect approved, verified progress. No old production/test/dependency file
needs changing. If a real blocking interface conflict requires it, stop and report.

### Task 1: Closed dataset draft, independent readiness and grouped folds

**Files:** new contract/fixture/test files listed above.

**Interfaces:** `validate_dataset_shape(draft: dict) -> None` raises EvidenceError;
`dataset_readiness(draft: dict) -> dict` returns derived validity/counts/reasons,
`training_data_ready`, and `evaluation_ready` separately;
`grouped_folds(draft: dict) -> list[dict]` returns deterministic per-match folds.
The new draft format uses the field families and semantics fixed in the spec;
write the closed field/type table in MODULE_2B2_DATASET_CONTRACT before consumers.

- [ ] Write failing synthetic tests: 4 positive matches/8 unique confirmed plays
  become training-data-ready; 3/8 and 4/7 do not; 4/8 without certified absent
  time remains evaluation-not-ready. Two IDs sharing the same spawn/frame/box
  evidence reject instead of increasing play count.
- [ ] Test a one-play new match is accepted; three unit boxes in each of four
  frames count one play, not twelve. Reencoded recordings keep one match.
- [ ] Test unknown/evolved/other-source/own-side observations remain visual
  records but do not increase ordinary-opponent target count or become negatives.
- [ ] Test unreviewed/missing unit boxes, duplicate annotation identities,
  invalid normalized boxes, NaN/Boolean numbers and unknown-negative overlaps.
- [ ] Test complete `0..last_frame` without result UI accepts; shortened start/end,
  incomplete or technically invalid sources reject.
- [ ] Test every recording/frame of an underlying match stays together in every
  fold; deterministic four- and five-match LOMO, no empty train split.
- [ ] Run the new test file to see the missing API failures; implement minimal
  validation/derived counts/folds and rerun it to green. No model imports.
- [ ] Review this independently testable contract; commit only if implementation
  approval includes committing, with `feat(dataset): add minion unit data contract`.

### Task 2: Media bindings and immutable Training Dataset Lock

**Files:** new training_dataset.py and its tests; reuse load_indexes, file_hash,
canonical_bytes and old load_lock without modifying them.

**Interfaces:** `bind_dataset(draft: dict, indexes: dict, development_lock: dict)
-> dict` validates checked evidence and derives a payload;
`make_dataset_lock(payload: dict) -> dict` creates a canonical envelope;
`validate_dataset_lock(lock: dict, development_lock: dict) -> None` checks its
digest/contract; `freeze_dataset(payload: dict, directory: Path) -> dict` writes
one exclusive version; `load_dataset_lock(path: Path, development_lock: dict,
indexes: dict) -> dict` rechecks declared on-disk bindings.

- [ ] Write failing tests for changed old-lock reference, PTS/dimensions/pixel/
  annotation conflicts, nonexistent frame references and label/image tampering.
- [ ] Test identical input gives identical bytes/digest; changing target, form,
  event identity, unknowns, reviewed absent ranges, unit box, intake order or split
  changes digest. New explicit UTC/version is not expected to preserve digest.
- [ ] Test duplicate version, renamed copies, symlink/junction escape, traversal,
  oversized JSON and partial-write failure; existing files must survive unchanged.
- [ ] Test freeze rejects not-ready drafts and loaded-lock checks do not accept a
  stored snapshot as proof that external images/labels still match.
- [ ] Implement the dedicated training_dataset envelope and immutable writer; do
  not extend old LOCK_TYPES or change old development/model/test-GT validation.
- [ ] Run new contract/lock tests plus existing test_experiment_lock.py and
  test_experiment_development.py; review and commit under the same approval rule.

### Task 3: Minimal local individual-unit annotation

**Files:** unit_annotation.py/test_unit_annotation.py.

**Interfaces:** `canvas_box_to_normalized(box: tuple[float,float,float,float],
image_size: tuple[int,int], display_rect: tuple[float,float,float,float])
-> list[float]`; `save_annotation_revision(document: dict, output: Path) -> Path`
validates then exclusively writes a new revision;
`launch_annotator(draft_path: Path, indexes: dict, output_directory: Path) -> None`
opens the local image canvas. No service or model prediction.

- [ ] Write failing tests for letterboxed/downscaled images, reverse-direction
  dragging, outside-image/zero-area boxes, multiple same-frame units and stable
  source frame/deployment bindings. Boxes refer to original rotated pixels.
- [ ] Test pending review cannot become a negative by clearing boxes; complete
  positive review must retain all known units and explicit source/form uncertainty.
- [ ] Test saves are additive, originals are unchanged, errors are sanitized and
  destination stays in ignored roots; Tk import creates no GUI during unit tests.
- [ ] Implement image/drag/delete-unsaved-box/metadata/review/save/next only, using
  existing Pillow and Tkinter. No auto boxes, recommendations from model or cloud.
- [ ] Run geometry/save tests and manually smoke-test the window using synthetic
  images only; record headless limitations honestly if GUI unavailable.
- [ ] Review the tool and commit under the same approval rule.

### Task 4: CLI and original-order real intake, then data-gate stop

**Files:** training_dataset_cli.py/test_training_dataset_cli.py; dataset contract
and verification docs plus scoped durable state updates.

**Interfaces:** `main(argv: list[str] | None = None) -> int`; subcommands
`validate-dataset`, `freeze-dataset`, `validate-dataset-lock`, `annotate`.
Validation: 0 valid/ready, 3 valid/not-ready, 2 invalid/I/O. Freeze: 0 frozen,
2 invalid/not-ready/duplicate. A frozen result does not authorize training.

- [ ] Write failing CLI tests for ready/not-ready/invalid inputs and sanitized
  errors; reject unknown flags/fields, protect existing files and old CLI semantics.
- [ ] Implement these thin commands over Tasks 1–3 without touching legacy CLIs.
- [ ] Snapshot an explicit inventory of every previously protected source,
  evidence, lock and 2B-1 result before approved real work; do not disclose paths or
  per-file hashes in public documents. Find original intake from its existing
  manifest, not alphabetical filenames; reuse existing evidence where valid.
- [ ] Inspect retained sources strictly in that order. Record actual review
  method/provenance; use confirmed coarse times for new exact PTS frame exports
  only where needed, in new ignored locations. Unreviewed absence stays unknown.
- [ ] Request only unresolved source/card/form/deployment/completeness facts from
  the user. Ordinary new matches may have one target play; keep difficult samples.
  Do not declare the remaining three recordings target-positive without review.
- [ ] New unit annotations may reference the old six images, but old group labels
  and lock stay byte-identical. Approx. four spaced frames/event; never force
  three boxes where only one/two are identifiable. Freeze only reviewed data.
- [ ] If less than 4 target-positive matches or 8 reviewed independent plays,
  report actual counts and missing matches/plays; give an ignored intake folder
  and recording instructions, preserve evidence, and stop waiting for recordings.
- [ ] If ready, create a new Training Dataset Lock, re-load with checked external
  bindings, report dataset version/digest and honest evaluation coverage, then stop
  for acceptance. Do not install/download/train just because this gate passes.
- [ ] Re-run all maintained tests:
  `.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short`.
  The explicit path includes all maintained tests and avoids ignored Review Packet
  copies; do not alter/discard old tests to avoid collection or assertions.
- [ ] Run `.\.venv\Scripts\python.exe -m pip check` and `git diff --check`.
  Inspect complete status/diff, tracked files, secrets and ignored-data roots.
  Compare all protected hashes; no overwritten/deleted original data permitted.
- [ ] Update verification and current state with only actual run outcomes,
  match/play/frame/box counts separately, unknown coverage and unresolved facts.
  No detector accuracy claim. Commit only approved source/tests/docs; no push,
  merge, PR or Release. Stop with a phase report, not overall 2B-2 completion.

## Plan self-review and execution handoff

This plan covers only dataset expansion, unit annotation, readiness and freeze.
Training/runtime/weights, visual aggregation, CV metrics/threshold selection,
Model Lock and prospective blind testing each require their later approved plan.
Sparse labels are not full-timeline evaluation evidence; missing negative-time
coverage stays explicit. Media/code license checks for a model are not passed.

Recommended execution: **subagent-driven**, with separate contract, lock and
annotation reviews and final whole-branch verification. These checks supplement,
not replace, the user's ChatGPT independent acceptance. No model switching needed.
The user approved this design/plan and subagent-driven execution on 2026-10-05.
