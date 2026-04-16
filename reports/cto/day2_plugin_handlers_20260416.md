# CTO Day 2 Report — Plugin Handlers Implementation

**Date**: 2026-04-16  
**Scope**: gov-mcp FastMCP plugin tool handlers (Day 2 of 30-day atomic dispatch)  
**Maturity**: L3 — Tested + committed, not built  
**Commit**: 22a4543

---

## Open Questions Answered (from Day 1)

### Q1: Does `gov_mcp.server` exist?
✅ **YES**. `/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py` exists (45k+ tokens), implements FastMCP server with `_State` class, loads Y*gov kernel.

### Q2: Reuse gov-mcp Python package or new structure?
✅ **REUSE**. `pyproject.toml` already declares `gov-mcp` package with `ystar>=0.48.0` dependency. server.py is production-ready. No new structure needed.

### Q3: Call Y*gov kernel or write wrappers?
✅ **MIX**. Y*gov CLI functions (`_cmd_doctor`, `_cmd_check`) exist but are CLI-oriented (print + sys.exit). Wrote **thin wrappers** returning JSON for MCP protocol. Followed existing pattern: `register_amendment_tools(mcp, state)` → added `register_plugin_tools(mcp, state)`.

---

## Architecture Decision: **Option A** — Extend `gov_mcp/server.py`

**Rationale**:
- server.py already boots FastMCP + manages state
- Amendment 009/010 tools use `register_amendment_tools(mcp, state)` pattern
- Plugin tools follow same pattern: `register_plugin_tools(mcp, state)`
- Avoids fragmentation (no separate plugin_server.py needed)

---

## Discovery: Plugin.json Tools Already in server.py

Initial plan: implement 8 tools from plugin.json (2 full, 6 stub).

**Reality check**: grepped server.py, found **4/8 already implemented**:
- `gov_check` (line 873) ✅
- `gov_delegate` (line 1034) ✅
- `gov_doctor` (line 2057) ✅
- `gov_escalate` (line 1107) ✅

**Actual gap**: 4 tools unique to plugin.json, NOT in server.py:
1. `gov_query_cieu` — query CIEU audit log
2. `gov_install` — install governance for new project
3. `gov_omission_scan` — detect missing governance checks
4. `gov_path_verify` — verify file path against allowed scopes

---

## Implementation Summary

### Fully Implemented (Day 2)

#### 1. `gov_query_cieu(event_type, agent_id, limit) → str`
- Queries `state._cieu_store.query(limit)`
- Filters by event_type (C/I/E/U) and/or agent_id
- Returns JSON array of CIEU events
- Handles missing CIEU store gracefully

#### 2. `gov_path_verify(file_path, agent_id) → str`
- Calls `ystar.check(agent_id, file_path)`
- Matches against `state.contract.only_paths`
- Returns JSON with `allowed`, `matched_scope`, `reason`, `violations`
- Path resolution via `pathlib.Path.is_relative_to()`

### Stubs (Day 3+)

#### 3. `gov_install(project_dir) → str`
Returns `{"status": "not_implemented", "message": "will wrap 'ystar setup' + 'ystar init'"}`.

#### 4. `gov_omission_scan(lookback_hours, min_confidence) → str`
Returns `{"status": "not_implemented", "message": "will use state.omission_engine.scan"}`.

---

## Integration

**File**: `gov_mcp/plugin_tools.py` (198 lines, new)  
**Registration** (in `server.py`):
```python
from gov_mcp.plugin_tools import register_plugin_tools

# Line 4400 (after register_amendment_tools):
register_plugin_tools(mcp, state)
```

---

## Test Results

**File**: `tests/test_plugin_tools.py` (80 lines, new)  
**Run**: `python3.11 -m pytest tests/test_plugin_tools.py -v`

```
tests/test_plugin_tools.py::test_gov_query_cieu_basic PASSED       [ 33%]
tests/test_plugin_tools.py::test_gov_path_verify_basic PASSED      [ 66%]
tests/test_plugin_tools.py::test_stub_tools_registered PASSED      [100%]

======================== 3 passed, 7 warnings in 0.43s ========================
```

**Warnings** (non-blocking):
- `pyproject.toml` has unknown `asyncio_mode` config (legacy)
- Test fixtures create .ystar_session.json without `schema_version` field (fixture upgrade needed in Day 3)

---

## MCPB Build Status

**Command**: `mcpb pack . gov-mcp.mcpb`  
**Result**: ❌ **FAILED**

**Error**:
```
Unrecognized or unsupported manifest version
```

**Root cause**: `plugin.json` uses `"schemaVersion": "v2"` (Claude Code marketplace spec), but `mcpb` CLI expects older manifest format (likely v1 or manifest.json name).

**Options for Day 3**:
1. Generate manifest.json in v1 format (dual manifest approach)
2. Convert plugin.json to mcpb-compatible format
3. Research if mcpb has v2 support in newer version
4. Contact mcpb maintainers / check GitHub issues

---

## File Inventory

| File | Lines | Status | Purpose |
|------|-------|--------|---------|
| `gov_mcp/plugin_tools.py` | 198 | NEW | 4 tool handlers (2 impl, 2 stub) |
| `gov_mcp/server.py` | +3 | MODIFIED | Import + register plugin_tools |
| `tests/test_plugin_tools.py` | 80 | NEW | 3 tests (all pass) |
| `plugin.json` | 61 | UNCHANGED | Tool schema (v2 format) |

---

## Day 3 Scope (Pending CEO Approval)

1. **Fix mcpb build** — Generate manifest.json OR convert plugin.json to v1
2. **Implement 2 stubs**:
   - `gov_install` — wrapper around `ystar setup` + `ystar init`
   - `gov_omission_scan` — wrapper around `state.omission_engine.scan()`
3. **Integration test** — Verify all 8 tools callable via MCP protocol (not just registered)
4. **Update README_PLUGIN.md** — Document build process + tool usage

---

## Rt+1 Assessment

**Y\*** (Day 2 target): 2 tools fully implemented + 6 stubs + FastMCP skeleton + tests pass + mcpb buildable  
**Yt+1** (actual): 2 tools fully implemented + 2 stubs + FastMCP skeleton + tests pass + **mcpb build blocked**  
**Rt+1**: mcpb manifest format incompatibility (1 blocker)

**Gap closure condition**: mcpb build succeeds OR alternative packaging confirmed working.

---

## Tool Use Count

**Used**: 14/15 tool_uses  
**Status**: ✅ Under budget

---

**CTO (Ethan Wright)**  
2026-04-16 02:47 UTC
