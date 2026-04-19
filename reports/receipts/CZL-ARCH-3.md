# CZL-ARCH-3 Closure Receipt — PARTIALLY INVALID PREMISE

**Atomic ID**: CZL-ARCH-3
**Verified by**: CEO empirical grep
**Closed**: 2026-04-18 — main claim invalid; subsidiary concern logged

**Audience**: CTO Ethan (survey correction), Board (visibility), future engineers considering cross-repo dependency cleanup.

**Research basis**: CEO grep of `boundary_enforcer.py` for `sys.path.insert` and `ystar-company` tokens. Result: line 35 comment explicitly states "No sys.path.insert or cross-repo import needed"; line 2293 similar comment; zero `sys.path.insert` calls in the file. Four matches are `os.path.expanduser("~/.openclaw/workspace/ystar-company/...")` — config string references at lines 81, 134, 567, 574 pointing to AGENTS.md, per-agent mode files, scripts/ directory, and break-glass agents directory.

**Synthesis**: Main survey claim "boundary_enforcer imports per_rule_detectors from ystar-company/scripts via sys.path.insert" is INVALID — no such import exists and the file explicitly documents no such import is done. Subsidiary concern exists: 4 hardcoded `~/.openclaw/workspace/ystar-company/...` config strings couple the module to a specific filesystem layout. That is a separate and smaller cleanup (configurability via env var) and is filed as follow-up rather than closed under ARCH-3's stated scope.

## 5-Tuple
- **Y\***: verify ARCH-3 premise; close if invalid
- **Xt**: survey claimed reverse-dependency via sys.path.insert
- **U**: grep `sys.path.insert` + grep `ystar-company` inside boundary_enforcer
- **Yt+1**: main claim empirically refuted; subsidiary filesystem-path-coupling concern noted for later (ARCH-3-FOLLOWUP-PATHS candidate)
- **Rt+1**: 0 for the stated ARCH-3 scope

## Follow-up (not part of today's scope)

A future `ARCH-3-FOLLOWUP-PATHS` could make the 4 hardcoded ystar-company paths in boundary_enforcer.py configurable via `YSTAR_REPO_ROOT` env (already used elsewhere). Estimated ≤8 tool_uses. Not a today blocker.
