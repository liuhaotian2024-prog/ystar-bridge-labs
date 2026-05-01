from __future__ import annotations

from typing import Any, Dict, List


def build_e6_offer_thesis(evaluation: Dict[str, Any], bundle: Dict[str, Any]) -> Dict[str, Any]:
    top = evaluation["rows"][0]
    opportunity = top["opportunity"]
    profile = top["market_reality_profile"]
    sources = [source for source in bundle.get("sources", []) if source.get("source_id") in top["source_ids"]]
    thesis_status = "evidence_backed" if evaluation["default_is_market_backed"] else "blocked_insufficient_public_evidence"
    source_ids = top["source_ids"]
    pricing_ids = [source["source_id"] for source in sources if source.get("pricing_signal") or source.get("budget_signal")]
    pain_ids = [source["source_id"] for source in sources if source.get("buyer_pain_signal")]
    competitor_ids = [source["source_id"] for source in sources if source.get("competitor_signal") or source.get("substitute_signal")]
    if thesis_status == "evidence_backed":
        return {
            "thesis_status": thesis_status,
            "selected_target_buyer": opportunity["buyer"],
            "job_to_be_done": "Help the buyer decide and act on an AI-agent/company-runtime bottleneck within 48 hours without unsafe external action.",
            "urgent_pain": opportunity["pain"],
            "evidence_basis": source_ids,
            "market_category": profile["category"],
            "competitors": profile["direct_competitors"],
            "substitutes": profile["substitutes"],
            "no_action_alternative": profile["no_action_alternative"],
            "diy_alternative": profile["diy_alternative"],
            "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
            "ybridge_differentiation_wedge": profile["differentiation_wedge"],
            "trust_gap": profile["trust_gap"],
            "offer_name": f"48h {opportunity['title']} Brief",
            "source_ids_supporting_pain": pain_ids,
            "source_ids_supporting_pricing_budget": pricing_ids,
            "source_ids_supporting_competition": competitor_ids,
            "48h_paid_signal_offer": opportunity["first_experiment"],
            "pricing_hypothesis": profile["pricing_references"],
            "delivery_scope": [
                "diagnostic findings",
                "evidence-backed competitor/substitute comparison",
                "48h action recommendation",
                "risk/governance boundary",
                "kill condition and residual review plan",
            ],
            "exclusions": [
                "customer outreach by Aiden",
                "implementation without separate approval",
                "legal/security certification",
                "payment setup",
                "core DB/brain/memory/CIEU writeback",
            ],
            "assumptions": [
                "Public evidence represents enough category pressure to justify a next validation step.",
                "A buyer values a concise decision artifact more than generic AI advice.",
            ],
            "risk_governance_boundary": "No customer contact, publication, payment, forms, account creation, obligation registration, or core writeback is approved.",
            "counterfactuals": [
                "If buyer pain is actually solved by incumbent tools, downgrade the offer.",
                "If trust gap remains higher than urgency, run another evidence pass before validation.",
            ],
            "validation_question": "Would this buyer pay for a 48h diagnostic because it beats no-action, DIY, or incumbent alternatives?",
            "kill_condition": opportunity["kill_condition"],
            "next_owner_decision": "approve_or_revise_next_validation_step",
            "customer_contact_still_blocked": True,
        }
    return {
        "thesis_status": thesis_status,
        "strongest_internal_hypothesis": opportunity["title"],
        "evidence_collected": source_ids,
        "why_insufficient": [
            "Top path did not meet the independent-source market-backing threshold.",
            "Evidence must include stronger buyer pain, pricing/budget, and competitor/substitute signals before customer validation.",
        ],
        "exact_missing_evidence": [
            "two independent source domains supporting the same top opportunity",
            "pricing or budget proxy for the buyer category",
            "clear buyer-process or urgency language",
        ],
        "revised_seed_or_next_research_action": "Add or revise public no-login seeds for the top opportunity, then rerun source-seeded page-read research.",
        "no_customer_contact_recommendation": True,
        "selected_target_buyer": opportunity["buyer"],
        "job_to_be_done": "Resolve the first-revenue offer hypothesis without overclaiming market proof.",
        "urgent_pain": opportunity["pain"],
        "market_category": profile["category"],
        "competitors": profile["direct_competitors"],
        "substitutes": profile["substitutes"],
        "no_action_alternative": profile["no_action_alternative"],
        "diy_alternative": profile["diy_alternative"],
        "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
        "ybridge_differentiation_wedge": profile["differentiation_wedge"],
        "trust_gap": profile["trust_gap"],
        "48h_paid_signal_offer": opportunity["first_experiment"],
        "pricing_hypothesis": profile["pricing_references"],
        "delivery_scope": ["owner-review sample only until evidence is sufficient"],
        "exclusions": ["customer contact", "email/message", "publication", "payment", "account creation", "form submission", "core writeback"],
        "validation_question": "What exact public evidence is missing before this can be tested with a buyer?",
        "kill_condition": opportunity["kill_condition"],
        "next_owner_decision": "request_revision_more_public_evidence",
        "customer_contact_still_blocked": True,
    }


def render_e6_offer_thesis(thesis: Dict[str, Any]) -> str:
    lines = [
        "# E6 Offer Thesis",
        "",
        f"- thesis_status: {thesis['thesis_status']}",
        f"- selected_target_buyer: {thesis.get('selected_target_buyer')}",
        f"- job_to_be_done: {thesis.get('job_to_be_done')}",
        f"- urgent_pain: {thesis.get('urgent_pain')}",
        f"- market_category: {thesis.get('market_category')}",
        f"- customer_contact_still_blocked: {thesis.get('customer_contact_still_blocked')}",
        "",
        "## Evidence Basis",
    ]
    basis = thesis.get("evidence_basis") or thesis.get("evidence_collected") or []
    lines.extend(f"- {item}" for item in basis) if basis else lines.append("- none")
    if thesis["thesis_status"] == "evidence_backed":
        lines.extend(
            [
                "",
                f"- source_ids_supporting_pain: {', '.join(thesis['source_ids_supporting_pain']) or 'none'}",
                f"- source_ids_supporting_pricing_budget: {', '.join(thesis['source_ids_supporting_pricing_budget']) or 'none'}",
                f"- source_ids_supporting_competition: {', '.join(thesis['source_ids_supporting_competition']) or 'none'}",
            ]
        )
    else:
        lines.extend(["", "## Why Evidence Is Insufficient"])
        lines.extend(f"- {item}" for item in thesis["why_insufficient"])
        lines.extend(["", "## Exact Missing Evidence"])
        lines.extend(f"- {item}" for item in thesis["exact_missing_evidence"])
        lines.extend(["", f"revised_seed_or_next_research_action: {thesis['revised_seed_or_next_research_action']}"])
    lines.extend(["", "## Competitors / Substitutes / Alternatives"])
    lines.append(f"- competitors: {', '.join(thesis['competitors'])}")
    lines.append(f"- substitutes: {', '.join(thesis['substitutes'])}")
    lines.append(f"- no_action_alternative: {thesis['no_action_alternative']}")
    lines.append(f"- DIY_alternative: {thesis['diy_alternative']}")
    lines.extend(["", "## Why Buyer Might Not Choose Us"])
    lines.extend(f"- {item}" for item in thesis["why_buyer_might_not_choose_us"])
    lines.extend(["", "## Y*Bridge Differentiation Wedge", thesis["ybridge_differentiation_wedge"]])
    lines.extend(["", "## Trust Gap", thesis["trust_gap"]])
    lines.extend(["", "## 48h Paid-Signal Offer", thesis["48h_paid_signal_offer"]])
    lines.extend(["", "## Pricing Hypothesis"])
    lines.extend(f"- {item}" for item in thesis["pricing_hypothesis"])
    lines.extend(["", "## Delivery Scope"])
    lines.extend(f"- {item}" for item in thesis["delivery_scope"])
    lines.extend(["", "## Exclusions"])
    lines.extend(f"- {item}" for item in thesis["exclusions"])
    if thesis.get("assumptions"):
        lines.extend(["", "## Assumptions"])
        lines.extend(f"- {item}" for item in thesis["assumptions"])
    lines.extend(["", "## Risk / Governance Boundary", thesis.get("risk_governance_boundary", "No external action is approved by default.")])
    if thesis.get("counterfactuals"):
        lines.extend(["", "## Counterfactuals"])
        lines.extend(f"- {item}" for item in thesis["counterfactuals"])
    lines.extend(["", "## Validation Question", thesis["validation_question"], "", "## Kill Condition", thesis["kill_condition"], "", "## Next Owner Decision", thesis["next_owner_decision"]])
    return "\n".join(lines)
