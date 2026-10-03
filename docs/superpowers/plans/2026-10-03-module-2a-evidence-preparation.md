# Module 2A Evidence Preparation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task after separate user approval. Steps use checkbox (`- [ ]`) syntax for tracking. No implementation is authorized by this planning handoff.

**Goal:** Prepare reviewed local evidence and report whether a single-card offline experiment has enough independent data.

**Architecture:** Reuse Module 1's exact-PTS extractor unchanged. Add small evidence preparation, validation and review helpers to its Python experiment package. Human review supplies boundaries, identity, owner and boxes; helpers never infer cards or emit gameplay events.

**Tech Stack:** Existing isolated Python 3.12, PyAV 19.0.1, Pillow 12.3.0, pytest 9.1.1 and standard library; no new dependencies.

**Spec:** [2026-10-03-module-2a-evidence-preparation-design.md](../specs/2026-10-03-module-2a-evidence-preparation-design.md)

## Global Constraints

- Only explicitly supplied local recordings; no private-directory discovery or uploads.
- All times use actual PTS/time_base relative to the first displayed frame; inclusive Module 1 100ms extraction tolerance remains unchanged.
- Schema version 1 and all entities/rules from spec section 5; unknown versions/fields and nonfinite numbers fail, never coerce or silently repair.
- Current target choice requires >=4 distinct manually verified opponent plays in one recording; no predefined Hog Rider.
- 2B requires >=2 independent complete matches, >=6 target plays, >=1 held-out whole match with >=2 plays, reviewed negatives and a pre-training locked split.
- Whole underlying matches and all their re-recordings stay in one split; whole source recordings and their non-match negatives also stay in one split.
- Media, hashes, actual labels and source paths stay in local_data/ or outputs/; public fixtures are entirely synthetic.
- No ML framework/model/data downloads, training, inference, Android/live/HUD, game control, cycle/elixir or OpponentCardPlayed production.
- No new database, GUI, package installation or changes to the existing video extraction algorithm.
- Begin only on a separately authorized feature branch from the accepted baseline; never automatically merge main or push without scope authorization.

## Review Focus

1. Same underlying match re-encoded under another name: manual group assignment and split collision rejection, Task 4.
2. Nonzero origin, VFR and rotation: frame coordinates and time derive from successful original PNG/export metadata, Tasks 1–3.
3. Ambiguous appearance or missing frames: cannot become verified evidence or raise data counts, Tasks 1 and 4.
4. Private paths, symlink/junction escape, existing output: reject without reading outside supplied paths or overwriting, Tasks 2 and 5.
5. UI/uncertain-target negatives and changed locked evidence: refuse conflicting labels or stale lock, Tasks 1 and 4.

## File and interface map

All files below are **future implementation**, not created by this round.

| File under tools/offline_video/ | Responsibility |
| --- | --- |
| src/clash_tracker_video/evidence_contract.py | strict JSON loading, EvidenceError, v1 entity/reference/time/box validation |
| src/clash_tracker_video/evidence_prepare.py | reuse extraction, safe local run, SHA check, indexed contact pages; no manual decisions |
| src/clash_tracker_video/evidence_annotations.py | reviewed pixel rectangle to normalized box; frame identity from export report |
| src/clash_tracker_video/evidence_review.py | manual whole-match split checks, evidence digest/lock, sufficiency report |
| src/clash_tracker_video/evidence_cli.py | prepare/validate/review/freeze commands; explicit status exits |
| tests/evidence_fixtures.py | programmatically created synthetic v1 entities and geometric/color PNGs |
| tests/test_evidence_contract.py | structural/referential/time/negative correctness |
| tests/test_evidence_prepare.py | index/PTS/rotation, paths/output/input preservation |
| tests/test_evidence_annotations.py | coordinates and original PNG identity |
| tests/test_evidence_review.py | unique plays, completeness, splits, lock and gate boundaries |
| tests/test_evidence_cli.py | end-to-end synthetic command/exit/report behavior |

Also update README.md, docs/CURRENT_STATE.md, docs/DEVELOPMENT_PLAN.md and create
docs/VERIFICATION_M2A.md after actual verification. No existing pipeline/CLI
refactor; run the new interface as `python -m clash_tracker_video.evidence_cli`.
Local source maps/evidence must be manually supplied, never committed.

### Task 1: Strict evidence contract

**Files:** create evidence_contract.py, tests/evidence_fixtures.py,
tests/test_evidence_contract.py from the map above.

**Interfaces:**

- `EvidenceError(Exception)` for invalid I/O/JSON evidence.
- `load_evidence(path: Path) -> dict[str, object]`: strict JSON; duplicates/nonfinite fail.
- `validate_evidence(doc: Mapping[str, object], export_reports: Mapping[str, Mapping[str, object]]) -> list[str]`: empty for valid, otherwise stable field-qualified errors; does not mutate.
- Fixture `synthetic_evidence(plays_per_match: tuple[int, ...] = (4, 2)) -> dict[str, object]`: all spec v1 entities, two synthetic hashes/groups and no gameplay imagery.

- [ ] Write failing tests: valid synthetic v1 returns []; version2/unknown fields/missing keys/bool-as-int/NaN/duplicate JSON keys fail; x=0.9,width=0.2 fails; x=0,width=1 succeeds; dangling recording/segment/play/frame fails.
- [ ] Add time/reference tests: origin_pts=5000, origin_time_base=1/1000, frame_pts=5210 gives timestamp0.21; timestamp0.2 fails; VFR never uses FPS; frames with miss status fail; a 90-degree64x48 input requires48x64 display dimensions. Overlap of a negative with verified or ambiguous target visibility fails. Draft/unknown owner/variant cannot become verified silently; duplicate frame references do not satisfy the three-frame requirement.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_contract.py -q`; expect import failure before implementation, then assertion failures as behavior is added.
- [ ] Implement exactly spec section5 using standard-library validation; use Fraction internally and absolute1e-6 tolerance for stored float timestamps. Preserve explicit ambiguity and error lists; JSON load limits16MiB to bound accidental huge labels.
- [ ] Rerun that test file and all Module1 tests; expect all pass, no media tracked.
- [ ] Commit only this task's source/tests: `feat(evidence): validate versioned local annotations`.

### Task 2: Local frame index and contact pages

**Files:** create evidence_prepare.py and tests/test_evidence_prepare.py.

**Interfaces:**

- Consumes existing `pipeline.inspect_video(path)` and `pipeline.extract_frames(path,times,output)` unchanged.
- `prepare_evidence(source: Path, output: Path, times: Sequence[float] | None = None) -> dict[str, object]`: exclusive ignored run; creates exports/report.json, index.json, contacts/page_0000.png etc. Default targets every5s plus final actual PTS. Optional explicit times follow Module1 ordering rules.
- index.json={schema_version:1,recording:RecordingDescriptor,export_report:"exports/report.json",frames:[{frame_id,requested_seconds,timestamp_seconds,raw_pts,time_base,image_path,image_width,image_height,status,reason}],contact_pages:[relative paths],status}. No public/source absolute path; include misses explicitly. A run records exactly one recording_id; explicit correspondence to contract records is required.

- [ ] Write failing tests using real synthetic MP4 from conftest: index times0/0.07/0.21/0.5 for nonzero-start VFR, actual not requested times; final display frame included; same raw frame not counted as a second occurrence; rotation preserved and original exports never resized.
- [ ] Add safety tests: input SHA before/after identical; existing sentinel output untouched; URL/UNC/traversal/symlink and Windows junction escape rejected; resolved output must stay in local_data or outputs. Missing source, corrupt input, gap>100ms and unwritable output preserve explicit errors/partial status.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_prepare.py -q`; expect failure without helper.
- [ ] Implement sequential PTS pre-scan for default final time, then reuse extraction into a new run; at most12 thumbnails/page, column count3, 224x480 fit preserving ratio, labels with actual time or miss reason. Never assign match/card/owner/review status. Treat images as images, not schema source; save new files exclusively.
- [ ] Run task tests and complete pytest; inspect synthetic contact page only; expect PNG/index metadata match exports and original source unchanged.
- [ ] Commit: `feat(evidence): prepare private timestamped frame indexes`.

### Task 3: Manual box conversion and frame references

**Files:** create evidence_annotations.py, tests/test_evidence_annotations.py.

**Interfaces:**

- `normalize_box(rect: tuple[float,float,float,float], image_size: tuple[int,int]) -> dict[str,float]`: input full-display pixel x,y,width,height, output normalized_bbox.
- `make_frame_annotation(entry: Mapping[str,object], *, annotation_id: str, recording_id: str, play_id: str, rect: tuple[float,float,float,float], review_status: str = "draft") -> dict[str,object]`: entry from successful Task2 index, copies frame_id and actual PTS/timebase/PNG dimensions and sets annotation_source=manual. No card identification, owner inference or approval automation.

- [ ] Write failing tests: (10,20,30,40) in100x200 -> {x:0.1,y:0.1,width:0.3,height:0.2}; negative/out-of-bounds/zero-size/nonfinite/bool values fail without clipping; image64x48 rotated90 uses48x64; miss/no-PTS/no-image entry fails; draft stays draft.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_annotations.py -q`; expect helper import failure.
- [ ] Implement pure conversion/reference helpers and reuse contract rules, not copied pipeline logic. Require restored full-image pixel coordinates, not contact-sheet or crop coordinates.
- [ ] Run task tests plus contract tests; confirm generated annotations validate against synthetic export reports.
- [ ] Commit: `feat(evidence): convert reviewed pixel boxes to local labels`.

### Task 4: Whole-match isolation, lock and sufficiency

**Files:** create evidence_review.py, tests/test_evidence_review.py.

**Interfaces:**

- `review_evidence(doc: Mapping[str,object], export_reports: Mapping[str,Mapping[str,object]]) -> dict[str,object]`: status=invalid/insufficient/ready, candidate_gate bool, experiment_gate bool, counts={independent_complete_matches,verified_plays,held_out_matches,held_out_plays}, reasons list; ready means data only, not permission to train.
- `evidence_digest(doc: Mapping[str,object]) -> str`: SHA256 of UTF8 sorted-key compact canonical JSON, exclude split_manifest; disallow nonfinite numbers.
- `freeze_split(doc: Mapping[str,object], *, locked_at: str) -> dict[str,object]`: returns a new document with reviewed split digest/UTC date locked; never overwrites disk or old lock. Allows creation of the first lock only after all gates except the lock itself pass; changing existing lock raises EvidenceError.

- [ ] Write failing boundary tests: (4) one-match -> candidate true, experiment false; (4,2) independent complete -> six total, two test, unlocked insufficient; same inputs frozen -> ready; (3,2) fails candidate/total; (4,1) fails six/test2; duplicate play_id or many annotations of one play do not increase play count. Ambiguous, rejected or missing>=3 reviewed frame evidence cannot count.
- [ ] Add isolation tests: same hash in train/test, same match_group with another filename/re-encode, shared recording, non-match negative moved to another split, mixed assignments -> invalid. require independence_reviewed and capture_complete verified; same recording's two matches cannot supply independent splits. Changed content/hash/target invalidates old lock; no auto-update. Entire review is non-mutating.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_review.py -q`; expect failure.
- [ ] Implement grouping/counting using manually verified identities, not inferred file count. Validate all referenced successful frames and negative coverage before counting. Require EvaluationFrame records at5FPS over each held-out match and its non-match intervals before locking: every extracted sample marked a verified positive box or reviewed target-absent, misses reported and blocking readiness; never infer absence from unlabeled frames. Require EvaluationProtocol from spec section5 before freezing, including development-only confidence selection and fixed prospective metrics. Store these only in local evidence JSON, not a detector.
- [ ] Run task tests then complete pytest; expect all pass, including intentionally insufficient inputs returning reasons rather than crashes. Add coverage test: one unreviewed held-out sample blocks freeze/ready.
- [ ] Commit: `feat(evidence): enforce match-isolated experiment readiness`.

### Task 5: CLI and reproducible synthetic end-to-end check

**Files:** create evidence_cli.py and tests/test_evidence_cli.py; update README.md.

**Interfaces:** `main(argv: list[str] | None = None) -> int` and module entry point.

- `prepare INPUT --output NEW_IGNORED_RUN [--times T ...]` -> Task2.
- `validate EVIDENCE --indexes INDEX ...` -> strict contract/reference checks.
- `review EVIDENCE --indexes INDEX ... --output NEW_REPORT` -> Task4 report.
- `freeze EVIDENCE --indexes INDEX ... --output NEW_LOCKED_JSON` -> validate/review then explicit first lock, never guess a split. freeze_split receives UTC now from CLI.
- Exit0=valid/prepared/ready/frozen; 2=invalid/I/O,3=partial extraction or valid-but-insufficient. Concise errors, no traceback/private absolute path in routine stdout. Outputs must resolve within ignored roots and use exclusive creation; use actual internal export reports referenced by indexes.

- [ ] Write failing tests executing synthetic prepare->manual draft fixture->validate->review->freeze: one match exits3 with independent-match reason; two valid reviewed groups freeze exits0; invalid box exits2; stale lock exits2; full source images/index privacy and output-sentinel protection remain intact. CLI freeze cannot bypass unreviewed coverage.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_cli.py -q`; expect module-not-found, then behavior assertions fail until implemented.
- [ ] Implement thin CLI composition only, no GUI or models. Document explicit manual JSON entry, pixel coordinates and version/PTS rules; freeze is not a training command.
- [ ] Run complete pytest and pip check; inspect actual synthetic index/contacts/results. README commands must use generic local paths, not the user's private file.
- [ ] Commit: `feat(evidence): add offline evidence review commands`.

### Task 6: Actual evidence review and Module 2A acceptance

**Files:** local_data/ or outputs/ only for actual records; update
docs/VERIFICATION_M2A.md, CURRENT_STATE.md and DEVELOPMENT_PLAN.md.

**Interfaces:** use Tasks1–5, spec v1 JSON and structured sufficiency report.
This is an integration/review deliverable, not a new recognition component.

- [ ] Add/run regression tests first: synthetic menus/results/system negatives excluded from match positives; repeated unit frames remain one play; unknown variant stays ambiguous; data insufficient does not authorize next module. Test expected lack of second match independently of the real recording.
- [ ] Using only separately approved supplied files, create a new local evidence run; check source hashes before/after; manually review boundaries/completeness/perspective and the four dragon episodes identified in planning. Assign distinct play IDs and reviewed boxes only where justified; don't pre-fill unobserved cards. Retain at least3 original annotated frames/play.
- [ ] Review non-match/target-absent intervals and all intended held-out samples. With this single recording report insufficient unless new independent recordings were explicitly supplied. Do not search for/download missing data or request training authorization as a substitute for evidence.
- [ ] Validate references/PTS/coordinates/negative ranges; run review and record its exit3 if insufficient. Freeze only if separate input additions satisfy every gate; evidence readiness does not authorize 2B.
- [ ] Run full pytest, pip check, git diff --check and tracked media/secret/path scans. Verify all private evidence is ignored. Record actual test totals/commands/results, files, data-layer nonchanges, remaining data needs and scope exclusions; do not copy private hashes or notifications into docs.
- [ ] Commit only source/docs/synthetic tests: `docs(evidence): verify module 2a preparation`; push only if authorized. Stop for user acceptance. No 2B execution, model training task or Module3 event code belongs to this plan.

## Plan self-review and handoff

Spec sections1–3/7/11 -> all constraints and Task6; section4 -> Tasks2/3/6;
section5/10 -> Tasks1–5; section6 -> Task3 manual helper, no GUI;
section8 -> Task4; section9 -> Task4 reviewed held-out coverage and frozen protocol,
not evaluation implementation. Section7 external route remains a gate, no downloads.
All five Review Focus failure classes have assigned tests. Public examples use
synthetic identities/geometry only; actual annotations and hashes never enter Git.

This plan is not executed. The user should review both documents before approving
Module 2A implementation. Native task-by-task execution is proposed because the
small helpers share a tight contract and reuse an already-tested decoder; no
subagent dispatch or new conversation is part of this task.
