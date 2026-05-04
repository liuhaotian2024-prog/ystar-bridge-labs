from __future__ import annotations

from typing import Any, Dict


def build_live_provider_enablement_plan(provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    return {"artifact_id":"e23_live_provider_enablement_plan","provider_name_placeholder":"future_low_risk_message_provider","supported_provider_category":"outbound_message_provider_with_sandbox_or_strict_low_volume_live_mode","required_credentials_config":["provider API credential stored outside repo","sender identity config","suppression source config","rate-limit config"],"provider_api_capability_required":True,"provider_tests_required":["disabled-live blocks","dry-run receipt remains no-effect","sandbox/live-test no external customer contact","one-action canary guarded by idempotency/suppression/rate limit"],"dry_run_to_live_promotion_tests_required":True,"live_receipt_format":"live_execution_receipt_distinct_from_dry_run_receipt","live_audit_receipt_storage":"gov-mcp receipt ledger plus bridge-labs CZL reference","idempotency_persistence_requirement":"persistent store required before live","suppression_registry_integration":"operations/external_validation/e23_suppression_registry.json","compliance_registry_integration":"operations/external_validation/e23_compliance_registry.json","rate_limit_configuration":{"initial_live_canary_limit":1,"limited_batch_limit":5},"kill_switch":"global and batch kill switches required before live","rollback_reversal_path":"stop future sends and write suppression; message recall only if provider supports it","owner_approval_policy":"owner approval only for risk tiers requiring it","launch_stages":["disabled-live scaffold","sandbox/live-test mode if provider supports it","one-action low-risk live canary","limited batch live execution","expanded governed autonomous execution"],"live_provider_remains_disabled":not provider_sync.get("live_provider_enabled"),"external_action_executed":False}


def render_live_provider_enablement_plan(plan: Dict[str, Any]) -> str:
    lines=["# E23 Live Provider Enablement Plan","",f"- provider_name_placeholder: {plan['provider_name_placeholder']}",f"- live_provider_remains_disabled: {str(plan['live_provider_remains_disabled']).lower()}",f"- owner_approval_policy: {plan['owner_approval_policy']}","- external_action_executed: false","","## Launch Stages"]
    lines.extend(f"- {item}" for item in plan["launch_stages"])
    return "\n".join(lines).rstrip()+"\n"
