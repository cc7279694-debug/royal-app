# Clash Tracker

## Purpose

Clash Tracker is a local-first research project for analyzing user-provided
Clash Royale match recordings. The project will test whether computer vision
can reliably turn visible opponent deployments into structured card-play
events, which can later support match history, card-cycle analysis, and
uncertainty-aware elixir estimates.

The immediate product is an offline analysis tool. A live Android assistant is
only a possible later direction and is not an approved current capability.

## Intended User

The initial user is a single Android player who wants automatic match analysis
without manually recording cards and without compromising normal game input or
account safety.

## Core Problem

The primary technical risk is whether one real opponent deployment can be
detected accurately and emitted once, rather than repeatedly detecting the same
on-screen unit across multiple frames.

## Product Principles

- Account safety takes priority over feature scope.
- Begin with user-provided recordings and test footage.
- Keep core processing local and functional without a cloud service.
- Prove recognition reliability before connecting game input to a complete App.
  A separately authorized mock-only App prototype may develop in parallel.
- Report uncertainty honestly; estimates must not be presented as exact facts.
- Prefer simple, testable modules over premature abstraction.

## Planned Capabilities

- Read recorded match video and select frames by timestamp.
- Detect a deliberately small initial set of opponent cards.
- Confirm deployments across frames and emit one event per play.
- Record known cards and inferred card order.
- Estimate an opponent elixir range from confirmed events and match timing.
- Evaluate on-device Android capture only after the offline pipeline is reliable.

## Non-Goals

The project must not:

- modify, patch, hook, inject into, or reverse engineer the Clash Royale client;
- read game memory, intercept game network traffic, or simulate its protocol;
- use AccessibilityService, synthetic input, or automation to control gameplay;
- click, place cards, or play matches for the user;
- implement bots, reinforcement-learning control, or automatic strategy execution;
- make cloud services necessary for core analysis;
- claim that live-match use is account-safe without current, explicit evidence.

## Safety Boundary

The current authorized input is limited to recordings and test footage supplied
by the user. Live online-match analysis and an overlay are gated future topics,
not part of the current product. They must remain disabled without explicit
Supercell permission covering the specific tool behavior, version, and usage
context. Passive capture, local execution, alternate accounts, training-ground
tests, and user risk acceptance cannot substitute for permission. Even with
permission, its scope must be reassessed; zero ban risk must never be promised.

Relevant official policies:

- [Supercell Terms of Service](https://supercell.com/en/terms-of-service/)
- [Supercell Safe and Fair Play Policy](https://supercell.com/en/safe-and-fair-play/)

## Architecture Direction

The intended domain flow is:

```text
Recorded Video / Approved Test Screen
                 |
                 v
          Frame Processor
                 |
                 v
      Opponent Card Detector
                 |
                 v
       Deployment Tracker
                 |
                 v
       OpponentCardPlayed
            /          \
           v            v
    Card History   Cycle / Elixir
           \            /
            v          v
          Analysis Result
```

The detector produces observations. Only the deployment tracker may promote
confirmed observations into `OpponentCardPlayed` events. Card history, cycle,
and elixir modules consume those events rather than model output directly.

## Technology Direction

Verified constraints:

- Android is the intended eventual device platform.
- Core analysis should run locally.
- Android gameplay control is forbidden.

Candidate technologies, not yet selected:

- Native Android plugins for separately approved capture/local inference;
- MediaProjection for a future, separately approved capture experiment;
- YOLO with ONNX Runtime, TensorFlow Lite, or another suitable on-device runtime.

The offline proof of concept will determine the model format and Android runtime.
No inference framework is currently an accepted dependency.

The authorized simulated UI/App prototype uses React, TypeScript, Vite and
Capacitor, with bundled offline assets and in-memory mock events only. Its small
HUD is inside its own Activity, not a game overlay. This selection does not
require future screen capture or inference to run in Web; those may use native
Android plugins after separate authorization and the existing safety gate.

## Open-Source References

- [Clash Commander](https://github.com/youssofal/Clash-Commander): Android
  capture, local inference, and overlay architecture. Only appropriately
  licensed, non-automation concepts are relevant.
- [CR Vision](https://github.com/bytkim/cr_vision): deployment confirmation,
  spatial tracking, cycle, and elixir concepts. Its repository currently has no
  declared license, so its source must not be copied.
- [KataCR](https://github.com/wty-yy/KataCR): computer-vision and dataset ideas;
  its gameplay automation and reinforcement-learning scope is excluded.
- [Clash Royale Detection Dataset](https://github.com/wty-yy/Clash-Royale-Detection-Dataset):
  candidate data-generation reference. Dataset contents and asset rights must be
  reviewed before use.

Third-party repository licenses do not grant rights to Supercell trademarks or
game assets. Every dependency, code import, model, and dataset requires its own
provenance review before entering this repository.

## Constraints

- No server, account system, Supabase, or Vercel dependency is currently needed.
- Match recordings, extracted frames, model weights, and generated datasets are
  not source files and must not be committed by default.
- This public repository currently has no project license. Licensing remains an
  explicit product decision.
