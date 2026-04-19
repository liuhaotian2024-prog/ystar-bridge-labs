# CZL-ARCH-8 Completion Receipt — NEXT_ACTION Router Rule (Goal 2)

**Atomic ID**: CZL-ARCH-8
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18 (10 tool_uses / 594s / 8/8 tests)

**Audience**: Board (Goal 2 "不空转" evidence), CTO Ethan (router registry integration), all agents (future recipient of auto NEXT hints).

**Research basis**: CEO demonstrator `reports/ceo/demonstrators/goal_2_next_action_inject_pattern.py` + router_registry API (RouterRule, RouterResult, get_default_registry). Ethan arch doc Part B maps NEXT_ACTION inject as the core Goal 2 mechanism.

**Synthesis**: Rule priority 50 (advisory tier — runs low priority, does not interfere with allow/deny). Detector matches Bash/Edit/Write with decision=allow. Executor reads dispatch_board.json, returns decision="inject" with NEXT hint for claimed/open tasks matching the agent, or decision="allow" (no-op) when nothing to surface. Registration via `register_next_action_rule()`.

## 5-Tuple
- **Y\***: Agent allow decision carries NEXT_ACTION hint automatically; agent no longer needs to remember to query dispatch_board
- **Xt**: OmissionEngine was detector-only, never pushed next-step hints; agent had to self-query
- **U**: 
  - `Y-star-gov/ystar/rules/next_action_inject.py` — the router rule
  - `Y-star-gov/tests/rules/test_next_action_inject.py` — 8 tests (3 classes: detector / executor / registry integration)
  - `Y-star-gov/tests/rules/__init__.py` — package init
- **Yt+1**: 8/8 new tests PASS in 0.08s; rule `builtin.next_action_inject` registered at priority 50; find_matching_rules hits it
- **Rt+1**: 0 for Goal 2 core closure
