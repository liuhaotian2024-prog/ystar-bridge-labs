from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

L6_5_DIRS = [
    "l6_controlled_real_read_only_observation_pilot_design",
    "pilot_candidate_selector",
    "pilot_scope_and_non_goals",
    "pilot_source_constraint_policy",
    "pilot_approval_packet_candidates",
    "pilot_operator_runbook",
    "pilot_evidence_packet_templates",
    "pilot_post_observation_review_workflow",
    "pilot_abort_quarantine_decision_policy",
    "pilot_success_failure_criteria",
    "pilot_no_action_and_execution_blockers",
    "pilot_design_decision_gate",
    "l6_pilot_design_strategic_residual_loop",
    "l6_pilot_design_readiness",
]

BLOCKED_AUTH_FIELDS = [
    "real_external_observation_authorized",
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
]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def all_l6_5_json_paths() -> list[Path]:
    paths: list[Path] = []
    for dirname in L6_5_DIRS:
        paths.extend(sorted((ROOT / dirname).rglob("*.json")))
    return paths


def test_l6_5_directories_exist_and_json_parse() -> None:
    for dirname in L6_5_DIRS:
        assert (ROOT / dirname).is_dir(), dirname
    json_paths = all_l6_5_json_paths()
    assert json_paths
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))


def test_milestone_contract_is_pilot_design_only_and_blocks_execution() -> None:
    contract = load_json(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.5"
    assert contract["input_milestones"] == ["L6.0", "L6.1", "L6.2", "L6.3", "L6.4"]
    assert contract["mode"] == "pilot_design_only"
    assert contract["pilot_design_only"] is True
    assert contract["preflight_only"] is True
    assert contract["future_real_read_only_observation_pilot_candidate_allowed"] is True
    assert contract["pilot_approval_packet_generation_authorized"] is True
    assert contract["pilot_operator_runbook_authorized"] is True
    assert contract["pilot_evidence_template_authorized"] is True
    assert contract["real_pilot_execution_authorized"] is False
    for field in BLOCKED_AUTH_FIELDS:
        assert contract[field] is False, field
    for field in BLOCKED_SAFETY_FLAGS:
        assert contract["safety_flags"][field] is False, field


def test_candidate_selector_uses_structural_read_only_criteria() -> None:
    selected = load_json("pilot_candidate_selector/selected_pilot_candidates.json")
    candidates = selected["candidates"]
    assert 1 <= len(candidates) <= 3
    assert selected["selected_by_hardcoded_opportunity_category"] is False
    assert selected["hardcoded_opportunity_class_used"] is False
    required_factors = {
        "evidence gap is clear",
        "observation question is narrow",
        "source type is allowlisted in L6.4 policy",
        "no login required",
        "no payment required",
        "no contact required",
        "no form submission required",
        "no MCP execution required",
        "operator can perform manually in future",
    }
    for candidate in candidates:
        assert required_factors.issubset(set(candidate["selection_factors"]))
        assert candidate["real_observation_authorized_now"] is False
        assert candidate["pilot_design_authorized_now"] is True
        assert candidate["future_human_approval_required"] is True
        assert candidate["future_runtime_isolation_required"] is True
        assert candidate["selected_by_hardcoded_opportunity_category"] is False


def test_pilot_scope_excludes_external_actions_and_canonical_updates() -> None:
    scope = load_json("pilot_scope_and_non_goals/pilot_scope_definition.json")
    non_goals = load_json("pilot_scope_and_non_goals/pilot_non_goals.json")
    boundary = load_json("pilot_scope_and_non_goals/pilot_boundary_contract.json")
    scope_text = " ".join(scope["pilot_scope"])
    assert "no publication" in scope_text
    assert "no outreach" in scope_text
    assert "no payment" in scope_text
    assert "no submission" in scope_text
    assert "no strategy mutation" in scope_text
    assert "no brain/memory writeback" in scope_text
    assert "no direct Y-star mutation" in scope_text
    non_goal_text = " ".join(non_goals["pilot_non_goals"])
    for term in ["posting/publishing", "payment or revenue action", "grant/RFP/bounty submission", "MCP execution", "canonical update"]:
        assert term in non_goal_text
    assert boundary["externalization_authorized"] is False
    assert boundary["artifact_update_without_review_authorized"] is False


def test_source_allowlist_and_denylist_are_present_and_blocked_now() -> None:
    allowlist = load_json("pilot_source_constraint_policy/pilot_source_allowlist.json")
    denylist = load_json("pilot_source_constraint_policy/pilot_source_denylist.json")
    allowed = {entry["source_type_id"] for entry in allowlist["source_types"]}
    denied = {entry["source_type_id"] for entry in denylist["source_types"]}
    assert {
        "official_informational_page",
        "public_static_informational_page",
        "public_document_page",
        "public_repository_page",
        "user_supplied_public_locator",
    }.issubset(allowed)
    assert {
        "login_required_page",
        "account_required_page",
        "payment_required_page",
        "contact_form",
        "submission_form",
        "private_customer_data",
        "private_inbox_message_surface",
        "checkout_payment_surface",
        "social_posting_surface",
        "comment_reply_surface",
        "production_mcp_tool_resource",
        "live_agent_control_surface",
        "access_control_bypass_required_source",
        "automated_scraping_required_source",
        "personal_sensitive_data_access_required_source",
    }.issubset(denied)
    assert all(entry["real_access_authorized_in_l6_5"] is False for entry in allowlist["source_types"])
    assert all(entry["denied_in_l6_5"] is True for entry in denylist["source_types"])


def test_approval_packet_candidates_do_not_authorize_real_observation() -> None:
    index = load_json("pilot_approval_packet_candidates/pilot_approval_packet_index.json")
    assert 1 <= index["packet_count"] <= 3
    for packet_ref in index["packets"]:
        packet = load_json(packet_ref["path"])
        assert packet["approval_status"] in {
            "pilot_design_generated",
            "blocked_pending_future_human_approval",
        }
        assert packet["real_observation_authorized"] is False
        assert packet["no_login_required"] is True
        assert packet["no_account_required"] is True
        assert packet["no_contact_required"] is True
        assert packet["no_payment_required"] is True
        assert packet["no_form_submission_required"] is True
        assert packet["no_mcp_required"] is True
        assert packet["no_direct_y_star_mutation_required"] is True
        assert "PLACEHOLDER LOCATOR ONLY" in packet["source_locator_placeholder"]
        assert "NOT FETCHED" in packet["source_locator_placeholder"]


def test_operator_runbook_contains_non_action_constraints() -> None:
    steps = load_json("pilot_operator_runbook/operator_step_sequence.json")
    step_text = " ".join(steps["steps"])
    for term in [
        "confirm future explicit human approval",
        "confirm runtime isolation",
        "do not submit forms",
        "do not log in",
        "do not create accounts",
        "do not message/contact/post/comment",
        "do not pay",
        "do not update artifacts directly",
        "do not update strategy",
        "do not write brain/memory",
    ]:
        assert term in step_text
    assert steps["real_run_executed_in_l6_5"] is False


def test_evidence_templates_are_empty_and_do_not_pretend_capture() -> None:
    template = load_json("pilot_evidence_packet_templates/pilot_evidence_packet_template.json")
    examples = load_json("pilot_evidence_packet_templates/pilot_evidence_packet_examples_empty.json")
    assert template["template_only"] is True
    assert template["real_evidence_captured"] is False
    assert template["captured_claims"] == []
    assert template["source_locator"] == ""
    assert template["external_action_taken"] is False
    assert template["publication_taken"] is False
    assert template["outreach_taken"] is False
    assert template["payment_taken"] is False
    assert template["revenue_action_taken"] is False
    assert examples["examples_are_empty_templates"] is True
    assert examples["real_evidence_captured"] is False


def test_post_review_workflow_does_not_authorize_externalization_or_mutation() -> None:
    contract = load_json(
        "pilot_post_observation_review_workflow/post_observation_review_contract.json"
    )
    policy = load_json(
        "pilot_post_observation_review_workflow/artifact_refinement_review_policy.json"
    )
    assert "block_externalization" in contract["allowed_review_outcomes"]
    for field in [
        "direct_publication_authorized",
        "direct_outreach_authorized",
        "direct_payment_authorized",
        "direct_revenue_execution_authorized",
        "direct_canonical_update_authorized",
        "direct_brain_memory_writeback_authorized",
        "direct_y_star_mutation_authorized",
    ]:
        assert contract[field] is False
    assert policy["artifact_refinement_candidates_allowed"] is True
    assert policy["artifact_refinement_application_authorized"] is False
    assert policy["canonical_update_authorized"] is False


def test_abort_quarantine_policy_has_required_triggers_and_blocks_mutation() -> None:
    registry = load_json("pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json")
    quarantine = load_json("pilot_abort_quarantine_decision_policy/pilot_quarantine_policy.json")
    conditions = {entry["condition"] for entry in registry["abort_conditions"]}
    assert {
        "login required unexpectedly",
        "account creation requested",
        "payment requested",
        "contact requested",
        "form submission required",
        "private/sensitive data encountered",
        "source asks for interaction",
        "source requires automation/scraping",
        "source requires MCP/tool execution",
        "operator uncertainty",
    }.issubset(conditions)
    assert quarantine["quarantined_evidence_cannot_update_artifacts"] is True
    assert quarantine["quarantined_evidence_cannot_update_strategy"] is True
    assert quarantine["quarantined_evidence_cannot_write_brain_memory"] is True
    assert quarantine["quarantined_evidence_cannot_update_canonical_state"] is True
    assert quarantine["quarantined_evidence_cannot_mutate_y_star"] is True


def test_success_failure_criteria_are_structural_not_scoring_authority() -> None:
    success = load_json("pilot_success_failure_criteria/pilot_success_criteria.json")
    failure = load_json("pilot_success_failure_criteria/pilot_failure_criteria.json")
    signal_model = load_json("pilot_success_failure_criteria/pilot_signal_model.json")
    assert "evidence packet completed" in success["success_signals"]
    assert "any forbidden action pressure encountered" in failure["failure_signals"]
    assert success["semantic_truth_scoring_used"] is False
    assert success["market_success_scoring_used"] is False
    assert success["llm_confidence_as_authority_used"] is False
    assert success["revenue_scoring_used"] is False
    combined = json.dumps([success, failure, signal_model]).lower()
    for forbidden in ["truth_score", "semantic_truth_score", "market_success_score", "llm confidence as authority", "revenue_score"]:
        assert forbidden not in combined


def test_no_action_receipts_all_executed_false() -> None:
    for path in (ROOT / "pilot_no_action_and_execution_blockers").glob("*_receipt.json"):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert receipt["authorized_in_l6_5"] is False, path
        assert receipt["executed_in_l6_5"] is False, path


def test_decision_gate_blocks_real_pilot_execution() -> None:
    decisions = load_json("pilot_design_decision_gate/pilot_candidate_decisions.json")
    assert 1 <= decisions["decision_count"] <= 3
    for decision in decisions["decisions"]:
        assert decision["pilot_design_decision"] == "design_packet_ready"
        assert (
            decision["real_observation_execution_decision"]
            == "blocked_pending_future_explicit_human_approval"
        )
        assert decision["real_network_authorized"] is False
        assert decision["execution_authorized"] is False
        assert decision["future_runtime_isolation_required"] is True
        assert decision["future_milestone_required"] is True


def test_strategic_residual_fixture_and_meta_learning_are_review_only() -> None:
    fixture = load_json("l6_pilot_design_strategic_residual_loop/l6_5_cieu_like_fixture.json")
    candidate = load_json(
        "l6_pilot_design_strategic_residual_loop/l6_5_meta_learning_update_candidate.json"
    )
    assert fixture["event_mode"] == "l6_5_controlled_real_read_only_observation_pilot_design_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert fixture["l6_pilot_execution_enabled"] is False
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_direct_strategy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_blocks_execution_and_recommends_future_approval_packet() -> None:
    readiness = load_json("l6_pilot_design_readiness/l6_5_readiness_assessment.json")
    assert readiness["l6_5_controlled_real_read_only_observation_pilot_design_complete"] is True
    assert readiness["ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet"] is True
    assert readiness["next_recommended_milestone"] == (
        "L6.6 Controlled Real Read-Only Observation Pilot Approval Packet v0"
    )
    for field in [
        "ready_for_actual_network_observation_now",
        "ready_for_scraping",
        "ready_for_publication",
        "ready_for_outreach",
        "ready_for_payment",
        "ready_for_revenue_execution",
        "ready_for_mcp_execution",
        "ready_for_canonical_update",
        "ready_for_brain_memory_writeback",
    ]:
        assert readiness[field] is False


def test_console_read_model_command_works() -> None:
    subprocess.run(
        [sys.executable, "console_read_model/loader/build_team_console_snapshot.py"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-real-read-only-observation-pilot-design",
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert "L6.5 Controlled Real Read-Only Observation Pilot Design" in result.stdout
    assert "real pilot execution authorized: False" in result.stdout
    assert "search enabled: False" in result.stdout


def test_l6_5_builder_does_not_import_or_call_network_execution_libraries() -> None:
    builder = (
        ROOT
        / "l6_controlled_real_read_only_observation_pilot_design"
        / "tools"
        / "build_l6_controlled_real_read_only_observation_pilot_design.py"
    )
    text = builder.read_text(encoding="utf-8")
    forbidden_fragments = [
        "import requests",
        "import httpx",
        "urllib.request",
        "import aiohttp",
        "import selenium",
        "import playwright",
        "import socket",
        "subprocess",
        "curl ",
        "wget ",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in text
