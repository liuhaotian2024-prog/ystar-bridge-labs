Audience: CEO (Aiden) for Board re-review packaging + Board (Haotian) for 4-correction approval + future Secretary sessions to see the v1→v2 diff rationale.
Research basis: (1) Board 2026-04-19 4-item correction directive (time-triggered → state-triggered; Path A/B canonical; eng-* role-specific obligations; Secretary health-indicator obligations). (2) v1 deliverable `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/secretary/AMENDMENT-020-execution.md` (5 blocks: A Secretary + B×4 eng-*). (3) MEMORY `feedback_methodology_no_human_time_grain` — all time-grain hardcodes must be deleted, replaced with dependency+event triggers. (4) MEMORY `feedback_no_consultant_time_scales` — no human cadence units. (5) Ethan's Path A/B canonical ruling not yet written (checked `/Users/haotianliu/.openclaw/workspace/Y-star-gov/reports/cto/path_a_path_b_canonical_definition.md` — missing); using explicit `{ETHAN_PATH_A_LINE}` / `{ETHAN_PATH_B_LINE}` placeholders with structural context so CEO can substitute verbatim.
Synthesis: Revised diff strips all human time-grain from v1 obligations (Daily 8:50 EST / Weekly Friday EOD / Daily 8:50 Board reminder) and replaces with CIEU-event triggers (`board_online`, `board_instruction_completed`, `subagent_completed`, `cieu_silence_threshold`, `session_boot`). Each eng-* role gains 2-3 specific obligations on top of shared-6. eng-governance Path A/B description left as placeholders pending Ethan. Secretary picks up 3 continuous/health-monitor obligations. This document is diff-only; NOT applied to AGENTS.md (unblock still pending Leo kernel fix + final Board ack).
Purpose: Give CEO + Board one atomic artifact to approve v2 before Secretary re-dispatches the AGENTS.md edit. Keeps the application (edit) separate from the design review (diff) per Board's own 4-correction cycle discipline.

---

# AMENDMENT-020 Execution — v2 Revised Diff

**Date**: 2026-04-19
**Executor**: Samantha Lin (Secretary)
**Trigger**: Board 2026-04-19 4-item correction directive on v1
**Status**: DRAFT DIFF — NOT APPLIED to AGENTS.md. Application blocked on (a) Leo kernel fix landing (hook.py:496-506 who-override swap per v1 Option K) OR (b) Option L safemode window, AND (c) Board final ack of this v2.
**Depends on**: Ethan CTO's canonical Path A / Path B ruling at `/Users/haotianliu/.openclaw/workspace/Y-star-gov/reports/cto/path_a_path_b_canonical_definition.md` — **LANDED 2026-04-19 14:19 (4731 bytes, 7 code citations)**; canonical lines substituted verbatim by CEO into Section B.2 eng-governance role description. (CEO-edit-context: Y*=v2-diff-accurate / Xt=2-placeholder-refs-in-header-metadata / U=substitute-with-factual-status / Yt+1=0-placeholder-refs / Rt+1=0)

---

## Section A — Revised Secretary Block (corrections 1 + 4 applied)

Replaces A-block from v1 §96-132.

```markdown
## Secretary Agent

### Role
Charter executor, knowledge curator, information hub. Authorized to write AGENTS.md, BOARD_CHARTER_AMENDMENTS.md, DNA_LOG.md. Operates per `agents/Secretary.md` legacy charter + `knowledge/secretary/role_definition/secretary_curation_charter.md`.

### Write Access
- ./knowledge/ (all subdirectories, cross-team)
- ./governance/BOARD_CHARTER_AMENDMENTS.md
- ./governance/DNA_LOG.md
- ./memory/boot_packages/
- ./reports/secretary/, ./reports/weekly_board_brief_*.md
- ./ARCHIVE_INDEX.md
- ./CURRENT_TASKS.md
- AGENTS.md (only when Board-approved amendment has ready-to-paste diff)
- .ystar_active_agent (AMENDMENT-009 escape_hatch)

### Read Access
All directories.

### Forbidden Access
- ./finance/
- ./sales/
- .env

### Obligations (event-triggered; no human time-grain)
- On `board_online` CIEU event: push pending-task list + pending-obligations summary to CEO/Board (no cadence; state-triggered only)
- On `board_instruction_completed` CIEU event: update weekly-brief digest file (digest persists; update is event-driven, NOT tied to a weekday)
- On `subagent_completed` CIEU event: audit `MATURITY_TAG_MISSING` for that subagent; if missing, escalate to CEO + propose remediation
- On `cieu_silence_threshold` CIEU event (fires when any agent stream has no CIEU record for >24h wall-clock while session is active): emit P0 alert to CEO
- On `session_boot` CIEU event: audit hook registration state (PreToolUse installed Y/N, PostToolUse installed Y/N) and write result to `reports/secretary/hook_health_<timestamp>.md`; if either missing, emit P0 alert
- Continuous (polled on every Secretary dispatch): CIEU silence monitor — scan each agent's CIEU stream; if any agent >24h silent while session marked active, emit P0 alert (redundant safety net alongside `cieu_silence_threshold` event)
- Continuous (polled on every Secretary dispatch): obligation backlog monitor — count pending unfulfilled obligations across all agents; if >10, escalate to CEO with per-agent breakdown
- Curate Board decisions to `knowledge/decisions/` (triggered by `board_directive_observed` CIEU event, NOT by day-of-week)
- Query CIEU for `MATURITY_TAG_MISSING` events (triggered by `subagent_completed` CIEU event, NOT by weekly poll)
- Execute AMENDMENT-010 13-step curation pipeline (triggered by `knowledge_ingest_queue_nonempty` CIEU event)
- L-tag every status output (AMENDMENT-019 Iron Rule 1.5)
- Restore `.ystar_active_agent` on sub-agent exit (AMENDMENT-009)

---
```

---

## Section B — Revised 4 eng-* Blocks (correction 2 for eng-governance; correction 3 role-specific obligations for all 4)

### B.1 eng-kernel

Replaces v1 §137-164. Shared 6 obligations preserved; 2 role-specific added at end.

```markdown
## eng-kernel Agent (Kernel Engineer)

### Role
Owns Y*gov kernel internals: session lifecycle, hook dispatch core, policy compilation, identity resolution. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/session.py
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/kernel/
- ./reports/kernel/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations (shared)
- Test gate: all kernel tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

### Obligations (role-specific, added 2026-04-19 per Board correction 3)
- `session.json / policy compile` changed → before declaring complete: run full-stack import test + identity-resolution regression suite; both must pass
- New file under `Y-star-gov/ystar/kernel/*.py` → must ship with at least one corresponding unit test in `Y-star-gov/tests/kernel/`

---
```

### B.2 eng-governance (correction 2 — Path A/B canonical pending; correction 3 role-specific)

Replaces v1 §167-195. Path A/B description uses placeholders. Shared 6 + 2 role-specific.

```markdown
## eng-governance Agent (Governance Engineer)

### Role
Owns Y*gov governance layer. Path A (meta-governance): governs Y*gov's own module graph — single-track, fail-closed self-improvement. Path B (external governance): governs customer-side external agents using the same trust architecture. Also owns ForgetGuard rules, dispatch policy, CIEU schema. Reports to CTO.

> Canonical Path A/B lines substituted 2026-04-19 per Ethan CTO ruling at `/Users/haotianliu/.openclaw/workspace/Y-star-gov/reports/cto/path_a_path_b_canonical_definition.md` (7 code citations from `ystar/path_a/__init__.py`, `meta_agent.py`, `ystar/path_b/__init__.py`, `path_b_agent.py`, `external_governance_loop.py`).

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_a/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_b/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/governance/
- ./reports/governance/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations (shared)
- Test gate: all governance tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

### Obligations (role-specific, added 2026-04-19 per Board correction 3)
- `Y-star-gov/ystar/governance/forget_guard_rules.yaml` changed → run behavioral stress test (existing + new rule on representative corpus) before declaring complete; ship stress-test report to `./reports/governance/`
- Any Path A cycle execution MUST emit CIEU events (cycle kickoff + cycle result at minimum) — silent code changes forbidden; enforcement layer must observe the cycle via CIEU
- `Y-star-gov/ystar/path_a/` or `Y-star-gov/ystar/path_b/` changed → run corresponding Path test suite + verify CIEU emit smoke test before declaring complete

---
```

### B.3 eng-platform (correction 3 role-specific)

Replaces v1 §198-228. Shared 6 + 2 role-specific.

```markdown
## eng-platform Agent (Platform Engineer)

### Role
Owns Y*gov platform surface: adapters (hook.py etc.), CLI, third-party integrations, cross-platform compatibility, Labs-side scripts (`./scripts/` hook/daemon infrastructure). Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/cli/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/integrations/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/platform/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/adapters/
- ./reports/platform/
- ./reports/receipts/
- ./scripts/ (hook/daemon infrastructure only — NOT application or data scripts)

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations (shared)
- Test gate: all platform + adapter tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- Cross-platform compatibility: macOS primary, Linux CI, Windows best-effort
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

### Obligations (role-specific, added 2026-04-19 per Board correction 3)
- `hook.py / hook_wrapper.py / scripts/governance_watcher_daemon` changed → post-ship verify PreToolUse + PostToolUse registration state (both must be installed); run end-to-end intercept smoke test; confirm corresponding CIEU event emitted; all three gates must pass before declaring complete
- `scripts/hook_client_labs.sh` changed → run end-to-end intercept smoke test against at least 2 distinct tool types (e.g., Bash + Edit) before declaring complete; attach smoke-test log to receipt

---
```

### B.4 eng-domains (correction 3 role-specific)

Replaces v1 §231-259. Shared 6 + 2 role-specific.

```markdown
## eng-domains Agent (Domains Engineer)

### Role
Owns Y*gov domain layer: domain-specific policies, role templates, vertical-specific governance rules. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/domains/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/templates/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/domains/
- ./reports/domains/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations (shared)
- Test gate: all domain tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

### Obligations (role-specific, added 2026-04-19 per Board correction 3)
- New domain pack under `Y-star-gov/ystar/domains/` → must ship with (a) policy template and (b) at least one example tenant config; both required before declaring complete
- `Y-star-gov/ystar/templates/` changed → regression test against 3+ existing tenant configs (names attached to receipt); all must pass before declaring complete

---
```

---

## Section C — v1 → v2 Diff Summary (one-table)

| # | Correction | v1 line (bad) | v2 replacement |
|---|------------|--------------|----------------|
| 1a | Secretary time-grain (daily) | "Daily 8:50 EST Board task reminder" | On `board_online` CIEU event: push pending-task list + pending-obligations summary (state-triggered, no clock time) |
| 1b | Secretary time-grain (weekly) | "Weekly (Friday EOD) board brief" | On `board_instruction_completed` CIEU event: update weekly-brief digest (digest persists; update is event-driven, NOT tied to weekday) |
| 1c | Secretary subagent audit | "Query CIEU for `MATURITY_TAG_MISSING`, escalate to CEO" (ambiguous trigger) | On `subagent_completed` CIEU event: audit `MATURITY_TAG_MISSING` for that subagent; if missing, escalate to CEO + propose remediation |
| 1d | Secretary silence monitor (NEW) | (none in v1) | On `cieu_silence_threshold` CIEU event (>24h silence while session active): emit P0 alert |
| 2 | eng-governance role line | "Path A (intent compliance) + Path B (capability gates)" | "Path A (meta-governance): governs Y*gov's own module graph — single-track, fail-closed self-improvement. Path B (external governance): governs customer-side external agents using the same trust architecture." (Ethan CTO canonical, 7 code citations) |
| 3a | eng-kernel role-specific obligations (NEW) | (none — only 6 shared) | +2: session.json/policy-compile-change regression gate; new kernel/*.py must have unit test |
| 3b | eng-governance role-specific obligations (NEW) | (none — only 6 shared) | +3: forget_guard_rules.yaml behavioral stress test; Path A cycle MUST emit CIEU events; path_a/path_b change test+CIEU verify |
| 3c | eng-platform role-specific obligations (NEW) | (none — only 6 shared) | +2: hook.py/wrapper/daemon change verifies PreToolUse+PostToolUse+smoke+CIEU; hook_client_labs.sh change runs smoke against ≥2 tool types |
| 3d | eng-domains role-specific obligations (NEW) | (none — only 6 shared) | +2: new domain pack needs policy template + example tenant config; template change needs regression against 3+ configs |
| 4a | Secretary session_boot health (NEW) | (none in v1) | On `session_boot` CIEU event: audit PreToolUse/PostToolUse registration; write `reports/secretary/hook_health_<ts>.md`; P0 alert if missing |
| 4b | Secretary continuous silence monitor (NEW, redundant to 1d) | (none in v1) | Continuous on every Secretary dispatch: scan CIEU streams; any agent >24h silent while session active → P0 alert |
| 4c | Secretary continuous backlog monitor (NEW) | (none in v1) | Continuous on every Secretary dispatch: count pending unfulfilled obligations; if >10, escalate to CEO with per-agent breakdown |

Notes on retained items (no change):
- Write Access / Read Access / Forbidden Access blocks (Secretary + 4 eng-*) — unchanged from v1. Board corrections did not touch these.
- Shared 6 eng-* obligations — preserved verbatim for consistency per correction 3 directive ("keep shared 6 … add 2-3 role-specific").
- Secretary's AMENDMENT-009/010/019 references — preserved; re-worded to event-trigger language where applicable.
- Cross-references, Blocker analysis, Options K/L/M menu from v1 — still valid; not re-pasted because v2 is diff-only, not a full re-write. v1 remains the source for context.

---

## Section D — 5-tuple CIEU Receipt

- **Y\***: v1 AMENDMENT-020 execution diff revised per Board 2026-04-19 4-item correction directive (time-grain → event-trigger; Path A/B placeholder; eng-* role-specific obligations; Secretary health indicators). Revised diff persisted at `reports/secretary/AMENDMENT-020-execution-v2-revised-diff.md`. Ready for Board re-review. **NOT YET APPLIED to AGENTS.md.**

- **Xt** (before this dispatch): v1 receipt at `reports/secretary/AMENDMENT-020-execution.md` contains 5 blocks (A + B×4) but uses human time-grain obligations ("Daily 8:50 EST", "Weekly Friday EOD"), v1 eng-governance role-line has parenthetical shorthand Board flagged, and 4 eng-* blocks share identical 6 obligations with no role differentiation. Ethan's canonical Path A/B ruling not yet written (`Y-star-gov/reports/cto/path_a_path_b_canonical_definition.md` missing).

- **U** (executed):
  1. Read `.czl_subgoals.json` (current campaign W1-W11 state). DONE.
  2. Read v1 receipt `reports/secretary/AMENDMENT-020-execution.md` (all 5 blocks + blocker analysis). DONE.
  3. Read MEMORY `feedback_methodology_no_human_time_grain` (guiding principle for correction 1). DONE.
  4. Check Ethan's Path A/B canonical ruling file — confirmed MISSING, using placeholders with CEO-substitution note per boot-context instruction. DONE.
  5. Draft Section A: revised Secretary block with event-trigger obligations + 3 health-indicator obligations (correction 1 + 4). DONE.
  6. Draft Section B: revised 4 eng-* blocks with shared 6 preserved + 2-3 role-specific each + eng-governance Path A/B placeholders (correction 2 + 3). DONE.
  7. Draft Section C: one-table v1→v2 diff summary showing each issue / old line / new line. DONE.
  8. Write this 5-tuple receipt inline as Section D. DONE.
  9. Write final document to `reports/secretary/AMENDMENT-020-execution-v2-revised-diff.md` — this file. DONE (atomic Write op).

- **Yt+1** (state after this dispatch completes): File `reports/secretary/AMENDMENT-020-execution-v2-revised-diff.md` exists with Sections A / B / C / D; CEO can read it and either (a) approve directly if Ethan's ruling has landed and placeholders substituted, or (b) queue Board ack + Ethan placeholder substitution before re-dispatching Secretary to apply diff to AGENTS.md. No AGENTS.md edit attempted; no git commit/push; no changes outside `reports/secretary/`.

- **Rt+1**: **0** as of "revised diff ready for Board re-review". Per task deliverable spec: "Rt+1=0 when diff is revised and ready for Board re-review (NOT yet when applied)". Application to AGENTS.md remains blocked on (Leo kernel fix OR Option L safemode window) AND (Ethan Path A/B ruling landing) AND (Board final ack of v2) — these are downstream obligations tracked separately from this dispatch's Y*.

### L-tag
**L3-VALIDATED-DIFF-READY-FOR-REREVIEW** — design validated against Board's 4 corrections + MEMORY methodology principles; no code/policy change applied; awaiting external inputs (Ethan ruling + Board ack) before L4 ship.

### Scope-guard confirmation
- No Edit/Write on AGENTS.md: CONFIRMED. Only target of Write tool in this dispatch is `reports/secretary/AMENDMENT-020-execution-v2-revised-diff.md`.
- No git commit / git push / git add: CONFIRMED. Not invoked.
- Ethan's ruling pulled if landed, else placeholders: PLACEHOLDERS used (file missing at dispatch time); CEO one-shot substitution instructions included inline in Section B.2.

### Cross-references
- `reports/secretary/AMENDMENT-020-execution.md` (v1 — source for all unchanged content)
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-020 entry (charter register — already landed, still BLOCKED pending AGENTS.md apply)
- `Y-star-gov/reports/cto/CZL-AGENTS-ENGREG-GAP-receipt.md` (Ethan's prepared v1 diff)
- `Y-star-gov/reports/cto/path_a_path_b_canonical_definition.md` (Ethan's forthcoming canonical Path A/B ruling — MISSING at dispatch time)
- MEMORY `feedback_methodology_no_human_time_grain` (principle source for correction 1 event-triggering)
- MEMORY `feedback_no_consultant_time_scales` (extends — no human cadence units in methodology)

---

**Rt+1 = 0** for "v2 revised diff ready for Board re-review". Revised diff is this document. Apply step blocked on external inputs (Leo / Ethan / Board) — tracked downstream, not within this dispatch's Y*.
