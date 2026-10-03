# Decisions

This document records durable product and architecture decisions. New entries
must describe accepted reality rather than speculative preferences.

## 2026-09-26 — Start With Offline Recorded Video

### Decision

The first executable stages will analyze user-provided recordings and test
footage. Live online-match capture and overlays are not authorized current scope.

### Context

The intended product may eventually analyze an Android screen, but the user has
made account safety a highest-priority constraint. The technical feasibility of
reliable deployment recognition is also unproven.

### Alternatives

- Begin directly with live Android MediaProjection capture.
- Build a complete Android interface before validating recognition.
- Validate the difficult recognition path using recorded input.

### Reason

Recorded input isolates the main technical risk without introducing live-match
policy exposure, overlay complexity, or device-capture variability.

### Consequences

- Modules 1 through 6 operate offline.
- Module 7 requires explicit Supercell permission covering specific live tool
  behavior, version, and usage context, plus project approval.
- Module 8 cannot begin before Module 7 is approved and verified.

## 2026-09-26 — Prohibit Game Interaction and Automation

### Decision

The project will not modify or control Clash Royale. APK modification, hooking,
injection, memory access, traffic interception, protocol emulation,
AccessibilityService control, synthetic input, bots, and automatic card placement
are permanently outside the project boundary.

### Context

These capabilities are unnecessary for visual match analysis and conflict with
the project's safety requirements.

### Alternatives

- Reuse automation capabilities from reference projects.
- Restrict the system to passive visual input and analysis.

### Reason

Passive analysis is the smallest architecture that addresses the intended
problem while reducing technical, privacy, and account risk.

### Consequences

- Reference-project automation code must not be imported.
- Android permissions and services must remain limited to approved passive needs.

## 2026-09-26 — Separate Detection From Confirmed Game Events

### Decision

The visual detector will emit observations. A separate deployment tracker will
use temporal and spatial evidence to emit confirmed `OpponentCardPlayed` events.
Only confirmed events may update history, cycle, or elixir state.

### Context

One deployed unit remains visible across many frames. Treating every detection
as a card play would repeatedly count the same deployment.

### Alternatives

- Let the model update game-state trackers directly.
- Confirm and deduplicate observations in a dedicated domain component.

### Reason

The dedicated event boundary makes false positives, repeated detections, and
uncertainty testable without coupling them to game-state calculations.

### Consequences

- Module 2 proves limited detection only.
- Module 3 owns confirmation and deduplication.
- Cycle and elixir work cannot consume raw detections.

## 2026-09-26 — Defer the Model Runtime Choice

### Decision

YOLO, ONNX Runtime, TensorFlow Lite, and other candidates remain unselected until
offline experiments provide accuracy, performance, model-size, and Android
deployment evidence.

### Context

No representative recording, trained model, benchmark, or Android performance
measurement currently exists.

### Alternatives

- Select a framework during project bootstrap.
- Allow the proof of concept to establish requirements first.

### Reason

Early lock-in would add dependencies without reducing the current uncertainty.

### Consequences

- Module 1 adds no machine-learning runtime.
- A later decision must record measured tradeoffs before standardizing a runtime.

## 2026-09-26 — Use Local-First Core Processing

### Decision

Core video analysis and future supported device analysis will run locally. A
server, account, or cloud database is not a default dependency.

### Context

The initial product serves one user, processes local media, and has no confirmed
collaboration or multi-device requirement.

### Alternatives

- Upload video to a hosted inference service.
- Keep the core pipeline local and add online capabilities only when necessary.

### Reason

Local processing reduces privacy exposure, latency, operating cost, and failure
dependencies while satisfying the current use case.

### Consequences

- Offline operation is an acceptance condition for core modules.
- Any future online capability must be optional and justified independently.

## 2026-09-26 — Treat External Code and Data as Provenance-Gated

### Decision

No external source, model, dataset, recording, or game asset enters the project
until its origin, license, and intended use have been reviewed. Source from an
unlicensed repository must not be copied.

### Context

The reference repositories differ in licensing, and code licenses do not
automatically grant redistribution rights for game assets or datasets.

### Alternatives

- Copy useful implementations first and resolve licensing later.
- Reimplement concepts cleanly and import only verified compatible material.

### Reason

Up-front provenance prevents the proof of concept from accumulating legal and
maintenance debt that would block later distribution.

### Consequences

- CR Vision is an algorithmic reference only while it lacks a declared license.
- Every external artifact requires an evidence-backed review before inclusion.

## 2026-10-03 — Require Specific Official Permission for Live Features

### Decision

Live online-match analysis and HUD remain Gated and disabled unless explicit
Supercell permission covers the exact behavior, version, and usage context.
Passive capture, local execution, alternate accounts, training-ground tests,
and user risk acceptance cannot substitute for permission. Even with permission,
reassess scope and never promise zero ban risk.

### Context

The Module 0 review found that risk acceptance could bypass the intended
account-safety constraint. This entry supersedes that weaker gate. No official
permission has been obtained or asserted.

### Alternatives

- Allow a user to accept remaining risk.
- Require explicit, applicable official permission for live features.

### Reason

The user's requirement places account safety above live functionality.

### Consequences

Offline-file modules may continue. This module never accesses a running game.
Live functionality remains closed; project approval is still necessary but
cannot replace official permission.

## 2026-10-03 — Python/PyAV Offline Experiment and Presentation-Time Contract

### Decision

Use a small Python 3.12 CLI with PyAV, Pillow, and pytest for Module 1. Select
frames by actual PTS/time_base normalized to the first display frame. Use exact
fraction arithmetic and choose the first frame at or after a target within an
inclusive 100ms window. Scan sequentially with bounded frame memory.

### Context

The user specifically authorized this Windows experiment. Variable frame rates
and nonzero starting PTS make frame-index/average-FPS calculation unreliable.

### Alternatives

- Estimate frame times from frame indices and average FPS.
- Use actual decoded display timestamps.
- Build an Android application before verifying recorded-video behavior.

### Reason

The selected approach makes temporal correctness reproducible using synthetic
media while remaining independent of Android, game control, and model choices.

### Consequences

Python is an explicitly authorized experiment, not a replacement for a future
app stack. Core app business logic/storage are not implemented here. No database
or inference framework is added. Keep original videos untouched and generated
media ignored. Missing timestamps fail explicitly; partial misses return nonzero.
Runtime versions are pinned in the tool configuration and test requirements.
Representative user-recording acceptance remains required after synthetic tests.
