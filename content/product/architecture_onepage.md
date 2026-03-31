# Y*gov Architecture — One-Page Overview

## System Summary

Y*gov is a **dual-track governance system** for AI agents.
Path A governs Y*gov itself ("who governs the governors").
Path B governs external agents ("how to control what they do").
A Bridge feeds external experience back into internal improvement.

## Five-Layer Architecture

```
 ┌─────────────────────────────────────────────────────────────┐
 │  Layer 5 — BRIDGE                                          │
 │  ExperienceBridge: Path B patterns → GovernanceLoop KPIs   │
 │  Direction: Path B ──► Bridge ──► GovernanceLoop (one-way) │
 └──────────────────────────┬──────────────────────────────────┘
           ▲ aggregates     │ feeds metrics
 ┌─────────┴───────────┐  ┌▼──────────────────────────────────┐
 │ Layer 3 — PATH B    │  │ Layer 2 — PATH A                  │
 │ External Governance  │  │ Internal Meta-Governance          │
 │                      │  │                                   │
 │ ExternalObservation  │  │ GovernanceSuggestion              │
 │   → constraint       │  │   → suggestion_to_contract()     │
 │ ConstraintBudget     │  │ check() own actions               │
 │ Escalation ladder:   │  │ Causal confidence tracking        │
 │  warn→down→freeze→dc │  │ CIEU audit trail                  │
 └──────────┬──────────┘  └──────────────────┬────────────────┘
            │ uses                            │ uses
 ┌──────────▼────────────────────────────────▼────────────────┐
 │  Layer 1 — INTENT COMPILATION                              │
 │  AGENTS.md (rules) → nl_to_contract → IntentContract       │
 │  ConstitutionalContract → statutory merge → check-ready    │
 └────────────────────────────┬────────────────────────────────┘
                              │ enforced by
 ┌────────────────────────────▼────────────────────────────────┐
 │  Layer 0 — FOUNDATION                                      │
 │  check()  CIEU  OmissionEngine  InterventionEngine         │
 │  CausalEngine (Pearl L2-3)  GovernanceLoop  Metalearning   │
 │  8 constraint dimensions + 4 higher-order dimensions       │
 └─────────────────────────────────────────────────────────────┘
```

## Call Directions

| From | To | Mechanism |
|------|----|-----------|
| Path B | Foundation | check(), CIEU, CausalEngine |
| Path A | Foundation | check(), CIEU, CausalEngine |
| Bridge | Path B | reads CIEU records |
| Bridge | GovernanceLoop | injects 3 KPIs into raw_kpis |
| GovernanceLoop | Path A | produces GovernanceSuggestion |

## Key Numbers

| Metric | Value |
|--------|-------|
| Test coverage | 304 tests passing |
| CIEU audit records | 830+ |
| Causal reasoning | Pearl Ladder L2-L3 (do-calculus, counterfactuals) |
| Patent applications | 3 filed |
| Safety-critical halt distance | SHD = 0 |
| Constraint dimensions | 8 base + 4 higher-order |
