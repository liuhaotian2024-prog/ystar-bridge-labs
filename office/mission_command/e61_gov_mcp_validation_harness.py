from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, run_gov_mcp_validation_harness, write_json, write_md


def run_e61_gov_mcp_validation_harness(root: Path | None = None) -> dict:
    return run_gov_mcp_validation_harness()


def write_e61_gov_mcp_validation_harness(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_e61_gov_mcp_validation_harness(root)
    write_json(root, "operations/external_validation/e61_gov_mcp_validation_harness_result.json", data)
    write_md(root, "reports/integration/e61_gov_mcp_validation_harness_result.md", "E61 gov-mcp Validation Harness", [f"Passed: `{data['passed']}`"])
    return data
