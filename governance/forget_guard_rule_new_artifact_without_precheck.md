# ForgetGuard Rule Spec: `new_artifact_without_precheck`

**Rule ID**: `new_artifact_without_precheck`  
**Category**: governance_discipline  
**Mode**: `dry_run` (48h auto-promote `warn`)  
**Author**: Maya Patel (Governance Engineer)  
**Date**: 2026-04-16  
**Status**: Spec complete, implementation deferred to next atomic  

---

## Purpose

Enforce Pre-Build Routing Gate discipline: sub-agents MUST run `python3 scripts/precheck_existing.py <component_name>` before creating NEW files in governance namespaces. Prevents duplication of existing Y*gov modules.

Upstream: `governance/pre_build_routing_gate_v1.md` spec  
Downstream: ForgetGuard LIVE enforcement (after 48h dry_run)

---

## Trigger Condition

**Violation detected when**:
1. Sub-agent uses Write tool to create NEW file (file does not exist before Write)
2. File path matches governance namespace:
   - `governance/` (ystar-company repo)
   - `Y-star-gov/ystar/governance/` (Y-star-gov repo)
   - `/ystar/governance/` (absolute path variant)
3. NO prior Bash call to `precheck_existing.py` in same atomic transcript

**Non-violation cases**:
- Write to existing file (Edit tool, not Write) → not NEW artifact
- Write to non-governance path (e.g., `scripts/`, `reports/`) → out of scope
- Precheck called BEFORE Write in same transcript → compliant

---

## Detector Implementation (≤40 lines)

```python
def detect_new_artifact_without_precheck(transcript: list[dict]) -> dict:
    """
    Scan sub-agent transcript for Write to governance namespace without prior precheck.

    Args:
        transcript: List of tool_use events with {tool, parameters, timestamp}

    Returns:
        {
            "violation_detected": bool,
            "governance_writes": list[str],  # File paths written
            "precheck_calls": list[str],     # Precheck commands run
            "rationale": str                 # Explanation
        }
    """
    GOVERNANCE_PATHS = [
        "governance/",
        "Y-star-gov/ystar/governance/",
        "/ystar/governance/"
    ]

    governance_writes = []
    precheck_calls = []

    for event in transcript:
        tool = event.get("tool", "")
        params = event.get("parameters", {})

        # Detect governance Write
        if tool == "Write":
            file_path = params.get("file_path", "")
            if any(p in file_path for p in GOVERNANCE_PATHS):
                governance_writes.append(file_path)

        # Detect precheck Bash call
        if tool == "Bash":
            command = params.get("command", "")
            if "precheck_existing.py" in command:
                precheck_calls.append(command)

    # Violation: governance Write without prior precheck
    violation = bool(governance_writes) and not bool(precheck_calls)

    rationale = ""
    if violation:
        rationale = f"Created {len(governance_writes)} governance file(s) without running precheck_existing.py: {governance_writes}"
    elif governance_writes and precheck_calls:
        rationale = f"Compliant: precheck run before {len(governance_writes)} governance write(s)"
    else:
        rationale = "No governance writes in this atomic"

    return {
        "violation_detected": violation,
        "governance_writes": governance_writes,
        "precheck_calls": precheck_calls,
        "rationale": rationale
    }
```

---

## Test Coverage (≥3 assertions)

### Test 1: Violation — Write without precheck

```python
def test_violation_write_without_precheck():
    transcript = [
        {
            "tool": "Write",
            "parameters": {"file_path": "governance/new_spec.md", "content": "..."},
            "timestamp": "2026-04-16T15:00:00Z"
        }
    ]
    result = detect_new_artifact_without_precheck(transcript)
    assert result["violation_detected"] is True
    assert len(result["governance_writes"]) == 1
    assert result["governance_writes"][0] == "governance/new_spec.md"
    assert len(result["precheck_calls"]) == 0
```

### Test 2: Compliant — Precheck before Write

```python
def test_compliant_precheck_before_write():
    transcript = [
        {
            "tool": "Bash",
            "parameters": {"command": "python3 scripts/precheck_existing.py new_spec"},
            "timestamp": "2026-04-16T14:59:00Z"
        },
        {
            "tool": "Write",
            "parameters": {"file_path": "governance/new_spec.md", "content": "..."},
            "timestamp": "2026-04-16T15:00:00Z"
        }
    ]
    result = detect_new_artifact_without_precheck(transcript)
    assert result["violation_detected"] is False
    assert len(result["governance_writes"]) == 1
    assert len(result["precheck_calls"]) == 1
```

### Test 3: No violation — Non-governance Write

```python
def test_no_violation_non_governance_write():
    transcript = [
        {
            "tool": "Write",
            "parameters": {"file_path": "scripts/util.py", "content": "..."},
            "timestamp": "2026-04-16T15:00:00Z"
        }
    ]
    result = detect_new_artifact_without_precheck(transcript)
    assert result["violation_detected"] is False
    assert len(result["governance_writes"]) == 0
```

### Test 4: Edge case — Y-star-gov repo path

```python
def test_ystar_gov_repo_path():
    transcript = [
        {
            "tool": "Write",
            "parameters": {"file_path": "/Users/user/Y-star-gov/ystar/governance/new_engine.py", "content": "..."},
            "timestamp": "2026-04-16T15:00:00Z"
        }
    ]
    result = detect_new_artifact_without_precheck(transcript)
    assert result["violation_detected"] is True
    assert len(result["governance_writes"]) == 1
```

---

## ForgetGuard YAML Entry (Implementation Target)

```yaml
new_artifact_without_precheck:
  description: "Sub-agent created NEW governance file without running precheck_existing.py"
  category: governance_discipline
  mode: dry_run  # Auto-promote to warn after 48h
  severity: medium
  detector: ystar.governance.forget_guard_detectors.new_artifact_without_precheck
  auto_promote:
    from: dry_run
    to: warn
    after_hours: 48
  rationale: |
    Enforce Pre-Build Routing Gate discipline. Sub-agents must check for existing
    components before creating new governance files to prevent duplication.
    
    Per governance/pre_build_routing_gate_v1.md (2026-04-16).
```

---

## Integration Points

1. **Sub-agent boot template**: Step 3 instructs precheck invocation (already added in CZL-118)
2. **Precheck script**: `scripts/precheck_existing.py` callable (already shipped in CZL-118)
3. **ForgetGuard detector**: Implementation deferred to next atomic (CZL-119 or similar)
4. **Test suite**: 4 test cases speced above, implementation deferred

---

## Success Criteria

**Spec complete (CZL-118)**: ✅ This file  
**Implementation (next atomic)**:
- Detector function in `Y-star-gov/ystar/governance/forget_guard_detectors.py`
- YAML entry in `Y-star-gov/ystar/governance/forget_guard_rules.yaml`
- 4 test cases in `tests/governance/test_new_artifact_without_precheck.py`
- All tests PASS

**L4 SHIPPED (after implementation)**:
- 48h dry_run window passed
- Auto-promote to `warn` mode
- 1+ real violation caught in wild

---

**END OF SPEC**
