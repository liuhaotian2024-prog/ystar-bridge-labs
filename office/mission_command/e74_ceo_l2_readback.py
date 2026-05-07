from __future__ import annotations

from pathlib import Path

from .e74_ceo_l2_internal_work_pilot import (
    BRIDGE_ROOT,
    build_existing_artifact_reuse_map,
    build_readback_state,
    build_owner_facing_l3_readiness_packet,
    build_completion_report,
    load_json,
    write_json,
)


def load_e74_l2_work_state_for_brain(root: Path | None = None) -> dict:
    return build_readback_state(root or BRIDGE_ROOT)


def get_e74_owner_facing_l3_readiness_packet(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", base) or build_owner_facing_l3_readiness_packet(base)


def get_e74_existing_artifact_reuse_map(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", base) or build_existing_artifact_reuse_map(base)


def run_e74_l2_work_readback_smoke(root: Path | None = None) -> dict:
    state = load_e74_l2_work_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "L2_work_completed": state.get("L2_work_status") == "completed_internal_no_external_action",
        "owner_packet_available": "L3 Read-Only Research Readiness Packet" in state.get("deliverable_produced", ""),
        "no_new_wheel_compliance": state.get("no_new_wheel_compliance") is True,
        "external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e74_l2_work_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_e74_l2_work_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e74_l2_work_readback_smoke(base)
    write_json(base, "operations/external_validation/e74_l2_work_readback_smoke_result.json", result)
    return result


def get_e74_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e74_completion_report.json", base) or build_completion_report(base)


__all__ = [
    "load_e74_l2_work_state_for_brain",
    "get_e74_owner_facing_l3_readiness_packet",
    "get_e74_existing_artifact_reuse_map",
    "run_e74_l2_work_readback_smoke",
    "write_e74_l2_work_readback_smoke",
    "get_e74_completion_report",
]
