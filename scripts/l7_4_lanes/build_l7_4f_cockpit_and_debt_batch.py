#!/usr/bin/env python3
"""Lane F: owner cockpit v3 and conservatism debt next batch."""

from __future__ import annotations

from common import bullets, load_json, no_action_receipt, packet, write_json, write_md


OUT = "l7_cockpit_v3_and_conservatism_batch"
LANE = "L7.4F"


def build() -> None:
    l7_3 = load_json("l7_approval_ready_offer_validation_workflow/l7_3_summary.json", {})
    first_revenue = {
        **packet("first_revenue_status_card", LANE),
        "first_revenue_path": l7_3.get("selected_offer", "Founder AI Workflow Audit & CEO Command Brief Sprint"),
        "ready_now": [
            "offer definition",
            "approval-ready outreach drafts",
            "human approval request",
            "delivery workflow",
            "intake template",
            "pricing hypothesis",
        ],
        "still_needs_approval": [
            "recipient selection",
            "manual outreach send",
            "price quote",
            "customer scope commitment",
            "payment setup/execution",
        ],
        "blocked": [
            "auto-send",
            "bulk outreach",
            "payment request",
            "publication",
            "core writeback",
        ],
    }
    approval_queue = {
        **packet("approval_queue_status_card", LANE),
        "open_approval_requests": [
            {
                "approval_id": "l7_3_outreach_approval_request_001",
                "status": "blocked_until_human_approved",
                "recommended_action": "review outreach_draft_001 and recipient criteria",
            }
        ],
    }
    cash_path = {
        **packet("cash_path_status_card", LANE),
        "cash_path_stage": "first_revenue_readiness",
        "readiness_score": 82,
        "score_basis": [
            "offer ready",
            "drafts ready",
            "delivery dry-run ready",
            "approval pipeline ready",
            "payment not ready for execution",
        ],
    }
    blockers = {
        **packet("remaining_blockers_status_card", LANE),
        "first_revenue_blockers": [
            "owner approval for first manual outreach",
            "recipient review",
            "trust proof still internal only",
            "payment/contract setup not approved",
        ],
        "can_be_done_without_external_side_effects": [
            "read-only target discovery",
            "dry-run delivery rehearsal",
            "offer refinement",
            "approval packet review",
        ],
    }
    debt = {
        **packet("conservatism_next_batch_report", LANE),
        "batch_scope": "small active L7.3/L7.4 policy-reference planning only",
        "patches_applied": 0,
        "reason": "L7.4 generated artifacts already include policy references; no low-risk active source patch was required.",
        "debt_that_blocks_first_revenue": [
            "approval execution remains intentionally blocked until owner approval",
            "payment execution remains intentionally blocked until approval and customer commitment",
        ],
        "legitimate_hard_boundaries_preserved": [
            "no secret leakage",
            "no unapproved outreach",
            "no unapproved payment",
            "no direct writeback",
        ],
    }
    cockpit = {
        **packet("owner_cockpit_v3", LANE),
        "first_revenue_path": first_revenue["first_revenue_path"],
        "what_is_ready_now": first_revenue["ready_now"],
        "what_still_needs_approval": first_revenue["still_needs_approval"],
        "what_is_blocked": first_revenue["blocked"],
        "what_can_happen_without_external_side_effects": blockers["can_be_done_without_external_side_effects"],
        "next_one_command_action": "bash scripts/run_l7_4_parallel_first_revenue_sprint.sh --mode status",
        "remaining_conservatism_debt": debt["debt_that_blocks_first_revenue"],
        "which_debt_blocks_first_revenue": [
            "approval workflow has not yet been used by owner",
            "payment execution policy is not yet approved",
        ],
    }

    write_json(f"{OUT}/owner_cockpit_v3.json", cockpit)
    write_json(f"{OUT}/first_revenue_status_card.json", first_revenue)
    write_json(f"{OUT}/approval_queue_status_card.json", approval_queue)
    write_json(f"{OUT}/cash_path_status_card.json", cash_path)
    write_json(f"{OUT}/remaining_blockers_status_card.json", blockers)
    write_json(f"{OUT}/conservatism_next_batch_report.json", debt)
    write_json(f"{OUT}/cockpit_no_action_receipt.json", no_action_receipt("cockpit_no_action_receipt", LANE))

    write_md(
        f"{OUT}/owner_cockpit_v3.md",
        f"""
# Owner Cockpit v3

**First revenue path:** {cockpit['first_revenue_path']}

**Ready now**
{bullets(cockpit['what_is_ready_now'])}

**Needs approval**
{bullets(cockpit['what_still_needs_approval'])}

**Blocked**
{bullets(cockpit['what_is_blocked'])}

**Next one-command action:** `{cockpit['next_one_command_action']}`
""",
    )
    print("L7.4F cockpit and conservatism batch generated")


if __name__ == "__main__":
    build()
