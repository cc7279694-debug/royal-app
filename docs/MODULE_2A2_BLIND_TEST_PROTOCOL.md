# Module 2A2 blind-test protocol v1

This protocol governs a small offline experiment, not gameplay assistance.
It does not authorize Module 2B or certify detection accuracy or zero ban risk.

## Development first

1. Play normally. After the match, record its entire replay with the system
   recorder, at normal speed and without edits. Completeness means the user
   confirms coverage of the full match; the last actual decoded frame is the
   evaluable end. A victory/defeat/result screen is not required. Record
   completion_attestation=user_confirmed and result-screen presence separately.
   Still reject damage, decoding failure, obvious mid-match truncation, missing
   key battle intervals or an explicit human statement of incompleteness.
2. Keep a new recording in `local_data/recordings/development_01.mp4`. The old
   2A1 Inferno Dragon match is only a historical pipeline regression sample.
3. A human reviews the whole replay, inventories the opponent's actual cards
   and their `normal`, `evolved` or `unknown` forms, and creates local evidence.
4. A candidate needs at least two clear, independent verified deployments of
   the same logical card and one known visual form. Images are not deployments.
   Multiple candidates are compared using count, distinctness, visible duration,
   occlusion and owner/form clarity. There is no fixed card-name priority.
5. Record all candidates, the human's selected target and the rationale. Other
   forms and unresolved observations remain evidence, not negative examples.
   If no candidate qualifies, preserve the replay as NOT_READY and use a later
   natural match; never lower the standard.
6. Validate evidence and freeze a versioned Development Data Lock. A correction
   creates a new freeze version. Do not overwrite or silently alter an old lock.

## Model before test exposure

Only a separately approved Module 2B may develop a model. It must create a Model
Lock referencing the exact development lock and fixing code/model hashes, target,
input geometry/crop/resize, preprocessing, sampling, confidence, NMS/IoU,
postprocessing and evaluation protocol. Keep test pixels and precise ground
truth outside the development session until this lock exists.

The first qualifying independent natural match becomes the test match: complete,
unedited replay, opponent used the locked card/form at least once. Same underlying
match is not independent even if re-recorded, re-encoded, renamed or cropped.
Do not skip a match for occlusion, difficulty or expected poor model performance.
Only missing/damaged replay, recording interruption or inability to decode permit
material exclusion; retain its reason and selection history locally.

## Ground truth before any test inference

After Model Lock, register the independent test recording. Use a new annotation
session to watch the complete replay without seeing model predictions. Register
all locked-form deployments, including `non_evaluable` entries with reasons.
Preserve other/unknown forms separately. Only manually verified target-absence
intervals are negatives; unknown intervals are never inferred negatives.

Freeze Test Ground Truth with development and model lock digests before the first
test inference. Do not put prediction fields in ground truth. Inference must
scan the whole recording using locked sampling/preprocessing, not ground-truth
deployment windows. A future immutable Evaluation Result references all three
locks and reports evaluated coverage and unknown regions, rather than hiding them.

## Evolution and uncertainty

Evolution capability, equipment status, charge requirement and rule version are
manual ground truth. Remaining plays are optional and never estimated. Gaps,
possible missed plays, unknown form/equipment/rules force unknown progression.
This module does not compute card cycle, elixir or automatic evolution countdown.

## What the tools can and cannot prove

Strict schemas, explicit linkage, timestamp ordering, recomputed digests, exclusive
creation and declared underlying-match IDs catch structural inconsistencies and
accidental leaks. Attestations cannot prove a human actually watched the replay,
that a declared match ID is truthful, that the first qualifying match was chosen,
or that nobody saw predictions. This is not OS isolation, signing, tamper-proof
storage or original-video authenticity certification. Local files can be edited
outside the tool; consumers must revalidate digests and references.

The 2026-10-04 user-confirmed completeness amendment supersedes the earlier
result-screen boundary gate. Missing ending UI alone is not missing battle
content and does not prevent development freeze. It is also not evidence of
target absence: retain uncertainty/other forms and ordinary half-open intervals,
including explicit terminal uncertainty where needed. Technical contradictions
about damaged/missing battle content still require rejection or resolution.

Core processing remains local. Private recordings, indexes, labels, identifiers,
hash manifests and locks stay in Git-ignored `local_data/` or `outputs/`. Public
reports contain aggregate results only. Do not upload private evidence to obtain
an independent code review unless the user separately authorizes disclosure.

## Current stopping rule

This implementation builds the lock-chain infrastructure. Real execution stops
at DEV_LOCKED, then waits for independent acceptance and Module 2B authorization.
If no new development replay has been supplied, the honest status is
WAITING_FOR_DEVELOPMENT_MATCH; no actual Development Lock is fabricated.
