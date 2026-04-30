#!/usr/bin/env python3
"""Build L7C human-approved external action gate artifacts."""

from __future__ import annotations

from common import base_no_action_receipt, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7C"
LANE_NAME = "Human-Approved External Action Gate"
OUTPUT_DIR = "l7_human_approved_external_action_gate"

ACTION_TYPES = [
    "customer_outreach_email",
    "partner_outreach_email",
    "grant_application_submission",
    "RFP_submission",
    "public_content_publication",
    "account_creation",
    "payment_or_purchase",
    "contract_or_signature",
    "social_posting",
    "MCP_live_behavior",
]


def action_type_packet(action_type: str) -> dict[str, object]:
    return {
        "schema_version": "v0",
        "action_type": action_type,
        "default_status": "blocked_until_human_approved",
        "required_evidence": [
            "reviewed evidence packet",
            "bounded claim boundary",
            "risk assessment",
            "human approval request",
        ],
        "required_human_confirmation": "explicit action-specific approval",
        "allowed_pre_approval_output": "draft_only",
        "forbidden_pre_approval_behavior": [
            "send",
            "submit",
            "publish",
            "pay",
            "create account",
            "sign",
            "execute live behavior",
        ],
        "post_action_receipt_required": True,
        "rollback_or_stop_condition": "any ambiguity, missing approval, payment request, login, form, or policy conflict",
        "revenue_relevance": "may contribute to revenue only after approval and post-action receipt",
    }


def build() -> None:
    artifacts: list[str] = []
    packets = [action_type_packet(action) for action in ACTION_TYPES]
    write_json(f"{OUTPUT_DIR}/external_action_types/external_action_type_index.json", {"schema_version": "v0", "action_types": packets})
    artifacts.append(f"{OUTPUT_DIR}/external_action_types/external_action_type_index.json")

    for packet in packets:
        path = f"{OUTPUT_DIR}/external_action_types/{packet['action_type']}.json"
        write_json(path, packet)
        artifacts.append(path)

    draft_schema = {
        "schema_version": "v0",
        "packet_type": "draft_only_action_packet",
        "required_fields": [
            "draft_id",
            "action_type",
            "draft_content",
            "evidence_basis",
            "human_review_required",
            "execution_authorized",
        ],
        "execution_authorized_default": False,
    }
    write_json(f"{OUTPUT_DIR}/draft_only_action_packets/draft_only_action_packet_schema.json", draft_schema)
    artifacts.append(f"{OUTPUT_DIR}/draft_only_action_packets/draft_only_action_packet_schema.json")

    request_schema = {
        "schema_version": "v0",
        "packet_type": "human_approval_request",
        "required_fields": [
            "approval_id",
            "action_type",
            "draft_packet_ref",
            "evidence_required",
            "risk_tier",
            "human_confirmation_text",
            "default_decision",
        ],
        "default_decision": "blocked_until_approved",
    }
    write_json(f"{OUTPUT_DIR}/human_approval_requests/human_approval_request_schema.json", request_schema)
    artifacts.append(f"{OUTPUT_DIR}/human_approval_requests/human_approval_request_schema.json")

    state_machine = {
        "schema_version": "v0",
        "approval_path": [
            "draft_created",
            "human_review_required",
            "approved_by_human",
            "execution_allowed",
            "executed",
            "post_action_receipt_created",
        ],
        "denial_path": [
            "draft_created",
            "human_review_required",
            "rejected_by_human",
            "blocked",
        ],
        "execution_without_approval_allowed": False,
    }
    write_json(f"{OUTPUT_DIR}/approval_state_machine/approval_state_machine.json", state_machine)
    artifacts.append(f"{OUTPUT_DIR}/approval_state_machine/approval_state_machine.json")

    receipt_schema = {
        "schema_version": "v0",
        "packet_type": "post_action_receipt",
        "required_after_execution": True,
        "required_fields": [
            "receipt_id",
            "approval_id",
            "action_type",
            "executed_at",
            "external_side_effect_summary",
            "rollback_or_stop_status",
        ],
    }
    write_json(f"{OUTPUT_DIR}/post_action_receipts/post_action_receipt_schema.json", receipt_schema)
    artifacts.append(f"{OUTPUT_DIR}/post_action_receipts/post_action_receipt_schema.json")

    no_go = {
        "schema_version": "v0",
        "action_types": ACTION_TYPES,
        "all_default_status": "blocked_until_human_approved",
        "execution_in_l7_0p_authorized": False,
        "external_actions_blocked": True,
    }
    write_json(f"{OUTPUT_DIR}/external_action_no_go_matrix/external_action_no_go_matrix.json", no_go)
    artifacts.append(f"{OUTPUT_DIR}/external_action_no_go_matrix/external_action_no_go_matrix.json")

    receipt = base_no_action_receipt(LANE_ID, LANE_NAME)
    write_json(f"{OUTPUT_DIR}/external_action_no_go_matrix/no_action_receipt.json", receipt)
    artifacts.append(f"{OUTPUT_DIR}/external_action_no_go_matrix/no_action_receipt.json")

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUTPUT_DIR,
        artifacts,
        "create draft-only action packets behind human approval",
        {"action_types_modeled": len(ACTION_TYPES), "all_actions_default_blocked": True},
    )
    write_json(f"{OUTPUT_DIR}/l7c_human_approved_external_action_gate_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7c_human_approved_external_action_gate_summary.md", simple_md("L7C Human-Approved External Action Gate", summary))


if __name__ == "__main__":
    build()
