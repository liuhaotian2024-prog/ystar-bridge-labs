from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e104_adaptive_market_intelligence_strategy_runtime import (
    build_adaptive_market_intelligence_strategy,
    run_e104_adaptive_market_intelligence_strategy_session,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E104_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E104 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e104_builds_open_world_strategy_with_seven_market_gates(tmp_path):
    strategy = build_adaptive_market_intelligence_strategy(brain_db=_brain_copy(tmp_path))
    gates = strategy["adaptive_market_governance_gates"]

    assert strategy["selected_strategy"]["selected_route_id"] == "agentic_engineering_control_room_rescue"
    assert strategy["cpa_route_status"]["status"] == "credible_high_risk_candidate_demoted_not_selected"
    assert len(gates) == 7
    assert all(gate["gate_passed"] is True for gate in gates.values())
    assert len(strategy["external_market_evidence_map"]["evidence_items"]) >= 10
    assert strategy["founder_market_fit_assessment"]["founder_is_cpa"] is False
    assert strategy["offer_and_pricing_hypotheses"]["pricing_validation_status"] == "hypothesis_only_not_validated"
    assert strategy["truth_constraints"]["no_external_action_executed"] is True


def test_e104_competitor_scan_includes_new_cpa_ai_and_offshore_alternatives(tmp_path):
    strategy = build_adaptive_market_intelligence_strategy(brain_db=_brain_copy(tmp_path))
    competitors = {
        item["competitor_id"]
        for item in strategy["adaptive_market_governance_gates"]["competitor_saturation_scan"]["competitors"]
    }

    assert {"black_ore", "basis", "juno", "cpa_pilot", "aiwyn", "canopy", "karbon", "taxdome"} <= competitors
    assert any("offshore" in item or "madras" in item for item in competitors)
    assert strategy["competitor_saturation_assessment"]["CPA_review_bottleneck_route"] == "crowded"


def test_e104_run_writes_strategic_and_market_refresh_cieustore_records(tmp_path):
    result = run_e104_adaptive_market_intelligence_strategy_session(
        cieu_db=tmp_path / "e104.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_market_refresh_strategy_proven"] is True
    assert receipt["Y_star_gov_strategic_decision"] == "ALLOW"
    assert receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 2
    assert receipt["selected_route_id"] == "agentic_engineering_control_room_rescue"
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
