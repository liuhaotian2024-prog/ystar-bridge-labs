#!/usr/bin/env python3
"""Lane B: human-approved outreach execution pipeline v1."""

from __future__ import annotations

from common import no_action_receipt, packet, write_json, write_md


OUT = "l7_human_approved_outreach_execution_pipeline"
LANE = "L7.4B"


def build() -> None:
    states = [
        "draft_ready",
        "owner_review_required",
        "owner_approved_for_manual_send",
        "manual_send_allowed",
        "sent_by_owner_or_approved_agent",
        "post_action_receipt_required",
        "response_capture_pending",
    ]
    approval_schema = {
        **packet("approval_record_schema", LANE),
        "fields": [
            "approval_id",
            "draft_id",
            "recipient_review_id",
            "approved_action",
            "approved_by",
            "approved_at",
            "approval_scope",
            "expiration",
        ],
        "default_decision": "blocked_until_human_approved",
    }
    manual_send_schema = {
        **packet("manual_send_packet_schema", LANE),
        "allowed_only_after_approval": True,
        "fields": [
            "approved_draft_id",
            "approved_recipient_reference",
            "approved_sender",
            "manual_send_instructions",
            "post_action_receipt_path",
        ],
        "autonomous_bulk_outreach_status": "hard_forbidden_unless_future_policy_changes",
    }
    recipient_checklist = {
        **packet("recipient_review_checklist", LANE),
        "checks": [
            "recipient was selected through approved read-only research",
            "no private personal data was collected",
            "recipient is relevant to target archetype",
            "owner approves manual contact",
            "no login-gated or private-source basis is used",
        ],
    }
    message_checklist = {
        **packet("message_review_checklist", LANE),
        "checks": [
            "no guaranteed revenue claim",
            "no compliance certification claim",
            "no payment request",
            "no customer commitment",
            "caveats are included",
            "message is low pressure and review-gated",
        ],
    }
    pre_send_gate = {
        **packet("outreach_pre_send_gate", LANE),
        "pipeline_states": states,
        "current_state": "owner_review_required",
        "execution_allowed": False,
        "reason": "owner_has_not_approved_send",
        "draft_generation": "allowed",
        "recipient_research": "read_only_allowed",
        "owner_approval_request": "allowed",
        "actual_send": "blocked_until_explicit_approval",
        "autonomous_bulk_outreach": "hard_forbidden_unless_future_policy_changes",
    }
    receipt_schema = {
        **packet("post_outreach_receipt_schema", LANE),
        "required_after_any_future_approved_send": True,
        "fields": [
            "sent_by",
            "approved_action_id",
            "recipient_reference",
            "message_hash_or_summary",
            "sent_at",
            "response_status",
            "side_effects_confirmed",
        ],
    }

    write_json(f"{OUT}/approval_record_schema.json", approval_schema)
    write_json(f"{OUT}/manual_send_packet_schema.json", manual_send_schema)
    write_json(f"{OUT}/recipient_review_checklist.json", recipient_checklist)
    write_json(f"{OUT}/message_review_checklist.json", message_checklist)
    write_json(f"{OUT}/outreach_pre_send_gate.json", pre_send_gate)
    write_json(f"{OUT}/post_outreach_receipt_schema.json", receipt_schema)
    write_json(f"{OUT}/outreach_execution_no_action_receipt.json", no_action_receipt("outreach_execution_no_action_receipt", LANE))

    write_md(
        f"{OUT}/outreach_execution_owner_guide.md",
        """
# Outreach Execution Owner Guide

Current status: execution is not allowed.

Allowed before approval:
- draft generation
- read-only recipient research
- owner approval request

Blocked now:
- actual send
- bulk outreach
- payment request
- customer commitment

Future manual send requires owner approval, recipient review, message review, and a post-action receipt.
""",
    )
    print("L7.4B outreach execution pipeline generated")


if __name__ == "__main__":
    build()
