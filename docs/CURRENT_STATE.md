# Current State

Last verified: 2026-09-26

## Current Stage

Module 0 — Project Bootstrap

## Verified Completed

- The local checkout is connected to `cc7279694-debug/royal-app`.
- The project identity, product boundaries, safety constraints, development
  sequence, and accepted initial decisions are documented.
- No application, Android, video-processing, detection, or model code exists.
- No database, migration, file-storage, cloud, or deployment infrastructure exists.

## In Progress

- None. Module 0 is complete and awaiting user acceptance.

## Pending

- User acceptance of Module 0.
- Module 1 — Offline Video Pipeline.
- Selection of a proof-of-concept language and video library during Module 1.
- Selection of model architecture and runtime after video ingestion is proven.
- Selection of a repository license.

## Current Risks and Unknowns

- No representative user recording has been provided, so video formats,
  resolutions, frame rates, orientations, and UI variants are unknown.
- Recognition feasibility and accuracy have not been measured.
- Dataset and game-asset rights require review before any training material is
  added or distributed.
- Live online-match analysis remains outside the approved scope and cannot be
  represented as free of account risk.

## Git

- Branch: `feat/bootstrap-clash-tracker`
- Base: `main` at the repository's initial commit
- Remote: `https://github.com/cc7279694-debug/royal-app`

## Next Recommended Task

After Module 0 acceptance, implement only Module 1: a minimal offline tool that
opens a user-provided MP4, reports metadata, seeks to requested timestamps, and
exports selected test frames. It must not perform card recognition.
