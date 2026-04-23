# Gov-MCP vs Y*gov Dual Path Audit

**Date**: 2026-04-23  
**Author**: eng-kernel (Kernel Engineer)  
**Trigger**: Board direct call -- suspected dual governance engine fragmentation

---

## Q1: Directory Layout Survey

Three locations contain gov_mcp code:

| Location | Files | server.py lines | Last modified |
|---|---|---|---|
| `ystar-company/gov_mcp/` | 8 .py/yaml | 42,997 bytes (~1,050 lines) | Apr 13-15 |
| `/workspace/gov-mcp/gov_mcp/` (standalone repo) | 10 .py/yaml | 174,335 bytes (4,404 lines) | Apr 16 |
| `/workspace/Y-star-gov/` | 0 (only test + docs ref) | N/A | N/A |

The standalone `gov-mcp` repo is the active development target (4,404-line server.py vs 1,050-line copy in ystar-company). The ystar-company copy is a stale snapshot from Apr 13.

## Q2: CIEU Emission Path Trace

**MCP-namespaced event_types in last 7 days**: ZERO rows returned.

```sql
SELECT event_type, COUNT(*) FROM cieu_events
WHERE created_at > strftime('%s','now','-7 day')
AND (event_type LIKE 'MCP%' OR event_type LIKE '%mcp%')
-- Result: (empty)
```

**File paths containing "mcp"**: 10 distinct paths, 72 total events. All point to the standalone `gov-mcp` repo:

```
/workspace/gov-mcp/gov_mcp/plugin_tools.py    | 16
/workspace/gov-mcp/tests/test_plugin_tools.py  | 39
/workspace/gov-mcp/gov_mcp/server.py           |  7
/workspace/gov-mcp/manifest.json               |  2
/workspace/Y-star-gov/reports/.../ruling.md     |  2
/workspace/ystar-company/.mcp.json             |  2
```

Gov-mcp emits CIEU events, but they are tagged with standard event_types (not MCP-prefixed), meaning they flow through the same Y*gov engine and are indistinguishable from direct ystar calls at the event level.

## Q3: Duplicate Decision Trace

Top event_types (last 7 days, count > 10):

```
K9_ROUTING_DISPATCHED       | system:k9_subscriber | 119,436
circuit_breaker_armed        | intervention_engine  |  22,868
orchestration:governance_loop| orchestrator         |  22,868
HOOK_PRE_CALL               | governance           |   6,662
HOOK_POST_CALL              | governance           |   5,555
```

No event_type appears under two different agent_ids in a pattern suggesting dual-emission. The `HOOK_PRE_CALL`/`HOOK_POST_CALL` events come exclusively from the `governance` agent_id (Y*gov hook path). Gov-mcp events (the 72 file_path-tagged ones) use the standard `agent` agent_id. There is no evidence of the same governance decision being emitted twice through two paths.

## Q4: Code-Level Route Inspection

**ystar-company/gov_mcp/server.py line 19**:
```python
from ystar import (
    CheckResult, DelegationChain, DelegationContract,
    InMemoryOmissionStore, IntentContract, OmissionEngine,
    check, enforce,
)
from ystar.kernel.nl_to_contract import translate_to_contract, validate_contract_draft
```

**gov-mcp repo server.py line 19** -- identical imports, plus:
```python
from ystar.memory import MemoryStore, Memory
from ystar.governance.cieu_store import CIEUStore
from ystar.governance.governance_loop import GovernanceLoop
from ystar.governance.omission_models import ObligationStatus
```

Both copies import FROM `ystar` -- neither reimplements the engine. Gov-mcp instantiates `IntentContract`, `DelegationChain`, `OmissionEngine`, `check()`, `enforce()` directly from the ystar package. It adds MCP tool wrappers (`@mcp.tool()`) around these calls. No governance logic is re-derived.

The standalone repo has additional modules (`dispatch_logic.py`, `plugin_tools.py`, `amendment_009_010_tools.py`, `cli.py`) that also import from ystar (e.g., `from ystar.kernel.dimensions import DelegationChain`).

## Q5: Verdict

**(A) UNIFIED** -- gov_mcp is a thin MCP adapter that delegates 100% of governance decisions to the ystar engine. 1 system, 2 frontends. Healthy architecture.

Evidence:
1. Every governance call (`check`, `enforce`, `IntentContract`, `OmissionEngine`) is imported from ystar, not reimplemented.
2. CIEU events from gov-mcp flow through the same ystar CIEU store -- no parallel emission path.
3. Zero MCP-prefixed event_types exist, confirming gov-mcp does not maintain its own event taxonomy.

## Q6: Recommendation

**No merge needed.** The architecture is sound: ystar is the engine, gov-mcp is the MCP transport adapter.

One hygiene action: the `ystar-company/gov_mcp/` directory is a stale copy (1,050 lines vs 4,404 in the standalone repo). It should either be deleted or replaced with a symlink/git-submodule reference to avoid future confusion about "which gov_mcp is canonical." This is a Platform Engineer task (file layout), not a kernel concern.

---

**5-Tuple Receipt**:
- **Y***: Evidence-based verdict on gov_mcp vs ystar dual-path question
- **Xt**: Audited 3 locations, 4 SQL queries, code-level import trace
- **U**: 6 queries executed, memo written
- **Yt+1**: Verdict (A) UNIFIED delivered with all evidence
- **Rt+1**: 0 -- path: `reports/kernel/gov_mcp_vs_ystar_dual_path_audit_20260423.md`, 89 lines, verdict: UNIFIED
