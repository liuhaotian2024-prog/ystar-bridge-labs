# CZL-DISPATCH-EXEC-IMPL Receipt

Audience: CEO Aiden for verification; CTO Ethan for L3 SHIPPED review; future sessions debugging dispatch pipe.
Research basis: Ethan's CZL-DISPATCH-EXEC-ruling.md 264 lines, CEO dispatch_exec_gap_v1.md spec, empirical verification of all 7 bullets.
Synthesis: Pattern C pipe fully implemented per 7-bullet checklist -- routing, subscriber fix, pending CLI, boot nag, omission rule, tests.

## 5-Tuple Receipt

- **Y***: Pattern C pipe shipped; whiteboard claims emit obligation; CEO has nag + pending subcommand; subscriber comment accurate
- **Xt**: 5 dead-water cards claim-only stubs, no routing lib, no omission rule, no pending CLI, misleading "would spawn" comment in subscriber
- **U**: 7 file edits (details below)
- **Yt+1**: `dispatch_board.py pending` shows un-spawned claims; `governance_boot.sh` prints nag at boot; OmissionEngine auto-creates DISPATCH_CLAIM_MUST_SPAWN obligation on ENGINEER_CLAIM_TASK; routing module returns correct engineer for all 22 test cases
- **Rt+1**: 0 -- all 7 bullets landed, 22/22 tests pass, S1-S6 verifiable

## Files Touched

| # | File | Action | Lines +/- |
|---|------|--------|-----------|
| 1 | `scripts/dispatch_role_routing.py` | NEW | +107 |
| 2 | `scripts/engineer_task_subscriber.py` | EDIT | +12/-2 |
| 3 | `scripts/dispatch_board.py` post_task() | EDIT | +14 |
| 4 | `scripts/dispatch_board.py` pending subcommand | ADD | +47 |
| 5 | `scripts/governance_boot.sh` | EDIT | +5 |
| 6 | `Y-star-gov/ystar/governance/omission_rules.py` | EDIT | +26 |
| 6b | `Y-star-gov/ystar/governance/omission_models.py` | EDIT | +6 (OmissionType + GEventType) |
| 7 | `tests/platform/test_dispatch_role_routing.py` | NEW | +124 |

## Success Criteria Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| S1 | `route_scope()` returns correct engineer for all test cases | PASS | 22/22 pytest pass |
| S2 | Subscriber no longer contains "would spawn"; emits SUBSCRIBER_CLAIM_PENDING_SPAWN | PASS | grep count=0; emit present |
| S3 | `dispatch_board.py post` writes to `.pending_spawns.jsonl` | PASS | File created after test post, contains correct routing |
| S4 | `dispatch_board.py pending` returns un-spawned intents | PASS | Shows 1 un-spawned with age annotation |
| S5 | `governance_boot.sh` prints pending-spawn section | PASS | Step 8.9/11 added |
| S6 | OmissionEngine rule `DISPATCH_CLAIM_MUST_SPAWN` registered | PASS | grep returns 3 matches; registry shows 8 rules with rule_h |
| S7 | Next 3 cards result in same-turn spawn | CEO-OWNED | Not verifiable by eng-platform |

## Test Output

```
22 passed in 0.08s (tests/platform/test_dispatch_role_routing.py)
```

## Notes

- OmissionType.DISPATCH_CLAIM_MUST_SPAWN added to omission_models.py enum
- GEventType.ENGINEER_CLAIM_TASK and GEventType.SUBAGENT_START added as trigger/fulfillment events
- Y-star-gov omission test failures (6 of them) are pre-existing, not caused by this change
- Rule H (rule_h_dispatch_claim_must_spawn) uses 300s soft / 600s hard TTL per Ethan's ruling
