from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_behavior_authorization(root: Path | None = None) -> dict:
    return core.build_behavior_authorization(root or core.BRIDGE_ROOT)


def write_behavior_authorization(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_behavior_authorization(root)
    core.write_json(root, "operations/external_validation/e63_behavior_authorization_result.json", data)
    return data
