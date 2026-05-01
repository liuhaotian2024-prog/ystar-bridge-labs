from __future__ import annotations

from typing import Any, Dict, List


TOP_OPPORTUNITY_ID = "opp_integration_implementation_ai_ops_room"
TOP_OFFER_NAME = "48h AI Ops Operating Room Blueprint"


def _ai_ops_rows(quality_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        row
        for row in quality_rows
        if TOP_OPPORTUNITY_ID in row.get("opportunity_ids", [])
    ]


def _source_ids(rows: List[Dict[str, Any]]) -> List[str]:
    return [row["source_id"] for row in rows if row.get("source_id")]


def _usable_source_ids(rows: List[Dict[str, Any]]) -> List[str]:
    return [row["source_id"] for row in rows if row.get("usable_for_customer_facing_packet")]


def build_e7_validation_ready_offer_packet(quality_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    ai_ops = _ai_ops_rows(quality_rows)
    noisy_count = sum(1 for row in ai_ops if row.get("noise_flags"))
    usable_ids = _usable_source_ids(ai_ops)
    return {
        "offer_name": TOP_OFFER_NAME,
        "target_buyer": "Technical founder, AI-heavy small team, or operations lead trying to turn AI tools and agents into a governed operating workflow.",
        "buyer_job_to_be_done": "Decide how to wire AI-agent work, approvals, evidence, and action boundaries into an operating room without unsafe automation or tool sprawl.",
        "urgent_pain": "The buyer can buy AI tools, but cannot reliably turn them into a governed operating system that makes decisions, routes work, and prevents unsafe external actions.",
        "evidence_backed_market_category": "AI ops implementation support / operating-room setup / governed workflow advisory.",
        "competitor_substitute_no_action_diy_landscape": {
            "competitors": [
                "LangSmith / LangChain ecosystem",
                "CrewAI-style agentic workflow platforms",
                "Zapier / Retool / Make-style automation platforms",
                "Humanloop / Vellum-style AI evaluation platforms",
                "automation agencies and AI ops consultants",
            ],
            "substitutes": [
                "generic automation platforms",
                "internal ops builders",
                "manual Notion/Linear checklists",
                "chat-only AI workflows",
            ],
            "no_action": "Keep using disconnected AI tools and absorb delay, unclear ownership, and unsafe-action risk.",
            "diy": "Assign internal staff to build custom scripts, checklists, and approval habits without an external operating model.",
        },
        "ybridge_wedge": "Y*Bridge combines mission-grade runtime design, CZL residual discipline, evidence provenance, action-wide preflight, and CEO-readable decision artifacts.",
        "why_buyer_might_not_choose_us": [
            "They may believe an incumbent tool already solves the operating-room problem.",
            "They may prefer internal implementation over advisory.",
            "They may need implementation labor, not only a blueprint.",
            "They may see governance language as slowing M-3 value production unless the offer stays crisp.",
            "They may not yet trust a new company without stronger proof or references.",
        ],
        "trust_gap": "E6 public evidence supports the market category and alternatives, but does not prove buyer willingness to pay Y*Bridge. E7 keeps this explicit.",
        "deliverable_48h": [
            "current AI workflow and tool-boundary map",
            "approval/action-boundary matrix",
            "top three operating-room bottlenecks",
            "48h implementation blueprint",
            "risk and exclusion boundary",
            "owner-ready next-decision packet",
        ],
        "delivery_scope": [
            "analyze one buyer workflow sample or representative workflow description",
            "map mission routing, approvals, evidence, and external-action gates",
            "identify where incumbent tools leave operational gaps",
            "produce a 48h blueprint and validation-ready next step",
        ],
        "exclusions": [
            "no customer-system access by default",
            "no production implementation",
            "no legal/security certification",
            "no payment setup",
            "no account creation",
            "no external sending or publication",
            "no core DB/brain/memory/CIEU writeback",
        ],
        "prerequisites": [
            "owner-approved validation mode before any external use",
            "specific buyer segment and sample workflow chosen by owner",
            "action-wide preflight before outreach, publication, or forms",
        ],
        "pricing_hypothesis": [
            "$750-$1,500 paid diagnostic / founder-speed tier",
            "$1,500-$3,000 focused implementation blueprint",
            "higher implementation work requires separate validation and approval",
        ],
        "pricing_claim_type": "hypothesis; vendor pricing pages are budget proxies, not direct willingness-to-pay proof for Y*Bridge.",
        "proof_evidence_basis": _source_ids(ai_ops),
        "customer_facing_usable_source_ids": usable_ids,
        "evidence_quality_notes": [
            f"{len(ai_ops)} AI-ops-relevant public sources were available from E6.",
            f"{noisy_count} sources included raw page boilerplate and require cleaned summaries.",
            "No claim here says customer validation has happened.",
        ],
        "remaining_uncertainties": [
            "whether the target buyer feels urgency within the proposed price range",
            "whether a 48h blueprint is valuable enough without hands-on implementation",
            "which channel can reach buyers with low owner burden",
            "which proof artifact best reduces the trust gap",
        ],
        "validation_question": "Would a technical founder or AI-heavy small team seriously consider paying for a 48h AI Ops Operating Room Blueprint before buying or wiring more AI tools?",
        "kill_condition": "Kill or revise if 3-5 approved validation conversations or equivalent owner-approved feedback produce no price curiosity, no workflow sample, and no urgency signal.",
        "owner_approval_boundary": "This packet is internal and validation-ready only. Outreach, landing-page publication, forms, payments, accounts, or customer contact require separate owner approval and preflight.",
        "external_action_executed": False,
        "customer_validation_claimed": False,
    }


def render_e7_validation_ready_offer_packet(packet: Dict[str, Any]) -> str:
    landscape = packet["competitor_substitute_no_action_diy_landscape"]
    lines = [
        "# E7 Validation-Ready Offer Packet",
        "",
        f"- offer_name: {packet['offer_name']}",
        f"- target_buyer: {packet['target_buyer']}",
        f"- customer_validation_claimed: {packet['customer_validation_claimed']}",
        f"- external_action_executed: {packet['external_action_executed']}",
        "",
        "## Executive Summary",
        f"{packet['offer_name']} is a 48h internal-to-external validation candidate for teams that have AI tools but lack a governed operating room. E6 made the thesis market-backed; E7 makes it validation-ready without executing validation.",
        "",
        "## Buyer Job-To-Be-Done",
        packet["buyer_job_to_be_done"],
        "",
        "## Urgent Pain",
        packet["urgent_pain"],
        "",
        "## Evidence-Backed Market Category",
        packet["evidence_backed_market_category"],
        "",
        "## Current Alternatives",
        f"- competitors: {', '.join(landscape['competitors'])}",
        f"- substitutes: {', '.join(landscape['substitutes'])}",
        f"- no-action: {landscape['no_action']}",
        f"- DIY: {landscape['diy']}",
        "",
        "## Why Alternatives Are Insufficient",
        "Incumbent tools can provide automation, evaluation, observability, or workflow building blocks, but they do not by themselves create a CEO-readable operating room with mission routing, evidence provenance, approval boundaries, and CZL residual closure.",
        "",
        "## Y*Bridge Wedge",
        packet["ybridge_wedge"],
        "",
        "## Why Buyer Might Not Choose Us",
    ]
    lines.extend(f"- {item}" for item in packet["why_buyer_might_not_choose_us"])
    lines.extend(["", "## Trust Gap", packet["trust_gap"], "", "## Exact 48h Deliverable"])
    lines.extend(f"- {item}" for item in packet["deliverable_48h"])
    lines.extend(["", "## Delivery Scope"])
    lines.extend(f"- {item}" for item in packet["delivery_scope"])
    lines.extend(["", "## What Is Excluded"])
    lines.extend(f"- {item}" for item in packet["exclusions"])
    lines.extend(["", "## Prerequisites"])
    lines.extend(f"- {item}" for item in packet["prerequisites"])
    lines.extend(["", "## Pricing Hypothesis"])
    lines.extend(f"- {item}" for item in packet["pricing_hypothesis"])
    lines.extend(["", f"pricing_claim_type: {packet['pricing_claim_type']}"])
    lines.extend(["", "## Proof / Evidence Basis"])
    lines.append(f"- source_ids: {', '.join(packet['proof_evidence_basis']) or 'none'}")
    lines.append(f"- customer_facing_usable_source_ids: {', '.join(packet['customer_facing_usable_source_ids']) or 'none'}")
    lines.extend(["", "## Evidence Quality Notes"])
    lines.extend(f"- {item}" for item in packet["evidence_quality_notes"])
    lines.extend(["", "## Remaining Uncertainties"])
    lines.extend(f"- {item}" for item in packet["remaining_uncertainties"])
    lines.extend(
        [
            "",
            "## Validation Question",
            packet["validation_question"],
            "",
            "## Kill Condition",
            packet["kill_condition"],
            "",
            "## Owner Approval Boundary",
            packet["owner_approval_boundary"],
        ]
    )
    return "\n".join(lines)
