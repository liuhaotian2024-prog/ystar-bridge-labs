from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from office.mission_command.e100_brain_locked_autonomous_profit_strategy import (
    build_brain_locked_autonomous_profit_strategy,
    run_e100_brain_locked_autonomous_profit_strategy,
    write_e100_reports,
)

BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_LOCK_ROOT = Path("/private/tmp/e100_ystar_patch_work")
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E100 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e100_resets_previous_market_target_and_selects_autonomously(tmp_path):
    strategy = build_brain_locked_autonomous_profit_strategy(brain_db=_brain_copy(tmp_path))

    assert strategy["market_target_reset"]["previous_target_status"] == "removed_as_default_target_retained_only_as_candidate"
    assert strategy["autonomous_route_selection"]["selected_route_id"] == "cpa_review_bottleneck_rescue"
    assert strategy["autonomous_route_selection"]["previous_tariff_route_rank"] > 1
    assert strategy["brain_provenance"]["unique_nodes"] >= 3
    assert strategy["truth_constraints"]["brain_grounded"] is True


def test_e100_passes_governance_side_brain_lock_and_writes_cieu(tmp_path):
    result = run_e100_brain_locked_autonomous_profit_strategy(
        cieu_db=tmp_path / "e100.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_LOCK_ROOT,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_brain_locked_strategy_proven"] is True
    assert receipt["Y_star_gov_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["selected_route_id"] == "cpa_review_bottleneck_rescue"
    assert receipt["truth_boundary"]["no_customer_validation"] is True


def test_e100_reports_include_new_target_and_honest_boundaries(tmp_path):
    result = run_e100_brain_locked_autonomous_profit_strategy(
        cieu_db=tmp_path / "e100_report.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_LOCK_ROOT,
    )
    paths = write_e100_reports(result, repo_root=tmp_path)

    assert set(paths) == {"report_json", "readback_md", "status_json", "status_md"}
    report = json.loads((tmp_path / "office/mission_command/e100_brain_locked_autonomous_profit_strategy_report.json").read_text())
    status = json.loads((tmp_path / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e100_brain_locked_autonomous_profit_strategy.json").read_text())
    assert report["CEO_runtime_receipt"]["selected_route_id"] == "cpa_review_bottleneck_rescue"
    assert report["market_target_reset"]["previous_target"] == "Tariff Shock Margin Rescue Desk for small importers"
    assert status["L5-D"] == "absent_or_not_executed"
