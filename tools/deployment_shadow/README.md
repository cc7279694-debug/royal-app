# Module 3C-3 — independent Deployment Evidence / Spawn Group Shadow

Authorized bounded experiment, not a production engine replacement. Inherited
`tools/event_engine` and its Oracle rules, evaluation window, GT and old FAIL
artifacts are immutable. Local baseline is `bbcd091`.

## Frozen experimental contract (before real replay)

Use the existing sealed detector VisualObservation stream. Reproduce the
original engine output exactly and keep it separate. No model inference,
training, GT answer input, human identity injection or timestamp shift.

Time evidence distinguishes first_seen_timestamp, confirmation_timestamp and
estimated_deployment_timestamp. The last is null unless actual deployment
evidence exists; sampled non-detection is not ground-truth absence. Source-video
visual review is separate post-run evidence and never supplies algorithm answers.

The Shadow strategy consumes baseline tracks/episodes, using their actual birth
positions, chronology and motion continuity. Original values are inherited:
birth window 2.5s, group distance 120px, movement budget 90px/s, track gap 7.5s.
Expected member count is metadata, not a merge or new-deployment proof.

First qualified baseline cohorts and direct events are PROVISIONAL, never
confirmed card-play truth. A later nearby overlapping cohort is associated as a
possible late discovery but remains UNRESOLVED rather than emitting another
provisional event. Close overlap remains ambiguous even outside the birth window;
no long card cooldown is used. Every suppressed baseline event survives with its
original ID, observations, episode and reason in unresolved candidates.

A second provisional cohort requires the baseline distinct-unit qualification
plus independent observational separation from every earlier group: either all
birth centers are farther than max(120px,90px/s * gap) from all recent old-member
positions (each gap <=7.5s), or the last two sampled frames before birth follow
all old-member sightings, are <=7.5s apart, with last-to-birth gap <=2.5s, and
contain no same visual class of any owner/form/origin. This is explicitly sampled
non-detection, NOT proven absence, a Negative label or physical deployment truth.
Track expiry alone is insufficient. Nearby owner/form/origin conflicts remain
uncertain; do not silently relabel unknown or own observations. Conflict analysis
is offline retrospective over all candidate source sightings: a later overlapping
own/unknown prediction can make an earlier candidate UNRESOLVED. No online
causality or calibrated owner confidence is claimed.

## Execution and evaluation boundary

```powershell
.\.venv\Scripts\python.exe -B -m tools.deployment_shadow --replay <sealed-detector-replay> --output <new-private-shadow-version>
```

The generation command has no GT parameter, rejects changed input and output
reuse, and verifies source hashes before writing an exclusive artifact manifest.
Only after sealing may the existing evaluator score the provisional first-seen
timeline against the unchanged GT and window. That score is a same-input
diagnostic comparison, NOT confirmed automatic recognition, a blind test,
cross-match generalization, full-timeline FP/min or permission for live use.

## Verification

Synthetic tests exercise staged group sightings, movement/sampling continuity,
owner flicker, close ambiguous second groups, far separate second groups while
old units survive, sampled fresh cohorts after disappearance, guards, immutable
inputs and deterministic replay. CLI tests verify sealing, no GT input, mismatch
rejection, no private-path errors and exclusive outputs. Stop after local commit;
no main merge, push, App changes, training or next stage.
