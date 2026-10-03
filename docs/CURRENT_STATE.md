# Current State

Last verified: 2026-10-03

## Current Stage

Module 1 — Offline Video Pipeline: **Completed**.
Implementation, synthetic tests, and representative user-recording verification
are complete. Stop for user review; Module 2 has not started.

## Verified Completed

- Module 0 baseline exists at `e8f702b5ed7ec33c852357f0be62ce0a8e25d3cd`;
  this module branches from it rather than the unbootstrapped main branch.
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

- None. Awaiting user review of the completed Module 1 report.

## Pending

- User review of Module 1; explicit authorization before Module 2.
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

- Branch: `feat/offline-video-pipeline`
- Base: `e8f702b5ed7ec33c852357f0be62ce0a8e25d3cd`
- Remote: `https://github.com/cc7279694-debug/royal-app`
- Main remains unchanged. Exact module commit/push is reported in the handoff
  and verifiable in Git rather than embedded in its own commit.

## Next Recommended Task

Review Module 1 evidence. When authorized, plan Module 2's limited-card detection
experiment on offline footage, including match-region/time selection and model
provenance. Do not implement Module 2 before authorization.

See [verification evidence](VERIFICATION_M1.md) and [Windows instructions](../README.md).
