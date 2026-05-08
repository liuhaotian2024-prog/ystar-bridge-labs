"""Chat-prefix router for the governed Aiden CEO meeting room.

This module makes the owner-facing convention explicit:

``Aiden: ...`` or ``Aiden：...`` means the message should be routed to the
governed Aiden meeting room. Unprefixed messages stay outside that route so
Codex does not implicitly impersonate the CEO principal.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from office.aiden_meeting_room.governed_gateway import answer_owner_governed_text
from office.mission_command.e104_adaptive_market_intelligence_strategy_runtime import (
    run_e104_adaptive_market_intelligence_strategy_session,
)


AIDEN_MEETING_ROOM_PREFIXES = ("Aiden:", "Aiden：", "aiden:", "aiden：")
MEETING_ROOM_PROTOCOL = "AidenPrefixV1"
STRATEGY_RUNTIME_PROTOCOL = "AidenStrategyRuntimeV1"

_STRATEGY_RUNTIME_TERMS = (
    "strategy",
    "strategic",
    "market",
    "first cash",
    "revenue",
    "pricing",
    "customer",
    "product",
    "offer",
    "competitor",
    "workflow",
    "赚钱",
    "收入",
    "第一笔钱",
    "现金",
    "市场",
    "战略",
    "策略",
    "产品",
    "客户",
    "竞品",
    "价格",
    "定价",
    "会计事务所",
    "cpa",
)


@dataclass(frozen=True)
class AidenChatRoute:
    route: str
    prefixed: bool
    owner_message: str
    response_text: str | None
    protocol: str = MEETING_ROOM_PROTOCOL
    ceo_actor: str = "Aiden"
    codex_actor: str = "Codex executor bridge"
    adaptive_governance_gate_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "prefixed": self.prefixed,
            "owner_message": self.owner_message,
            "response_text": self.response_text,
            "protocol": self.protocol,
            "ceo_actor": self.ceo_actor,
            "codex_actor": self.codex_actor,
            "adaptive_governance_gate_required": self.adaptive_governance_gate_required,
        }


def is_aiden_meeting_room_message(message: str) -> bool:
    """Return true only when the owner explicitly invokes Aiden."""

    stripped = (message or "").lstrip()
    return any(stripped.startswith(prefix) for prefix in AIDEN_MEETING_ROOM_PREFIXES)


def strip_aiden_meeting_room_prefix(message: str) -> str:
    """Remove the explicit Aiden prefix and return the owner message."""

    stripped = (message or "").lstrip()
    for prefix in AIDEN_MEETING_ROOM_PREFIXES:
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return stripped


def build_empty_aiden_prefix_revision() -> str:
    return (
        "Adaptive Governance Gate: REQUIRE_REVISION\n"
        "The `Aiden:` meeting-room prefix was present, but no owner message followed it.\n"
        "Correct path: provide the owner intent after `Aiden:` so the governed Aiden "
        "behavior center can answer through brain provenance, Y-star-gov validation, "
        "CIEUStore recording, and no-external-action route gating."
    )


def is_aiden_strategy_runtime_message(owner_message: str) -> bool:
    """Return true when Aiden must use the governed strategy runtime."""

    text = (owner_message or "").lower()
    return any(term in text for term in _STRATEGY_RUNTIME_TERMS)


def default_aiden_strategy_cieu_db(repo_root: Path) -> Path:
    runtime_dir = repo_root / ".runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / "aiden_strategy_runtime.db"


def render_aiden_strategy_runtime_response(result: dict[str, Any]) -> str:
    strategy = result["strategy"]
    receipt = result["CEO_runtime_receipt"]
    selected = strategy["selected_strategy"]
    pricing = strategy["offer_and_pricing_hypotheses"]["entry_offer"]
    competitors = strategy["adaptive_market_governance_gates"]["competitor_saturation_scan"]["competitors"]
    packet = strategy["next_L4_feedback_owner_decision_packet"]
    route_scores = strategy["route_scoring"][:5]
    offer = strategy["customer_visible_offer_shape"]
    cpa_status = strategy["cpa_route_status"]
    founder_fit = strategy["founder_market_fit_assessment"]
    competitor_lines = "\n".join(
        f"- {item['competitor_id']}: {item['threat_level']}" for item in competitors[:8]
    )
    route_lines = "\n".join(
        f"- {item['route_id']}: {item['first_cash_score']}" for item in route_scores
    )
    visible_lines = "\n".join(f"- {item}" for item in offer["visible_deliverables"])
    return (
        "CEO Strategy Runtime: E104_ADAPTIVE_MARKET_INTELLIGENCE_OPEN_WORLD_STRATEGY\n"
        "This Aiden strategy question was auto-upgraded from meeting-room answer "
        "to the governed 6D brain + live market refresh + open-world strategy runtime.\n\n"
        f"Y-star-gov strategic decision: {receipt['Y_star_gov_strategic_decision']}\n"
        f"Y-star-gov market refresh decision: {receipt['Y_star_gov_market_refresh_decision']}\n"
        f"CIEUStore written: {str(receipt['CIEUStore_written']).lower()}\n"
        f"Brain unique nodes: {receipt['brain_unique_nodes']}\n"
        f"External public-read evidence items: {receipt['external_evidence_count']}\n"
        f"CIEU events: {receipt['CIEU_event_count']}\n\n"
        "Selected first-cash path:\n"
        f"{selected['current_best_first_cash_path']}\n"
        f"- selected_route_id: {selected['selected_route_id']}\n\n"
        "Why this now:\n"
        f"{selected['why_this_path_now']}\n\n"
        "Why CPA review bottleneck was demoted:\n"
        f"{selected['why_not_cpa_first']}\n"
        f"- CPA route status: {cpa_status['status']}\n"
        f"- CPA validation question: {cpa_status['strongest_validation_question']}\n\n"
        "Founder-market fit:\n"
        f"- founder_is_cpa: {str(founder_fit['founder_is_cpa']).lower()}\n"
        f"- strong_fit_assets: {', '.join(founder_fit['strong_fit_assets'][:4])}\n\n"
        "Route comparison:\n"
        f"{route_lines}\n\n"
        "Competitor saturation scan:\n"
        f"{competitor_lines}\n"
        f"- saturation: {strategy['competitor_saturation_assessment']['CPA_review_bottleneck_route']}\n\n"
        "Customer-visible offer shape:\n"
        f"- {offer['offer_name']}\n"
        f"{visible_lines}\n\n"
        "Pricing hypothesis, not validation:\n"
        f"- {pricing['name']}: {pricing['hypothesis_price_range_usd']}\n"
        f"- status: {strategy['offer_and_pricing_hypotheses']['pricing_validation_status']}\n\n"
        "Strongest validation question:\n"
        f"Will a founder/operator using AI coding agents consider paying {pricing['hypothesis_price_range_usd']} "
        "for a 48-hour AI Agent Control Room Rescue Brief that prevents repo drift, prompt-scope creep, "
        "and unsafe delivery?\n\n"
        "Next owner-gated L4 packet:\n"
        f"- packet_id: {packet['packet_id']}\n"
        f"- target_profile: {packet['target_profile']}\n"
        f"- evidence_sought: {', '.join(packet['evidence_sought'])}\n"
        f"- no_send_default: {str(packet['no_send_default']).lower()}\n"
        f"- owner_approval_state: {packet['owner_approval_state']}\n\n"
        "Boundary:\n"
        "No external action was executed. No customer validation, pricing validation, "
        "paid signal, payment, revenue, accounting advice, tax advice, or K9Audit integration is claimed."
    )


def run_aiden_strategy_runtime(
    owner_message: str,
    *,
    repo_root: Path | None = None,
    cieu_db: str | Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
) -> AidenChatRoute:
    root = repo_root or Path(__file__).resolve().parents[2]
    selected_cieu_db = Path(cieu_db) if cieu_db is not None else default_aiden_strategy_cieu_db(root)
    result = run_e104_adaptive_market_intelligence_strategy_session(
        cieu_db=selected_cieu_db,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        seal_session=True,
    )
    response_text = render_aiden_strategy_runtime_response(result)
    return AidenChatRoute(
        route="aiden_ceo_strategy_runtime",
        prefixed=True,
        owner_message=owner_message,
        response_text=response_text,
        protocol=STRATEGY_RUNTIME_PROTOCOL,
    )


def route_chat_message_to_aiden_meeting_room(
    message: str,
    *,
    repo_root: Path | None = None,
    cieu_db: str | Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str | None = None,
) -> AidenChatRoute:
    """Route an owner chat message if it explicitly targets Aiden.

    The router is deliberately conservative. It does not treat raw natural
    language as a CEO meeting-room instruction unless the explicit prefix is
    present.
    """

    if not is_aiden_meeting_room_message(message):
        return AidenChatRoute(
            route="codex_executor_default",
            prefixed=False,
            owner_message=(message or "").strip(),
            response_text=None,
        )

    owner_message = strip_aiden_meeting_room_prefix(message)
    if not owner_message:
        return AidenChatRoute(
            route="aiden_ceo_meeting_room",
            prefixed=True,
            owner_message="",
            response_text=build_empty_aiden_prefix_revision(),
        )

    if is_aiden_strategy_runtime_message(owner_message):
        return run_aiden_strategy_runtime(
            owner_message,
            repo_root=repo_root,
            cieu_db=cieu_db,
            brain_db=brain_db,
            ystar_gov_root=ystar_gov_root,
        )

    response_text = answer_owner_governed_text(
        owner_message,
        repo_root=repo_root,
        cieu_db=cieu_db,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
        session_id=session_id or "aiden_prefix_meeting_room_session",
    )
    return AidenChatRoute(
        route="aiden_ceo_meeting_room",
        prefixed=True,
        owner_message=owner_message,
        response_text=response_text,
    )


def answer_aiden_prefixed_message(message: str, **kwargs: Any) -> str:
    """Return the governed Aiden response for an explicit ``Aiden:`` message."""

    route = route_chat_message_to_aiden_meeting_room(message, **kwargs)
    if route.route == "aiden_ceo_strategy_runtime":
        return route.response_text or build_empty_aiden_prefix_revision()
    if route.route != "aiden_ceo_meeting_room":
        return (
            "This message was not routed to Aiden because it did not start with "
            "`Aiden:` or `Aiden：`."
        )
    return route.response_text or build_empty_aiden_prefix_revision()


__all__ = [
    "AIDEN_MEETING_ROOM_PREFIXES",
    "AidenChatRoute",
    "MEETING_ROOM_PROTOCOL",
    "STRATEGY_RUNTIME_PROTOCOL",
    "answer_aiden_prefixed_message",
    "build_empty_aiden_prefix_revision",
    "default_aiden_strategy_cieu_db",
    "is_aiden_meeting_room_message",
    "is_aiden_strategy_runtime_message",
    "render_aiden_strategy_runtime_response",
    "route_chat_message_to_aiden_meeting_room",
    "run_aiden_strategy_runtime",
    "strip_aiden_meeting_room_prefix",
]
