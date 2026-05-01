from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class MarketRealityProfile:
    opportunity_id: str
    buyer: str
    budget_channel: str
    buying_trigger: str
    buying_process: str
    direct_competitors: List[str]
    substitutes: List[str]
    no_action_alternative: str
    diy_alternative: str
    incumbent_tools: List[str]
    incumbent_consultants: List[str]
    pricing_references: List[str]
    category: str
    differentiation_wedge: str
    why_buyer_might_not_choose_us: List[str]
    trust_gap: str
    market_evidence_refs: List[str]
    confidence: str
    missing_evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _keyword_profile(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    title = str(opportunity.get("title", "")).lower()
    if "coding-agent" in title or "mcp" in title or "governance" in title:
        return {
            "category": "AI engineering governance / agent safety advisory",
            "direct_competitors": [
                "internal platform/security teams",
                "AI coding-assistant governance consultants",
                "DevSecOps advisory firms",
            ],
            "substitutes": [
                "standard code review policy",
                "manual checklist process",
                "disable or limit AI coding agents",
            ],
            "incumbent_tools": ["GitHub branch protection", "CI policy checks", "security scanners", "MCP gateway tools"],
            "incumbent_consultants": ["DevSecOps consultants", "AI transformation advisors"],
            "budget_channel": "engineering productivity, security, or platform tooling budget",
        }
    if "incident" in title or "postmortem" in title:
        return {
            "category": "AI incident postmortem / operational risk review",
            "direct_competitors": ["incident response consultants", "platform reliability advisors"],
            "substitutes": ["internal retro", "do nothing until next incident", "generic RCA template"],
            "incumbent_tools": ["incident trackers", "observability dashboards", "runbooks"],
            "incumbent_consultants": ["SRE consultants", "AI risk consultants"],
            "budget_channel": "risk, reliability, or executive emergency budget",
        }
    if "cockpit" in title or "operating room" in title or "runtime setup" in title:
        return {
            "category": "AI operations setup / implementation advisory",
            "direct_competitors": ["automation agencies", "AI ops consultants", "internal ops builders"],
            "substitutes": ["Notion/Linear workspace", "custom scripts", "chat-only AI use"],
            "incumbent_tools": ["Notion", "Linear", "Zapier", "LangGraph templates", "agent dashboards"],
            "incumbent_consultants": ["AI implementation agencies", "fractional ops advisors"],
            "budget_channel": "operations, founder productivity, or implementation budget",
        }
    return {
        "category": "AI workflow diagnostic / founder advisory",
        "direct_competitors": ["AI workflow consultants", "fractional CTO advisors", "automation agencies"],
        "substitutes": ["internal trial-and-error", "generic ChatGPT advice", "buy another SaaS tool"],
        "incumbent_tools": ["ChatGPT Team", "Claude", "Cursor", "Notion AI", "workflow automation tools"],
        "incumbent_consultants": ["AI adoption consultants", "productivity coaches"],
        "budget_channel": "founder productivity, operations improvement, or urgent advisory budget",
    }


def build_market_reality_profile(
    opportunity: Dict[str, Any],
    live_evidence_refs: List[str] | None = None,
) -> Dict[str, Any]:
    live_refs = live_evidence_refs or []
    profile = _keyword_profile(opportunity)
    buyer = str(opportunity.get("buyer", "Founder/operator evaluating AI-agent work."))
    pain = str(opportunity.get("pain", "Unclear AI workflow value, safety, or execution bottleneck."))
    confidence = "medium_live_evidence" if live_refs else "low_internal_hypothesis_only"
    missing = [] if live_refs else [
        "live public competitor/pricing evidence",
        "fresh buyer-language evidence",
        "current willingness-to-pay proxy",
        "specific channel access evidence",
    ]
    return MarketRealityProfile(
        opportunity_id=str(opportunity.get("opportunity_id", "unknown_opportunity")),
        buyer=buyer,
        budget_channel=profile["budget_channel"],
        buying_trigger=f"Buyer feels acute pain: {pain}",
        buying_process="Likely founder/operator-led manual evaluation first; enterprise procurement is not assumed.",
        direct_competitors=profile["direct_competitors"],
        substitutes=profile["substitutes"],
        no_action_alternative="Keep current AI workflow and absorb delay, confusion, or governance risk.",
        diy_alternative="Use internal staff plus generic AI tools to build a checklist or workflow manually.",
        incumbent_tools=profile["incumbent_tools"],
        incumbent_consultants=profile["incumbent_consultants"],
        pricing_references=[
            "internal hypothesis: $750 entry diagnostic",
            "internal hypothesis: $1500 focused sprint",
            "internal hypothesis: $3000 deeper advisory",
        ],
        category=profile["category"],
        differentiation_wedge="Y*Bridge combines M Triangle value pressure, deterministic governance, action preflight, and CEO-readable mission outputs.",
        why_buyer_might_not_choose_us=[
            "Insufficient public proof or trust signal.",
            "Buyer prefers an incumbent consultant or internal team.",
            "Pain is interesting but not urgent enough to pay within 7 days.",
            "Offer sounds like governance overhead instead of faster value production.",
        ],
        trust_gap="Live market evidence and a concrete sample are needed before claiming market-backed demand.",
        market_evidence_refs=live_refs,
        confidence=confidence,
        missing_evidence=missing,
    ).to_dict()


def profile_has_competition(profile: Dict[str, Any]) -> bool:
    return bool(profile.get("direct_competitors")) and bool(profile.get("substitutes")) and bool(profile.get("no_action_alternative")) and bool(profile.get("diy_alternative"))
