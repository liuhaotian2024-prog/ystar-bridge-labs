from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List


DEFAULT_RESEARCH_TARGETS = [
    "Agent Workflow Bottleneck Diagnosis",
    "Founder AI Workflow Audit / CEO Command Brief",
    "Coding-Agent Governance Audit",
]


@dataclass(frozen=True)
class Tier1ResearchMissionPacket:
    packet_id: str
    mission_goal: str
    research_questions: List[str]
    target_evidence_types: List[str]
    source_categories: List[str]
    max_search_queries: int
    max_pages_read: int
    max_domains: int
    no_login: bool
    no_contact: bool
    no_form_submit: bool
    no_payment: bool
    no_publication: bool
    stop_conditions: List[str]
    budget_receipt_format: Dict[str, Any]
    evidence_packet_format: Dict[str, Any]
    recommendation_update_criteria: List[str]
    owner_approval_options: List[str]
    live_research_executed: bool = False
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _packet_id(mission_goal: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(mission_goal.encode("utf-8")).hexdigest()[:8]
    return f"tier1_read_only_research_{stamp}_{digest}"


def build_tier1_research_mission_packet() -> Dict[str, Any]:
    mission_goal = (
        "Validate or falsify Agent Workflow Bottleneck Diagnosis against Founder AI Workflow Audit "
        "and Coding-Agent Governance Audit using bounded public read-only evidence."
    )
    packet = Tier1ResearchMissionPacket(
        packet_id=_packet_id(mission_goal),
        mission_goal=mission_goal,
        research_questions=[
            "Which buyer pain language appears most often around agent workflow bottlenecks, founder AI workflow audits, and coding-agent governance?",
            "Which path shows the clearest urgent, budget-adjacent problem without requiring customer contact?",
            "Which path can be tested with a 48h sample deliverable and lowest owner burden?",
            "What public evidence would falsify Agent Workflow Bottleneck Diagnosis as the default next path?",
            "What pricing or service-packaging references exist for comparable diagnostic/advisory offers?",
        ],
        target_evidence_types=[
            "public pain-language snippets summarized in our words",
            "buyer segment signals",
            "pricing/reference signals",
            "competitor or adjacent service examples",
            "delivery expectation and trust-gap evidence",
            "conflicting evidence against the current default",
        ],
        source_categories=[
            "public founder/operator posts",
            "public engineering leadership posts",
            "AI tooling/community discussions",
            "public product/service pages",
            "public documentation and comparison pages",
            "public pricing/service-package references",
        ],
        max_search_queries=10,
        max_pages_read=15,
        max_domains=8,
        no_login=True,
        no_contact=True,
        no_form_submit=True,
        no_payment=True,
        no_publication=True,
        stop_conditions=[
            "budget limit reached",
            "page limit reached",
            "domain limit reached",
            "login, paywall, form, file upload, or private content encountered",
            "source asks for personal data or credentials",
            "evidence becomes repetitive enough to update or falsify the default recommendation",
        ],
        budget_receipt_format={
            "queries_used": 0,
            "pages_read": 0,
            "domains_seen": [],
            "stopped_because": "",
            "no_login": True,
            "no_contact": True,
            "no_form_submit": True,
            "no_payment": True,
            "no_publication": True,
        },
        evidence_packet_format={
            "source_url": "",
            "source_category": "",
            "credibility_notes": "",
            "summary": "",
            "pain_signal": "",
            "money_path_implication": "",
            "supports_paths": [],
            "weakens_paths": [],
            "conflicts_or_uncertainty": "",
            "private_or_secret_content_included": False,
        },
        recommendation_update_criteria=[
            "At least two independent public sources support urgent agent workflow bottleneck pain more strongly than alternatives.",
            "Or, Founder AI Workflow Audit / CEO Command Brief shows clearer buyer language, lower delivery burden, and faster disconfirmation.",
            "Or, Coding-Agent Governance Audit shows stronger budget/trust urgency than the default.",
            "If evidence is weak or contradictory, keep the plan internal-only and request more evidence instead of outreach.",
        ],
        owner_approval_options=["approve", "reject", "request_revision", "hold"],
    )
    return packet.to_dict()


def render_tier1_research_mission_packet_markdown(packet: Dict[str, Any]) -> str:
    lines = [
        "# E1.6 Tier 1 Read-Only Evidence Mission Packet",
        "",
        f"- packet_id: {packet['packet_id']}",
        f"- mission_goal: {packet['mission_goal']}",
        f"- live_research_executed: {packet['live_research_executed']}",
        f"- external_action_executed: {packet['external_action_executed']}",
        "",
        "## Research Questions",
    ]
    lines.extend(f"- {item}" for item in packet["research_questions"])
    lines.extend(["", "## Target Evidence Types"])
    lines.extend(f"- {item}" for item in packet["target_evidence_types"])
    lines.extend(["", "## Source Categories"])
    lines.extend(f"- {item}" for item in packet["source_categories"])
    lines.extend(
        [
            "",
            "## Budget",
            f"- max_search_queries: {packet['max_search_queries']}",
            f"- max_pages_read: {packet['max_pages_read']}",
            f"- max_domains: {packet['max_domains']}",
            f"- no_login: {packet['no_login']}",
            f"- no_contact: {packet['no_contact']}",
            f"- no_form_submit: {packet['no_form_submit']}",
            f"- no_payment: {packet['no_payment']}",
            f"- no_publication: {packet['no_publication']}",
            "",
            "## Stop Conditions",
        ]
    )
    lines.extend(f"- {item}" for item in packet["stop_conditions"])
    lines.extend(
        [
            "",
            "## Budget Receipt Format",
            "```json",
            json.dumps(packet["budget_receipt_format"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Evidence Packet Format",
            "```json",
            json.dumps(packet["evidence_packet_format"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Enough Evidence To Update Recommendation",
        ]
    )
    lines.extend(f"- {item}" for item in packet["recommendation_update_criteria"])
    lines.extend(
        [
            "",
            "## Owner Approval Options",
            f"- {', '.join(packet['owner_approval_options'])}",
            "",
            "Boundary: this packet prepares approval for a future Tier 1 read-only evidence mission only. It does not run live research, contact customers, send email, publish, pay, submit forms, register obligations, or write CIEU/core DB.",
        ]
    )
    return "\n".join(lines)
