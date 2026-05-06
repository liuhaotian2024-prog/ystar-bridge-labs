from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_archaeology, write_json, write_md


def run_external_observation_archaeology(root: Path | None = None) -> dict:
    return build_archaeology(root)


def write_external_observation_archaeology(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_observation_archaeology(root)
    write_json(root, "operations/external_validation/e59_external_observation_archaeology.json", data)
    write_md(root, "reports/integration/e59_external_observation_archaeology.md", "E59 External Observation Archaeology", [
        f"Assets discovered: `{data['asset_count']}`",
        f"E57 blocker diagnosis: `{data['E57_blocker_diagnosis']}`",
        "Seed domains are methodology seeds, not hardcoded boundaries.",
    ])
    return data

