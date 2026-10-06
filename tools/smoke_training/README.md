# Fixed two-class Phase C smoke runner

This narrow runner consumes only the user-authorized immutable training snapshot.
It does not change historical offline_video extraction, evidence schemas or gates.
See [the frozen protocol](../../docs/PHASE_C_SMOKE_PROTOCOL.md).

Use the existing offline environment for `prepare_run.py`, artifact checks and
`python -m pytest tools/smoke_training/tests -q --tb=short`. The standalone
`train_smoke.py` must run in the previously qualified isolated model environment.
It uses official YOLOX model/loss/optimizer components without installing the
full Trainer's extra UI/logging dependencies. No additional dependencies here.

Each entry point takes explicit `--root`, `--lock` and/or `--run` arguments.
All data/results must be ignored under outputs/local_data; output writes are
exclusive. Preparation may verify and resume an interrupted metadata preflight,
but never replace previous export/download. Training and DEV_VAL start markers
forbid implicit repeat experiments. A failure is preserved and needs review.

The export includes all eleven accepted labels and retains coverage metadata.
Only two complete TRAIN frames enter loss. Partial DEV_VAL frames cannot provide
negative supervision, precision or unmatched FP. Outside-image padding candidates
remain in audit output but not image-level FP. Metrics are sampled-frame smoke
diagnostics, not full-match FP/min, owner discrimination or accuracy acceptance.

No private media/labels/weights, blind testing, extra steps or Model Lock belongs
in Git. The runner does not upload anything or start another module.
