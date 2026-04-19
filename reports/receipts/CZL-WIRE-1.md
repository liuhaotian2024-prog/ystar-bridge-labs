# CZL-WIRE-1 Completion Receipt — register_next_action_rule() caller

**Atomic ID**: CZL-WIRE-1
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18 (17 tool_uses / 474s / 1/1 test)

**Audience**: Board (Goal 2 "不空转" final wire so router rule actually fires in live traffic), CTO Ethan (ARCH-11 series final integration brick).

**Research basis**: After ARCH-8 landed the next_action_inject RouterRule module, empirical audit showed `register_next_action_rule()` had ZERO callers — rule module existed but never joined the live registry. Precedent pattern: break_glass rule was already similarly registered in `handle_hook_event`.

**Synthesis**: Add 4 lines (try/import/call/except) to `handle_hook_event` in hook.py, between the break_glass block and per_rule_detectors block, using the identical defensive pattern. Test clears the rule from registry, calls handle_hook_event, asserts re-registration.

## 5-Tuple
- **Y\***: next_action_inject rule actually registers into registry when hook boots; Goal 2 module stops being a dead file
- **Xt**: Module existed + tested + registered function but zero caller → Goal 2 Rt+1 half-open
- **U**: `Y-star-gov/ystar/adapters/hook.py:2010-2013` — 4 lines (try / import / call / except-pass) + `Y-star-gov/tests/rules/test_next_action_wire.py` — 1 test
- **Yt+1**: 1/1 test PASS; registry contains `builtin.next_action_inject` after handle_hook_event call
- **Rt+1**: 0 for Goal 2 wiring closure (live-traffic requires `YSTAR_HOOK_V2=1` env, which is ARCH-6 feature-flag operational decision)
