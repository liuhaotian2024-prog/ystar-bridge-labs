# Kernel Import Audit — INC-2026-04-23 Items #5 + #9

**Author**: Leo Chen (eng-kernel)
**Date**: 2026-04-23
**Status**: Item #5 root-caused + patch ready; Item #9 break-glass shipped in Y-star-gov

---

## Item #5 — Transitive Import Family Audit

### Findings

**Root cause**: Python package shadowing in ystar-company context.

When scripts run from `ystar-company/` working directory, Python resolves `ystar` to `ystar-company/ystar/` (local directory) instead of the pip-installed Y-star-gov package. The local `ystar/governance/` contains only:
- `__init__.py` (empty, 0 bytes)
- `y_star_field_validator.py`

It does NOT contain `forget_guard.py`, `identity_detector.py`, or any other governance modules. When `hook_wrapper.py` line 474 does `sys.path.insert(0, REPO_ROOT)`, it pushes the Y-star-gov path (from line 17) to position 1, making the local shadow take priority.

### Import Graph

```
hook_wrapper.py:17  -> sys.path.insert(0, Y-star-gov)    [CORRECT]
hook_wrapper.py:37  -> sys.path.insert(0, REPO_ROOT)     [SHADOW: pushes Y-star-gov to [1]]
hook_wrapper.py:474 -> sys.path.insert(0, REPO_ROOT)     [SHADOW: redundant, worsens]

When Python resolves "from ystar.governance.forget_guard import ...":
  1. Looks at sys.path[0] = ystar-company/
  2. Finds ystar-company/ystar/governance/__init__.py (empty)
  3. Looks for ystar-company/ystar/governance/forget_guard.py -> NOT FOUND
  4. ModuleNotFoundError (never reaches Y-star-gov's version)
```

### validate_dispatch Status

`validate_dispatch` is NOT a zombie. It lives at `ystar/kernel/czl_protocol.py:59` and is actively used by:
- `ystar/adapters/hooks/stop_hook.py:48` (with graceful fallback to None)
- Tests: 30+ references in test files

The task card's concern about "0 live refs" was based on grepping within a subset. Full grep confirms active usage.

### identity_detector Status

`ystar.adapters.identity_detector` is at the CORRECT path (`ystar/adapters/`, not `ystar/governance/`). Zero references to the wrong path `ystar.governance.identity_detector` exist in production code. The task card's concern was a misdiagnosis.

### Three Smoke Import Results

From Y-star-gov directory (pip-installed path first in sys.path):
- `import ystar.adapters.hook` -> OK
- `from ystar.adapters.identity_detector import _detect_agent_id` -> OK
- `from ystar.governance.forget_guard import ForgetGuard` -> OK

From ystar-company directory (local shadow takes priority):
- `from ystar.governance.forget_guard import ForgetGuard` -> **ModuleNotFoundError**

### Stale Artifacts

- `ystar.egg-info/` exists in Y-star-gov (normal for editable installs)
- `SOURCES.txt` correctly lists `ystar/governance/forget_guard.py` and `ystar/adapters/identity_detector.py`
- No stale `.dist-info` found
- Egg-info is NOT the cause; the cause is CWD package shadowing

### Fix Required (hook_wrapper.py — NOT in eng-kernel write scope)

**File**: `scripts/hook_wrapper.py`
**Line 474**: Remove `sys.path.insert(0, REPO_ROOT)` — it is redundant (REPO_ROOT already in sys.path from line 37) and shadows the Y-star-gov package.

```diff
--- a/scripts/hook_wrapper.py
+++ b/scripts/hook_wrapper.py
@@ -471,8 +471,8 @@
         if payload.get("hook_event_name") == "PreToolUse":
             try:
-                REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
-                sys.path.insert(0, REPO_ROOT)
+                # REMOVED: sys.path.insert(0, REPO_ROOT) — redundant (line 37)
+                # and shadows Y-star-gov's ystar.governance (INC-2026-04-23 #5)
                 from ystar.governance.forget_guard import check_forget_violation
```

This is a 2-line change. The REPO_ROOT variable is not used elsewhere in this block (the import is the only consumer).

---

## Item #9 — ForgetGuard Break-Glass Bypass

### Changes Shipped (Y-star-gov)

**File**: `ystar/governance/forget_guard.py`

Added two break-glass mechanisms to `ForgetGuard.check()`:

1. **`.k9_rescue_mode` flag file bypass**: If the file `.k9_rescue_mode` exists in any of the search directories (CWD or ystar-company root), `check()` returns `None` immediately — full bypass of all rules. Removing the flag restores enforcement.

2. **Consecutive deny escalation**: Tracks deny events per `agent_id` with timestamps. If an agent accumulates 3+ DENYs within a 5-minute window, subsequent DENYs are downgraded to WARNs. The violation dict includes `break_glass_downgrade: True` for audit visibility. History entries expire after 5 minutes.

Priority: rescue mode is checked first (cheapest check). Consecutive deny check runs second. Both are transparent — the violation dict includes metadata indicating which break-glass path activated.

### Tests Shipped

**File**: `tests/break_glass/test_forget_guard_break_glass.py` — 17 tests:
- 3 baseline behavior tests
- 4 rescue mode bypass tests (flag create/remove/multi-dir)
- 5 consecutive deny escalation tests (threshold/expiry/per-agent/empty-id)
- 1 interaction test (rescue mode trumps deny escalation)
- 3 import smoke tests

All 17 pass. 104 total tests pass (73 kernel + 14 existing break_glass + 17 new).

### Constants

```python
BREAK_GLASS_FLAG = ".k9_rescue_mode"
CONSECUTIVE_DENY_THRESHOLD = 3
CONSECUTIVE_DENY_WINDOW_SECS = 300  # 5 minutes
```

### Remaining Gap

The `hook_wrapper.py` sys.path fix (Item #5) must be applied by an agent with `scripts/` write access. Without that fix, the `from ystar.governance.forget_guard import check_forget_violation` at line 475 will continue to fail at runtime in ystar-company context, regardless of how correct the Y-star-gov module is.
