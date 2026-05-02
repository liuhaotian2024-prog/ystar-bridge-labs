# E11 Canonical Ownership Map

## cluster_target_lifecycle: Target candidate/proposal/approval lifecycle
- canonical_owner: bridge-labs owns business target lifecycle; Y-star-gov owns external-action permission semantics; gov-mcp exposes gateway checks.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P1
- why: E10, E8/E9 validation, operations JSON, and ystar-company approval packets all represent target or approval states; proposal-only targets can be confused with approved contact targets without a lifecycle router.

## cluster_evidence_signal_ladder: Evidence, feedback, and paid-signal ladder
- canonical_owner: bridge-labs owns market/evidence claim ladder; CIEU governs durable learning; owner decides commercial escalation.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P1
- why: Reports and modules use public evidence, external pattern evidence, target discovery evidence, validation feedback, and paid signal for different claims; routing is needed to prevent public discovery from becoming validation or paid-pilot readiness.

## cluster_action_authorization_chain: External action authorization chain
- canonical_owner: Y-star-gov owns deterministic policy; gov-mcp owns gateway exposure; bridge-labs owns business intent and execution packet assembly.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P0
- why: Bridge-labs risk tiers, Y-star-gov permission tiers, gov-mcp preflight tools, manifests, execution gates, ledgers, and receipts all govern side effects; a facade is needed so future validation cannot bypass formal governance.

## cluster_learning_writeback_gate: Report, method, dream, brain, and CIEU learning paths
- canonical_owner: CIEU/Y-star-gov owns prediction-delta eligibility; Aiden Brain owns graph state; bridge-labs reports are proposal-only.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: CIEU/Y-star-gov.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P0
- why: Reports propose learning, method kernel stores durable principles, dream cycles propose diffs, brain stores cognitive graph/activation, and CIEU carries prediction delta. Direct report-to-brain learning would bypass review gates.

## cluster_closure_status_semantics: Closure status and completion semantics
- canonical_owner: bridge-labs CZL owns mission closure semantics; repository status remains delivery-only; commercial validation needs feedback/ledger evidence.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P1
- why: E milestones distinguish discovery complete, validation complete, paid-signal readiness, repository delivery, and blocked statuses. Without routing, local completion can be mistaken for commercial validation completion.

## cluster_counterfactual_protocol: Counterfactual and disconfirmation protocol
- canonical_owner: Method kernel owns durable counterfactual protocol; stage modules adapt it to opportunity, market, execution, revenue, governance, or learning contexts.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P2
- why: Counterfactual language appears in method kernel, opportunity evaluation, market evaluation, validation packets, and tests. A router should source the canonical protocol from method-kernel semantics instead of stage-local wording.

## cluster_field_brain_cognitive_runtime: Field/activation/brain cognitive runtime
- canonical_owner: Aiden Brain owns graph/activation state; ystar-company remains incubation source; bridge-labs owns interpretation reports; CIEU gates persistent learning.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: gov-mcp.
- persistence_owner: CIEU/Y-star-gov.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P2
- why: Aiden Brain, dream diffs, field-functional archaeology, world-value field, and activation/Hebbian concepts overlap as cognitive-field mechanisms, but not all are harmful duplicates. Integration mapping is safer than destructive consolidation.

## cluster_incubated_company_runtime: ystar-company incubated commercial/runtime mechanisms
- canonical_owner: bridge-labs owns current E-series commercial runtime; ystar-company remains incubation/reference unless separately backflowed.
- adapter_owner: bridge-labs E-series modules remain adapters unless explicitly promoted.
- renderer_owner: bridge-labs reports/integration.
- gateway_owner: bridge-labs.
- persistence_owner: bridge-labs reports.
- test_owner: bridge-labs E11 router tests plus future Y-star-gov/gov-mcp backflow tests.
- migration_priority: P2
- why: ystar-company contains scheduler, commercial loop, runtime packets, public research adapters, approval packets, and no-action receipts that overlap bridge-labs E6-E10 but are incubation artifacts with a very dirty runtime state.
