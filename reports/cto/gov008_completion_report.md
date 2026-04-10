# GOV-008 Completion Report

**Author**: Ethan Wright (CTO)
**Date**: 2026-04-09
**Status**: All three gaps closed. Ready for Board acceptance.
**Directive**: Board GOV-008 completion directive (this chat turn)

---

## Executive summary

GOV-008 as originally shipped (commit `9a421f7`) gave the Board a
one-line-NL → CIEU obligation pipeline. Board identified three
structural gaps still open after that commit. This report documents
the close-out of all three in one continuous working session
(~90 minutes wall time, 3 commits).

| Gap | Commit | Deliverable | Status |
|---|---|---|---|
| 2. Write Hook Intent Guard | `ab9204e` | `hook_wrapper.py` + `.ystar_session.json` config | ✅ |
| 3. Directive closure protocol | `f19b4fc` | `reject_directive.py` + `--board` view + 第八条 + 6 agents/*.md | ✅ |
| 1. Real LLM end-to-end test | this commit | `reports/cto/gov008_gap1_real_llm_test.md` | ✅ |

Execution followed Board's suggested order (Gap 2 first, then Gap 3,
then Gap 1 last) because Gap 1 needed a live LLM environment and
the other two did not.

Per GOV-006 protocol: two Level 3 intents (`intent_67238c015cbb`
for Gap 2, `intent_9d72be9d7d9a` for Gap 3) were recorded before any
code modification and CONFIRMED by board via verbatim quotes from
this directive. Gap 1 was declared Level 1 by Board (read-only test)
and did not require an intent row.

---

## Gap 2 — Write Hook Intent Guard

**Commit**: `ab9204e` — `gov(GOV-008): Gap 2 — hook intent guard (warn-only, fail-open)`
**Intent**: `intent_67238c015cbb` (cto, Level 3, CONFIRMED by board)

### What shipped

`scripts/hook_wrapper.py` gained a new section placed between the
CEO code-write block and the `check_hook()` delegation. The new
section runs on every `Write` / `Edit` / `NotebookEdit` tool call,
matches the target `file_path` against a configured list of
protected paths, and — if the match hits — queries CIEU for any
`INTENT_RECORDED` row by any actor within a configured window. On
miss, it writes one `GOV006_VIOLATION_WARNING` row and logs to
`hook_debug.log`. It **does not block** the tool call. It
fails open on any error.

`.ystar_session.json` gained two new keys:

```json
{
  "intent_guard_window_hours": 4,
  "intent_guard_protected_paths": [
    "governance/",
    "agents/",
    "README.md",
    "scripts/record_intent.py",
    "scripts/check_intents.py"
  ]
}
```

### What the protection does

| Protected path | Rationale |
|---|---|
| `governance/` | constitutional surface (WORKING_STYLE, DNA_LOG, INTERNAL_GOVERNANCE, BOARD_CHARTER_AMENDMENTS, CALENDAR, TEMP_LAW) |
| `agents/` | the 6 role constitutions, DNA-distilled from Board conversations |
| `README.md` | external positioning, the strategic artifact |
| `scripts/record_intent.py` | the protocol tool itself — can't be silently rewritten without recording intent |
| `scripts/check_intents.py` | same — fixed-point protection |

An agent writing code under `scripts/`, `tests/`, `products/`,
`frontend-v2/`, `finance/`, or anywhere else is unaffected. The
protection is deliberately narrow: only files whose content *is*
governance.

### Architectural consistency

The guard is **warn-only, not block**, which is consistent with the
original GOV-006 design decision to pick Option C (hybrid protocol
+ CIEU audit, no blocking hook) over Option B (hard hook enforcement,
400 lines + cross-repo dependency). The guard does not reintroduce
the rejected blocking model; it adds the enforcement point that
Option C always envisioned but did not have code for.

**Fail-open** is the existing pattern in `hook_wrapper.py` — the
outer `try` block already outputs `{}` on exception so Claude Code
doesn't crash. The new guard uses a tighter inner `try/except` that
logs to `hook_debug.log` and returns cleanly, never raising.

### Smoke test (inline, 4 scenarios — all pass)

| # | Scenario | Expected | Actual |
|---|---|---|---|
| A | Write to `governance/WORKING_STYLE.md` WITH recent intent | no new warning row | ✓ |
| B | Write to `scripts/publish_telegram.py` (non-protected) | guard ignores, no new warning | ✓ |
| C | Write to `governance/DNA_LOG.md` with `intent_guard_window_hours=0.00001` (forces no recent intent) | exactly one `GOV006_VIOLATION_WARNING` row written with correct payload (`tool=Edit`, `file_path=governance/DNA_LOG.md`, `window_hours=1e-05`, `protected_path_match=governance/`) | ✓ |
| D | Unreachable CIEU DB (`/nonexistent/path/ghost.db`) | helper returns cleanly, no exception propagates | ✓ |

Additional cleanup: added `if __name__ == "__main__"` guard around
the main entry point so the module can be imported by future test
files without side effects on stdout or the session call counter.

---

## Gap 3 — Directive closure protocol

**Commit**: `f19b4fc` — `gov(GOV-008): Gap 3 — directive closure protocol (REJECTED state)`
**Intent**: `intent_9d72be9d7d9a` (cto, Level 3, CONFIRMED by board)

### What shipped

**Three deliverables in one commit**:

1. **`scripts/reject_directive.py`** (150 lines) — mirrors
   `record_intent.py`. Writes one `DIRECTIVE_REJECTED` CIEU event
   with `evidence_grade="decision"`. Hard-rejects:
   - `--actor` not in ROLES whitelist → exit 2
   - `--reason` empty after strip → exit 2
   - `--reason` < 20 chars after strip → exit 2 (the explicit
     defense against one-word brushoffs — Board sees real analysis
     in the audit chain, not "nope")
   - `--directive-id` empty → exit 2

2. **`scripts/check_obligations.py` `--board` flag** (~130 new
   lines). New functions `collect_rejections()` and
   `print_board_view()`. Renders five groups: **COMPLETED**,
   **REJECTED**, **PENDING**, **OVERDUE**, **CANCELLED**. Each
   group shows owner, directive, rule, and state-specific extra
   (completion note, wrapped rejection reason, pending countdown,
   overdue duration, cancel reason). Rejections without matching
   obligations are synthesized into REJECTED rows so a Board who
   said "do X" in chat (never registered as an obligation) still
   sees the agent's pushback.

3. **`governance/WORKING_STYLE.md` 第八条 义务拒绝协议** (~120 lines)
   — new top-level article placed after 第七条 7.5 and before the
   team role card. Defines the three legal end states (COMPLETED /
   REJECTED / PENDING), the 2-hour SLA for agent response, the
   `reject_directive.py` CLI, the Board dashboard view, and the
   "rejection is not terminal" semantics (Board can override with a
   new directive, at which point GOV-006 intent verification kicks in).

4. **6 agents/*.md role-specific sections** — each gains a
   "GOV-008 拒绝义务权（第八条）" block right after their GOV-008
   awareness section. Each is tuned to that role's typical
   rejection scenarios:

    - **CEO**: reject when Board's dispatch granularity is wrong
      (needs further decomposition)
    - **CTO**: reject when design conflicts with architecture — must
      pair with a GOV-005 §7 counterfactual proposal first
    - **CMO**: reject when asked to publish unverified data or
      exaggerated narrative (direct CASE-001 remediation path)
    - **CSO**: reject when asked to breach commercial/legal/trust
      boundary
    - **CFO**: reject when data is insufficient or assumptions
      unverifiable (direct CASE-002 remediation path)
    - **Secretary**: reject when amendment text disagrees with
      Board's verbal intent; also gains the weekly Monday duty to
      surface silent-overdue directives in the weekly audit report

### Why this closes the loop

Before this commit, Board directives could only end in
**COMPLETED** (via `--mark-fulfilled`) or **silence**. Silence is
illegal but was the only available option when an agent genuinely
disagreed or could not execute. This created an incentive to stay
silent and hope the directive would be forgotten, exactly the
failure mode CASE-001 (CMO) and CASE-002 (CFO) were founded on.

With REJECTED as an explicit, audit-recorded path:

- Disagreement becomes visible state instead of hidden state
- Board can see a REJECTED row and choose to accept, negotiate, or
  override
- Override forces a GOV-006 intent-verification loop (agent must
  record their understanding of the override reason before
  executing), which catches interpretation drift
- Secretary's weekly audit has a new category to surface:
  "silent overdue" directives (Level 2/3 with no mark-fulfilled
  and no DIRECTIVE_REJECTED after 2 hours)

The state machine of a Board directive is now:

```
         register_obligation   mark-fulfilled
  [new] ───────────────────▶ [PENDING] ────────▶ [COMPLETED] ✓
                                │
                                │ reject_directive.py
                                ▼
                            [REJECTED] — terminal unless Board
                                │        issues override directive
                                ▼
                     (Board override → GOV-006 intent loop → execute)
                                │
                      time > due_at
                                ▼
                            [OVERDUE] — Secretary audit surfaces this
                                │        to Board as "silent overdue"
                                ▼
                     (Board action forces COMPLETED or REJECTED)
                                │
                       gov_order_undo.py
                                ▼
                           [CANCELLED] — Board changed mind
```

All five states are now legal and all five are visible in
`check_obligations.py --board`.

### Smoke tests (6 scenarios — all pass)

| # | Scenario | Expected | Actual |
|---|---|---|---|
| 1 | `reject_directive.py --reason ""` | exit 2 | ✓ |
| 2 | `reject_directive.py --reason "nope"` (4 chars) | exit 2 (< 20) | ✓ |
| 3 | `reject_directive.py --actor random_dude` | exit 2 (bad role) | ✓ |
| 4 | Valid rejection | CIEU row + rejection_id returned | ✓ |
| 5 | `check_obligations.py --board` | shows REJECTED group with wrapped reason | ✓ |
| 6 | Regular `check_obligations.py --actor / --overdue-only` | no regression | ✓ |

---

## Gap 1 — Real LLM end-to-end test

**Commit**: this commit (alongside this report)
**Intent**: not required — Board declared Gap 1 as Level 1 (read-only test)
**Full report**: `reports/cto/gov008_gap1_real_llm_test.md`

### Summary

Ran gov_order.py against real local LLM providers — not against a
mock — and verified that every CIEU row the design doc predicted
actually gets written.

**Provider chain outcome**: this environment had no Anthropic or
OpenAI keys and no SDKs, but Ollama was running with `gemma4:e4b`
(8 B) and `gemma3:4b` (4 B) available. The detection chain correctly
fell through to Ollama (the fourth fallback tier). This is itself a
validation of the portable provider design — the pipeline works on
a machine with zero cloud API keys.

**Trial 1** — `gemma4:e4b` cold start: **timed out at 30 seconds**.
The failure path fired exactly as designed: LLM call failed → pending
file written → INTENT_RECORDED with `validation_status="llm_call_failed"`
→ exit 0 → no exception propagated to Board. The pending file was
preserved for Secretary's Monday review.

**Trial 2** — `gemma3:4b` warm: **full success**. Every stage of the
chain fired:

| Stage | Record |
|---|---|
| LLM translation | gemma3:4b output parsed cleanly as JSON |
| Deterministic validator | PASS (0 validation errors) |
| INTENT_RECORDED CIEU | `intent_b402ef853d64` |
| OBLIGATION_REGISTERED CIEU | `a95d1256-6a96-47a1-94e9-16cd5a3185b6` |
| INTENT_LINKED CIEU | yes, linking the two |
| dashboard (`check_obligations --actor cto`) | `PENDING  high  CTO  GOV-008  gov_008_impl_cto  a95d1256  due in 4.0h` |

Wall-clock latency: **under 10 seconds** end-to-end on warm gemma3:4b.

**Quality note**: gemma3:4b is a 4 B local model — smaller than the
"70-80% accuracy" estimate in the original design doc (which assumed
mid-tier cloud models like Claude Sonnet). On this one test input
it produced a clean dict that passed the deterministic validator on
the first attempt with zero errors. n=1 is not a quality benchmark,
but it is an existence proof that the pipeline is usable even with
the smallest supported provider tier.

**Cleanup**: the test obligation was not a real Board order, so it
was undone via `gov_order_undo.py` (which is itself a GOV-008 Step 2
deliverable — second real exercise of the undo tool in this session).
The dashboard now shows the test obligation as `CANCELLED` with
reason "GOV-008 Gap 1 real LLM end-to-end test cleanup". All
append-only rows remain in CIEU as proof of the test.

---

## Forward-looking notes

These are observations, not open questions. Board can ignore or
defer any of them.

1. **Timeout may need to become configurable.** The 30 s default is
   tight for cold-start local models. Adding
   `llm_call_timeout_secs` to `.ystar_session.json` (default 30,
   override 60 or 90 for local Ollama users) would reduce the
   false-failure rate on Trial-1-like cases. One-line change if/when
   Board asks.

2. **Quality sampling is n=1.** We've proven the pipeline works on
   one real input. A proper quality benchmark is 20+ varied inputs
   (ambiguous ownership, relative time, mixed Chinese/English,
   non-task inputs, adversarial inputs). This is out of scope for
   GOV-008 and would be a separate directive if/when Board wants it.

3. **"Silent overdue" could become an explicit CIEU event type.**
   第八条 defines the 2-hour SLA for agent response, but detection
   is currently Secretary-audit-only. A future version could have a
   background sweep that writes `DIRECTIVE_SILENT_TIMEOUT` rows
   automatically. Kept out of scope for this close-out per the
   "detection via weekly audit is consistent with GOV-006 method C"
   principle in 第八条's closing note.

4. **Intent-guard protected-path list could grow.** Candidates for
   future addition: `AGENTS.md` (but this file is immutable per
   GOV-004 amendment flow — guard would never miss it), `.claude/`,
   any file with `KEY` or `.env` in the name (dangerous). Not adding
   any of these now — `governance/` + `agents/` + `README.md` + the
   two intent scripts are the high-signal surface today.

5. **Hook guard depends on CIEU being reachable.** If CIEU is down
   or locked, the guard fails open. This is correct behavior (hook
   failures must never become tool failures) but means the
   enforcement can silently go dark. Secretary's weekly audit can
   include a "hook health check" step that greps `hook_debug.log`
   for fail-open entries and surfaces them.

---

## Intent audit trail

Both Level 3 intents for this session can be inspected with:

```bash
python3.11 scripts/check_intents.py --show intent_67238c015cbb  # Gap 2
python3.11 scripts/check_intents.py --show intent_9d72be9d7d9a  # Gap 3
python3.11 scripts/check_intents.py --directive GOV-008
```

Both show `Status: CONFIRMED` with the exact verbatim Board
confirmation text preserved in the review note field.

---

## Git state

```
f19b4fc gov(GOV-008): Gap 3 — directive closure protocol (REJECTED state)
ab9204e gov(GOV-008): Gap 2 — hook intent guard (warn-only, fail-open)
70c0b24 docs(readme): fix Samantha execution deviation
9a421f7 gov(GOV-008): Step 2 — gov_order NL → CIEU pipeline + undo + weekly audit
4eba26f gov(GOV-006): Intent Verification Protocol — option C implementation
43759eb docs(readme): bidirectional accountability narrative
```

(Plus this commit, which adds `reports/cto/gov008_gap1_real_llm_test.md`
and this summary.)

---

## Board acceptance checklist

For Board convenience, the three things to spot-check if you want to
convince yourself GOV-008 is actually closed:

1. **Gap 2 guard fires on real protected-path writes** —
   ```bash
   python3.11 scripts/check_obligations.py --board 2>&1 | grep -v "^$" | head
   sqlite3 .ystar_cieu.db "SELECT event_type, created_at FROM cieu_events WHERE event_type='GOV006_VIOLATION_WARNING' ORDER BY created_at DESC LIMIT 5;"
   ```

2. **Gap 3 reject + board view** —
   ```bash
   python3.11 scripts/check_obligations.py --board
   # Should show REJECTED group with GOV-008-REJECT-TEST (smoke test row)
   ```

3. **Gap 1 real LLM chain** —
   ```bash
   python3.11 scripts/check_intents.py --show intent_b402ef853d64
   # Should show Source: gov_order, LLM provider: ollama, LLM model: gemma3:4b,
   # Validation: pass, Status: REJECTED (because we undid it).
   ```

— Ethan Wright (CTO)
