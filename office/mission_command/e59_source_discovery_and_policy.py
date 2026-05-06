from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_source_discovery_policy, write_json, write_md


def run_source_discovery_and_policy() -> dict:
    return build_source_discovery_policy()


def write_source_discovery_and_policy(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_source_discovery_and_policy()
    write_json(root, "operations/external_validation/e59_source_discovery_policy.json", data)
    write_md(root, "reports/integration/e59_source_discovery_policy.md", "E59 Source Discovery and Policy", [
        f"Candidate sources: `{data['bounded_source_plan_count']}`",
        "Seed domains are not exhaustive.",
        "Public papers/docs/GitHub/blogs are knowledge sources, not human contact.",
    ])
    return data

