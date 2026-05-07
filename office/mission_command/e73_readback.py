from __future__ import annotations

from pathlib import Path

from .e73_ecosystem_boundary_lock import (
    BRIDGE_ROOT,
    build_e72_proposal_reclassification,
    build_no_new_wheel_policy,
    build_readback_smoke,
    build_responsibility_matrix,
    load_e73_boundary_state_for_brain,
    load_json,
    write_json,
)
from .e73_ceo_real_work_readiness import load_ceo_real_work_readiness_gate
from .e73_ceo_self_architecture_protocol import load_ceo_self_architecture_protocol


def get_ecosystem_responsibility_matrix(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base) or build_responsibility_matrix(base)


def get_no_new_wheel_policy(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_no_new_wheel_policy.json", base) or build_no_new_wheel_policy(base)


def get_ceo_real_work_readiness_gate(root: Path | None = None) -> dict:
    return load_ceo_real_work_readiness_gate(root)


def get_ceo_self_architecture_protocol(root: Path | None = None) -> dict:
    return load_ceo_self_architecture_protocol(root)


def get_e72_proposal_reclassification(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_e72_proposal_reclassification.json", base) or build_e72_proposal_reclassification(base)


def get_owner_readable_closure_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_owner_readable_closure_report.json", base)


def run_e73_readback_smoke(root: Path | None = None) -> dict:
    return build_readback_smoke(root or BRIDGE_ROOT)


def write_e73_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    smoke = run_e73_readback_smoke(base)
    write_json(base, "operations/external_validation/e73_ceo_readback_smoke_result.json", smoke)
    return smoke


__all__ = [
    "load_e73_boundary_state_for_brain",
    "get_ecosystem_responsibility_matrix",
    "get_no_new_wheel_policy",
    "get_ceo_real_work_readiness_gate",
    "get_ceo_self_architecture_protocol",
    "get_e72_proposal_reclassification",
    "get_owner_readable_closure_report",
    "run_e73_readback_smoke",
    "write_e73_readback_smoke",
]
