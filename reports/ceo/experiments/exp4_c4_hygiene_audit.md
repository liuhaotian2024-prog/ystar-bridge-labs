---
Phase: C4 — Cross-Repo License & Name Hygiene Audit
Date: 2026-04-19
Author: eng-platform (Ryan Park)
Purpose: Ensure Y*gov product repo has zero Labs-specific name leaks
---

# C4: Name & License Hygiene Audit

## Scan Command
```bash
grep -rnE "(ystar-company|Aiden|Ethan|Leo Chen|Maya Patel|Ryan Park|Jordan Lee)" ystar/ --include="*.py"
```

## Findings

### Category 1: "ystar-company" hardcoded paths (HIGH — product should not reference company repo)

| File | Line | Context | Severity |
|------|------|---------|----------|
| `ystar/cli/safemode_cmd.py` | 31 | `~/.openclaw/workspace/ystar-company/.ystar_cieu.db` | HIGH |
| `ystar/cli/safemode_cmd.py` | 193 | `~/.openclaw/workspace/ystar-company/.ystar_session.json` | HIGH |
| `ystar/adapters/activation_triggers.py` | 322-323 | `workspace/ystar-company` path resolution | HIGH |
| `ystar/capabilities.py` | 86 | `~/.openclaw/workspace/ystar-company/.ystar_session.json` | HIGH |
| `ystar/governance/narrative_coherence_detector.py` | 479 | sys.path insert for ystar-company | MEDIUM |
| `ystar/governance/enforcement_observer.py` | 34,320,323,325 | Governance file scan roots ystar-company | HIGH |
| `ystar/governance/charter_drift.py` | 46,65,66 | Workspace root inference via ystar-company | HIGH |
| `ystar/governance/boundary_enforcer.py` | 69 | Session JSON path ystar-company | HIGH |
| `ystar/governance/cieu_brain_streamer.py` | 36 | os.path.join for ystar-company | HIGH |
| `ystar/governance/stuck_claim_watchdog.py` | 22-24 | 3x absolute paths `/Users/haotianliu/.openclaw/workspace/ystar-company/` | CRITICAL |
| `ystar/governance/omission_engine.py` | 2220,2252,2319,2411 | Labs root references | HIGH |
| `ystar/governance/k9_routing_subscriber.py` | 219,254,300,401 | 4x ystar-company path references | HIGH |
| `ystar/governance/liveness_audit.py` | 199-201 | 3x absolute paths with `/Users/haotianliu/` | CRITICAL |
| `ystar/governance/obligation_remediation.py` | 41 | sys.path insert ystar-company | MEDIUM |
| `ystar/rules/per_rule_detectors.py` | 6,10 | Comment references to ystar-company | LOW |
| `ystar/kernel/rt_measurement.py` | 36,38 | sys.path insert ystar-company | HIGH |

**Total: 30+ occurrences across 16 files**

### Category 2: Agent persona names (should not appear in product code)

No occurrences of "Aiden", "Ethan", "Leo Chen", "Maya Patel", "Ryan Park", or "Jordan Lee" were found in the `ystar/` Python source. The CZL-REFACTOR-LABS-NAMES cleanup successfully removed agent names from product code.

### Category 3: Absolute user paths (CRITICAL for portability)

| File | Pattern | Severity |
|------|---------|----------|
| `ystar/governance/stuck_claim_watchdog.py` | `/Users/haotianliu/.openclaw/workspace/ystar-company/` | CRITICAL |
| `ystar/governance/liveness_audit.py` | `/Users/haotianliu/.openclaw/workspace/ystar-company/` | CRITICAL |

These are hardcoded to a specific user's home directory and will break for any other user.

## License Check

- Y*gov: MIT License (confirmed in repo)
- No AGPL-3.0 (K9Audit) code copied into Y*gov source
- No license header violations detected

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| "ystar-company" path refs | 30+ | HIGH-CRITICAL |
| Agent persona name leaks | 0 | CLEAN |
| Absolute user paths | 6 | CRITICAL |
| License violations | 0 | CLEAN |

## Recommended Fix

All "ystar-company" references should be replaced with:
1. Environment variable `YSTAR_WORKSPACE` or `YSTAR_COMPANY_ROOT`
2. XDG-compliant config discovery: `~/.config/ystar/workspace.toml`
3. Runtime detection via `ystar.config.get_workspace_root()` function

The absolute `/Users/haotianliu/` paths must be converted to `os.path.expanduser("~")` or removed entirely.

**This is the single largest portability blocker for external adoption.**
