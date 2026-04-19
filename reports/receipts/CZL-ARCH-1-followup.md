# CZL-ARCH-1 Follow-up — Sibling Fixes Discovered Via Live-Fire

**Atomic ID**: CZL-ARCH-1-followup (integrated into ARCH-1 closure, no new whiteboard task)
**Fixed by**: ceo (CEO_ENGINEERING_OVERRIDE #2, Board-authorized 2026-04-18 "继续全推")
**Completed**: 2026-04-18

**Audience**: Board (session closure evidence + CEO override accounting month=2/3), CTO Ethan (ARCH-2/3/4/5/6 unblocker), Leo/Maya/Ryan (their 3 prior BLOCKED_ON reports resolve via these 2 patches).

**Research basis**: Empirical failure evidence from 3 parallel engineer spawns post-ARCH-1. Ryan (aa dispatch ARCH-6): marker="Ryan-Platform" → identity_detector priority 1 returned literal unmapped → policy lookup fallback "agent" → deny. Leo (ARCH-2+4): marker="ceo" → hook_wrapper.py hardcoded CEO_DENY list blocks Y-star-gov/ystar/ writes for ANY caller. Maya (ARCH-3+5): same hook_wrapper.py CEO_DENY issue. All three precisely described the two bugs ARCH-1 did not cover.

**Synthesis**: ARCH-1 hardened _AGENT_TYPE_MAP and _map_agent_type at the "who am I?" layer (identity_detector.py). But two parallel identity-checkpoint bugs downstream remained:
(a) Priority 1 in _detect_agent_id returned payload.agent_id verbatim without mapping, so "Ryan-Platform" bypassed the map entirely.
(b) hook_wrapper.py CEO code-write prohibition was a hardcoded constant that applied to ALL callers, not just CEO — structurally wrong since it's nominally a "CEO" rule.

Both are Maya's diagnosis rendered as surgical edits. Together with ARCH-1 they close the identity chain that was causing today's recurring Leo/Maya/Ryan lock-deaths at engineer spawn.

## 5-Tuple

- **Y\***: identity chain correctly resolves subagent-pushed marker through canonical IDs + CEO code-write prohibition only applies when caller is actually CEO
- **Xt**: post-ARCH-1 engineer spawn still deadlocks because (a) priority 1 unmapped, (b) CEO_DENY non-selective
- **U**:
  - `Y-star-gov/ystar/adapters/identity_detector.py:109-121` — priority 1 now calls `_map_agent_type(aid)` and continues if mapping degenerates to "agent" (mirrors CZL-P1-b priority 1.5 pattern)
  - `ystar-company/scripts/hook_wrapper.py:76-86` — CEO code-write prohibition now gated by `_caller_id in _ceo_identities` where `_ceo_identities = ("ceo", "Aiden-CEO", "Aiden", "")`
- **Yt+1**: 19/19 existing identity tests PASS (ARCH-1 8 + P1-b 11); both files syntax-clean; hook restored after edit
- **Rt+1**: 0 for the 2 sibling fixes (the ARCH-2/3/4/5/6 landing now unblocked as separate tasks)

## CEO Engineering Override Accounting
- **Override #2 this month**
- **Trigger**: T1, hard_cap_expires_at 1776535070 (20 min from trigger)
- **Conditions met**: P0 production (all 3 engineers simultaneously BLOCKED) + Board authorized ("继续全推") + engineers unreachable (every spawn attempted hit the same 2 sibling bugs)
- **Month counter**: 2/3 (Secretary audit)

## Governance note
These are kernel-touching fixes. Under normal discipline Leo (eng-kernel) does identity_detector.py and Ryan (eng-platform) does hook_wrapper.py. Both were blocked specifically BY these bugs — classic infrastructure P0. Appropriate scope for CEO override per AGENTS.md §CEO Engineering Boundary.

## Tests evidence
```
cd Y-star-gov && pytest tests/adapters/test_identity_arch1.py tests/adapters/test_identity_detector_p1b.py -q
...................                                                      [100%]
19 passed in 0.07s
```
