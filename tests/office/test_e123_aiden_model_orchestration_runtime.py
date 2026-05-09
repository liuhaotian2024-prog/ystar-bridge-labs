from __future__ import annotations

from office.mission_command.e123_aiden_model_orchestration_runtime import (
    build_model_orchestration_packet,
    classify_aiden_task,
    discover_local_long_term_memory_assets,
    run_aiden_model_orchestration_session,
    select_model_for_task,
)


def test_discovers_reusable_local_memory_assets() -> None:
    discovery = discover_local_long_term_memory_assets()
    asset_ids = {item["asset_id"] for item in discovery["assets"]}
    assert "CIEUStore_formal_memory" in asset_ids
    assert "Aiden_6D_brain" in asset_ids
    assert "YstarGov_memory_store" in asset_ids
    assert "legacy_gemma_shadow_quality_client" in asset_ids
    assert discovery["reuse_conclusion"]


def test_low_risk_private_task_selects_local_gemma() -> None:
    task = classify_aiden_task("Summarize private local memory assets for Aiden.")
    selected = select_model_for_task(task)
    assert selected["model_id"] == "local_gemma4_e4b"


def test_governance_task_selects_deterministic_validator() -> None:
    task = classify_aiden_task("Validate this governance contract.")
    selected = select_model_for_task(task)
    assert selected["model_id"] == "deterministic_validator"


def test_engineering_task_selects_codex_executor_boundary() -> None:
    task = classify_aiden_task("Implement code and tests in the repo.")
    selected = select_model_for_task(task)
    assert selected["model_id"] == "codex_executor"


def test_packet_contains_memory_plan_quality_plan_and_no_direct_policy_mutation(tmp_path) -> None:
    packet = build_model_orchestration_packet(
        "Aiden should decide which model to use for a private local memory task.",
        cieu_db=tmp_path / "e123.db",
    )
    assert packet["memory_context_plan"]["local_long_term_memory_required"] is True
    assert packet["memory_context_plan"]["recent_memory_only"] is False
    assert packet["quality_comparison_plan"]["comparison_required"] is True
    assert packet["routing_policy_update"]["direct_policy_mutation"] is False
    assert packet["truth_constraints"]["external_model_called_without_owner_approval"] is False


def test_high_wisdom_public_task_can_select_external_only_with_owner_approval(tmp_path) -> None:
    packet = build_model_orchestration_packet(
        "Run a global strategy analysis with public market context.",
        cieu_db=tmp_path / "e123.db",
        owner_approved_external_model_use=True,
    )
    assert packet["selected_model"]["model_id"] == "external_gpt"
    assert packet["execution_boundary"]["redacted_context_only"] is True


def test_end_to_end_session_writes_cieustore_record(tmp_path) -> None:
    result = run_aiden_model_orchestration_session(
        owner_intent="Summarize local long-term memory assets and choose a local model.",
        cieu_db=tmp_path / "e123_cieu.db",
        task_id="e123_test_session",
    )
    assert result["YstarGov_model_orchestration_result"]["governance_decision"]["decision"] == "ALLOW"
    assert result["CIEUStore_summary"]["event_count"] >= 1
    assert "AIDEN_MODEL_ORCHESTRATION_DECISION" in result["CIEUStore_summary"]["event_types"]
    assert result["selected_execution_preview"]["actual_generation_executed"] is False
