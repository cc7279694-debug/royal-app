# Current State

Last verified: 2026-10-03

## Current Stage

Module 1 — Offline Video Pipeline: **In Progress**.
Implementation and synthetic validation complete; representative user-recording
acceptance is pending. Module 2 must not start.

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
- No Android, recognition, model, database, cloud, or game-connection code exists.

## In Progress

- Module 1 real-recording acceptance.

## Pending

- User-provided `local_data/recordings/sample.mp4` (not present at verification).
- Inspect and extract that recording; validate time, dimensions, orientation,
  PNG content, and JSON before considering Module 1 accepted.
- User acceptance of Module 1 after representative recording verification.
- Model/runtime selection remains deferred; project license remains undecided.

## Current Risks and Limitations

- Synthetic H.264 8-bit SDR tests do not establish compatibility with every phone.
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

Provide a 30–60 second local MP4 of an already completed match replay at normal
speed. Run Module 1 against that file and review the PNGs/report. Keep Module 1
In Progress until this acceptance is verified.

See [verification evidence](VERIFICATION_M1.md) and [Windows instructions](../README.md).
