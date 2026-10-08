# Module 3C-1 — Offline Detector-to-Event Integration

Date: 2026-10-08. Authorized baseline:
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.
Branch: `codex/module3c1-detector-event-baseline`. Local only; no main merge/push.

## Scope and frozen boundaries

Actual retained KataCR predictions, not Human-GT Visual Stream, enter the unchanged
Module3B engine. Added adapter/replay/diagnostics and synthetic tests only; existing
engine, Episode/config/rules, scorer, Event GT, visual locks, Attempt01/02,
original KataCR benchmark and Android App are unchanged.

The five positives and two continuity windows are match01; candidate12 is match04.
Therefore scan complete match01 first, then complete match04 with the same fixed
configuration. No GT-selected inference windows, other matches, retraining,
threshold tuning, new package/model/data download, App edit or live-game access.
These are historical development recordings, not independent blind tests.

Each scan is exclusive and configuration/weight/source SHA-bound before inference.
Both source videos decode to EOF with strictly increasing PTS. Prediction files
are sealed before replay; replay artifacts are sealed before the separate scorer
reads GT. The private processing-order receipt and inference import audit retain
this boundary. GT supplies final scores and post-score display windows only.

## Actual model/runtime and fixed configuration

Retained upstream commit `36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8`, clean checkout;
isolated Python3.12.4, Torch2.2.2+cu118, TorchVision0.17.2+cu118, Ultralytics8.1.24,
OpenCV4.9.0.80. GTX1050Ti4GB CUDA model parameters and nvidia-smi telemetry confirm
GPU execution. Existing offline environment remains separate.

Weights are unchanged retained detector1/2_v0.7.13, with SHA256 respectively:

- `72707f7af25a6b95e9dc8c3dbbf317cc727dbc5d7b457dae64b5c32e9a7024f2`
- `613062634618679418ef238acb6077c7357dfafde32b4f6078dde346f73d865a`

Source432×960; ROI `[8,67,422,729]`; canvas576×896; input896; FP32/batch1;
confidence0.1; per-model NMS0.7/max300; combo class-agnostic NMS0.6; retained fixed
UI filter. Full-file4FPS selects the first actual PTS at/after each target with
lag under100ms. No confidence/geometry/time parameter is changed after scores.

Preserve the historical explicit CUBIC resize divergence from upstream's effective
LINEAR call, and detector1 filename v0.7.13/internal training-name v0.7.12 caveat.
Root MIT does not override modified Ultralytics AGPL-3.0 or establish game-asset/
weight rights. Weight license/training chain/rights remain unverified. Only private
local research; no redistribution/product integration or legal-clearance claim.
Existing socket-denial/autoinstall/telemetry-disabled safeguards are not a security
sandbox. No new weight fetch or environment installation was performed.

## Prediction contract and engine input

33,337 actual final predictions become observations, 0 identical-box exclusions.
Raw per-model proposals, unmapped/padding rows, combined NMS rows, UI exclusions,
final boxes/confidence/owner channel and original PTS remain in private scan files.
The observation ID is deterministic from prediction-file SHA/match/PTS/time-base/row index.
Inverse ROI/canvas coordinates are retained in original-source geometry.

Nine explicit **visual** label mappings; all other/evolved names remain unsupported
observations. Existing card registry still has five cards, not arbitrary all-card
semantics. Source is `katacr_prediction`, never `human_gt_continuity`; no human
appearance ID or source-card hint is admitted. Owner requires agreeing raw
categorical channel/string and is **unvalidated model prediction**, otherwise
unknown. Form and spawn origin remain unknown for this runtime.

Frozen engine permits supported opponent observations with unknown origin and
does not calibrate confidence. STRONG here is an engine evidence level, not human
deployment confirmation. First-seen time is retrospective; confirmed_at is
separate. Inherited `oracle_*` schema labels are compatibility formats, not a
claim that this run used Human Oracle input.

## Actual fixed scoring result — FAIL, valid experiment

Event GT SHA remains
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
The unchanged one-sided hit window is `[GT timestamp, GT timestamp+2.5s]`.
Replay exits0. Frozen evaluation exits**3**: **2/5 hits**, **1 positive duplicate**,
**0 explicit continuity-window false emissions**, **3/3 windows sampled**.
2339 candidates;14 emitted events;12 listed as unscored. The extra Royal Hogs
output is both unscored in the inherited report and a **positive-duplicate failure**;
unscored does not erase that failure. Preserve all14 outputs; none enters the App.

| Card | GT time | Related output first-seen / confirmed-at | Fixed score |
| --- | ---: | --- | --- |
| Witch | 31.5 | 30.5 /30.75 | MISS: earlier output, not zero visual support |
| Royal Hogs | 75.5 | 75.75 /76.0; extra76.75 /77.25 | HIT plus duplicate failure |
| Flying Machine | 78.0 | 77.75 /78.0 | MISS: first-seen is earlier |
| Golden Knight | 102.5 | 102.25 /102.75 | MISS: first-seen is earlier |
| Minions | 116.0 | 116.75 /117.0 | HIT once |

For matched positives, first-seen/confirmation delay is Royal Hogs0.25/0.5s and
Minions0.75/1.0s. Related earlier outputs differ by -1s/-0.25s/-0.25s respectively;
they are **not rescored as PASS**, and their exact physical onset/box identity is
not independently established. The three MISS score windows still contain8/12/10
target-class predictions. Therefore these are fixed-window misses, not proof that
the model completely failed to see all three classes. GT timestamps are approximate;
no GT/time-window adjustment was made to manufacture a higher score.

Continuity checks retain candidate04 Golden Knight49..55, candidate09 Minions
124..130, candidate12 Witch match04 69..75: each0 new event. Raw target predictions
are17/20/**0**. Candidate12's zero output does **not exercise Witch tracking**;
sample coverage alone is not evidence that dedupe works across matches.

Four unresolved windows remain non-evaluable, never no-play Negative/FP truth.
Other unreviewed outputs cannot be certified false or true. Full-match FP/min is
**null**, not zero; no box AP/mAP, detector precision or cross-match positive
validation is claimed. No engine-output ID or timestamp was replaced with GT.

## Visual vs engine evidence

Royal Hogs creates two Episodes. At77.25s two member tracks from each are visible:
old tracks have already matched other same-frame boxes, remaining observations
become new tracks and qualify the second group under the unchanged min2/expected4
rule. Source observation/candidate/track/Episode IDs,75..79s raw boxes and owner
transitions are retained. A nearby own→opponent pair has IoU0.8401 and center
distance2.662px; this is a potential owner-flicker signature, **not certified
physical identity**. Late unit discovery, incorrect model proposals and association
fragmentation cannot be separated conclusively without new object-level review.

Thus the mechanical grouping pathway is demonstrated, while its physical cause
remains an inference. Earlier first-seen failures involve timing/onset semantics;
they are not automatically blamed on class recognition. Many unvalidated/noisy visual
proposals and missing Witch support in match04 also remain detector limitations.
No repair/tuning/new model was attempted in this baseline task.

## Processing speed

| Input | Sampled / decoded frames | Model mean / median / P95 | Full scan wall |
| --- | --- | --- | --- |
| match01 | 713 /4277 | 369.37 /311.72 /350.73ms | 278.09s |
| match04 | 810 /4859 | 311.15 /308.73 /327.19ms | 264.26s |

Source EOF is178.166667s/202.416667s; last sampled frame178.0s/202.25s. Means
include cold first-predict overhead; total scan wall542.35s,2.81 sampled FPS.
Steady median is about3.2FPS, below the4FPS sampling schedule for realtime use.
Torch peak allocated580,731,392 bytes across these scans; reserved624,951,296.
Driver memory includes other processes/context and is not Torch-only consumption.
Frozen engine processing26.63s; adapter+engine29.22s. This is offline processing,
not an end-to-end real-time detection or phone-performance benchmark.

## Fresh regression and protection

New synthetic adapter/replay/diagnostics tests:37 passed. TDD initially reproduced
missing adapter/replay/reporting behavior, then passed; later compatibility cases
cover nonzero PTS origin, evolved labels and empty prediction frames.
Full event/deployment/preannotation/recorded-replay/new-layer group:
**331 passed/1 existing Windows permission skip**. Historical smoke contracts:
**200 passed** (tests only; no real training). App102 and Node8 tests passed.
Both offline and retained detector `pip check` exit0.

Complete offline regression: **908 passed/3 existing Windows permission skips**,
exit0 in1237.80s (wrapper1239.875s). Combined fresh Python total:
**1439 passed/4 skipped, zero failures/errors**. No timeout change, test suppression
or real-model rerun. The regression process used a temporary process-scoped Windows
awake request, restored on exit; no global power/hibernate setting was changed.

Read-only protection confirms **2165 historical material files** and **144 existing
non-document tracked sources** byte-unchanged, including recordings, model weights,
GT locks, original benchmark/FAIL/repair/Attempts and accepted App/private demo.
Source checkout stays clean; replay/evaluation manifests verify. All inventoried
private material/new receipts are ignored, no private media/GT/model/APK is tracked;
diff and public link/secret checks pass. A first private protection-helper invocation
failed before writing a report because its Python module search path omitted the
repository root. Only that ignored helper was corrected and rerun successfully;
no experiment/source evidence or public implementation was changed for this error.
Android/Gradle/emulator/phone build or tests: **Not Run**, unchanged App/permissions,
outside this module. No new SQLite/schema/migration/persistence/native permission.

Exact commands/stdout/exit/JUnit and hashes remain ignored under
`outputs/module3c1/verification/`. Prediction/replay/evaluation artifacts remain
ignored under `run-v1`, `replay-v1`, `evaluation-v1`. Display-only12 contact sheets,
candidate CSV/JSON, timeline, diagnostic and forensic records make the local review
packet; original videos, GT locks, weights and account UI are excluded. Display
export redecodes only existing prediction PTS after scoring; it is not new model
inference or evidence relabeling. Full raw predictions remain local.

## Stopping point

The detector→observations→unchanged engine→independent scoring chain ran, but the
fixed detector-derived event baseline is **insufficient**, not Oracle5/5 replay
performance or product-ready automatic card counting. Wait for independent review
of this baseline. No main merge/push, automatic repair, training, App integration,
Module4/cycle/evolution/elixir/live-game or next-module work is authorized.
Local implementation commit is the revision containing this checkpoint; the review
packet manifest records its full SHA and real baseline→review diff. Formal ChatGPT
acceptance remains pending; local code review is not substituted for that review.
