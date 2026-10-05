# Module 2B-1 — Minions visual baseline protocol

Authorized 2026-10-05; implementation baseline is
`48136affd470a39feb9815f19e1dbd207ffc14ca`. This is development-only,
not an independent-match blind test, deployment tracker or gameplay assistant.

## Data and folds

Only the accepted immutable minions/normal Development Lock: one underlying
match, two clear independent deployments, three original group boxes each.
Six images are not six independent deployments. Unknown intervals, other forms
and unlabeled coverage are never negatives. No old Inferno Dragon or other
unassigned recording is used. Source MP4 and explicitly supplied report/index/PNG
references must match the frozen hash/snapshot before scanning.

A's three crops scan the whole replay to find B; B's crops find A. Scanner takes
source pixels, reference templates and fixed configuration, no hidden ground
truth. The reference visibility interval alone excludes source self-matches.
Both complete ranked lists are written exclusively before hidden evaluation.
The cross-validation receipt binds the pre-scan protocol file hash. Building
rechecks that file, its code/data/target and the a priori settings above; editing
the result report cannot select new settings for the final detector.

## A priori settings

- Full-image normalized battlefield ROI: x=0, y=0.12, width=1, height=0.73.
  Excludes fixed top/bottom UI, not either player's battlefield half. It is a
  fixed layout assumption, not automatic arena detection.
- RGB uint8; bilinear working scale 0.5; template scales
  0.85, 0.925, 1, 1.075, 1.15. Invalid/constant scales are skipped and counted.
- Maximum RGB `TM_CCOEFF_NORMED` score is the ranking signal. ORB uses 64
  features, edge threshold 8, patch size 15 and ratio 0.75 for diagnostics only.
- Whole-file 4Hz coarse scan uses actual relative PTS, never average-FPS time.
  At most 24 score-ranked temporal seeds, separated by more than 2 seconds;
  fine scan covers actual frames within each fixed +/-1 second window.
- Proposal-support floor 0.55 is fixed before real scanning, not fitted from
  unknown negatives. Final detector threshold is a separate, PASS-only value.
- Final candidate grouping joins adjacent supported observations with gaps of
  at most 2 seconds, transitively. Continuous support lasting longer than two
  seconds stays one event. A gap >2 seconds creates separate proposals, not
  proof of separate physical plays. Residual split/merge errors remain a limit.
- Peak score determines ranking. First support determines delay; these are
  separate PTS-bearing observations. An early first support cannot be rescued
  by a later peak. Deterministic ties use time/template identity.

## Gates and stopping points

Hidden onset is loaded only after rankings freeze. The temporal evaluation proxy
requires first support in the inclusive onset..onset+2s interval and rank <=5
in BOTH folds. A temporal coincidence alone does not certify card identity or
ownership; local candidate PNGs support later human/independent review. One
physical hidden deployment is scored once, never once per frame/candidate.

Any failed fold stops at `2B1_BASELINE_INSUFFICIENT`: preserve diagnostics and
do not build a Model Lock, tune until PASS, add data or start 2B-2. Both passing
folds permit all-six-template final development scanning. Threshold is exactly
the lower of the two held-out true-event peak scores. Unknown areas cannot
improve it. This is not cross-match generalization or a false-positive estimate.

On PASS only, canonical detector JSON file bytes define a genuine artifact SHA,
not invented neural weights. The additive reference-template Model Lock variant
binds code/development/artifact/template hashes, ROI/scales/sampling/preprocessing,
merge/score/ORB/threshold/protocol. Existing v1 model/GT contracts stay supported.
No independent test pixels or precise GT may be exposed before Model Lock; a
fresh natural test match and frozen GT require the next separate authorization.

Source code must be locally committed and clean before the first real scan.
The code-freeze check always runs Git at the repository root, regardless of the
launch directory. Reference Model Locks bind the complete actual RGB/uint8,
resize/interpolation, rotated working geometry, sampling, disabled NMS and
temporal postprocess parameters, not merely their ROI and FPS.
Do not change parameters after seeing real results. Outputs, crops, labels,
rankings, source hashes and protection inventories remain Git-ignored. No push,
main merge, model training, Module 3, Android or live operation is authorized.

## Dependency provenance

Pinned optional baseline dependency: opencv-python-headless 4.13.0.92,
with required NumPy 2.4.3, installed as Windows wheels into the existing venv.
No old dependency was upgraded. Actual package wrapper LICENSE.txt is MIT;
LICENSE-3RD-PARTY.txt begins with the bundled OpenCV Apache-2.0 terms and
retains additional notices. Wheel metadata's single Apache label is not the
complete licensing description. Installed notices remain with the package.

Primary references checked before implementation:
[package](https://pypi.org/project/opencv-python-headless/4.13.0.92/),
[template matching](https://docs.opencv.org/4.13.0/d4/dc6/tutorial_py_template_matching.html),
[ORB](https://docs.opencv.org/4.13.0/d1/d89/tutorial_py_orb.html).
Core Module 1 dependencies and extraction behavior are unchanged; OpenCV is an
optional `baseline` extra, not a requirement to read videos or validate legacy evidence.
