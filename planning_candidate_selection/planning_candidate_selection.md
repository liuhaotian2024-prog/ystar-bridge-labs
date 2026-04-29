# Planning Candidate Selection

```json
{
  "schema_version": "v0",
  "milestone_id": "L6.16",
  "candidates_considered": 5,
  "primary_selected_planning_candidate": "l6_15_candidate_internal_strategy_memo",
  "selection": [
    {
      "candidate_id": "l6_15_candidate_internal_strategy_memo",
      "selected_status": "primary_recommended",
      "reason": "Matches L6.15 next safe step and stays internal with bounded-conflict caveats.",
      "evidence_basis": [
        "l6_13_claim_002"
      ],
      "caveat": "Conflict remains bounded and must be disclosed.",
      "risk": "low if caveats are preserved",
      "recommended_next_step": "draft internal strategy memo"
    },
    {
      "candidate_id": "l6_15_candidate_third_pass_observation",
      "selected_status": "secondary_candidate",
      "reason": "Useful follow-up after owner review, but not required before this memo.",
      "evidence_basis": [
        "bounded_conflict_interpretation"
      ],
      "caveat": "Only run under a new budgeted observation gate.",
      "risk": "low read-only risk if governed",
      "recommended_next_step": "run third-pass read-only observation"
    },
    {
      "candidate_id": "l6_15_candidate_market_hypothesis_table",
      "selected_status": "secondary_candidate",
      "reason": "Useful follow-up after owner review, but not required before this memo.",
      "evidence_basis": [
        "l6_13_claim_002"
      ],
      "caveat": "Use evidence as hypotheses, not settled market truth.",
      "risk": "medium if caveats are dropped",
      "recommended_next_step": "create market hypothesis table"
    },
    {
      "candidate_id": "l6_15_candidate_technical_gap_analysis",
      "selected_status": "deferred_candidate",
      "reason": "Helpful once the internal strategy direction is selected.",
      "evidence_basis": [
        "l6_13_claim_002"
      ],
      "caveat": "Scope gaps to observed public evidence only.",
      "risk": "low",
      "recommended_next_step": "create technical gap analysis"
    },
    {
      "candidate_id": "l6_15_candidate_internal_investor_narrative_draft",
      "selected_status": "deferred_candidate",
      "reason": "Internal draft material only; external sharing remains blocked.",
      "evidence_basis": [
        "l6_13_claim_002"
      ],
      "caveat": "Narrative must label bounded evidence and unresolved claims.",
      "risk": "medium if shared externally without approval",
      "recommended_next_step": "create investor narrative draft for internal review only"
    }
  ]
}
```
