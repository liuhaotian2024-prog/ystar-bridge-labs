#!/usr/bin/env python3
"""Build L7.1 owner cockpit v2 lane outputs."""

from __future__ import annotations

from common import base_no_action_receipt, base_packet, lane_summary, load_json, simple_md, write_json, write_text


LANE_ID = "L7.1F"
LANE_NAME = "Owner Cockpit v2 Money Path"
OUT = "l7_owner_runtime_cockpit_v2"


def build() -> None:
    revenue = load_json("l7_revenue_opportunity_radar_l7_1/real_read_only_revenue_scan_report.json", {})
    offers = load_json("l7_first_offer_hypothesis_builder/offer_hypotheses.json", {"offer_hypotheses": []})
    approval = load_json("l7_human_approval_workflow_v1/approved_action_execution_preflight.json", {})
    memory = load_json("l7_review_gated_memory_dry_run_v1/writeback_dry_run_receipts.json", {})

    cards = {
        "money_path_status_card.json": {
            "title": "Shortest path toward first revenue",
            "status": "internal offer hypotheses ready; external validation requires human-approved outreach in future sprint",
            "next_step": "prepare human review session for l7_1_offer_001",
        },
        "agent_team_status_card.json": {
            "title": "Agent team",
            "status": "parallel L7 lanes can build revenue, offer, approval, memory dry-run, and cockpit artifacts",
        },
        "revenue_opportunity_status_card.json": {
            "title": "Revenue opportunities",
            "classification": revenue.get("run_classification"),
            "opportunity_packets": revenue.get("opportunity_packets_generated", 0),
        },
        "offer_hypothesis_status_card.json": {
            "title": "Offer hypotheses",
            "count": len(offers.get("offer_hypotheses", [])),
            "primary_offer": "l7_1_offer_001",
        },
        "approval_queue_status_card.json": {
            "title": "Approval queue",
            "default_state": "blocked_until_human_approved",
            "execution_defaults": approval.get("all_execution_defaults", []),
        },
        "memory_dry_run_status_card.json": {
            "title": "Memory dry-run",
            "dry_run_receipts": len(memory.get("dry_run_receipts", [])),
            "actual_writeback_occurred": False,
        },
        "blocked_actions_status_card.json": {
            "title": "Blocked actions",
            "blocked": ["outreach send", "publication", "payment", "account creation", "form submission", "grant/RFP submission", "actual writeback"],
        },
        "next_5_commands.json": {
            "commands": [
                "bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel",
                "review l7_first_offer_hypothesis_builder/offer_hypotheses.md",
                "review l7_human_approval_workflow_v1/approval_workflow_owner_guide.md",
                "prepare human approval review for l7_1_offer_001",
                "run third-pass read-only market observation if more evidence is needed",
            ],
        },
    }
    for filename, payload in cards.items():
        write_json(f"{OUT}/{filename}", {**base_packet(filename.removesuffix(".json")), **payload})

    cockpit = {
        **base_packet("owner_cockpit_v2"),
        "what_do_i_own_now": "A governed commercial agent-team sprint system that can discover opportunities, draft offers, prepare approval requests, and queue dry-run learning without external side effects.",
        "what_can_the_agent_team_do_today": "Run read-only commercial planning lanes, generate opportunity packets, build offer hypotheses, prepare approval workflow records, and update an owner cockpit.",
        "commercial_opportunities_found": [card for card in cards["revenue_opportunity_status_card.json"].items()],
        "offer_hypotheses_exist": [offer.get("offer_id") for offer in offers.get("offer_hypotheses", [])],
        "what_is_blocked": cards["blocked_actions_status_card.json"]["blocked"],
        "what_needs_my_approval": ["sending outreach", "publishing", "payments", "account creation", "grant/RFP submission", "MCP/live behavior", "actual writeback"],
        "what_can_safely_happen_next": "Internal review of l7_1_offer_001 and approval workflow dry run.",
        "shortest_path_toward_first_revenue": "Shortest path toward first revenue: pick the governed research-to-brief pilot offer, review the evidence/caveats, approve a small outreach draft in a future sprint, then collect feedback before payment or publication.",
        "what_should_not_be_built_next": "Do not build autonomous sending, payment, publication, or permanent memory writeback before approval gates and receipts are exercised.",
        "next_recommended_command": "bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel",
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
    }
    write_json(f"{OUT}/owner_cockpit_v2.json", cockpit)
    write_text(
        f"{OUT}/owner_cockpit_v2.md",
        simple_md(
            "L7.1 Owner Cockpit v2",
            [
                ("Plain Answer", cockpit["what_do_i_own_now"]),
                ("Money Path", cockpit["shortest_path_toward_first_revenue"]),
                ("Blocked", ", ".join(cockpit["what_is_blocked"])),
                ("Next Command", cockpit["next_recommended_command"]),
            ],
        ),
    )
    write_json(f"{OUT}/owner_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))
    summary = lane_summary(LANE_ID, LANE_NAME, OUT, "completed", {"owner_cockpit_v2_generated": True, "shortest_path": cockpit["shortest_path_toward_first_revenue"]})
    write_json(f"{OUT}/l7_1_owner_cockpit_v2_summary.json", summary)


if __name__ == "__main__":
    build()
