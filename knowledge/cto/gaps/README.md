# CTO (Ethan Wright) — gaps/

Cognitive gaps — things this role noticed it did not know. The
**purpose** is to surface unknowns early so the idle learning loop
can work on them, rather than rediscover them under pressure during
a real directive.

## What goes here

### 1. Counterfactual-simulation gaps

One file per simulation: `YYYY-MM-DD-<scenario_slug>.md`

Content: the simulated task from `local_learn.py --mode tasks`, the
agent's framework walk-through (layers 0–8), the self-evaluation
(from `local_learn.py --mode eval`), and the specific gaps surfaced
by the exercise. Examples of "gaps":

- "I do not know how to prioritize X vs Y in this context"
- "I assumed Z but could not verify it"
- "The theory I would reach for here does not exist in my library yet"
- "I recognize I would need to talk to role N before acting and I
  have never had that conversation"

### 2. Gemma session log

One file (not per-day): `gemma_sessions.log`

Format: one JSON object per line (JSONL). Written by
`scripts/local_learn.py` on every invocation. Each line contains
`timestamp`, `mode` (questions|tasks|eval), `actor`, `input_summary`,
`endpoint` (which Gemma URL answered), `question_count` (for mode
questions) or output hash. Secretary's weekly Monday audit reads
this file and separately verifies that every role has at least one
entry per working day.

## How it is used

- Secretary weekly Monday audit checks gemma_sessions.log per role
- Idle learning priority #3 reads the gap files to pick which
  theory-library entry to build next
- Board or CEO can grep gaps/ across roles to see the company-wide
  map of acknowledged unknowns

## Never delete

Both kinds of files are append-only audit evidence. Gaps should be
closed by writing a theory file in `../theory/`, not by deleting
the gap file. A gap with a "closed in commit XXX" footer is
stronger evidence than a missing file.

## Source

Board capability system directive (2026-04-10);
`governance/WORKING_STYLE.md` 第九条 layer 2 (assumptions) and the
idle learning loop definition in `AGENTS.md`.
