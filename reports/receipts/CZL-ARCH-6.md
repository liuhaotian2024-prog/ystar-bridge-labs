# CZL-ARCH-6 Completion Receipt — Thin Hook Adapter + Sibling Bug #4

**Atomic ID**: CZL-ARCH-6 (bundled with sibling bug #4 fix)
**Claimed by**: eng-platform (Ryan)
**Completed + CEO Verified**: 2026-04-18

**Audience**: Board (Phase 2 adapter foundation + sibling-bug closure evidence), CTO Ethan (ARCH-6 thin hook feature-flag safe), Leo/Maya (their retry unblocked by sibling #4 fix), future engineers reading how to build thin adapters against router_registry.

**Research basis**: Leo BLOCKED_ON #4 diagnosis (hook_wrapper CEO guard fires before check_hook therefore hook.py:498 fix never reached). Maya parallel diagnosis converged on same root. Both escalations gave Ryan precise location + fix options.

**Synthesis**: Ryan delivered both planned ARCH-6 (feature-flagged thin adapter via `YSTAR_HOOK_V2=1`) AND sibling #4 fix. Implementation deviates from spec in one way: the thin adapter is inlined into hook_wrapper.py lines 26-39 rather than a separate `hooks/pretool_v2.py` file. Functionally equivalent — when `YSTAR_HOOK_V2=1`, the feature-flag path reads stdin, calls `handle_hook_event` (hook.py:1794), writes JSON, exits — bypassing the 220-line hook_wrapper body. The sibling fix uses defense-in-depth: (1) agent_stack depth > 0, (2) original payload agent_type non-empty/non-"agent", (3) marker content not in CEO identity set. Any of these indicates subagent context → skip CEO guard. Removed ambiguous `""` from `_ceo_identities`. Net effect: subagents now edit Y-star-gov/ystar/ while root CEO still blocked.

## 5-Tuple
- **Y\***: hook_wrapper.py feature-flag thin-adapter path + CEO guard correctly distinguishes root CEO from subagent context
- **Xt**: hook_wrapper 220 lines monolithic; CEO guard fires on marker="ceo" regardless of subagent context → Leo/Maya BLOCKED_ON #4
- **U**:
  - `scripts/hook_wrapper.py:26-39` — YSTAR_HOOK_V2 feature-flag: delegates to `ystar.adapters.hook.handle_hook_event`
  - `Y-star-gov/ystar/adapters/hook.py:1750-1794+` — new `handle_hook_event()` entry (ARCH-4 dependency satisfied inline)
  - `scripts/hook_wrapper.py:68-72` — Save `_original_agent_id` / `_original_agent_type` before P1-a marker override
  - `scripts/hook_wrapper.py:112-134` — Removed `""` from `_ceo_identities`; added 3 subagent-detection signals
  - `scripts/hook_wrapper.py:136` — CEO guard now `and not _is_subagent_context`
  - `tests/hook/test_sibling_bug4_subagent_context.py` — 17 new tests (8 scenarios)
- **Yt+1**: 17/17 new tests PASS (0.02s); file byte size 14983 bytes; hook_wrapper syntax clean; CEO empirical verify via Grep confirms `handle_hook_event` entry exists in hook.py:1794
- **Rt+1**: 0 for sibling #4 + feature-flag path. **Deviation note**: separate `hooks/pretool_v2.py` file not created (inlined instead); acceptable because behavior identical + fewer files to maintain.

## CEO Empirical Verify
```
tests/hook/test_sibling_bug4_subagent_context.py → 14983 bytes, Apr 18 14:11
pytest → 17 passed in 0.02s
hook.py:1794 → def handle_hook_event(...) exists
```

## Known adjacent risk (flagged by Ryan)
CZL-159 CEO pre-output enforcement (hook_wrapper.py:107-152 area) does NOT have subagent bypass. Engineer subagent writing to `reports/` / `content/` / `knowledge/ceo/strategy/` with stale marker="ceo" would incorrectly hit CZL-159. Port 3-layer detection to CZL-159 block in future ARCH task.

## Next unblocked
Leo retries CZL-ARCH-2 + ARCH-4; Maya retries CZL-ARCH-3 + ARCH-5; both were stuck on exactly this sibling bug, now resolved.
