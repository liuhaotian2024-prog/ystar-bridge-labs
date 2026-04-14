# AMENDMENT-025: Compliance Read-Before-Action (CROBA) Framework

**Type:** Infrastructure — Governance enforcement prerequisite  
**Status:** PROPOSED  
**Date:** 2026-04-13  
**Author:** CTO (Ethan Wright)  
**L-tag:** L6-ENFORCEMENT-PREREQUISITE (新建 — 现有标签无直接命中，CROBA 属于元级 enforcement 要求)  

---

## §0 Board Mandate (原话提取)

> "随时主动+被动读合规机制内容才是终极解"  
> — Haotian Liu, 2026-04-13, A025 任务上下文

**问题根源:** 4 sub-agent 分别因未读现有规则直接写 rules 触发循环故障，包括 `nl_to_contract.py` invariant 默认 fail-closed、`forget_guard_rules.yaml` 无 schema validation、缺 self-heal whitelist、boot 后未 e2e self-test。

**为何现有 enforcement 无效:** Y*gov 现有 193 条约束，11 个类别，**0 条**强制 agent 在写规则前必须先读取现有规则全文。PreToolUse hook 只 inject session context 摘要，不注入相关规则全文。Subagent spawn 不强制 cat role definition。

---

## §1 Current State Audit (现有 enforcement 机制盘点)

### 1.1 Hook Layer (7-layer)
| Layer | Enforcement Point | Read Enforcement |
|-------|------------------|------------------|
| L1 | Secret leakage detection | ❌ No rule read |
| L2 | Scope boundary (directory whitelist) | ❌ No rule read |
| L3 | Tense check (future tense deny) | ❌ No rule read |
| L4 | Task ownership (agent_id match) | ❌ No rule read |
| L5 | Sensitive file write (`.env`, credentials) | ❌ No rule read |
| L6 | Forget Guard (`forget_guard_rules.yaml`) | ❌ No rule read |
| L7 | Behavioral pattern (no choice questions) | ❌ No rule read |

**结论:** 所有 hook layer 均为**事后拦截** (deny after violation detected)，无**事前注入** (inject before action)。

### 1.2 Session Boot (`governance_boot.sh`)
- ✅ Restores `.ystar_session.json` (193 constraints)
- ✅ Injects agent_id to working memory
- ✅ Runs CIEU database connection test
- ❌ **Does NOT** force agent to read role definition (`knowledge/{role}/role_definition/*.md`)
- ❌ **Does NOT** force agent to read current governance rules (`governance/*.yaml`)

### 1.3 Subagent Spawn (Agent tool)
- ✅ Delegates task via MCP `gov_delegate`
- ❌ **Does NOT** inject subagent's role definition into spawn prompt
- ❌ **Does NOT** require subagent to cat `knowledge/{role}/` on first action

### 1.4 PreToolUse Hook (`hook_client_labs.sh`)
- ✅ Injects session context summary (120 chars)
- ❌ **Does NOT** inject relevant governance rules for high-risk writes
- ❌ **Does NOT** detect "agent hasn't read rules in last N turns"

---

## §2 Proposed Solution: CROBA (Compliance Read-Before-Action)

### 2.1 Active Read (Subagent Spawn)
**When:** Agent tool spawns subagent  
**Action:** Inject forced preamble to subagent prompt:

```markdown
Before ANY action, run:
cat /Users/haotianliu/.openclaw/workspace/ystar-company/knowledge/{role}/role_definition/*.md
cat /Users/haotianliu/.openclaw/workspace/ystar-company/governance/*.yaml

Output: "CROBA confirmed: read {N} role files, {M} governance rules"
```

**Implementation:** Modify `.claude/agents/{role}.md` to include boot ritual preamble.

**Owner:** Platform Engineer (Ryan Park)  
**Acceptance:** Subagent first message MUST contain "CROBA confirmed" or spawn fails.

---

### 2.2 Passive Read Injection (PreToolUse Hook)
**When:** PreToolUse hook detects high-risk write  
**Action:** Inject relevant governance rules full text into LLM context

**High-risk write triggers:**
- Write to `governance/*.yaml`
- Write to `.claude/agents/*.md`
- Write to `scripts/governance_boot.sh`
- Write to `scripts/hook_client_labs.sh`
- Edit to `ystar/kernel/nl_to_contract.py`

**Implementation:**
1. Hook detects file path matches high-risk pattern
2. Grep `governance/*.yaml` for rules mentioning that file
3. Inject matched rules **full text** (not summary) into hook response payload:
   ```json
   {
     "action": "allow",
     "message": "High-risk write detected. Relevant rules injected.",
     "injected_context": "<full rule text here>"
   }
   ```
4. Harness appends `injected_context` to next assistant turn context

**Owner:** Platform Engineer (Ryan Park)  
**Acceptance:** Write to `forget_guard_rules.yaml` without reading it first → hook injects schema, agent must validate before write.

---

### 2.3 Verification Gate (Last-N-Turns Read Check)
**When:** PreToolUse hook on high-risk write  
**Action:** Check last 5 assistant turns for evidence of Read tool call on relevant governance files

**Logic:**
```python
recent_turns = context.last_n_turns(5)
required_files = get_relevant_governance_files(action.target_file)
read_files = extract_read_tool_calls(recent_turns)

if not all(f in read_files for f in required_files):
    return {
        "action": "deny",
        "message": "CROBA violation: must Read governance files before write",
        "recipe": f"Run: Read {', '.join(required_files)}"
    }
```

**Owner:** Governance Engineer (Maya Patel)  
**Acceptance:** Write to `nl_to_contract.py` without prior Read → deny + recipe shows exact Read command.

---

### 2.4 Dry-Run Enforcement (New Rule Grace Period)
**When:** New governance rule added to `forget_guard_rules.yaml`  
**Action:** Enforce `dry_run_until` field (ISO timestamp) — rule only emits warnings for 24h, then hardens to deny

**Schema change:**
```yaml
rules:
  - pattern: "rm -rf governance/"
    action: deny
    message: "Cannot delete governance directory"
    dry_run_until: "2026-04-14T12:00:00Z"  # REQUIRED for new rules
```

**Implementation:** Modify `governance/forget_guard.py` to:
1. Validate `dry_run_until` exists on all rules
2. Compare current time vs `dry_run_until`
3. If within dry-run window: `action=warn`, else `action=deny`

**Owner:** Governance Engineer (Maya Patel)  
**Acceptance:** New rule without `dry_run_until` → governance_boot.sh STEP 8 fails with schema error.

---

## §3 Acceptance Criteria

| Test Case | Expected Outcome | Verification Method |
|-----------|------------------|---------------------|
| A025-T1: Maya spawned, writes `forget_guard_rules.yaml` without Read | Deny + recipe shows "Read governance/forget_guard_rules.yaml" | Manual spawn + attempt write |
| A025-T2: Leo modifies `nl_to_contract.py` after reading file | Allow (read detected in last 5 turns) | Manual spawn + Read + Edit |
| A025-T3: New rule lacks `dry_run_until` | `governance_boot.sh` STEP 8.5 fails | Add rule, rerun boot |
| A025-T4: `pkill -9 -f hook_daemon` | Always allow (self-heal whitelist bypass) | Manual pkill attempt |
| A025-T5: Subagent spawn | First message contains "CROBA confirmed: read N files" | Spawn any subagent |

---

## §4 RAPID Assignment (真分派)

### R (Responsible)
- **P1:** Kernel Engineer (Leo Chen) — `nl_to_contract.py` invariant default flip
- **P2:** Platform Engineer (Ryan Park) — `hook_client_labs.sh` self-heal whitelist
- **P3:** Governance Engineer (Maya Patel) — `forget_guard_rules.yaml` schema + dry-run logic
- **P4:** Platform Engineer (Ryan Park) — `governance_boot.sh` STEP 8.5 self-test

### A (Accountable)
- **CTO (Ethan Wright)** — e2e test, commit, report

### P (Participants)
- CEO (Aiden) — monitors for stuck subagents, applies self-heal if CTO active_agent drifts

### I (Informed)
- Board (Haotian Liu) — receives commit hash + one-line confirmation

### D (Decider)
- Board (Haotian Liu) — approves AMENDMENT-025 charter before implementation begins

---

## §5 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **R1:** Passive injection bloats context (5k+ tokens per high-risk write) | LLM context overflow, slower inference | Inject max 2 rules per trigger, prioritize by edit distance |
| **R2:** Active read preamble ignored by subagent | CROBA bypassed | Hook verifies "CROBA confirmed" string in subagent first turn, deny spawn if missing |
| **R3:** `dry_run_until` timezone ambiguity | Rule hardens early/late | Enforce UTC ISO8601 format, boot validation rejects non-UTC |
| **R4:** Self-heal whitelist too broad | Hook bypass creates security hole | Whitelist exact command patterns (not wildcards), audit quarterly |
| **R5:** CTO active_agent drift after subagent spawn | CEO loses write permissions | CTO self-heals via daemon window before exiting (per memory `feedback_self_heal_via_daemon_window.md`) |

---

## §6 Relationship to Prior Amendments

### A012 (Secretary Event-Driven Work Allocation)
- **Connection:** Secretary curates `.claude/tasks/`, subagents read tasks. CROBA ensures subagent reads role def before claiming task.
- **Conflict:** None. CROBA is prerequisite, A012 is work distribution.

### A013 (Emergency Article 11 Sub-Agent Autonomy)
- **Connection:** Article 11 spawns N subagents in parallel. Each must CROBA on spawn.
- **Conflict:** None. CROBA adds 2-3s overhead per spawn, negligible for emergency.

### A018 (Hook Daemon Health Self-Heal)
- **Connection:** Self-heal commands (pkill hook_daemon, rm socket) must bypass hook.
- **Integration:** **P2 implements self-heal whitelist in hook_client_labs.sh.**

### A020 (Working Memory Snapshot)
- **Connection:** Session handoff includes "what rules were read this session".
- **Integration:** CROBA verification gate writes to `.ystar_session.json` field `rules_read_this_session: [...]`.

### A023 (Conversation Replay Engine)
- **Connection:** Replay must preserve CROBA context injection payloads.
- **Integration:** Replay engine includes hook `injected_context` in reconstructed turns.

---

## §7 Implementation Timeline

| Phase | Duration | Tasks | Gate |
|-------|----------|-------|------|
| **Phase 1:** Charter Draft | 30 min | This doc | Board approval |
| **Phase 2:** Parallel Impl | 90 min | P1 (Leo), P2+P4 (Ryan), P3 (Maya) | All tasks green |
| **Phase 3:** E2E Test | 15 min | CTO runs A025-T1 to A025-T5 | All PASS |
| **Phase 4:** Commit | 5 min | CTO commits to Y-star-gov main | Hash to Board |
| **Phase 5:** Boot Verification | 10 min | Rerun governance_boot.sh, confirm STEP 8.5 | ALL SYSTEMS GO |

**Total:** 150 min (2.5h)  
**Board review window:** 30 min (async, Board can abort during Phase 2)

---

## §8 Success Metrics (30-day post-deployment)

| Metric | Target | Data Source |
|--------|--------|-------------|
| CROBA deny rate | <5% (most agents comply on first attempt) | Hook audit log |
| Subagent spawn failures (missing "CROBA confirmed") | 0 | MCP `gov_delegate` error log |
| Governance rule conflicts detected by passive injection | ≥3 (proves injection works) | CIEU `category=CROBA_INJECT` |
| Self-heal whitelist false denies | 0 | Hook audit log + incident reports |
| New rules deployed without `dry_run_until` | 0 (boot validation catches all) | `governance_boot.sh` exit code log |

---

**Approval Required:** Board (Haotian Liu)  
**ETA to Ship:** 2.5h from approval timestamp  
**Rollback Plan:** Revert 4 commits (P1-P4), restore pre-A025 governance_boot.sh, restart session

---

**CTO Signature:** Ethan Wright, 2026-04-13  
**Status:** AWAITING_BOARD_APPROVAL
