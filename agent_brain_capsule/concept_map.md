# Concept Map

This map summarizes existing concepts only. It does not define new theory.

| Concept | Existing definition/source | Runtime-facing meaning | Gaps |
|---|---|---|---|
| Agent Brain | `cieu_brain_bridge.py`, `cieu_brain_streamer.py`, `cieu_brain_learning.py`, `aiden_brain.db` path references | A 6D graph substrate where CIEU events and memory artifacts can activate nodes and influence future context. | DB contents not inspected; current live wiring needs validation. |
| DNA/Ontology | `knowledge/ceo/AIDEN_ONTOLOGY.md`, `knowledge/ceo/team_dna.md` | Identity, operating principles, Board relationship, team habits, and counterfactual thinking style. | `team_dna.md` is older and should be reconciled with current agent registry. |
| Long-term memory | `knowledge/`, `memory/boot_packages/`, `brain_auto_ingest.py`, `MEMORY_AND_DEGRADATION_STRATEGY.md` | Durable human-readable memory that can be indexed and ingested into brain nodes. | Exact current ingestion coverage needs validation. |
| Working memory | `memory/WORLD_STATE.md`, `memory/session_handoff.md`, `.czl_subgoals.json` | Current runtime state and boot/handoff context. | Runtime state can be stale or mutable; should be read through indexes. |
| Thinking Model / Cognitive Policy | `AIDEN_ONTOLOGY.md`, `brain_3loop_consolidated_v2.md`, `CZL-BRAIN-3LOOP-FINAL-ruling.md` | Counterfactual operating style plus L1/L2/L3 brain loops. | No single “LLM reflection calculator” found. |
| Field Functional | `Y_STAR_FIELD_THEORY_SPEC.md`, `y_star_field_validator.py` | Mission field maps mission components into local task `Y*`; `m_functor` makes that link explicit. | Field gradient and metacognition runtime are partial/spec-level. |
| CZL | `CZL.md`, `charter_amendment_014_closed_loop_cieu_residual_engine.md` | Runtime contract for closing residuals: `Rt+1 = 0` means done, nonzero residual remains open. | RLE live status unclear. |
| CIEU Log | `.ystar_cieu.db` path references, CIEU modules, brain rulings | Evidence ledger, residual signal source, and training/nutrition substrate. | DB contents not inspected. |
| Brain Writeback | `brain_3loop_consolidated_v2.md`, `CZL-BRAIN-L2-WRITEBACK-PARTIAL-20260420.md` | Post-action learning path from decision/outcome into activation/access/edge updates. | Partial receipt says hook wiring was not live at that time; current status needs validation. |
| Dream/Reflection | `brain_dream_scheduler.py`, `CZL-BRAIN-L3-GUARD-RAILS-ruling.md` | Offline consolidation over activation history; proposes edges/nodes/archive actions. | Auto-commit status and guardrail implementation need validation. |
| Governance Boundary | `GOVERNANCE-DUAL-ASPECT-AND-INSIGHT-RULE-PIPELINE-20260420.md`, `Y_STAR_FIELD_THEORY_SPEC.md` Section 11, `boundary_enforcer.py` | Deterministic governance checks form; operations/cognition achieve content. | Must avoid LLM-judge governance. |
