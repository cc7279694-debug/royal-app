# Module 1 Verification

Verification date: 2026-10-03. Implementation, synthetic tests, and representative
user-recording verification complete. **Module 1 Completed**; await user review
before advancing to Module 2.

## Scope

Local MP4 metadata, exact presentation-time frame selection, PNG and JSON export.
Safety-gate correction included. No recognition, Android, runtime game capture,
HUD, audio analysis, database, cloud upload, or machine-learning dependency.

## Actual Environment

- Windows 11 x64, reported build 10.0.26200.
- CPython 3.12.4, isolated root `.venv`.
- PyAV 19.0.1, Pillow 12.3.0, pytest 9.1.1.
- All tested dependency versions are pinned in
  [requirements-test.txt](../tools/offline_video/requirements-test.txt).
- Bundled FFmpeg libraries reported: libavutil 61.1.102, libavcodec 63.1.102,
  libavformat 63.1.102, libavdevice 63.1.102, libavfilter 12.1.102,
  libswscale 10.1.102, libswresample 7.1.102.
- PyAV and Pillow installed as Windows x64 wheels. Initial environment used a
  configured mirror, then every pinned dependency was reinstalled successfully
  using the explicit official `https://pypi.org/simple` index with
  `--only-binary=:all:`. No global changes or FFmpeg/PyAV source build.
- Project itself installed editable with no build isolation/dependency resolution;
  a distributable pure-Python wheel was also built under Git-ignored outputs.

## Test-First Evidence

Initial suite: 33 expected failures and one Git-ignore test passing, before
pipeline/CLI behavior existed. Real decoding then exposed side-data mapping and
unspecified pixel-aspect metadata handling; both were corrected.

Additional error tests exposed a missing per-target error reason on PNG write
failure. That failure was reproduced before correcting the report. A second
write-denial test verified that inability to save even the error report is
explicitly reported to the caller. Final suite: **47 passed**, with no outstanding
test failure.

Final commands executed from repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip wheel --no-deps --no-build-isolation --wheel-dir outputs/package-check tools/offline_video
```

Results: 47 passed; no broken requirements; wheel build successful.

## A. Synthetic Recording Validation

Real encoding/decoding uses PyAV and Pillow in temporary directories:

- 64 x 48 H.264 SDR, 10 average FPS, 0.4 seconds.
- Non-uniform millisecond PTS: 5000, 5070, 5210, 5500.
  Normalized frame times are 0, 0.07, 0.21, 0.5 seconds.
- Known colored fields and asymmetric white corner verify content/orientation.
- Request 0.15 selects 0.2; requests 0.06 and 0.065 both select 0.07.
- Candidate 0.2 against target 0.1 succeeds (exact 100ms);
  target 0.099 misses (101ms).
- A target after the last display frame is a miss, even inside the last frame's
  nominal duration. No final-frame fallback.
- Raw PTS, time_base, normalization origin, actual timestamps, errors, PNG names,
  dimensions, and JSON round-trip are checked.
- PNGs reopen correctly and match independent expected color values.
- Chinese/spaced paths; negative/NaN/infinite/duplicate/unsorted timestamps;
  absent/directory/empty/corrupt/audio-only input; input hashes and sentinel
  output preservation; output-is-file behavior are checked.
- Pure 0/90/180/270 rotations are tested with real MP4 display matrices.
- Arbitrary rotation, mirrored matrices, HDR transfer markers, and non-square
  pixels are tested using real encoded files and rejected explicitly.
- Unavailable optional FPS/duration metadata and cover-image stream selection
  have narrow metadata boundary tests.
- Missing PTS/time_base, duplicate/backward PTS, changing dimensions, and empty
  decode results are injected at the decoded-frame boundary of a real container.
  MP4 encoders normally prevent these states. Error reports preserve honest state.
- Write denial is injected at the PNG filesystem boundary; error is returned and
  recorded. This is not a claim of actual Windows ACL permission manipulation.
- Git-ignore behavior is checked with `git check-ignore` for local data,
  outputs, environments, Python caches, test caches, and builds.

Manual CLI: `inspect` ran on the synthetic CFR fixture and reported expected
metadata. Extraction reports were generated for CFR, VFR, and 90-degree input.

Visual inspection: the first red frame, selected blue frame, and 90-degree frame
were actually opened with the image viewer. Colors, complete dimensions and
white-corner position matched expected orientation. Other rotations are covered
by pixel-position tests, not claimed as individually visually inspected.

## B. User Recording Validation

**Passed — exactly the local MP4 explicitly supplied by the user was read.**
No private-directory search, source copy, or upload was performed. This public
record deliberately excludes its filename, private source path, player identities,
screenshots, and notifications.

- H.264, 448 x 960, no display rotation, duration 273.166333 seconds from video
  stream metadata; average FPS metadata approximately 30.000037.
- Full independent decode: 8,195 frames, origin PTS 0, time_base 1/90000,
  final relative presentation timestamp 273.133333 seconds. Timestamp spacing
  remained 1/30 second throughout.
- Successful requested times: 0, 1.5, 10, 60, 120, 180, 240, 272.9, 273.12 seconds.
  The first eight matched exactly; the last selected 273.133333 seconds, late by
  13.333ms (within the inclusive 100ms limit).
- Deliberate request at 274 seconds: miss, no PNG, null actual timestamp.
  Report correctly recorded partial status; a separate CLI boundary check
  explicitly confirmed exit code 3. This expected negative case is not a failure.
- Independent timestamp lookup via sorted decoded PTS and binary search matched
  all report selections/errors. Every successful PNG reopened at 448 x 960 and
  matched the independently decoded frame's RGB bytes exactly.
- First, 60-second, 240-second, and last selected PNG were actually opened and
  viewed. Portrait orientation, complete frame, and scene progression were correct.
  The recording includes menus at the start and system UI at the end; the tool
  correctly preserves these. Future detection must distinguish non-match frames.
- Original source SHA-256 before/after decoding and extraction was identical.
- PNGs and raw JSON reports reside only under Git-ignored local outputs.
  No gameplay/media bytes are included in this repository update.
- Full automated suite rerun after real recording validation: 47 passed.

The already documented synthetic tests remain the evidence for rotation variants,
variable frame rate, nonzero initial PTS, and malformed-input boundaries; this
single real recording does not establish those properties for every phone.

## Not Run / Not Applicable

- TypeScript / ESLint: Python-only module.
- Android build / device test: no Android application in this module.
- Recognition accuracy: no recognition implementation.
- Other phone recordings/codecs: not tested.
- Broader codec/HDR compatibility: not claimed.

## Dependency Provenance and Licenses

Dependency source and metadata checked against official package pages and
installed distribution metadata. Versions are pinned, not vendored.
The repository's own license remains undecided.

| Package | Version | License | Official source |
| --- | --- | --- | --- |
| PyAV | 19.0.1 | BSD-3-Clause | [PyPI](https://pypi.org/project/av/19.0.1/) |
| Pillow | 12.3.0 | MIT-CMU | [PyPI](https://pypi.org/project/pillow/12.3.0/) |
| pytest | 9.1.1 | MIT | [PyPI](https://pypi.org/project/pytest/9.1.1/) |
| setuptools | 84.0.0 | MIT | [PyPI](https://pypi.org/project/setuptools/84.0.0/) |
| colorama | 0.4.6 | BSD-3-Clause | [PyPI](https://pypi.org/project/colorama/0.4.6/) |
| iniconfig | 2.3.0 | MIT | [PyPI](https://pypi.org/project/iniconfig/2.3.0/) |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | [PyPI](https://pypi.org/project/packaging/26.3/) |
| pluggy | 1.6.0 | MIT | [PyPI](https://pypi.org/project/pluggy/1.6.0/) |
| Pygments | 2.21.0 | BSD-2-Clause | [PyPI](https://pypi.org/project/Pygments/2.21.0/) |

FFmpeg and bundled codec libraries have separate licenses; the PyAV code license
does not cover all linked libraries. No wheels or codec binaries are redistributed
in this repository; review the actual binary distribution before any app release.

References used: [PyAV current installation information](https://pypi.org/project/av/),
[frame PTS and time_base documentation](https://pyav.org/docs/stable/api/frame.html).
The older stable docs identify themselves as 9.0.2; installation/runtime versions
were therefore checked against PyPI and the actual installed 19.0.1 package.
