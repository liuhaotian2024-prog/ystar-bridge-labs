# Enforcement Patterns — CTO Knowledge Base

Last updated: 2026-04-10  
Source: BLOCKING_ENFORCEMENT_RESEARCH

## Core Principle

**Enforcement requires chokepoints.** Governance can only block what it can intercept.

### Chokepoint Inventory

| Chokepoint | Controlled By | Coverage |
|------------|---------------|----------|
| PreToolUse hook | Y-star-gov hook.py | All registered tools (Bash, Write, Edit, Read, Grep, MCP tools) |
| disallowed_tools | AGENTS.md + boundary_enforcer.py | Tool-level blocking (ANY tool can be blocked) |
| write_access paths | AGENTS.md + boundary_enforcer.py | File write operations |
| delegation_chain | gov_delegate MCP tool | Task dispatch |

### Non-Chokepoints (Cannot Block Directly)

| Action | Why Not a Chokepoint | Workaround |
|--------|----------------------|------------|
| Agent tool (OpenClaw primitive) | Bypasses PreToolUse hook | Block via disallowed_tools |
| Task tool (OpenClaw primitive) | Bypasses PreToolUse hook | Block via disallowed_tools |
| LLM reasoning | Not a tool call | No enforcement possible (design-time only) |
| PostToolUse actions | Hook not implemented yet | Add to platform backlog |

## Enforcement Pattern Catalog

### Pattern 1: Immutable Path Protection

**Use case**: Prevent agents from modifying governance charter files (AGENTS.md, .claude/agents/)

**Implementation**: `_check_immutable_paths()` in boundary_enforcer.py

**Mechanism**:
```python
def _check_immutable_paths(tool_name, params, who) -> Optional[PolicyResult]:
    if tool_name not in {"Write", "Edit", "MultiEdit"}:
        return None  # Not a write operation
    
    file_path = params.get("file_path", "")
    patterns = ["AGENTS.md", ".claude/agents/"]
    
    for pattern in patterns:
        if matches(file_path, pattern):
            return PolicyResult(allowed=False, reason="Immutable path")
    
    return None  # Allow
```

**Key insight**: Check happens BEFORE policy.check(), so even high-privilege agents cannot override.

### Pattern 2: Write Boundary Enforcement

**Use case**: Restrict agents to their authorized write paths

**Implementation**: `_check_write_boundary()` in boundary_enforcer.py

**Data source**: `write_access` section in AGENTS.md

**Mechanism**:
```python
def _check_write_boundary(who, tool_name, params) -> Optional[PolicyResult]:
    if tool_name not in {"Write", "Edit", "MultiEdit"}:
        return None
    
    allowed_paths = _AGENT_WRITE_PATHS.get(who, [])
    file_path = params.get("file_path", "")
    
    if not any(file_path.startswith(p) for p in allowed_paths):
        return PolicyResult(allowed=False, reason=f"Outside write boundary: {allowed_paths}")
    
    return None
```

**Key insight**: Path lists are preloaded (lazy init), so no AGENTS.md parsing on every hook call.

### Pattern 3: Tool Restriction

**Use case**: Block specific tools for specific roles (e.g., CEO cannot use Agent tool)

**Implementation**: `_check_tool_restriction()` in boundary_enforcer.py

**Data source**: `allowed_tools` / `disallowed_tools` in AGENTS.md

**Mechanism**:
```python
def _check_tool_restriction(who, tool_name) -> Optional[PolicyResult]:
    disallowed = _AGENT_DISALLOWED_TOOLS.get(who, [])
    if tool_name in disallowed:
        return PolicyResult(allowed=False, reason=f"Tool {tool_name} disallowed for {who}")
    
    allowed = _AGENT_ALLOWED_TOOLS.get(who, [])
    if allowed and tool_name not in allowed:
        return PolicyResult(allowed=False, reason=f"Tool {tool_name} not in allowlist")
    
    return None
```

**Key insight**: This pattern works for ANY tool, including OpenClaw platform primitives (Agent, Task).

### Pattern 4: Delegation Chain Validation

**Use case**: Enforce organizational hierarchy (CEO → CTO → engineers, not CEO → engineers directly)

**Implementation**: `check_delegation_authority()` in dispatch_logic.py

**Data source**: `.ystar_session.json` delegation_chain field

**Mechanism**:
```python
def check_delegation_authority(dispatcher_id, target_agent, chain) -> Tuple[bool, List[str]]:
    # Tree mode: check if target is in dispatcher's subtree
    dispatcher_node = chain.all_contracts.get(dispatcher_id)
    if dispatcher_node:
        if is_descendant(dispatcher_node, target_agent):
            return True, [dispatcher_id, target_agent]
    
    # Linear mode: check if link exists
    for link in chain.links:
        if link.principal == dispatcher_id and link.actor == target_agent:
            return True, [dispatcher_id, target_agent]
    
    return False, []
```

**Key insight**: This only works when agents use gov_delegate. Direct Agent tool usage bypasses this check — must use Pattern 3 to block Agent tool.

### Pattern 5: Layer Gate Enforcement (Autonomous Missions)

**Use case**: Require agents to complete Layer 1 (GEMMA questions) before Layer 3 (execution) in 12-layer framework

**Implementation**: NEW — proposed in BLOCKING_ENFORCEMENT_RESEARCH

**Data source**: `knowledge/{role}/active_task.json`

**Mechanism**:
```python
def _check_layer_gate(layer_state, tool_name, params, agent_id) -> Optional[PolicyResult]:
    if not layer_state["is_autonomous_mission"]:
        return None  # Only enforce for Autonomous Missions
    
    current_layer = layer_state["current_layer"]
    progress = layer_state["twelve_layer_progress"]
    
    # Gate 1: Layer 1 required before execution
    if current_layer >= 3 and not progress.get("1_gemma_questions"):
        if _is_execution_tool(tool_name, params):
            return PolicyResult(
                allowed=False,
                reason="Layer 1 (GEMMA questions) required before execution"
            )
    
    return None
```

**Key insight**: Layer state is external to hook (stored in knowledge/ directory), so hook becomes stateless gate enforcer.

### Pattern 6: Content Inspection (Intent Detection)

**Use case**: Detect delegation intent in task file writes, force use of gov_delegate

**Implementation**: NEW — proposed in BLOCKING_ENFORCEMENT_RESEARCH

**Mechanism**:
```python
def _check_task_file_dispatch(who, file_path, content) -> Optional[PolicyResult]:
    if not file_path.startswith(".claude/tasks/"):
        return None
    
    delegation_patterns = [
        r"(cto|eng-\w+):\s*(build|fix|implement)",
        r"deadline|due\s+by"
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in delegation_patterns):
        return PolicyResult(
            allowed=False,
            reason="Use gov_delegate for task delegation, not task files"
        )
    
    return None
```

**Key insight**: Pattern-based detection has inherent false positive/negative rates. Requires tuning.

**Confidence**: 70% (vs 95%+ for structural patterns like path matching)

## Design Principles

### Principle 1: Fail-Safe Defaults

All enforcement functions return `Optional[PolicyResult]`:
- `None` → allow (no violation)
- `PolicyResult(allowed=False)` → deny

If enforcement code raises exception → hook catches it, logs, and **allows** the action (fail open).

**Rationale**: Governance bugs should not brick the system.

### Principle 2: Enforcement Before Scoring

Hook execution order:
1. Immutable path check (unconditional block)
2. Tool restriction check (unconditional block)
3. Write boundary check (unconditional block)
4. Layer gate check (NEW, unconditional block)
5. Policy.check() (score-based, can be overridden)

**Rationale**: Security boundaries (immutable, write_access, disallowed_tools) are non-negotiable. Policy violations (cost limits, risk scores) are warnings.

### Principle 3: Stateless Hook, Stateful Context

Hook.py does not store state. All state comes from:
- `.ystar_session.json` (session config)
- `AGENTS.md` (governance charter)
- `knowledge/{role}/active_task.json` (layer progression)
- `.ystar_cieu.db` (audit log)

**Rationale**: Stateless hooks are easier to test, debug, and reason about.

### Principle 4: Chokepoint Fallback

When primary chokepoint doesn't exist, block at secondary chokepoint:

| Primary Chokepoint | Secondary Chokepoint | Example |
|--------------------|----------------------|---------|
| Agent tool hook | disallowed_tools | CEO spawning eng-kernel |
| PostToolUse hook | PreToolUse content inspection | Detecting delegation in Write |
| Runtime enforcement | Config-time error | Invalid delegation chain in session.json |

**Rationale**: Enforcement depth degrades gracefully when platform primitives change.

## Anti-Patterns

### Anti-Pattern 1: Scoring Without Blocking

**Wrong**:
```python
if cost > budget:
    score -= 10  # Agent ignores this
```

**Right**:
```python
if cost > budget:
    return PolicyResult(allowed=False, reason="Budget exceeded")
```

**Lesson**: Agents optimize for task completion, not score. Only blocking changes behavior.

### Anti-Pattern 2: Blocking in Orchestrator

**Wrong**:
```python
# In orchestrator.py
if violation_detected:
    return {"action": "block"}  # TOO LATE — hook already allowed the action
```

**Right**:
```python
# In hook.py (before tool execution)
if violation_detected:
    return {"action": "block"}
```

**Lesson**: Orchestrator runs AFTER hook allows action. By then, tool may have already executed.

### Anti-Pattern 3: Relying on Agent Compliance

**Wrong**:
```yaml
ceo:
  guidelines:
    - "Please use gov_delegate instead of Agent tool"  # Agent may ignore
```

**Right**:
```yaml
ceo:
  disallowed_tools:
    - Agent  # Enforced by hook
```

**Lesson**: Guidelines are suggestions. disallowed_tools is enforcement.

## Future Patterns (Roadmap)

### Pattern 7: PostToolUse Hook (Not Yet Implemented)

**Use case**: Enforce Layer 12 gate (knowledge writeback required before task completion)

**Mechanism**:
```python
# In post_tool_use hook
if tool_name == "Write" and "active_task.json" in file_path:
    if status_changed_to_completed(old_content, new_content):
        # Check if knowledge writeback happened during this task
        kb_files = glob("knowledge/{role}/**/*.md")
        new_files = [f for f in kb_files if created_after(f, task_start_time)]
        if not new_files:
            ROLLBACK_WRITE()  # Or DENY next tool call
            return PolicyResult(allowed=False, reason="Layer 12 required")
```

**Blocker**: OpenClaw does not yet support PostToolUse hooks.

**Timeline**: Add to platform backlog, 2-3 day implementation.

### Pattern 8: Causal Chain Enforcement

**Use case**: Require that action Y only happens if action X happened first (e.g., deploy only after tests pass)

**Mechanism**:
```python
# In hook.py
if tool_name == "Bash" and "git push" in command:
    # Check CIEU log: did tests run in past 10 minutes?
    recent_events = cieu_store.query(actor=who, action="Bash", within_secs=600)
    if not any("pytest" in e.params.get("command", "") for e in recent_events):
        return PolicyResult(allowed=False, reason="Tests required before push")
```

**Status**: Feasible with existing CIEU infrastructure, not yet implemented.

**Confidence**: 85% (depends on CIEU query performance)

## Lessons from BLOCKING_ENFORCEMENT_RESEARCH

1. **Agent tool bypass discovered** — Platform primitives may not respect hooks. Always have fallback (disallowed_tools).

2. **12-layer framework needs runtime enforcement** — Documentation alone is insufficient. Agents skip steps unless blocked.

3. **Content inspection is unreliable** — Pattern matching for intent (delegation vs documentation) has 70% confidence. Use only when no structural alternative exists.

4. **Effort scaling**: Config changes (5 min) < Hook integration (2 hours) < New subsystem (12 hours)

5. **Board's insight validated**: Scoring doesn't change behavior. Only DENY does.
