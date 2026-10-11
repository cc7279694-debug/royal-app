# Offline assisted candidate export

This independent presentation tool reads the existing frozen detector replay.
It does not load a model, train, read Event GT, replay or change the formal engine.
Its JSON is a list of review hypotheses, not confirmed `OpponentCardPlayed` events.
The App initializes separate pending review state for each candidate.

Using the existing offline environment from the repository root:

```powershell
.\.venv\Scripts\python.exe -B -m tools.assisted_tracking --replay <sealed-replay-directory> --config <match-config.json> --source <approved-recording.mp4> --match <match-id> --output <new-private-directory>
.\.venv\Scripts\python.exe -B -m pytest tools/assisted_tracking/tests -q --import-mode=importlib --tb=short
```

The sealed replay must contain exactly its five detector replay members plus
`manifest.json`; additional members are rejected before opening them. The config's
sibling `predictions.json`, config, recording and all replay members must match the
frozen source hashes. The explicit recording argument is checked against that
source binding. Inputs remain read only. Existing output directories are refused;
source overlap and linked paths are rejected. CLI errors omit private paths.

Selection is fixed: `owner=opponent`, nonnull `card_id`, and STRONG or MEDIUM engine
evidence. Every other match candidate contributes to one exclusion reason (owner,
unsupported mapping, insufficient evidence), in that order. The complete original
match inventory gets a canonical SHA-256. Repeated cards retain their original
candidate IDs. Filtering has no GT input and makes no accuracy or completeness claim.

For each candidate, first/middle/last distinct samples among its own source
observations supply at most three screenshot references. Exact source PTS/time-base
and native dimensions are verified during one decode of the approved source.
Shared selected frames use one image and the union of their supporting source
boxes. JPEGs preserve native dimensions; bbox coordinates are source-pixel xyxy.
Frame and evidence IDs are deterministic. Confidence is the maximum source detector
confidence across that candidate's observations, never a calibrated event score.
First appearance and engine confirmation times keep their frozen meaning; neither
proves physical deployment onset or owner/form/origin truth.

`candidates.json` uses `offline_assisted_candidates_v1`. Its exact root fields are
`schema`, `packet_id`, `match_id`, `provenance`, `candidates`, `evidence`, `summary`.
There are no review-decision fields. The strict validator checks fields, references,
counts, data URL bytes/JPEG dimensions and hashes. Limits are 24 MiB per packet,
128 evidence images and 512 KiB decoded JPEG bytes per image. A source frame that
exceeds these bounds causes rejection; no hidden resize or partial export is used.

The private directory also contains native `evidence/*.jpg`, a presentation-only
`contact-sheet.jpg`, and a SHA-bound content manifest. Raw screenshots may contain
personal game UI: keep them local/ignored and do not bundle them in source commits,
APKs or public review documents. JPEGs/contact sheets are display derivatives, not
pixel-verified annotation GT. Candidate-derived samples cannot prove exhaustive
miss/false-positive counts, detector accuracy, exact elixir or live-game performance.
