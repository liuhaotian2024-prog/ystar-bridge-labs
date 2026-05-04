from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")


def _load_gov_mcp():
    sys.path.insert(0, str(GOV_MCP_ROOT))
    try:
        from gov_mcp.outbound.models import OutboundActionIntent, OutboundAuthorizationState, OutboundCapabilityDomain, OutboundExecutionMode, OutboundRiskTier
        from gov_mcp.outbound.provider_adapter import DryRunProviderSimulator, ProviderExecutionRequest
        return OutboundActionIntent, OutboundAuthorizationState, OutboundCapabilityDomain, OutboundExecutionMode, OutboundRiskTier, DryRunProviderSimulator, ProviderExecutionRequest
    finally:
        try:
            sys.path.remove(str(GOV_MCP_ROOT))
        except ValueError:
            pass


def execute_gov_mcp_dry_run_batch(envelopes: Dict[str, Any], guard_results: Dict[str, Any]) -> Dict[str, Any]:
    OutboundActionIntent, AuthState, Domain, Mode, RiskTier, Simulator, Request = _load_gov_mcp()
    guard_by_action = {row["action_id"]: row for row in guard_results["guard_results"]}
    simulator = Simulator()
    rows: List[Dict[str, Any]] = []
    for env in envelopes["envelopes"]:
        guard = guard_by_action[env["action_id"]]
        if guard["failed_checks"]:
            rows.append({
                "action_id": env["action_id"],
                "target_name": env["target_name"],
                "dry_run_executed": False,
                "execution_status": "blocked_by_guard",
                "reason_codes": guard["failed_checks"],
                "external_provider_called": False,
                "real_message_sent": False,
                "live_receipt_created": False,
            })
            continue
        intent = OutboundActionIntent(
            action_id=env["action_id"],
            capability_domain=Domain.EXTERNAL_VALIDATION_MESSAGE,
            risk_tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION,
            execution_mode=Mode.SEND_GATED_DRY_RUN,
            authorization_state=AuthState.OWNER_REVIEW_REQUIRED,
            target_id=env["target_id"],
            target_identity_sufficient=True,
            message_hash=env["message_hash"],
            idempotency_key=env["idempotency_key"],
            ai_transparency_present=True,
            opt_out_language_present=True,
            suppression_clear=env["suppression_status"] == "clear",
            rate_limit_clear=True,
            hard_gates_absent=True,
        )
        result = simulator.execute(Request(action_intent=intent, provider_mode="dry_run"))
        payload = result.to_dict()
        rows.append({
            "action_id": env["action_id"],
            "target_name": env["target_name"],
            "dry_run_executed": payload["execution_status"] == "dry_run_completed",
            "dry_run_receipt_id": payload["receipt"].get("receipt_id"),
            "provider_mode": payload["provider_mode"],
            "execution_status": payload["execution_status"],
            "receipt_type": payload["receipt_type"],
            "reason_codes": payload["reason_codes"],
            "guard_summary": guard["resulting_action_status"],
            "idempotency_key": env["idempotency_key"],
            "external_provider_called": payload["external_provider_called"],
            "real_message_sent": payload["real_message_sent"],
            "live_receipt_created": payload["live_receipt_created"],
            "no_external_effect_proof": {"provider_called": False, "real_message_sent": False, "live_receipt_created": False},
        })
    return {"artifact_id": "e22_gov_mcp_dry_run_results", "integration_mode": "direct_gov_mcp_import", "dry_run_results": rows, "dry_run_executed_count": sum(1 for row in rows if row.get("dry_run_executed")), "dry_run_blocked_count": sum(1 for row in rows if not row.get("dry_run_executed")), "external_action_executed": False}
