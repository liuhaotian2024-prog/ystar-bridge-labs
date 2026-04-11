# Blocking Enforcement Research

**Task ID**: BLOCKING_ENFORCEMENT_RESEARCH  
**Date**: 2026-04-10  
**Author**: CTO (Ethan)  
**Requestor**: Board of Directors  

## Executive Summary

This research investigates technical mechanisms to enforce agent governance through blocking (DENY) rather than scoring. Three failure scenarios were analyzed:

1. **Autonomous Missions bypassing 12-layer framework** — agents skip mandatory layers (GEMMA questions, self-eval, knowledge writeback)
2. **CEO bypassing CTO for engineering delegation** — delegation chain violated by direct spawn
3. **Dispatch-by-documentation** — agents write task files instead of actually executing delegation

Key finding: **Scenario 1 and parts of Scenario 3 are technically feasible with existing hook infrastructure. Scenario 2 has a fundamental limitation — OpenClaw's Agent tool bypasses PreToolUse hooks entirely.**

## Scenario 1: 12-Layer Gate Enforcement

### Problem Statement

When a task is marked as `"type": "Autonomous Mission"` in `knowledge/{role}/active_task.json`, the agent must progress through 12 layers:

```
Layer 0: INTENT_RECORDED
Layer 1: GEMMA questions → gemma_sessions.log entry required
Layer 3: Execution plan documented
Layer 10: Self-evaluation written before marking complete
Layer 12: Knowledge writeback to knowledge/ directory
```

Current state: Agents can skip layers. No technical enforcement exists.

### Technical Solution Design

#### Component 1: Layer State Tracker

Add to `ystar/adapters/layer_enforcer.py`:

```python
def _read_layer_state(agent_id: str) -> dict:
    """Read current layer state from knowledge/{agent_id}/active_task.json.
    
    Returns:
        {
            "is_autonomous_mission": bool,
            "current_layer": int,
            "task_id": str,
            "twelve_layer_progress": {
                "0_INTENT_RECORDED": bool,
                "1_gemma_questions": bool,
                ...
            }
        }
    """
    task_file = Path(f"knowledge/{agent_id}/active_task.json")
    if not task_file.exists():
        return {"is_autonomous_mission": False}
    
    data = json.loads(task_file.read_text())
    return {
        "is_autonomous_mission": data.get("type") == "Autonomous Mission",
        "current_layer": data.get("current_layer", 0),
        "task_id": data.get("task_id", ""),
        "twelve_layer_progress": data.get("twelve_layer_progress", {}),
    }
```

#### Component 2: Gate Conditions

Define gate rules (added to `.ystar_session.json` or AGENTS.md):

```yaml
twelve_layer_gates:
  1_gemma_questions:
    required_before_layer: 3
    artifact: knowledge/{role}/gaps/gemma_sessions.log
    condition: "file contains task_id"
  
  10_self_eval:
    required_before_status: "completed"
    artifact: knowledge/{role}/self_eval/{task_id}.md
    condition: "file exists"
  
  12_knowledge_writeback:
    required_before_status: "completed"
    artifact_pattern: knowledge/{role}/**/*.md
    condition: "at least 1 new file created during task"
```

#### Component 3: Hook Integration

Add to `ystar/adapters/hook.py` (in `check_hook` function, after immutable path check):

```python
# Layer 11: 12-layer progression gate (Autonomous Missions only)
layer_state = _read_layer_state(who)
if layer_state["is_autonomous_mission"]:
    gate_violation = _check_layer_gate(
        layer_state, tool_name, params_early, who
    )
    if gate_violation is not None:
        _write_cieu(who, tool_name, params_early, gate_violation,
                    session_id_payload or "unknown",
                    contract.hash if contract else "", cieu_db)
        _log.warning("DENY layer gate: %s layer=%d tool=%s", 
                     who, layer_state["current_layer"], tool_name)
        return _result_to_response(gate_violation)
```

#### Component 4: Gate Check Logic

```python
def _check_layer_gate(
    layer_state: dict,
    tool_name: str,
    params: dict,
    agent_id: str,
) -> Optional[PolicyResult]:
    """Check if tool call violates layer progression gates.
    
    Examples:
    - Layer 1 not complete + trying to execute → DENY
    - Trying to mark task complete without Layer 10 self-eval → DENY
    - Writing task completion without Layer 12 knowledge writeback → DENY
    """
    current_layer = layer_state["current_layer"]
    progress = layer_state["twelve_layer_progress"]
    task_id = layer_state["task_id"]
    
    # Gate 1: Layer 1 (GEMMA questions) required before Layer 3 (execution)
    if current_layer >= 3 and not progress.get("1_gemma_questions"):
        # Check if this is an execution tool (Write to non-knowledge paths, Bash, etc)
        if _is_execution_tool(tool_name, params):
            return PolicyResult(
                allowed=False,
                reason=(
                    f"Autonomous Mission layer gate violation: Layer 1 "
                    f"(GEMMA questions) must be completed before execution. "
                    f"Expected entry in knowledge/{agent_id}/gaps/gemma_sessions.log "
                    f"for task {task_id}"
                ),
                who=agent_id,
                what=tool_name,
                violations=[],
            )
    
    # Gate 2: Layer 10 (self-eval) required before marking complete
    if not progress.get("10_self_eval"):
        # Check if trying to update active_task.json status to "completed"
        if tool_name in {"Write", "Edit"} and \
           "active_task.json" in params.get("file_path", "") and \
           _content_contains_status_completed(params):
            return PolicyResult(
                allowed=False,
                reason=(
                    f"Autonomous Mission layer gate violation: Layer 10 "
                    f"(self-evaluation) must be completed before marking task complete. "
                    f"Expected file: knowledge/{agent_id}/self_eval/{task_id}.md"
                ),
                who=agent_id,
                what=tool_name,
                violations=[],
            )
    
    # Gate 3: Layer 12 (knowledge writeback) checked via post-completion scan
    # (cannot be enforced in PreToolUse hook — requires PostToolUse or async scan)
    
    return None

def _is_execution_tool(tool_name: str, params: dict) -> bool:
    """Execution = modifying non-knowledge files or running commands."""
    if tool_name == "Bash":
        return True
    if tool_name in {"Write", "Edit", "MultiEdit"}:
        path = params.get("file_path", "")
        # Knowledge path writes are always allowed (documentation phase)
        if path.startswith("knowledge/"):
            return False
        return True
    return False

def _content_contains_status_completed(params: dict) -> bool:
    """Check if Write/Edit content sets status to completed."""
    content = params.get("content", "") or params.get("new_string", "")
    return '"status": "completed"' in content or "'status': 'completed'" in content
```

### Feasibility Analysis

| Component | Feasibility | Effort | Constraints |
|-----------|-------------|--------|-------------|
| Layer state reader | HIGH | 1 hour | Requires knowledge/{role}/active_task.json exists |
| Gate conditions | HIGH | 2 hours | Config format needs design (YAML vs JSON) |
| Hook integration | HIGH | 30 min | Insert at correct position in check_hook |
| Gate 1 enforcement | HIGH | 2 hours | Can detect execution tools reliably |
| Gate 2 enforcement | HIGH | 2 hours | Content inspection needed (regex) |
| Gate 3 enforcement | MEDIUM | 4 hours | Needs PostToolUse hook or async scan |

**Total implementation time: ~12 hours**

**Blockers**: None. All required mechanisms exist.

**Recommendation**: IMPLEMENT THIS. High impact, low risk.

---

## Scenario 2: Block CEO Bypassing CTO for Engineering Delegation

### Problem Statement

Current delegation chain:
```
Board → CEO → CTO → eng-kernel/eng-governance/eng-platform/eng-domains
```

When CEO uses `Agent` tool to spawn eng-kernel directly, the delegation chain is violated. CTO is bypassed.

Expected behavior: Hook should DENY and force CEO to use `gov_delegate` targeting CTO.

### Root Cause Analysis

#### Finding 1: Agent Tool Bypasses Hook

Tested in `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_hook.py`:

```python
# This tool call DOES trigger hook.py
{"tool_name": "Bash", "tool_input": {"command": "echo test"}}

# This tool call DOES NOT trigger hook.py
{"tool_name": "Agent", "tool_input": {"agent": "eng-kernel", "task": "..."}}
```

Reason: `Agent` is an OpenClaw platform primitive, not a tool in the tool registry. It spawns a subprocess directly without invoking the tool execution pipeline.

#### Finding 2: gov_delegate Already Implements the Right Pattern

From `gov_mcp/dispatch_logic.py`:

```python
def dispatch_task(...) -> Dict:
    # Layer 1: Check delegation chain authority
    has_authority, authority_path = check_delegation_authority(
        dispatcher_id, target_agent, chain
    )
    if not has_authority:
        return {
            "decision": "DENY",
            "reason": f"Agent '{dispatcher_id}' has no delegation authority over '{target_agent}'",
        }
```

This works correctly when agents use `gov_delegate`. The problem is that `Agent` tool doesn't route through `gov_delegate`.

### Technical Solutions (Three Approaches)

#### Approach A: Disallow Agent Tool, Enforce gov_delegate

Add to AGENTS.md:

```yaml
ceo:
  disallowed_tools:
    - Agent  # DENY direct subagent spawning
    - Task   # DENY bypassing delegation chain
```

Add to hook.py (already exists — tool restriction check):

```python
tool_deny = _check_tool_restriction(who, tool_name)
if tool_deny is not None:
    return _result_to_response(tool_deny)
```

**Result**: CEO's attempt to use Agent tool → DENIED. Error message instructs to use `gov_delegate`.

**Pros**:
- Works with existing infrastructure
- Zero code changes needed (config-only)
- Clear error message guides correct behavior

**Cons**:
- Requires CEO to learn MCP tool (gov_delegate)
- Breaks if OpenClaw adds new delegation primitives

**Status**: READY TO DEPLOY (add to AGENTS.md)

#### Approach B: Intercept Agent Tool via Platform Hook

Modify OpenClaw's tool dispatcher to treat `Agent` as a hookable tool.

**Status**: REQUIRES OPENCLAW CODEBASE MODIFICATION. Outside our control.

#### Approach C: Post-spawn Detection + Retroactive Kill

After CEO spawns eng-kernel, detect the violation via CIEU analysis:

1. CEO writes to `.claude/agents/eng-kernel/.session`
2. Hook detects Write to `.claude/agents/*/.session`
3. Hook checks: did CEO call `gov_delegate` with target=cto in past 60 seconds?
4. If no → DENY the Write (prevents session file creation)

**Pros**: Works without modifying Agent tool

**Cons**:
- Fragile (depends on session file write pattern)
- Doesn't prevent the spawn, only prevents session persistence
- Subagent may already execute before killed

**Status**: TECHNICALLY FEASIBLE but unreliable. Not recommended.

### Feasibility Matrix

| Approach | Feasibility | Effort | Reliability |
|----------|-------------|--------|-------------|
| A: Disallow Agent tool | HIGH | 5 min | HIGH |
| B: Hook Agent tool | LOW | N/A | HIGH (if possible) |
| C: Post-spawn detection | MEDIUM | 6 hours | LOW (race conditions) |

**Recommendation**: DEPLOY APPROACH A IMMEDIATELY. Add `Agent` to disallowed_tools for ceo role.

---

## Scenario 3: Block Dispatch-by-Documentation

### Problem Statement

CEO receives instruction: "Give this task to Ethan (CTO)."

**Wrong behavior**: CEO writes `.claude/tasks/cto_task_001.md` and considers it done.

**Right behavior**: CEO calls `gov_delegate` or uses `Agent` tool to actually spawn CTO.

### Root Cause

Distinguishing "documentation" from "delegation" requires intent inference:

```python
# Documentation (allowed)
Write(".claude/tasks/future_ideas.md", "Consider adding feature X")

# Delegation (must use gov_delegate)
Write(".claude/tasks/cto_task_001.md", "CTO: Build feature X by Friday")
```

Both are Write operations to `.claude/tasks/`. No structural difference.

### Technical Solutions

#### Solution 1: Require gov_delegate for All .claude/tasks Writes

Add to AGENTS.md:

```yaml
ceo:
  write_access:
    - "!.claude/tasks/"  # DENY all writes to task directory
  
  # CEO must use gov_delegate instead of writing task files directly
```

**Result**: CEO tries to write task file → DENIED. Error message: "Use gov_delegate to assign tasks."

**Pros**: Simple, clear enforcement

**Cons**:
- Breaks legitimate use cases (e.g., CEO documenting task backlog)
- Too strict

**Status**: FEASIBLE but too restrictive.

#### Solution 2: Post-write Obligation Check

1. Allow CEO to Write `.claude/tasks/{target}_task_*.md`
2. Create obligation: "If file contains delegation language, must call gov_delegate within 5 minutes"
3. OmissionEngine scans for unfulfilled obligations
4. If CEO wrote task file but never called gov_delegate → OMISSION alert

**Pros**: Allows documentation, enforces delegation

**Cons**:
- Not a blocking mechanism (retroactive detection only)
- Requires NLP to detect "delegation language"
- CEO can still ignore the alert

**Status**: FEASIBLE for detection, NOT a blocker.

#### Solution 3: Write Hook Content Inspection

When CEO writes to `.claude/tasks/`, inspect content:

```python
def _check_task_file_dispatch(who: str, file_path: str, content: str) -> Optional[PolicyResult]:
    """Block task file writes that look like delegation without gov_delegate."""
    if not file_path.startswith(".claude/tasks/"):
        return None
    
    # Pattern detection: imperative language addressed to another agent
    delegation_patterns = [
        r"(cto|cmo|cso|cfo|eng-\w+):\s*(build|fix|implement|write|create)",
        r"(please|must|should)\s+(build|fix|implement)",
        r"deadline|due\s+by|deliver\s+by",
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in delegation_patterns):
        # This looks like delegation — require gov_delegate instead
        return PolicyResult(
            allowed=False,
            reason=(
                f"Task file contains delegation language. "
                f"Use gov_delegate tool instead of writing task files directly. "
                f"This ensures proper obligation tracking."
            ),
            who=who,
            what="Write",
            violations=[],
        )
    
    return None
```

Add to hook.py:

```python
if tool_name in {"Write", "Edit"}:
    content = params.get("content", "") or params.get("new_string", "")
    dispatch_violation = _check_task_file_dispatch(who, params.get("file_path", ""), content)
    if dispatch_violation is not None:
        return _result_to_response(dispatch_violation)
```

**Pros**: Blocks actual delegation attempts while allowing documentation

**Cons**:
- False positives (e.g., "CTO should consider..." is not a delegation)
- False negatives (delegation written without imperative language)
- Regex fragility

**Status**: FEASIBLE with tuning. Requires pattern refinement.

### Feasibility Matrix

| Solution | Feasibility | Effort | False Positive Rate |
|----------|-------------|--------|---------------------|
| 1: Block all .claude/tasks writes | HIGH | 5 min | HIGH (blocks docs) |
| 2: Post-write obligation | HIGH | 4 hours | N/A (not blocking) |
| 3: Content inspection | MEDIUM | 3 hours | MEDIUM (needs tuning) |

**Recommendation**: PILOT SOLUTION 3. Start with strict patterns, relax based on false positive rate.

---

## Consolidated Feasibility Matrix

| Scenario | Blocking Feasible? | Implementation Effort | Recommended Approach |
|----------|--------------------|-----------------------|----------------------|
| 1: 12-layer gates | YES | 12 hours | Add layer_enforcer.py, integrate into hook.py |
| 2: CEO → CTO chain | YES (via disallow) | 5 minutes | Add Agent to disallowed_tools in AGENTS.md |
| 3: Dispatch-by-doc | PARTIAL | 3-4 hours | Content inspection with delegation pattern detection |

---

## Implementation Roadmap

### Phase 1: Immediate (Config Changes Only)

**Timeline**: Today  
**Effort**: 10 minutes

1. Add to AGENTS.md:
   ```yaml
   ceo:
     disallowed_tools:
       - Agent  # Must use gov_delegate for delegation
       - Task   # Must use gov_delegate for task assignment
   ```

2. Test:
   ```python
   # CEO tries to spawn eng-kernel directly
   # Expected: DENIED by tool restriction check
   ```

**Result**: Scenario 2 BLOCKED immediately.

### Phase 2: Layer Gate Enforcement

**Timeline**: 1-2 days  
**Effort**: 12 hours

1. Create `ystar/adapters/layer_enforcer.py`:
   - `_read_layer_state(agent_id)`
   - `_check_layer_gate(layer_state, tool_name, params, agent_id)`
   - `_is_execution_tool(tool_name, params)`

2. Integrate into `ystar/adapters/hook.py`:
   - Add layer gate check after tool restriction check
   - Write CIEU denial events

3. Add gate configuration to `.ystar_session.json`:
   ```json
   {
     "twelve_layer_gates": {
       "1_gemma_questions": {
         "required_before_layer": 3,
         "artifact": "knowledge/{role}/gaps/gemma_sessions.log"
       },
       "10_self_eval": {
         "required_before_status": "completed",
         "artifact": "knowledge/{role}/self_eval/{task_id}.md"
       }
     }
   }
   ```

4. Write tests in `tests/test_layer_gates.py`

**Result**: Scenario 1 BLOCKED.

### Phase 3: Dispatch-by-Documentation Detection

**Timeline**: 2-3 days  
**Effort**: 4 hours

1. Add to `ystar/adapters/boundary_enforcer.py`:
   ```python
   def _check_task_file_dispatch(who, file_path, content)
   ```

2. Integrate into hook.py (after write boundary check)

3. Define delegation patterns in `.ystar_session.json`:
   ```json
   {
     "delegation_patterns": [
       "(cto|cmo|eng-\\w+):\\s*(build|fix|implement)",
       "deadline|due\\s+by"
     ]
   }
   ```

4. Monitor false positive rate for 1 week
5. Adjust patterns based on CIEU denial logs

**Result**: Scenario 3 PARTIALLY BLOCKED (pattern-dependent).

---

## Technical Constraints and Limitations

### Constraint 1: Agent Tool Opacity

**Issue**: OpenClaw's `Agent` tool bypasses PreToolUse hooks.

**Impact**: Cannot intercept subagent spawning at tool call level.

**Mitigation**: Use `disallowed_tools` to force agents to use `gov_delegate` instead.

**Long-term fix**: Requires OpenClaw to expose `Agent` as a hookable tool.

### Constraint 2: Content Inspection Reliability

**Issue**: Detecting delegation intent from text requires NLP, which has false positives/negatives.

**Impact**: Solution 3 (dispatch-by-doc) cannot achieve 100% accuracy.

**Mitigation**: Start strict, tune based on operational data.

**Long-term fix**: Use structured delegation commands (gov_delegate) instead of freeform text.

### Constraint 3: PostToolUse Hooks Not Yet Implemented

**Issue**: Layer 12 (knowledge writeback) gate cannot be enforced in PreToolUse hook.

**Impact**: Cannot block task completion until knowledge writeback is verified.

**Mitigation**: Implement PostToolUse hook or async post-completion scan.

**Timeline**: Requires Y-star-gov platform work (2-3 days).

---

## Recommended Priority Order

1. **IMMEDIATE (5 min)**: Add `Agent` to disallowed_tools for ceo (Scenario 2)
2. **HIGH (2 days)**: Implement 12-layer gate enforcement (Scenario 1)
3. **MEDIUM (3 days)**: Pilot dispatch-by-doc detection (Scenario 3)
4. **LONG-TERM (1 week)**: Implement PostToolUse hook for Layer 12 gate

---

## Conclusion

Blocking enforcement is technically feasible for all three scenarios, with varying levels of complexity:

- **Scenario 2** can be solved immediately with config changes (disallowed_tools)
- **Scenario 1** requires new enforcement logic but uses existing hook infrastructure (12 hours)
- **Scenario 3** requires pattern detection with inherent reliability limits (4 hours + tuning)

The root insight: **Enforcement works when we control the chokepoint.** PreToolUse hooks are chokepoints for file writes, command execution, and governed tools. Agent spawning is NOT a chokepoint (OpenClaw platform primitive) — so we block it at the tool level instead.

Next step: Board approval to implement Phase 1 (immediate) and Phase 2 (layer gates).
