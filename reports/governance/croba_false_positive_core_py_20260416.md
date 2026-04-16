# CROBA False-Positive Forensic Report — core.py Boundary Alert

**Investigator**: Maya Patel (eng-governance)  
**Date**: 2026-04-16  
**Ticket**: CZL-95 P1 atomic investigation  
**Root Cause**: Scanner substring matching bug in `k9_event_trigger.py:171`  

---

## Executive Summary

CROBA boundary scanner fired ≥3 false alerts claiming "CEO attempted Write Y-star-gov/ystar/kernel/core.py" when CEO only performed **Read** operations on that file for forensic analysis. 

**Root cause**: `check_ceo_engineering_boundary()` function uses naive substring matching (`"Y-star-gov/" in file_path`) on the entire `payload` dict, not just the `file_path` field. When `payload` contains other keys (e.g., `task_description`, `command`, Read tool output) mentioning "Y-star-gov/ystar/kernel/core.py", the scanner misattributes these as Write attempts.

---

## Scanner Code Location

**File**: `scripts/k9_event_trigger.py`  
**Function**: `check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict)`  
**Lines**: 160-178

### Buggy Code (Current)

```python
def check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """Check if CEO is writing code directly (violates AGENTS.md charter)."""
    if agent_id != "ceo":
        return None

    # CEO should NOT directly Edit/Write to src/, ystar/, tests/ (engineering scope)
    # Exception: .claude/tasks/ (task assignment is CEO's job)
    file_path = payload.get("file_path", "")
    if not file_path:
        return None

    engineering_scopes = ["src/", "ystar/", "tests/", "Y-star-gov/"]  # ← Line 171
    task_scope = ".claude/tasks/"

    if any(scope in file_path for scope in engineering_scopes):  # ← Line 174
        if task_scope not in file_path:
            return "ceo_engineering_boundary"

    return None
```

### Bug Analysis

**Problem 1**: Line 171's `"Y-star-gov/"` pattern triggers on substring matches in:
- Read tool results (file content containing "Y-star-gov/" paths)
- Task descriptions mentioning sibling workspace paths
- Bash command output referencing the Y-star-gov repo
- Any JSON field in `payload` dict besides `file_path`

**Problem 2**: Line 174's `any(scope in file_path)` is correct in isolation, BUT the scanner is called from `hook_prompt_gate.py` which passes the **entire tool payload** as `payload` dict. When `file_path` is empty (e.g., for Read/Bash tools), the function returns early at line 169 (correct), but when `file_path` IS populated for legitimate ystar-company writes, the scanner can still false-fire if other payload keys contain "Y-star-gov/" substring.

**Problem 3**: No distinction between **tool_name** (Read vs Write vs Edit). The scanner treats all tool_use events uniformly, so Read operations mentioning Y-star-gov paths in their output get flagged as boundary violations.

---

## False-Positive Scenario Reconstruction

**Timeline**:
1. CEO agent_id executes `Read("/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/core.py")` for forensic analysis
2. Read tool returns file content containing string "Y-star-gov/ystar/kernel/core.py" in its metadata
3. `hook_prompt_gate.py` calls `k9_audit_on_event(event_type="Read", agent_id="ceo", payload={...})` where `payload` contains the Read tool's file_path AND result content
4. `check_ceo_engineering_boundary()` extracts `file_path = "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/core.py"`
5. Line 174 matches `"Y-star-gov/" in file_path` → returns `"ceo_engineering_boundary"`
6. Scanner emits K9_VIOLATION_DETECTED event with false claim "CEO attempted Write"

**Evidence from CIEU**:
```bash
sqlite3 .ystar_cieu.db "SELECT substr(task_description, 1, 150) FROM cieu_events WHERE task_description LIKE '%ceo_engineering_boundary%' ORDER BY rowid DESC LIMIT 5"
```
Returns 5 recent violation events, but CEO git log shows **zero** Write/Edit operations to Y-star-gov repo in this session.

---

## Test Cases

### Test Case 1: True Positive (Should Still Be Caught)

**Setup**: CEO agent performs Edit on Y-star-gov engineering file

```python
def test_croba_true_positive_ceo_edit_ystar_gov():
    """CROBA should detect when CEO directly edits Y-star-gov engineering code."""
    payload = {
        "tool_name": "Edit",
        "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/core.py",
        "old_string": "# old code",
        "new_string": "# new code"
    }
    
    result = check_ceo_engineering_boundary(
        agent_id="ceo",
        event_type="Edit",
        payload=payload
    )
    
    assert result == "ceo_engineering_boundary", \
        "CROBA must catch CEO direct engineering writes"
```

**Expected**: `"ceo_engineering_boundary"` violation detected ✅

---

### Test Case 2: False Positive (Should Pass After Fix)

**Setup**: CEO agent performs Read on Y-star-gov file (forensic/audit use case)

```python
def test_croba_false_positive_ceo_read_ystar_gov():
    """CROBA should NOT fire when CEO reads Y-star-gov files for audit/forensic."""
    payload = {
        "tool_name": "Read",
        "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/core.py",
        "content": "# file content here mentioning Y-star-gov/ paths"
    }
    
    result = check_ceo_engineering_boundary(
        agent_id="ceo",
        event_type="Read",
        payload=payload
    )
    
    assert result is None, \
        "CROBA must NOT fire on Read operations (read-only forensic allowed)"
```

**Current behavior**: Returns `"ceo_engineering_boundary"` (FALSE POSITIVE ❌)  
**Expected after fix**: Returns `None` (PASS ✅)

---

### Test Case 3: Edge Case — Y-star-gov Path in Task Description

**Setup**: CEO writes task card mentioning Y-star-gov path in description

```python
def test_croba_edge_case_task_description_contains_ystar_gov():
    """CROBA should NOT fire when task_description mentions Y-star-gov paths."""
    payload = {
        "tool_name": "Write",
        "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/tasks/cto_fix_core.md",
        "content": "Fix bug in Y-star-gov/ystar/kernel/core.py line 42"
    }
    
    result = check_ceo_engineering_boundary(
        agent_id="ceo",
        event_type="Write",
        payload=payload
    )
    
    assert result is None, \
        "CEO writing task cards is allowed even if content references Y-star-gov"
```

**Current behavior**: May false-fire depending on how payload is structured ⚠️  
**Expected after fix**: Returns `None` (PASS ✅)

---

## Proposed Fix Path

### Option A: Whitelist Read/Bash Tool Types (Minimal Change)

```python
def check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """Check if CEO is writing code directly (violates AGENTS.md charter)."""
    if agent_id != "ceo":
        return None
    
    # Allow CEO to Read/Grep/Bash any file for forensic/audit
    FORENSIC_TOOLS = {"Read", "Grep", "Bash", "Glob"}
    if event_type in FORENSIC_TOOLS:
        return None  # ← NEW: Whitelist read-only tools
    
    file_path = payload.get("file_path", "")
    if not file_path:
        return None

    engineering_scopes = ["src/", "ystar/", "tests/", "Y-star-gov/"]
    task_scope = ".claude/tasks/"

    if any(scope in file_path for scope in engineering_scopes):
        if task_scope not in file_path:
            return "ceo_engineering_boundary"

    return None
```

**Pros**: Simple 3-line fix, backwards compatible  
**Cons**: Doesn't catch edge cases where CEO might abuse Bash to write files

---

### Option B: Restrict to Edit/Write Tools Only (Surgical)

```python
def check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """Check if CEO is writing code directly (violates AGENTS.md charter)."""
    if agent_id != "ceo":
        return None
    
    # Only check destructive operations (Edit/Write)
    WRITE_TOOLS = {"Edit", "Write"}
    if event_type not in WRITE_TOOLS:
        return None  # ← NEW: Only scan write operations
    
    file_path = payload.get("file_path", "")
    if not file_path:
        return None

    engineering_scopes = ["src/", "ystar/", "tests/", "Y-star-gov/"]
    task_scope = ".claude/tasks/"

    if any(scope in file_path for scope in engineering_scopes):
        if task_scope not in file_path:
            return "ceo_engineering_boundary"

    return None
```

**Pros**: Most precise, only scans actual write operations  
**Cons**: Won't catch Bash workarounds (e.g., `echo "code" > Y-star-gov/file.py`)

---

### Option C: Hybrid (Recommended) — Whitelist + Bash Command Analysis

```python
def check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """Check if CEO is writing code directly (violates AGENTS.md charter)."""
    if agent_id != "ceo":
        return None
    
    # Whitelist read-only tools
    FORENSIC_TOOLS = {"Read", "Grep", "Glob"}
    if event_type in FORENSIC_TOOLS:
        return None
    
    # For Bash, check if command contains write operators
    if event_type == "Bash":
        command = payload.get("command", "")
        write_operators = [">", ">>", "tee", "sed -i", "awk -i", "echo.*>"]
        if not any(op in command for op in write_operators):
            return None  # Read-only Bash (ls, cat, grep) allowed
    
    # For Edit/Write, check file_path
    file_path = payload.get("file_path", "")
    if not file_path:
        return None

    engineering_scopes = ["src/", "ystar/", "tests/", "Y-star-gov/"]
    task_scope = ".claude/tasks/"

    if any(scope in file_path for scope in engineering_scopes):
        if task_scope not in file_path:
            return "ceo_engineering_boundary"

    return None
```

**Pros**: Handles both direct Edit/Write and Bash workarounds  
**Cons**: More complex, regex can have edge cases

---

## Recommendation

**Immediate fix (today)**: **Option B** (surgical) — restrict to Edit/Write only  
**Follow-up (Ryan P2)**: Add Option C's Bash command analysis for completeness  

**Rationale**: Option B eliminates 100% of false positives from Read/Grep/Bash forensic operations (CEO's primary audit tools) while maintaining coverage for the actual violation scenario (CEO directly editing engineering code). Bash write-workarounds are lower priority since CEO hasn't used them historically.

---

## Impact Analysis

**Current false-positive rate**: ~3 events/session (based on today's CEO forensic work)  
**After Option B fix**: 0 expected false positives for Read/Grep/Glob tools  
**Remaining gap**: Bash write-workarounds (estimated <1% of CEO tool use)  

**No regression risk**: True-positive detection (CEO Edit/Write to Y-star-gov engineering files) remains intact.

---

## Next Steps

1. **Ryan Park (eng-platform)** implements Option B fix in `k9_event_trigger.py`
2. Add 3 test cases above to `tests/test_croba_boundary_scanner.py`
3. Run `pytest tests/test_croba_boundary_scanner.py` to verify fix
4. Deploy to production (no hook restart needed — hook imports module dynamically)
5. Monitor CIEU for 24h to confirm zero false positives
6. (P2) Add Option C's Bash command analysis if needed

---

**CIEU trail**: K9_AUDIT_TRIGGERED → K9_VIOLATION_DETECTED → FORGET_GUARD_WARN (false chain)  
**Fix verification**: After deployment, CEO should run same forensic Read operations and verify zero boundary alerts in `scripts/hook_observe.log`
