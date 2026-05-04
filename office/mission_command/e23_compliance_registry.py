from __future__ import annotations

from typing import Any, Dict


def build_compliance_registry() -> Dict[str, Any]:
    channels=["email_like_manual_or_provider_message","linkedin_like_manual_or_provider_message"]
    rows=[]
    for channel in channels:
        rows.append({"channel":channel,"jurisdiction":"unknown","commercial_outreach_risk":"low_medium_limited_b2b_validation","public_private_surface":"private_external_message","regulated_claim_risk":"blocked_if_present","legal_financial_commitment_risk":"blocked_no_go","payment_risk":"blocked_no_go","credential_account_risk":"blocked_no_go","sensitive_brand_publication_risk":"not_applicable_private_message","data_privacy_risk":"target_contact_metadata_only_no_customer_data_access","rate_limit_policy":{"max_batch_actions":5,"max_actions_per_target":1},"required_footer_disclosure":["AI transparency","light opt-out/no follow-up on request"],"opt_out_suppression_handling":"write suppression registry entry before any future action","classification":"policy_allows_agent_with_limits","owner_approval_requirement":"only_when_risk_tier_requires_it","external_action_executed":False})
    return {"artifact_id":"e23_compliance_registry","rows":rows,"compliance_blocked_count":0,"owner_approval_required_by_risk_count":0,"owner_manual_send_is_default":False,"external_action_executed":False}


def render_suppression_compliance(suppression: Dict[str, Any], compliance: Dict[str, Any]) -> str:
    return "\n".join(["# E23 Suppression and Compliance Registry","",f"- production_suppressed_target_count: {suppression['production_suppressed_target_count']}",f"- compliance_blocked_count: {compliance['compliance_blocked_count']}",f"- owner_approval_required_by_risk_count: {compliance['owner_approval_required_by_risk_count']}",f"- owner_manual_send_is_default: {str(compliance['owner_manual_send_is_default']).lower()}","- external_action_executed: false"]).rstrip()+"\n"
