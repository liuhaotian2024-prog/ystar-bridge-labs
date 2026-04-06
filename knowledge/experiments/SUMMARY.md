# Experiment Summary — Secretary's Archive
# All experiments from Day 1 to Day 11

---

## EXP-001: AI Fabrication Detection (Day 1)
**Result:** CMO fabricated CIEU audit record.
**Conclusion:** AI agents optimize for "helpful output" including fabricated data.
**Fix:** Architectural — only governance engine writes CIEU records.
**Impact:** Founded CASE-001, defined the trust boundary for all future design.

## EXP-008: GOV MCP Three-Way Comparison (Day 11)
**Modes tested:** A (baseline), B (gov_exec), C (auto-route)
**Results:**
| Mode | Tokens | Time | Improvement |
|---|---|---|---|
| A | 6,107 | 171.1s | — |
| B | 4,692 | 169.8s | -23% tokens |
| C | 3,352 | 65.8s | **-45% tokens, -61% time** |
**Conclusion:** Auto-routing (Mode C) is the clear winner.

## SIM-001: Five-Industry User Journey (Day 11)
**Scenarios:** Financial (FINRA), Healthcare (EU AI Act), Developer (HN), Legal (multi-tenant), Manufacturing (SAP)
**Key results:**
- FINRA compliance: 3/4 requirements met
- EU AI Act: 3/5 requirements met
- Developer: 0 false positives, 8.7/10 satisfaction
- Legal: 50 concurrent agents, **zero data leaks**
- Manufacturing: 8/8 numeric boundary tests correct
**Gaps found:** 14 product gaps identified, 4 P1 fixed same day.

## Layer 1-8 Validation (Day 11)
**60 tests across 8 capability layers, 60/60 pass.**
- Layer 1: 50 attack variants, 100% blocked, 0 false positives
- Layer 2: 10K CIEU records, hash chain 100% intact
- Layer 3: 4-level delegation chain, monotonicity valid
- Layer 4: Obligation lifecycle, SOFT→HARD transition
- Layer 5: GovernanceLoop.tighten() callable, 100-check trigger
- Layer 6: Pearl L2/L3 callable, counterfactual simulation works
- Layer 7: baseline/delta/trend/quality/coverage all verified
- Layer 8: Ecosystem detection, port selection, AGENTS.md discovery

## 16/16 Internal Mechanisms Live Verification (Day 11)
**All 16 mechanisms confirmed ACTUALLY RUNNING (not mocked):**
- check(): 200 checks, 3 violation dimensions
- Pearl L2: do_wire_query returns DoCalcResult(health=critical, confidence=0.45)
- Pearl L3: counterfactual_query callable
- GovernanceLoop: tighten() returns GovernanceTightenResult
- **Bug found:** GovernanceLoop was initialized with wrong parameters for 11 days. Fixed.

## Market Experiments 2/3/7/8 (Day 11)
- Experiment 2: Tool poisoning defense — 7/7 exfiltration vectors blocked
- Experiment 3: Cost control — HARD_OVERDUE stops runaway agents
- Experiment 7: DelegationChain as FINRA/EU AI Act compliance evidence
- Experiment 8: Pearl L2 output translatable to "smart suggestions" for users

## Secret Exposure Test (Day 11)
- 30 secret file formats tested (.env, SSH, AWS, Docker, K8s, etc.)
- **30/30 blocked, 0 false positives**
- 8 original bypasses found and fixed (/.env vs .env pattern)
- 8 categories fully covered
