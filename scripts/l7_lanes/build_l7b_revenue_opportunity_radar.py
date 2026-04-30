#!/usr/bin/env python3
"""Build L7B revenue opportunity radar scaffold artifacts."""

from __future__ import annotations

from common import artifact_ref, base_no_action_receipt, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7B"
LANE_NAME = "Revenue Opportunity Radar"
OUTPUT_DIR = "l7_revenue_opportunity_radar"

FORBIDDEN = [
    "real outreach",
    "grant submission",
    "RFP submission",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "revenue execution",
]


def build() -> None:
    artifacts: list[str] = []
    l6_refs = [
        artifact_ref("ceo_command_brief/l6_16_ceo_command_brief.json"),
        artifact_ref("internal_strategy_memo/l6_16_internal_strategy_memo.json"),
        artifact_ref("human_review_packet/l6_15_human_review_packet.json"),
        artifact_ref("real_mission_evidence_report/l6_14_updated_mission_evidence_report.json"),
    ]

    work_order = {
        "schema_version": "v0",
        "work_order_id": "l7b_revenue_scan_work_order_001",
        "goal": "Convert L6 evidence and bounded-conflict review into one safe revenue opportunity hypothesis.",
        "inputs": l6_refs,
        "allowed_mode": "offline_fixture_from_existing_artifacts",
        "external_search_permitted": False,
        "external_action_permitted": False,
    }
    write_json(f"{OUTPUT_DIR}/revenue_scan_work_orders/revenue_scan_work_order_001.json", work_order)
    artifacts.append(f"{OUTPUT_DIR}/revenue_scan_work_orders/revenue_scan_work_order_001.json")

    policy = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "controlled_market_observation_default": "read_existing_artifacts_only",
        "future_real_observation_requires": "explicit read-only budget and approval",
        "forbidden_actions": FORBIDDEN,
    }
    write_json(f"{OUTPUT_DIR}/controlled_market_observation/controlled_market_observation_policy.json", policy)
    artifacts.append(f"{OUTPUT_DIR}/controlled_market_observation/controlled_market_observation_policy.json")

    opportunity = {
        "schema_version": "v0",
        "opportunity_id": "l7b_opportunity_001",
        "market_area": "controlled public evidence operations for small AI-enabled companies",
        "customer_segment": "founders and owner-operators who need governed AI research before external action",
        "pain_point": "They need evidence-backed strategy without accidentally publishing, outreaching, paying, or overclaiming.",
        "evidence_basis": [
            "L6.13 real observation succeeded",
            "L6.14 bounded a conflict after second-pass observation",
            "L6.15 produced human-review planning boundaries",
            "L6.16 produced an internal strategy memo and owner command brief",
        ],
        "source_urls_or_artifact_refs": l6_refs,
        "revenue_model_hypothesis": "offer a governed research-to-internal-strategy workflow before approved external execution",
        "urgency": "medium",
        "feasibility": "medium_high_for_internal_service_design",
        "competition_notes": "Competes with generic research agents, but differentiates through no-action governance and evidence traceability.",
        "regulatory_or_policy_link": "requires human approval gate before any external claims, outreach, or submissions",
        "next_safe_step": "market hypothesis table",
        "forbidden_actions": FORBIDDEN,
        "human_approval_required_before_external_action": True,
        "read_only_revenue_work_allowed": True,
        "draft_and_planning_allowed": True,
        "actual_execution_blocked_until_approval": True,
        "expected_revenue_path": "internal service packaging, then review-gated pilot offers after explicit approval",
        "uncertainty_level": "bounded_but_requires_more_market_observation",
    }
    write_json(f"{OUTPUT_DIR}/opportunity_packets/opportunity_packet_001.json", opportunity)
    artifacts.append(f"{OUTPUT_DIR}/opportunity_packets/opportunity_packet_001.json")

    pain = {
        "schema_version": "v0",
        "hypothesis_id": "l7b_customer_pain_001",
        "customer_segment": opportunity["customer_segment"],
        "pain_point": opportunity["pain_point"],
        "evidence_basis": opportunity["evidence_basis"],
        "safe_validation_step": "third-pass read-only observation or human review session",
        "external_contact_authorized": False,
    }
    write_json(f"{OUTPUT_DIR}/customer_pain_hypotheses/customer_pain_hypothesis_001.json", pain)
    artifacts.append(f"{OUTPUT_DIR}/customer_pain_hypotheses/customer_pain_hypothesis_001.json")

    funding_watch = {
        "schema_version": "v0",
        "candidate_id": "l7b_funding_watch_001",
        "watch_area": "governed AI assurance and evidence workflows",
        "safe_next_step": "policy/funding landscape map",
        "submission_authorized": False,
        "forms_authorized": False,
    }
    write_json(f"{OUTPUT_DIR}/funding_and_grant_watch_candidates/funding_watch_candidate_001.json", funding_watch)
    artifacts.append(f"{OUTPUT_DIR}/funding_and_grant_watch_candidates/funding_watch_candidate_001.json")

    pathway = {
        "schema_version": "v0",
        "pathway_id": "l7b_commercialization_pathway_001",
        "steps": [
            "internal strategy memo",
            "market hypothesis table",
            "technical gap analysis",
            "human review session",
            "draft-only external offer packet",
            "human-approved pilot outreach in a future milestone",
        ],
        "external_action_currently_blocked": True,
    }
    write_json(f"{OUTPUT_DIR}/commercialization_pathways/commercialization_pathway_001.json", pathway)
    artifacts.append(f"{OUTPUT_DIR}/commercialization_pathways/commercialization_pathway_001.json")

    risks = {
        "schema_version": "v0",
        "risks": [
            {
                "risk_id": "l7b_risk_overclaiming_market_need",
                "severity": "medium",
                "mitigation": "treat packet as hypothesis until read-only market observation and human review",
            },
            {
                "risk_id": "l7b_risk_external_action_before_gate",
                "severity": "high",
                "mitigation": "route through L7C human-approved external action gate",
            },
        ],
    }
    write_json(f"{OUTPUT_DIR}/revenue_risk_register/revenue_risk_register.json", risks)
    artifacts.append(f"{OUTPUT_DIR}/revenue_risk_register/revenue_risk_register.json")

    receipt = base_no_action_receipt(LANE_ID, LANE_NAME)
    write_json(f"{OUTPUT_DIR}/revenue_no_action_receipts/no_action_receipt.json", receipt)
    artifacts.append(f"{OUTPUT_DIR}/revenue_no_action_receipts/no_action_receipt.json")

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUTPUT_DIR,
        artifacts,
        "run_revenue_opportunity_radar_read_only",
        {"opportunity_packets_generated": 1, "first_opportunity_id": opportunity["opportunity_id"]},
    )
    write_json(f"{OUTPUT_DIR}/l7b_revenue_opportunity_radar_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7b_revenue_opportunity_radar_summary.md", simple_md("L7B Revenue Opportunity Radar", summary))


if __name__ == "__main__":
    build()
