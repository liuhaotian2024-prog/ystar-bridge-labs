# Y*gov 100% Framework — Compressed Execution Table
# Source: ChatGPT 9.3/10 evaluation + team consensus
# Date: 2026-03-31

## Current: 9.3/10 → Target: 10/10

---

## Batch 1: Root-level + Intent Compilation (P0)

### T1. Amendment System Object
- New: `ystar/governance/amendment.py`
- AmendmentProposal dataclass (status machine: draft→proposed→under_review→approved→rejected→activated→rolled_back)
- Amendment hash/version lineage
- Amendment CIEU recording
- Amendment provenance tracking

### T2. Amendment Response Chain
- Intent Compilation auto-detects new constitution version
- Path A/B cycle reads latest constitution at start
- Mismatch triggers formal response (not just skip)
- Activate/deactivate response unified

### T3. Compile→Validate→Review→Activate Workflow
- compile() produces draft contract
- validate() returns structured report
- review gate (Board confirmation for production)
- activate() makes contract live
- rollback/supersede mechanism

### T4. Constitution Source Unification
- All constitution loading goes through Intent Compilation
- Path A/B stop loading constitution directly (use IC output)
- Hash/provenance/version all from IC

---

## Batch 2: Path A/B Final Polish (P1)

### T5. Path A Causal Governance Strengthening
- Plan selection fully driven by causal ranking
- Causal evidence structured in CIEU
- Counterfactual output structured
- Causal confidence → human gate linkage explicit

### T6. Path B Authority Scope Formalization
- Constraint dimensions derived from observations only
- External constraint scope as structured object
- Scope enforcement tests

### T7. Path B Complete Result Loop
- External obligation model
- Inconclusive/soft/hard/human gate (full cycle)
- Repeated ineffective constraint → escalation policy
- Intermediate actions before disconnect

### T8. Path B Unified Execution Protocol
- apply_constraint / verify_compliance / downgrade_contract / freeze_session / disconnect_agent / require_human_review
- All as formal action types with schema

---

## Batch 3: Bridge + Action Schema (P1)

### T9. Bridge I/O Schema
- Input schema: Path B CIEU, compliance, budget, causal, disconnect events
- Output schema: metrics, gap candidates, suggestion candidates
- Input validation

### T10. Bridge Aggregation Logic
- Repeated violation patterns
- Ineffective constraint patterns
- Budget exhaustion patterns
- Causal effectiveness summary

### T11. Bridge-Only Routing Enforcement
- Test: A cannot eat B's raw events
- Test: B cannot drive A directly
- Test: GovernanceLoop cannot read Path B private state
- CI rules

### T12. Governance Action Schema (unified)
- governance_action_schema.md
- Shared fields: actor, target, scope, decision, evidence_ref, contract_ref, constitution_ref, followup_obligation, rollback_semantics
- CIEU/obligation/intervention aligned to schema

---

## Batch 4: Scenario Validation (P2)

### T13. Scenario Battery (8 scenarios)
1. Path A internal self-governance
2. Path B external governance
3. A + B + Bridge integrated
4. Constitution amendment
5. Compile ambiguity/error
6. Adversarial external agent
7. Multi-agent complex
8. Partial failure/degraded

### T14. Validation Report
- FRAMEWORK_VALIDATION_REPORT_v1.md
- Per-scenario: setup, execution, result, failure modes, recovery
- Overall: framework stability assessment
