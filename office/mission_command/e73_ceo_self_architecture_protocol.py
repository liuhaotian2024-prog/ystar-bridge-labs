from __future__ import annotations

from pathlib import Path
from typing import Any

from .e73_ecosystem_boundary_lock import BRIDGE_ROOT, build_self_architecture_protocol, load_json, write_json


def load_ceo_self_architecture_protocol(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e73_ceo_self_architecture_protocol.json", base) or build_self_architecture_protocol(base)


def evaluate_new_file_justification(justification: dict[str, Any], root: Path | None = None) -> dict:
    protocol = load_ceo_self_architecture_protocol(root)
    required = protocol["required_output_for_new_or_extended_function"]
    missing = [key for key in required if not justification.get(key)]
    decision = justification.get("decision")
    rejected = bool(missing) or decision not in protocol["valid_construction_decisions"]
    if decision == "create_new_only_if_no_owner_exists" and not justification.get("no_duplication_proof"):
        rejected = True
        missing.append("no_duplication_proof")
    return {
        "artifact_id": "e73_new_file_justification_evaluation",
        "accepted": not rejected,
        "missing_or_invalid_fields": sorted(set(missing)),
        "decision": decision,
        "external_action_allowed": False,
    }


def write_ceo_self_architecture_protocol(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    protocol = build_self_architecture_protocol(base)
    write_json(base, "operations/external_validation/e73_ceo_self_architecture_protocol.json", protocol)
    return protocol


__all__ = [
    "load_ceo_self_architecture_protocol",
    "evaluate_new_file_justification",
    "write_ceo_self_architecture_protocol",
]
