# Module 3B — approved Oracle implementation contract

The user-provided 2026-10-07 implementation/acceptance brief is authoritative.
Baseline: `d4c5b94625dda49dfb1af2c1b5c8d4851751650a`; use the existing checkout,
branch `codex/module3b-oracle-event-engine`. No push or main merge.

## Scope and tasks

1. Validate the immutable Event GT v1 SHA; capture old evidence protection.
2. TDD pure deterministic observations, tracking, five versioned rules and
   STRONG-only event emission. Track/group identity, not cooldown, deduplicates.
3. TDD a separate human-visual adapter, Event-GT-only scorer and exclusive-output
   CLI. Replay all accepted observations, never select input by event answers.
4. TDD offline recorded JSON compatibility; do not change App UI/mock controls.
5. Run the frozen Oracle replay and evaluation, regressions, privacy/protection
   checks and independent code review. Record actual PASS or FAIL and stop.

## Interfaces

`VisualObservation`: observation_id, match_id, timestamp, visual_class,
bbox (xyxy), owner, form, origin_kind, optional appearance_group_id/confidence,
source. IDs provided as continuity evidence must be human-confirmed appearance
identities; unresolved observation tokens are not identities.

`OpponentCardPlayed`: event_id, match_id, card_id, timestamp, form,
evidence_level, source_observation_ids, source_appearance_groups, rule_version.
Diagnostics also retain `confirmed_at`: offline timestamps refer to first
supported appearance, not the later moment confirmation became possible.

## Fixed registry/config before first real replay

- Rule version `oracle-card-rules-v1`; direct Witch/Flying Machine/Golden Knight.
- Grouped Minions/Royal Hogs: minimum_new_units=2, expected_units=3/4.
- Geometry: xyxy pixels; one-to-one assignment at each timestamp, class/owner/form
  compatible; IoU >=0.05 OR center distance <= max(90px, 2*bbox diagonal).
- Track gap and direct confirmation window: 7.5s (three existing 2.5s sample
  intervals); short occlusion can reconnect. Human continuity overrides gap.
- New grouped appearances: birth window <=2.5s, center separation <=120px;
  at least two distinct new tracks must coexist in one frame, rather than count
  fragments of a single unit; each track contributes once. A surviving group
  absorbs its returning members. No cooldown-only grouping or complex ReID.
- Owner own/unknown, explicitly spawned/secondary, and unmapped visuals cannot
  emit events. Unknown/candidates are never Negative.
- Events record first appearance and confirmation time separately. This is
  retrospective logic, not real-time latency validation.
- Score matching: exact card/match, one-to-one, [GT time, GT+2.5s]. Explicit
  continuity windows score only their candidate card; unresolved windows and
  other unreviewed time are unscored, never inferred false-positive negatives.

## Source/evaluation separation

Adapter consumes SHA-bound accepted visual annotations and their frame PTS,
owner overrides and genuine human continuity metadata only. Old confirmed smoke
visual GT may supply the existing match04 Witch continuity check, explicitly
reported separately from the 83-box multiclass stream. Neither adapter nor
engine reads Event GT. The scorer alone reads Event GT after replay.

## Acceptance and exclusions

Five confirmed events must each match exactly once and all three explicit
dedupe outcomes must have zero new events. Test the guards, identity/grouping,
determinism, unsupported observations and unscored unknowns. Preserve visual and
event locks, old experiments, videos and model environments. No detector, model
training, fresh extraction/annotation, 8-card/cycle/elixir, game connection,
capture/overlay, Android build, Module4 or detector mode.
