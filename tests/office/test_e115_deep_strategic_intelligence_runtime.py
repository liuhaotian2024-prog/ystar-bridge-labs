from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room
from office.mission_command.e115_deep_strategic_intelligence_runtime import (
    build_e115_deep_strategy_dossier,
    run_e115_deep_strategic_intelligence_runtime,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E115_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E115 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e115_deep_strategy_runtime_writes_governed_dossier(tmp_path):
    result = run_e115_deep_strategic_intelligence_runtime(
        cieu_db=tmp_path / "e115.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        use_host_live_network=False,
        seal_session=False,
    )
    dossier = result["deep_strategy_dossier"]
    decision = result["YstarGov_deep_strategy_write_result"]["governance_decision"]

    assert result["deep_strategy_runtime_proven"] is True
    assert decision["decision"] == "ALLOW"
    assert len(dossier["deep_reasoning_dimensions"]) >= 14
    evidence_sets = [tuple(item["evidence_refs"]) for item in dossier["deep_reasoning_dimensions"]]
    unique_refs = {ref for refs in evidence_sets for ref in refs}
    assert len(set(evidence_sets)) >= 8
    assert len(unique_refs) >= 12
    assert len(dossier["competitive_landscape"]["competitors_and_substitutes"]) >= 5
    assert all(
        competitor.get("source_date") and competitor.get("public_signal_date_basis") == "source_dated_public_evidence"
        for competitor in dossier["competitive_landscape"]["competitors_and_substitutes"]
    )
    assert not any(
        competitor["source_url"].rstrip("/").count("/") <= 2 and competitor.get("source_date_basis", "").startswith("public competitor presence")
        for competitor in dossier["competitive_landscape"]["competitors_and_substitutes"]
    )
    assert len(dossier["product_shape"]["buyer_visible_deliverables"]) >= 5
    assert dossier["causal_zero_loop_model"]["R_t_plus_1"] == 0.0
    assert dossier["causal_zero_loop_model"]["residual_truth_status"]["real_market_residual_closed"] is False
    assert dossier["extrapolation_gate"]["class_of_issue"]["issue_class_id"]
    assert len(dossier["extrapolation_gate"]["extrapolation_to_other_cases"]) >= 3
    assert "CEO_DEEP_STRATEGIC_INTELLIGENCE_DECISION" in result["CIEUStore_summary"]["event_types"]
    assert result["truth_constraints"]["no_customer_validation_claim"] is True
    assert result["L5_truth_table_after"]["L5-D"] == "absent_or_not_executed"


def test_e115_dossier_makes_product_shape_and_right_to_win_concrete(tmp_path):
    result = run_e115_deep_strategic_intelligence_runtime(
        cieu_db=tmp_path / "e115_product.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        use_host_live_network=False,
        seal_session=False,
    )
    dossier = result["deep_strategy_dossier"]
    product = dossier["product_shape"]
    right_to_win = dossier["right_to_win_and_right_to_lose"]

    assert "Evidence" in product["product_name"] or "Rescue" in product["product_name"]
    assert any("CIEU" in item for item in product["buyer_visible_deliverables"])
    assert any("Y-star-gov" in item for item in right_to_win["right_to_win_assets"])
    assert len(right_to_win["market_visible_right_to_win_assets"]) >= 4
    assert all(item["buyer_visible_proof"] for item in right_to_win["market_visible_right_to_win_assets"])
    assert all(item["why_buyer_cares"] for item in right_to_win["market_visible_right_to_win_assets"])
    assert len(right_to_win["right_to_lose_risks"]) >= 3


def test_e115_chat_router_upgrades_strategy_questions_to_deep_runtime(tmp_path):
    route = route_chat_message_to_aiden_meeting_room(
        "Aiden: 再做一次全球化赚钱战略分析，要求深度竞品、产品形态、right to win 和失败假设",
        repo_root=BRIDGE_ROOT,
        cieu_db=tmp_path / "e115_router.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        allow_live_network=False,
    )

    assert route.route == "aiden_ceo_deep_strategic_intelligence_runtime"
    assert route.protocol == "AidenDeepStrategicIntelligenceRuntimeV1"
    assert "CEO Strategy Runtime: E115_AIDEN_DEEP_STRATEGIC_INTELLIGENCE_RUNTIME" in route.response_text
    assert "Concrete product shape:" in route.response_text
    assert "Competitors and substitutes:" in route.response_text
    assert "Assumptions to test:" in route.response_text
    assert "No external action was executed" in route.response_text


def test_e115_dossier_builder_preserves_no_overclaim_boundary(tmp_path):
    result = run_e115_deep_strategic_intelligence_runtime(
        cieu_db=tmp_path / "e115_boundary.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        use_host_live_network=False,
        seal_session=False,
    )
    dossier = build_e115_deep_strategy_dossier(result["source_e114_result"], owner_intent="test")

    assert dossier["no_overclaim_boundary"]["customer_validation_claim"] is False
    assert dossier["no_overclaim_boundary"]["revenue_claim"] is False
    assert dossier["experiment_design"]["no_send_default"] is True
    assert dossier["experiment_design"]["external_action_executed"] is False
