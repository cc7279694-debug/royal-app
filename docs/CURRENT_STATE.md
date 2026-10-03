# Current State

Last verified: 2026-10-03

## Current Stage

Module 1 — Offline Video Pipeline: **Completed and user accepted**.
Module 2A1 — Current Recording Evidence: **Lightweight plan revised; not implemented**.
Module 2A2 — Independent Data and Split Freeze: **Not approved; deferred**.
Module 2B and Module 3 have not started.

## Verified Completed

- Module 0 baseline exists at `e8f702b5ed7ec33c852357f0be62ce0a8e25d3cd`;
  Module 1 originally branched from it. Both modules are now on accepted main.
- Safety gate corrected: explicit Supercell permission covering specific behavior,
  version, and usage context is required before live online-match analysis or HUD.
  Risk acceptance and passive capture do not substitute for permission.
- Windows Python offline tool provides `inspect` and `extract`.
- Extraction uses real PTS/time_base relative to the first display frame,
  inclusive 100ms tolerance, PNGs, and per-target JSON success/miss/error states.
- Input and existing output files are protected; generated media and environments
  are excluded from Git.
- 47 automated tests passed on Windows using real encoded synthetic MP4s.
- Dependency integrity check and Python wheel build passed.
- Selected synthetic PNGs were visually inspected.
- User-provided H.264 MP4 (448 x 960, 273.166333 seconds, approximately 30 FPS)
  decoded completely: 8,195 frames, nine successful extraction targets, maximum
  lateness 13.333ms. A deliberate out-of-range target correctly missed.
- All nine PNGs matched independently decoded pixel data; start, middle, and
  end images were visually inspected. Input SHA-256 remained unchanged.
- Partial-miss CLI exit code 3 verified; all local PNG/report outputs ignored by Git.
- No Android, recognition, model, database, cloud, or game-connection code exists.

## In Progress

- None. This task stops at the revised Module 2A1 design/plan handoff.

## Pending

- Review revised Module 2A1 design and four-task plan; separate approval required.
- Only one observed match is available. Inferno Dragon remains a pending-review
  candidate, with at least four provisionally identified independent appearances.
  Ownership, variants and absence/spawn/visibility need re-review; no finalized
  annotations or formal candidate-gate acceptance exists.
- Planned boxing is 3–5 distinct key frames per verified play (12–20 for four
  surviving plays), plus whole-match interval review; no dense 5FPS manual labels.
- Split assignments, Evaluation Protocol, digest/lock and freeze CLI belong only
  to separately approved Module 2A2 after a second independent complete match.
- Module 2B requires at least two independent complete matches, six verified plays
  total and a whole held-out match with two plays. Current data are insufficient.
- Model/runtime selection remains deferred; project license remains undecided.

## Current Risks and Limitations

- Synthetic and one real H.264 recording do not establish compatibility with every phone.
- User recording includes non-match screens at its beginning and end; future
  recognition work must distinguish match footage from menus/system UI.
- Pure 0/90/180/270 rotation is supported; other display transforms, non-square
  pixels, HDR markers, and high-bit-depth frames are explicitly rejected.
- Sequential decoding scans the entire video; no random-seek optimization.
- Missing optional metadata is reported as unknown. Missing required timestamps,
  non-increasing PTS, or changing dimensions fail explicitly.
- Undeclared color properties and silent decoder concealment cannot be certified
  from available metadata; no blanket format/integrity guarantee.
- No feature is enabled for use during live online matches.

## Git

- Branch: `feat/plan-module-2a-evidence`
- Base/main: `e30ca01fb7a70a0f3bfc14e4fb838dd7ff0da491`
- Remote: `https://github.com/cc7279694-debug/royal-app`
- Main fast-forward and push verified on 2026-10-03; original feature branch kept.
- Before merge: 47 tests passed, pip check passed, whitespace/media/targeted secret
  scans passed. New planning commit/push is reported in the handoff and Git.
- Planning branch is not merged; no product code or new dependency changed.
- This revision changes five planning/state documents only. No new private media
  was read, no dependency installed, no main merge or implementation performed.

## Next Recommended Task

Review [Module 2A design](superpowers/specs/2026-10-03-module-2a-evidence-preparation-design.md)
and [implementation plan](superpowers/plans/2026-10-03-module-2a-evidence-preparation.md).
When separately authorized, implement only Module 2A1 and report honest insufficiency
with current one-match evidence. Commands are prepare / validate / review only.
No new recording or software installation is requested during this planning round.
Further independent recordings and separate Module 2A2 approval will be needed
before Module 2B can be approved. Public summaries contain candidate names/counts/
gates only; individual times, boxes and actual labels remain local and ignored.

See [verification evidence](VERIFICATION_M1.md) and [Windows instructions](../README.md).
