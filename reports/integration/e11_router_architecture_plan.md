# E11 Router Architecture Plan

Routers were selected only after semantic inventory, capability fingerprints, duplicate clustering, conflict matrix, and ownership map existed.

## Implemented Routers
### cluster_target_lifecycle
- cluster_name: Target candidate/proposal/approval lifecycle
- conflict_risk: high
- router_module: office.mission_command.target_lifecycle_router
- canonical_owner: bridge-labs owns business target lifecycle; Y-star-gov owns external-action permission semantics; gov-mcp exposes gateway checks.
- old_path_role: adapter-only unless routed through this facade.

### cluster_evidence_signal_ladder
- cluster_name: Evidence, feedback, and paid-signal ladder
- conflict_risk: high
- router_module: office.mission_command.evidence_signal_router
- canonical_owner: bridge-labs owns market/evidence claim ladder; CIEU governs durable learning; owner decides commercial escalation.
- old_path_role: adapter-only unless routed through this facade.

### cluster_action_authorization_chain
- cluster_name: External action authorization chain
- conflict_risk: critical
- router_module: office.mission_command.action_authorization_router
- canonical_owner: Y-star-gov owns deterministic policy; gov-mcp owns gateway exposure; bridge-labs owns business intent and execution packet assembly.
- old_path_role: adapter-only unless routed through this facade.

### cluster_learning_writeback_gate
- cluster_name: Report, method, dream, brain, and CIEU learning paths
- conflict_risk: critical
- router_module: office.mission_command.learning_writeback_router
- canonical_owner: CIEU/Y-star-gov owns prediction-delta eligibility; Aiden Brain owns graph state; bridge-labs reports are proposal-only.
- old_path_role: adapter-only unless routed through this facade.

### cluster_closure_status_semantics
- cluster_name: Closure status and completion semantics
- conflict_risk: high
- router_module: office.mission_command.closure_status_router
- canonical_owner: bridge-labs CZL owns mission closure semantics; repository status remains delivery-only; commercial validation needs feedback/ledger evidence.
- old_path_role: adapter-only unless routed through this facade.

### cluster_counterfactual_protocol
- cluster_name: Counterfactual and disconfirmation protocol
- conflict_risk: medium
- router_module: office.mission_command.counterfactual_router
- canonical_owner: Method kernel owns durable counterfactual protocol; stage modules adapt it to opportunity, market, execution, revenue, governance, or learning contexts.
- old_path_role: adapter-only unless routed through this facade.

## Mapped Without Destructive Routing
- cluster_field_brain_cognitive_runtime: mapped through field/brain/CIEU integration map and learning_writeback_router; no destructive centralization.
- cluster_incubated_company_runtime: mapped through cross-repo backflow plan; ystar-company remains incubation source.

## E10/E11 Validation Path Gate
- target contact must pass target_lifecycle_router.
- evidence claims must pass evidence_signal_router.
- external action must pass action_authorization_router.
- learning writeback must pass learning_writeback_router.
- mission completion claims must pass closure_status_router.
