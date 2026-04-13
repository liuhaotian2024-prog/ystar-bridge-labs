# Task: AMENDMENT-015 Phase 3 - Architecture Design

**Owner**: Ethan-CTO
**Priority**: P0
**Assigned**: 2026-04-13
**Deadline**: 2026-04-14 21:00 (6h after Phase 2 completion)
**Blocked By**: Phase 2 (Maya taxonomy)
**INTENT**: Design 4-layer systemic unlock architecture for gov-mcp + Y*gov

## 4-Layer Architecture Skeleton

### Layer 1: Identity Source of Truth
Decisions pending Phase 2:
- Single source: file / memory / both?
- Sub-agent identity semantics: shadow vs transfer?
- Restoration: auto on exit vs manual handoff?
- Owner component: hook daemon / MCP / session file?

### Layer 2: Capability-Based Permissions
- Replace role whitelist with capability grants (`write:reports/*` not `role:ceo`)
- User-defined roles in `.ystar_session.json` without code changes
- Delegation mechanism: agent A grants temporary cap to B
- Revocation: explicit / time-based / scope-limited

### Layer 3: Self-Recovery
- Sub-agent auto-restore caller identity
- Hook daemon file watcher replace cached state (inotify/FSEvents)
- Circuit breaker auto-reset on stuck ARMED
- Daemon-cache vs file-state conflict resolution

### Layer 4: User Escape Hatch (Zero Board Override)
- CLI `ystar safemode <action>` bypass single action
- MCP `gov_safemode` from Claude Code
- CIEU audit trail + justification
- Scope limits + abuse prevention (rate limit / intent decl / post-review)

## Output
Expand to 6-pager `reports/amendment_015_design_20260413.md` after Phase 2:
- Problem (Phase 1+2 findings)
- Architecture (4 layers filled)
- Migration path
- Testing strategy (red-team scenarios)
- Rollout plan (Phase 4 patch sequence)

## Next Steps
1. Wait Phase 2 taxonomy
2. Fill architecture decisions
3. Write full 6-pager
4. Hand off Phase 4 (Leo+Ryan+Maya patch impl)
