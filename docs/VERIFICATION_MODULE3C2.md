# Module 3C-2 — Detector Baseline Failure Diagnosis

Verified:2026-10-09. Authorized baseline:
`b146a4f81a31d33e73d72cfcc49c33721608f9e9`; branch
`codex/module3c2-detector-failure-diagnosis`. Main remains
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`. This is a diagnosis-only local
checkpoint, not independent acceptance or a working detector.

## Contract and unchanged evidence

Trace five scored positives and the Royal Hogs duplicate from frozen actual
prediction→observation→track/episode→candidate→event. A defect may be repaired
only when its root cause is independently reproducible and its expected behavior
is established without the Event GT answers. No change to GT, one-sided `[0,2.5]`
scoring, card/group rules, tracking configuration or episode logic was justified.
No production code/test/Schema/manifest/dependency/App changes were made.

Original Event GT file SHA remains
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
Predictions still use match01 then match04. Source predictions/config/locks,
3C-1 FAIL/evaluation/unscored lists, all earlier experiments and APK are preserved.
Human identity/GT labels are not supplied to adapter or event generation.
Diagnosis may read sealed GT/scoring afterwards; it does not rewrite them.

## Five time chains

All five GT positives are match01. Times in seconds; `GT` is the frozen human
**approximate** timestamp. The raw time below belongs to the diagnostic-related
actual event, not an independently box-verified match. For misses, no scored
matched event exists. `event timestamp` is first appearance; `confirmed_at`
is when the engine's confirmation condition is met, not shifted GT onset.

| Candidate/card | GT | First raw opponent detection | Member track births | Event timestamp | confirmed_at | Frozen result |
| --- | ---: | ---: | --- | ---: | ---: | --- |
|02/witch|31.5|30.5|30.5|30.5|30.75|MISS,1s early|
|05/royal_hogs|75.5|75.75|75.75,76.0|75.75|76.0|HIT plus duplicate|
|06/flying_machine|78.0|77.75|77.75|77.75|78.0|MISS,0.25s early|
|07/golden_knight|102.5|102.25|102.25|102.25|102.75|MISS,0.25s early|
|08/minions|116.0|116.75|116.75,117.0|116.75|117.0|HIT|

Direct-event identity chains:

- Witch: `det-a970594a897fbaafe8688649`→
  `track-621e2ee6d66db0b69afec8db`→`event-678b70b49611e800e8c8897d`.
  Source sample122, rawPTS2745000 at1/90000; confirmation observation
  `det-5d7baf36e95384ae8d609815` at30.75/sample123/PTS2767500.
 58 source observations, last51.75. Score window has8 raw same-class detections
 (7 opponent/1 own), seven remain on this event's track.
- Flying Machine: `det-dffb87cb45de62274f64156e`→
  `track-71cbcadd2488ca6377e22b15`→`event-d4a7db4c263f9a9be64a0058`.
  Sample311/rawPTS6997500; confirmation
  `det-7314e8e1173ce6572bc8a2c1` at78/sample312/rawPTS7020000.
 80 source observations, last98. Score window has12 raw predictions
 (11 opponent/1 own);11 remain on this event's track.
- Golden Knight: `det-4f9c085b7ae88883fc2c56dd`→
  `track-8bcd3f9ec71d10c891bb16fb`→`event-4265bb5d6d4175126735d114`.
  Sample409/rawPTS9202500; confirmation
  `det-99ab3c2a7efe1ca99c641e32` at102.75/sample411/rawPTS9247500.
 50 source observations, last117. Score window has10 opponent predictions,
 all remain on this event's track.

The sampler, PTS conversion and track births agree exactly. In these data,
origin=0 and all time_base=1/90000. The adapter does not move timestamps;
`_candidate()` chooses the first source observation as timestamp. The scorer
uses that timestamp, not confirmed_at. Thus Flying Machine/Golden Knight
confirmation inside the score window does not turn either into a hit.
These are first-seen/approximate-onset semantics, **not proven clock drift**.
Which early boxes depict the correct entity/new deployment is still unknown.
Changing to confirmation time, adding a delay or widening tolerance would change
the frozen contract. No such change or GT adjustment was made.

## Royal Hogs duplicate chain

| Event | Episode | Member tracks | First/confirmation |
| --- | --- | --- | --- |
|`event-4c8512a30989a44bdf85cb98`|`appearance-4d5ef3b3562196f58ab393f0`|`track-4d5ef3b3562196f58ab393f0`, `track-9159888df5530711555faa61`|75.75/76.0|
|`event-470cbb33af8aaba57965eddc`|`appearance-e6e07d6f3d0d1acbf452c113`|`track-e6e07d6f3d0d1acbf452c113`, `track-31b2f9413fbd6a1e5a58d201`|76.75/77.25|

First tracks begin with `det-095a018fc208644983645bbb` (75.75) and
`det-a05a73faef56300dd7fb9ea6` (76.0). At76.75 three opponent boxes compete
for two compatible pre-existing opponent tracks; both old tracks are matched.
Remaining `det-c498569d0db218e900c5d7f6` creates the third track.
At77.25 four opponent boxes compete for three existing tracks, all matched;
remaining `det-ebc81cacd9b665ed00538a98` creates the fourth. The two later tracks
coexist and meet `minimum_new_units=2`, forming the second episode. The first
episode still has both members visible. **Two different episodes emit once
each; not one episode emitting twice.** An alternative maximal-cardinality
one-to-one matcher would still need an additional track in both frames.

The old policy admits genuinely unassigned new tracks as a new episode, even
while old members survive. `expected_units=4` is metadata, not a capacity rule.
Without trusted human continuity, confirmed episodes do not adopt newly visible
tracks. A GT-free two-nearby-units→four-nearby-units stream therefore also emits
two events; two-old+two-far-new must remain eligible for two events. This exposes
**late-member/new-deployment ambiguity**, not a proven implementation violation.
Automatically filling the first group to four would alter the accepted contract
and may swallow a legitimate second play. No forced merge/cooldown was applied.

Raw owner flicker also appears: a75.75 own box and76.0 opponent box haveIoU0.8401
and center distance2.66px. Owner equality prevents track association, but geometry
does not certify these are the same physical hog. First-event membership can
swap between nearby units; this is a model/identity risk, not evidence of a
software owner inversion. Additional visual/continuity truth would be required
before assigning a physical cause or changing group membership.

## Adapter audit versus detector limitations

Pinned upstream uses friend=0/enemy=1; scanner maps to own/opponent accordingly.
Adapter demands integer-channel/string consistency; otherwise unknown. All
33337 actual detections agree on owner. None is changed using battlefield side
or GT. Canvas576×896→source432×960 usesx=8+x*414/576,y=67+y*662/896;
the predictor already reverses letterbox to canvas. No double scaling found.
All source PTS/sampling/raw model rows/merged detection class/index/confidence/
ROI mapping and re-converted observation/binding checks agree; maximum
coordinate/PTS discrepancy0, identical-box exclusions0.

All actual forms/origins remain unknown; source_card is null. Supported base
class names do not imply normal form or primary origin. Evolution names stay
`visual.other.*_evolution`; unsupported classes and spawned-origin truth are not
converted into the five supported card rules. Model owner remains unvalidated.
The inherited engine permits unknown origin for supported opponent classes;
STRONG is its continuity level, not verified card provenance/calibrated accuracy.

Synthetic contradictory redundant canvas/global-index fields are not independently
cross-checked by the current adapter. The actual frozen data contain zero such
conflicts, so this is deferred hardening, not a cause or a repair in this task.

No isolated deterministic implementation bug was established. Program-level
limits remain: no onset/absence proof and no distinction between newly observed
group members and truly new deployment. Detector-side weaknesses include
unvalidated owner/identity and match04 zero Witch predictions in its reviewed
window; the latter makes a zero-event dedupe score uninformative about tracking.
Three early failures alone do **not** prove the detector needs retraining.
For eventual use, stable class/owner/unit coverage is needed, but retraining will
not alone solve onset/group semantics. Review the time/identity diagnosis first;
no model improvement experiment is implicitly authorized here.

## Fresh fixed-data rerun and verification

Only sealed prediction JSON is replayed; **no model inference rerun**. New private
directories `outputs/module3c2/replay-v1` and `evaluation-v1` are exclusive,
never overwrite3C-1. Replay command uses existing `tools.detector_events`;
grading uses existing `tools.event_engine event-evaluate` afterwards.

- Replay exit0; evaluation exit3: valid insufficient baseline, not broken input.
- Observations, complete replay (tracks/episodes/config/registry/events),
  candidates and event files are byte-identical to3C-1.
- Score fields are equal except the new replay manifest binding. Source-summary
  runtime varies, so the full run manifest is intentionally not byte-identical.
- Before→after:2/5→2/5;1 duplicate→1;dedupe0/0/0 unchanged;14 emitted events,
 12 inherited unscored outputs retained, including the scored duplicate. Four
 unresolved windows remain non-negative. No full-timeline FP/min/cross-match claim.
- Full related contract command:
  `.venv/Scripts/python.exe -B -m pytest tools/detector_events/tests tools/event_engine/tests tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests -q --import-mode=importlib --tb=short -rs`
  **331 passed/1 skipped**,exit0. Existing symlink privilege skip in
  `test_event_gt.py:363`; no failures/errors. Actual logs/JUnit remain ignored.
- Existing offline environment and isolated KataCR environment `pip check`:exit0,
  no broken requirements. No installation/environment change.
- Offline extractor's908-test suite, smoke-training200 tests, JS/App tests and
  Android build/phone/emulator: **Not Run**, unchanged paths and no extraction,
  training or App task. Previous3C-1 full1439/4 is historical, not a fresh run.

Public change set is only five Markdown files: README/current state/plan,
this verification document and a checkpoint. Private reproducible helpers,
event-trace/group/adapter audit JSON, rerun/test receipts and protection results
remain ignored under `outputs/module3c2/`; no video/frame/weights/GT are tracked.
Fresh protection check passes: **2347 existing material files** (including3C-1
predictions/results/Review ZIP and earlier protected history) and **151 existing
non-document tracked source files** are byte-identical. At the final check2379 private
files were inspected, all ignored, none tracked. Four old/new replay/evaluation
manifests pass verification and Event GT SHA matches. Fresh five-document public
inspection:117 relative links resolve, new private-path and full-file credential
patterns absent, worktree/staged diff checks exit0.

Reproducible private audit receipts:

| Ignored artifact under `outputs/module3c2/` | SHA-256 |
| --- | --- |
|`event-trace.json`|`7dfcbecee7cec05db8f388ce535c02e79546c68a8e72ce5f6257da15d1cf6941`|
|`group-audit.json`|`12ceab238d731c176c39ba5b792545d9fc6c5dbe5e4418734d35476855d4e8cb`|
|`adapter-audit.json`|`a18943d07694e09c621cb3ab389ec47afd291d8ba41b10586090730ce8d141f5`|

Trace readback validates sealed input before post-score GT reading, all1523 PTS
frames/33337 bindings and unchanged input hashes. Group audit replays59 RoyalHogs
observations with no GT, reproducing all three actual RoyalHogs events; two
synthetic no-GT scenarios each reproduce two events. Exclusive second group-audit
export is rejected without changing its original SHA. Adapter audit independently
checks24 conflict categories (all0), class/global-index/local-row membership,
sampling/PTS/ROI and full regenerated observation/binding/frame identity; ten
input/implementation hashes before/after match.

Actual local commit/ref/status are verifiable from Git and private final receipts,
not a self-referential SHA embedded in this document. No source/test changes or
new regression test are claimed because no production fix was justified. Stop
for independent review; no push/main integration.
