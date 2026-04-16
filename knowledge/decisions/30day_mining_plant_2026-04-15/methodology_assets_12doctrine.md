# Methodology Assets Inventory — 2026-04-15

**Purpose**: Canonical lookup index for methodologies/mechanisms/doctrines produced during the 2026-04-15 session. Use this as the first stop when an agent encounters a familiar-shaped problem — find the matching asset, then jump to its canonical file.

**Audience**: Aiden (CEO, next session) + any sub-agent onboarding after this session.

**Why this doc exists**: Board explicitly flagged the risk of losing today's methodology gains to session amnesia. Without a consolidated inventory, the next boot would read only `priority_brief.md` and miss these assets entirely. This file is the durable index.

**Convention**: Each asset = name + one-liner value + canonical location + when-to-apply trigger + real evidence (commit hash or measurable data).

---

## 1. Atomic Dispatch Mechanism

**Value**: 1 dispatch = 1 deliverable + ≤15 tool_uses budget. Forces sub-agents to ship incrementally instead of stalling in planning swamps.

**Canonical location**:
- `governance/sub_agent_atomic_dispatch.md` (doctrine body)
- `AGENTS.md §IRON RULE 0.5` (constitutional binding)

**When to apply**:
- Any time CEO spawns a sub-agent (CTO, engineers, CMO, CSO, CFO, Secretary)
- Any time a sub-agent plans to exceed 15 tool_uses in one call
- Any time a task description reads like a campaign (>1 deliverable)

**Real evidence**:
- Architecture Fix Campaign 2026-04-15: 72 tool_uses total, 9 deliverables shipped (atomic).
- Pre-atomic baseline: Ethan #5 dispatch consumed 47 tool_uses and shipped 0 deliverables.
- Efficiency delta: ~60x (9 ship / 72 uses vs 0 ship / 47 uses).
- Ship commits: `824092f8` (doctrine), `03948762` (AGENTS.md reference), `ac47b44d` (subagent_no_commit_after_5_writes rule).

**Why it works** (4 reasons):
1. Anthropic's tool_use cap acts as a hard circuit breaker — no unbounded drift.
2. Attention stays focused on one deliverable — no context dilution.
3. Fast-fail surfaces stuck sub-agents in <15 uses instead of 60+.
4. Incremental commits create a ratchet — each atomic ship is non-losable progress.

---

## 2. CZL Five-Tuple Work Method (Y*/Xt/U/Yt+1/Rt+1)

**Value**: Every task opens with an explicit ideal contract (Y\*), current state (Xt), action set (U), predicted end-state (Yt+1), and honest residual (Rt+1). Loop until Rt+1=0.

**Canonical location**:
- `governance/WORKING_STYLE.md §第十二条` (five-tuple definition)
- `.czl_subgoals.json` (CEO dogfood runtime state)
- `knowledge/shared/unified_work_protocol_20260415.md` (framework integration)

**When to apply**:
- Top of every task reply (mandatory per AGENTS.md Iron Rule 1.6)
- Before claiming "done" — if Rt+1 > 0, task is not complete
- When a sub-agent reports completion — verify Rt+1=0 with evidence

**Real evidence**:
- CEO dogfood: `.czl_subgoals.json` tracked across today's session.
- Memory reminder `feedback_cieu_5tuple_task_method.md` codified 2026-04-14.
- Replaces the failed "sub-agent said done so it's done" pattern.

---

## 3. Three-Layer Doctrine (规则写了 / 在跑 / 在拦)

**Value**: A rule is not enforced until three layers verify: (1) rule written, (2) runtime actually running, (3) hook actively blocking violations. Prevents "doc exists but nothing enforces it" drift.

**Canonical location**:
- `AGENTS.md §Rule Verification Three-Layer Doctrine`

**When to apply**:
- Any time a new ForgetGuard rule or governance hook is added
- Any time someone claims "we already have a rule for that" — verify all three layers
- Weekly K9 audit checks

**Real evidence**:
- ForgetGuard rules `ceo_no_midstream_checkin` (commit `073d641b`) + `subagent_no_commit_after_5_writes` (`ac47b44d`) — both shipped with all three layers verified.
- CZL meta-audit commit `067991bd` used this doctrine to catch 40% identity-drift in audit layer.

---

## 4. Session-Level Y\* Five Hard Constraints

**Value**: Five session-scope invariants that must hold regardless of task — if any breaks, session is in governance violation.

**Canonical location**:
- `AGENTS.md §Session-Level Y\* Doctrine`

**When to apply**:
- Session boot (verify all 5 hold)
- After any governance file edit (re-verify)
- When Board asks "are we still compliant" — audit against these 5

**Real evidence**:
- Constitutional commits `dab004c7` (Total Y\* + 6-Step CZL Daily Loop), `823a0595` (CTO hourly K9 patrol + CMO weekly README audit mandates).

---

## 5. Defer ≠ Schedule Distinction

**Value**: "Defer" (push to later without a concrete return mechanism) is a banned anti-pattern. "Schedule" (calendared trigger with owner + return time) is allowed. Clarifies when delayed work is acceptable.

**Canonical location**:
- `AGENTS.md §Defer ≠ Schedule Distinction`

**When to apply**:
- Any time an agent wants to postpone work
- Any time Board hears "we'll get to that later" — ask: is it deferred or scheduled?
- Weekly secretary audit for stale `CURRENT_TASKS.md` items

**Real evidence**:
- Memory reminder `feedback_no_clock_out.md` codifies the ban on deferral language.
- CEO hard constraint: every reply must contain a new tool_call — no "wait for later" permitted.

---

## 6. CEO Engineering Boundary + Dispatch Self-Check

**Value**: CEO (Aiden) is explicitly barred from writing engineering code. Must dispatch via CTO (Ethan). Self-check protocol catches boundary violations before they commit.

**Canonical location**:
- `AGENTS.md §CEO Engineering Boundary`
- `governance/ceo_dispatch_self_check.md` (step-by-step checklist)

**When to apply**:
- Any time CEO considers editing `scripts/`, `src/`, `Y-star-gov/`, `gov-mcp/`
- Any time a task involves code/tests/git operations
- Before spawning an engineer sub-agent — run self-check to confirm dispatch is warranted

**Real evidence**:
- ForgetGuard rule shipped commit `20f4018f` (ceo engineering boundary rule + agent_filter support).
- Doctrine shipped commit `89ead579` (CEO dispatch self-check protocol, W24 R5 fix).
- AGENTS.md reference commit `814f55e1` (CEO Dispatch Self-Check sub-section).

---

## 7. CEO Mid-Stream Check-In Protocol

**Value**: Prohibits CEO from interrupting sub-agents mid-flight with status pings. Sub-agents must complete their atomic dispatch before CEO re-engages. Protects atomic-dispatch discipline.

**Canonical location**:
- `governance/ceo_midstream_checkin_protocol.md`

**When to apply**:
- Any time CEO is waiting on a sub-agent and feels the urge to "just check in"
- Any time Board asks CEO "what's {engineer} doing right now" — redirect to the sub-agent's eventual return, not a mid-stream ping

**Real evidence**:
- Doctrine commit `30e99091` (CEO mid-stream check-in protocol, W25 R6 root fix).
- ForgetGuard rule commit `073d641b` (ceo_no_midstream_checkin enforcement layer).

---

## 8. IRON RULE 0 — NO CHOICE QUESTIONS

**Value**: CEO must never present Board with "please choose 1/2/3". CEO decides and executes; Board vetoes if needed. Essential for unattended autonomous operation.

**Canonical location**:
- `CLAUDE.md` top section (hard constraint)
- `AGENTS.md` top section (IRON RULE 0)

**When to apply**:
- Every Board-facing message
- Every decision point where the agent feels tempted to ask "which one"
- Any sub-agent report that punts a decision back to CEO

**Real evidence**:
- Constitutional commits `e8a4c55e` (CLAUDE.md top) + `46e3249c` (AGENTS.md top) + `168720c2` (AGENTS.md head injection).

---

## 9. Sub-Agent Boot Prompt Template

**Value**: Standardized boot context injected into every sub-agent dispatch. Ensures sub-agents know their Y\*, atomic budget, canonical references, and return contract before the first tool_use.

**Canonical location**:
- `governance/sub_agent_boot_prompt_template.md`

**When to apply**:
- Every sub-agent spawn (CTO, engineers, CMO, CSO, CFO, Secretary)
- Any new agent role added to the roster — reuse the template structure

**Real evidence**:
- Doctrine commit `190a6020` (sub_agent_boot_prompt_template.md — W22 constitutional boot context for all sub-agent dispatch).

---

## 10. K9 Audit v3 Three-Layer (Liveness / Causal Chain / Invariant)

**Value**: Automated audit framework with three orthogonal checks — is the agent alive, does its causal chain hold, do invariants hold. Runs on 6h schedule.

**Canonical location**:
- `scripts/k9_audit_v3.py` (implementation)
- `governance/cieu_event_taxonomy.md` (event naming + aliases)

**When to apply**:
- Scheduled: every 6 hours via cron
- On demand: after major governance change, before a release, when Board suspects drift

**Real evidence**:
- Feature commit `8e35d053` (k9_audit_v3.py — 3-layer audit framework).
- Doctrine commit `e4d0675d` (CIEU event taxonomy canonical naming — 148 types registered, 5 audit_v3 aliases, ForgetGuard rule spec).
- Schema fix commit `ba4328d3` (W26.1 schema + event_type aliases).
- Cron schedule commit `34a45256` (6h schedule + wire_integrity_check retain).

---

## 11. HiAgent Working Memory Subgoal Compression

**Value**: Compresses long-horizon task state into a small JSON subgoal tree so agents (especially sub-agents with short context) can resume without reloading full session history.

**Canonical location**:
- `.czl_subgoals.json` (CEO dogfood runtime state)
- `governance/sub_agent_boot_prompt_template.md` (injection pattern)

**When to apply**:
- Long-running multi-hour tasks where context window pressure is real
- Any sub-agent dispatch that depends on prior session state
- Session handoff — subgoals persist; full chat history doesn't

**Real evidence**:
- `.czl_subgoals.json` tracked across session (git status shows modified).
- Integrated into sub_agent_boot_prompt_template commit `190a6020`.

---

## 12. WORLD_STATE Mission Control (4-Repo God View)

**Value**: Generates a unified mission-control view across the 4 workspace repos (ystar-company, Y-star-gov, gov-mcp, K9Audit). Single file for Aiden to glance at and know "where is everything right now".

**Canonical location**:
- `scripts/generate_world_state.py` (generator)
- `memory/WORLD_STATE.md` (output artifact)

**When to apply**:
- Session boot — check WORLD_STATE before diving into tasks
- Cross-repo coordination moments (e.g., product change needs ops doc update)
- Board status requests — WORLD_STATE is the 30-second answer

**Real evidence**:
- Script + output artifact both present in repo (verified ls).
- Replaces ad-hoc grep-across-repos pattern that previously cost 10+ tool_uses.

---

## How to use this index (next session)

1. Boot as CEO (Aiden) per `CLAUDE.md §SESSION BOOT`.
2. If encountering a familiar-shaped problem, grep this file for the matching asset name.
3. Jump to the canonical location — do NOT paraphrase from this index alone.
4. Apply the trigger conditions to decide whether the asset fits.
5. Cite the asset's commit hash when referencing in new work (preserves provenance).

---

## Session authorship

- Produced: 2026-04-15 session
- Codified by: Samantha Lin (Secretary) per Board P0 atomic dispatch
- Canonical authority: AGENTS.md IRON RULE 0.5 (atomic dispatch budget ≤15 tool_uses)
