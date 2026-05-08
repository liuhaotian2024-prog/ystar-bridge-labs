from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e106_strategy_process_integrity_runtime import (
    build_strategy_process_integrity_runtime_strategy,
    run_e106_strategy_process_integrity_session,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E106_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E106 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e106_adds_full_strategy_process_and_anti_anchor_proof(tmp_path):
    strategy = build_strategy_process_integrity_runtime_strategy(brain_db=_brain_copy(tmp_path))
    proof = strategy["strategy_process_integrity_proof"]

    assert proof["process_mode"] == "full_strategy_process_with_anchor_audit"
    assert proof["recent_memory_only"] is False
    assert len(proof["completed_phases"]) >= 17
    assert len(proof["opportunity_universe_scan"]) >= 8
    assert len(proof["counterfactual_comparison"]) >= 5
    assert len(proof["customer_segment_and_buyer_map"]) >= 3
    assert len(proof["business_model_options"]) >= 3
    assert proof["anchor_dependence_audit"]["anchor_penalty_applied"] is True
    assert proof["anchor_dependence_audit"]["selected_route_supported_without_anchor"] is True


def test_e106_runtime_writes_four_cieustore_records_and_passes_governance(tmp_path):
    result = run_e106_strategy_process_integrity_session(
        cieu_db=tmp_path / "e106.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_strategy_process_integrity_proven"] is True
    assert receipt["Y_star_gov_strategic_decision"] == "ALLOW"
    assert receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
    assert receipt["Y_star_gov_open_world_decision"] == "ALLOW"
    assert receipt["Y_star_gov_process_integrity_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 4
    assert receipt["recent_memory_only"] is False
    assert receipt["anchor_penalty_applied"] is True
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
