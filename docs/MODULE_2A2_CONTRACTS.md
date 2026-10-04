# Module 2A2 local contracts v1

These structures contain private evidence when used with real recordings. Keep
them in ignored `outputs/` or `local_data/`, never public Git. The complete
anonymous development example is `tools/offline_video/tests/experiment_fixtures.py`.
This document describes structural validation, not human/video authentication.

## Development draft

The closed root has `schema_version=1`, `experiment_id`, positive `freeze_version`,
`created_at` (explicit UTC ISO time ending Z), `protocol_version=1`,
`policy_version=1`, `identity`, `candidates`, `selection`, `unknown_intervals`.

- `identity`: underlying_match_id, recording_id, split=development,
  provenance=new_natural, complete_recording, unedited_recording, full_human_review.
  All three attestations must be true; they are not machine-proven facts.
- Each candidate: candidate_id, card_id, form, notes, evidence, deployments,
  evolution. Forms are normal/evolved/unknown. Notes explicitly record distinctness,
  visibility, occlusion, owner_clarity, form_clarity.
- `evidence` is an unchanged v1 single-target bundle for this card/form. Map
  evolved to v1 known_evolution only at this boundary. Unknown observations remain
  ambiguous/draft; they cannot become verified positives. All candidates refer to
  the same measured recording metadata and exactly one shared reviewed complete
  match segment. Segment identity/bounds/metadata must agree across bundles;
  deployment counts cannot be combined across segments or incomplete matches.
- Deployment annotations reference each v1 play_id exactly once and add clear,
  form, possible_missed_play, evolution={progress, remaining_count, source=manual}.
- Candidate evolution={capable, equipped, charge_requirement, rules_version}.
  equipped is verified/not_equipped/unknown; progress is known/unknown; unknown
  progress requires remaining_count=null. Counts are never calculated by this tool.
- `selection` is null or {candidate_id, card_id, form, method=manual, reason}.
  It must refer to an eligible candidate: >=2 independent clear verified plays of
  this one known form. A missing/ineligible selection is NOT_READY.
- Unknown intervals: unknown_id, recording_id, start_seconds, end_seconds, reason.
  Ordinary intervals are half-open. An unknown singleton is allowed only at the
  exact last actual frame; it conflicts with a closed terminal negative.

Candidate counts and eligibility are derived, never trusted input. The adapter
revalidates v1 metadata and retains recomputed gaps. Unknown gaps and possible
other-form visibility cannot overlap verified negatives. Duplicate occurrence or
exact frame/box evidence cannot manufacture independent plays; two units may
coexist in a frame with different boxes and distinct spawn evidence.

`validate_development(draft, indexes)` reports status DEV_VALIDATED or NOT_READY,
validity, derived candidates/counts/reasons, gaps and explicit unknown intervals.
Invalid inputs set valid=false; insufficient valid inputs set valid=true.
`require_development(draft, indexes)` returns an isolated payload containing draft,
derived report and index_snapshot, or raises a sanitized EvidenceError.

The snapshot binds used successful frame metadata and available checked RGBA
pixel hashes/aliases. Command-line disk operations must first use existing
load_indexes to verify reports, indexes and PNGs. Revalidating a stored snapshot
alone checks metadata, not that external media are still present or authentic.

## Lock chain

Development Data Lock -> Model Lock -> Test Ground Truth Lock -> future Evaluation
Result. The closed envelope is {schema_version, experiment_id, freeze_version,
created_at, lock_type, payload, sha256}. Types are development/model/test_gt.
The digest covers the entire envelope except its own sha256 field: compact,
sorted-key UTF-8 JSON, finite values only, array order preserved. Serialized files
have exactly one LF terminator and cannot exceed the strict loader's 16MiB limit.

Development payload is the checked {draft, derived, index_snapshot}. Consumers
recompute it and compare canonical bytes, not permissive Python numeric equality.
Dedicated ignored lock directories use canonical names
`EXPERIMENT.TYPE.vVERSION.json`; same experiment/type/version cannot be overwritten
or bypassed by renaming an existing lock. Corrections use a new version. Do not
mix input drafts, reports or unrelated files into the dedicated lock directory.

## Model Lock contract

The payload has common schema/experiment/freeze/UTC fields, development_lock_sha256,
target={card_id,form}, git_commit (40 lowercase hexadecimal characters),
model_sha256 (the **model file** digest), development_session_id,
test_pixels_unseen=true, precise_test_gt_unseen=true, input, sampling,
confidence_threshold, nms, postprocess, evaluation_protocol_version=1.

Input locks width/height, crop, resize/interpolation and preprocessing
(color order, dtype, scale, mean/std). Sampling and postprocessing parameters are
explicit, never inferred from test GT. Protocol v1 requires sampling.start_seconds
to equal zero, so a locked prefix skip cannot omit early recording content.
The actual closed options are defined in
experiment_lock.py, with a complete anonymous model contract in lock_fixtures.py.
No runtime/architecture, binary model or inference is supplied by this module.
Hash shape and contract consistency do not independently authenticate a model
file; the separately authorized model stage must compute/verify its real digest.

## Test Ground Truth contract

The payload includes common fields, development_lock_sha256, model_lock_sha256,
the locked target, independent match identity and completeness/first-qualifying/
all-deployments review attestations, a fresh prediction-unseen annotation session,
permissible excluded-material history, full recording/match metadata, evolution,
all deployments, negatives, unknown intervals, checked index_snapshot and protocol.

Each deployment retains manual onset brackets, visibility, known/unknown form,
evaluable/non_evaluable status, exclusion reason when required, optional original
key-frame boxes and manual/unknown evolution progress. Non-evaluable deployments
remain recorded and may have no boxes. Metrics must disclose the boxed subset;
temporal evaluation cannot be restricted to ground-truth deployment windows.
Unknown/other-form evidence is never a negative. All timeline gaps require explicit
coverage/uncertainty, including terminal state. Prediction fields are rejected.
Repeated frame/bbox annotations within one Test GT deployment are currently
accepted under different annotation IDs. No present box threshold or metric
depends on that count; future scoring must reject or deduplicate these samples.

The selected test's underlying match, recording ID and source media digest must
differ from development; re-encoding cannot override a same-underlying-match
declaration. The model session cannot also be the test annotation session.
Ordering is strict UTC: development < model < GT. Source authenticity and honest
blindness remain human declarations, not software certification.

## APIs and disk boundary

`make_development_lock`, `freeze_development`, `freeze_model`, `freeze_test_gt`,
`validate_lock`, `load_lock`, `lock_filename`, `canonical_bytes` and
`evaluation_references` are the separate lock-layer APIs. Freeze functions return
validated envelopes; lock_filename supplies the canonical created filename.
load_lock rechecks strict JSON, digest and full prerequisite chain.

GT's model_lock_sha256 references the **Model Lock envelope**, not the model file.
Future Evaluation Result references all three lock digests; this module supplies
reference fields only, no predictions, inference, scoring or actual result.
Before any disk freeze, verify supplied report/index/PNG files and compare the
used frame binding to the declared snapshot. Metadata-only API validation is not
an external-file integrity check.

## Command-line interface

Use the existing environment from the project root. The first two commands
require a new fully reviewed local development draft, not the old 2A1 bundle:

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.experiment_cli readiness "outputs\module2a2\development-draft.json" --indexes "outputs\module2a2\dev-survey\index.json"
.\.venv\Scripts\python.exe -m clash_tracker_video.experiment_cli freeze-development "outputs\module2a2\development-draft.json" --indexes "outputs\module2a2\dev-survey\index.json" --output "outputs\module2a2\locks"
.\.venv\Scripts\python.exe -m clash_tracker_video.experiment_cli validate-lock "outputs\module2a2\locks\experiment_01.development.v1.json"
```

The names are examples; use the actual experiment ID and preparation directory.
Readiness returns 0 for DEV_VALIDATED, 3 for valid but NOT_READY, and 2 for
invalid input/I/O. Successful development freeze returns 0 and DEV_LOCKED;
failed/not-ready/duplicate-version freezes return 2 and never overwrite a file.
Lock validation returns 0 or 2 and checks stored metadata/digests/prerequisites,
not external media; it does not substitute for readiness's disk verification.
Multiple exports use --indexes INDEX1 INDEX2. Normal output contains status only.

For future separately approved test work, validate a Model Lock with
--development DEV_LOCK; validate a Test GT Lock with --development DEV_LOCK
--model MODEL_LOCK. Freeze GT with:

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.experiment_cli freeze-test-gt "outputs\module2a2\test-gt-draft.json" --development "outputs\module2a2\locks\experiment_01.development.v1.json" --model "outputs\module2a2\locks\experiment_01.model.v1.json" --indexes "outputs\module2a2\test-survey\index.json" --output "outputs\module2a2\locks"
```

The command requires the full valid lock chain and equality of the supplied GT
snapshot with the loaded report/index/PNG binding before any write. Exit 0 means
the contract froze; failure is 2. There is deliberately no freeze-model command:
only the metadata API exists for the separately authorized model stage. No real
Model/GT operation is authorized by these examples. New development footage is
currently absent; none of the development/test examples have been run on it.

No live functionality, model inference or next-module authorization follows from
a syntactically valid contract. Refer to [the blind protocol](MODULE_2A2_BLIND_TEST_PROTOCOL.md).
