from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

L6_7_DIRS = [
    "l6_integrated_approval_record_and_pilot_readiness_sandbox",
    "sandbox_approval_record_lifecycle",
    "pilot_run_package_assembler",
    "pilot_operator_readiness_package",
    "pilot_runtime_isolation_readiness",
    "pilot_evidence_capture_readiness",
    "pilot_post_observation_review_readiness",
    "manual_evidence_import_readiness",
    "pilot_integrated_decision_gate",
    "pilot_integrated_no_action_receipts",
    "l6_integrated_pilot_readiness_strategic_residual_loop",
    "l6_integrated_pilot_readiness_report",
]

BLOCKED_AUTH_FIELDS = [
    "durable_real_approval_record_created",
    "real_approval_granted",
    "real_external_observation_authorized",
    "real_pilot_execution_authorized",
    "network_authorized",
    "api_authorized",
    "scraping_authorized",
    "browser_fetch_authorized",
    "search_authorized",
    "publication_authorized",
    "outreach_authorized",
    "payment_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "live_behavior_authorized",
    "cieu_db_write_authorized",
    "canonical_update_authorized",
    "direct_y_star_mutation_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
]

BLOCKED_SAFETY_FLAGS = [
    "network_enabled",
    "api_enabled",
    "scraping_enabled",
    "browser_fetch_enabled",
    "search_enabled",
    "publication_enabled",
    "outreach_enabled",
    "payment_enabled",
    "revenue_execution_enabled",
    "mcp_tool_execution_enabled",
    "live_execution_enabled",
    "cieu_db_write_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "durable_approval_persistence_enabled",
    "real_approval_record_write_enabled",
]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def all_l6_7_json_paths() -> list[Path]:
    paths: list[Path] = []
    for dirname in L6_7_DIRS:
        paths.extend(sorted((ROOT / dirname).rglob("*.json")))
    return paths


def test_l6_7_directories_exist_and_json_parse() -> None:
    for dirname in L6_7_DIRS:
        assert (ROOT / dirname).is_dir(), dirname
    json_paths = all_l6_7_json_paths()
    assert json_paths
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))


def test_milestone_contract_is_integrated_sandbox_only() -> None:
    contract = load_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.7"
    assert contract["input_milestones"] == [
        "L6.0",
        "L6.1",
        "L6.2",
        "L6.3",
        "L6.4",
        "L6.5",
        "L6.6",
    ]
    assert contract["mode"] == "integrated_sandbox_only"
    assert contract["approval_record_sandbox_only"] is True
    assert contract["pilot_run_readiness_only"] is True
    assert contract["sandbox_approval_record_created"] is True
    assert contract["manual_evidence_import_future_candidate_allowed"] is True
    for field in BLOCKED_AUTH_FIELDS:
        assert contract[field] is False, field
    for field in BLOCKED_SAFETY_FLAGS:
        assert contract["safety_flags"][field] is False, field


def test_sandbox_approval_lifecycle_records_do_not_authorize_real_execution() -> None:
    state_machine = load_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_lifecycle_state_machine.json"
    )
    states = set(state_machine["states"])
    assert {
        "draft_packet",
        "ready_for_review",
        "blocked_pending_human_approval",
        "sandbox_approved_for_readiness_only",
        "expired",
        "revoked",
        "invalid",
    }.issubset(states)

    index = load_json("sandbox_approval_record_lifecycle/sandbox_approval_record_index.json")
    assert 1 <= index["record_count"] <= 3
    for record_ref in index["records"]:
        record = load_json(record_ref["path"])
        assert record["approval_status"] == "sandbox_approved_for_readiness_only"
        assert record["real_approval_granted"] is False
        assert record["durable_real_approval_record"] is False
        assert record["real_observation_authorized"] is False
        assert record["sandbox_readiness_use_only"] is True
        assert "real observation execution" in record["no_action_constraints"]
        assert "direct Y-star mutation" in record["no_action_constraints"]


def test_pilot_run_packages_are_readiness_only_and_fully_linked() -> None:
    index = load_json("pilot_run_package_assembler/pilot_run_package_index.json")
    assert 1 <= index["package_count"] <= 3
    for package_ref in index["packages"]:
        package = load_json(package_ref["path"])
        assert package["linked_sandbox_approval_record"]
        assert package["linked_approval_packet"]
        assert package["linked_operator_runbook"]
        assert package["linked_runtime_isolation_readiness"]
        assert package["linked_evidence_capture_template"]
        assert package["linked_abort_quarantine_policy"]
        assert package["linked_post_observation_review_workflow"]
        assert package["run_mode"] == "future_manual_read_only_pilot_candidate"
        assert package["real_run_authorized"] is False
        assert package["network_authorized"] is False
        assert package["execution_authorized"] is False
        assert package["future_human_approval_required"] is True


def test_operator_runtime_and_evidence_readiness_remain_non_executing() -> None:
    operator = load_json("pilot_operator_readiness_package/operator_readiness_checklist.json")
    runtime = load_json("pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json")
    evidence = load_json("pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json")

    assert operator["readiness_package_created"] is True
    assert operator["operator_authorized_now"] is False
    assert operator["future_human_approval_required"] is True
    constraints = {entry["constraint"] for entry in operator["checklist"]}
    for constraint in [
        "no login",
        "no account creation",
        "no contact",
        "no payment",
        "no form submission",
        "no posting/commenting/messaging",
        "no publication",
        "no outreach",
        "no revenue action",
        "no MCP execution",
        "no artifact mutation",
        "no canonical strategy mutation",
        "no brain/memory writeback",
        "no direct Y-star mutation",
    ]:
        assert constraint in constraints

    assert runtime["readiness_only"] is True
    assert runtime["real_runtime_isolation_activated"] is False
    assert runtime["network_accessed"] is False
    assert runtime["browser_launched"] is False
    assert runtime["external_tool_executed"] is False

    assert evidence["template_only"] is True
    assert evidence["real_evidence_captured"] is False
    for field in [
        "external_action_taken",
        "publication_taken",
        "outreach_taken",
        "payment_taken",
        "revenue_action_taken",
        "mcp_execution_taken",
        "canonical_update_taken",
        "brain_memory_writeback_taken",
        "direct_y_star_mutation_taken",
    ]:
        assert evidence[field] is False, field


def test_post_observation_review_cannot_authorize_externalization_or_mutation() -> None:
    matrix = load_json("pilot_post_observation_review_readiness/evidence_review_decision_matrix.json")
    decisions = {entry["decision"]: entry for entry in matrix["decisions"]}
    assert {
        "accept_evidence_for_internal_review",
        "quarantine_evidence",
        "reject_evidence",
        "require_additional_source",
        "require_claim_boundary_revision",
        "generate_review_only_artifact_refinement_candidate",
        "block_externalization",
    }.issubset(decisions)
    assert all(entry["direct_externalization_authorized"] is False for entry in decisions.values())

    gate = load_json("pilot_post_observation_review_readiness/artifact_refinement_candidate_gate.json")
    assert gate["review_required"] is True
    for field in [
        "direct_artifact_update_authorized",
        "canonical_update_authorized",
        "brain_memory_writeback_authorized",
        "direct_y_star_mutation_authorized",
    ]:
        assert gate[field] is False, field


def test_manual_evidence_import_readiness_does_not_fetch_urls_or_update_artifacts() -> None:
    contract = load_json("manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json")
    boundary = load_json("manual_evidence_import_readiness/user_supplied_evidence_boundary.json")
    assert contract["future_manual_evidence_import_candidate_allowed"] is True
    assert contract["fetch_urls_authorized"] is False
    assert contract["network_authorized"] is False
    assert contract["source_supplied_by_user_required"] is True
    assert contract["source_content_supplied_by_user_required"] is True
    assert contract["review_required"] is True
    assert contract["automatic_artifact_update_authorized"] is False
    assert boundary["agent_url_fetch_authorized"] is False
    assert boundary["external_action_authorized"] is False


def test_integrated_decision_gate_blocks_real_execution() -> None:
    matrix = load_json("pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json")
    assert 1 <= matrix["decision_count"] <= 3
    for decision in matrix["decisions"]:
        assert decision["sandbox_readiness_decision"] in {
            "ready_for_manual_evidence_import_pilot",
            "incomplete",
        }
        assert (
            decision["real_observation_execution_decision"]
            == "blocked_pending_future_explicit_human_approval"
        )
        assert decision["real_network_authorized"] is False
        assert decision["execution_authorized"] is False
        assert decision["durable_real_approval_record_created"] is False
        assert decision["review_required"] is True
        assert decision["future_milestone_required"] is True


def test_no_action_receipts_exist_and_all_executed_flags_are_false() -> None:
    receipts_dir = ROOT / "pilot_integrated_no_action_receipts"
    receipts = sorted(receipts_dir.glob("*_receipt.json"))
    assert len(receipts) >= 18
    for path in receipts:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert receipt["authorized_in_l6_7"] is False, path.name
        assert receipt["executed_in_l6_7"] is False, path.name
        if "persisted_in_l6_7" in receipt:
            assert receipt["persisted_in_l6_7"] is False, path.name
        assert receipt["future_boundary_required"] == "L6.8 User-Mediated Manual Evidence Import Pilot v0"


def test_strategic_residual_fixture_and_meta_learning_candidate_are_review_only() -> None:
    fixture = load_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_cieu_like_fixture.json"
    )
    candidate = load_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_meta_learning_update_candidate.json"
    )
    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in fixture
    assert fixture["event_mode"] == "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_fixture"
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_direct_strategy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_recommends_l6_8_and_blocks_real_paths() -> None:
    readiness = load_json("l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json")
    assert readiness["l6_7_integrated_approval_record_and_pilot_readiness_sandbox_complete"] is True
    assert readiness["ready_for_l6_8_user_mediated_manual_evidence_import_pilot"] is True
    assert readiness["next_recommended_milestone"] == "L6.8 User-Mediated Manual Evidence Import Pilot v0"
    for field in [
        "ready_for_actual_network_observation_now",
        "ready_for_real_approval_now",
        "ready_for_durable_real_approval_persistence_now",
        "ready_for_publication",
        "ready_for_outreach",
        "ready_for_payment",
        "ready_for_revenue_execution",
        "ready_for_mcp_execution",
        "ready_for_canonical_update",
        "ready_for_brain_memory_writeback",
    ]:
        assert readiness[field] is False, field


def test_console_read_model_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "integrated-approval-record-and-pilot-readiness",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.7 Integrated Approval Record And Pilot Readiness Sandbox" in result.stdout
    assert "real approval granted: False" in result.stdout
    assert "durable real approval record created: False" in result.stdout


def test_l6_7_builder_does_not_import_or_call_network_execution_libraries() -> None:
    builder = ROOT / (
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/tools/"
        "build_l6_integrated_approval_record_and_pilot_readiness_sandbox.py"
    )
    text = builder.read_text(encoding="utf-8")
    forbidden = [
        r"\bimport\s+requests\b",
        r"\bfrom\s+requests\b",
        r"\bimport\s+httpx\b",
        r"\bfrom\s+httpx\b",
        r"urllib\.request",
        r"\bimport\s+aiohttp\b",
        r"\bfrom\s+aiohttp\b",
        r"\bimport\s+selenium\b",
        r"\bfrom\s+selenium\b",
        r"\bimport\s+playwright\b",
        r"\bfrom\s+playwright\b",
        r"\bimport\s+socket\b",
        r"\bfrom\s+socket\b",
        r"\bsubprocess\b",
        r"\bcurl\s+",
        r"\bwget\s+",
    ]
    for pattern in forbidden:
        assert re.search(pattern, text) is None, pattern
