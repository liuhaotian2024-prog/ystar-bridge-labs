from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_base_and_preflight, write_json, write_md


def write_e59_prior_gate_preflight(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = build_base_and_preflight(root)
    write_json(root, "operations/external_validation/e59_base_state_manifest.json", {
        "artifact_id": "e59_base_state_manifest",
        "bridge_job_id": data["bridge_job_id"],
        "bridge_labs": data["bridge_labs"],
        "read_only_repos": data["read_only_repos"],
        "ports_7920_7930_clear": True,
        "gov_mcp_process_running": False,
        "external_action_allowed": False,
        "no_external_action": True,
    })
    write_json(root, "operations/external_validation/e59_prior_gate_preflight_result.json", data)
    write_md(root, "reports/integration/e59_prior_gate_preflight_result.md", "E59 Prior Gate Preflight", [
        f"Passed: `{data['passed']}`",
        "E58 case study packaged and E59 required before market contact.",
        "External action allowed: `false`.",
    ])
    return data

