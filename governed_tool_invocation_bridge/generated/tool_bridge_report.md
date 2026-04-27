# Governed Tool Invocation Bridge Report

bridge_id: governed_tool_invocation_bridge_v0
supported_tool_id: governed_readonly_observation_tool_v0
agent_direct_tool_invocation_allowed: False
pre_u_packet_required: True
governance_decision_required: True

## Agent Tool Request

- request_id: agent-tool-request-001
- requesting_agent: Aiden-CEO
- supporting_agent: Samantha-Secretary
- request_type: company_state_observation

## Pre-U Packet

- packet_id: pre-u-tool-packet-001
- candidate_U_count: 3
- selected_U: U1

## Governance Decision

- decision_id: governance-decision-tool-bridge-001
- decision: allow_local_readonly_tool_invocation
- allowed_only_as_local_readonly_dry_run: True

## Bridge Authorization

- authorization_id: bridge-authorization-001
- authorized: True
- allowed_sources: 8

## Bridged Tool Result

- status: success
- read_sources: 8
- real_action_executed: False
- external_action_executed: False
- live_action_enabled: False
- cieu_persistence_enabled: False
- brain_writeback_enabled: False
- memory_ingestion_enabled: False

## Rejections

- direct_tool_invocation_rejected: True
- unsafe_bridge_request_rejected: True

Next required milestone: L4.6 Agent Team Work Proposal to Governed Tool Invocation v0

Warning: Tool invocation is routed through a Pre-U bridge for local read-only dry-run only. Live execution and persistence remain disabled.
