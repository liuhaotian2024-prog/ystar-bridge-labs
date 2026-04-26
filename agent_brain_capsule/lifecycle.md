# Agent Brain Capsule Lifecycle

This lifecycle describes runtime-facing phases using existing artifacts only.

## L0 — Boot / Identity / Memory References

- Purpose: restore who the agent is and what state it is in.
- Inputs: `AIDEN_ONTOLOGY.md`, `team_dna.md`, `WORLD_STATE.md`, `session_handoff.md`, boot packages.
- Evidence status: implemented as memory/state artifacts; exact boot integration should be validated separately.

## L1 — Pre-Action Cognitive Context

- Purpose: inject relevant brain/memory context before a reasoning/action chain.
- Inputs: prompt/current state, brain top-k, 6D projection, ontology.
- Evidence status: specified in `brain_3loop_consolidated_v2.md` and ratified in `CZL-BRAIN-3LOOP-FINAL-ruling.md`; implementation status needs current validation.

## L2 — Post-Action CIEU / Writeback

- Purpose: convert decisions and outcomes into activation/access/edge updates.
- Inputs: CIEU events, prior L1 context, tool/action outcomes, negative/positive outcome signals.
- Evidence status: specified and partially implemented historically; `CZL-BRAIN-L2-WRITEBACK-PARTIAL-20260420.md` says hook wiring was incomplete at that time.

## L3 — Offline Dream / Consolidation

- Purpose: scan activation history, propose new edges/nodes/archive actions, and prevent catastrophic drift.
- Inputs: activation log, CIEU-derived activations, recent and historical samples.
- Evidence status: `brain_dream_scheduler.py` implements dream proposal patterns; `CZL-BRAIN-L3-GUARD-RAILS-ruling.md` defines safety guardrails.

## Residual-Driven Correction

- Purpose: use CZL residuals to retry, delegate, escalate, revise targets, or record gaps.
- Inputs: `Y* / Xt / U / Yt+1 / Rt+1`, CIEU evidence, residual loop design.
- Evidence status: defined in `CZL.md` and Amendment 014; live RLE implementation status is unclear.

## Boundary

This lifecycle is not permission to mutate DBs, run daemons, or bypass governance. Runtime execution must still pass the governance boundary.
