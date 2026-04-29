from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

L6_6_DIRS = [
    "l6_controlled_observation_pilot_approval_packet",
    "pilot_approval_candidate_selector",
    "pilot_approval_authority_model",
    "pilot_approval_packet_assembler",
    "pilot_approval_evidence_dossier",
    "pilot_approval_risk_review",
    "pilot_operator_authorization_prerequisites",
    "pilot_runtime_isolation_attestation",
    "pilot_evidence_capture_authorization",
    "pilot_approval_no_action_constraints",
    "pilot_approval_decision_sandbox",
    "pilot_approval_non_persistence_receipts",
    "l6_pilot_approval_strategic_residual_loop",
    "l6_pilot_approval_readiness",
]

BLOCKED_AUTH_FIELDS = [
    "real_external_observation_authorized",
    "real_pilot_execution_authorized",
    "real_approval_granted",
    "durable_real_approval_record_created",
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


def all_l6_6_json_paths() -> list[Path]:
    paths: list[Path] = []
    for dirname in L6_6_DIRS:
        paths.extend(sorted((ROOT / dirname).rglob("*.json")))
    return paths


def test_l6_6_directories_exist_and_json_parse() -> None:
    for dirname in L6_6_DIRS:
        assert (ROOT / dirname).is_dir(), dirname
    json_paths = all_l6_6_json_paths()
    assert json_paths
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))


def test_milestone_contract_is_approval_packet_only_and_blocks_real_approval() -> None:
    contract = load_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.6"
    assert contract["input_milestones"] == ["L6.0", "L6.1", "L6.2", "L6.3", "L6.4", "L6.5"]
    assert contract["mode"] == "approval_packet_only"
    assert contract["approval_packet_only"] is True
    assert contract["approval_sandbox_only"] is True
    assert contract["future_real_read_only_observation_pilot_candidate_allowed"] is True
    assert contract["approval_packet_generation_authorized"] is True
    assert contract["approval_decision_sandbox_authorized"] is True
    assert contract["operator_authorization_template_authorized"] is True
    assert contract["runtime_isolation_attestation_template_authorized"] is True
    assert contract["evidence_capture_authorization_template_authorized"] is True
    assert contract["requires_future_explicit_human_approval_before_real_observation"] is True
    assert contract["requires_future_durable_approval_record_before_real_observation"] is True
    for field in BLOCKED_AUTH_FIELDS:
        assert contract[field] is False, field
    for field in BLOCKED_SAFETY_FLAGS:
        assert contract["safety_flags"][field] is False, field


def test_candidate_selector_uses_structural_approval_readiness() -> None:
    selected = load_json("pilot_approval_candidate_selector/selected_approval_candidates.json")
    candidates = selected["candidates"]
    assert 1 <= len(candidates) <= 3
    assert selected["selected_by_hardcoded_opportunity_category"] is False
    assert selected["hardcoded_opportunity_class_used"] is False
    required_factors = {
        "linked L6.5 pilot candidate exists",
        "pilot design packet exists",
        "approval packet candidate exists or can be assembled",
        "observation question is narrow",
        "source locator placeholder exists",
        "source type is allowlisted",
        "no login required",
        "no payment required",
        "no contact required",
        "no form submission required",
        "no MCP execution required",
        "evidence capture template exists",
        "operator runbook exists",
        "runtime isolation prerequisite can be represented",
    }
    for candidate in candidates:
        assert required_factors.issubset(set(candidate["selection_factors"]))
        assert candidate["approval_packet_authorized_now"] is True
        assert candidate["real_approval_authorized_now"] is False
        assert candidate["real_observation_authorized_now"] is False
        assert candidate["durable_approval_record_authorized_now"] is False
        assert candidate["future_human_approval_required"] is True
        assert candidate["future_runtime_isolation_required"] is True
        assert candidate["selected_by_hardcoded_opportunity_category"] is False


def test_authority_model_disallows_automated_or_inferred_approval() -> None:
    model = load_json("pilot_approval_authority_model/approval_authority_model.json")
    roles = load_json("pilot_approval_authority_model/approval_role_registry.json")
    policy = load_json("pilot_approval_authority_model/non_delegable_human_approval_policy.json")
    assert model["l6_6_does_not_grant_real_approval"] is True
    assert model["automated_approval_allowed"] is False
    assert model["candidate_auto_approval_allowed"] is False
    assert model["approval_inferred_from_tests_allowed"] is False
    assert model["approval_inferred_from_readiness_allowed"] is False
    assert model["approval_inferred_from_packet_completeness_allowed"] is False
    assert model["future_explicit_human_approval_required"] is True
    assert model["future_durable_approval_record_required"] is True
    approvers = {role["role_id"] for role in roles["roles"] if role["may_future_approve"]}
    assert approvers == {"human_approver"}
    assert policy["approval_non_delegable_to_automation"] is True
    assert policy["real_approval_granted_in_l6_6"] is False


def test_approval_packets_do_not_grant_approval_or_authorize_observation() -> None:
    index = load_json("pilot_approval_packet_assembler/approval_packet_index.json")
    assert 1 <= index["packet_count"] <= 3
    for packet_ref in index["packets"]:
        packet = load_json(packet_ref["path"])
        assert packet["approval_status"] in {
            "approval_packet_generated_pending_future_human_approval",
            "blocked_pending_future_human_approval",
        }
        assert packet["real_approval_granted"] is False
        assert packet["real_observation_authorized"] is False
        assert packet["human_approval_required"] is True
        assert packet["durable_approval_record_required"] is True
        assert packet["no_login_required"] is True
        assert packet["no_account_required"] is True
        assert packet["no_contact_required"] is True
        assert packet["no_payment_required"] is True
        assert packet["no_form_submission_required"] is True
        assert packet["no_mcp_required"] is True
        assert packet["no_direct_y_star_mutation_required"] is True
        assert "PLACEHOLDER LOCATOR ONLY" in packet["source_locator_placeholder"]
        assert "NOT FETCHED" in packet["source_locator_placeholder"]


def test_evidence_dossiers_link_back_to_l6_0_through_l6_5() -> None:
    index = load_json("pilot_approval_evidence_dossier/evidence_dossier_index.json")
    assert 1 <= index["dossier_count"] <= 3
    for dossier_ref in index["dossiers"]:
        dossier = load_json(dossier_ref["path"])
        assert dossier["source_l6_0_hypothesis_trace"]
        assert dossier["source_l6_1_artifact_case_trace"]
        assert dossier["source_l6_2_boundary_trace"]
        assert dossier["source_l6_3_sandbox_trace"]
        assert dossier["source_l6_4_preflight_trace"]
        assert dossier["source_l6_5_pilot_design_trace"]
        assert dossier["dossier_status"] in {
            "dossier_ready_for_review",
            "dossier_incomplete",
            "blocked_pending_future_review",
        }
        assert dossier["approved"] is False


def test_risk_review_is_structural_and_cannot_approve_observation() -> None:
    contract = load_json("pilot_approval_risk_review/risk_review_contract.json")
    assert contract["risk_review_mode"] == "structural_only_no_semantic_truth_scoring"
    assert contract["semantic_truth_scoring_used"] is False
    assert contract["risk_review_can_approve_real_observation"] is False
    forbidden = re.compile(r"truth_score|semantic_truth_score|market_success_score|llm_confidence", re.I)
    for path in sorted((ROOT / "pilot_approval_risk_review").glob("*.json")):
        assert not forbidden.search(path.read_text(encoding="utf-8"))


def test_operator_runtime_and_evidence_authorizations_remain_templates_or_blocked() -> None:
    operator = load_json("pilot_operator_authorization_prerequisites/operator_authorization_contract.json")
    runtime = load_json("pilot_runtime_isolation_attestation/runtime_isolation_attestation_template.json")
    evidence = load_json("pilot_evidence_capture_authorization/evidence_capture_authorization_template.json")
    assert operator["operator_authorization_status"] == "blocked_pending_future_human_approval_and_durable_record"
    assert operator["real_operator_authorization_granted"] is False
    assert runtime["template_only"] is True
    assert runtime["attestation_status"] in {
        "template_only",
        "blocked_pending_future_runtime_confirmation",
    }
    assert runtime["no_mcp_execution_confirmed"] is False
    assert evidence["template_only"] is True
    assert evidence["authorization_status"] == "template_only_pending_future_approval"
    assert evidence["real_evidence_capture_authorized"] is False


def test_no_action_constraints_block_downstream_actions() -> None:
    constraints = load_json("pilot_approval_no_action_constraints/disallowed_downstream_actions.json")
    actions = set(constraints["disallowed_downstream_actions"])
    for action in [
        "publication",
        "outreach",
        "payment",
        "revenue execution",
        "customer contact",
        "form submission",
        "posting/commenting/messaging",
        "MCP execution",
        "live behavior",
        "CIEU DB write",
        "canonical update",
        "strategy mutation",
        "brain/memory writeback",
        "direct Y-star mutation",
        "external artifact delivery",
        "product launch",
        "grant/RFP/bounty submission",
    ]:
        assert action in actions


def test_decision_sandbox_blocks_real_approval_and_durable_record() -> None:
    matrix = load_json("pilot_approval_decision_sandbox/approval_packet_decision_matrix.json")
    assert 1 <= matrix["decision_count"] <= 3
    for decision in matrix["decisions"]:
        assert decision["packet_completeness_decision"] in {"ready_for_review", "incomplete"}
        assert decision["real_approval_decision"] == "blocked_pending_future_explicit_human_approval"
        assert decision["real_observation_decision"] == "blocked_pending_future_durable_approval_record"
        assert decision["real_network_authorized"] is False
        assert decision["execution_authorized"] is False
        assert decision["durable_approval_record_created"] is False
        assert decision["review_required"] is True
        assert decision["human_approval_required"] is True
        assert decision["future_runtime_isolation_required"] is True
        assert decision["future_milestone_required"] is True


def test_non_persistence_receipts_exist_and_executed_flags_are_false() -> None:
    receipt_paths = sorted((ROOT / "pilot_approval_non_persistence_receipts").glob("*_receipt.json"))
    assert receipt_paths
    names = {path.name for path in receipt_paths}
    assert "no_durable_real_approval_record_receipt.json" in names
    assert "no_real_approval_granted_receipt.json" in names
    for path in receipt_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["authorized_in_l6_6"] is False
        assert data["executed_in_l6_6"] is False
        if "persisted_in_l6_6" in data:
            assert data["persisted_in_l6_6"] is False


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    fixture = load_json("l6_pilot_approval_strategic_residual_loop/l6_6_cieu_like_fixture.json")
    update = load_json(
        "l6_pilot_approval_strategic_residual_loop/l6_6_meta_learning_update_candidate.json"
    )
    assert fixture["event_mode"] == "l6_6_controlled_real_read_only_observation_pilot_approval_packet_fixture"
    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert fixture["real_approval_granted"] is False
    assert update["eligible_for_review_queue"] is True
    assert update["eligible_for_direct_brain_writeback"] is False
    assert update["eligible_for_direct_memory_ingestion"] is False
    assert update["eligible_for_candidate_auto_approval"] is False
    assert update["eligible_for_direct_strategy_mutation"] is False
    assert update["approved"] is False
    assert update["applied"] is False


def test_readiness_blocks_network_real_approval_and_durable_persistence_now() -> None:
    readiness = load_json("l6_pilot_approval_readiness/l6_6_readiness_assessment.json")
    assert readiness["l6_6_controlled_pilot_approval_packet_complete"] is True
    assert readiness["ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox"] is True
    assert readiness["ready_for_actual_network_observation_now"] is False
    assert readiness["ready_for_real_approval_now"] is False
    assert readiness["ready_for_durable_approval_persistence_now"] is False
    assert readiness["ready_for_publication"] is False
    assert readiness["ready_for_outreach"] is False
    assert readiness["ready_for_payment"] is False
    assert readiness["ready_for_revenue_execution"] is False
    assert readiness["ready_for_mcp_execution"] is False
    assert readiness["ready_for_canonical_update"] is False
    assert readiness["ready_for_brain_memory_writeback"] is False
    assert (
        readiness["next_recommended_milestone"]
        == "L6.7 Controlled Real Read-Only Observation Approval Record Sandbox v0"
    )


def test_console_read_model_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-observation-pilot-approval-packet",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.6 Controlled Observation Pilot Approval Packet" in result.stdout
    assert "real approval granted: False" in result.stdout
    assert "durable real approval record created: False" in result.stdout


def test_l6_6_builder_does_not_import_or_call_network_execution_libraries() -> None:
    builder = (
        ROOT
        / "l6_controlled_observation_pilot_approval_packet"
        / "tools"
        / "build_l6_controlled_observation_pilot_approval_packet.py"
    )
    text = builder.read_text(encoding="utf-8")
    forbidden_patterns = [
        r"^\s*import\s+requests\b",
        r"^\s*from\s+requests\b",
        r"^\s*import\s+httpx\b",
        r"^\s*from\s+httpx\b",
        r"^\s*import\s+urllib\.request\b",
        r"^\s*from\s+urllib\.request\b",
        r"^\s*import\s+aiohttp\b",
        r"^\s*from\s+aiohttp\b",
        r"^\s*import\s+selenium\b",
        r"^\s*from\s+selenium\b",
        r"^\s*import\s+playwright\b",
        r"^\s*from\s+playwright\b",
        r"^\s*import\s+socket\b",
        r"^\s*from\s+socket\b",
        r"^\s*import\s+subprocess\b",
        r"subprocess\.",
        r"\bcurl\b",
        r"\bwget\b",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, text, flags=re.MULTILINE) is None, pattern
