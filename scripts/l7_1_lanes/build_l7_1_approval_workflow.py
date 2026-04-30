#!/usr/bin/env python3
"""Build L7.1 human approval workflow v1 lane outputs."""

from __future__ import annotations

from common import base_no_action_receipt, base_packet, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7.1D"
LANE_NAME = "Human Approval Workflow v1"
OUT = "l7_human_approval_workflow_v1"

ACTION_TYPES = [
    "outreach_email_send",
    "partner_outreach",
    "grant_RFP_submission",
    "public_content_publication",
    "account_creation",
    "payment_purchase",
    "contract_signature",
    "MCP_live_behavior",
    "actual_memory_brain_canonical_writeback",
]


def build() -> None:
    queue_schema = {
        **base_packet("approval_queue_schema"),
        "default_state": "blocked_until_human_approved",
        "allowed_before_approval": ["draft", "evidence_packet", "approval_request", "risk_summary", "expected_value_summary"],
        "action_types": ACTION_TYPES,
        "required_fields": ["approval_id", "action_type", "evidence_basis", "risk_summary", "expected_value", "default_state"],
    }
    write_json(f"{OUT}/approval_queue_schema.json", queue_schema)

    examples = {
        **base_packet("approval_request_examples"),
        "approval_requests": [
            {
                "approval_id": "l7_1_approval_request_001",
                "action_type": "outreach_email_send",
                "draft_only": True,
                "default_state": "blocked_until_human_approved",
                "evidence_basis": ["l7_1_offer_001"],
                "risk_summary": "Could overclaim before customer validation.",
                "expected_value": "Validate willingness-to-pay hypothesis.",
            },
            {
                "approval_id": "l7_1_approval_request_002",
                "action_type": "actual_memory_brain_canonical_writeback",
                "draft_only": True,
                "default_state": "blocked_until_human_approved",
                "evidence_basis": ["l7_review_gated_memory_dry_run_v1"],
                "risk_summary": "Incorrect permanent learning could steer future strategy.",
                "expected_value": "Persist reviewed commercial strategy deltas.",
            },
        ],
    }
    write_json(f"{OUT}/approval_request_examples.json", examples)

    decision_schema = {
        **base_packet("approval_decision_record_schema"),
        "states": ["draft_created", "human_review_required", "approved_by_human", "execution_allowed", "executed", "post_action_receipt_created", "rejected_by_human", "blocked"],
        "denial_path": ["draft_created", "human_review_required", "rejected_by_human", "blocked"],
    }
    write_json(f"{OUT}/approval_decision_record_schema.json", decision_schema)

    preflight = {
        **base_packet("approved_action_execution_preflight"),
        "all_execution_defaults": [
            {"action_type": action, "default_state": "blocked_until_human_approved", "execution_allowed_now": False}
            for action in ACTION_TYPES
        ],
        "requires_explicit_human_approval": True,
    }
    write_json(f"{OUT}/approved_action_execution_preflight.json", preflight)

    rejected = {
        **base_packet("rejected_action_receipt_schema"),
        "required_fields": ["approval_id", "action_type", "rejected_by", "reason", "blocked_state", "no_action_receipt"],
        "blocked_state": "blocked",
    }
    write_json(f"{OUT}/rejected_action_receipt_schema.json", rejected)
    write_json(f"{OUT}/approval_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))

    write_text(
        f"{OUT}/approval_workflow_owner_guide.md",
        simple_md(
            "L7.1 Human Approval Workflow",
            [
                ("What It Does", "Turns draft-only revenue and writeback actions into approval requests you can review before anything external or permanent happens."),
                ("Default", "Every execution action is blocked_until_human_approved."),
                ("Allowed Before Approval", "Drafts, evidence packets, risk summaries, expected-value summaries, and approval requests."),
            ],
        ),
    )
    summary = lane_summary(LANE_ID, LANE_NAME, OUT, "completed", {"action_types_supported": len(ACTION_TYPES), "default_state": "blocked_until_human_approved"})
    write_json(f"{OUT}/l7_1_approval_workflow_summary.json", summary)


if __name__ == "__main__":
    build()
