from __future__ import annotations

from office.mission_command.e89_ceo_intelligence_loop_runtime_compiler import (
    compile_ceo_intelligence_loop_packet,
    run_ceo_intelligence_runtime_session,
)
from office.mission_command.e90_market_grounded_strategy_run import (
    build_market_grounded_strategy_artifact,
    run_e90_market_grounded_strategy_session,
)
from office.mission_command.e91_ceo_doctrine_enforced_runtime_session import (
    build_e90_doctrine_action_context,
    enforce_doctrine_before_ceo_runtime,
    load_ystar_governance,
)
from office.mission_command.e91_ceo_operating_doctrine_registry import (
    build_doctrine_invocation_plan,
)


def test_static_evidence_map_cannot_satisfy_non_test_external_observation():
    governance = load_ystar_governance()
    context = build_e90_doctrine_action_context(test_mode=False)
    plan = build_doctrine_invocation_plan(context)

    decision = governance.validate_ceo_doctrine_invocation_plan(plan)

    assert decision.to_dict()["decision"] == "REQUIRE_REVISION"
    assert decision.to_dict()["failed_doctrine"] == "external_observation_public_read_evidence"


def test_static_template_cannot_satisfy_non_test_market_strategy_generation():
    governance = load_ystar_governance()
    context = build_e90_doctrine_action_context(test_mode=False)
    context["generation_mode"] = "static_template"
    plan = build_doctrine_invocation_plan(context)

    decision = governance.validate_ceo_doctrine_invocation_plan(plan)

    assert decision.to_dict()["decision"] == "REQUIRE_REVISION"
    assert decision.to_dict()["failed_doctrine"] == "generation_mode"


def test_doctrine_gate_writes_cieustore_records_in_test_mode(tmp_path):
    context = build_e90_doctrine_action_context(test_mode=True)

    gate = enforce_doctrine_before_ceo_runtime(
        action_context=context,
        cieu_db=str(tmp_path / "e91_gate.db"),
        session_id="e91_gate_session",
        seal_session=True,
    )

    assert gate["runtime_may_continue"] is True
    assert gate["plan_write"]["governance_decision"]["decision"] == "ALLOW"
    assert gate["proof_write"]["governance_decision"]["decision"] == "ALLOW"
    assert gate["proof_write"]["formal_CIEU_log_written"] is True
    assert gate["proof_write"]["CIEU_write_result"]["verify_result"]["valid"] is True


def test_e89_runtime_session_is_doctrine_enforced_and_no_external_action(tmp_path):
    result = run_ceo_intelligence_runtime_session(cieu_db=str(tmp_path / "e89_e91.db"))
    receipt = result["provider_route"]["gov_mcp_receipt"]
    metadata = receipt["intelligence_loop_metadata"]

    assert result["doctrine_invocation_plan_decision"] == "ALLOW"
    assert result["doctrine_invocation_proof_decision"] == "ALLOW"
    assert result["end_to_end_intelligence_chain_proven"] is True
    assert metadata["doctrine_registry_id"] == "ceo_operating_doctrine_registry_open_world_v1"
    assert metadata["required_doctrines_satisfied"] is True
    assert receipt["provider_action_executed"] is False
    assert receipt["external_side_effect"] is False


def test_e90_test_fixture_uses_doctrine_registry_but_non_test_live_gap_is_blocked(tmp_path):
    strategy = build_market_grounded_strategy_artifact()

    assert strategy["doctrine_registry_required"] is True
    assert strategy["generation_mode"] == "runtime_generated_structured_output"

    test_result = run_e90_market_grounded_strategy_session(cieu_db=str(tmp_path / "e90_e91.db"), test_mode=True)
    assert test_result["doctrine_invocation_plan_decision"] == "ALLOW"
    assert test_result["end_to_end_chain_proven"] is True

    blocked = run_e90_market_grounded_strategy_session(cieu_db=str(tmp_path / "e90_e91_blocked.db"), test_mode=False)
    assert blocked["runtime_may_continue"] is False
    assert blocked["doctrine_gate"]["plan_write"]["governance_decision"]["decision"] == "REQUIRE_REVISION"


def test_e89_compiler_marks_deterministic_fixture_truthfully():
    packet = compile_ceo_intelligence_loop_packet()

    assert packet["generation_mode"] == "deterministic_fixture"
    assert packet["doctrine_registry_required"] is True
