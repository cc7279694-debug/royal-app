# Current State

Last verified: 2026-10-04

## Current Stage

Module 1 — Offline Video Pipeline: **Completed and user accepted**.
Module 2A1 — Current Recording Evidence: **Completed and formally user accepted
on 2026-10-04 at `98037ceba81683ad1a2c214bada30a10f2f3f69e`**.
Acceptance includes the current recording's manual evidence with eight unknown
intervals retained. Candidate gate true; experiment gate false; insufficient.
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

## Module 2A1 Verified Evidence

- prepare / validate / review implemented without changing Module 1 decoding/CLI.
- Strict local v1 evidence, stable frame identities, index conflict checks,
  full-image box helpers, interval gaps and conservative insufficiency reporting.
- User supplied whole-recording playback review, completeness, perspective and
  four distinct opponent normal Inferno Dragon deployment leads. Executor
  inspected original onset, movement, disappearance and boundary frames; no
  continuous playback by executor is claimed.
- Four verified deployments and 12 distinct original key-frame boxes entered
  into ignored local evidence; onset brackets and sampled visibility endpoints
  retain uncertainty. Candidate gate true; experiment gate false; insufficient.
- Three new fine-extraction runs succeeded; source hash unchanged; real validate
  exits 0 and review exits 3. Eight unknown timeline gaps remain, never negatives.
- Reviewed selection/result/transition/system-UI negatives include the exact
  terminal timestamp. Broad battlefield absences are not certified from sparse
  frames or a rough user form. Local labels/media were not published.
- Pre-repair regression: 145 passed, 1 symlink-permission skip; pip check passed.
  Real Windows junction escape regression passed. Independent branch review
  found three Important issues, reproduced/fixed with RED/GREEN and full regression.
  Minor nested advisory gap validation remains documented technical debt.
- This continuation changed no tracked tool code, tests or dependencies.
  Whole-playback review is attributed to the user; static frame review and
  coordinate annotations are attributed to the executor.
- Subsequent acceptance review found missing report/index request pairing and
  time-relation validation. The authorized local repair adds these checks in
  load_indexes before frame merging, with synthetic RED/GREEN regressions.
  Success retains inclusive 100ms; legal timeout/EOF misses and partial runs
  remain accepted using narrow float-rounding compatibility, not extra tolerance.
- Final repair regression: 223 passed, 1 symlink-permission skip; dependency and diff
  checks passed. Four existing export reports / 533 raw requests / 402 unique
  successful frames revalidated; actual validate/review exits 0/3 and all gates,
  four deployments, 12 boxes and eight unknown gaps unchanged. Hashes of 591
  explicitly referenced original files unchanged; new report kept local/ignored.
  No new extraction, playback, labels, dependencies or Module 1 producer changes.
- Independent read-only repair review found one Important cross-request time
  contradiction. Backwards candidates and skipping a known eligible candidate
  reproduced with three RED/GREEN tests and were fixed in one pass; final full
  regression and real evidence/hash recheck passed. No Critical/new Minor;
  no second independent review or media-authenticity certification claimed.

## Pending

- Module 2A1 Tasks 1–4 and the report/index repair are formally accepted.
  The user separately authorized only a four-document acceptance commit,
  feature-branch push, ff-only integration/push to main and branch preservation.
  Integration outcome is recorded in Git and the final handoff; this authorization
  does not approve planning or implementing a next module.
- Only one observed match is available. Inferno Dragon passes the current
  candidate gate with four distinct deployments and three key boxes each.
  This does not establish detector accuracy or complete negative coverage.
- Unknown gaps and sampled endpoint uncertainty remain explicit. Further
  interval review is needed before whole-timeline model scoring; no dense
  5FPS manual annotation inventory was created.
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
- Report/index consistency is not proof of source-video authenticity or first
  eligible source-frame selection without decoding. Coherent forgery and lost
  sub-ULP request precision cannot be independently ruled out by this patch.
- Nested preparation_report.coverage_gaps advisory validation remains deferred;
  it cannot override recomputed counts, gates or gaps. The symlink permission skip
  remains a limitation, distinct from passing real Windows junction tests.
- Formal acceptance used remote code/test-design review plus committed local
  verification. ChatGPT did not independently rerun the 223 tests or access
  private footage/evidence; no independent private-media certification is claimed.

## Git

- Preserved implementation branch: `feat/module-2a1-current-recording-evidence`
- Pre-integration main baseline: `35653db3f50b756a53aa6a27c7d9de632c808b89`
- Remote: `https://github.com/cc7279694-debug/royal-app`
- Accepted repair commit: `98037ceba81683ad1a2c214bada30a10f2f3f69e`, verified
  published on the implementation branch; repair baseline was `13330de9967b2c15af64d8b829be7431b6b10181`.
- Integration target: main, ff-only after fresh full regression/dependency checks.
  Exact acceptance-document commit and final local/remote refs are reported by Git
  and the final handoff, not inferred from permission. Keep the original branch.
- No PR, release, branch deletion, history rewrite or next module is authorized.
- No new dependency, SQLite, Android, inference, split/freeze or network runtime.

## Next Recommended Task

Stop after the authorized acceptance recording and integration. Do not request a
second recording or begin another module in this task. Commands remain prepare /
validate / review only. Any future independent-recording, split-freeze or model
work needs a separate user-approved Astra planning step and explicit module
authorization; Module 2A2 remains unapproved and 2B gates remain closed.
Public summaries contain candidate names/counts/gates only; individual times,
boxes and actual labels remain local and ignored.

See [Module 2A1 verification](VERIFICATION_M2A1.md),
[Module 1 evidence](VERIFICATION_M1.md) and [Windows instructions](../README.md).
