from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e107_strategy_math_model_runtime import (
    build_market_first_strategy_math_model_strategy,
    build_mathematical_source_map,
    run_e107_strategy_math_model_session,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E107_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E107 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e107_builds_source_backed_market_first_math_model(tmp_path):
    strategy = build_market_first_strategy_math_model_strategy(brain_db=_brain_copy(tmp_path))
    source_map = build_mathematical_source_map()
    math_model = strategy["strategy_math_model"]
    route_scores = strategy["route_math_scores"]

    assert math_model["primary_selector"] == "market_first_expected_utility"
    assert math_model["internal_capability_role"] == "feasibility_multiplier_not_primary_selector"
    assert set(source_map).issubset(set(strategy["mathematical_source_map"]))
    assert len(route_scores) >= 5
    assert route_scores[0]["route_id"] == strategy["selected_strategy"]["selected_route_id"]
    assert route_scores[0]["market_first_score"] >= route_scores[1]["market_first_score"]
    assert route_scores[0]["evsi_usd"] > 0
    assert strategy["validation_experiment_design"]["no_send_default"] is True
    assert strategy["validation_experiment_design"]["owner_decision_required"] is True


def test_e107_demotes_internal_capability_to_feasibility_multiplier(tmp_path):
    strategy = build_market_first_strategy_math_model_strategy(brain_db=_brain_copy(tmp_path))

    assert strategy["strategy_math_model_status"]["prior_weight_problem_corrected"] is True
    assert strategy["strategy_math_model"]["internal_capability_role"] == "feasibility_multiplier_not_primary_selector"
    for row in strategy["route_math_scores"]:
        assert row["internal_capability_role"] == "feasibility_multiplier_not_primary_selector"
        assert row["calibration_status"] == "source_backed_prior_requires_owner_approved_market_validation"


def test_e107_runtime_writes_five_cieustore_records_and_passes_governance(tmp_path):
    result = run_e107_strategy_math_model_session(
        cieu_db=tmp_path / "e107.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_strategy_math_model_proven"] is True
    assert receipt["Y_star_gov_strategic_decision"] == "ALLOW"
    assert receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
    assert receipt["Y_star_gov_open_world_decision"] == "ALLOW"
    assert receipt["Y_star_gov_process_integrity_decision"] == "ALLOW"
    assert receipt["Y_star_gov_math_model_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 5
    assert receipt["internal_capability_role"] == "feasibility_multiplier_not_primary_selector"
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
