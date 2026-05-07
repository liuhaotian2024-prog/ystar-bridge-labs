from __future__ import annotations

from pathlib import Path

from .e75_l3_owner_decision_packet import (
    BRIDGE_ROOT,
    build_ceo_readback,
    build_completion_report,
    build_l3_owner_decision_packet,
    load_json,
    write_json,
)


def load_e75_owner_decision_state_for_brain(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e75_ceo_readback.json", base) or build_ceo_readback(base)


def get_e75_l3_owner_decision_packet(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e75_l3_owner_decision_packet.json", base) or build_l3_owner_decision_packet(base)


def run_e75_readback_smoke(root: Path | None = None) -> dict:
    state = load_e75_owner_decision_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "packet_finalized": state.get("E75_status") == "owner_decision_packet_finalized_no_execution",
        "L3_not_executed": state.get("L3_executed") is False,
        "owner_approval_pending": state.get("owner_approval_status") == "pending_owner_decision",
        "L4_L5_not_ready": state.get("L4_ready") is False and state.get("L5_ready") is False,
        "external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e75_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_e75_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e75_readback_smoke(base)
    write_json(base, "operations/external_validation/e75_readback_smoke_result.json", result)
    return result


def get_e75_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e75_completion_report.json", base) or build_completion_report(base)


__all__ = [
    "load_e75_owner_decision_state_for_brain",
    "get_e75_l3_owner_decision_packet",
    "run_e75_readback_smoke",
    "write_e75_readback_smoke",
    "get_e75_completion_report",
]
