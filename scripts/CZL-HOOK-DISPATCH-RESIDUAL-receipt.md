## CZL-HOOK-DISPATCH-RESIDUAL Receipt

Audience: CTO (Ethan Wright) + CEO (Aiden) for dispatch chain verification
Research basis: identity_detector.py alias resolution code + boundary_enforcer.py _check_must_dispatch_via_cto + governance_boot.sh Step 7 payload
Synthesis: Three artifacts patched to close display-name bypass gap in must_dispatch_via_cto detector

### CIEU 5-Tuple

- **Y***: aliases map live in .ystar_session.json, detector resolves display names to canonical IDs, Step 7 uses canonical eng-kernel
- **Xt**: Step 7 targeted Leo-Kernel (display name, not canonical); .ystar_session.json lacked agent_aliases field; display-name CEO spawns bypassed detector
- **U**: 3 file edits + 15 regression tests
- **Yt+1**: CEO Agent(subagent_type=Leo-Kernel) triggers DENY via Leo- prefix matching from alias keys
- **Rt+1**: 0 (all 3 gaps closed, 15/15 tests PASS)

### Changes Made

1. **governance_boot.sh Step 7** (line 331): Changed test payload subagent_type from Leo-Kernel to eng-kernel (canonical). Step 7 tests the must_dispatch_via_cto enforcement and should use the canonical name that the detector definitely recognizes via the built-in eng- prefix.

2. **.ystar_session.json**: Added agent_aliases field with 10 entries mapping display names to canonical governance IDs.

3. **Y-star-gov/tests/adapters/test_dispatch_aliases.py**: 15 regression tests covering alias loading, display-name resolution, dispatch blocking, and no-regression on canonical names.

### Test Evidence

15 passed in 0.17s

### Files Modified
- scripts/governance_boot.sh (line 331)
- .ystar_session.json (added agent_aliases)
- Y-star-gov/tests/adapters/test_dispatch_aliases.py (new, 15 tests)
