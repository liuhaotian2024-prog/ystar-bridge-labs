from __future__ import annotations

import os
import shutil
from pathlib import Path

from office.mission_command.e108_live_global_open_world_strategy_runtime import FixtureGlobalPublicReadProvider
from office.mission_command.e110_labs_universal_operating_control_plane import (
    build_labs_universal_control_packet,
    build_operation_context,
    build_strategic_completeness_gate,
    enforce_labs_universal_control_before_runtime,
    resolve_required_capabilities_for_operation,
    run_e110_controlled_aiden_strategy_session,
    validate_labs_universal_control_local,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E110_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_strategy_context_requires_universal_baseline_and_competitive_gates():
    context = build_operation_context(owner_intent="Aiden: do global strategy and find easiest revenue path")
    required = resolve_required_capabilities_for_operation(context)

    assert "adaptive_governance_discovery" in required
    assert "open_world_doctrine_registry" in required
    assert "six_d_brain_provenance" in required
    assert "live_public_read_open_world_scan" in required
    assert "competitive_intelligence_current_sources" in required
    assert "substitute_threat_analysis" in required
    assert "latest_source_freshness_policy" in required
    assert "post_action_residual" in required


def test_static_evidence_or_static_competitor_map_cannot_pass_live_strategy():
    context = build_operation_context(owner_intent="全球赚钱战略分析")
    packet = build_labs_universal_control_packet(
        context,
        capability_overrides={
            "competitive_intelligence_current_sources": {
                "satisfied_by": "static_evidence_map",
                "invocation_mode": "static_evidence_map",
            }
        },
    )

    local = validate_labs_universal_control_local(packet)
    assert local["decision"] == "REQUIRE_REVISION"
    assert "competitive_intelligence_current_sources" in local["missing_capabilities"]


def test_universal_control_writes_cieustore_before_runtime(tmp_path):
    context = build_operation_context(owner_intent="Aiden: global strategy", operation_id="e110_gate_session")
    result = enforce_labs_universal_control_before_runtime(
        operation_context=context,
        cieu_db=tmp_path / "e110_gate.db",
        ystar_gov_root=YSTAR_ROOT,
        session_id="e110_gate_session",
    )

    assert result["runtime_may_continue"] is True
    assert result["Y_star_gov_universal_control_decision"] == "ALLOW"
    assert result["YstarGov_universal_control_write_result"]["formal_CIEU_log_written"] is True


def test_e110_controlled_strategy_runs_control_plane_then_e108_and_competition(tmp_path):
    result = run_e110_controlled_aiden_strategy_session(
        cieu_db=tmp_path / "e110_strategy.db",
        owner_intent="Find the easiest global first-cash strategy with current competitors.",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )
    receipt = result["CEO_runtime_receipt"]
    strategy = result["strategy"]

    assert result["end_to_end_controlled_strategy_proven"] is True
    assert receipt["Y_star_gov_universal_control_decision"] == "ALLOW"
    assert receipt["Y_star_gov_live_global_decision"] == "ALLOW"
    assert receipt["Y_star_gov_math_model_decision"] == "ALLOW"
    assert receipt["competitive_intelligence_gate_passed"] is True
    assert receipt["current_source_freshness_gate_passed"] is True
    assert receipt["selected_route_competitor_count"] >= 5
    assert receipt["current_source_count"] >= 5
    assert receipt["CIEU_event_count"] >= 3
    assert "competitive_intelligence" in strategy
    assert build_strategic_completeness_gate(strategy)["substitute_threat_analysis_present"] is True
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
