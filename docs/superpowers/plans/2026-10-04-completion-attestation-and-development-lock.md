# Completion Attestation and Development Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for this already user-authorized continuation. Do not request another planning approval or create another checkout.

**Goal:** Record user-confirmed completeness without a result-screen gate, then continue the first viable original-order development recording to a truthful lock or evidence blocker.

**Architecture:** Keep v1 extraction/evidence validation unchanged. Add only paired optional completion-source/result-screen metadata to the development identity, already covered by the lock digest. Reuse existing private evidence; create supplements and snapshots exclusively.

**Tech Stack:** Existing pinned Python/PyAV/Pillow/pytest, local JSON and SHA-256; no new dependency.

**Spec:** Current explicit user authorization and the completion-definition amendment in `docs/DECISIONS.md`.

## Global Constraints

- Preserve every existing source, report, index, image, rough review and old exclusion record.
- Complete means user confirms whole-match coverage; last actual decoded frame is the evaluable end. A result screen is not required.
- Still reject corrupt/undecodable footage, obvious mid-match truncation, missing key battle intervals or explicit human incompleteness.
- Inspect original intake order, not target difficulty. Reuse first rough review, retaining unknowns and other forms, never fabricate negatives.
- Same known form needs >=2 clear independent verified deployments, each with 3–5 actual-PTS original key frames. Never invent onset/boxes or force a freeze.
- No old v1 behavior change, model training/inference, 2B, Android/live/HUD, network upload, push or main merge.

## Review Focus

- Completion metadata must not bypass false full-review/unedited/complete attestations or the shared complete-segment rule.
- New fields stay closed, strictly typed and digest-bound; old draft/lock compatibility remains.
- Missing result UI is not an implied negative or independent technical proof of human completeness.
- Human approximate times are location hints, not verified PTS deployment/visibility boundaries.
- No old media/labels overwritten, no unknown interval silently converted to absence, no ambiguous deployment counted as clear.

### Task 1: Completion-source metadata and superseding policy

**Files:** Modify experiment_contract.py; test_experiment_development.py; test_experiment_lock.py; the affected protocol/contracts/decision/status/verification documents only.

**Interfaces:** Consumes existing validate_development(draft,indexes), make/freeze/load_development_lock. Produces compatible identities with paired completion_attestation=user_confirmed and strict Boolean terminal_result_screen_present, preserved in unchanged lock APIs.

- [x] Write tests: a user-confirmed no-result recording with segment ending at last actual frame remains DEV_VALIDATED; metadata is preserved/digest-bound; malformed/orphan fields and false original attestations still fail.
- [x] Run focused tests before production change; expected new acceptance/lock cases fail because the identity is currently closed.
- [x] Extend only development identity's allowed fields, requiring both new fields when either appears. No permissive generic-object change.
- [x] Run focused and full existing tests; expected no failures, known permission skip only. Run pip check/diff check.
- [ ] Record the superseding definition and actual verification, then local feature commit only.

### Task 2: Original-order real development evidence

**Files:** Exclusively new ignored attestation, precise extracts, evidence draft/reports and lock; update public aggregate status/verification after checks.

**Interfaces:** Consumes Task 1 identity metadata, original intake, first rough review, existing prepare/load_indexes and experiment CLI. Produces real DEV_LOCKED only with adequate verified evidence; otherwise an honest NOT_READY/blocked handoff.

- [ ] Protect explicitly listed existing four-recording and historical 2A1 files by before hashes. Save the current user statement as a new sidecar, superseding but not rewriting old exclusions.
- [ ] Reconsider source one first. Reuse its survey/rough review and last actual PTS; only extract missing locator/key-frame requests around reported deployments.
- [ ] Review absence/spawn/visibility and original key-frame boxes, preserve ambiguous observations and unknown regions; record manual candidate comparison and known-form choice.
- [ ] Run existing v1 validate/review and new readiness with all actual indexes; expect 0/3/0 only if evidence is valid and eligible. Otherwise do not change labels to force expected results.
- [ ] Only then freeze-development into a new dedicated versioned lock directory and validate-lock; expect 0/0 with stable SHA-256. Stop at DEV_LOCKED; do not infer test qualification or enter 2B.
- [ ] Fresh full regression/dependency/diff/privacy/hash checks, one fresh-context whole-change review, verified aggregate documents, local feature commit and stop. No push/merge.
