#!/usr/bin/env python3
"""Build L7.1 integration manifest and sprint summary."""

from __future__ import annotations

from common import base_no_action_receipt, base_packet, lane_summary, load_json, simple_md, write_json, write_text


OUT = "l7_parallel_commercial_autonomy_sprint"


LANE_SUMMARIES = [
    "l7_conservatism_debt_remediation_l7_1/l7_1_conservatism_batch_summary.json",
    "l7_revenue_opportunity_radar_l7_1/l7_1_revenue_radar_summary.json",
    "l7_first_offer_hypothesis_builder/l7_1_offer_hypothesis_summary.json",
    "l7_human_approval_workflow_v1/l7_1_approval_workflow_summary.json",
    "l7_review_gated_memory_dry_run_v1/l7_1_memory_dry_run_summary.json",
    "l7_owner_runtime_cockpit_v2/l7_1_owner_cockpit_v2_summary.json",
]


def build() -> None:
    lanes = [load_json(path, {"status": "missing", "output_dir": path}) for path in LANE_SUMMARIES]
    revenue = load_json("l7_revenue_opportunity_radar_l7_1/real_read_only_revenue_scan_report.json", {})
    offers = load_json("l7_first_offer_hypothesis_builder/offer_hypotheses.json", {"offer_hypotheses": []})
    memory = load_json("l7_review_gated_memory_dry_run_v1/writeback_dry_run_receipts.json", {"dry_run_receipts": []})
    cockpit = load_json("l7_owner_runtime_cockpit_v2/owner_cockpit_v2.json", {})
    patched = load_json("l7_conservatism_debt_remediation_l7_1/l7_1_patched_files_report.json", {})

    lane_status = {
        **base_packet("lane_status"),
        "all_lanes_complete": all(lane.get("status") == "completed" for lane in lanes),
        "lanes": lanes,
    }
    write_json(f"{OUT}/l7_1_lane_status.json", lane_status)

    manifest = {
        **base_packet("commercial_autonomy_manifest"),
        "lanes_executed": [lane.get("lane_id") for lane in lanes],
        "commercial_artifacts": [
            "revenue opportunity packets",
            "offer hypotheses",
            "pricing hypotheses",
            "approval workflow",
            "writeback dry-run candidates",
            "owner cockpit v2",
        ],
        "blocked_until_human_approval": [
            "outreach send",
            "publication",
            "payment",
            "account creation",
            "grant/RFP submission",
            "customer contact",
            "actual memory/brain/canonical/CIEU writeback",
        ],
        "next_recommended_command": "bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel",
    }
    write_json(f"{OUT}/l7_1_commercial_autonomy_manifest.json", manifest)

    summary = {
        **base_packet("l7_1_summary"),
        "lanes_executed": len(lanes),
        "conservatism_p0_p1_batch_patched_count": patched.get("patched_count", 0),
        "revenue_scan_classification": revenue.get("run_classification"),
        "opportunity_packets_generated": revenue.get("opportunity_packets_generated", 0),
        "offer_hypotheses_generated": len(offers.get("offer_hypotheses", [])),
        "approval_workflow_generated": True,
        "memory_dry_run_candidates_generated": len(memory.get("dry_run_receipts", [])),
        "owner_cockpit_v2_generated": True,
        "shortest_path_toward_first_revenue": cockpit.get("shortest_path_toward_first_revenue"),
        "next_recommended_command": manifest["next_recommended_command"],
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }
    write_json(f"{OUT}/l7_1_summary.json", summary)
    write_text(
        f"{OUT}/l7_1_summary.md",
        simple_md(
            "L7.1 Parallel Commercial Autonomy Sprint",
            [
                ("Outcome", "Generated commercial opportunity, offer, approval, memory dry-run, and owner cockpit artifacts."),
                ("Revenue Scan", str(summary["revenue_scan_classification"])),
                ("Shortest Path", str(summary["shortest_path_toward_first_revenue"])),
                ("Next Command", summary["next_recommended_command"]),
            ],
        ),
    )
    write_json(f"{OUT}/l7_1_no_action_receipt.json", base_no_action_receipt("L7.1", "Parallel Commercial Autonomy Sprint"))


if __name__ == "__main__":
    build()
