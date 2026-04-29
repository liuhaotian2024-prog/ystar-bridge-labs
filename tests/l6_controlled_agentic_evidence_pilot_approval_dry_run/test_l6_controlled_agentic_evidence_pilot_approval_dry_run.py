import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DIRS = [
    "l6_controlled_agentic_evidence_pilot_approval_dry_run",
    "agentic_work_order_pilot_selector",
    "agentic_pilot_approval_eligibility_gate",
    "agentic_pilot_approval_packet_assembler",
    "agentic_pilot_sandbox_approval_records",
    "agentic_pilot_runtime_readiness_package",
    "agentic_pilot_dry_run_executor",
    "agentic_pilot_empty_evidence_capture_simulator",
    "agentic_pilot_post_run_review_simulator",
    "agentic_pilot_residual_and_refinement_candidates",
    "agentic_pilot_real_execution_blockers",
    "agentic_pilot_no_action_receipts",
    "l6_agentic_pilot_dry_run_strategic_residual_loop",
    "l6_agentic_pilot_dry_run_readiness_report",
]

JSON_PATHS = [
    "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_milestone_contract.json",
    "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_scope.json",
    "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_safety_flags.json",
    "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_summary.json",
    "agentic_work_order_pilot_selector/l6_8_work_order_inventory.json",
    "agentic_work_order_pilot_selector/work_order_pilot_selection_matrix.json",
    "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json",
    "agentic_work_order_pilot_selector/deferred_agentic_pilot_work_orders.json",
    "agentic_pilot_approval_eligibility_gate/approval_eligibility_contract.json",
    "agentic_pilot_approval_eligibility_gate/approval_eligibility_matrix.json",
    "agentic_pilot_approval_eligibility_gate/eligible_work_orders.json",
    "agentic_pilot_approval_eligibility_gate/ineligible_work_orders.json",
    "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_schema.json",
    "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json",
    "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_validation_matrix.json",
    "agentic_pilot_sandbox_approval_records/sandbox_approval_record_schema.json",
    "agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json",
    "agentic_pilot_sandbox_approval_records/sandbox_approval_record_lifecycle_replay.json",
    "agentic_pilot_runtime_readiness_package/runtime_readiness_contract.json",
    "agentic_pilot_runtime_readiness_package/runtime_readiness_packet_index.json",
    "agentic_pilot_runtime_readiness_package/prohibited_runtime_actions.json",
    "agentic_pilot_dry_run_executor/dry_run_executor_contract.json",
    "agentic_pilot_dry_run_executor/dry_run_sequence.json",
    "agentic_pilot_dry_run_executor/dry_run_trace_index.json",
    "agentic_pilot_empty_evidence_capture_simulator/empty_evidence_capture_contract.json",
    "agentic_pilot_empty_evidence_capture_simulator/empty_evidence_packet_template.json",
    "agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json",
    "agentic_pilot_post_run_review_simulator/post_run_review_contract.json",
    "agentic_pilot_post_run_review_simulator/post_run_review_packet_index.json",
    "agentic_pilot_residual_and_refinement_candidates/dry_run_residual_registry.json",
    "agentic_pilot_residual_and_refinement_candidates/dry_run_refinement_candidate_index.json",
    "agentic_pilot_real_execution_blockers/real_execution_blocker_contract.json",
    "agentic_pilot_real_execution_blockers/real_execution_blocker_matrix.json",
    "agentic_pilot_real_execution_blockers/future_real_pilot_entry_conditions.json",
    "agentic_pilot_real_execution_blockers/blocked_real_execution_decisions.json",
    "l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_cieu_like_fixture.json",
    "l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_strategic_residual_delta.json",
    "l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_meta_learning_update_candidate.json",
    "l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json",
    "l6_agentic_pilot_dry_run_readiness_report/l6_9_next_milestone_recommendation.json",
    "l6_agentic_pilot_dry_run_readiness_report/l6_9_blockers.json",
    "console_read_model/generated/l6_agentic_pilot_dry_run_summary.json",
]

FALSE_AUTH_FIELDS = [
    "real_external_observation_authorized",
    "real_pilot_execution_authorized",
    "real_approval_granted",
    "durable_real_approval_record_created",
    "agent_external_fetch_authorized",
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

FALSE_SAFETY_FLAGS = [
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


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_l6_9_directories_exist():
    for directory in DIRS:
        assert (ROOT / directory).is_dir(), directory


def test_all_required_json_files_parse():
    for path in JSON_PATHS:
        assert (ROOT / path).is_file(), path
        load_json(path)


def test_milestone_contract_and_authorizations():
    contract = load_json("l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_milestone_contract.json")
    assert contract["milestone_id"] == "L6.9"
    assert contract["input_milestones"] == [
        "L6.0",
        "L6.1",
        "L6.2",
        "L6.3",
        "L6.4",
        "L6.5",
        "L6.6",
        "L6.7",
        "L6.8",
    ]
    assert contract["mode"] == "pilot_approval_and_dry_run_only"
    assert contract["agentic_work_order_selection_authorized"] is True
    assert contract["pilot_approval_packet_generation_authorized"] is True
    assert contract["sandbox_approval_record_generation_authorized"] is True
    assert contract["dry_run_lifecycle_simulation_authorized"] is True
    assert contract["empty_evidence_capture_simulation_authorized"] is True
    assert contract["future_tiny_real_read_only_pilot_candidate_allowed"] is True
    for field in FALSE_AUTH_FIELDS:
        assert contract[field] is False, field


def test_safety_flags_block_all_real_surfaces():
    flags = load_json("l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_safety_flags.json")
    safety = flags["safety_flags"]
    for field in FALSE_SAFETY_FLAGS:
        assert safety[field] is False, field
    assert safety["agent_external_fetch_enabled"] is False
    assert safety["durable_real_approval_record_creation_enabled"] is False
    assert safety["real_approval_grant_enabled"] is False
    assert safety["semantic_truth_scoring_enabled"] is False
    assert safety["llm_confidence_as_authority_enabled"] is False


def test_work_order_selector_selects_structurally_from_l6_8():
    selected = load_json("agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json")
    matrix = load_json("agentic_work_order_pilot_selector/work_order_pilot_selection_matrix.json")
    work_orders = selected["selected_work_orders"]
    assert 1 <= selected["selected_count"] <= 3
    assert matrix["hard_coded_opportunity_categories_used"] is False
    assert matrix["source_categories_exhaustive"] is False
    required_factors = {
        "evidence_need_importance",
        "value_of_information",
        "trust_tier_candidate",
        "read_only_feasibility",
        "clear_claim_boundary",
        "future_approval_feasibility",
    }
    assert required_factors.issubset(set(matrix["selection_factors"]))
    for item in work_orders:
        assert item["linked_l6_8_work_order_id"].startswith("l6_8_observation_work_order_")
        assert item["approval_packet_required"] is True
        assert item["sandbox_approval_record_required"] is True
        assert item["dry_run_authorized_now"] is True
        assert item["real_observation_authorized_now"] is False
        assert item["hard_coded_opportunity_category_used"] is False


def test_approval_eligibility_gate_exists_and_keeps_real_observation_blocked():
    matrix = load_json("agentic_pilot_approval_eligibility_gate/approval_eligibility_matrix.json")
    assert matrix["eligible_count"] >= 1
    for result in matrix["eligibility_results"]:
        assert result["eligible_for_sandbox_packet_assembly"] is True
        assert result["checks"]["source_locator_placeholder_only"] is True
        assert result["checks"]["no_login_expected"] is True
        assert result["checks"]["no_payment_expected"] is True
        assert result["checks"]["no_mcp_execution_expected"] is True
        assert result["checks"]["real_observation_remains_unauthorized"] is True


def test_approval_packets_do_not_authorize_observation():
    index = load_json("agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json")
    assert index["approval_packet_count"] >= 1
    for packet_ref in index["approval_packets"]:
        packet = load_json(packet_ref["path"])
        assert packet["approval_status"] == "sandbox_packet_generated_pending_future_human_approval"
        assert packet["human_approval_required"] is True
        assert packet["durable_approval_record_required"] is True
        assert packet["real_approval_granted"] is False
        assert packet["real_observation_authorized"] is False


def test_sandbox_approval_records_are_dry_run_only():
    index = load_json("agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json")
    for record_ref in index["sandbox_records"]:
        record = load_json(record_ref["path"])
        assert record["sandbox_dry_run_use_only"] is True
        assert record["real_approval_granted"] is False
        assert record["durable_real_approval_record_created"] is False
        assert record["real_observation_authorized"] is False
        assert record["real_network_authorized"] is False
    replay = load_json("agentic_pilot_sandbox_approval_records/sandbox_approval_record_lifecycle_replay.json")
    assert replay["real_observation_authorized_by_any_state"] is False


def test_runtime_readiness_does_not_activate_network_or_runtime():
    index = load_json("agentic_pilot_runtime_readiness_package/runtime_readiness_packet_index.json")
    for packet_ref in index["runtime_packets"]:
        packet = load_json(packet_ref["path"])
        assert packet["no_network_activated"] is True
        assert packet["no_browser_launched"] is True
        assert packet["no_search_performed"] is True
        assert packet["no_external_tool_executed"] is True
        assert packet["no_mcp_executed"] is True
        assert packet["execution_authorized"] is False
        assert packet["network_authorized"] is False


def test_dry_run_traces_show_no_external_observation():
    index = load_json("agentic_pilot_dry_run_executor/dry_run_trace_index.json")
    assert index["dry_run_trace_count"] >= 1
    for trace_ref in index["dry_run_traces"]:
        trace = load_json(trace_ref["path"])
        assert trace["observation_step"] == "skipped_no_network"
        assert trace["real_observation_executed"] is False
        assert trace["network_used"] is False
        assert trace["url_opened"] is False
        assert trace["search_performed"] is False
        assert trace["evidence_captured_from_live_source"] is False
        assert trace["dry_run_completed"] is True


def test_empty_evidence_packets_do_not_claim_real_evidence():
    index = load_json("agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json")
    for packet_ref in index["empty_evidence_packets"]:
        packet = load_json(packet_ref["path"])
        assert packet["live_source_evidence_captured"] is False
        assert packet["captured_claims"] == []
        assert packet["freshness_class"] == "not_observed"
        assert "no live observation executed" in packet["missing_context"]
        assert packet["external_action_taken"] is False
        assert packet["publication_taken"] is False
        assert packet["outreach_taken"] is False
        assert packet["payment_taken"] is False
        assert packet["revenue_action_taken"] is False
        assert packet["mcp_execution_taken"] is False


def test_post_run_review_does_not_authorize_externalization_or_mutation():
    index = load_json("agentic_pilot_post_run_review_simulator/post_run_review_packet_index.json")
    for review_ref in index["post_run_review_packets"]:
        review = load_json(review_ref["path"])
        assert "dry_run_no_evidence_to_review" in review["review_decisions"]
        assert "maintain_externalization_block" in review["review_decisions"]
        assert "no_artifact_refinement_applied" in review["review_decisions"]
        assert review["externalization_authorized"] is False
        assert review["artifact_update_authorized"] is False
        assert review["canonical_update_authorized"] is False
        assert review["brain_writeback_authorized"] is False
        assert review["memory_ingestion_authorized"] is False
        assert review["direct_y_star_mutation_authorized"] is False


def test_residual_refinement_candidates_are_review_only_and_not_applied():
    index = load_json("agentic_pilot_residual_and_refinement_candidates/dry_run_refinement_candidate_index.json")
    for candidate_ref in index["candidates"]:
        candidate = load_json(candidate_ref["path"])
        assert candidate["review_required"] is True
        assert candidate["approved"] is False
        assert candidate["applied"] is False
        assert candidate["artifact_update_authorized"] is False
        assert candidate["canonical_update_authorized"] is False
        assert candidate["brain_writeback_authorized"] is False
        assert candidate["memory_ingestion_authorized"] is False
        assert candidate["direct_y_star_mutation_authorized"] is False


def test_real_execution_blockers_exist():
    blockers = load_json("agentic_pilot_real_execution_blockers/real_execution_blocker_matrix.json")
    assert blockers["real_execution_authorized"] is False
    required = {
        "no future explicit human approval yet",
        "no durable real approval record",
        "no runtime isolation confirmation",
        "no operator confirmation",
        "real network still not authorized in L6.9",
    }
    assert required.issubset(set(blockers["blockers"]))
    decisions = load_json("agentic_pilot_real_execution_blockers/blocked_real_execution_decisions.json")
    for decision in decisions["decisions"]:
        assert decision["real_execution_decision"].startswith("blocked_")
        assert decision["real_network_authorized"] is False
        assert decision["execution_authorized"] is False


def test_no_action_receipts_exist_and_executed_flags_false():
    receipt_dir = ROOT / "agentic_pilot_no_action_receipts"
    receipts = sorted(path for path in receipt_dir.glob("*.json"))
    assert len(receipts) >= 19
    for path in receipts:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["authorized_in_l6_9"] is False
        assert payload["executed_in_l6_9"] is False


def test_strategic_residual_fixture_and_meta_learning_are_review_only():
    fixture = load_json("l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_cieu_like_fixture.json")
    assert fixture["event_mode"] == "l6_9_controlled_read_only_agentic_evidence_pilot_approval_dry_run_fixture"
    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in fixture
    candidate = load_json("l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_meta_learning_update_candidate.json")
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_direct_strategy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_recommends_l6_10_and_blocks_network_now():
    readiness = load_json("l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json")
    assert readiness["l6_9_controlled_read_only_agentic_evidence_pilot_approval_and_dry_run_complete"] is True
    assert readiness["ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot"] is True
    assert readiness["ready_for_actual_network_observation_now"] is False
    assert readiness["ready_for_autonomous_web_search_now"] is False
    assert readiness["ready_for_scraping"] is False
    assert readiness["ready_for_publication"] is False
    assert readiness["ready_for_outreach"] is False
    assert readiness["ready_for_payment"] is False
    assert readiness["ready_for_revenue_execution"] is False
    assert readiness["ready_for_mcp_execution"] is False
    assert readiness["ready_for_canonical_update"] is False
    assert readiness["ready_for_brain_memory_writeback"] is False
    assert readiness["next_recommended_milestone"] == "L6.10 Tiny Real Read-Only Agentic Evidence Observation Pilot v0"


def test_console_read_model_command_works():
    result = subprocess.run(
        [
            "python3",
            "console_read_model/cli/team_console.py",
            "controlled-agentic-evidence-pilot-approval-dry-run",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "L6.9 Controlled Agentic Evidence Pilot Approval Dry-Run" in result.stdout
    assert "real external observation authorized: False" in result.stdout
    assert "ready for L6.10 tiny real read-only agentic evidence observation pilot: True" in result.stdout


def test_l6_9_builder_has_no_network_execution_imports_or_calls():
    builder = ROOT / "l6_controlled_agentic_evidence_pilot_approval_dry_run/tools/build_l6_controlled_agentic_evidence_pilot_approval_dry_run.py"
    text = builder.read_text(encoding="utf-8")
    forbidden = [
        "import requests",
        "import httpx",
        "urllib.request",
        "import aiohttp",
        "import selenium",
        "import playwright",
        "import socket",
        "curl ",
        "wget ",
    ]
    for marker in forbidden:
        assert marker not in text
