# gov_pretrain Real Verification Report
# Date: 2026-04-05
# Status: INSUFFICIENT DATA — Cannot Verify

---

## What We Tried

Attempted to run gov_pretrain against all available CIEU databases
on the MAC mini to verify whether it actually learns anything useful.

## CIEU Data Available

| Database | Events | Deny Rate |
|---|---|---|
| `~/.ystar_cieu.db` | 2 | 100% (both DENY) |
| `~/.openclaw/workspace/.ystar_cieu.db` | 9 | 44% (4 deny, 5 allow) |
| **Total available** | **11** | — |

## gov_pretrain Minimum Requirement

gov_pretrain returns `"insufficient_data"` when events < 10.
We have 11 total across two databases, but:
- Only 2 in the home database (doctor_agent test events)
- Only 9 in the workspace database
- No database has enough for meaningful pattern detection

## Honest Conclusion

**gov_pretrain CANNOT be verified today.**

It requires 100+ CIEU events with diverse agents, actions, and decisions
to detect meaningful patterns. The 11 events we have are:
- All from the same session
- Almost all from doctor_agent or governance tests
- No real user workflow data

## What gov_pretrain WOULD Do (Based on Code)

If sufficient data existed (100+ events):
1. Count denied paths by frequency → suggest tightening or relaxing
2. Detect sensitive-looking paths that were ALLOWED → suggest adding to deny
3. Count denied commands by frequency → identify over-broad rules
4. Generate suggestions with confidence scores

## When This Can Be Verified

- After PyPI release and first 10+ real users
- After running SIM-001 scenarios with persistent CIEU storage
- After GovernanceLoop runs for 24+ hours with real agent traffic

## Written into Phase 2 Roadmap

This verification is not forgotten — it's condition-dependent.
See `roadmap/SIM-001_product_gaps.md` for the full list.
