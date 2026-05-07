from __future__ import annotations

from pathlib import Path

from .e73_ecosystem_boundary_lock import BRIDGE_ROOT, build_readiness_gate, load_json, write_json


def load_ceo_real_work_readiness_gate(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base) or build_readiness_gate(base)


def get_highest_ready_work_level(root: Path | None = None) -> dict:
    gate = load_ceo_real_work_readiness_gate(root)
    return {
        "highest_ready_level": gate.get("highest_ready_level"),
        "next_allowed_autonomous_work": gate.get("next_allowed_autonomous_work"),
        "external_action_allowed": False,
    }


def write_ceo_real_work_readiness_gate(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    gate = build_readiness_gate(base)
    write_json(base, "operations/external_validation/e73_ceo_real_work_readiness_gate.json", gate)
    return gate


__all__ = [
    "load_ceo_real_work_readiness_gate",
    "get_highest_ready_work_level",
    "write_ceo_real_work_readiness_gate",
]
