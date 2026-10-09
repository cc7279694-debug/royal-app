# Module 3C-3 — bounded Shadow prototype checkpoint

Date:2026-10-09. Local baseline `bbcd0917493e8d04aa8a61bc74d3da4d2941b376`;
branch `codex/module3c3-deployment-spawn-shadow`. Main remains
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.

## Built and why

- Independent GT-free Deployment Evidence / Spawn Group Shadow prototype and CLI.
- Separate original first-seen, confirmation and unknown deployment time.
- Possible late membership, ambiguous overlap and observationally separated new
  cohorts, without long cooldown or production engine/rule changes.
- Thirty-nine new synthetic/CLI test cases, four short source-video evidence
  windows, original-versus-Shadow timelines and a sealed one-run comparison.

## Actual result and limitations

Baseline2/5 hits and1 duplicate; Shadow0/5 and0 duplicates,2 PROVISIONAL events.
Both Hogs episodes and10 other original outputs become UNRESOLVED due to
identity/owner conflict. Actual groups are empty, so duplicate reduction is
abstention, not successful real-data dedupe. Do not replace the accepted3B engine.

Source pixels support the three early target detections and one four-Hog arrival.
Visible onset intervals are analyst observations, not exact card-release time or
new GT. Fixed timestamps/scoring stay unchanged. Synthetic second-group success
is not cross-match performance. No full-match FP/min, online latency or phone
recognition is established.

One initial unscored IO abort is preserved; a detector-only64MB bounded parser
replaces the incompatible16MB Oracle limit in the new CLI only. Policy did not
change; exactly one subsequent scored FAIL is retained.

## Verification and inheritance

Fresh Python1478 passed/4 existing permission skips; both pip checks pass.
All historical evidence, locks, FAIL results and production non-document sources
are protected; details and actual receipts are in
[verification](../VERIFICATION_MODULE3C3.md).

No training/inference rerun, model/environment/App/Android changes, production
storage migration, push or main merge. Private pixels/JSON/logs stay ignored.
Next separately authorized work should improve trustworthy visual identity,
owner and deployment cues, not continue GT-tuned rule accumulation.
