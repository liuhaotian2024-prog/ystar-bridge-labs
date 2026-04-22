# SOFT Rule Rubric Reclassification (Layered Translation Method)

**Author**: Jordan Lee (eng-domains)
**Date**: 2026-04-22
**Method**: 6-criteria rubric from arxiv 2604.05229 (Layered Translation Method, Table I)
**Source**: CEO spec Section 3c, 10 remaining SOFT rules (items 1-9, 12; items 10-11 already reclassified by CEO)

## Scoring Scale

| Criterion | What It Measures | 3 (high) | 2 (mid) | 1 (low) |
|---|---|---|---|---|
| **Timing** | When can rule be checked? | pretool | posttool | audit-only |
| **Observability** | Can violation be detected from tool_calls + reply? | fully | partial | requires-judgment |
| **Determinacy** | Deterministic or requires LLM? | deterministic (regex/logic) | heuristic | llm-judge |
| **Judgment-load** | How much context needed? | single-reply | multi-turn | full-session |
| **Reversibility** | If rule fires wrong, is damage reversible? | info-only | warn-reversible | deny-irreversible |
| **Evidence-clarity** | How clear is violation evidence? | self-evident | needs-explanation | ambiguous |

## Classification Thresholds

- **13-18**: COMMISSION candidate (hard enforce, runtime deny)
- **9-12**: OMISSION candidate (deadline/required-action, warn+escalate)
- **6-8**: ADVISORY (info-only, weekly review)

## Rubric Scores

| # | Rule | Tim | Obs | Det | Judg | Rev | Evid | Total | Reclassification |
|---|---|---|---|---|---|---|---|---|---|
| 1 | feedback_cmo_12layer_rt_loop | 1 | 1 | 1 | 1 | 3 | 1 | 8 | ADVISORY |
| 2 | feedback_cto_subagent_cannot_async_orchestrate | 1 | 1 | 1 | 1 | 3 | 2 | 9 | UPGRADE CANDIDATE: OMISSION |
| 3 | feedback_daemon_cache_workaround | 1 | 2 | 2 | 2 | 3 | 3 | 13 | UPGRADE CANDIDATE: COMMISSION |
| 4 | feedback_self_heal_via_daemon_window | 1 | 2 | 2 | 2 | 3 | 3 | 13 | UPGRADE CANDIDATE: COMMISSION |
| 5 | feedback_team_enforce_asymmetry | 1 | 1 | 1 | 1 | 3 | 2 | 9 | UPGRADE CANDIDATE: OMISSION |
| 6 | feedback_testing_is_ceo_scope | 2 | 3 | 3 | 3 | 2 | 3 | 16 | UPGRADE CANDIDATE: COMMISSION |
| 7 | feedback_scenario_c_is_real_usp | 1 | 1 | 1 | 1 | 3 | 2 | 9 | UPGRADE CANDIDATE: OMISSION |
| 8 | feedback_cto_owns_technical_modeling | 2 | 2 | 2 | 2 | 2 | 2 | 12 | UPGRADE CANDIDATE: OMISSION |
| 9 | feedback_boot_no_pipe | 3 | 3 | 3 | 3 | 2 | 3 | 17 | UPGRADE CANDIDATE: COMMISSION |
| 12 | feedback_rt1_0_lesson_default_is_production | 1 | 2 | 2 | 2 | 3 | 2 | 12 | UPGRADE CANDIDATE: OMISSION |

## Per-Rule Justifications

### 1. feedback_cmo_12layer_rt_loop (Total: 8 — ADVISORY)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Compliance requires reviewing an entire content deliverable after completion — audit-only, no pretool gate possible. |
| Observability | 1 | Detecting whether CMO actually walked through 12 layers + 5 counterfactuals requires reading the full deliverable output, not just tool calls. |
| Determinacy | 1 | No regex can verify "genuine 12-layer cognitive process" vs. checklist lip service — requires LLM judgment. |
| Judgment-load | 1 | Needs full session context to verify each layer was substantive (not just headings), including cross-referencing prior deliverables. |
| Reversibility | 3 | Info-only: CMO content can be revised; wrong detection costs only a re-review cycle. |
| Evidence-clarity | 1 | Ambiguous — presence of 12 section headers does not prove genuine cognitive engagement at each layer. |

### 2. feedback_cto_subagent_cannot_async_orchestrate (Total: 9 — OMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Architectural lesson learned — only detectable when a CTO dispatch attempt actually fails at runtime (audit-only). |
| Observability | 1 | Failure mode (nested sub-sub-agent block) manifests as timeout/hang, not as visible tool_call error pattern. |
| Determinacy | 1 | Requires understanding whether CTO intended async orchestration vs. sequential — pure LLM judgment on intent. |
| Judgment-load | 1 | Requires full session context: the dispatch chain, sub-agent nesting depth, and CDP vs Path B disambiguation. |
| Reversibility | 3 | Info-only advisory: wrong detection just logs a warning; CTO can ignore if doing sequential dispatch correctly. |
| Evidence-clarity | 2 | Partially clear — nested Agent calls are visible in tool_calls, but distinguishing intentional nesting from CDP anti-pattern requires context. |

### 3. feedback_daemon_cache_workaround (Total: 13 — COMMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Daemon cache staleness only surfaces after a sub-agent returns and CEO tries to write — audit-only. |
| Observability | 2 | Partially observable: permission-denied errors in Write tool results signal the stale-cache state. |
| Determinacy | 2 | Heuristic: "Write failed + recent sub-agent return + .ystar_active_agent mismatch" is a detectable pattern, but not pure regex. |
| Judgment-load | 2 | Needs multi-turn context: sub-agent dispatch + return + subsequent CEO write attempt. |
| Reversibility | 3 | Info-only: the workaround (pkill + rm socket) is non-destructive and self-healing. |
| Evidence-clarity | 3 | Self-evident: Write permission errors with active_agent file showing wrong agent_id is unambiguous. |

### 4. feedback_self_heal_via_daemon_window (Total: 13 — COMMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Recovery pattern only needed after active_agent drift lock-death — reactive by definition. |
| Observability | 2 | Partially observable: the 1-2 second window after pkill is empirically verified, Write success/fail gives signal. |
| Determinacy | 2 | Heuristic: "pkill daemon -> wait 1s -> Write succeeds" is a testable sequence but not pure regex. |
| Judgment-load | 2 | Multi-turn: needs the lock-death context (which daemon, which file locked, prior agent identity). |
| Reversibility | 3 | Info-only: self-heal attempts are safe; if wrong diagnosis, daemon restarts normally. |
| Evidence-clarity | 3 | Self-evident: the 2-step procedure (pkill + write) either works or does not — binary outcome. |

### 5. feedback_team_enforce_asymmetry (Total: 9 — OMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Enforcement asymmetry (CEO hooks live but sub-agents bypass) only detected via audit of CIEU event gaps. |
| Observability | 1 | Requires comparing CEO CIEU event density vs. sub-agent density — not visible in individual tool_calls. |
| Determinacy | 1 | Needs LLM judgment: low sub-agent CIEU count could be legitimate (fewer violations) or broken hooks (import failures). |
| Judgment-load | 1 | Full-session: comparing hook log errors (ModuleNotFoundError) across all agents requires session-wide scan. |
| Reversibility | 3 | Info-only: diagnostic knowledge — wrong detection just triggers an unnecessary investigation. |
| Evidence-clarity | 2 | Needs explanation: "sub-agent CIEU count = 0" requires checking hook import logs to distinguish zero-violation from broken-hook. |

### 6. feedback_testing_is_ceo_scope (Total: 16 — COMMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 2 | Can be checked posttool: if a non-CEO agent initiates pytest/red-team/dogfood, the tool_call reveals scope violation immediately. |
| Observability | 3 | Fully observable: agent_id + tool_name(Bash) + command containing "pytest"/"red-team" directly in tool_calls. |
| Determinacy | 3 | Deterministic: regex on tool_input.command for test-execution patterns + agent_id != "ceo" is a clean logic gate. |
| Judgment-load | 3 | Single-reply: the violating tool_call contains all needed context (agent_id + command). |
| Reversibility | 2 | Warn-reversible: blocking a test run delays but does not destroy work; test can be re-run by CEO. |
| Evidence-clarity | 3 | Self-evident: "agent=Ryan ran pytest" is unambiguous scope violation evidence. |

### 7. feedback_scenario_c_is_real_usp (Total: 9 — OMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Sales positioning accuracy can only be assessed after content is drafted — audit-only. |
| Observability | 1 | Requires reading the content to check if Scenario A (break_glass) is being presented as Scenario C (CROBA inject). |
| Determinacy | 1 | LLM judgment needed to distinguish "correctly presents Scenario C USP" vs. "mislabels Scenario A as USP." |
| Judgment-load | 1 | Full-session: needs knowledge of the Scenario A/B/C taxonomy + the specific content being produced. |
| Reversibility | 3 | Info-only: content drafts can be revised; wrong detection costs only a re-review. |
| Evidence-clarity | 2 | Needs explanation: the distinction between Scenario A (GOV_DOC_CHANGED audit) and Scenario C (CROBA inject) requires domain expertise. |

### 8. feedback_cto_owns_technical_modeling (Total: 12 — OMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 2 | Can be checked posttool: if CEO writes code touching formal-methods/Bayesian/adapter design, scope violation is visible. |
| Observability | 2 | Partially observable: CEO writing to src/ files with technical architecture content is detectable, but "providing direction" vs. "substituting design" is gray. |
| Determinacy | 2 | Heuristic: CEO agent_id + Write to ystar/ src paths is detectable, but intent (direction vs. design override) requires judgment. |
| Judgment-load | 2 | Multi-turn: needs to see whether CTO was dispatched first (proper delegation) or CEO bypassed (scope violation). |
| Reversibility | 2 | Warn-reversible: CEO's code can be reverted; CTO can override with authoritative design. |
| Evidence-clarity | 2 | Needs explanation: "CEO wrote adapter code" could be emergency fix (legitimate) or scope creep (violation). |

### 9. feedback_boot_no_pipe (Total: 17 — COMMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 3 | Pretool: can detect piping/background in the Bash command BEFORE execution (PreToolUse gate on governance_boot.sh). |
| Observability | 3 | Fully observable: tool_input.command string containing "governance_boot.sh" + pipe ("|") or background ("&") characters. |
| Determinacy | 3 | Deterministic: regex `governance_boot\.sh.*[\|&]` or `tail\|head.*governance_boot` is a clean logic match. |
| Judgment-load | 3 | Single-reply: the violating command is self-contained in one Bash tool_call input. |
| Reversibility | 2 | Warn-reversible: piped boot output hangs but does not corrupt state; re-running without pipe recovers. |
| Evidence-clarity | 3 | Self-evident: "bash governance_boot.sh | tail -5" is an unambiguous violation of the "run directly" rule. |

### 12. feedback_rt1_0_lesson_default_is_production (Total: 12 — OMISSION)

| Criterion | Score | Justification |
|---|---|---|
| Timing | 1 | Production-mode awareness violation only surfaces when an agent writes to real M-state files without realizing it — audit-only. |
| Observability | 2 | Partially observable: Write tool to governance/*.yaml or .ystar_session.json without explicit "production mode" acknowledgment in reply. |
| Determinacy | 2 | Heuristic: can detect writes to known production files, but distinguishing "intentional production write" from "forgot we are in production" requires context. |
| Judgment-load | 2 | Multi-turn: needs to check whether agent acknowledged production mode in prior turn or is operating under test assumptions. |
| Reversibility | 3 | Info-only: wrong detection just adds a reminder; actual production writes are separately guarded by other hooks. |
| Evidence-clarity | 2 | Needs explanation: the violation is about awareness/acknowledgment, not the write itself — inherently harder to evidence. |

## Summary

| Classification | Count | Rules |
|---|---|---|
| **COMMISSION (13+)** | 4 | feedback_daemon_cache_workaround (13), feedback_self_heal_via_daemon_window (13), feedback_testing_is_ceo_scope (16), feedback_boot_no_pipe (17) |
| **OMISSION (9-12)** | 5 | feedback_cto_subagent_cannot_async_orchestrate (9), feedback_team_enforce_asymmetry (9), feedback_scenario_c_is_real_usp (9), feedback_cto_owns_technical_modeling (12), feedback_rt1_0_lesson_default_is_production (12) |
| **ADVISORY (6-8)** | 1 | feedback_cmo_12layer_rt_loop (8) |

### Key Findings

1. **4 rules are UPGRADE CANDIDATE: COMMISSION** — these have sufficient observability and determinacy for automated runtime enforcement. `feedback_boot_no_pipe` (17) and `feedback_testing_is_ceo_scope` (16) score highest because they can be gated pretool with pure regex.

2. **5 rules are UPGRADE CANDIDATE: OMISSION** — these have detectable patterns but require multi-turn context or heuristic judgment, making them better suited for tracked-deadline enforcement with warn+escalate rather than hard deny.

3. **Only 1 rule remains truly ADVISORY** — `feedback_cmo_12layer_rt_loop` (8) requires LLM-level judgment across all criteria, making automated enforcement impractical. Best left as periodic human/LLM audit.

4. **Immediate implementation candidates**: `feedback_boot_no_pipe` and `feedback_testing_is_ceo_scope` could be converted to PreToolUse deny hooks within a single session — their deterministic regex patterns and single-reply judgment make them low-risk to automate.
