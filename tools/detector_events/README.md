# Offline detector-to-event baseline

Module 3C-1 accepts sealed local KataCR prediction files, converts them into
`VisualObservation`, and calls the existing frozen event engine. It does not
install/load models, train, connect to a game, or change the Android App.
The pinned local inference runtime and third-party weights remain private/ignored.

## Source boundary

Each prediction frame includes actual `raw_pts`, `time_base`, relative timestamp,
and original-image `bbox_xyxy_original`. The configuration binds the recording SHA,
dimensions, match identity and exact PTS origin. Prediction/config/recording hashes
are checked before and after loading; output directories cannot be reused.

The explicit class map is visual, not a card lookup. Unsupported/evolved labels
remain observations, not silently normalized into supported cards. Owner is an
unvalidated model prediction only when its categorical channel and string agree;
otherwise it is `unknown`. Origin remains `unknown` because the model has no
spawn-origin classifier. No human appearance identity or Event GT enters replay.
Identical same-frame boxes are excluded from unit counting with raw bindings kept.
Empty/unreviewed frames are **not** certified negative evidence.

## Replay, then score

From the repository root, using the existing offline environment:

```powershell
.\.venv\Scripts\python.exe -B -m tools.detector_events --sources <local-sources.json> --output <new-replay-directory>
```

The descriptor has only `sources`; each entry contains `predictions`, `config`,
`prediction_sha256`, `config_sha256`. It cannot contain GT input. The replay writes
a hash manifest, observation/raw bindings, candidates, tracks/episodes and events.
Only after sealing this output may the unchanged scoring command read Event GT:

```powershell
.\.venv\Scripts\python.exe -B -m tools.event_engine event-evaluate --replay <sealed-replay-directory> --gt-lock <local-event-gt-lock> --gt-sha <frozen-sha256> --output <new-evaluation-directory>
```

Evaluation exits `0` for the existing scoring PASS, `3` for a valid experiment
FAIL, `2` for invalid evidence. Inherited `oracle_*` artifact schema names do not
mean these detector observations were generated from human Oracle GT. The new
source summary explicitly identifies `katacr_prediction`.

`build_diagnostics()` is post-score only. It preserves the frozen score, reports
sampled-window coverage, raw class/owner support and possible causes, and retains
all unresolved/unscored events. Positive duplicates and explicit no-new-play
emissions remain failures even when an extra event is also listed as unscored.
No full-match FP/min, detector box AP/mAP, real-time latency, or cross-match positive
validation can be claimed from the existing sparse Event GT.

The engine currently permits supported opponent observations with unknown origin
and does not calibrate model confidence. STRONG is an engine evidence level, not
human-confirmed deployment or a product-ready card play. Predictions/tracks can
still be wrong; inspect the sealed diagnostics and visual review packet.

All real artifacts and display-only gameplay crops remain local/ignored. No
third-party weights, source video or GT is included in the public repository.
See [verification](../../docs/VERIFICATION_MODULE3C1.md).
