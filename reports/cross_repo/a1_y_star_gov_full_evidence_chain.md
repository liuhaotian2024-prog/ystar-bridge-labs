# A1 Y-star-gov Full Evidence Chain Audit

- generated_at: 2026-05-03T21:21:59Z
- scope: Y-star-gov, gov-mcp, ystar-bridge-labs, ystar-company
- rule: read-only cross-repo audit; no source changes outside ystar-bridge-labs

## Human Summary

Y-star-gov 的完整面貌不是一个简单的 permission-tier 文件。扫描显示它包含治理 validator、Pre-U packet、CIEU prediction delta、residual loop、approval/delegation/obligation、hook/dry-run、intervention/enforcement、learning promotion、release/live boundary 的多层治理骨架。

当前 bridge-labs 已经把商业 runtime 的目标、证据、审批、反馈、交付闭环做得很具体；但这些商业规则仍主要在 bridge-labs 本地实现。下一步不是删除这些能力，而是把稳定规则 backflow 成 Y-star-gov canonical profiles，并由 gov-mcp 承接工具边界。

## Repository Evidence

### Y-star-gov
- path: `/Users/haotianliu/.openclaw/workspace/Y-star-gov`
- exists: `True`
- branch: `backflow/company-runtime-domain-pack`
- head: `5f031f4 [auto] WIP checkpoint 2026-05-02 07:00 -- 1 files changed`
- safe_file_count: `662`
- status_sample_count: `0`

### gov-mcp
- path: `/Users/haotianliu/.openclaw/workspace/gov-mcp`
- exists: `True`
- branch: `backflow/company-runtime-tools`
- head: `f06aef3 feat: extend company runtime mission preflight tools`
- safe_file_count: `81`
- status_sample_count: `0`

### ystar-bridge-labs
- path: `/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs`
- exists: `True`
- branch: `backflow/aiden-ceo-meeting-room`
- head: `a100c38c feat: add owner operated validation prep packet`
- safe_file_count: `29963`
- status_sample_count: `59`

### ystar-company
- path: `/Users/haotianliu/.openclaw/workspace/ystar-company`
- exists: `True`
- branch: `main`
- head: `dd9cb6b2 fix: ground aiden ceo chat in labs context`
- safe_file_count: `43261`
- status_sample_count: `80`

## Y-star-gov Capability Categories

### governance validators
- purpose: Deterministic validation of Y*, U, packet structure, contract drafts, and hook-facing decisions.
- maturity: High for deterministic local checks; semantic proof remains explicitly bounded.
- files: `ystar/governance/pre_u_packet_validator.py`, `ystar/governance/u_v2_validator.py`, `ystar/governance/y_star_field_validator.py`, `ystar/kernel/nl_to_contract.py`, `ystar/kernel/prefill.py`, `ystar/kernel/czl_protocol.py`, `tests/governance/test_pre_u_packet_validator.py`, `tests/test_nl_to_contract.py`
- tests: Tests present for Pre-U, NL-to-contract, CZL protocol, and governance protocol rules; commercial validation schemas are not yet canonical here.
- bridge-labs relationship: Bridge-labs E11/E14 routers enforce similar invariants locally for commercial validation packets.
- gov-mcp relationship: gov-mcp exposes Y-star-gov decisions as MCP tools and should call these validators for live tool boundaries.
- backflow need: Backflow commercial validation packet schemas and owner approval invariants into Y-star-gov validator standards.
- risk if not integrated: Commercial runtime can drift into local policy forks that look safe but are not canonical.

### Pre-U packet validation
- purpose: Pre-action packet gate for Y*, Xt, candidate U, selected U, residual rationale, risk tier, and CIEU link policy.
- maturity: Spec plus skeleton implementation plus tests; intentionally structural, not semantic omniscience.
- files: `docs/pre_u_packet_validator/README.md`, `docs/pre_u_packet_validator/validator_interface_spec.md`, `docs/pre_u_packet_validator/validation_matrix.md`, `docs/pre_u_packet_validator/cieu_contract.md`, `docs/pre_u_packet_validator/hook_contract.md`, `ystar/governance/pre_u_packet_validator.py`, `tests/governance/test_pre_u_packet_validator.py`
- tests: Tests present; missing commercial owner-operated validation packet fixtures.
- bridge-labs relationship: E-series CZL closure packets mirror Pre-U semantics but are currently rendered in bridge-labs reports.
- gov-mcp relationship: gov-mcp can expose the validator as an owner/tool preflight envelope.
- backflow need: Define E14/E15 owner validation prep as a Pre-U packet profile.
- risk if not integrated: Milestone actions may claim readiness without canonical pre-action packet validation.

### CIEU / prediction delta / residual
- purpose: Prediction-vs-actual delta, residual loops, learning eligibility, and writeback gating.
- maturity: Strong kernel and tests for structural delta and residual loop; commercial feedback-to-CIEU profile still missing.
- files: `ystar/governance/cieu_prediction_delta.py`, `ystar/governance/cieu_store.py`, `ystar/governance/residual_loop_engine.py`, `ystar/kernel/cieu.py`, `ystar/kernel/rt_measurement.py`, `docs/cieu_prediction_delta/schema_v0.md`, `tests/governance/test_cieu_prediction_delta.py`, `tests/test_cieu_store.py`, `tests/test_residual_loop_engine.py`
- tests: Tests present for delta, store, residual loop, brain bridge; missing E14/E15 feedback-to-delta fixture.
- bridge-labs relationship: Bridge-labs keeps public evidence, validation feedback, paid signal, and learning writeback separate through E11 routers.
- gov-mcp relationship: gov-mcp must not write CIEU/core state from tool calls; it should normalize envelopes and route to approved writers.
- backflow need: Backflow commercial feedback event classification into CIEU prediction-delta eligibility rules.
- risk if not integrated: Public evidence or owner notes could be promoted into persistent learning without delta validation.

### approval records / approval lifecycle
- purpose: Owner escalation, mission envelopes, permission tiers, and bounded approval semantics.
- maturity: Good domain pack for company runtime; owner validation batch approval lifecycle is not fully modeled as canonical record.
- files: `ystar/domains/company_runtime/escalation_contract.py`, `ystar/domains/company_runtime/delegated_mission_contract.py`, `ystar/domains/company_runtime/company_runtime_policy.py`, `ystar/domains/company_runtime/permission_tiers.py`, `tests/domains/company_runtime/test_escalation_contract.py`, `tests/domains/company_runtime/test_permission_tiers.py`
- tests: Company-runtime tests present; approval expiration/revocation/action-ledger coupling needs formal fixtures.
- bridge-labs relationship: E12/E14 owner approval request and decision packets implement concrete commercial approval lifecycle locally.
- gov-mcp relationship: gov-mcp already normalizes owner decisions with no external execution.
- backflow need: Promote E14 owner-operated manual validation approval packet as Y-star-gov approval record profile.
- risk if not integrated: Approval text, revocation, and action ledger requirements can diverge across milestones.

### delegation contracts
- purpose: Defines what an agent or role may do under delegated mission constraints.
- maturity: Implemented and tested for general governance and company runtime.
- files: `ystar/governance/delegation_policy.py`, `ystar/domains/company_runtime/delegated_mission_contract.py`, `tests/test_delegation_chain.py`, `tests/test_delegation_chain_runtime.py`, `tests/domains/company_runtime/test_mission_permission_check.py`
- tests: Delegation tests present; missing owner-operated commercial validation delegation examples.
- bridge-labs relationship: Bridge-labs models Aiden/Codex as non-senders and owner as executor for E14.
- gov-mcp relationship: gov-mcp exposes mission checks and escalation checks.
- backflow need: Add commercial validation delegation fixture: owner executor only, Aiden draft/prep only.
- risk if not integrated: Aiden/tool execution authority may be inferred from prepared packets rather than explicit delegation.

### obligation registration / obligation enforcement
- purpose: Registers, tracks, and remediates obligations generated by governance activity.
- maturity: Implemented with tests, but commercial validation explicitly forbids auto-registration in bridge-labs.
- files: `ystar/governance/obligation_triggers.py`, `ystar/governance/obligation_remediation.py`, `tests/test_obligation_triggers.py`, `tests/test_obligation_remediation.py`, `tests/governance/test_obligation_closure.py`
- tests: Obligation tests present; missing policy for when commercial feedback creates obligations.
- bridge-labs relationship: Bridge-labs E11-E14 receipts explicitly prevent obligation auto-registration.
- gov-mcp relationship: MCP boundary should not auto-register obligations on tool preflight.
- backflow need: Define no-auto-obligation rule for market validation unless owner explicitly approves.
- risk if not integrated: Validation prep could accidentally create commitments or follow-up duties.

### hook adapters / dry-run contract harness
- purpose: Executes governance decisions in dry-run/hook-facing form without pretending to perform live side effects.
- maturity: Strong for local hook and dry-run compatibility.
- files: `ystar/adapters/hook.py`, `ystar/adapters/hook_response.py`, `ystar/governance/hook_contract_adapter.py`, `ystar/governance/contract_dry_run.py`, `docs/hook_contract_adapter_dry_run.md`, `docs/hook_contract_cli_dry_run.md`, `docs/governance_contract_dry_run.md`, `tests/governance/test_contract_dry_run.py`, `tests/governance/test_hook_contract_adapter.py`
- tests: Hook adapter and dry-run tests present; missing bridge-labs delivery/evidence runner hook profile.
- bridge-labs relationship: Host-side delivery bridge and E13/E14 runners should become governed dry-run/live-boundary clients.
- gov-mcp relationship: gov-mcp is the external tool gateway that can host equivalent preflight decisions.
- backflow need: Add host-delivery and owner-validation packet adapters as dry-run fixtures.
- risk if not integrated: Delivery/evidence runners remain outside canonical hook governance.

### MCP decision envelope
- purpose: Defines how governance decisions are exposed to external tools and adapters.
- maturity: Documented and tested at adapter level; gov-mcp contains concrete server/tool implementation.
- files: `docs/gov_mcp_setup.md`, `docs/external_governance_adapter_sdk.md`, `docs/governance_endpoint_acceptance.md`, `tests/governance/test_external_adapter_sdk.py`, `tests/test_gov_mcp_delegation.py`
- tests: Adapter SDK tests present; commercial validation tools missing.
- bridge-labs relationship: Bridge-labs uses local routers pending MCP-backed formal tools.
- gov-mcp relationship: gov-mcp should own executable gateway exposure and result normalization.
- backflow need: Create MCP tools for validation approval packet, target batch, action ledger, and feedback event checks.
- risk if not integrated: Commercial runtime may bypass MCP gateway when moving from prep to execution.

### intervention / enforcement
- purpose: Detects omission, drift, and intervention conditions and routes them into governance action.
- maturity: Implemented with tests for governance-side behavior.
- files: `ystar/governance/intervention_engine.py`, `ystar/governance/intervention_models.py`, `ystar/governance/enforcement_observer.py`, `ystar/governance/omission_engine.py`, `tests/governance/test_enforcement_observer.py`, `tests/governance/test_omission_engine_cieu_persistence.py`
- tests: Tests present; missing commercial no-contact/no-payment violation fixtures.
- bridge-labs relationship: Bridge-labs emits safety receipts but does not yet route violations into Y-star-gov intervention.
- gov-mcp relationship: gov-mcp should expose deny/escalate outcomes at tool boundary.
- backflow need: Add market-validation violation scenarios to intervention/enforcement fixtures.
- risk if not integrated: A failed safety boundary may only be documented locally rather than enforced canonically.

### canonical learning / shadow learning / promotion
- purpose: Separates learning candidates, CIEU-reviewed deltas, and persistent brain/writeback promotion.
- maturity: Active and tested, with explicit anti-uncurated-writeback rules in CIEU validators.
- files: `ystar/governance/cieu_brain_bridge.py`, `ystar/governance/cieu_brain_learning.py`, `ystar/governance/brain_auto_ingest.py`, `ystar/governance/metalearning.py`, `ystar/governance/proposal_submission.py`, `tests/governance/test_cieu_brain_learning.py`, `tests/governance/test_brain_auto_ingest.py`
- tests: Tests present; missing E13/E14 commercial feedback learning fixture.
- bridge-labs relationship: E11 learning_writeback_router blocks direct report-to-brain writes.
- gov-mcp relationship: MCP tools should not perform persistent learning writes directly.
- backflow need: Backflow public-evidence vs feedback vs paid-signal learning eligibility rules.
- risk if not integrated: Commercial reports could become strategy memory without validated prediction deltas.

### release preflight / release simulation / no-go / live boundary
- purpose: Checks readiness, liveness, and post-ship completeness before treating a capability as live.
- maturity: Partial in Y-star-gov; richer historical release/live-boundary artifacts exist in ystar-company.
- files: `docs/development/RELEASE_AUDIT_v043.md`, `ystar/governance/liveness_audit.py`, `tests/test_liveness_audit.py`, `tests/governance/test_post_ship_completeness.py`
- tests: Some liveness/post-ship tests present; missing canonical commercial live/no-go standard.
- bridge-labs relationship: Bridge-labs CZL distinguishes repository delivery from validation/market closure.
- gov-mcp relationship: MCP gateway should expose no-go decisions before live tool execution.
- backflow need: Formalize repository delivery, evidence readiness, and live outreach boundaries as release standards.
- risk if not integrated: Repo closure can be mistaken for capability, validation, or revenue closure.

## Four-Repo Responsibility Boundary

- Y-star-gov should own normative governance kernel, deterministic validators, Pre-U/CIEU/residual/approval/learning/release standards.
- gov-mcp should own governed tool execution gateway, MCP preflight, allow/deny envelopes, and execution result normalization.
- ystar-bridge-labs should own Aiden CEO runtime, commercial validation loop, offer/target/evidence/owner packet generation, and host-side delivery.
- ystar-company should remain an incubator archive: absorb useful patterns, quarantine runtime drift, do not treat dirty artifacts as source of truth.

## Most Serious Misalignments

- A1-C01 `high`: bridge-labs target lifecycle vs canonical approval lifecycle - Backflow target lifecycle profile to Y-star-gov and expose gov-mcp preflight.
- A1-C02 `high`: public evidence vs validation feedback vs paid signal - Canonicalize signal taxonomy and CIEU eligibility.
- A1-C03 `critical`: action authorization split between bridge-labs router and gov-mcp gateway - Add gov-mcp commercial validation tools backed by Y-star-gov company runtime.
- A1-C04 `high`: report-only learning vs persistent brain/CIEU writeback - Define commercial feedback-to-CIEU prediction delta profile.
- A1-C05 `medium`: repository delivery closure vs capability/market closure - Formalize closure status semantics in Y-star-gov CZL profile.
- A1-C06 `medium`: ystar-company historical live/commercial runtime drift - Triage incubator assets: absorb patterns, archive runtime drift, avoid source-of-truth status.

## Runtime Alignment Snapshot

| capability | canonical owner | current implementation | risk | priority | next action |
|---|---|---|---|---|---|
| target lifecycle | Y-star-gov | ystar-bridge-labs | high | P0 | Backflow target lifecycle state machine and owner-operated contact gating. |
| evidence/signal | Y-star-gov | ystar-bridge-labs | high | P0 | Canonicalize public evidence vs validation feedback vs paid signal. |
| action authorization | Y-star-gov + gov-mcp | ystar-bridge-labs + gov-mcp | critical | P0 | Make gov-mcp gateway call Y-star-gov company-runtime decisions for E14/E15. |
| learning writeback | Y-star-gov | ystar-bridge-labs | high | P0 | Backflow commercial learning eligibility into CIEU delta schema. |
| closure status | Y-star-gov | ystar-bridge-labs | medium | P1 | Formalize repository/capability/validation/paid-signal closure distinctions. |
| counterfactual | Y-star-gov | ystar-bridge-labs | medium | P1 | Use Y-star-gov counterfactual protocol as canonical source. |
| approval record | Y-star-gov | ystar-bridge-labs | high | P0 | Promote owner validation approval packet into Y-star-gov approval record profile. |
| feedback event | Y-star-gov | ystar-bridge-labs | high | P0 | Define feedback event to CIEU prediction-delta eligibility. |
| action ledger | Y-star-gov + gov-mcp | ystar-bridge-labs | high | P0 | Create canonical action ledger validator and MCP preflight/read model. |
| host delivery | ystar-bridge-labs | ystar-bridge-labs | low | P1 | Keep bridge-labs owner; optionally expose no-go status to gov-mcp. |
| MCP execution | gov-mcp | gov-mcp + bridge-labs adapters | medium | P0 | Add commercial validation preflight tools; no external execution without owner approval. |
| CIEU residual | Y-star-gov | Y-star-gov + bridge-labs reports | medium | P1 | Map commercial CZL residuals to prediction delta profile. |
| obligation registration | Y-star-gov | Y-star-gov with bridge-labs no-auto receipts | medium | P1 | Specify market validation no-auto-obligation rule. |
| release/live boundary | Y-star-gov | bridge-labs + ystar-company | high | P1 | Backflow live boundary/no-go standard from incubator and bridge-labs. |
| commercial validation | ystar-bridge-labs | ystar-bridge-labs | medium | P0 | Keep commercial runtime in bridge-labs while formalizing governance profiles upstream. |

## CEO Validation Parallelism

允许并行推进 CEO validation 的 owner-operated 决策台和人工验证准备，但不允许 Aiden 自动发送、发布、收款、登录、提交表单或把 public evidence 当作 validation feedback。E15 仍必须等待有效 action ledger + feedback event。

## CZL

- A1 inventory_rt1: 0
- A1 ownership_map_rt1: 0
- A1 backflow_plan_rt1: 0
- A1 repository_delivery_rt1: 1 until host-side delivery pushes and confirms remote SHA
- A1 full_mission_rt1: 1 until repository delivery closes
