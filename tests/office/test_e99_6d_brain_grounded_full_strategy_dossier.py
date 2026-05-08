from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from office.mission_command.e99_6d_brain_grounded_full_strategy_dossier import (
    build_6d_brain_grounded_strategy_dossier,
    run_e99_6d_brain_grounded_strategy_dossier,
    write_e99_reports,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"

pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E99 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e99_uses_real_6d_brain_provenance(tmp_path):
    dossier = build_6d_brain_grounded_strategy_dossier(brain_db=_brain_copy(tmp_path))

    assert dossier["truth_constraints"]["brain_grounded"] is True
    assert dossier["brain_provenance"]["six_d_dimension_count"] == 6
    assert dossier["brain_provenance"]["total_activations"] >= 6
    assert dossier["brain_provenance"]["unique_nodes"] >= 3
    assert len(dossier["six_d_brain_review"]) == 6
    assert all(item["brain_activation_count"] >= 1 for item in dossier["six_d_brain_review"])
    assert dossier["benchmark_result"]["benchmark_decision"] == "ALLOW"


def test_e99_contains_full_strategy_sections_not_just_direction(tmp_path):
    dossier = build_6d_brain_grounded_strategy_dossier(brain_db=_brain_copy(tmp_path))

    assert len(dossier["competitor_analysis"]["direct_competitors"]) >= 5
    assert len(dossier["target_customer_segments"]) >= 4
    assert len(dossier["product_strategy"]["product_stages"]) >= 4
    assert dossier["product_strategy"]["product_stages"][0]["stage_id"] == "v0_no_send_demo_report"
    assert dossier["offer_and_pricing_hypotheses"]["pricing_validation_status"] == "hypothesis_only_not_validated"
    assert dossier["risk_and_boundary_controls"]["no_customs_legal_or_tax_advice"] is True
    assert "Tariff Shock Margin Rescue Desk" in dossier["selected_strategy"]["current_best_first_cash_path"]


def test_e99_writes_formal_cieustore_record_and_keeps_truth_boundaries(tmp_path):
    result = run_e99_6d_brain_grounded_strategy_dossier(
        cieu_db=tmp_path / "e99.db",
        brain_db=_brain_copy(tmp_path),
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_dossier_record_proven"] is True
    assert receipt["mode"] == "CEO_RUNTIME_CERTIFIED_6D_BRAIN_GROUNDED_STRATEGY_DOSSIER"
    assert receipt["Y_star_gov_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["brain_grounded"] is True
    assert receipt["competitor_count"] >= 5
    assert receipt["truth_boundary"]["no_L4_feedback_executed"] is True
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_customs_legal_or_tax_advice"] is True


def test_e99_reports_include_product_shape_competitors_and_l5_boundary(tmp_path):
    result = run_e99_6d_brain_grounded_strategy_dossier(
        cieu_db=tmp_path / "e99_report.db",
        brain_db=_brain_copy(tmp_path),
    )
    paths = write_e99_reports(result, repo_root=tmp_path)

    assert set(paths) == {"report_json", "readback_md", "status_json", "status_md"}
    report = json.loads((tmp_path / "office/mission_command/e99_6d_brain_grounded_full_strategy_dossier_report.json").read_text())
    status = json.loads(
        (
            tmp_path
            / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e99_6d_brain_grounded_full_strategy_dossier.json"
        ).read_text()
    )

    assert report["CEO_runtime_receipt"]["brain_grounded"] is True
    assert report["product_strategy"]["first_deliverable"] == "v0_no_send_demo_report"
    assert len(report["competitor_analysis"]["direct_competitors"]) >= 5
    assert status["L5-D"] == "absent_or_not_executed"
