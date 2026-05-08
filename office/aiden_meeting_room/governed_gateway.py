"""Governed owner-facing entrypoint for the Aiden behavior center.

The raw ``answer_owner`` function remains the deterministic behavior-center
kernel used by E94. Owner-facing callers should use this module so every
behavior-center response goes through brain provenance, Y-star-gov validation,
CIEUStore recording, and route gating first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def default_behavior_center_cieu_db(repo_root: Path) -> Path:
    runtime_dir = repo_root / ".runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / "aiden_behavior_center_runtime.db"


def answer_owner_governed(
    owner_message: str,
    *,
    repo_root: Path | None = None,
    cieu_db: str | Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Return the full governed behavior-center session result."""

    root = repo_root or Path(__file__).resolve().parents[2]
    selected_cieu_db = Path(cieu_db) if cieu_db is not None else default_behavior_center_cieu_db(root)
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
    )

    return run_behavior_center_runtime_gateway_session(
        owner_message=owner_message,
        cieu_db=str(selected_cieu_db),
        repo_root=root,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
        session_id=session_id or "owner_facing_behavior_center_runtime_session",
    )


def answer_owner_governed_text(
    owner_message: str,
    *,
    repo_root: Path | None = None,
    cieu_db: str | Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str | None = None,
) -> str:
    """Return user-facing text plus a compact governance receipt."""

    result = answer_owner_governed(
        owner_message,
        repo_root=repo_root,
        cieu_db=cieu_db,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
        session_id=session_id,
    )
    packet = result["behavior_center_packet"]
    route_type = result["route_result"].get("route_type")
    cieu_summary = result["CIEUStore_summary"]
    footer = (
        "\n\nRuntime governance:\n"
        f"- decision: {result['behavior_center_decision']}\n"
        f"- route: {route_type}\n"
        f"- brain_nodes: {packet['brain_provenance']['unique_nodes']}\n"
        f"- CIEU_events: {cieu_summary['event_count']}\n"
        f"- external_action_executed: {result['no_external_action_executed'] is False}"
    )
    return str(packet["behavior_center_response"]) + footer


__all__ = [
    "answer_owner_governed",
    "answer_owner_governed_text",
    "default_behavior_center_cieu_db",
]
