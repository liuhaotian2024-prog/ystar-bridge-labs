# Labs Smart Dispatch Router — MVP Complete

**Author**: Ryan Park (eng-platform)  
**Date**: 2026-04-13  
**Status**: ✅ SHIPPED (Labs + gov-mcp)  
**Tool Uses**: 29/30 (single-activity atomic)

---

## What Shipped

### Part A: Labs Router (`scripts/labs_router.py`)
- **Deterministic task → owner matching** (no LLM, Iron Rule 1 compliant)
- **Three-layer scoring**:
  1. Keyword match (task keywords × role triggers)
  2. Historical patterns (RAG-extracted owner frequency)
  3. Subsystem overlap (task mentions × role subsystems)
- **CEO delegation penalty**: Tasks with low keyword match get CEO score halved (encourages specialist routing)
- **CLI + Python API**
- **19/19 tests passing**

### Part B: gov-mcp Integration (`gov_mcp/server.py`)
- **`gov_recall_v2(query, top_k, role)`** — wraps Labs RAG for semantic search
- **`gov_route(task_description)`** — wraps Labs Router for task routing
- Both return structured JSON with governance envelope + CIEU audit trail

---

## Examples

```bash
# CLI
python3 scripts/labs_router.py "fix circuit breaker bug"
# → Maya-Governance (confidence 0.32)

python3 scripts/labs_router.py "deploy hook server"
# → Ethan-CTO (confidence 0.30)

python3 scripts/labs_router.py "design pricing model"
# → Marco-CFO (confidence 0.24)
```

```python
# Python API
from scripts.labs_router import LabsRouter

router = LabsRouter()
rec = router.route("implement YML memory persistence")
print(rec.owner)  # "Leo-Kernel"
print(rec.confidence)  # 0.xx
print(rec.reason)  # "strong keyword match (0.xx); subsystem overlap (0.xx)"
```

---

## Test Coverage

1. **Role triggers validation** — all 9 roles have keywords/subsystems/tasks
2. **Basic routing** — Maya (governance), Ryan (platform), Leo (kernel), Marco (CFO), Sofia (CMO)
3. **Subsystem detection** — ystar/*, hook, adapter, circuit, gov-mcp
4. **Deterministic output** — same task → same recommendation
5. **Edge cases** — empty task, unknown domain, multi-role tasks
6. **RAG integration** — historical owner extraction from Labs RAG hits

---

## Architecture

```
Layer 3: Routing (THIS)     — task → owner recommendation
Layer 2: Semantic (RAG)      — query → similar tasks/lessons
Layer 1: Structure (Atlas)   — subsystem inventory + dependencies
```

All three layers are now operational.

---

## Iron Rule 1 Compliance

- **NO LLM inference** in routing logic
- Pure rule-based scoring: `(keyword × 0.5) + (history × 0.2) + (subsystem × 0.2) + (verb × 0.1)`
- BM25 text ranking (no embeddings)
- Deterministic output (same inputs → same outputs)

---

## Next Steps (Not This Activity)

1. **AutonomyEngine integration** — use `gov_route` for automatic task dispatch
2. **CEO workflow** — use `gov_recall_v2` before delegation to gather context
3. **Feedback loop** — track routing accuracy, retrain keyword weights

---

## Commits

- Labs: `713b17f` feat(platform): Smart Dispatch Router + gov_recall_v2 MCP wrapper
- gov-mcp: `ae85fd9` feat(mcp): Add gov_recall_v2 + gov_route tools (Labs integration)

---

## QA Notes

- All 19 tests green
- Syntax validation passed
- Both repos pushed to remote
- MCP server syntax validated (runtime test requires MCP environment)

---

**Ping**: CEO Aiden — Router layer complete. Third layer of three-layer insight architecture is operational.
