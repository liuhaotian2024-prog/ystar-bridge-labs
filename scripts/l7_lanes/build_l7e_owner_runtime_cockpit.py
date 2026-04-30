#!/usr/bin/env python3
"""Build L7E owner runtime cockpit artifacts."""

from __future__ import annotations

from common import artifact_ref, base_no_action_receipt, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7E"
LANE_NAME = "Owner Runtime Cockpit"
OUTPUT_DIR = "l7_owner_runtime_cockpit"


def build() -> None:
    artifacts: list[str] = []
    l6_refs = {
        "ceo_command_brief": artifact_ref("ceo_command_brief/l6_16_ceo_command_brief.md"),
        "internal_strategy_memo": artifact_ref("internal_strategy_memo/l6_16_internal_strategy_memo.md"),
        "human_review_packet": artifact_ref("human_review_packet/l6_15_human_review_packet.json"),
        "l6_16_summary": artifact_ref("l6_16_read_model/l6_16_read_model_summary.json"),
    }

    system_card = {
        "schema_version": "v0",
        "card_id": "l7e_system_status_card",
        "status": "l7_parallel_orchestration_initialized",
        "l6_refs": l6_refs,
        "external_actions_blocked": True,
        "core_writebacks_blocked": True,
    }
    write_json(f"{OUTPUT_DIR}/system_status_cards/system_status_card.json", system_card)
    artifacts.append(f"{OUTPUT_DIR}/system_status_cards/system_status_card.json")

    agent_cards = {
        "schema_version": "v0",
        "agents": ["CEO", "Researcher", "Operator/COO", "Engineer/CTO", "Secretary", "Auditor", "Revenue Scout"],
        "team_runtime_ref": "l7_agent_team_runtime/agent_reporting_lines/team_orchestration_manifest.json",
    }
    write_json(f"{OUTPUT_DIR}/agent_team_cards/agent_team_card_index.json", agent_cards)
    artifacts.append(f"{OUTPUT_DIR}/agent_team_cards/agent_team_card_index.json")

    work_queue = {
        "schema_version": "v0",
        "cards": [
            {
                "work_order_id": "l7b_revenue_scan_work_order_001",
                "lane": "L7B",
                "status": "ready_for_read_only_radar",
            }
        ],
    }
    write_json(f"{OUTPUT_DIR}/work_order_queue_cards/work_order_queue_cards.json", work_queue)
    artifacts.append(f"{OUTPUT_DIR}/work_order_queue_cards/work_order_queue_cards.json")

    revenue_cards = {
        "schema_version": "v0",
        "cards": [
            {
                "opportunity_id": "l7b_opportunity_001",
                "status": "offline_fixture_ready",
                "next_safe_step": "market hypothesis table",
            }
        ],
    }
    write_json(f"{OUTPUT_DIR}/revenue_opportunity_cards/revenue_opportunity_cards.json", revenue_cards)
    artifacts.append(f"{OUTPUT_DIR}/revenue_opportunity_cards/revenue_opportunity_cards.json")

    approval_cards = {
        "schema_version": "v0",
        "cards": [
            {
                "approval_queue": "external_action_gate",
                "status": "empty_but_required_before_external_action",
            },
            {
                "approval_queue": "writeback_gate",
                "status": "dry_run_candidates_only",
            },
        ],
    }
    write_json(f"{OUTPUT_DIR}/approval_queue_cards/approval_queue_cards.json", approval_cards)
    artifacts.append(f"{OUTPUT_DIR}/approval_queue_cards/approval_queue_cards.json")

    blocked_cards = {
        "schema_version": "v0",
        "blocked_actions": [
            "outreach",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "revenue execution",
            "MCP/live behavior",
            "CIEU DB write",
            "brain/memory writeback",
            "canonical strategy mutation",
            "direct Y* mutation",
        ],
    }
    write_json(f"{OUTPUT_DIR}/blocked_action_cards/blocked_action_cards.json", blocked_cards)
    artifacts.append(f"{OUTPUT_DIR}/blocked_action_cards/blocked_action_cards.json")

    recommendations = {
        "schema_version": "v0",
        "next_safest_command": "bash scripts/run_l7_parallel_lanes.sh --mode local-parallel",
        "then": "run_revenue_opportunity_radar_read_only",
        "do_not_build_next": [
            "external action automation before L7C approval gate is used",
            "core writeback before L7D human review gate is used",
            "manual URL injection paths",
        ],
    }
    write_json(f"{OUTPUT_DIR}/next_command_recommendations/next_command_recommendations.json", recommendations)
    artifacts.append(f"{OUTPUT_DIR}/next_command_recommendations/next_command_recommendations.json")

    receipt = base_no_action_receipt(LANE_ID, LANE_NAME)
    write_json(f"{OUTPUT_DIR}/owner_cockpit_no_action_receipts/no_action_receipt.json", receipt)
    artifacts.append(f"{OUTPUT_DIR}/owner_cockpit_no_action_receipts/no_action_receipt.json")

    cockpit = {
        "schema_version": "v0",
        "cockpit_id": "l7e_owner_runtime_cockpit",
        "what_do_i_own_now": [
            "A governed CEO agent with real public read-only observation history.",
            "A parallel commercial agent team scaffold.",
            "A revenue opportunity radar, approval gate, writeback protocol, and owner cockpit.",
        ],
        "what_agents_exist": agent_cards["agents"],
        "what_can_they_do": "They can generate internal, review-gated commercial work products without external side effects.",
        "what_are_they_working_on": ["team runtime", "revenue opportunity radar", "approval gates", "writeback protocol", "owner cockpit"],
        "what_opportunity_radar_exists": "L7B creates one offline opportunity packet from L6 evidence and review artifacts.",
        "what_actions_are_blocked": blocked_cards["blocked_actions"],
        "what_needs_human_approval": ["external actions", "payment/account/form behavior", "core memory/brain/canonical writeback"],
        "next_safest_command": recommendations["next_safest_command"],
        "shortest_path_toward_money_making_company": [
            "Run L7 local-parallel scaffold.",
            "Review the revenue opportunity packet.",
            "Approve only draft-only external action packets in a future gate.",
            "Keep memory/writeback dry-run until reviewed.",
        ],
        "what_should_not_be_built_next": recommendations["do_not_build_next"],
    }
    write_json(f"{OUTPUT_DIR}/owner_cockpit.json", cockpit)
    artifacts.append(f"{OUTPUT_DIR}/owner_cockpit.json")

    markdown = "\n".join(
        [
            "# L7E Owner Runtime Cockpit",
            "",
            "## What do I own now?",
            *[f"- {item}" for item in cockpit["what_do_i_own_now"]],
            "",
            "## What agents exist?",
            *[f"- {item}" for item in cockpit["what_agents_exist"]],
            "",
            "## What can they do?",
            f"- {cockpit['what_can_they_do']}",
            "",
            "## What actions are blocked?",
            *[f"- {item}" for item in cockpit["what_actions_are_blocked"]],
            "",
            "## What needs human approval?",
            *[f"- {item}" for item in cockpit["what_needs_human_approval"]],
            "",
            "## Next safest command",
            f"- `{cockpit['next_safest_command']}`",
            "",
            "## Shortest path toward a real money-making AI company",
            *[f"- {item}" for item in cockpit["shortest_path_toward_money_making_company"]],
            "",
            "## What should not be built next?",
            *[f"- {item}" for item in cockpit["what_should_not_be_built_next"]],
            "",
        ]
    )
    write_text(f"{OUTPUT_DIR}/owner_cockpit.md", markdown)
    artifacts.append(f"{OUTPUT_DIR}/owner_cockpit.md")

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUTPUT_DIR,
        artifacts,
        recommendations["next_safest_command"],
        {"owner_cockpit_created": True, "blocked_actions": len(blocked_cards["blocked_actions"])},
    )
    write_json(f"{OUTPUT_DIR}/l7e_owner_runtime_cockpit_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7e_owner_runtime_cockpit_summary.md", simple_md("L7E Owner Runtime Cockpit", summary))


if __name__ == "__main__":
    build()
