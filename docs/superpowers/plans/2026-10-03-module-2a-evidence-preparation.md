# Module 2A1 Current Recording Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans after separate implementation approval. Steps use checkbox (`- [ ]`) syntax. This revision authorizes documents only; do not execute this plan now.

**Goal:** Prepare small local key-frame/interval evidence and honestly report current data insufficient for a single-card experiment.

**Architecture:** Reuse Module1 extraction unchanged. Three small helpers cover contract, preparation and annotation/review, plus a thin three-command CLI. Humans supply identity, owner, match boundaries and complete reviewed visibility intervals; no card detector.

**Tech Stack:** Existing Python3.12, PyAV19.0.1, Pillow12.3.0, pytest9.1.1 and standard library; no new dependencies.

**Spec:** [Revised2A design](../specs/2026-10-03-module-2a-evidence-preparation-design.md)

## Global Constraints

- Execute2A1 only after approval;2A2 has no approval or implementation tasks here.
- Commands: prepare, validate, review. No freeze, split lock, canonical digest or Evaluation Protocol implementation.
- Only supplied local media, ignored outputs and synthetic public tests; never publish private timestamps/paths/hashes/boxes/screenshots.
- Exact PTS-normalized times, unchanged inclusive100ms extraction tolerance; no FPS-derived times or game countdown.
- Three to five distinct-timestamp original key frames per verified play, not manual labels for every5FPS inference frame.
- candidate_gate>=4 distinct reviewed opponent plays in one recording; Inferno Dragon is a pending-review candidate.
- Current one-match data return insufficient; independent full-match isolation/pre-training test lock remain future2A2/2B gates.
- No inference, ML downloads/training, Android/live/HUD, game interaction, events, custom GUI, database or dependency installation.

## Review Focus

1. Final frame equals negative endpoint: terminal-negative closure only, Task1.
2. NonzeroPTS/VFR/rotation: original times/display coordinates, Tasks1–3.
3. Duplicate key exports: one play counts once;3–5 different times required, Tasks1/3.
4. Path escape/existing output/private data: reject and preserve, Tasks2/4.
5. Ambiguous visibility/variant: cannot become negative or verified implicitly, Tasks1/3.

## Future file map

All paths below are relative to tools/offline_video/. None are created by this revision.

| File | Owner / responsibility |
| --- | --- |
| src/clash_tracker_video/evidence_contract.py | Task1: EvidenceError, strict JSON/v1 validation, interval membership |
| src/clash_tracker_video/evidence_prepare.py | Task2: safe extraction/index/contact pages and source integrity |
| src/clash_tracker_video/evidence_review.py | Task3: box conversion, annotation references, unique-play counts/gaps/insufficiency |
| src/clash_tracker_video/evidence_cli.py | Tasks2/3: thin prepare/validate/review dispatcher |
| tests/evidence_fixtures.py | Task1: synthetic six-entity v1 fixtures |
| tests/test_evidence_contract.py | Task1: structure/time/interval/reference tests |
| tests/test_evidence_prepare.py | Task2: synthetic real MP4/index/output/contact tests |
| tests/test_evidence_review.py | Task3: boxes/counts/gates/gaps |
| tests/test_evidence_cli.py | Tasks2/3: synthetic command/exit tests |

Task4 updates README.md, docs/CURRENT_STATE.md, docs/DEVELOPMENT_PLAN.md and creates
docs/VERIFICATION_M2A1.md after verification. Keep pipeline.py and Module1 CLI
unchanged. No separate annotations/split module or dense evaluation-frame list.

### Task 1: Simplified evidence contract and tests

**Files:** evidence_contract.py, tests/evidence_fixtures.py, tests/test_evidence_contract.py.

**Interfaces:**

- EvidenceError(Exception); load_evidence(path: Path) -> dict[str,object]: strict JSON,16MiB cap.
- validate_evidence(doc: Mapping[str,object], indexes: Mapping[str,Mapping[str,object]]) -> list[str]: field-qualified errors; empty if valid, no mutation. Indexes keyed by recording_id, contain successful export metadata from Task2; fixtures provide equivalents.
- interval_contains(t: Fraction, start: Fraction, end: Fraction, *, last_frame: Fraction, terminal_negative: bool = False) -> bool: ordinary start<=t<end; close endpoint only when terminal_negative=true AND end==last_frame.
- synthetic_evidence(plays: int = 4) -> dict[str,object]: one recording/segment, synthetic card, plays with3 distinct successful key references each, reviewed intervals; no game imagery.

- [ ] Write failing tests for six required entities, optional version1/report, missing keys/dangling references, bool-as-int, NaN/duplicate keys/oversize JSON. Reject deferred root objects. No split manifest needed for valid2A1 evidence.
- [ ] Add boundary test assertions exactly:

```python
F = Fraction
assert not interval_contains(F(1), F(0), F(1), last_frame=F(1))
assert interval_contains(F(1), F(0), F(1), last_frame=F(1), terminal_negative=True)
assert not interval_contains(F(1, 2), F(0), F(1, 2), last_frame=F(1), terminal_negative=True)
```

- [ ] Add nonzero origin5000ms/frame5210ms ->0.21s (stored0.2 invalid); VFR without FPS;90-degree64x48 ->48x64; x0.9+width0.2 invalid/full-image box valid; negative overlapping verified/ambiguous visibility invalid; repeated actual timestamp cannot satisfy three key frames. Positive end remains half-open even at last frame.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_contract.py -q`; expect initial import/behavior failures.
- [ ] Implement spec sections4/5 only, with Fraction membership and1e-6 timestamp consistency. Preserve drafts/ambiguity; no target guessing or deferred objects.
- [ ] Rerun task and Module1 tests; expect all pass with synthetic fixtures only.
- [ ] Commit: `feat(evidence): validate lightweight key-frame evidence`.

### Task 2: Local index, contact pages and safe output

**Files:** evidence_prepare.py, evidence_cli.py, tests/test_evidence_prepare.py,
tests/test_evidence_cli.py. Uses Task1 contract; no identity/inference logic.

**Interfaces:**

- Consume existing pipeline.inspect_video(path) and pipeline.extract_frames(path,times,output) unchanged.
- prepare_evidence(source: Path, output: Path, *, recording_id: str, times: Sequence[float] | None = None) -> dict[str,object]: new ignored run, exports/report.json, index.json, contacts/page_0000.png. Default every5s plus last actual PTS; explicit times permit fine candidate windows.
- Index={schema_version:1,recording:RecordingDescriptor,export_report:"exports/report.json",frames:[{frame_id,requested_seconds,timestamp_seconds,raw_pts,time_base,image_path,image_width,image_height,status,reason}],contact_pages:[relative paths],status}. Preserve misses/partial status; source path stays in separate local map. Same recording_id across finer runs; repeated timestamp remains one frame of a play.
- evidence_cli.main(argv: list[str] | None = None) -> int; entry `python -m clash_tracker_video.evidence_cli`. Commands `prepare INPUT --recording-id ID --output NEW_RUN [--times T ...]` and `validate EVIDENCE --indexes INDEX ...`. Only supplied ignored indexes/reports; combine same-recording frames with checked metadata agreement. Resolve images relative to supplied run, never arbitrary private directories.

- [ ] Write failing synthetic encoded MP4 tests: VFR/nonzero-start actual times0/0.07/0.21/0.5, finalPTS included, rotation preserved; contacts keep ratio/actual labels, never change original PNGs; source SHA before/after identical.
- [ ] Test URL/UNC, traversal and symlink/junction/ancestor escape, sentinel/existing-output and write failure; outputs must resolve within local_data or outputs and be exclusively new. Partial misses stay explicit, no last-frame fallback. Confirm private outputs Git-ignored. CLI invalid input exits2 without traceback/private source path.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_prepare.py tools/offline_video/tests/test_evidence_cli.py -q`; expect failures before helpers exist.
- [ ] Implement PTS pre-scan for default last time, reuse extraction and create max12 thumbnails/page,3 columns, fit224x480. No automatic match/card/owner review. Thin prepare/validate dispatch, exit0 success/valid,2 invalid/I/O,3 partial.
- [ ] Rerun task and full tests; visually inspect synthetic contacts; check source/sentinel preservation and metadata.
- [ ] Commit: `feat(evidence): prepare private frame indexes and contacts`.

### Task 3: Deployment intervals, key-frame boxes and sufficiency

**Files:** evidence_review.py, tests/test_evidence_review.py; extend evidence_cli.py
and tests/test_evidence_cli.py only with review.

**Interfaces:**

- normalize_box(rect: tuple[float,float,float,float], image_size: tuple[int,int]) -> dict[str,float]: full displayed pixel x/y/width/height ->normalized_bbox.
- make_frame_annotation(entry: Mapping[str,object], *, annotation_id: str, recording_id: str, play_id: str, rect: tuple[float,float,float,float], review_status: str = "draft") -> dict[str,object]: copy successful export frame_id/PTS/dimensions/path; no automatic approval.
- review_evidence(doc: Mapping[str,object], indexes: Mapping[str,Mapping[str,object]]) -> dict[str,object]: spec section8 fields/status/counts/reasons/gaps. Recompute distinct plays and reviewed interval-union gaps; no independence certification or split system. Valid status=insufficient,experiment_gate=false in2A1; candidate gate separate.
- `review EVIDENCE --indexes INDEX ... --output NEW_REPORT`: exclusively new ignored report, exit2 invalid/I/O,3 valid insufficient. No ready/freeze shortcut if another file supplied.

- [ ] Write failing tests: rect(10,20,30,40)/size100x200 ->{x:0.1,y:0.1,width:0.3,height:0.2}; negative/zero/nonfinite/bool/out-of-range fails without clipping. Miss/noPTS/no dimensions fails; draft unchanged; rotation uses display size.
- [ ] Test four verified plays/one recording ->candidate true,experiment false,insufficient; three ->candidate false; many images of one play count1. Only2 distinct timestamps or6 verified boxes fail3–5 rule. Unknown variant/owner/perspective, missing narrative or draft frames cannot count. One unboxed frame in a reviewed interval is NOT a gap/blocker.
- [ ] Test complete interval union vs unknown gap; ambiguous possible target cannot become negative. Terminal-negative covers last frame. Stored preparation_report cannot override recomputed counts. Review is non-mutating. Synthetic prepare/validate/review ->0/0/3; invalid box ->2; unsupported freeze command fails rather than existing.
- [ ] Run `.venv/Scripts/python.exe -m pytest tools/offline_video/tests/test_evidence_review.py tools/offline_video/tests/test_evidence_cli.py -q`; expect failures before implementation.
- [ ] Implement pure box/reference helpers, interval-union gaps, unique-play counting and thin review command. Keep last_absent/onset/visibility evidence manual. Report independent-data/lock prerequisites as deferred reasons, not new features.
- [ ] Rerun task and full tests; expect all pass with insufficient treated as expected output.
- [ ] Commit: `feat(evidence): review deployment intervals and data sufficiency`.

### Task 4: Current real recording verification and completion report

**Files:** ignored local evidence only; README.md, docs/VERIFICATION_M2A1.md,
docs/CURRENT_STATE.md, docs/DEVELOPMENT_PLAN.md. No new recognition code.

**Interfaces:** Tasks1–3 and six-entity JSON. Requires separate implementation
approval; this document revision reads no new footage.

- [ ] First run/add synthetic regressions: non-match negatives outside positives, persistent frames count once, unknown variants stay ambiguous, one recording returns insufficient. No game media in fixtures.
- [ ] Prepare the already explicitly supplied video in a new ignored run; verify source SHA before/after. Watch whole match, refine boundaries and all candidate plays; review owner/variant/absence→spawn→visibility. If candidate gate fails, report it without a guessed replacement.
- [ ] Enter last_absent/onset bracket/point and complete visibility interval per play; box3–5 distinct original key frames. Four surviving plays imply12–20 boxes; additional plays add3–5 each. Record reviewed negatives and unresolved gaps. No5FPS manual inventory or second-video demand simply to finish2A1.
- [ ] Run validate (0 if valid) and review (3 insufficient for current one-match data); compare local report/key boxes/timestamps with original PNGs. No2A2/freeze work.
- [ ] Run full pytest, pip check, git diff --check and tracked-file/secret/private-path scans; confirm actual media/hash/timestamps/JSON ignored. Public report only candidate/count/gate/anonymous aggregates.
- [ ] Document actual checks/totals, Not Run and limitations, three-command generic Windows usage; update state from verified reality.2A1 completion and2B readiness differ. No SQLite/migration/config/dependency changes expected.
- [ ] Commit `docs(evidence): verify module 2a1 preparation`; push only if authorized; stop for2A1 acceptance. Second independent data plus separate2A2 design/approval are future steps, never automatic continuation.

## Self-review and handoff

Exactly four tasks: spec contract/terminal interval ->Task1; preparation ->Task2;
key annotations/gates/gaps ->Task3; real verification/privacy/state ->Task4.
All five Review Focus items have tests. Split/protocol/digest/freeze and detector
remain deferred, not missing implementation tasks. Prospective2B metrics use
complete reviewed intervals plus a disclosed small boxed subset, not dense labels.

Plan not executed. Review both revised documents before separately approving2A1.
2A2 unapproved. No new chat, delegation, merge, installation, new private-file
read or model execution is authorized by this revision.
