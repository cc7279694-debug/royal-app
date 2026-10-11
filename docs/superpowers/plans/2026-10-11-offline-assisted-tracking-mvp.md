# Offline Assisted Card Tracking MVP Implementation Plan

> **For agentic workers:** Use subagent-driven development for the isolated exporter and App tasks; verify their shared contract before integration. Steps use checkbox syntax.

**Goal:** Let a user inspect real detector-derived card candidates and locally confirm a deduplicated opponent deck, without drawing boxes.

**Architecture:** Export the existing frozen detector replay into an immutable, private JSON packet with source-bound screenshots. A separate App review state projects only user-confirmed opponent cards; it never manufactures formal engine events or training GT.

**Tech Stack:** Existing Python/PyAV/Pillow tools and React/TypeScript/Capacitor; no new dependencies.

**Spec:** The user's 2026-10-11 authorization, bounded by the requirements below. This is an implementation contract, not a new model or product architecture.

## Global Constraints

- Preserve formal Module 3B, all historical GT/locks/scoring, detector predictions and failed runs.
- No training, live capture, game connection, input control, cross-app HUD, public media, push, merge or release.
- The three accepted geometry suggestions are assistant-reviewed provisional geometry, not pixel Human GT; the other four remain unknown.
- A candidate is not a confirmed play. Screenshot review of a card/owner does not prove an exact deployment timestamp.
- Imports always begin pending. Rejection, unknown and omitted observations do not become Negative.
- Mock and Recorded Oracle remain separate and usable; do not relax their existing event contracts.
- Review is session-only; closing or reimporting resets decisions, explicitly stated in the interface. No localStorage business data.
- Unsupported cards require unknown/manual handling, not invented automatic mappings.

## Review Focus

- Imported confirmation claims must be rejected rather than populating the deck.
- Duplicate candidates of one card must retain separate review records but only one deck slot.
- Unknown/own owners and unknown card mappings must not silently enter the opponent deck.
- Embedded evidence must reject external URLs, SVG, oversized payloads and invalid geometry.
- An asynchronous import after a mode switch must not overwrite the current review.

## Task 1: Geometry closure and frozen input protection

**Files:** New private closure under `outputs/offline-assisted-tracking/`; current-state and durable decisions updated after verification.

- [x] Bind the existing precise snapshot, geometry draft and seven display items by SHA and original IDs.
- [x] Record FC06 TO017 and GB07 6.018/6.676 as assistant-reviewed provisional geometry; keep the other four unknown.
- [x] Verify zero pixel-human-confirmed boxes, new training labels, Negative or confirmed card plays.
- [x] Protect the source media, locks, predictions, replay, formal engine, dependencies and native permission/configuration files.

## Task 2: Real detector candidate export

**Files:** `tools/assisted_tracking/` implementation and synthetic tests.

**Interface:** `offline_assisted_candidates_v1`, shared with Task 3; source hashes, original engine candidate IDs/observation IDs and actual PTS-bound JPEG evidence.

- [x] Write and observe failing synthetic tests before implementation.
- [x] Select all supported opponent STRONG/MEDIUM candidates from one frozen real replay, never from GT windows. Report every exclusion count.
- [x] Use first/middle/last actual candidate observation frames, native-size JPEGs and unverified detector boxes. Confidence is the maximum detector observation score, not calibrated event confidence.
- [x] Validate input artifact/hash/source consistency, packet references, geometry and size limits; never overwrite outputs.
- [x] Export the real first-match packet and a private contact sheet. Review actual evidence before declaring the list useful.

## Task 3: App review mode

**Files:** `app/src/assisted/`, `app/src/ui/AssistedReview.tsx`, minimal existing App/style/card-label integration, tests and App instructions.

**Interface:** Consume exactly Task 2's versioned packet; review decisions remain separate from immutable candidates and from `OpponentCardPlayed`.

- [x] Test parser limits, duplicates/orphan references, image restrictions and invalid fields.
- [x] Test confirm/exclude/correct/undo/manual handling, owner guard, deck dedup, overflow, reset and separate Mock/Recorded modes.
- [x] Implement the smallest mobile-friendly import, evidence and review flow; no new native permissions or persistence layer.
- [x] Run full App tests, typecheck/build and rendered workflow checks with the real private packet and synthetic error input.

## Task 4: End-to-end verification and acceptance handoff

**Files:** Current state, development plan, decisions and a historical checkpoint; private receipts, screenshots and Debug APK.

- [x] Report automatic inventory and assistant visual-review outcomes separately from the unchanged 3C baseline score.
- [x] Report misses only within frozen evaluable windows; unreviewed whole-match regions cannot supply a false-positive or miss denominator.
- [x] Regress existing event engine, detector adapter, preannotation/import tools and App; check dependencies and diff.
- [x] Build Android Debug with the retained local toolchain; no release signing or device-test claim without actual evidence.
- [x] Verify protected files/hashes and Git privacy; local feature commit is the commit containing this plan.
- [x] Stop at independent acceptance, with real limitations and one concrete next step. Do not merge or push.

## Execution Notes

- Existing first-match inventory is 1,188 candidates; 18 satisfy the predeclared supported/opponent/STRONG-or-MEDIUM review policy. No GT filter is involved.
- Original detector-to-engine frozen scoring remains 2/5 with one Royal Hogs duplicate; this MVP does not claim that baseline passed.
- Hog Rider, Goblin Barrel and Firecracker are not supported by the unchanged engine's card mapping. Manual entry is explicitly manual.
- Exporter and App may be implemented concurrently in disjoint paths with the frozen JSON interface; the controller owns integration, review and Git.
- Native Android Assisted import/confirmation remains unverified after bounded
  emulator QA timeout. Computer review flow and APK install/start evidence do not
  constitute a native import PASS; retain the failure and verify at acceptance.
