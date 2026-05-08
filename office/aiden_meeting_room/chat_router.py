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
from office.mission_command.e100_brain_locked_autonomous_profit_strategy import (
    run_e100_brain_locked_autonomous_profit_strategy,
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
    competitors = strategy["competitor_analysis"]["direct_competitors"]
    packet = strategy["next_L4_feedback_owner_decision_packet"]
    route_scores = strategy["route_scoring"][:5]
    product_stages = strategy["product_strategy"]["product_stages"]
    competitor_lines = "\n".join(
        f"- {item['competitor_id']}: {item['positioning']}" for item in competitors[:5]
    )
    route_lines = "\n".join(
        f"- {item['route_id']}: {item['brain_adjusted_first_cash_score']}" for item in route_scores
    )
    product_lines = "\n".join(
        f"- {item['stage_id']}: {item['description']} ({item['execution_status']})"
        for item in product_stages
    )
    return (
        "CEO Strategy Runtime: E100_BRAIN_LOCKED_AUTONOMOUS_PROFIT_STRATEGY\n"
        "This Aiden strategy question was auto-upgraded from meeting-room answer "
        "to the governed 6D brain-locked strategy runtime.\n\n"
        f"Y-star-gov decision: {receipt['Y_star_gov_decision']}\n"
        f"CIEUStore written: {str(receipt['CIEUStore_written']).lower()}\n"
        f"Brain unique nodes: {receipt['brain_unique_nodes']}\n"
        f"CIEU events: {receipt['CIEU_event_count']}\n\n"
        "Selected first-cash path:\n"
        f"{selected['current_best_first_cash_path']}\n\n"
        "Why this now:\n"
        f"{selected['why_this_path_now']}\n\n"
        "Why not the others:\n"
        f"{selected['why_not_others']}\n\n"
        "Route comparison:\n"
        f"{route_lines}\n\n"
        "Competitor / alternative map:\n"
        f"{competitor_lines}\n"
        f"- indirect alternatives: {', '.join(strategy['competitor_analysis']['indirect_alternatives'])}\n\n"
        "Product shape:\n"
        f"{product_lines}\n\n"
        "Pricing hypothesis, not validation:\n"
        f"- {pricing['name']}: {pricing['hypothesis_price_range_usd']}\n"
        f"- status: {strategy['offer_and_pricing_hypotheses']['pricing_validation_status']}\n\n"
        "Strongest validation question:\n"
        "Will a principal of a 2-10 person CPA/bookkeeping firm consider paying "
        f"{pricing['hypothesis_price_range_usd']} for a 48-hour review bottleneck rescue brief?\n\n"
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
    result = run_e100_brain_locked_autonomous_profit_strategy(
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
