# Module3C4 — parallel visual evidence experiment

Not a production tracker, owner classifier or accepted card-play recognizer.
The accepted3B engine, existing detector adapter, GT and scorer are unchanged.

## Runtime / source boundary

The single mature tracker is official
[ByteTrack](https://github.com/FoundationVision/ByteTrack/tree/d1bf0191adff59bc8fcfeaa0b33d3d1642552a99),
pin `d1bf0191adff59bc8fcfeaa0b33d3d1642552a99`. Its root
[MIT notice](https://github.com/FoundationVision/ByteTrack/blob/d1bf0191adff59bc8fcfeaa0b33d3d1642552a99/LICENSE)
is preserved locally. Source-history clearance, game assets and existing KataCR
weights are not established by that root license. The adapted four-file core,
license, NOTICE and provenance stay private/ignored; the public loader checks
their exact SHA256 before executing verified bytes. No Ultralytics tracker,
learned ReID model, new detector, training or new model weights are introduced.

An independent tracking-only environment uses NumPy1.26.4, SciPy1.13.1 and
LAP0.5.13. Original offline and detector environments are not changed.
LAP preserves the upstream cost-limit solver; a NumPy IoU implementation
preserves pixel-inclusive `+1` geometry. Compatibility and observation-ID
instrumentation plus a synthetic-proven terminal-removal repair are itemized in
the private NOTICE. This is an adapted, not byte-identical upstream runtime.

Frozen high=.5, low=.1, match=.8, buffer=2s at4FPS, score fusion enabled.
Effective upstream boundaries: high score>.5; low .1<score<.5; new birth>=.6.
Exactly .5 is in neither association pool. These defaults were frozen before
real output; no threshold or motion budget was changed after results.

## Evidence, not answers

`tracking.track_stream` consumes raw observations plus complete contiguous4FPS
sample metadata (including empty frames), partitions by match/class but not
owner, and preserves all original detections. IDs are algorithmic hypotheses.
Kalman extrapolation does not create new detection rows or establish absence.
Ambiguous associations, missing IDs, low scores and lifecycle history remain
inspectable; no human appearance identity is manufactured.

`policy.run_policy` requires three unanimous distinct owner predictions online.
Unknown/ambiguous/conflicting evidence remains unknown. Initial region,
movement, crossing and reacquisition are context only; neither current screen
half nor detection confidence determines owner. Persistent same wrong owner
can remain wrong: stability is not accuracy. First-seen and first owner-consensus
time are separate, with no estimated physical deployment time.

Grouped diagnostic cohorts can tentatively attach late members using original
birth geometry, a fixed2.5s total birth span and120px anchor proximity. The
anchor is immutable; earliest member and individual member birth times remain
explicit. Multiple/capacity/owner conflicts are unresolved. Spatially or
temporally separate new groups remain possible; there is no card cooldown.
These cohorts **do not emit events** or prove physical deployment grouping.

`cli.run_files` gives unchanged3B only the schema whitelist. MOT/cohort IDs stay
in sidecars, never in trusted human identity fields. Owner abstention changes
event eligibility and can delay a newly eligible engine track; improved scoring
from that delay is not proven deployment timing. All timestamps/bboxes/raw
confidence/form/origin are preserved. Exact post-projection geometry collisions
are lexical-ID excluded only at the engine boundary, retaining every exclusion
and the fixed original denominator. Actual frozen trial has zero such exclusions.

Generation accepts no Event GT input and reads no scoring labels. Existing
`tools.event_engine event-evaluate` scores only after the replay is sealed.
Outputs are exclusive versions; old locks/baselines/results are never overwritten.

## Run / verify

Using a qualified isolated Python and the locally audited source directory:

```text
python -B -m tools.visual_evidence replay --input <frozen-detector-stream.json> --sha <input-SHA256> --baseline <frozen-replay.json> --baseline-sha <baseline-SHA256> --tracker-source <audited-core-directory> --source-width 432 --source-height 960 --output <new-ignored-version>
python -B -m pytest tools/visual_evidence/tests -q --import-mode=importlib
```

Core tests must actually run in the tracking environment. The offline environment
deliberately has no SciPy/LAP, so its optional tracker tests skip explicitly.
Do not call that skip a successful runtime test. Private source availability is
required: this research wrapper is not a self-contained distributed product.

## Metrics interpretation

Use the same five3B classes and raw observation denominator for main comparison.
Starts/100, singleton counts and possible continuations are algorithmic proxies,
not true physical ID-switch or fragmentation measurements. Assignment coverage
and ambiguous/unassigned counts are always reported. `initial_visible_track_count`
and `final_visible_track_count` mean edges of each class's **observed detection
stream**, not recording boundaries, physical birth/death or censoring.

Owner flips compare raw/projected owners on the same owner-agnostic ByteTrack
hypothesis links. Report known-known coverage and unknown fraction alongside
flips; otherwise abstention looks falsely successful. No owner probabilities or
physical identity GT exist. No full-match FP/min or blind generalization claim.

See [actual trial and limitations](../../docs/VERIFICATION_MODULE3C4.md).
