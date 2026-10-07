# Deployment Event Engine — Oracle Mode only

This package replays confirmed Human visual observations, not detector predictions.
It does not read videos, infer hidden state or connect to the game. The engine
and visual adapter never consume Event GT; the grading command alone does.

```powershell
.\.venv\Scripts\python.exe -B -m tools.event_engine event-replay-oracle --sources <private-visual-sources.json> --output <new-private-replay-directory>
.\.venv\Scripts\python.exe -B -m tools.event_engine event-evaluate --replay <private-replay-directory> --gt-lock <event-gt-lock.json> --gt-sha <expected-byte-sha> --output <new-private-evaluation-directory>
.\.venv\Scripts\python.exe -B -m pytest tools/event_engine/tests -q --tb=short
```

The source config has only `sources`: each descriptor has `kind` (`multiclass`
or `legacy_smoke_visual`), `lock_path` and pinned `sha256`. No Event GT, candidate
windows or target timestamps are replay inputs. All accepted source objects are
used, including own/unmapped/spawned observations; the engine applies guards.

`VisualObservation` uses source-pixel xyxy bbox and source-PTS-relative seconds.
Optional `appearance_group_id` is **confirmed human continuity**, not a proposal
ID or unresolved observation token. `source=human_gt_continuity` designates this
Oracle evidence. The adapter requires multiple source times and recorded human
group confirmation. Do not attach arbitrary IDs to detector predictions.

Direct rules cover Witch/Flying Machine/Golden Knight. Grouped rules cover
Minions/Royal Hogs: at least two distinct new tracks must **coexist in one
frame**, within fixed birth/spatial bounds. A single unit whose track splits
cannot establish multiple entities. Human appearance dedupe is match-scoped;
geometry assignment is one-to-one. Own/unknown owner, spawned/secondary and
unmapped visuals cannot emit events. Medium/weak candidates remain diagnostics.

`timestamp` means first supported appearance; `confirmed_at` separately records
when sufficient observations became available. Confirmation may be retrospective
and delayed. Do not claim event timestamps measure real-time detection latency or
independently prove deployment onset. See the frozen [contract](../../docs/plans/MODULE3B_ORACLE_IMPLEMENTATION.md).

Replay artifacts: full source/frame manifest and observations, registry/config,
tracks/candidates, emitted events and a recorded-App projection. Evaluation writes
one-to-one positive matches, explicit class-specific dedupe checks, unscored
unknown/unreviewed events and a timeline. Exit codes: replay0; evaluation0 only
when gates pass,3 for valid insufficient logic;2 for rejected evidence. New output
directories cannot overwrite old versions. File hashes check consistency, not
authenticity against coordinated forgery.

App compatibility uses `recorded_oracle_events_v1`, source `recorded_oracle` and
`confidence=null` (STRONG is evidence level, not a calibrated probability).
`RecordedEventSource.fromJSON()` accepts the projection, but is not wired to the
App UI, phone APK or live game. Existing Witch/Balloon mock controls are unchanged.

The current fixed real Oracle result is **FAIL**: all five positives match, but
the127s Minions continuity sample produces a new event. Do not tune parameters or
rewrite GT to turn this into PASS. [Verification](../../docs/VERIFICATION_MODULE3B.md).
