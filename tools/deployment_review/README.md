# Module 3A — manual deployment-event review preparation

This small presentation packager receives **explicitly curator-selected** visual
anchors and context media. It does not select events, track entities, resolve
card semantics, run a detector, import human returns or create an Event GT Lock.
Module 1's extractor and the existing visual-review tools remain unchanged.

## Current task contract

- Goal: provide a local ZIP with video context, exact-PTS source frames, contact
  sheets, visual-GT references and a blank human return for about10–20 candidate
  windows. Candidate windows are not a count of independent deployments.
- Scope: presentation/validation code, synthetic tests, new ignored output and
  current-state documentation. Existing media, locks, environments and App stay
  immutable. No database or migration is needed.
- Stop: ready for human review; no confirmed `OpponentCardPlayed` or Event GT Lock
  until context is reviewed and the user explicitly attests the returned result.
- Verify: pending-only and boundary tests, repository-owned regressions, exact
  source PTS, ZIP/member checks, old-data SHA/membership and privacy checks.

## Usage

Use the existing offline-video environment; no new package is required:

```python
from pathlib import Path
from tools.deployment_review.bundle import write_bundle, zip_bundle

# plan: deployment_event_review_plan_v1 with manual anchors and already-prepared
# local context media; no detector/GT import is invoked.
write_bundle(plan, Path("outputs/new-context-media"), Path("outputs/new-review"))
zip_bundle(Path("outputs/new-review"), Path("outputs/new-review.zip"))
```

The output directory and ZIP must not exist. Paths are relative, local and
confined. The manifest SHA-binds all presentation members; this establishes file
consistency, not source-video authenticity or human-confirmed event truth.

The input carries original intake order, recording/underlying-match pairs,
bound visual-source SHA values, visual frame/object/appearance references and
pending card/owner hints. All candidates are `pending_human_review`,
`confidence=uncertain`, `evaluable=false`. `approximate_timestamp` is a visual
anchor, not an inferred spawn. Clip playback is presentation-only; source
PTS/time_base minus source origin is the timing authority.

## Human return and future event truth

Open `index.html`, watch each context MP4, inspect full-size source frames and
fill `event-review.csv` or `human-return.template.json`. Supported manual choices:
confirm, reject, uncertain, merge_duplicate; confirmation may correct card,
owner, form or timestamp. Record last-absent/first-visible bounds, uncertainty
and notes. When the deployment is outside a window, request wider context rather
than guessing or using first observation as the play time.

Human-return fields are a **draft interchange template**, not a GT validator or
freeze contract. This milestone deliberately provides no import/freeze command.
A later explicitly authorized return-validation step must verify corrections,
attestation, merges, evidence and new-deployment semantics before producing:
`event_gt_id`, underlying match/recording, approximate timestamp, owner, card,
form, visual classes/frame IDs, direct/grouped/uncertain type, evaluable,
human_confirmed/uncertain confidence and notes. Source visual groups, spawned
relationships and uncertainty reasons are preserved where available.

Persistent/reappearing units need one event, not one per frame. Minion/Royal Hog
units are not individually card plays; grouped card identity needs context.
Witch-spawned Skeleton cannot imply a Skeletons-card event. Own objects, unknown
owner, unresolved source-card mappings, rejected/uncertain candidates and omitted
areas never become opponent event GT or Negative automatically. ChatGPT visual
suggestions need explicit user attestation; ChatGPT is not a human reviewer.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tools/deployment_review/tests -q --tb=short
```

Run maintained Python suites separately using their existing import conventions.
Do not recursively collect ignored output archives or isolated upstream model
environments as this repository's tests.
