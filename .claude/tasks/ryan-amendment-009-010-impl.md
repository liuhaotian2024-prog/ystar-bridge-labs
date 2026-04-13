# TASK: Ryan-Platform — AMENDMENT-009 + 010 Full Implementation

**Dispatcher**: CTO (Ethan Wright)
**Target**: eng-platform (Ryan Park)
**Task ID**: AMENDMENT-009-010-IMPL-ryan-2026-04-12
**Obligation ID**: 76859b2c-f65a-4189-9bf3-a4c792a32e79
**Acknowledge Due**: 2026-04-12 +15min
**Channel**: agent_tool
**Dispatched By**: Board direct order → CEO (Aiden) → CTO (Ethan) → Ryan-Platform
**Routing Rule**: hook `must_dispatch_via_cto` (CEO cannot dispatch directly to engineers)

---

## Mandatory Pre-Read (in order)

1. `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/boot_packages/eng-platform.json` — full boot pack, authoritative action queue in `category_11_next_session_action_queue`
2. `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/dispatches/ryan_amendment_009_impl_6pager_v2.md` — implementation 6-pager
3. `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/proposals/charter_amendment_009_priority_brief_tombstone_escape_hatch.md` — AMENDMENT-009 spec
4. `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/proposals/charter_amendment_010_secretary_curation_charter_and_11_category_boot_contract.md` — AMENDMENT-010 spec

## Execution Contract

- **Order**: Seq 1 → 15 strictly. No reordering.
- **Partial-Execution Protocol** (§6 Q6 of the 6-pager):
  - Exit 0 = all 15 green
  - Exit 1 = partial (some DONE, some FAIL) — report which and why
  - Exit 2 = pre-requisite failure (can't even start)
  - Exit 3 = brief fact-check failure (6-pager contradicts boot pack or charter)
- **On any hook DENY**: STOP immediately. Report to CTO. DO NOT bypass (no `chmod +x` on hooks, no `sudo`, no `--no-verify`, no disabling governance_boot).
- **Seq 9** (MCP tools in `gov-mcp/src/`): this is Kernel territory. Ryan escalates to Leo-Kernel via CTO (Ethan). Do not touch gov-mcp/src/ directly.
- **Git**: commit locally, **do not push**. External release is Board's decision.

## Required Report Back to CTO

1. Per-seq status (1-15): DONE / FAIL / SKIPPED (with reason)
2. CIEU record counts per seq (from gov_audit queries)
3. Final commit hash (single squashed commit preferred, or commit range)
4. Verification output for seq 11 (full stdout/stderr)
5. Any hook DENY events encountered (full denial record)
6. Whether seq 9 triggered Leo-Kernel escalation
7. Exit code per partial-execution protocol

## Governance

- Delegation chain: CEO → CTO → eng-platform (depth 2) — registered
- Hook rules still apply to Ryan (reads `.ystar_session.json` 193 constraints)
- Any write outside `ystar-company/` or `Y-star-gov/` is out of scope — escalate
