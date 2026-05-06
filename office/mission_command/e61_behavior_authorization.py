from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, build_behavior_authorization, write_json, write_md


def run_behavior_authorization(root: Path | None = None) -> dict:
    return build_behavior_authorization(root or BRIDGE_ROOT)


def write_behavior_authorization(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_authorization(root)
    write_json(root, "operations/external_validation/e61_behavior_authorization_result.json", data)
    write_md(root, "reports/integration/e61_behavior_authorization_result.md", "E61 Behavior Authorization", [f"Passed: `{data['passed']}`"])
    return data
