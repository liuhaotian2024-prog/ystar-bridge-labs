from __future__ import annotations

from office.mission_command.e15d_gov_mcp_outbound_adapter import (
    build_e15d_gov_mcp_outbound_adapter_contract,
    mode_for_e15d_policy_decision,
    validate_e15d_gov_mcp_outbound_adapter_contract,
)


def test_e15d_adapter_contract_defines_modes_without_live_execution() -> None:
    contract = build_e15d_gov_mcp_outbound_adapter_contract()
    assert validate_e15d_gov_mcp_outbound_adapter_contract(contract) == []
    assert contract["gateway_owner"] == "gov-mcp"
    assert contract["executes_real_external_action_in_e15d"] is False
    assert "send_gated_dry_run" in contract["currently_executable_modes_in_e15d"]


def test_e15d_adapter_maps_policy_to_pending_authorization() -> None:
    assert mode_for_e15d_policy_decision({"decision": "send_gated_requires_owner_authorization"}) == "send_gated_pending_authorization"
    assert mode_for_e15d_policy_decision({"decision": "suppress_target"}) == "deny"
