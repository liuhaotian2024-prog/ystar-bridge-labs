from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping


E15D_CAPABILITY_STATES = [
    "unavailable",
    "draft_only_available",
    "owner_send_only",
    "send_gated_pending_authorization",
    "gov_mcp_controlled_pilot_available",
    "revoked",
    "suspended_by_risk",
    "disabled_by_hard_gate",
]

E15D_HARD_GATES = [
    "payment",
    "contract",
    "legal_obligation",
    "financial_commitment",
    "customer_system_access",
    "regulated_government_tax_immigration_identity_forms",
    "credential_disclosure",
    "core_brain_cieu_memory_canonical_writeback",
]

E15D_PROGRESSIVE_DOMAINS = [
    "low_risk_validation_messaging",
    "draft_only_message_preparation",
    "owner_approved_send_queue",
    "feedback_intake",
    "follow_up_draft_preparation",
    "suppression_aware_target_replacement",
]


def load_e15a_console(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "operations" / "external_validation" / "e15a_owner_execution_console.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_e15d_controlled_outbound_domain(console: Mapping[str, Any]) -> Dict[str, Any]:
    primary_actions = list(console.get("primary_actions", []))
    return {
        "domain_id": "e15d_controlled_outbound_validation_messaging",
        "capability_name": "low-risk AI-transparent validation messaging",
        "current_state": "send_gated_pending_authorization",
        "state_model": E15D_CAPABILITY_STATES,
        "hard_gates": E15D_HARD_GATES,
        "progressive_governed_domains": E15D_PROGRESSIVE_DOMAINS,
        "source_console_id": console.get("console_id"),
        "source_action_ids": [action["action_id"] for action in primary_actions],
        "draft_only_available": True,
        "owner_send_only_available": True,
        "send_gated_available_after_authorization": True,
        "gov_mcp_execute_available_now": False,
        "real_send_allowed_now": False,
        "owner_authorization_required_for_send": True,
        "required_controls": [
            "narrow_owner_authorization_envelope",
            "Y_gov_outbound_policy_decision",
            "gov_mcp_outbound_adapter_receipt",
            "kill_switch_guard",
            "rate_limit_guard",
            "suppression_guard",
            "action_ledger_hook",
            "feedback_wait_state_hook",
        ],
        "external_action_executed": False,
    }


def validate_e15d_controlled_outbound_domain(domain: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if domain.get("current_state") not in E15D_CAPABILITY_STATES:
        errors.append("invalid_capability_state")
    if domain.get("gov_mcp_execute_available_now") is not False:
        errors.append("gov_mcp_execute_must_not_be_available_before_authorization")
    if domain.get("real_send_allowed_now") is not False:
        errors.append("real_send_must_not_be_allowed_now")
    if domain.get("owner_authorization_required_for_send") is not True:
        errors.append("send_must_require_owner_authorization")
    hard_gates = set(domain.get("hard_gates", []))
    for gate in ["payment", "contract", "credential_disclosure", "core_brain_cieu_memory_canonical_writeback"]:
        if gate not in hard_gates:
            errors.append(f"missing_hard_gate_{gate}")
    if len(domain.get("source_action_ids", [])) != 3:
        errors.append("domain_must_reuse_three_e15a_primary_actions")
    if domain.get("external_action_executed") is not False:
        errors.append("domain_must_not_execute_external_action")
    return list(dict.fromkeys(errors))
