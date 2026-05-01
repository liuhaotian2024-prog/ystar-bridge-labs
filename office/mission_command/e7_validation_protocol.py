from __future__ import annotations

from typing import Any, Dict, List


DRAFT_WARNING = "\n".join(
    [
        "DRAFT ONLY.",
        "NOT SENT.",
        "NOT PUBLISHED.",
        "OWNER APPROVAL REQUIRED BEFORE EXTERNAL USE.",
        "NO CUSTOMER CONTACT EXECUTED.",
    ]
)


def build_e7_validation_protocol() -> Dict[str, Any]:
    return {
        "validation_goal": "Determine whether a specific buyer segment would pay for or seriously consider the 48h AI Ops Operating Room Blueprint.",
        "target_segment": "technical founders, AI-heavy small teams, or operations leads with active AI tooling and unclear operating boundaries",
        "allowed_validation_modes": [
            "owner-approved direct outreach to a small number of known contacts",
            "owner-approved public post",
            "owner-approved landing page",
            "owner-approved expert feedback request",
            "owner-approved founder interview request",
            "owner-approved internal benchmark against a real workflow sample",
        ],
        "forbidden_validation_modes": [
            "automated bulk outreach",
            "cold spam",
            "scraped leads",
            "form submission",
            "payment collection",
            "account creation",
            "publication without approval",
            "customer contact without approval",
            "contract/legal commitment",
            "production system changes",
        ],
        "sample_size_options": [
            "3-person qualitative feedback test",
            "5-10 targeted outreach test",
            "1 public post / landing page smoke test",
            "1 internal benchmark demo",
        ],
        "success_signals": [
            "buyer asks for price",
            "buyer asks for example deliverable",
            "buyer offers a real workflow to analyze",
            "buyer says they would pay within stated range",
            "buyer requests follow-up",
            "buyer introduces another potential buyer",
        ],
        "disconfirming_signals": [
            "buyer says tools already solve it",
            "buyer sees it as generic consulting",
            "buyer does not feel urgency",
            "buyer rejects price range",
            "buyer needs implementation not diagnostic",
            "buyer cannot identify owner for decision",
        ],
        "stop_conditions": [
            "safety boundary unclear",
            "any external action not explicitly approved",
            "more than approved contact count",
            "evidence contradicts top thesis",
            "owner burden exceeds threshold",
        ],
        "residual_learning_update": [
            "update offer thesis",
            "update market reality model",
            "update opportunity ranking",
            "do not write CIEU/core memory unless separately approved",
        ],
        "owner_burden_minimization": "Owner should choose one validation mode, approve exact count/channel/message/stop condition, and review results. Aiden prepares and summarizes; owner should not become the manual operator.",
        "safety_preflight_requirements": [
            "semantic action classification before E8",
            "owner approval packet before external use",
            "gov/company preflight for any external side effect",
            "no payment/form/account/publication without separate approval",
        ],
        "external_action_executed": False,
    }


def render_e7_validation_protocol(protocol: Dict[str, Any]) -> str:
    lines = [
        "# E7 Commercial Validation Protocol",
        "",
        f"- external_action_executed: {protocol['external_action_executed']}",
        "",
        "## Validation Objective",
        protocol["validation_goal"],
        "",
        "## Target Segment",
        protocol["target_segment"],
        "",
        "## Allowed Validation Modes",
    ]
    lines.extend(f"- {item}" for item in protocol["allowed_validation_modes"])
    lines.extend(["", "## Forbidden Validation Modes"])
    lines.extend(f"- {item}" for item in protocol["forbidden_validation_modes"])
    lines.extend(["", "## Sample Size Options"])
    lines.extend(f"- {item}" for item in protocol["sample_size_options"])
    lines.extend(["", "## Success Criteria"])
    lines.extend(f"- {item}" for item in protocol["success_signals"])
    lines.extend(["", "## Disconfirming Signals"])
    lines.extend(f"- {item}" for item in protocol["disconfirming_signals"])
    lines.extend(["", "## Stop Conditions"])
    lines.extend(f"- {item}" for item in protocol["stop_conditions"])
    lines.extend(["", "## Residual Learning Update"])
    lines.extend(f"- {item}" for item in protocol["residual_learning_update"])
    lines.extend(["", "## Owner Burden Minimization", protocol["owner_burden_minimization"], "", "## Safety / Preflight Requirements"])
    lines.extend(f"- {item}" for item in protocol["safety_preflight_requirements"])
    return "\n".join(lines)


def render_e7_outreach_draft() -> str:
    return "\n\n".join(
        [
            DRAFT_WARNING,
            "# E7 Outreach Draft",
            "Subject: quick feedback on a 48h AI ops blueprint idea",
            "Hi [Name],",
            "I’m testing whether technical founders or AI-heavy small teams need a concise 48h AI Ops Operating Room Blueprint: a decision artifact that maps AI-agent work, approvals, evidence, and unsafe-action boundaries before teams buy or wire more tools.",
            "This is not a claim that you have this problem. If useful, I’d value 10 minutes of feedback on whether this would be worth paying for, what would make it credible, and what would make you ignore it.",
            "No external action should use this draft until the owner approves the exact recipient count, channel, message, and stop condition.",
            "Respectfully, [Owner/Y*Bridge]",
        ]
    )


def render_e7_landing_page_draft() -> str:
    return "\n\n".join(
        [
            DRAFT_WARNING,
            "# E7 Landing Page Draft",
            "## Hero",
            "Turn scattered AI tools into a governed operating room in 48 hours.",
            "## Problem",
            "Teams can buy AI tooling, but still lack mission routing, approval boundaries, evidence trails, and safe action gates.",
            "## Who It Is For",
            "Technical founders, AI-heavy small teams, and operations leads trying to make AI-agent work operational instead of experimental.",
            "## What You Receive",
            "A workflow map, operating-room blueprint, approval/action-boundary matrix, top bottlenecks, risk boundary, and next-decision packet.",
            "## What Is Excluded",
            "No production implementation, no system access, no legal certification, no payment setup, and no external automation.",
            "## Evidence-Backed Context",
            "Public E6 source evidence shows active categories around AI evaluation, automation platforms, agentic workflow tooling, and implementation alternatives. This does not prove buyer willingness to pay.",
            "## Pricing Hypothesis",
            "$750-$1,500 diagnostic or $1,500-$3,000 focused blueprint, pending validation.",
            "## CTA Draft Only",
            "Request a sample blueprint review. This CTA is not active and must not be published without owner approval.",
        ]
    )


def render_e7_demo_call_script() -> str:
    return "\n\n".join(
        [
            DRAFT_WARNING,
            "# E7 Demo Call Script",
            "## Opening",
            "I’m validating whether a 48h AI Ops Operating Room Blueprint would help teams make AI-agent workflows safer and more operational.",
            "## Discovery Questions",
            "- What AI tools or agents are already in your workflow?",
            "- Where does work get stuck between tool output and business decision?",
            "- Who approves external actions, customer-facing messages, or production changes?",
            "- What evidence would make an AI-generated recommendation trustworthy?",
            "- What current tools or internal processes would this need to beat?",
            "- What budget or approval path would a 48h blueprint need to fit?",
            "## Objection Handling",
            "If the buyer says tools already solve it, ask which tool owns approvals, evidence provenance, and cross-team action boundaries.",
            "If the buyer says it sounds like consulting, ask what concrete artifact would make it operational rather than advisory.",
            "## Close",
            "Would you seriously consider paying within the stated range for this if the sample matched your workflow?",
        ]
    )


def render_e7_validation_question_set() -> str:
    return "\n\n".join(
        [
            DRAFT_WARNING,
            "# E7 Validation Survey Or Question Set",
            "- How severe is the pain of turning AI tools into an operational workflow?",
            "- What are you using now instead: internal process, SaaS tool, consultant, or no action?",
            "- How urgent is this in the next 30 days?",
            "- Would a 48h blueprint be valuable without implementation?",
            "- Which price range would feel plausible: under $750, $750-$1,500, $1,500-$3,000, or more with implementation?",
            "- What proof would reduce the trust gap?",
            "- Who would approve this purchase or validation step?",
            "- What answer would make us stop pursuing this offer?",
        ]
    )
