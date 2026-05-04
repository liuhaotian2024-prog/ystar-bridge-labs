from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16g_gov_mcp_adapter_promotion_result.json").read_text())


def test_e16g_records_gov_mcp_as_canonical_no_send_adapter_owner() -> None:
    data = load()
    assert data["canonical_surface_promoted_to_gov_mcp"] is True
    assert data["provider_adapter_mode"] == "local_no_send"
    assert data["real_send_enabled"] is False
    assert data["bridge_labs_e15d_adapter_status"] == "prototype_source_only"


def test_e16g_lists_gov_mcp_outbound_paths() -> None:
    paths = set(load()["gov_mcp_canonical_outbound_paths"])
    assert "gov_mcp/outbound/models.py" in paths
    assert "gov_mcp/outbound/dry_run_adapter.py" in paths
    assert "tests/test_outbound_dry_run_adapter.py" in paths
