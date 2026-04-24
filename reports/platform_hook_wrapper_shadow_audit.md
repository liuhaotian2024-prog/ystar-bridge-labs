Audience: CTO (Ethan Wright) and CEO (Aiden) for prioritization of line 37 fix and shadow directory removal
Research basis: Empirical sys.path shadow test on ystar-company/ystar/ directory; Leo Chen kernel_import_audit_20260423.md Item #5 + #9
Synthesis: Line 37 has identical shadow bug as patched line 474; CIEU Layer 1 audit silently drops; fix is zero-regression removal
Purpose: Enable CTO to schedule line 37 fix + shadow directory cleanup as follow-up task

# Platform Audit: hook_wrapper.py Line 37 Shadow sys.path

**Date**: 2026-04-23
**Author**: eng-platform (Jordan Lee)
**Ref**: reports/kernel_import_audit_20260423.md (Leo Chen, Item #5 + #9)

## Context

Mission 1 patched lines 473-474 (ForgetGuard wire block) by removing the redundant `sys.path.insert(0, REPO_ROOT)`. This audit examines line 37, which has the identical pattern.

## Line 37 Analysis

```python
# Layer 1: CIEU
try:
    REPO_ROOT = os.path.dirname(os.path.dirname(__file__))  # line 36
    sys.path.insert(0, REPO_ROOT)                           # line 37
    from ystar.governance.cieu_store import CIEUStore       # line 38
```

### Shadow directory contents (empirical)

```
ystar-company/ystar/
  __init__.py
  __pycache__/
  governance/
    __init__.py
    y_star_field_validator.py
```

No `cieu_store.py` exists in the shadow. Therefore `from ystar.governance.cieu_store import CIEUStore` will always fail when the shadow is at `sys.path[0]`, because Python resolves `ystar` to the shadow package first, finds no `cieu_store` submodule, and raises `ImportError`.

### Empirical verification

```
$ python3 -c "import sys; sys.path.insert(0, '.../ystar-company'); from ystar.governance.cieu_store import CIEUStore"
-> ImportError: No module named 'ystar.governance.cieu_store'
```

### Impact assessment

Line 37's import is wrapped in a `try/except` (the CIEU triple-layer logging function). When the CIEUStore import fails, execution falls through to Layer 2 (JSONL structured log) and Layer 3 (stderr). This means:

- **CIEU audit records from hook_wrapper are silently lost** (Layer 1 never fires)
- The hook still functions (Layers 2+3 catch the fallthrough)
- No governance enforcement is blocked (unlike the ForgetGuard case)

### Recommendation

**Same fix as Mission 1**: remove lines 36-37's `REPO_ROOT` + `sys.path.insert(0, REPO_ROOT)`. The real Y-star-gov package should already be on `sys.path` via pip install or a prior path setup. However, per CEO scope guard, this audit is informational only -- the fix should be applied as a separate tracked task after Mission 1 is verified stable.

**Risk of NOT fixing**: CIEU Layer 1 audit records from hook events continue to silently drop. This is an M-2a gap (governance audit trail incomplete).

**Risk of fixing**: If Y-star-gov is not properly installed (pip) and no other `sys.path` entry points to it, removing line 37 would cause the same `ImportError` but that is already the current behavior (shadow blocks the import anyway). Net risk: zero regression.

### Additional finding: the shadow ystar/ directory itself

The real root cause is `ystar-company/ystar/` existing at all. It contains only a `y_star_field_validator.py` and empty `__init__.py` files. This directory shadows the real `ystar` package from Y-star-gov whenever `ystar-company/` is on `sys.path`. Deleting or renaming this shadow directory would fix all current and future shadow import issues at the source. This is outside eng-platform scope (requires CTO decision on directory structure).

## Status

- Mission 1 patch: APPLIED, commit 1b554c1b, smoke PASS
- Line 37 fix: RECOMMENDED, not applied (audit only per CEO scope guard)
- Shadow directory removal: RECOMMENDED for CTO review
