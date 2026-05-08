# E93.1 — Removing the Shadow `gov_mcp/` Package from bridge-labs

## What was removed
Nine files at `<bridge-labs>/gov_mcp/`:
- `__init__.py` (empty marker)
- `__main__.py`
- `benchmark.py`
- `exec_whitelist.yaml`
- `health.py`
- `router.py`
- `server.py` (~43KB)
- `whitelist_unix.yaml`
- `whitelist_windows.yaml`

These were a frozen snapshot from 2026-04-30 of an older gov-mcp internal
state that lived inside the bridge-labs repo. They duplicated content that
already lives at the canonical `gov-mcp` repo (`~/.openclaw/workspace/gov-mcp`).

## Why this caused E93 to fail on owner's Mac
When `e93_brain_grounded_live_runtime.run_e93_brain_grounded_runtime_session()`
called `importlib.import_module("gov_mcp.outbound.dry_run_adapter")`, Python's
import machinery resolved `gov_mcp` to the SHADOW directory in bridge-labs
because it appeared earlier in `sys.path` than the real gov-mcp.

The shadow had no `outbound/` subpackage, so the `outbound.dry_run_adapter`
import failed with `ModuleNotFoundError: No module named 'gov_mcp.outbound'`
even though the real adapter module exists at
`<gov-mcp>/gov_mcp/outbound/dry_run_adapter.py`.

E89's "Fixed bridge-labs gov-mcp package shadowing" report referred to a
sys.path-ordering workaround in tests, NOT a removal. The shadow files
remained in the repo and continued to break import resolution under
PYTHONPATH-based execution paths.

## Verification before removal
Repository-wide grep showed that `from gov_mcp.outbound.*` and
`import gov_mcp.outbound.*` are used only in:
- `office/mission_command/e22_gov_mcp_dry_run_integration.py`
- `office/mission_command/e93_brain_grounded_live_runtime.py`
- (test files for the above)

All other `gov_mcp.*` imports in the repo are for `server`, `router`,
`benchmark`, `health`, `runtime_linkage_tools`, `company_runtime_tools`,
`plugin_tools`, `cli`, `dispatch_logic` — every one of these names also
exists in the real gov-mcp repo with equal or greater coverage. None of
those imports require the shadow.

## Effect after removal
- `gov_mcp.outbound.dry_run_adapter` resolves to real gov-mcp.
- `gov_mcp.server`, `gov_mcp.router`, etc. continue to resolve to real
  gov-mcp via the existing `_add_sibling_repos` helpers.
- E22 and E93 sessions complete the full pre→dry-run→post chain end-to-end.
- No external action executed; no customer/revenue/payment claim made.

## Verified by owner
On 2026-05-08, owner ran E93 end-to-end after `mv gov_mcp gov_mcp.shadow_DISABLED`
and observed:
- `decision chain: ALLOW / ALLOW / ALLOW`
- `chain proven: True`
- `brain unique nodes activated: 20`
- `CIEU events written: 3`
- `merkle root: c001dbce0610c1a0719301920f8c3de5d2ad996183db57df64ae2c71048d923f`

This commit makes the fix permanent: the shadow is removed from version
control rather than depending on a local mv.
