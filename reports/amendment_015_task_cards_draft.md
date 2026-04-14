# AMENDMENT-015 Task Cards (Draft for Board Transfer to .claude/tasks/)

**Context**: CEO hit L5 lock writing task cards — `.claude/tasks/` requires secretary, switching to secretary requires secretary. Task content drafted here for Board to transfer.

---

## eng-platform-20260413-phase1-mcp-permission-matrix.md

```markdown
## Task: AMENDMENT-015 Phase 1 - MCP Permission Matrix Audit
Engineer: eng-platform (Ryan Park)
Priority: P0
Assigned: 2026-04-13
Deadline: 2026-04-13 17:00 (4h)
Owner: Ethan-CTO (AMENDMENT-015)

## Objective
Enumerate every gov-mcp MCP tool's permission requirements and produce a dependency graph showing circular dependencies between role checks, locks, and state files.

## Acceptance Criteria
- [ ] Complete matrix: tool × role × required_lock mapping for all gov-mcp tools
- [ ] Dependency graph identifying all permission cycles (e.g., tool A requires role X → switching to X requires writing file F → writing F requires tool A permission)
- [ ] Output written to `reports/lock_dependency_graph_20260413.md`
- [ ] No files outside scope modified
- [ ] All tests pass

## Files in Scope
- gov-mcp repo: all MCP tool definitions (server.py or equivalent)
- /Users/haotianliu/.openclaw/workspace/ystar-company/reports/lock_dependency_graph_20260413.md (create)

## Context
Part of AMENDMENT-015 systemic self-lock audit. This phase feeds into Phase 2 (Maya's taxonomy) and Phase 3 (Ethan's architecture design).

Your deliverable: permission matrix showing which tools have circular preconditions (tool needs role, role switch needs file write, file write needs tool permission).

## Coordination
- Parallel with Leo-Kernel (Y*gov role gates)
- Output to be consumed by Maya-Governance (Phase 2) after completion
```

---

## eng-kernel-20260413-phase1-ystar-role-gates.md

```markdown
## Task: AMENDMENT-015 Phase 1 - Y*gov Role Gates Audit
Engineer: eng-kernel (Leo Chen)
Priority: P0
Assigned: 2026-04-13
Deadline: 2026-04-13 17:00 (4h)
Owner: Ethan-CTO (AMENDMENT-015)

## Objective
Enumerate all Y*gov role gates, restricted_write_paths, immutable_paths, and agent_role_gates. Map dependencies showing which permissions require which preconditions, identifying circular dependency chains.

## Acceptance Criteria
- [ ] Complete list: all restricted_write_paths / immutable_paths / agent_role_gates from .ystar_session.json and Y*gov source
- [ ] Dependency graph: which paths require which roles, which role switches require writing which paths
- [ ] Identify cycles: permission A requires state B, achieving state B requires permission A
- [ ] Output written to `reports/lock_dependency_graph_20260413.md` (append to Ryan's section or merge)
- [ ] No files outside scope modified
- [ ] All tests pass

## Files in Scope
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ (read source code)
- /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json (read constraints)
- /Users/haotianliu/.openclaw/workspace/ystar-company/reports/lock_dependency_graph_20260413.md (create or merge)

## Context
Part of AMENDMENT-015 systemic self-lock audit. This phase runs in parallel with Ryan's MCP permission matrix. Your output feeds into Phase 2 (Maya's taxonomy) and Phase 3 (Ethan's architecture design).

## Coordination
- Parallel with Ryan-Platform (MCP permission matrix)
- Output to be consumed by Maya-Governance (Phase 2) after completion
```

---

## eng-governance-20260413-phase2-lock-taxonomy.md

```markdown
## Task: AMENDMENT-015 Phase 2 - Lock Cycle Root-Cause Taxonomy
Engineer: eng-governance (Maya Patel)
Priority: P0
Assigned: 2026-04-13
Deadline: 2026-04-13 19:00 (2h after Phase 1 completion)
Owner: Ethan-CTO (AMENDMENT-015)
Blocked By: Phase 1 (Ryan + Leo)

## Objective
Analyze each circular dependency found in Phase 1 and classify root cause: genuine security requirement, over-defensive design, or legacy artifact. Assess whether breaking the cycle introduces new vulnerabilities.

## Acceptance Criteria
- [ ] Each lock cycle from Phase 1 has a classification: security-essential / over-defense / legacy
- [ ] Each cycle has a risk assessment: breaking it introduces [specific risk] or safe to break
- [ ] Output written to `reports/lock_cycles_taxonomy_20260413.md`
- [ ] No files outside scope modified
- [ ] All tests pass

## Files in Scope
- reports/lock_dependency_graph_20260413.md (read input from Phase 1)
- reports/lock_cycles_taxonomy_20260413.md (create)

## Context
Part of AMENDMENT-015 systemic self-lock audit. Your taxonomy feeds directly into Ethan's Phase 3 architecture design. For each cycle, answer:
1. Why does this lock exist? (original intent)
2. Is the intent still valid? (current necessity)
3. Can we break the cycle without introducing new attack surface?

## Coordination
- Blocked on Phase 1 (Ryan + Leo)
- Output consumed by Ethan-CTO (Phase 3)
- Start as soon as `reports/lock_dependency_graph_20260413.md` exists
```

---

## cto-phase3-architecture-skeleton.md

```markdown
## AMENDMENT-015 Phase 3 Architecture Design (Skeleton)
Owner: Ethan-CTO
Priority: P0
Assigned: 2026-04-13
Deadline: 2026-04-14 21:00 (6h after Phase 2 completion)
Blocked By: Phase 2 (Maya's taxonomy)

## Objective
Design the systemic unlock architecture based on Phase 1+2 findings. Replace role-based permission gates with capability-based delegation, introduce self-recovery mechanisms, and provide zero-Board-override escape paths for users.

## 4-Layer Architecture (Skeleton)

### Layer 1: Identity Source of Truth
**Decision Required** (fill after Phase 2):
- Single source of truth: .ystar_active_agent file vs in-memory state vs both?
- Sub-agent identity semantics: shadow (temporary impersonation) vs transfer (ownership change)?
- Restoration protocol: automatic on sub-agent exit vs manual handoff?
- Owner: which component owns identity truth? Hook daemon? MCP server? Session file?

### Layer 2: Capability-Based Permissions
**Design Principles** (fill after Phase 2):
- Replace role whitelist with capability grants (e.g., "write:reports/*" not "role:ceo")
- User-defined roles: allow custom roles in .ystar_session.json without code changes
- Delegation mechanism: agent A can grant temporary capability to agent B
- Revocation: explicit revoke vs time-based expiry vs scope-limited

### Layer 3: Self-Recovery Mechanisms
**Components** (fill after Phase 2):
- Sub-agent auto-restore: caller identity saved on delegation, restored on exit
- Hook daemon file watcher: replace cached state with inotify/FSEvents real-time watch
- Circuit breaker auto-reset: detect stuck ARMED state, auto-reset after timeout + log
- Conflict resolution: when file state diverges from daemon cache, which wins?

### Layer 4: User Escape Hatch (Zero Board Override)
**Safe Mode Design** (fill after Phase 2):
- CLI command: `ystar safemode <action>` bypasses all role checks for single action
- MCP tool: `gov_safemode` callable from Claude Code
- Audit trail: every safemode invocation logged to CIEU with justification
- Scope limits: which actions allowed in safemode? (role switch, state reset, daemon restart?)
- Abuse prevention: rate limit? Require intent declaration? Post-audit review?

## Output Format
Expand this skeleton into 6-pager format (`reports/amendment_015_design_20260413.md`) after Phase 2 completes:
- Problem statement (from Phase 1+2)
- Architecture layers (4 above, with decisions filled)
- Migration path (how to transition from current to new design)
- Testing strategy (red-team scenarios)
- Rollout plan (Phase 4 patch sequence)

## Files in Scope
- reports/lock_dependency_graph_20260413.md (Phase 1 output)
- reports/lock_cycles_taxonomy_20260413.md (Phase 2 output)
- reports/amendment_015_design_20260413.md (create after Phase 2)

## Next Steps (After This Skeleton)
1. Wait for Phase 2 completion
2. Fill architecture decisions based on taxonomy
3. Write full 6-pager design doc
4. Hand off to Phase 4 (Leo + Ryan + Maya for patch implementation)
```

---

**Board Action Required**:
Create the 4 task files above in `.claude/tasks/` directory. CEO cannot write there due to L5 lock (CEO → secretary switch requires secretary to already be active).

This is **demo-grade evidence** of AMENDMENT-015's motivation: even dispatching the fix requires hitting the bug.
