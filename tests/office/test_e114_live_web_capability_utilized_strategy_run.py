from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e114_live_web_capability_utilized_strategy_run import (
    FreshnessBackfilledPublicReadProvider,
    build_default_e114_live_public_read_evidence_snapshot,
    build_snapshot_public_read_provider,
    run_e114_live_web_capability_utilized_strategy_run,
    summarize_source_dates,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E114_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E114 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e114_default_snapshot_is_current_dated_and_non_fixture():
    items = build_default_e114_live_public_read_evidence_snapshot()
    summary = summarize_source_dates(items)
    domains = {item["domain_id"] for item in items}

    assert len(items) >= 24
    assert summary["dated_count"] == len(items)
    assert summary["undated_count"] == 0
    assert "ai_security_compliance" in domains
    assert "cpa_tax_accounting" in domains
    assert all(item["evidence_type"] == "live_public_read_evidence_snapshot" for item in items)
    assert all("example.com" not in item["source_url"] for item in items)


def test_snapshot_provider_returns_domain_specific_public_read_rows():
    provider = build_snapshot_public_read_provider()
    ai_rows = provider.search("AI governance", domain_id="ai_security_compliance", max_results=3)
    cpa_rows = provider.search("CPA automation", domain_id="cpa_tax_accounting", max_results=3)

    assert len(ai_rows) == 3
    assert len(cpa_rows) == 3
    assert {row["domain_id"] for row in ai_rows} == {"ai_security_compliance"}
    assert {row["domain_id"] for row in cpa_rows} == {"cpa_tax_accounting"}
    assert all(row.get("source_date") for row in ai_rows + cpa_rows)


def test_freshness_backfilled_provider_replaces_undated_live_rows():
    class UndatedLiveProvider:
        def search(self, query: str, *, domain_id: str, max_results: int = 3):
            return [
                {
                    "source_title": "Undated live row",
                    "source_url": "https://live.example/undated",
                    "claim_summary": "Undated rows must not satisfy E112 brain learning.",
                    "domain_id": domain_id,
                    "evidence_type": "live_public_read_search_result",
                }
            ]

    provider = FreshnessBackfilledPublicReadProvider(
        live_provider=UndatedLiveProvider(),
        dated_snapshot_provider=build_snapshot_public_read_provider(),
    )
    rows = provider.search("AI governance", domain_id="ai_security_compliance", max_results=3)

    assert rows
    assert all(row.get("source_date") for row in rows)
    assert all("freshness_backfill" in row.get("evidence_type", "") for row in rows)


def test_e114_runs_through_e113_e110_e108_e112_and_cieustore(tmp_path):
    result = run_e114_live_web_capability_utilized_strategy_run(
        cieu_db=tmp_path / "e114_strategy.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        use_host_live_network=False,
        seal_session=False,
    )
    proof = result["ability_leap_proof"]
    scan = result["live_public_read_scan_summary"]
    utilization = result["capability_utilization_summary"]
    freshness = result["freshness_and_brain_learning_summary"]["freshness_filter_summary"]
    event_types = result["CIEUStore_summary"]["event_types"]

    assert proof["E113_capability_utilization_gate_passed"] is True
    assert proof["E110_universal_control_passed"] is True
    assert proof["E108_public_read_strategy_passed"] is True
    assert proof["E112_freshness_filter_passed"] is True
    assert utilization["code_index_loaded"] is True
    assert utilization["Rt_plus_1"] == 0.0
    assert scan["evidence_count"] >= 20
    assert scan["source_date_summary"]["dated_count"] == scan["evidence_count"]
    assert freshness["accepted_count"] >= 10
    assert result["freshness_and_brain_learning_summary"]["brain_mutation_candidate_count"] >= 10
    assert "NO_NEW_WHEEL_RUNTIME_LAW_DECISION" in event_types
    assert "LABS_UNIVERSAL_OPERATING_CONTROL_DECISION" in event_types
    assert "CEO_LIVE_GLOBAL_OPEN_WORLD_STRATEGY_DECISION" in event_types
    assert "CEO_BRAIN_LEARNING_LOOP_DECISION" in event_types
    assert result["truth_constraints"]["no_customer_validation_claim"] is True
    assert result["L5_truth_table_after"]["L5-D"] == "absent_or_not_executed"


def test_e114_strategy_demotes_crowded_accounting_route_with_competitor_evidence(tmp_path):
    result = run_e114_live_web_capability_utilized_strategy_run(
        cieu_db=tmp_path / "e114_strategy_competition.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        use_host_live_network=False,
        seal_session=False,
    )
    top_routes = result["top_routes"]
    cpa_routes = [row for row in top_routes if row.get("domain_id") == "cpa_tax_accounting"]

    assert result["selected_strategy"]["selected_route_id"] != "cpa_tax_accounting_first_cash_pack"
    assert cpa_routes
    assert any("crowded" in str(row.get("why_it_might_fail", "")).lower() for row in cpa_routes)
