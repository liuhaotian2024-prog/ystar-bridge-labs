#!/usr/bin/env python3
"""Build L7.1 first offer hypothesis lane outputs."""

from __future__ import annotations

from common import base_no_action_receipt, base_packet, lane_summary, load_json, md_table, simple_md, write_json, write_text


LANE_ID = "L7.1C"
LANE_NAME = "First Offer Hypothesis Builder"
OUT = "l7_first_offer_hypothesis_builder"


def build() -> None:
    opportunities = []
    for idx in (1, 2):
        opportunities.append(load_json(f"l7_revenue_opportunity_radar_l7_1/opportunity_packets/opportunity_packet_{idx:03d}.json", {}))

    offers = [
        {
            "offer_id": "l7_1_offer_001",
            "target_customer_segment": opportunities[0].get("customer_segment", "AI startup founders"),
            "problem_statement": "Founders need credible external research and decision briefs without accidental side effects.",
            "proposed_solution": "A governed read-only observation sprint that produces evidence packets, conflict notes, and a CEO command brief.",
            "evidence_basis": opportunities[0].get("evidence_basis", []),
            "caveats": "Market willingness-to-pay remains a hypothesis until approved customer discovery.",
            "pricing_hypothesis": "founder pilot package at $500-$1500 per scoped internal research sprint",
            "delivery_model": "internal-only deliverable, reviewed by owner before any external use",
            "required_capabilities": ["controlled search", "public page read", "evidence extraction", "human approval gate"],
            "missing_capabilities": ["approved external outreach execution", "repeatable customer feedback loop"],
            "fastest_validation_path": "human-reviewed offer one-pager plus approved outreach in a future sprint",
            "forbidden_actions": ["send outreach", "publish offer", "collect payment", "create account", "submit forms"],
            "human_approval_required_before_external_action": True,
        },
        {
            "offer_id": "l7_1_offer_002",
            "target_customer_segment": opportunities[1].get("customer_segment", "solo owner-operators using AI agents"),
            "problem_statement": "Owners need one clear cockpit for agent team status, money path, blocked actions, and approval queue.",
            "proposed_solution": "Owner cockpit setup with revenue radar, offer hypotheses, approval workflow, and writeback dry-run queue.",
            "evidence_basis": opportunities[1].get("evidence_basis", []),
            "caveats": "Cockpit value improves once approved execution and feedback capture are added.",
            "pricing_hypothesis": "monthly internal operations cockpit retainer at $300-$1000 after pilot validation",
            "delivery_model": "private owner-facing dashboard artifacts and weekly command brief",
            "required_capabilities": ["parallel lanes", "approval queue", "owner cockpit", "memory dry-run"],
            "missing_capabilities": ["execution receipts from approved actions", "customer result tracking"],
            "fastest_validation_path": "use cockpit v2 internally for next two commercial sprints",
            "forbidden_actions": ["send outreach", "publish claims", "send customer contact", "sign contracts", "accept payment"],
            "human_approval_required_before_external_action": True,
        },
    ]

    offer_payload = {**base_packet("offer_hypotheses"), "internal_use_only": True, "offer_hypotheses": offers}
    write_json(f"{OUT}/offer_hypotheses.json", offer_payload)

    pricing = {
        **base_packet("pricing_hypotheses"),
        "pricing_hypotheses": [
            {"offer_id": "l7_1_offer_001", "hypothesis": "$500-$1500 pilot sprint", "confidence": "low_to_medium", "requires_market_validation": True},
            {"offer_id": "l7_1_offer_002", "hypothesis": "$300-$1000 monthly retainer after pilot", "confidence": "low", "requires_market_validation": True},
        ],
    }
    write_json(f"{OUT}/pricing_hypotheses.json", pricing)

    matrix = {
        **base_packet("customer_segment_to_offer_matrix"),
        "rows": [
            {"segment": offer["target_customer_segment"], "offer_id": offer["offer_id"], "fit": "strong_internal_hypothesis", "approval_required": True}
            for offer in offers
        ],
    }
    write_json(f"{OUT}/customer_segment_to_offer_matrix.json", matrix)

    trace = {
        **base_packet("evidence_to_offer_trace"),
        "trace_items": [
            {"trace_id": f"l7_1_trace_{idx:03d}", "offer_id": offer["offer_id"], "evidence_basis": offer["evidence_basis"], "allowed_use": "internal planning", "forbidden_use": "external claim without review"}
            for idx, offer in enumerate(offers, start=1)
        ],
    }
    write_json(f"{OUT}/evidence_to_offer_trace.json", trace)

    risk = {
        **base_packet("offer_risk_register"),
        "risks": [
            {"risk_id": "offer_risk_001", "risk": "pricing may be wrong", "mitigation": "validate through approved customer discovery"},
            {"risk_id": "offer_risk_002", "risk": "evidence may not generalize", "mitigation": "run third-pass market observation before publication"},
        ],
    }
    write_json(f"{OUT}/offer_risk_register.json", risk)

    next_steps = {
        **base_packet("offer_next_steps"),
        "next_safe_steps": [
            "prepare human review session for offer hypotheses",
            "draft outreach for review only",
            "run read-only customer segment observation",
        ],
        "external_actions_authorized": False,
    }
    write_json(f"{OUT}/offer_next_steps.json", next_steps)
    write_json(f"{OUT}/offer_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))
    write_text(
        f"{OUT}/offer_hypotheses.md",
        simple_md(
            "L7.1 First Offer Hypotheses",
            [
                ("Internal Only", "These are not publication-ready claims and not customer outreach."),
                ("Offers", md_table(offers, ["offer_id", "target_customer_segment", "pricing_hypothesis", "fastest_validation_path"])),
            ],
        ),
    )
    summary = lane_summary(LANE_ID, LANE_NAME, OUT, "completed", {"offer_hypotheses_generated": len(offers), "primary_offer": "l7_1_offer_001"})
    write_json(f"{OUT}/l7_1_offer_hypothesis_summary.json", summary)


if __name__ == "__main__":
    build()
