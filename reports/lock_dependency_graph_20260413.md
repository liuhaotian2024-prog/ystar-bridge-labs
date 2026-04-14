# MCP Permission Matrix & Lock Dependency Graph

**Generated**: 2026-04-13  
**Engineer**: Ryan Park (eng-platform)  
**Source**: `gov_mcp/server.py` (15 tools audited)  
**Scope**: AMENDMENT-015 Phase 1 — Systemic unlock design

---

## Executive Summary

- **Total tools**: 15 MCP tools in gov-mcp server
- **Permission locks identified**: 6 state locks (active_contract, delegation_chain, draft_contract, exec_whitelist, cieu_store, omission_engine)
- **Circular dependencies**: 0 direct cycles found (all tools are leaf operations, no gov_X→gov_Y→gov_X loops)
- **Dependency clustering**: Core enforcement (gov_check/gov_enforce) gates all other operations via `state.active_contract` + `delegation_chain`

**Key Finding**: No **tool-level** cycles exist, but **state-level deadlock risk** is present: `gov_contract_activate` mutates `state.active_contract` while `gov_check` reads it. If a hook calls `gov_check` during `gov_contract_activate`, the contract is in undefined transition state.

---

## Tool × Lock Permission Matrix

| Tool | active_contract | delegation_chain | draft_contract | exec_whitelist | cieu_store | omission_engine | Calls Other Tools |
|------|----------------|------------------|---------------|---------------|------------|----------------|------------------|
| `gov_check` | READ | - | - | - | - | - | none |
| `gov_enforce` | READ | READ | - | - | - | READ | none |
| `gov_delegate` | - | WRITE | - | - | - | - | none |
| `gov_escalate` | READ | READ+WRITE | - | - | WRITE | - | none |
| `gov_chain_reset` | - | WRITE | - | - | WRITE | - | none |
| `gov_contract_load` | - | - | WRITE | - | - | - | none |
| `gov_contract_validate` | - | - | READ | - | - | - | none |
| `gov_contract_activate` | WRITE | - | READ+CLEAR | - | - | - | none |
| `gov_exec` | READ | - | - | READ | - | - | none |
| `gov_report` | - | - | - | - | WRITE | - | none |
| `gov_verify` | - | - | - | - | READ | - | none |
| `gov_obligations` | - | - | - | - | - | READ | none |
| `gov_doctor` | READ | READ | - | READ | READ | READ | none |
| `gov_radar` | - | - | - | - | - | - | none |
| `gov_benchmark` | - | - | - | - | - | - | none |

**Legend**:  
- `READ` = Reads lock state, blocks if lock unavailable  
- `WRITE` = Mutates lock state, requires exclusive access  
- `READ+WRITE` = Both reads current state and mutates it (e.g., escalation expands delegation_chain)  
- `READ+CLEAR` = Special case: reads draft, clears it, writes to active (transaction-like)

---

## State Lock Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                   state.active_contract                      │
│  (global enforcement gate, read by gov_check/enforce/exec)   │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_check (READ) ────────────────────────────────┐
        │                                                     │
        ├─► gov_enforce (READ) ──┬─► delegation_chain (READ) │
        │                        └─► omission_engine (READ)  │
        │                                                     │
        ├─► gov_exec (READ + exec_whitelist READ)            │
        │                                                     │
        └─► gov_contract_activate (WRITE) ◄─── draft_contract (READ+CLEAR)
                    │
                    └─► **RISK**: If gov_check runs during activate,
                                   contract is in undefined state

┌─────────────────────────────────────────────────────────────┐
│                   state.delegation_chain                     │
│  (delegation authority tree, mutated by delegate/escalate)  │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_delegate (WRITE) ──► Appends new DelegationContract
        │
        ├─► gov_escalate (READ+WRITE) ──► Expands existing delegation
        │
        ├─► gov_chain_reset (WRITE) ──► Clears all links (destructive)
        │
        └─► gov_enforce (READ) ──► Validates chain integrity

┌─────────────────────────────────────────────────────────────┐
│                   state.draft_contract                       │
│  (staging buffer for contract load → validate → activate)   │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_contract_load (WRITE) ──► Populates draft from AGENTS.md
        │
        ├─► gov_contract_validate (READ) ──► Checks draft validity
        │
        └─► gov_contract_activate (READ+CLEAR) ──► Promotes to active, clears draft

┌─────────────────────────────────────────────────────────────┐
│                   state.exec_whitelist                       │
│  (auto-routing gate for deterministic commands)             │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_check (READ via _is_deterministic) ──► Auto-routes safe commands
        │
        └─► gov_exec (READ) ──► Validates command before execution

┌─────────────────────────────────────────────────────────────┐
│                   state._cieu_store                          │
│  (audit log, immutable append-only CIEU events)             │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_report (WRITE) ──► Appends new CIEU event
        │
        ├─► gov_verify (READ) ──► Validates session seal integrity
        │
        ├─► gov_escalate (WRITE) ──► Records escalation decision
        │
        └─► gov_chain_reset (WRITE) ──► Records reset event

┌─────────────────────────────────────────────────────────────┐
│                   state.omission_engine                      │
│  (obligation tracker, scans for overdue obligations)        │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├─► gov_enforce (READ via scan()) ──► Returns obligation warnings
        │
        └─► gov_obligations (READ) ──► Lists pending obligations
```

---

## Circular Dependency Analysis

### Direct Cycles (Tool → Tool)
**Count**: 0

**Rationale**: All 15 tools are **leaf operations**. No tool calls another `gov_*` tool. The `"Calls Other Tools"` column is empty across all rows.

### Indirect Cycles (State Lock Contention)
**Count**: 1 critical race condition identified

#### Cycle 1: `gov_contract_activate` ↔ `gov_check` via `state.active_contract`

**Scenario**:
1. Agent A calls `gov_contract_activate()` → begins writing to `state.active_contract`
2. Before activate completes, a hook triggers `gov_check()` on Agent B's action
3. `gov_check()` reads `state.active_contract` while it's being mutated
4. Result: **undefined behavior** — check may see partial contract, stale contract, or race to completion

**Impact**: Low in single-threaded FastMCP server (Python GIL), but **high if MCP server scales to async concurrent handlers** (planned in AMENDMENT-015 Phase 2).

**Mitigation**: Add `RWLock` around `state.active_contract` or atomic contract swap (copy-on-write).

---

## State Lock Contention Hotspots

| Lock | Writers | Readers | Concurrent Access Pattern |
|------|---------|---------|--------------------------|
| `active_contract` | 1 (gov_contract_activate) | 3 (gov_check, gov_enforce, gov_exec) | **HIGH CONTENTION**: Every agent action hits this lock |
| `delegation_chain` | 3 (gov_delegate, gov_escalate, gov_chain_reset) | 2 (gov_enforce, gov_doctor) | Medium contention during delegation tree mutations |
| `draft_contract` | 1 (gov_contract_load) | 2 (gov_contract_validate, gov_contract_activate) | Low contention (only during AGENTS.md reload) |
| `exec_whitelist` | 0 (read-only after init) | 2 (gov_check, gov_exec) | No contention (immutable) |
| `cieu_store` | 3 (gov_report, gov_escalate, gov_chain_reset) | 2 (gov_verify, gov_doctor) | Low contention (append-only log) |
| `omission_engine` | 0 (store mutated externally) | 2 (gov_enforce, gov_obligations) | Low contention (read-heavy) |

---

## Recommendations for Phase 2 (Systemic Unlock)

1. **Add RWLock to `state.active_contract`**:  
   - Writers: `gov_contract_activate` (exclusive lock)
   - Readers: `gov_check`, `gov_enforce`, `gov_exec` (shared lock)
   - Prevents partial contract reads during activation

2. **Atomic Contract Swap**:  
   - Replace `state.active_contract = draft` with `state.contracts.swap_active(draft_hash)`
   - Store contracts in versioned dict: `{hash: IntentContract}`
   - Readers always see a stable snapshot

3. **Delegation Chain Immutability**:  
   - Make `delegation_chain.links` immutable (copy-on-write)
   - Writers produce new chain snapshots
   - Eliminates `gov_chain_reset` destructive mutation

4. **CIEU Store Concurrency**:  
   - Current design (append-only) is safe
   - Add batch write API for gov_report if throughput becomes bottleneck

5. **Hook Reentrancy Guard**:  
   - If a hook calls `gov_check`, set `reentrancy_depth` flag
   - Block nested `gov_contract_activate` during hook execution
   - Prevents "activate-during-check" race

---

## Appendix: Tool Descriptions

| Tool | Purpose | Permission Model |
|------|---------|-----------------|
| `gov_check` | Pre-action governance gate (ALLOW/DENY decision) | Reads active contract, no mutations |
| `gov_enforce` | Full enforcement pipeline (check + obligations + delegation) | Reads active contract + chain + omissions |
| `gov_delegate` | Register parent→child delegation link | Writes to delegation_chain |
| `gov_escalate` | Request permission expansion from principal | Reads principal contract, writes expanded delegation |
| `gov_chain_reset` | Clear delegation chain (destructive reset) | Writes to delegation_chain, logs to CIEU |
| `gov_contract_load` | Parse AGENTS.md into draft contract | Writes to draft_contract buffer |
| `gov_contract_validate` | Validate draft contract syntax/semantics | Reads draft_contract |
| `gov_contract_activate` | Promote draft → active enforcement | Reads draft, writes active, clears draft |
| `gov_exec` | Execute deterministic command with contract check | Reads active contract + whitelist, executes subprocess |
| `gov_report` | Record CIEU audit event | Appends to cieu_store |
| `gov_verify` | Verify CIEU session seal integrity | Reads cieu_store, validates Merkle root |
| `gov_obligations` | Query pending obligations | Reads omission_engine store |
| `gov_doctor` | Health check (all subsystems) | Reads all locks (diagnostic only) |
| `gov_radar` | Tech scouting recommendations | No governance locks (external API call) |
| `gov_benchmark` | A/B token savings benchmark | No governance locks (runs synthetic workload) |

---

**End of Report**
