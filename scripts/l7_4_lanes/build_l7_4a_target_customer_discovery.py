#!/usr/bin/env python3
"""Lane A: read-only target customer discovery radar."""

from __future__ import annotations

from common import bullets, load_json, no_action_receipt, packet, write_json, write_md


OUT = "l7_target_customer_discovery_radar"
LANE = "L7.4A"


def archetypes() -> list[dict]:
    rows = [
        (
            "archetype_001",
            "AI startup founder",
            ["urgent AI workflow choice", "needs investor/customer-ready clarity", "founder time bottleneck"],
        ),
        (
            "archetype_002",
            "technical operator",
            ["owns internal AI tooling", "needs workflow governance", "wants low-risk automation"],
        ),
        (
            "archetype_003",
            "solo founder building with AI agents",
            ["uses coding agents", "needs one-person operating leverage", "needs decision support"],
        ),
        (
            "archetype_004",
            "small AI automation agency owner",
            ["client delivery quality risk", "needs audit templates", "needs proof package"],
        ),
        (
            "archetype_005",
            "founder using Codex/Claude Code/OpenClaw-like workflows",
            ["agent governance uncertainty", "toolchain sprawl", "approval boundary confusion"],
        ),
        (
            "archetype_006",
            "startup team with urgent strategy/research/workflow decision",
            ["fast research needed", "unclear automation ROI", "needs internal command brief"],
        ),
    ]
    return [
        {
            "archetype_id": archetype_id,
            "name": name,
            "public_pain_signals": signals,
            "buying_triggers": [
                "deadline-driven decision",
                "visible AI workflow adoption",
                "need for evidence-backed internal brief",
            ],
            "future_approved_research_channels": [
                "public founder posts",
                "public product docs",
                "public job posts",
                "public startup community posts without login",
            ],
            "approval_required_before_contact": True,
        }
        for archetype_id, name, signals in rows
    ]


def build() -> None:
    l7_3 = load_json("l7_approval_ready_offer_validation_workflow/l7_3_summary.json", {})
    service = load_json("l7_approval_ready_offer_validation_workflow/service_offer_definition/service_offer_definition.json", {})
    archetype_rows = archetypes()
    target_segment_map = {
        **packet("target_segment_map", LANE),
        "selected_offer": l7_3.get("selected_offer", "Founder AI Workflow Audit & CEO Command Brief Sprint"),
        "segments": archetype_rows,
        "selection_logic": "Prioritize public signals of urgent AI workflow decisions, low implementation dependency, and clear founder pain.",
        "private_personal_data_collected": False,
    }
    report = {
        **packet("read_only_customer_discovery_report", LANE),
        "observation_mode": "existing_artifact_based_read_only",
        "real_web_observation_used": False,
        "limitation": "No live web scan was required for this deterministic sprint; use controlled read-only observation later if approved/configured.",
        "evidence_basis": [
            "L7.2 shortest cash path",
            "L7.3 selected offer and target customer profile",
        ],
        "offer": service.get("offer_name", l7_3.get("selected_offer")),
        "public_pain_signals": [
            "founder mentions AI workflow confusion",
            "team is adopting coding agents",
            "company needs urgent research or strategy decision",
            "operator is concerned about unsafe automation",
        ],
        "disqualification_criteria": [
            "requires guaranteed revenue",
            "requires legal certification",
            "requires autonomous action before approval",
            "requires private data collection",
        ],
        "next_safe_read_only_observation": "Run a bounded public signal scan for founder posts, docs, and job posts matching the archetypes.",
        "approval_required_before_contact": True,
    }
    public_sources = {
        **packet("public_signal_sources", LANE),
        "allowed_source_types": [
            "public company pages",
            "public founder posts",
            "public job posts",
            "public product docs",
            "public changelogs",
            "public startup community discussions without login",
        ],
        "blocked_source_types": [
            "private communities",
            "login-gated content",
            "payment-gated content",
            "private personal data",
            "direct messages",
        ],
    }
    no_contact_template = {
        **packet("no_contact_target_list_template", LANE),
        "template_only": True,
        "contains_live_customer_contacts": False,
        "fields": [
            "candidate_archetype",
            "public_signal_summary",
            "public_source_reference",
            "pain_hypothesis",
            "approval_required_before_contact",
        ],
        "forbidden_fields": ["private email", "phone number", "private profile data", "credentials"],
    }

    write_json(f"{OUT}/target_segment_map.json", target_segment_map)
    write_json(f"{OUT}/read_only_customer_discovery_report.json", report)
    write_json(f"{OUT}/public_signal_sources.json", public_sources)
    write_json(f"{OUT}/candidate_customer_archetypes.json", {**packet("candidate_customer_archetypes", LANE), "archetypes": archetype_rows})
    write_json(f"{OUT}/no_contact_target_list_template.json", no_contact_template)
    write_json(f"{OUT}/customer_discovery_no_action_receipt.json", no_action_receipt("customer_discovery_no_action_receipt", LANE))

    write_md(
        f"{OUT}/target_segment_map.md",
        "# Target Segment Map\n\n"
        + "\n".join(f"- {row['name']}: {', '.join(row['public_pain_signals'])}" for row in archetype_rows),
    )
    write_md(
        f"{OUT}/read_only_customer_discovery_report.md",
        f"""
# Read-Only Customer Discovery Report

**Mode:** existing-artifact read-only.

**Selected offer:** {target_segment_map['selected_offer']}

**Likely buyer archetypes**
{bullets([row['name'] for row in archetype_rows])}

**Next safe read-only observation:** {report['next_safe_read_only_observation']}

No customer contact occurred. No live private contact list was created.
""",
    )
    print("L7.4A target customer discovery generated")


if __name__ == "__main__":
    build()
