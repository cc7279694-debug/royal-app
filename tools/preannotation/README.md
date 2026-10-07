# Local proposal / human correction tool

This additive tool reads preserved offline predictions. It does not run a model,
train, update older GT locks, emit card events or connect to a game. It uses the
existing `.venv` PyAV, Pillow and pytest; the browser reviewer has no dependencies.

Run commands from the repository root. All generated material must stay private
under ignored `outputs/milestone1/`; use a fresh output/revision directory each
time. Existing directories are never replaced.

## Prepare the first retained recording

```powershell
.\.venv\Scripts\python.exe -m tools.preannotation prepare --out outputs/milestone1/match01-review-v1
.\.venv\Scripts\python.exe -m tools.preannotation validate --bundle outputs/milestone1/match01-review-v1
.\.venv\Scripts\python.exe -m tools.preannotation serve --bundle outputs/milestone1/match01-review-v1 --port 8765
```

Open `http://127.0.0.1:8765/`. You can also open the bundle's `review.html` directly
in a browser. The optional server is loopback-only, read-only and exposes only
integrity-checked bundle members. It has no upload endpoint; CSP blocks external
connections. Stop it with Ctrl+C when finished.

The defaults read the immutable KataCR `detections.json` / `probe-config.json`
from the preserved benchmark and the original retained inventory. Fixed stride
20 selects 12 frames at 12,17,...67 seconds, without selection by output quality.
Full source PNGs are decoded at exact `raw_pts` / `time_base`; source, config and
prediction SHA-256 bindings must pass. No annotated screenshot is used as input.
The bundle copies original teacher bytes and keeps their fields unchanged.

To use a later reviewer presentation with an already prepared bundle, create a
fresh view directory without decoding the source again:

```powershell
.\.venv\Scripts\python.exe -m tools.preannotation presentation --bundle outputs/milestone1/match01-review-v1 --out outputs/milestone1/match01-review-presentation-v2
```

This copies identical bundle JSON, teacher bytes and source PNGs, uses the current
reviewer assets, and seals a new file manifest. Original bundle/manifest files are
untouched; the data bundle SHA and human-return identity stay identical. Serve the
new directory to see the refreshed presentation.

Recording order is always 01,02,03,04. The newer explicit user declaration makes
02 truncated and training-excluded even when a historical pending inventory says
otherwise. It cannot supply negative training evidence. 04 remains exposed
development/DEV_TUNE material; this tool creates no blind split or qualification.

## Review and save a separate return

Choose a frame and proposal. Enter the human visual class, optional canonical
mapping, appearance identity, owner/form/origin, visibility and uncertainty.
Teacher owner and class remain visible as hypotheses; human fields start empty
or unknown. Labels use `visual.unit.*`, `visual.structure.*`, `visual.effect.*`,
`visual.ui.*` or `visual.other.*`. A mapping such as `unit.witch` is a separate
explicit human field; raw teacher names remain available.

- Accept: confirm the proposal with its original box.
- Reject: preserve the rejected area as unresolved; an invented class/identity
  is not required.
- Relabel: record a corrected human visual class with the original box.
- Correct box: use source-pixel xyxy coordinates; class can also be corrected.
- Missing box: drag on the source image, fill the human fields, then save it.

The reviewer stores decisions in page memory only. Download the separate JSON
before leaving. Give the actual reviewer identity and explicit review attestation.
No review identity, time or confirmation is fabricated by the tool.

Completeness is a separate per-frame, per-class human declaration. Acceptance of
one box does not establish full-frame coverage. Keep the unresolved checkbox on
when any class region remains unknown. Rejected, uncertain, unknown and untouched
proposals cannot become negatives. Class-specific negative evidence requires an
explicit exhaustive whole-source-frame declaration with zero class positives and
zero unresolved proposal regions (conservatively across all classes; a rejected
class hypothesis cannot exempt an area). All ordinary full-frame training exports remain
disabled: unmarked frame areas are still unreviewed, not background.

```powershell
.\.venv\Scripts\python.exe -m tools.preannotation validate --bundle outputs/milestone1/match01-review-v1 --return "C:/path/to/downloaded-human-return.json"
.\.venv\Scripts\python.exe -m tools.preannotation import --bundle outputs/milestone1/match01-review-v1 --return "C:/path/to/downloaded-human-return.json" --revision outputs/milestone1/match01-review-revision-v1
```

Imports validate before creating a new exclusive revision. They preserve the
downloaded return bytes and write `reviewed-annotations.json` plus a receipt.
Predictions, bundle and previous revisions are never edited. Reuse appearance
identities across frames; incompatible class/mapping/known metadata is rejected.
Repeated frames, boxes and spawned units never add independent deployments.
`training_qualified=false`, `ordinary_training_export_allowed=false` and empty
card events apply to every exported revision. Reviewed visuals are not a Training
Dataset Lock, detector accuracy acceptance or confirmed card plays.

## Synthetic operation check

```powershell
.\.venv\Scripts\python.exe -m tools.preannotation demo --out outputs/milestone1/synthetic-review-v1
.\.venv\Scripts\python.exe -m tools.preannotation serve --bundle outputs/milestone1/synthetic-review-v1/bundle --port 8766
```

The demo contains generated rectangles, three exact-PTS frames, all five
operations and repeated appearance continuity. It saves an explicit synthetic
round-trip. Browser downloads from its page are also forced synthetic. Validate
or import those with `--synthetic`; default real-GT import refuses them, and a
synthetic source cannot be attested into real GT. QA never needs fake human
confirmation of real KataCR proposals.

## Future prediction protocol

Use `prepare --format generic --predictions ... --config ... --inventory ...`.
The config records `source_recording`, its `source_sha256`, `underlying_match_id`
and optional `source_dimensions_wh`. Prediction JSON has
`schema=offline_predictions_v1`, the exact config file's `config_sha256`, and
`frames`. Each frame has integer `raw_pts`, rational-string `time_base`, optional
source-relative `timestamp_seconds`, and `detections`. Each detection contains
`class`, finite `confidence` in 0..1 and source-pixel `bbox_xyxy_original`; optional
raw teacher fields are retained. Missing or out-of-image PTS/boxes fail. Importing
new predictions still creates pending proposals and grants no training authority.

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest tools/preannotation/tests -q
node --test tools/preannotation/tests/reviewer.test.cjs tools/preannotation/tests/review-ui.test.cjs
```

Hashes catch changed bytes and accidental revision mix-ups; they do not prove
source authenticity or truthful human attestations, and are not an OS sandbox.
Private media/game assets are not redistributable because this tool can read them.
