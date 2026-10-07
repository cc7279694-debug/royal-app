# Module 3A — manual deployment-event review and attested GT

The unchanged `bundle.py` presentation packager receives **explicitly curator-selected** visual
anchors and context media. It does not select events, track entities, resolve
card semantics, run a detector, import human returns or create an Event GT Lock.
The separate `event_gt.py` now validates explicitly user-attested decisions and
freezes an annotation-only v1 lock. It is not a tracker or detector. Module 1's
extractor and the existing visual-review tools remain unchanged.

## Current task contract

- Goal: preserve the original pending context ZIP and bind a separate explicit
  user return to a new immutable Event GT Lock. Candidate windows and visual
  objects are not a count of independent deployments.
- Scope: presentation/validation code, synthetic tests, new ignored output and
  current-state documentation. Existing media, locks, environments and App stay
  immutable. No database or migration is needed.
- Stop: after validating the newly authorized Event GT Lock. Never enter Module
  3B automatically; original pending source files are not rewritten as GT.
- Verify: pending-only and human-return boundary tests, repository-owned
  regressions, source bindings, lock readback/overwrite refusal, old-data
  SHA/membership and privacy checks.

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

## Human review and separate event truth

Open `index.html`, watch each context MP4, inspect full-size source frames and
fill `event-review.csv` or `human-return.template.json`. Supported manual choices:
confirm, reject, uncertain, merge_duplicate; confirmation may correct card,
owner, form or timestamp. Record last-absent/first-visible bounds, uncertainty
and notes. When the deployment is outside a window, request wider context rather
than guessing or using first observation as the play time.

The original bundle's `human-return.template.json` remains a **pending draft
interchange template**, not confirmed truth, and is never overwritten. After
explicit user authorization, `event_gt.py` accepts a separate
`deployment_event_human_return_v1` with the entire pending source plan bound by
canonical digest and its supplied file SHA. The caller must check the raw source
file SHA separately; the embedded snapshot cannot authenticate source bytes.

Each of the original candidates must have exactly one explicit decision:
`confirm`, `uncertain`, `continuity` or `merge_duplicate`. Confirmation requires
opponent evidence, supported visual/card mapping, form, direct/grouped type,
human-confirmed confidence and an approximate time inside the reviewed window.
Continuity may refer to an earlier unresolved candidate without resolving its
deployment onset. A duplicate must refer to an earlier confirmed event in the
same underlying match. Neither decision adds a new event or Negative evidence.
The locked human return carries `reviewer=user`, explicit human confirmation and
attestation, `review_basis=chatgpt_visual_review` and
`confirmation_source=user_attestation_based_on_chatgpt_visual_review`.

```python
from pathlib import Path
from tools.deployment_review.event_gt import build_lock, freeze_lock, load_lock

# Read/check the original source and separate explicit user return first.
lock = build_lock(plan, human_return)
path = freeze_lock(lock, Path("outputs/new-event-gt/deployment_event_gt.lock.v1.json").resolve())
assert load_lock(path) == lock
```

The explicit parent directory must already exist. Freeze uses exclusive creation,
rejects symlink/junction paths and refuses an existing sibling lock with the same
source/freeze-version identity, even if renamed. Loading uses bounded strict JSON
and recomputes both digest and derived event/continuity/unresolved semantics.
Only v1 is currently implemented; a future revision needs separate authorization.
This is manual annotation/file consistency, not an automatic tracker, source
authenticity proof, detector performance or full-match event coverage. It does
not invent exact onset intervals from approximate human times.

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
