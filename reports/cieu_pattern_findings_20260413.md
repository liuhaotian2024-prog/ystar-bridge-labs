# CIEU Pattern Findings — 21,378 Events Mined
**Date**: 2026-04-13
**Source**: `.ystar_cieu.db`
**Author**: CEO (live mining, no sub-agent)

---

## Smoking Gun #1: 480/480/480/480 Lockstep — Omission Rules Are Schedule-Triggered, Not Behavior-Triggered

```
omission_violation:intent_declaration          480
omission_violation:directive_acknowledgement   480
omission_violation:progress_update             480
omission_violation:task_completion_report      469  (~480)
omission_violation:required_acknowledgement_omission  502
```

Equal-count signature = these rules fire on a timer/loop, not on actual missing acknowledgements. This is the **root cause of Circuit Breaker ARMED 1844** noise documented in priority_brief P0-1 #3.

**Ticket**: Audit `governance/omission_rules.yaml` (or equivalent) — find the loop firing these rules and gate on "agent currently active" + "actually missing the artifact" instead of "time elapsed".
**Owner**: Maya-Governance
**ETA**: 2h
**Acceptance**: 24h after fix, the 4 omission counts diverge naturally; breaker doesn't ARM on formal-only violations.

---

## Smoking Gun #2: 1651 OFF_TARGET_WARNING — CEO Is "Off-Target" Constantly Per Heartbeat

CEO has 4795 total events; 1651 OFF_TARGET = **34% of CEO actions flagged off priority_brief targets**. Two possibilities:
1. CEO genuinely drifts a lot (wouldn't survive 1651 incidents)
2. `ceo_heartbeat.py` matcher is too strict — flags any CEO action whose verb doesn't lexically match a today_target line

Hypothesis (2) likely: heartbeat probably greps for exact target keywords; CEO's actual work uses paraphrasing.

**Ticket**: Soften matcher in `scripts/ceo_heartbeat.py:parse_priority_brief_targets` — use semantic distance (cosine on cached Gemma embeddings) instead of substring match. Threshold 0.5 OFF, 0.7 ON.
**Owner**: Ryan-Platform
**ETA**: 90min
**Acceptance**: After fix, OFF_TARGET rate drops below 10% on CEO event stream during normal session.

---

## Smoking Gun #3: 205 identity_violation Drift Events

Hard evidence the 6-lock incident pattern (`.ystar_active_agent` desync) is repetitive, not new. AMENDMENT-016 6-pager Appendix B is correct on motivation strength.

**No new ticket** — already covered by AMENDMENT-016 + Maya exp7 experiment in flight.

---

## Smoking Gun #4: Decision Distribution
- allow: 11,456 (54%)
- info: 3,774 (18%)
- escalate: 3,464 (16%)
- deny: 1,526 (7%)
- warn/warning: 226 (1%)

**16% escalate rate is high** for an autonomous system — should be <5%. Means agents constantly hit "I don't know what to do" walls. Likely related to AMENDMENT-012 (deny-as-teaching) + AMENDMENT-013 (proactive activation) — which both address compliance_recipe gaps.

**No new ticket** — both amendments queued for Board batch review (`reports/board_amendment_batch_review_20260413.md`).

---

## Agent Activity Ranking
1. ceo (4795) — highest, expected
2. eng-platform (2564)
3. eng-governance (2381)
4. "agent" (2276) — generic untagged events; **Ticket** to Ryan: trace where these come from
5. cto (1925)
6. eng-domains (1772)
7. secretary (1541) — surprisingly active given identity-lock issues
8. orchestrator (1359)
9. "" empty (942) — **Ticket**: trace empty agent_id source
10. path_a_agent (915)

**Ticket**: 942 events with empty `agent_id` + 2276 with generic `"agent"` = ~15% of CIEU events untagged. Find emit sites and add proper agent_id.
**Owner**: Ryan-Platform
**ETA**: 60min
**Acceptance**: New events 100% have specific agent_id; backfill historical with best-effort heuristic.

---

## Action Summary

| # | Ticket | Owner | ETA | Priority |
|---|---|---|---|---|
| 1 | Omission rules timer→behavior gating | Maya | 2h | P0 |
| 2 | OFF_TARGET semantic matcher | Ryan | 90min | P1 |
| 3 | Untagged agent_id backfill | Ryan | 60min | P2 |

All 3 to be picked up after current sub-agent sprints end.
