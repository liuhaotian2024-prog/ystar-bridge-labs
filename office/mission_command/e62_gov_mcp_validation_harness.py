from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_gov_mcp_validation_harness(root: Path | None = None) -> dict:
    return core.run_gov_mcp_validation_harness(root or core.BRIDGE_ROOT)


def write_gov_mcp_validation_harness(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_gov_mcp_validation_harness(root)
    core.write_json(root, "operations/external_validation/e62_gov_mcp_validation_harness_result.json", data)
    return data
