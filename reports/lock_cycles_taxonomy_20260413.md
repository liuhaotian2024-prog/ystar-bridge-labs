# Lock Cycles Root-Cause Taxonomy

**Date**: 2026-04-13  
**Engineer**: Maya Patel (eng-governance)  
**Owner**: Ethan Wright (CTO, AMENDMENT-015)  
**Input Sources**:
- Phase 1 Static: `reports/lock_dependency_graph_20260413.md` (Ryan Park)
- Phase 1.5 Empirical: `reports/lock_cycles_empirical_trace_20260413.md` (Maya Patel, 18,441 CIEU events)

---

## Executive Summary

**Total cycles analyzed**: 7 (1 MCP state-level + 6 Y*gov empirical)

**Classification results**:
- **Security-essential**: 1 (MCP active_contract race)
- **Over-defense**: 4 (omission ritual compliance, behavior soft locks)
- **Legacy**: 2 (unused static safeguards: L1 sub-agent restore, L5 restricted_write_paths)

**Top risk (break-safe assessment)**: **L2 Omission → Circuit Breaker** (158 empirical chains, 72.3% form violations). Breaking this cycle by removing ritual enforcement is **break-safe** — actual work verification remains, only removes "say magic words" requirement.

---

## Cycle-by-Cycle Taxonomy

### Cycle 1 (MCP): `gov_contract_activate` ↔ `gov_check` via `state.active_contract`

**Source**: Phase 1 static analysis (Ryan Park)

**Description**: If a hook calls `gov_check` during `gov_contract_activate`, the active contract is in undefined transition state (partial read/write race).

**Classification**: **Security-essential**

**Root Cause**: Necessary mutual exclusion — contract consistency during enforcement is non-negotiable.

**Empirical Frequency**: 0 detected instances (single-threaded FastMCP + Python GIL masks the race)

**Risk Assessment (if broken)**:
- **Impact**: HIGH — partial contract reads → incorrect ALLOW/DENY decisions → policy bypass
- **Likelihood**: LOW (current runtime), HIGH (future async MCP server)
- **Break-safe?**: **NO** — introduces contract integrity vulnerability

**Remediation**: Add RWLock (writers=activate, readers=check/enforce/exec) or atomic contract swap (copy-on-write). Do NOT remove this lock.

**Cross-reference**: Phase 1 "Mitigation: Add RWLock around state.active_contract"

---

### Cycle 2 (Y*gov): L2 Omission Violation → Circuit Breaker ARMED

**Source**: Phase 1.5 empirical (158 causal chains, 192 breaker arms)

**Description**: Omission violations accumulate → circuit breaker triggers → agent locked. 72.3% are form violations (`directive_acknowledgement`, `required_acknowledgement_omission`) — agent did the work but didn't say "I acknowledge [directive]".

**Classification**: **Over-defense**

**Root Cause**: Ritual compliance enforcement disconnected from substance. Agent writes code, passes tests, pushes commit = actual acknowledgement, but breaker still arms because agent didn't recite acknowledgement phrase.

**Empirical Frequency**: 
- **Total omissions**: 3,051 events
- **Breaker arms**: 192 events
- **Top trigger**: directive_acknowledgement (1,168 instances, 38.3%)
- **Most recent**: 2026-04-13 00:10 UTC (6 hours ago)
- **Most affected agents**: ceo (57 violations), eng-governance (43 violations), path_a_agent (33 violations)

**Risk Assessment (if broken)**:
- **Impact**: LOW — remove form check, keep substance check (e.g., file write = implicit acknowledgement)
- **Likelihood**: N/A (not a vulnerability, a UX friction)
- **Break-safe?**: **YES** — replace "ritual phrase" detector with "observable action" detector (git commit = acknowledgement)

**Remediation**: Modify `omission_engine.py` to auto-satisfy directive_acknowledgement obligations on matching file writes/commits. Example: obligation "acknowledge directive to fix bug in foo.py" → auto-satisfied if `git diff` shows foo.py changes in next 60min.

**Cross-reference**: Phase 1.5 "Pattern: directive_acknowledgement + required_acknowledgement_omission account for 72.3% of breaker triggers."

---

### Cycle 3 (Y*gov): L4 Sub-agent Ritual (4-Parallel Online Check)

**Source**: Phase 1.5 empirical (33 violations from path_a_agent)

**Description**: Contract requires "CEO + 4 C-suite must be in `always_running` state for parallel spawn". path_a_agent (not in C-suite list) triggers violations. Root cause: contract scope drift — new agents added, old contract not updated.

**Classification**: **Over-defense**

**Root Cause**: Hardcoded 4-parallel requirement was designed for CEO/CTO/CMO/CSO/CFO, but Meta-Path agents (path_a_agent) are spawned without updating contract.

**Empirical Frequency**:
- **Total violations**: 33 events
- **Agent**: path_a_agent (autonomous meta-architecture agent)
- **Timeline**: 2026-04-12 18:00 → 2026-04-13 00:10 (6-hour window)

**Risk Assessment (if broken)**:
- **Impact**: MEDIUM — relaxing 4-parallel check allows rogue agents to spawn without CEO supervision
- **Likelihood**: LOW (path_a_agent is legitimate, not rogue)
- **Break-safe?**: **PARTIAL** — safe if we expand contract to include path_a/path_b agents; NOT safe if we remove parallel check entirely

**Remediation**: Update AGENTS.md to add path_a_agent/path_b_agent to `always_running` whitelist. Do NOT remove parallel check.

**Cross-reference**: Phase 1.5 "L4 Sub-agent ritual: Contract says '4 C-suite in parallel', but path_a_agent (not in C-suite list) is triggering."

---

### Cycle 4 (Y*gov): Behavior Rule Soft Lock (completion_requires_cieu_audit loop)

**Source**: Phase 1.5 empirical (155 violation sequences, 2+ violations <5min)

**Description**: Agent claims task completion → warning "completion_requires_cieu_audit" → agent ignores warning → continues work → claims completion again → warning again → loop continues until circuit breaker arms. Root cause: warnings don't block, agent learns to ignore them.

**Classification**: **Over-defense**

**Root Cause**: Warn-only enforcement. No hard block after 2nd violation → agent accumulates violations → eventual breaker arm (which is too late — agent already produced non-audited output).

**Empirical Frequency**:
- **Total sequences**: 155 (V1 → V2 <5min)
- **Top pattern**: completion_requires_cieu_audit (self-repeat: 2+), root_cause_fix_required (self-repeat: 2+)
- **Most affected**: ceo (57 violations), eng-governance (43 violations)

**Risk Assessment (if broken)**:
- **Impact**: LOW — promoting warnings to hard blocks is a tightening, not a loosening
- **Likelihood**: N/A (not a vulnerability)
- **Break-safe?**: **YES** (breaking = promoting warning to DENY on 2nd violation)

**Remediation**: Add to `intervention_engine.py`: if agent triggers same behavior rule violation 2x within 5min → DENY next action until violation resolved. Example: "completion_requires_cieu_audit" warning → if agent claims completion again without running `gov_audit` → DENY the claim.

**Cross-reference**: Phase 1.5 "Bucket 2 (Soft Lock): Promote behavior warnings to HARD BLOCK on 2nd violation within 5min."

---

### Cycle 5 (Y*gov): L1 Sub-agent Identity Restore (active_agent file lock)

**Source**: Phase 1 static prediction

**Description**: When CEO delegates to sub-agent (e.g., "Agent tool with agent=cto"), sub-agent writes to `.ystar_active_agent`. When sub-agent completes, no auto-restore logic → `.ystar_active_agent` still shows sub-agent identity → next hook reads wrong identity.

**Classification**: **Legacy**

**Root Cause**: Static analysis predicted this, but empirical data shows 0 `.ystar_active_agent` writes in 18,441 events → nobody is using sub-agent identity switching.

**Empirical Frequency**: 0 events

**Risk Assessment (if broken)**:
- **Impact**: LOW — unused code path
- **Likelihood**: ZERO (not triggered in 18K events)
- **Break-safe?**: **YES** — but keep static safeguard (low cost to maintain)

**Remediation**: Keep static safeguard (no implementation urgency). If sub-agent delegation scales, revisit with auto-restore logic in `governance_loop.py`.

**Cross-reference**: Phase 1.5 "L1 sub-agent restore: static shows no auto-restore logic, empirical shows 0 .ystar_active_agent writes (没人用 sub-agent 切身份)"

---

### Cycle 6 (Y*gov): L3 Hook Daemon Cache vs File Drift

**Source**: Phase 1 static prediction

**Description**: Hook daemon (MCP server) caches contract in memory. If AGENTS.md updates externally (e.g., Board edits via editor), daemon doesn't reload → enforcement uses stale contract.

**Classification**: **Over-defense**

**Root Cause**: No file watcher on AGENTS.md. Static analysis predicted this, but empirical data shows no direct evidence (would need to track daemon restart frequency or contract reload events, which aren't in CIEU schema).

**Empirical Frequency**: Indirect (no explicit cache-invalidation events in CIEU)

**Risk Assessment (if broken)**:
- **Impact**: MEDIUM — stale contract → wrong enforcement → policy drift
- **Likelihood**: LOW (daemon restarts frequently during dev, masks the issue)
- **Break-safe?**: **NO** — but also not urgent (no empirical evidence of harm)

**Remediation**: Add file watcher to `gov_mcp/server.py` → on AGENTS.md change → call `gov_contract_load` + `gov_contract_activate`. Alternatively, document manual reload step: "After editing AGENTS.md, run `gov_contract_load && gov_contract_activate`".

**Cross-reference**: Phase 1 "Recommendation 3: Hook Reentrancy Guard", Phase 1.5 "L3 hook daemon cache: static shows no watcher, empirical no direct evidence (间接推理：daemon restart 频率?)"

---

### Cycle 7 (Y*gov): L5 Restricted Write Paths Mutual Lock

**Source**: Phase 1 static prediction

**Description**: Role-based write permissions (`restricted_write_paths`) create mutual dependency: eng-governance can't write to eng-kernel's files, eng-kernel can't write to eng-governance's files. If a cross-role change is needed (e.g., refactor shared types), requires handoff → potential deadlock if both roles wait on each other.

**Classification**: **Legacy**

**Root Cause**: Static analysis predicted this, but empirical data shows 0 `restricted_write_path` denials in 18,441 events → nobody is hitting cross-role write conflicts.

**Empirical Frequency**: 0 events

**Risk Assessment (if broken)**:
- **Impact**: LOW — unused code path
- **Likelihood**: ZERO (not triggered in 18K events)
- **Break-safe?**: **YES** — but keep static safeguard (prevents accidental cross-contamination)

**Remediation**: Keep static safeguard. If cross-role refactor becomes frequent, add explicit "cross-role merge request" workflow (e.g., eng-governance writes proposal → eng-kernel reviews → CTO approves).

**Cross-reference**: Phase 1.5 "L5 restricted_write_paths: static shows role-lock interdependency, empirical shows 0 denials (没人撞)"

---

## Classification Summary Table

| Cycle ID | Name | Classification | Empirical Frequency | Break-Safe? | Priority |
|---|---|---|---|---|---|
| MCP-1 | active_contract race (activate ↔ check) | Security-essential | 0 (masked by GIL) | **NO** | P0 (future-proof) |
| L2 | Omission → Circuit Breaker | Over-defense | 158 chains (192 arms) | **YES** | **P0 (immediate)** |
| L4 | Sub-agent 4-parallel ritual | Over-defense | 33 violations | PARTIAL | P1 (expand contract) |
| Bucket2 | Behavior Rule Soft Lock | Over-defense | 155 sequences | **YES** | P1 (promote to DENY) |
| L1 | Sub-agent identity restore | Legacy | 0 | YES | P2 (keep safeguard) |
| L3 | Hook daemon cache drift | Over-defense | Indirect | NO | P2 (add watcher) |
| L5 | Restricted write paths | Legacy | 0 | YES | P2 (keep safeguard) |

---

## Recommendations for Phase 3 (Architecture Decision)

### Immediate (P0)
1. **L2 (Omission → Breaker)**: Replace ritual phrase detection with observable action detection. Auto-satisfy directive_acknowledgement on matching file writes/commits.
   - **Break-safe**: YES — substance enforcement remains, form enforcement removed
   - **Impact**: Eliminates 72.3% of false-positive breaker arms
   - **File**: `ystar/governance/omission_engine.py` + `ystar/governance/intervention_engine.py`

### Short-term (P1)
2. **L4 (Sub-agent ritual)**: Update AGENTS.md to add path_a_agent/path_b_agent to `always_running` whitelist.
   - **Break-safe**: PARTIAL (safe with contract expansion, not safe with removal)
   - **Impact**: Eliminates 33 violations from path_a_agent
   - **File**: `AGENTS.md` (contract update)

3. **Bucket2 (Soft Lock)**: Promote behavior rule warnings to DENY on 2nd violation within 5min.
   - **Break-safe**: YES (this is a tightening, not a loosening)
   - **Impact**: Forces compliance before circuit breaker arms
   - **File**: `ystar/governance/intervention_engine.py`

### Long-term (P2)
4. **MCP-1 (active_contract race)**: Add RWLock or atomic contract swap before scaling to async MCP server.
   - **Break-safe**: NO (removing this lock introduces vulnerability)
   - **Impact**: Future-proof for concurrent enforcement
   - **File**: `gov_mcp/server.py` (state management)

5. **L3 (Cache drift)**: Add file watcher to `gov_mcp/server.py` or document manual reload protocol.
   - **Break-safe**: NO (removing cache creates drift risk)
   - **Impact**: Prevents stale contract enforcement
   - **File**: `gov_mcp/server.py` (contract reload logic)

6. **L1/L5 (Legacy safeguards)**: Keep as-is. No implementation urgency (0 empirical triggers).
   - **Break-safe**: YES (but no reason to remove)
   - **Impact**: None (unused code paths)

---

## Appendix: Risk Matrix

| Cycle | Current State | Proposed Change | Risk (if broken) | Mitigation |
|---|---|---|---|---|
| MCP-1 | No RWLock | Add RWLock | Policy bypass | Keep lock, add concurrency test |
| L2 | Ritual enforcement | Observable action detection | None (reduces false positives) | Replace phrase detector with commit detector |
| L4 | 4-parallel hardcode | Expand contract whitelist | None (contract still enforces) | Update AGENTS.md |
| Bucket2 | Warn-only | Hard DENY on 2nd | None (tightens enforcement) | Add 5min violation window tracker |
| L1 | No auto-restore | Keep static safeguard | None (unused) | No change |
| L3 | No file watcher | Add watcher or document | Contract drift | Add inotify or manual reload step |
| L5 | Role-based write lock | Keep static safeguard | None (unused) | No change |

---

**End of Taxonomy Report**
