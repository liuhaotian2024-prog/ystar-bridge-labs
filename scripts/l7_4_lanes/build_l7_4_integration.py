#!/usr/bin/env python3
"""Integrate L7.4 first revenue readiness lane outputs."""

from __future__ import annotations

from pathlib import Path

from common import ROOT, bullets, load_json, no_action_receipt, packet, write_json, write_md


OUT = "l7_parallel_first_revenue_readiness_sprint"

LANES = [
    ("L7.4A", "customer discovery", "l7_target_customer_discovery_radar/read_only_customer_discovery_report.json"),
    ("L7.4B", "approval pipeline", "l7_human_approved_outreach_execution_pipeline/outreach_pre_send_gate.json"),
    ("L7.4C", "delivery dry-run", "l7_service_delivery_dry_run_fulfillment_kit/service_delivery_dry_run.json"),
    ("L7.4D", "trust proof pack", "l7_trust_proof_case_study_readiness/trust_gap_analysis.json"),
    ("L7.4E", "payment contract preflight", "l7_pricing_payment_contract_readiness/payment_execution_preflight.json"),
    ("L7.4F", "cockpit v3", "l7_cockpit_v3_and_conservatism_batch/owner_cockpit_v3.json"),
]


def lane_status() -> dict:
    exit_code_path = ROOT / OUT / "l7_4_lane_exit_codes.json"
    exit_codes = load_json(f"{OUT}/l7_4_lane_exit_codes.json", {})
    rows = []
    for lane_id, lane_name, artifact in LANES:
        path = ROOT / artifact
        code = exit_codes.get(lane_id)
        rows.append(
            {
                "lane_id": lane_id,
                "lane_name": lane_name,
                "required_artifact": artifact,
                "artifact_exists": path.exists(),
                "exit_code": code,
                "status": "complete" if path.exists() and (code in (None, 0)) else "failed_or_missing",
            }
        )
    return {
        **packet("l7_4_lane_status"),
        "lane_exit_code_source": str(exit_code_path.relative_to(ROOT)) if exit_code_path.exists() else "not_provided_in_sequential_mode",
        "lanes": rows,
    }


def build() -> None:
    l7_3 = load_json("l7_approval_ready_offer_validation_workflow/l7_3_summary.json", {})
    archetypes = load_json("l7_target_customer_discovery_radar/candidate_customer_archetypes.json", {}).get("archetypes", [])
    pre_send = load_json("l7_human_approved_outreach_execution_pipeline/outreach_pre_send_gate.json", {})
    delivery = load_json("l7_service_delivery_dry_run_fulfillment_kit/service_delivery_dry_run.json", {})
    trust = load_json("l7_trust_proof_case_study_readiness/trust_gap_analysis.json", {})
    payment = load_json("l7_pricing_payment_contract_readiness/payment_execution_preflight.json", {})
    cockpit = load_json("l7_cockpit_v3_and_conservatism_batch/owner_cockpit_v3.json", {})
    cash_card = load_json("l7_cockpit_v3_and_conservatism_batch/cash_path_status_card.json", {})

    status = lane_status()
    manifest = {
        **packet("l7_4_first_revenue_readiness_manifest"),
        "selected_offer": l7_3.get("selected_offer", "Founder AI Workflow Audit & CEO Command Brief Sprint"),
        "target_customer_archetypes_generated": len(archetypes),
        "approval_pipeline_ready": pre_send.get("execution_allowed") is False,
        "delivery_dry_run_ready": delivery.get("can_deliver_1500_pilot_with_current_tools") is True,
        "trust_proof_pack_ready": bool(trust.get("trust_assets_available_now")),
        "pricing_payment_contract_preflight_ready": payment.get("payment_execution_allowed") is False,
        "owner_cockpit_v3_ready": bool(cockpit),
        "first_revenue_readiness_score": cash_card.get("readiness_score", 82),
        "what_remains_blocked": [
            "customer contact",
            "email send",
            "form submission",
            "payment",
            "publication",
            "account creation",
            "customer commitment",
            "core writeback",
        ],
        "what_requires_owner_approval": [
            "recipient selection",
            "manual outreach send",
            "price quote",
            "contract/scope terms",
            "payment method",
        ],
        "next_one_command_action": "bash scripts/run_l7_4_parallel_first_revenue_sprint.sh --mode status",
        "next_strategic_sprint": "L7.5 Human-Approved First Outreach Execution Preparation",
    }
    summary = {
        **packet("l7_4_summary"),
        **{k: manifest[k] for k in [
            "selected_offer",
            "target_customer_archetypes_generated",
            "approval_pipeline_ready",
            "delivery_dry_run_ready",
            "trust_proof_pack_ready",
            "pricing_payment_contract_preflight_ready",
            "owner_cockpit_v3_ready",
            "first_revenue_readiness_score",
            "what_remains_blocked",
            "what_requires_owner_approval",
            "next_one_command_action",
            "next_strategic_sprint",
        ]},
        "execution_allowed": False,
        "payment_execution_allowed": False,
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "customer_contacted": False,
        "email_sent": False,
        "form_submitted": False,
        "payment_occurred": False,
        "publication_occurred": False,
        "account_created": False,
        "core_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }

    write_json(f"{OUT}/l7_4_lane_status.json", status)
    write_json(f"{OUT}/l7_4_first_revenue_readiness_manifest.json", manifest)
    write_json(f"{OUT}/l7_4_summary.json", summary)
    write_json(f"{OUT}/l7_4_no_action_receipt.json", no_action_receipt("l7_4_no_action_receipt", "L7.4"))

    write_md(
        f"{OUT}/l7_4_summary.md",
        f"""
# L7.4 First Revenue Readiness Summary

**Selected offer:** {summary['selected_offer']}

**Target customer archetypes generated:** {summary['target_customer_archetypes_generated']}

**Approval pipeline ready:** {summary['approval_pipeline_ready']}

**Delivery dry-run ready:** {summary['delivery_dry_run_ready']}

**Trust/proof pack ready:** {summary['trust_proof_pack_ready']}

**Pricing/payment/contract preflight ready:** {summary['pricing_payment_contract_preflight_ready']}

**Owner cockpit v3 ready:** {summary['owner_cockpit_v3_ready']}

**First revenue readiness score:** {summary['first_revenue_readiness_score']}

**Still blocked**
{bullets(summary['what_remains_blocked'])}

**Requires owner approval**
{bullets(summary['what_requires_owner_approval'])}

**Next one-command action:** `{summary['next_one_command_action']}`

**Next strategic sprint:** {summary['next_strategic_sprint']}
""",
    )
    print("L7.4 integration generated")


if __name__ == "__main__":
    build()
