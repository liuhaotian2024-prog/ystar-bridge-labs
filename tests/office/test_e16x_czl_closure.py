from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_report(name: str) -> dict:
    return json.loads((ROOT / f"operations/external_validation/{name}.json").read_text())


def test_e16x_czl_closes_inventory_when_repos_exist() -> None:
    ownership = load_report("e16x_cross_repo_canonical_ownership")
    scans = ownership["repo_scan_receipts"]
    assert all(item["exists"] for item in scans.values())

    czl_text = (ROOT / "reports/integration/e16x_czl_closure.md").read_text()
    assert "Rt+1: 0" in czl_text
    assert "no_real_outbound_action=true" in czl_text


def test_e16x_reports_no_external_side_effects() -> None:
    route = load_report("e16x_route_reconciliation_packet")
    assert "no customer contact" in route["no_external_side_effects"]
    assert "real provider API call" in route["no_external_side_effects"]
