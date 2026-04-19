# CZL-P2-c PAUSED — Board Directive 2026-04-18

**Atomic ID**: CZL-P2-c
**Claimed by**: eng-governance (Maya Patel)
**Status**: BLOCKED_ON CZL-ARCH review pending
**Pause directive**: Board 2026-04-18 — stop all Phase 2 engineering work pending CTO architecture review

---

## Audience

Future engineer resuming CZL-P2-c after CTO architecture review unblocks it.

## Research — Files Read / Context Gathered

### Task Definition
- `governance/dispatch_board.json` — CZL-P2-c entry: "Dispatch workflow -> enforce AUTO_POST"
- `reports/ceo/enforce_as_router_migration_plan_20260418.md` — architectural context for enforce-as-router refactor

### Dependency Chain
- **CZL-P2-a** (COMPLETED): EnforceDecision expanded with INVOKE/INJECT/AUTO_POST; `router_registry.py` API skeleton with RouterRule/RouterResult/RouterRegistry landed
- **CZL-P2-b** (ALSO PAUSED, claimed by eng-governance): Session Boot -> enforce router migration; same blocker
- **CZL-P2-c** depends on P2-a API (completed) but Board paused before any P2-c code was written

### Scope Files (not yet modified)
- `scripts/dispatch_board.py` — existing dispatch CLI
- `scripts/cto_dispatch_broker.py` — CTO broker logic
- `scripts/engineer_task_subscriber.py` — engineer task subscriber
- `Y-star-gov/ystar/governance/router_registry.py` — P2-a API (target for new rule registration)

### Implementation Plan (not started)
Per task card: write a RouterRule with:
- **detector**: match CEO Bash calls containing dispatch/assign intent OR Agent tool calls with eng-* subagent_type
- **executor**: AUTO_POST task card to dispatch_board
- Goal: CEO says "Leo go fix X" and enforce auto-posts whiteboard task without manual CLI

### Code Written
None. Task was claimed but no implementation started before Board pause.

## Synthesis — Pause Reason + Resume Guidance

### Why Paused
Board directive 2026-04-18: all Phase 2 engineering work stopped pending CTO architecture review (task a00cd8a6596785e9b). The concern is that P2 work may proceed on incorrect architectural assumptions before CTO validates the enforce-as-router design.

### Resume Guidance
1. Wait for CTO architecture review completion (task a00cd8a6596785e9b)
2. Check if `router_registry.py` API changed during review — P2-c depends on `RouterRule`, `RouterRegistry.register()`, `RouterResult` with `AUTO_POST` decision
3. The implementation is straightforward once unblocked: ~15 tool_uses to write detector + executor + register rule + tests
4. Also unblock CZL-P2-b (session boot migration) which has the same blocker

### Sibling Tasks Also Blocked
- CZL-P2-b (eng-governance): Session Boot -> enforce router
- CZL-P2-d (ryan-platform): Batch protocol -> enforce router rules
- CZL-P2-e (eng-kernel): Drift live-fire test suite (depends on P2-b/c/d)
