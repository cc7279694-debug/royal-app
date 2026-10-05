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

## 2026-10-03 — Evidence Preparation Before Single-Card Detection

Status: retained for stage/event separation and historical 2A1 behavior.
Its first-experiment data thresholds are superseded by the 2026-10-04 Module 2A2
decision below; do not reuse the old 4/6/2 experiment gate for new 2A2 work.

### Decision

The user explicitly split Module 2 into 2A (manual evidence/annotations/sufficiency)
and 2B (one-card visual Observations). Only Module 3 emits OpponentCardPlayed.
Target selection requires four distinct reviewed opponent deployments in current
footage; Hog Rider is not predefined. Before 2B require two independent complete
matches, six total verified plays, a whole held-out match with two plays, reviewed
non-match negatives and a locked split. Same underlying match/re-recording frames
cannot cross development and test. These minima do not certify reliability.

### Context

Module 1 has been accepted. A single real recording proves extraction, not model
generalization. Random frame splits would leak nearly identical match evidence.
The current task authorizes planning only, plus the accepted branch's main merge.

### Alternatives

- Train immediately on frames randomly split from one recording.
- Establish evidence and independent whole-match boundaries before an experiment.

### Reason

Manual evidence and pre-registered isolation make the next experiment verifiable
without adding a model, GUI or live-game risk prematurely.

### Consequences

Module 2A implementation remains subject to separate user approval. Proposed
target/tool/evaluation details in the design are recommendations, not decisions
accepted by this entry. Real footage, hashes and labels remain local and ignored.
External datasets/models remain separately provenance-gated; no download approved.

## 2026-10-03 — Lightweight Key Evidence Before Independent Split Infrastructure

Historical scope: its 2A1 constraints remain valid. Its deferral of 2A2 until
a second recording is superseded by the separately approved 2026-10-04 design.

### Decision

The user's review directs 2A1 to prepare current-recording evidence only, with
prepare/validate/review commands, full manual deployment/visibility/negative
interval review and 3–5 distinct original key-frame boxes per verified play.
No dense 5FPS manual annotation inventory. Independence allocation, Evaluation
Protocol, canonical digest, split lock and freeze are deferred to 2A2 after at
least a second independent complete recording and separate design/approval.

### Context

The prior draft required every 5FPS held-out/non-match frame to be reviewed and
planned freeze infrastructure despite having only one observed match. Neither
implementation nor final annotations exist; this task authorizes document revision.

### Alternatives

- Build the original dense-label/freeze system immediately.
- Complete a lightweight current-recording stage, then approve independent-data
  preparation when a second match exists.

### Reason

The smaller stage matches an individual PoC's workload without lowering the
independent full-match isolation, data/provenance or live-safety gates.

### Consequences

2A1 is not implemented; 2A2 is unapproved. Inferno Dragon stays a pending-review
candidate, and one match remains insufficient for 2B. Future box metrics cover
only the disclosed key-frame subset; temporal coverage/FP metrics use complete
reviewed intervals, not implicitly negative unlabeled frames.
Ordinary intervals stay half-open, with a closed end only for terminal negatives
ending at the exact last actual frame. Public documents allow anonymous candidate/
count/gate aggregates; actual timestamps, paths, hashes, boxes, media and labels
stay local. Prior commits are not rewritten. Proposed model/protocol details are
not made accepted technical decisions by this entry.

## 2026-10-04 — Independent Experiment Locks and Prospective Blind Testing

### Decision

The user approved Module 2A2 implementation: a new natural development replay,
human target selection, at least two clear independent deployments of one known
card/form, immutable versioned Development Data Lock, later Model Lock, and a
separate-session Test Ground Truth Lock before any test inference. The first
qualifying independent natural test match needs at least one locked-form play.
The old Inferno Dragon recording is historical regression evidence only.

### Context

The accepted 2A1 tools establish evidence consistency, not model readiness.
Freezing the model before test exposure prevents test-driven target/parameter
selection. The user explicitly approved building infrastructure before supplying
new development footage. Real Module 2A2 execution stops at DEV_LOCKED; absent
that footage it stops WAITING_FOR_DEVELOPMENT_MATCH, without fabricated locks.

### Alternatives

- Require all development and test labels before developing a model.
- Prospectively freeze development, then model, then independent blind labels.

### Reason

The second flow preserves a small one-development/one-test PoC while protecting
independence and avoiding parameter tuning on test pixels or ground truth.

### Consequences

- Supersedes the old first-experiment 4/6/2 thresholds and pre-2B test-label
  requirement only; existing 2A1 four-play candidate/review behavior stays intact.
- Add a separate Python experiment layer; no database or new dependency.
- normal/evolved/unknown are separate. Other/unknown forms and timeline gaps
  are not negatives. Evolution is manual ground truth, not an automatic counter.
- Split identity is the underlying match, not the recording file or its hash.
- Digests and exclusive creation detect inconsistencies, not dishonest human
  attestations, coherent forgery or source-video authenticity.
- Module 2B still requires separate acceptance, planning and explicit approval.
  No training, inference, Android or live feature is authorized by this decision.

## 2026-10-04 — User-Confirmed Completeness and Actual File-End Boundary

### Decision

The user explicitly replaces the result-screen requirement: a complete replay is
one the user confirms covers the full natural match. Its last actual decoded
frame is the valid evaluable end. Record completion_attestation=user_confirmed
and terminal_result_screen_present separately; false screen presence is not
incompleteness or a Development Data Freeze veto.

### Context

The user reconfirms all four supplied recordings and authorizes continuing in
their original intake order, starting with the first usable input and reusing its
existing human rough review. This supersedes the visible-result-based exclusions
in the earlier boundary-check documents, not their factual image observations.
Historical exclusions, files and reviews are retained rather than rewritten.

### Alternatives

- Require a visible victory/defeat/result screen before any development evidence.
- Use explicit human whole-match coverage plus technical integrity and actual PTS.

### Reason

Missing ending UI does not establish missing battle content. Human confirmation
is an auditable declaration, not software-certified source authenticity.

### Consequences

- Still reject damaged or undecodable files, obvious mid-match truncation, missing
  key battle intervals or explicit human incompleteness. Do not hide such conflicts
  behind an attestation; absence of result UI alone is not one.
- Preserve strict report/index/PNG/PTS checks, whole-file human review, one shared
  complete segment and >=2 independent clear verified deployments of one known form.
- Ordinary intervals remain half-open; retain explicit terminal uncertainty when
  needed. The file end or missing result screen is never an automatic negative.
- Retain the existing v1 evidence/extractor and prior immutable records. Additive
  development identity metadata can be bound by the existing digest without a
  new database, dependency or lock format.
- No result-screen-driven re-recording is required for these four inputs. Do not
  filter or reorder them by card/difficulty/quality. Stop at a truthful Development
  Data Lock or unresolved evidence blocker; Module 2B remains separately gated.

## 2026-10-05 — Development-only Reference Template Baseline

### Decision

The user separately authorizes Module 2B-1: fixed multiscale OpenCV template
matching on the existing two ordinary Minions deployments. ORB is diagnostic,
never a ranking/gate weight. Both held-out deployment folds must meet the fixed
Top5/2s temporal search criterion before a real detector artifact/Model Lock may
be created. Failure is a valid result and stops, not automatic training or tuning.

### Context

Two independent plays and six group-box frames are too little evidence to claim
generalization. A simple reference baseline tests feasibility before a separately
planned neural route. The full approved protocol and a priori settings are in
[MODULE_2B1_PROTOCOL.md](MODULE_2B1_PROTOCOL.md).

### Alternatives

- Train a detector immediately on the six images.
- Search for each deployment using only the other deployment's references.

### Reason

The second approach is transparent, preserves frozen evidence, exposes self-match
failure and leaves independent-match testing untouched.

### Consequences

- Scanner/ranker do not receive hidden GT. Freeze both rankings before evaluation.
- First support and highest peak are different fields. Continuous support uses
  transitive event grouping; >2s gaps can still split one play, a disclosed limit.
- Unknown intervals/forms never tune thresholds or establish false-positive rates.
- A temporal match is a development proxy, not verified card identity/ownership,
  OpponentCardPlayed, cross-match reliability or permission for live use.
- Add only optional pinned headless OpenCV plus its NumPy dependency; no neural
  weights/framework, database, cloud runtime or Android dependency.
- An additive closed Model Lock artifact variant preserves legacy v1 contracts.
  Detector JSON hashes are actual canonical file hashes, not imaginary model files.
- Freeze code/settings before the first real scan. Preserve all original evidence.
  No independent test, 2B-2, Module 3, push or main integration is implied.
