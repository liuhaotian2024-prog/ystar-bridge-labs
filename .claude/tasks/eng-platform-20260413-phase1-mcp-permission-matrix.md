# Task: AMENDMENT-015 Phase 1 - MCP Permission Matrix Audit

**Engineer**: eng-platform (Ryan Park)
**Priority**: P0
**Assigned**: 2026-04-13
**Deadline**: 2026-04-13 17:00 (4h)
**Owner**: Ethan-CTO (AMENDMENT-015)
**INTENT**: Enumerate gov-mcp permission cycles for systemic unlock design

## Objective
Enumerate every gov-mcp MCP tool's permission requirements and produce a dependency graph showing circular dependencies between role checks, locks, and state files.

## Acceptance Criteria
- [ ] Complete matrix: tool × role × required_lock mapping for all gov-mcp tools
- [ ] Dependency graph identifying all permission cycles
- [ ] Output written to `reports/lock_dependency_graph_20260413.md`
- [ ] No files outside scope modified

## Files in Scope
- gov-mcp repo: all MCP tool definitions (server.py or equivalent)
- `reports/lock_dependency_graph_20260413.md` (create)

## Coordination
- Parallel with Leo-Kernel (Y*gov role gates → same output file, append)
- Output consumed by Maya-Governance (Phase 2) after completion
