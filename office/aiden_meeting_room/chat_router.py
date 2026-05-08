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


AIDEN_MEETING_ROOM_PREFIXES = ("Aiden:", "Aiden：", "aiden:", "aiden：")
MEETING_ROOM_PROTOCOL = "AidenPrefixV1"


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
    "answer_aiden_prefixed_message",
    "build_empty_aiden_prefix_revision",
    "is_aiden_meeting_room_message",
    "route_chat_message_to_aiden_meeting_room",
    "strip_aiden_meeting_room_prefix",
]
