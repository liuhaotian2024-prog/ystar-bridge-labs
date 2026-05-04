# E16X Cross-Repo Canonical Ownership

## Y-star-gov

Owns:
- deterministic governance kernel
- IntentContract and ConstitutionalContract semantics
- canonical check/enforce entrypoints
- CIEU evidence chain and residual standards
- obligation, omission, delegation monotonicity governance
- governance loop and intervention standards
- release/live/no-go boundary standards

Evidence:
- README.md
- ystar/__init__.py
- ystar/kernel/cieu.py
- ystar/kernel/engine.py
- ystar/kernel/czl_protocol.py
- ystar/governance/contract_lifecycle.py
- ystar/governance/intervention_engine.py
- ystar/governance/obligation_triggers.py
- ystar/governance/router_registry.py
- ystar/governance/y_star_field_validator.py
- docs/pre_u_packet_validator/README.md
- docs/gov_mcp_setup.md
- docs/external_governance_adapter_sdk.md
- tests/test_delegation_chain.py

## gov-mcp

Owns:
- MCP execution gateway
- gov_check and gov_enforce tool surface
- contract activation through MCP
- execution receipts and normalized deny/allow envelopes
- provider adapter boundary
- future outbound adapter implementation if accepted

Evidence:
- README.md
- pyproject.toml
- gov_mcp/server.py
- gov_mcp/router.py
- gov_mcp/company_runtime_tools.py
- gov_mcp/dispatch_logic.py
- gov_mcp/exec_whitelist.yaml

## ystar-bridge-labs

Owns:
- Aiden/CEO company runtime dogfood
- commercial validation loop
- offer, target, batch, owner console, feedback artifacts
- prototype outbound governance contracts before promotion
- host-side repository delivery closure

Evidence:
- office/mission_command/e8_risk_controlled_action_model.py
- office/mission_command/e8_external_action_preflight.py
- office/mission_command/e8_execution_gate.py
- office/mission_command/e9_suppression_registry.py
- office/mission_command/action_authorization_router.py
- office/mission_command/e12_action_packet.py
- office/mission_command/e12_execution_gate.py
- office/mission_command/e12_feedback_capture.py
- office/mission_command/e12_signal_evaluator.py
- office/mission_command/b2r_capability_domains.py
- office/mission_command/b2r_external_validation_messaging.py
- office/mission_command/b2r_gov_mcp_execution_contract.py
- office/mission_command/c2_ygov_action_decision.py
- office/mission_command/c2_gov_mcp_execution_control.py
- office/mission_command/c3_validation_batch_selector.py
- office/mission_command/e15a_owner_execution_console.py
- office/mission_command/e15d_ygov_outbound_policy.py
- office/mission_command/e15d_gov_mcp_outbound_adapter.py
- scripts/host_delivery_runner.py

## ystar-company

Owns:
- historical incubated assets
- legacy company runtime patterns for possible backflow
- archive candidates

Evidence:
- README.md
- runtime_artifact_quarantine/README.md
- l8_first_cash_path_operating_loop/README.md

## Safety

- E16X performs read-only cross-repo inventory and static governance canonicalization only. It performs no customer contact, email/message sending, publication, payment, account creation, form submission, login, external validation submission, customer system access, legal/financial commitment, credential disclosure, core brain/CIEU/memory canonical writeback, real provider API call, outbound adapter call, or real send receipt.
