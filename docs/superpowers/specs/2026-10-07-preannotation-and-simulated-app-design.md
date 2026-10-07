# Milestone 1 — Offline human correction and simulated App

Status: implementation authorized by the user on 2026-10-07. This is not
authorization for training, live game capture, or a game HUD.

## Task A: pre-annotation / human correction

Goal: turn the retained KataCR benchmark predictions into a usable local
proposal queue, with human correction recorded separately from predictions.

Use a new, isolated `tools/preannotation/` tool. Reuse the existing official-source
benchmark predictions first, in original recording order. Do not rerun or edit
the benchmark. New frame exports, if needed for viewing proposals, go to a new
ignored output directory and use exact source PTS, not annotated screenshots.
Future prediction imports use the same adapter; no training is part of this tool.

The private bundle contains an immutable source/proposal manifest, source images,
a self-contained local browser review page, and a human-return template. The
review page supports accept/reject, class relabel, bbox correction, manual missing
boxes, owner/form/origin, appearance identity, visibility and uncertainty. Save
human decisions as a separate return file; validate/import into a new exclusive
revision, never overwrite predictions or older revisions.

Stable proposal identity binds prediction-file SHA, recording, exact PTS and row.
Stable frame identity binds recording and PTS/time_base. Preserve raw teacher
label, score, owner hypothesis and bbox alongside human fields. Teacher owner is
not human owner. Every proposal begins pending. A class's exhaustive coverage is
a separate explicit human decision; acceptance alone cannot establish coverage.
Rejected/unknown/unlabeled regions must stay unresolved/ignored, not negatives.
Negative evidence requires explicit class-specific exhaustive human confirmation
with no positive or unresolved region for that class. No deployment independence
may be inferred merely from multiple frames or multiple boxes.

The recording inventory keeps original order 01,02,03,04. Match 02 is truncated,
training excluded, preserved, and cannot contribute negative training evidence.
10–20 confirmed visual classes is a target, not a readiness requirement. GT
form may remain unknown. Spawned visual entities do not imply card deployments.
Human-return provenance identifies the actual reviewer; synthetic demonstrations
are explicitly synthetic and cannot be imported as real reviewed GT.

No new Training Dataset Lock or model is produced. All old contracts, old gates,
locks, Attempt01/02 and benchmark outputs remain unchanged. Private media,
predictions, decisions and bundle files stay ignored. The demo starts with match
01; later matches are processed in order, not selected for easy categories.

## Task B: simulated App

Goal: a runnable React/TypeScript/Capacitor prototype with a small App-internal
HUD driven by mock Witch and Balloon events, producing `已发现 2/8`.

Use Vite, bundled local assets and restrained CSS/Tailwind styling. A typed
`OpponentCardPlayed` interface carries `eventId`, `cardId`, `timestamp`,
`confidence`, and `source`. Its consumer does not import any visual implementation.
For this prototype only `source=mock` is accepted; observation→confirmed event
conversion is not implemented. Validate inputs, deduplicate event identity, count
unique known cards, and cap discovered slots at eight with explicit overflow.
Use in-memory state: there is no persistent user database yet, so no SQLite
migration or localStorage is needed.

Provide play/advance/reset controls, event history, eight discovery slots, a clear
mock-data label and a small non-interactive HUD inside the page. No card-cycle,
evolution or elixir calculation. No game art is required. A design reference is
only a visual guide, not a screenshot of a verified implementation.

Generate/sync a Capacitor Android project. Runtime assets must be local: no remote
`server.url`. No SYSTEM_ALERT_WINDOW, MediaProjection, Accessibility service,
detector bridge, real game connection, synthetic input or cross-app UI. Future
native Android capture/inference is separately gated and not constrained to Web.
Verify Android tooling and attempt build only if the required local tools exist;
report missing JDK/SDK honestly rather than install system tools silently.

## Acceptance / verification

- Task A: synthetic correction round-trip demonstrates all five actions; invalid
  returns are rejected; real match-01 proposal bundle is viewable and remains
  pending human review; class coverage/unknown/grouping invariants are tested.
- Task B: tests prove mock event validation/idempotency/count/reset; TypeScript,
  tests and production web build pass; actual mobile browser interaction and
  screenshots are checked; Capacitor sync and Android environment status reported.
- Existing offline regression, dependency checks, diff/privacy checks and hashes
  of historical private artifacts pass. No training, new model download, push,
  main merge, Module 3 or live game HUD.

## Storage and task boundaries

Public: source, tests, dependency lock, Android source project and documentation.
Private: new bundles/review returns/source frames/screenshots/protection receipts
under ignored `outputs/milestone1/`. No existing output is removed or replaced.
Two implementation tasks have disjoint paths and can run in parallel; the parent
owns integration, final verification, documentation and Git operations.
