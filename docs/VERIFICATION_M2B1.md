# Module 2B-1 verification

## Scope and checkpoint

Authorized 2026-10-05 from main/origin/main
`48136affd470a39feb9815f19e1dbd207ffc14ca`; feature
`feat/module-2b1-minions-visual-baseline`, current checkout retained.
Only frozen minions/normal development data, two independent plays/six original
boxes/three explicit unknown intervals/no verified negatives. No labels/Development
Lock edits, independent test pixels, neural training, later modules or live input.

## Fresh checks before first real experiment

- Full baseline: `./.venv/Scripts/python.exe -m pytest -q --tb=short`:
  **406 passed, 1 skipped in 70.49s**, exit 0.
- Existing real Development Lock and explicit seven report/index pairs reloaded;
  canonical reconstruction equals the existing lock, readiness DEV_VALIDATED.
  No source decoding or model scan by this metadata/PNG check.
- Initial 28 core tests observed RED for missing baseline, then GREEN 28/28.
- Fourteen adapter tests observed RED, then 12/14 GREEN. Two incorrect synthetic
  assumptions were diagnosed: random RGB textures lose chroma under YUV420 and
  model fixture geometry/sampling did not match its baseline configuration.
  Achromatic fixture pixels and consistent fixture metadata fixed those tests;
  no real settings or success threshold changed. Then 42/42 GREEN.
- Three binding/build tests added; missing Model Lock/artifact semantic verifier
  observed RED, implemented, then **45/45** new tests GREEN.
- Full pre-experiment regression: same full command, **451 passed, 1 skipped in
  64.06s**, exit 0. One known Windows symlink permission skip; junction tests run.
- Resumed full regression (including fixed Top5 contract test): **452 passed,
  1 skipped in 92.93s**, exit 0.
- Fresh-context internal review reproduced three Important issues before any
  real scan: cwd-sensitive code freezing, result configuration not bound to
  the prefrozen protocol, and incomplete reference Model Lock runtime bindings.
  Sixteen regression cases observed RED and were repaired; six further Git-error/
  artifact-semantic cases observed RED. A misplaced test tail briefly produced
  five NameErrors, then was corrected without removing assertions. All 68 new
  baseline/adapter tests passed. The internal reviewer rechecked all three repairs;
  this is not ChatGPT independent acceptance.
- Fresh repaired full regression: same full command, **474 passed, 1 skipped
  in 168.53s**, exit 0. No real settings changed in these repairs.
- Bytecode compilation and offline wheel build both exited 0 after repair;
  generated artifacts remain ignored. These checks are not Android/UI builds.
- `python -m pip check`: **No broken requirements found**, exit 0.
- Only headless OpenCV 4.13.0.92 and required NumPy 2.4.3 installed as pinned
  Windows wheels. No existing dependency upgraded. Installed wrapper MIT notice
  and bundled OpenCV Apache-2.0/third-party notices inspected, not inferred solely
  from metadata. Sources and license detail: [protocol](MODULE_2B1_PROTOCOL.md).
- All actual commands/stdout/stderr and the preflight hash inventory stay in a
  new ignored receipt directory. Existing protected set is **10231 files**,
  including private original recordings/evidence/locks and retained synthetic
  scratch; the explicit inventory is not published.
- Fresh post-repair protection check: **10231/10231 unchanged**, zero missing,
  not-ignored or tracked-private files. No extraction or label/lock edits.

## Implementation boundaries

Pure baseline and separate disk/CLI adapter; unchanged Module 1 extractor and
2A1 prepare/validate/review, still experiment_gate=false. 2A2 model contract gains
only a closed additive reference-template artifact variant; old model and Test GT
contracts retain their regression tests. Optional baseline extra does not make
OpenCV necessary for legacy video/evidence tools.

Fixed scan/rank/evaluation details are in the protocol. Both full rankings are
persisted before hidden scoring, source exclusion uses only the reference
occurrence, and score/earliest-time fields are separate. The CLI rejects malformed
local arguments without echoing private values. Build refuses any failed fold.

## Real result

Not Run at this pre-experiment checkpoint. No PASS, recognition accuracy,
cross-match generalization, Model Lock or independent blind test is claimed.
The next step is fresh-context code review, protection checks, local code commit,
then the two fixed development folds. Do not tune after observing their results.

## Limits

Fixed ROI is a layout assumption. Group crops contain background; no persistent
three-unit tracking. Temporal candidate grouping is not proof of physical play
independence: long gaps can split a play and close evidence can merge plays.
The temporal held-out gate alone cannot certify spatial/card identity; private
candidate screenshots support independent review. Unknowns are not negatives,
so no calibrated confidence, recall/FP rate or generalization claim follows.
Digest/snapshot consistency and manual attestations do not certify source truth.
Android/live/independent blind inference Not Run; no push/merge is authorized.
