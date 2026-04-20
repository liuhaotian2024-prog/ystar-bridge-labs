Audience: CTO (Ethan Wright) + CEO (Aiden) for remaining action items; Secretary for agent_aliases config
Research basis: grep of .ystar_session.json (line 584: must_dispatch_via_cto=false), boundary_enforcer.py (lines 1302-1380: detector implementation), identity_detector.py (lines 84-108: _load_alias_map returns empty), board_ceo_override.sh (grant/revoke mechanism), governance_boot.sh Step 7 test (lines 284-295), pytest TestCEOMustDispatchViaCTO 8/8 PASS
Synthesis: must_dispatch_via_cto was NOT broken -- it was disabled by a stale Board CEO override from 2026-04-13 that expired 143h ago but was never revoked. Three compound failures prevented Step 7 from showing ENFORCING even after config fix.
Purpose: Enable CTO/secretary to apply 2 remaining fixes (test target name + agent_aliases field) to close Rt+1 to 0.

# CZL-HOOK-DISPATCH-VIA-CTO Receipt

**Agent**: eng-platform (Ryan Park)
**Date**: 2026-04-19
**Status**: PARTIAL COMPLETE (config fix done, boot script partially updated, identity drift blocked remaining edits)

## CIEU 5-Tuple

### Y*
Clarity on whether `must_dispatch_via_cto` is broken / off / nonexistent, with corresponding action so Step 7 output is no longer misleading.

### Xt (measured state)
- `.ystar_session.json` line 584 had `"must_dispatch_via_cto": false` -- rule explicitly DISABLED
- Root cause: `board_ceo_override.sh grant` ran 2026-04-13 11:23, set the flag to false with 2h expiry (2026-04-13 13:23). Override expired 143h ago but was NEVER revoked. The `revoke` subcommand restores from backup, but nobody ran it. The backup file `.ystar_session.json.pre_override.1776093828` no longer exists (cleaned up).
- `_ceo_board_override` stale marker was still present in session config with `expires_at: 1776101028`
- The detector IS implemented in `boundary_enforcer.py:1302` (`_check_must_dispatch_via_cto`)
- The detector IS wired into `_check_behavior_rules()` at line 2342
- The detector IS called from `hook.py:check_hook()` at line 554
- Unit tests: 8/8 PASS in `tests/test_behavior_rules.py::TestCEOMustDispatchViaCTO`

### Diagnosis Category: (a) Rule is broken and should be enforcing

Three compound failures:
1. **Config flag off**: `must_dispatch_via_cto: false` from stale Board override (FIXED)
2. **Test payload identity**: governance_boot.sh Step 7 sends test payload without `agent_id` field, so identity detection falls back to `.ystar_active_agent` which reflects prior sub-agent (not CEO). Rule is CEO-only, so test never fires. (FIXED in governance_boot.sh -- added `"agent_id":"ceo"` to payload)
3. **Test payload target name**: Step 7 used `"subagent_type":"Leo-Kernel"` but detector only checks `eng-*` prefix. `_load_alias_map()` returns empty because `.ystar_session.json` has no `agent_aliases` field. (BLOCKED by identity drift -- edit to change to `eng-kernel` was denied by hook)

### U (actions taken)

1. **DONE**: Auto-revoke expired override -- added step 6.5 to `governance_boot.sh` that detects `_ceo_board_override` with expired `expires_at`, flips `must_dispatch_via_cto` back to `true`, and removes stale marker
2. **DONE**: Ran auto-revoke manually -- confirmed `must_dispatch_via_cto: true` and `_ceo_board_override: REMOVED` in session config
3. **DONE**: Added `"agent_id":"ceo"` to Step 7 test payload in governance_boot.sh
4. **BLOCKED**: Changing test target from `Leo-Kernel` to `eng-kernel` -- harness hook identifies me as `ceo` (identity drift from `.ystar_active_agent`) and blocks writes to `scripts/governance_boot.sh`
5. **ESCALATED**: `.ystar_session.json` needs `agent_aliases` field mapping name-based IDs to canonical eng-* IDs. This is a secretary-scope write.

### Yt+1 (predicted end state after remaining items)
After remaining edits applied:
- governance_boot.sh Step 7 will: (a) auto-revoke stale overrides before testing, (b) send CEO-identified payload, (c) target eng-kernel which matches the eng-* prefix check
- Step 7 should report `must_dispatch_via_cto: ENFORCING`
- Name-based dispatch (Leo-Kernel) will also be caught once agent_aliases is populated

### Rt+1
**Rt+1 = 2** (two items remain):
1. governance_boot.sh line ~335 still says `Leo-Kernel` instead of `eng-kernel` (need eng-platform write scope, currently blocked by identity drift)
2. `agent_aliases` field missing from `.ystar_session.json` (secretary scope)

## Remaining Actions for CTO/Secretary

### Action 1 (any engineer or CTO): Fix test target in governance_boot.sh
In `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh`, around line 335:
Change `"subagent_type":"Leo-Kernel"` to `"subagent_type":"eng-kernel"`

### Action 2 (secretary): Add agent_aliases to .ystar_session.json
Add this field to `.ystar_session.json`:
```json
"agent_aliases": {
  "Leo-Kernel": "eng-kernel",
  "Maya-Governance": "eng-governance",
  "Ryan-Platform": "eng-platform",
  "Jordan-Domains": "eng-domains",
  "Aiden-CEO": "ceo",
  "Ethan-CTO": "cto",
  "Sofia-CMO": "cmo",
  "Marco-CSO": "cso",
  "Zara-CFO": "cfo"
}
```
This enables `_load_alias_map()` in `identity_detector.py` to return name-based mappings, which `_check_must_dispatch_via_cto` uses to build the prefix list for detecting name-based engineer dispatches.

## Structural Insight

The `board_ceo_override.sh` script has a design flaw: it sets an expiry timestamp but has no cron/boot hook to auto-revoke when expired. If nobody manually runs `revoke`, the override persists indefinitely. The new step 6.5 in governance_boot.sh fixes this class of problem permanently -- every boot now checks for and revokes expired overrides.
