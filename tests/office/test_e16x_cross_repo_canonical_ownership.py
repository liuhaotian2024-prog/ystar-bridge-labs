from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_cross_repo_canonical_ownership.json").read_text())


def test_e16x_scans_all_four_repos() -> None:
    data = load()
    scans = data["repo_scan_receipts"]
    assert set(scans) == {"ystar_bridge_labs", "y_star_gov", "gov_mcp", "ystar_company"}
    assert all(scans[key]["exists"] for key in scans)
    assert scans["ystar_bridge_labs"]["head"]
    assert scans["gov_mcp"]["evidence_files"]


def test_e16x_ownership_map_assigns_canonical_roles() -> None:
    ownership = load()["canonical_ownership"]
    assert "deterministic governance kernel" in ownership["Y-star-gov"]["owns"]
    assert "MCP execution gateway" in ownership["gov-mcp"]["owns"]
    assert "commercial validation loop" in ownership["ystar-bridge-labs"]["owns"]
    assert ownership["ystar-company"]["canonical_role"] == "not final source of truth unless explicitly promoted"
