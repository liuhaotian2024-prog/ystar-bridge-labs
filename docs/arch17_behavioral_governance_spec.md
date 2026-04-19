# ARCH-17: Behavioral Governance Layer

**Author**: Ethan Wright (CTO)
**Date**: 2026-04-18
**Status**: SPEC (L1)
**Authority**: Board directive 2026-04-18
**Implementers**: Leo Chen (eng-kernel), Maya Patel (eng-governance), Ryan Park (eng-platform)

---

## 1. Problem Statement

Y*gov currently enforces **structural** governance: file permissions, agent identity, dispatch routing, session lifecycle. It does NOT enforce **behavioral** governance: cognitive discipline, communication quality, work habits, honesty signals.

30+ behavioral rules exist as MEMORY.md feedback entries. These are LLM-self-applied: the agent reads them at boot, promises to follow them, then degrades under pressure. This is structurally inevitable, not a willpower problem.

**Empirical evidence of regression (2026-04-18 Board-caught)**:
- CEO built new components that already existed (reinventing) -- violates `feedback_god_view_before_build.md`
- CEO produced activity without progress (performative busyness) -- violates `feedback_status_maturity_taxonomy.md`
- CEO postponed work without blocker (procrastination) -- violates `feedback_no_clock_out.md`
- CEO stated intent without executing -- violates `feedback_no_deferred_dispatch_promise.md`

**Root cause**: Self-enforcement has no backstop. When context window fills, cognitive load rises, or lock-death pressure mounts, self-enforcement is the first thing to degrade. Per `autonomy_degradation_root_cause_2026_04_13.md`, this is factor #1 (decision muscle atrophy) and factor #7 (no proactive-work hard constraint).

---

## 2. Taxonomy: 7 Behavioral Enforcement Categories

Classification of all 41 feedback memory files into enforceable categories.

### Category 1: PRE-OUTPUT DISCIPLINE
**Definition**: Rules governing the text Claude emits before it reaches the user/Board.

| Feedback File | Rule Summary |
|---|---|
| `feedback_aiden_authority_no_questions.md` | No choice questions; CEO decides and executes |
| `feedback_subagent_no_choice_question.md` | Iron Rule 0 propagates to sub-agent receipts |
| `feedback_ceo_reply_must_be_5tuple.md` | CEO replies to Board must be Y*/Xt/U/Yt+1/Rt+1 structured |
| `feedback_no_consultant_time_scales.md` | No "one week / 3 days" consultant time units internally |
| `feedback_methodology_no_human_time_grain.md` | Strip human cadence from imported frameworks |
| `feedback_status_maturity_taxonomy.md` | Every work item must carry L0-L5 maturity tag |
| `feedback_address_laoda.md` | Board-facing replies use proper addressing convention |
| `feedback_restart_quietude.md` | Post-boot: one line only, no governance dump |
| `feedback_close_stub_trigger.md` | No EOD stub while Board is online |
| `feedback_board_shell_marker.md` | Shell commands to Board must use marker format |
| `feedback_article11_framing.md` | Frame sub-agent dispatch as "Article 11", not passive waiting |

**Existing enforcement**: ForgetGuard `choice_question_to_board` (deny), postponement-language rules (deny). Stop hook scans for avoidance/choice patterns post-reply (warn only). `hook_ceo_pre_output.py` checks U-workflow signals on Write to external paths.

**Gap**: 5-tuple structure, L-tag presence, consultant time-scale language, and addressing convention have ZERO runtime enforcement. Self-applied only.

### Category 2: PRE-EXECUTION DISCIPLINE
**Definition**: Rules governing what must happen BEFORE an agent takes a significant step (build, create, dispatch).

| Feedback File | Rule Summary |
|---|---|
| `feedback_god_view_before_build.md` | Glob+Grep 4 repos before proposing new component |
| `feedback_ceo_ecosystem_view_required.md` | Ecosystem Dependency Map before any design dispatch |
| `feedback_testing_is_ceo_scope.md` | Testing is CEO scope, no Board approval needed |
| `feedback_no_defer_immediate_activation.md` | Changes effective immediately, no "next session" postponement |
| `feedback_cieu_5tuple_task_method.md` | Every task driven by 5-tuple until Rt+1=0 |
| `feedback_action_model_3component.md` | Every dispatch = backlog + K9 + AC (3-component) |

**Existing enforcement**: ForgetGuard `czl_dispatch_missing_5tuple` (deny). `task_dispatch_without_y_star` (deny, dry_run grace period).

**Gap**: "god view before build" has NO enforcement. An agent can Write a new file to `scripts/` without any pre-check that the capability already exists. This is today's highest-regression category.

### Category 3: DISPATCH DISCIPLINE
**Definition**: Rules governing how work is assigned to sub-agents / engineers.

| Feedback File | Rule Summary |
|---|---|
| `feedback_dispatch_via_cto.md` | Cross-engineer work must go through CTO |
| `feedback_use_whiteboard_not_direct_spawn.md` | Post to dispatch_board.json, not Agent spawn |
| `feedback_taskcard_not_dispatch.md` | Writing task card without Agent call is not dispatch |
| `feedback_explicit_git_op_prohibition.md` | Spawn prompts must include "no git commit/push" clause |
| `feedback_hi_agent_campaign_mechanism.md` | Dispatch must include BOOT CONTEXT block |
| `feedback_no_deferred_dispatch_promise.md` | "Next-round dispatch X" without same-turn Agent call = hollow promise |
| `feedback_cto_subagent_cannot_async_orchestrate.md` | CDP structural limitation: CTO cannot nest sub-sub-agents |

**Existing enforcement**: ForgetGuard `ceo_direct_engineer_dispatch` (deny), `ceo_skip_gov_dispatch` (deny). `hook_pretool_agent_dispatch.py` gates Agent tool calls.

**Gap**: Hollow dispatch promise detection, whiteboard-vs-direct-spawn enforcement, git-op prohibition in spawn payload, BOOT CONTEXT block presence check -- all unenforced.

### Category 4: RECEIPT/CLOSE DISCIPLINE
**Definition**: Rules governing how completed work is verified and marked done.

| Feedback File | Rule Summary |
|---|---|
| `feedback_subagent_receipt_empirical_verify.md` | Never trust self-reported Rt+1=0; verify artifacts on disk |
| `feedback_cmo_12layer_rt_loop.md` | CMO content must complete 12-layer + 5 counterfactual checks |
| `feedback_no_static_image_for_video.md` | Video task L4 must be real dynamic video |
| `feedback_rt1_0________lesson_default_is_production_mode.md` | Default is production mode |
| `feedback_rt1_0________lesson_production_mode_writes_to_real_m.md` | Production mode writes to real MEMORY |
| `feedback_team_enforce_asymmetry.md` | Format compliance != runtime enforcement; smoke-test gates |

**Existing enforcement**: ForgetGuard `czl_receipt_rt_not_zero` (deny). Stop hook `auto_validate_subagent_receipt` runs post-reply.

**Gap**: Empirical verification (ls/wc/pytest after sub-agent return) is self-applied. tool_uses=0 or duration<30s red-flag detection has no automatic trigger.

### Category 5: DELEGATION/IDENTITY DISCIPLINE
**Definition**: Rules governing who does what and agent identity boundaries.

| Feedback File | Rule Summary |
|---|---|
| `feedback_default_agent_is_ceo.md` | Default boot identity is CEO (Aiden) |
| `feedback_cto_owns_technical_modeling.md` | Technical arch decisions = CTO scope, not CEO |
| `feedback_daemon_cache_workaround.md` | Daemon caches stale agent identity; pkill+rm to fix |
| `feedback_self_heal_via_daemon_window.md` | Self-heal active_agent drift via daemon kill window |
| `feedback_subagent_registry_boot_only.md` | Agent registry only reloads at session boot |
| `feedback_no_clock_out.md` | CEO never "clocks out" unilaterally |

**Existing enforcement**: hook_wrapper.py checks `.ystar_active_agent` for file-write scope. `hook_session_start.py` sets identity at boot.

**Gap**: "CEO is doing CTO's work" (technical design, formal methods) has no enforcement. The delegation boundary between coordinator and engineer roles is structurally unenforced.

### Category 6: HONESTY/TRANSPARENCY DISCIPLINE
**Definition**: Rules governing truthful communication and disclosure.

| Feedback File | Rule Summary |
|---|---|
| `feedback_ai_disclosure_mandatory.md` | All external outreach must disclose AI authorship |
| `feedback_scenario_c_is_real_usp.md` | Don't overclaim governance evidence (Scenario A vs C) |
| `feedback_defer_vs_schedule_distinction.md` | Postponement (avoidance) vs scheduling (planning) must be distinguished |
| `feedback_break_glass_disable_project_hook.md` | Break-glass protocol for lock-death |

**Existing enforcement**: ForgetGuard postponement-language rule (deny) catches avoidance keywords but cannot distinguish avoidance from scheduling (known false-positive source).

**Gap**: AI disclosure in outbound content has NO enforcement. Overclaim detection (claiming L4 SHIPPED without live evidence) is partially covered by receipt validation but not systematically.

### Category 7: OPERATIONAL HYGIENE
**Definition**: Rules governing infrastructure discipline, boot protocol, and process integrity.

| Feedback File | Rule Summary |
|---|---|
| `feedback_boot_no_pipe.md` | Run governance_boot.sh directly, no pipes |

**Existing enforcement**: `governance_boot.sh` validates 5 E2E constraints. Session watchdog monitors health signals.

**Gap**: Minimal. Low priority for additional enforcement.

---

## 3. Enforcement Mechanism Matrix

| Category | Enforcement Point | Mechanism | Rationale |
|---|---|---|---|
| **1. Pre-Output** | **Stop hook reply scan** | Extend `hook_stop_reply_scan.py` with 4 new detectors: (a) 5-tuple presence in >200char Board replies, (b) L-tag presence in status reports, (c) consultant time-scale language, (d) addressing convention in Board-facing text | Stop hook is post-emission (warn-only) which is correct: blocking output for formatting violations causes lock-death. Warn + CIEU event is sufficient. |
| **2. Pre-Execution** | **Pre-tool hook (PreToolUse)** | New detector in `hook_wrapper.py` for Write tool calls: before creating a new file in `scripts/` or `ystar/`, require evidence of prior Glob/Grep search in the same session turn. Deny if no ecosystem scan evidence. | Highest-value enforcement. Reinventing-the-wheel is a Write -- catching it at Write-time prevents the waste. |
| **3. Dispatch** | **Dispatch board broker check** | Extend `hook_pretool_agent_dispatch.py` with payload scan: (a) git-op prohibition clause present, (b) BOOT CONTEXT block present, (c) no hollow-dispatch language. | Dispatch is the tightest gate: all sub-agent work flows through Agent tool call. |
| **4. Receipt/Close** | **Omission obligation** | New omission rule: after sub-agent Agent tool call returns, CEO MUST within 2 turns execute at least one empirical verification command. OmissionEngine emits `RECEIPT_UNVERIFIED` if obligation expires. | Receipt verification is an obligation (must-do), not a gate (must-pass). |
| **5. Delegation/Identity** | **CIEU event rule** | Pattern detector: when CEO writes formal-method predicates, Bayesian math, or architecture code directly, emit `CEO_SCOPE_VIOLATION_TECHNICAL_DESIGN`. 3 events in one session = auto-warn to Board. | Identity boundary violations are patterns, not single events. |
| **6. Honesty/Transparency** | **Pre-output hook (PreToolUse on Write)** | Extend `hook_ceo_pre_output.py`: when Write target is `content/` or `marketing/` or `sales/`, scan for AI disclosure markers. Deny if writing external-facing content without disclosure signal. | External content without AI disclosure has legal risk (CAN-SPAM, GDPR Art 14). |
| **7. Operational Hygiene** | **No additional enforcement** | Existing boot validation + session watchdog cover this. | Lowest marginal return. |

---

## 4. Industry Precedent Scan

### 4.1 Constitutional AI (Anthropic, 2022)

**Reference**: Bai et al., "Constitutional AI: Harmlessness from AI Feedback," arXiv:2212.08073.

Constitutional AI embeds behavioral principles as training-time constraints. Our feedback memories ARE the constitution. The difference: CAI bakes rules into weights (pre-training); ARCH-17 enforces at runtime (hooks). Runtime enforcement is the only option when you cannot retrain the model.

**Applicable pattern**: The "critique then revise" loop maps to our Stop hook (post-emission scan) + CIEU event (critique record) + next-turn self-correction (revision). Stop hook should emit "suggested correction" text, mirroring the CAI revision step.

### 4.2 Guardrails AI / NeMo Guardrails (NVIDIA, 2023)

**Reference**: NVIDIA NeMo Guardrails, https://github.com/NVIDIA/NeMo-Guardrails, 2023.

Architecture: `input rails -> LLM -> output rails -> action rails`. Maps to our hooks: PreToolUse = input rail, Stop hook = output rail, OmissionEngine = missing "must-do" rail. NeMo's "canonical form" intermediate representation should inform our evolution from regex to semantic-level intent classifiers.

### 4.3 Open Policy Agent (OPA) / Rego (CNCF, 2018+)

**Reference**: OPA documentation, https://www.openpolicyagent.org/docs/latest/

Key insight: **policy-as-data separation**. Behavioral rules should be declared in YAML (`behavioral_rules.yaml`), not hardcoded in hook Python scripts. OPA's `allow/deny/undecided` three-valued logic maps well -- most behavioral rules should default to `undecided` (allow with CIEU audit trail) rather than `deny`.

### 4.4 Langfuse Eval / Tracing (2023+)

**Reference**: Langfuse documentation, https://langfuse.com/docs/scores/model-based-evals

Our Stop hook is architecturally identical to a Langfuse eval. Missing piece: structured scoring -- each behavioral violation should produce a numeric severity score feeding into an aggregate "behavioral health" metric alongside AC (Agent Capability).

### 4.5 LLM-as-Judge (Various, 2024+)

**Reference**: Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," NeurIPS 2023.

Phase 3 only. For ambiguous cases where regex produces >20% false positive rate. Call local Gemma via Ollama, capped at 1 call per 5 minutes.

---

## 5. Prioritized Implementation Plan

### Phase 1: Highest Catch-Rate (3 categories)

**Selection rationale**: These match the 4 empirical regressions Board caught on 2026-04-18.

#### P1-A: Pre-Execution "God View" Gate (Category 2)
**Regression caught**: Reinventing (building what already exists)
- Extend `hook_wrapper.py` PreToolUse handler
- When tool = Write AND `file_path` targets `scripts/*.py` or `ystar/**/*.py` (new file):
  - Check session tool call history (`/tmp/ystar_pretool_state.json`)
  - Require at least 1 Glob and 1 Grep in preceding 10 tool calls
  - No evidence: deny with remediation message
- Whitelist: `tests/`, `.claude/tasks/` (routine new files)
- **Acceptance criteria**: (a) Write-without-prior-Glob = deny, (b) Write-after-Glob = allow, (c) state file tracks last 10 tool calls
- **Assignee**: Ryan Park (eng-platform), 8-12 tool_uses

#### P1-B: Dispatch Payload Integrity Gate (Category 3)
**Regression caught**: Declarative-only promises
- Extend `hook_pretool_agent_dispatch.py` for Agent tool
- Required elements in `prompt` field:
  1. Git-op prohibition: deny if absent
  2. BOOT CONTEXT block: deny if absent
  3. Scope guard: warn if absent
- Add `coordinator_hollow_dispatch_promise` ForgetGuard rule
- **Assignee**: Maya Patel (eng-governance), 10-15 tool_uses

#### P1-C: Receipt Verification Obligation (Category 4)
**Regression caught**: Performative busyness
- New OmissionEngine obligation: `VERIFY_SUBAGENT_RECEIPT`
- Triggered on Agent tool return; requires 1 verification tool call within 3 turns
- Red-flag: `tool_uses: 0` or `duration < 30s` = emit `SUBAGENT_HALLUCINATION_RISK` immediately
- **Assignee**: Leo Chen (eng-kernel), 12-18 tool_uses

### Phase 2: Medium Priority

#### P2-A: Pre-Output Quality Scan Extensions (Category 1)
- 4 new Stop hook detectors: 5-tuple, L-tag, time-scale, addressing
- **Assignee**: Maya Patel, 15-20 tool_uses

#### P2-B: Delegation Boundary Enforcement (Category 5)
- CIEU pattern detector for CEO writing technical design
- 3+ events in session = auto-escalate to Board
- **Assignee**: Ryan Park, 8-10 tool_uses

### Phase 3: Lower Priority

#### P3-A: Honesty/Transparency Enforcement (Category 6)
- AI disclosure gate on Write to `content/`, `marketing/`, `sales/`

#### P3-B: Semantic Upgrade (cross-cutting)
- Replace highest-FP regex rules with semantic classifier via local Gemma

---

## 6. Self-Reference Safety

All behavioral enforcement rules apply to ALL agents, not just CEO. Board explicit directive: "all team members' behavioral rules."

### Agent Scope Matrix

| Rule | CEO | CTO | Engineers | C-Suite |
|---|---|---|---|---|
| No choice questions | YES | YES | YES | YES |
| 5-tuple structured replies | YES (to Board) | YES (to CEO) | YES (to CTO/CEO) | YES (to CEO) |
| L-tag on status reports | YES | YES | YES | YES |
| God view before build | YES | YES (builds arch) | YES (creates files) | N/A |
| Dispatch payload integrity | YES (dispatches) | YES (dispatches) | N/A (receivers) | N/A |
| Receipt verification | YES (receives receipts) | YES (receives eng receipts) | N/A | N/A |
| AI disclosure | YES | YES | YES | YES |
| Git-op prohibition | N/A | N/A | YES (enforced ON them) | N/A |
| No procrastination language | YES | YES | YES | YES |

### CTO-Specific Rules
- CTO specs missing `## Formal Definitions` + `## Mathematical Model` sections: ForgetGuard `spec_missing_formal_section` (needs implementation)
- CTO must proactively install tools/skills without CEO dispatch

### Implementation Note
Hook scripts determine active agent from `.ystar_active_agent`. All behavioral rules must check this value and apply correct agent-scope filter via lookup table, not per-rule hardcoded checks.

---

## 7. Failure Mode Analysis

### F1: Rule fires but agent cannot comply (lock-death risk)
- State file `/tmp/ystar_pretool_state.json` append-only, last 50 tool calls. On corruption: fail-open + CIEU event.
- All DENY decisions include exact remediation steps.
- 3 consecutive denies on same target within 5 minutes: auto-downgrade to warn-only.
- Break-glass: Board disables via `jq '.hooks.PreToolUse=[]' .claude/settings.json`.

### F2: Rule fires with false positive (crying wolf)
- Phase 1-2 rules default to WARN except: choice questions, AI disclosure, git-op prohibition (DENY).
- `false_positive_rate` field per rule. Auto-demote to audit-only if FP >30% after 100 firings.
- Agent self-reports FP via `# FP: <rule_name>` comment; Stop hook records for rate calculation.

### F3: Enforcement creates perverse incentives (gaming)
- Phase 2: God View gate checks Glob results non-empty AND Read/Grep followed on result path.
- K9 audit: sample 5 random gate-pass instances per rule, check substantive compliance.

### F4: Behavioral + structural enforcement cascade (compound deny)
- Structural gates fire FIRST. If structural denies, behavioral gates skip (short-circuit).
- Maximum 1 deny message per tool call. Priority indicators: `[STRUCTURAL]` vs `[BEHAVIORAL]`.

### F5: Hook process crashes (silent failure)
- Behavioral engine: stdlib-only (`re`, `json`, `os`, `sqlite3`). Zero Y*gov import dependency.
- Session watchdog pings engine health every 30s. No response: `BEHAVIORAL_ENGINE_DOWN` + auto-restart.
- Boot smoke test: governance_boot.sh fires deliberate violation, verifies deny, cleans up.

### F6: Sub-agent has no behavioral enforcement
- Enforced at TWO parent-context points: dispatch-time payload scan + receipt-time verification.
- Sub-agents do NOT run behavioral hooks internally (Claude Code limitation).
- Receipt verification obligation (P1-C) ensures parent-context validation.

---

## 8. Behavioral Rule Schema

```yaml
# Schema for governance/behavioral_rules.yaml
rules:
  - name: string           # unique identifier
    category: enum          # pre_output | pre_execution | dispatch | receipt_close |
                            # delegation_identity | honesty | operational
    enforcement_point: enum # pre_tool_hook | stop_hook | omission | cieu_event |
                            # dispatch_broker
    severity: enum          # deny | warn | audit
    agent_scope: list       # [ceo, cto, eng-kernel, eng-governance, eng-platform,
                            #  eng-domains, cmo, cso, cfo, secretary]
    pattern: string         # regex or heuristic identifier
    pattern_type: enum      # regex | tool_sequence | content_scan | metadata_check
    message: string         # remediation message shown on fire
    evidence_file: string   # feedback memory file documenting the gap
    false_positive_rate: float  # tracked, auto-demote if >0.30
    created_at: datetime
    dry_run_until: datetime | null
    escalation_threshold: int | null  # N fires per session before auto-escalation
```

Extends ForgetGuard schema with: `category`, `enforcement_point`, `agent_scope`, `pattern_type`, `evidence_file`, `false_positive_rate`, `escalation_threshold`.

---

## 9. Formal Definitions

Let B = set of all behavioral rules {b_1, ..., b_n}.
Let A = set of all agent steps (tool calls + text emissions).
Let S = session state (tool call history, active agent, CIEU events).

**Enforcement predicate**:
```
enforce(b, a, s) = 
  DENY   if severity(b) = deny AND match(pattern(b), a, s) AND agent(s) in scope(b)
  WARN   if severity(b) = warn AND match(pattern(b), a, s) AND agent(s) in scope(b)  
  AUDIT  if severity(b) = audit AND match(pattern(b), a, s) AND agent(s) in scope(b)
  ALLOW  otherwise
```

**Short-circuit rule** (F4 mitigation):
```
For step a, if exists structural_rule r such that enforce(r, a, s) = DENY:
  skip all behavioral rules for a
  return DENY(r)
```

**Escalation predicate**:
```
escalate(b, s) = TRUE iff count({a in session(s) | enforce(b, a, s) = WARN}) >= threshold(b)
```

**Fail-open invariant**:
```
For all b in B, a in A, s in S:
  if state_corrupt(s) then enforce(b, a, s) = ALLOW AND emit(BEHAVIORAL_GATE_STATE_CORRUPT)
```

## 10. Mathematical Model

### Behavioral Health Score

Define BH(t) = behavioral health at session time t:

```
BH(t) = 1 - (sum over b in B of w(b) * v(b, t)) / (sum over b in B of w(b))
```

Where:
- w(b) = weight of rule b (deny=3, warn=2, audit=1)
- v(b, t) = violation count of rule b in window [t-W, t], capped at 1
- W = sliding window of last 20 tool calls

BH(t) ranges [0, 1]. Thresholds:
- BH >= 0.8: healthy (green)
- 0.5 <= BH < 0.8: degrading (yellow, emit BEHAVIORAL_HEALTH_DEGRADED)
- BH < 0.5: critical (red, emit BEHAVIORAL_HEALTH_CRITICAL, notify Board)

Combined health = 0.5 * AC + 0.5 * BH (integrates with session_watchdog.py AC score).

### False Positive Adaptation

```
FP_rate(b, t) = FP_count(b, [0, t]) / total_fires(b, [0, t])
```

Auto-demotion when FP_rate > 0.30 after min 10 fires:
```
severity(b) <- max(severity(b) - 1, audit)
emit(BEHAVIORAL_RULE_DEMOTED, {rule: b, fp_rate: FP_rate(b, t)})
```

---

## 11. Implementation Dependencies

### Files to Create (Phase 1)
1. `governance/behavioral_rules.yaml` -- rule declarations (Leo)
2. `ystar/governance/behavioral_engine.py` -- rule evaluation engine, stdlib-only (Leo)
3. Extensions to `scripts/hook_wrapper.py` -- pre-execution gate (Ryan)
4. Extensions to `scripts/hook_pretool_agent_dispatch.py` -- dispatch payload scan (Maya)
5. Extensions to `scripts/hook_stop_reply_scan.py` -- 4 new post-output detectors (Maya)
6. New omission type in `ystar/governance/omission_engine.py` -- receipt verification (Leo)
7. State tracker `/tmp/ystar_pretool_state.json` -- tool call history (Ryan)
8. Tests: `tests/governance/test_behavioral_engine.py` (all)

### Files to Modify (Phase 1)
1. `scripts/governance_boot.sh` -- add behavioral engine smoke test
2. `scripts/session_watchdog.py` -- integrate BH score
3. `ystar/governance/forget_guard_rules.yaml` -- add `coordinator_hollow_dispatch_promise` rule

### Cross-Repo Dependencies
- `Y-star-gov/ystar/governance/omission_engine.py` -- new obligation type
- `Y-star-gov/ystar/governance/forget_guard.py` -- new rule loading
- No K9Audit dependencies (read-only repo)

---

## 12. Non-Goals

1. **Not replacing ForgetGuard**: Behavioral rules extend ForgetGuard. ForgetGuard = text-pattern rules; behavioral engine = multi-signal rules (tool sequence, metadata, session state).
2. **Not training-time enforcement**: Cannot fine-tune Claude. All enforcement is runtime.
3. **Not blocking all behavioral violations**: Most rules are warn-level. Goal = audit trail + self-correction nudge.
4. **Not building a general-purpose policy engine**: Y*gov-specific. OPA/Rego patterns inform but we do not import OPA.
5. **Not LLM-as-judge in Phase 1**: Semantic classification via secondary LLM is Phase 3 only.

---

## 13. Success Metrics

| Metric | Baseline (pre-ARCH-17) | Target (post-Phase 1) |
|---|---|---|
| Board-caught behavioral regressions per session | ~4 (2026-04-18 data) | <=1 |
| Behavioral violations with CIEU audit trail | 0% (no detection) | >=80% produce CIEU event |
| False positive rate per rule | N/A | <20% after 50 firings |
| Lock-death incidents from behavioral gates | N/A | 0 (fail-open + 3-deny auto-downgrade) |
| BH score during normal operation | unmeasured | >=0.7 mean |

---

*End of spec. Implementation dispatched via dispatch_board.json.*
