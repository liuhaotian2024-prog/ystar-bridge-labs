from __future__ import annotations

import json
import os
from pathlib import Path

from office.mission_command.e92_ceo_principal_codex_executor_boundary import (
    REQUIRED_CODEX_RECEIPT_FIELDS,
    build_ceo_implementation_order_from_e90_strategy,
    build_ceo_post_codex_residual,
    build_codex_handoff_prompt_from_order,
    build_compliant_codex_execution_receipt,
    discover_existing_executor_assets,
    run_ceo_codex_executor_boundary_session,
    validate_ceo_implementation_order_local,
    validate_codex_execution_receipt_local,
    write_e92_boundary_reports,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def test_ceo_implementation_order_contains_required_boundary_fields():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)

    for field in [
        "order_id",
        "source_owner_intent",
        "CEO_decision_actor",
        "executor_actor",
        "selected_strategy",
        "selected_action",
        "why_this_action",
        "why_not_alternatives",
        "evidence_refs",
        "CIEU_prediction",
        "allowed_repos",
        "allowed_paths",
        "forbidden_actions",
        "tests_required",
        "completion_criteria",
        "required_codex_receipt_fields",
        "post_action_residual_required",
        "no_overclaim_policy",
        "no_hidden_chain_of_thought_policy",
    ]:
        assert order[field]

    assert order["CEO_decision_actor"] != "Codex"
    assert order["executor_actor"] == "Codex"
    assert order["external_action_allowed"] is False
    assert order["truth_constraints"]["Codex_is_executor_not_CEO"] is True
    assert validate_ceo_implementation_order_local(order)["decision"] == "ALLOW"


def test_codex_handoff_prompt_declares_executor_not_ceo():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    prompt = build_codex_handoff_prompt_from_order(order)

    assert "You are Codex, the executor / engineering worker" in prompt
    assert "You are not the CEO" in prompt
    assert "Do not change strategy" in prompt
    assert "Do not expand scope" in prompt
    assert order["order_id"] in prompt
    assert "CodexExecutionReceipt" in prompt


def test_compliant_codex_execution_receipt_validates():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    receipt = build_compliant_codex_execution_receipt(order)

    assert set(REQUIRED_CODEX_RECEIPT_FIELDS).issubset(receipt)
    assert receipt["linked_order_id"] == order["order_id"]
    assert receipt["executor_actor"] == "Codex"
    assert receipt["strategy_changed_by_codex"] is False
    assert receipt["scope_expanded_by_codex"] is False
    assert validate_codex_execution_receipt_local(receipt)["decision"] == "ALLOW"


def test_receipt_strategy_change_escalates():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    receipt = build_compliant_codex_execution_receipt(order)
    receipt["strategy_changed_by_codex"] = True

    assert validate_codex_execution_receipt_local(receipt)["decision"] == "ESCALATE"


def test_receipt_external_action_without_approval_denies():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    receipt = build_compliant_codex_execution_receipt(order)
    receipt["external_action_executed"] = True

    assert validate_codex_execution_receipt_local(receipt)["decision"] == "DENY"


def test_receipt_missing_tests_requires_revision():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    receipt = build_compliant_codex_execution_receipt(order)
    receipt["tests_run"] = []

    assert validate_codex_execution_receipt_local(receipt)["decision"] == "REQUIRE_REVISION"


def test_e90_selected_action_converts_into_ceo_implementation_order():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)

    assert order["strategic_benchmark_id"] == "e90_market_grounded_strategy_run"
    assert "next L4" in json.dumps(order["selected_strategy"], sort_keys=True) or order["selected_action"]
    assert "E90" in order["milestone_id"] or order["milestone_id"].startswith("E92")
    assert order["owner_approval_boundary"]["external_action_allowed"] is False


def test_end_to_end_session_writes_order_receipt_and_residual_cieustore_records(tmp_path):
    result = run_ceo_codex_executor_boundary_session(
        cieu_db=str(tmp_path / "e92_boundary.db"),
        root=BRIDGE_ROOT,
        ystar_gov_root=Y_GOV_ROOT,
    )

    assert result["order_write"]["governance_decision"]["decision"] == "ALLOW"
    assert result["receipt_write"]["governance_decision"]["decision"] == "ALLOW"
    assert result["residual_write"]["governance_decision"]["decision"] == "ALLOW"
    assert result["CIEUStore_record_summary"]["event_count"] >= 3
    assert result["end_to_end_ceo_codex_ceo_chain_proven"] is True
    assert result["post_codex_residual"]["no_external_action_executed"] is True
    assert result["codex_execution_receipt"]["external_action_executed"] is False
    assert result["codex_execution_receipt"]["provider_action_executed"] is False


def test_post_codex_residual_is_produced_without_external_action():
    order = build_ceo_implementation_order_from_e90_strategy(root=BRIDGE_ROOT)
    receipt = build_compliant_codex_execution_receipt(order)
    residual = build_ceo_post_codex_residual(order, receipt)

    assert residual["CEO_decision_actor"] == "bridge_labs_ceo"
    assert residual["executor_actor"] == "Codex"
    assert residual["linked_order_id"] == order["order_id"]
    assert residual["linked_receipt_id"] == receipt["receipt_id"]
    assert residual["no_external_action_executed"] is True
    assert residual["no_customer_revenue_payment_claim"] is True
    assert residual["learning_update"]


def test_existing_executor_assets_and_reports_are_written(tmp_path):
    discovery = discover_existing_executor_assets(root=BRIDGE_ROOT)
    report = write_e92_boundary_reports(
        cieu_db=str(tmp_path / "e92_report.db"),
        root=tmp_path,
        ystar_gov_root=Y_GOV_ROOT,
    )

    assert discovery["asset_count"] > 0
    assert any(item["exists"] for item in discovery["high_value_existing_assets"])
    assert report["end_to_end_chain_proven"] is True
    assert (tmp_path / "operations/codex_executor_boundary/e92_ceo_implementation_order_example.json").exists()
    assert (tmp_path / "operations/codex_executor_boundary/e92_codex_handoff_prompt_example.md").exists()
    assert (tmp_path / "operations/codex_executor_boundary/e92_codex_execution_receipt_example.json").exists()
    assert (tmp_path / "office/mission_command/e92_ceo_principal_codex_executor_boundary_report.json").exists()
    assert (
        tmp_path
        / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e92_ceo_principal_codex_executor_boundary.json"
    ).exists()
