from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_adapter_result, controlled_public_read, is_forbidden_source, write_json, write_md


def run_controlled_public_page_read_adapter() -> dict:
    return build_adapter_result()


def write_controlled_public_page_read_adapter(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_controlled_public_page_read_adapter()
    write_json(root, "operations/external_validation/e59_controlled_public_page_read_adapter_result.json", data)
    write_md(root, "reports/integration/e59_controlled_public_page_read_adapter_result.md", "E59 Controlled Public Page Read Adapter", [
        f"Adapter status: `{data['adapter_status']}`",
        f"Network status: `{data['network_status']}`",
        "Fixture reads prove the pipeline without faking live fresh reads.",
    ])
    return data

