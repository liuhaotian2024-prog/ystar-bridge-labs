from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "l6_meta_development_mvp_artifact_sandbox"
    / "tools"
    / "build_l6_meta_development_mvp_artifact_sandbox.py"
)

REQUIRED_DIRS = [
    "l6_meta_development_mvp_artifact_sandbox",
    "l6_mvp_artifact_input_selector",
    "mvp_artifact_generation_contract",
    "sandbox_mvp_artifact_templates",
    "selected_mvp_artifact_cases",
    "mvp_artifact_evidence_validation",
    "mvp_artifact_review_gate",
    "mvp_artifact_externalization_boundary",
    "l6_mvp_artifact_strategic_residual_loop",
    "l6_mvp_artifact_sandbox_readiness",
]

REQUIRED_JSON = [
    "l6_meta_development_mvp_artifact_sandbox/l6_1_milestone_contract.json",
    "l6_meta_development_mvp_artifact_sandbox/l6_1_sandbox_scope.json",
    "l6_meta_development_mvp_artifact_sandbox/l6_1_safety_flags.json",
    "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
    "l6_mvp_artifact_input_selector/l6_0_input_reference_map.json",
    "l6_mvp_artifact_input_selector/hypothesis_selection_source_map.json",
    "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json",
    "l6_mvp_artifact_input_selector/rejected_or_deferred_hypotheses_for_l6_1.json",
    "mvp_artifact_generation_contract/mvp_artifact_definition.json",
    "mvp_artifact_generation_contract/mvp_artifact_generation_contract.json",
    "mvp_artifact_generation_contract/mvp_artifact_allowed_forms.json",
    "mvp_artifact_generation_contract/mvp_artifact_disallowed_forms.json",
    "mvp_artifact_generation_contract/mvp_artifact_claim_safety_policy.json",
    "sandbox_mvp_artifact_templates/template_registry.json",
    "selected_mvp_artifact_cases/selected_case_index.json",
    "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json",
    "mvp_artifact_evidence_validation/artifact_evidence_registry.json",
    "mvp_artifact_evidence_validation/artifact_acceptance_criteria_registry.json",
    "mvp_artifact_evidence_validation/artifact_signal_model.json",
    "mvp_artifact_evidence_validation/artifact_quality_gate.json",
    "mvp_artifact_review_gate/review_gate_contract.json",
    "mvp_artifact_review_gate/approval_preconditions.json",
    "mvp_artifact_review_gate/externalization_preflight_checklist.json",
    "mvp_artifact_review_gate/claim_review_checklist.json",
    "mvp_artifact_review_gate/privacy_ip_review_checklist.json",
    "mvp_artifact_externalization_boundary/externalization_blocker.json",
    "mvp_artifact_externalization_boundary/future_boundary_map.json",
    "mvp_artifact_externalization_boundary/non_publication_receipt.json",
    "mvp_artifact_externalization_boundary/non_outreach_receipt.json",
    "mvp_artifact_externalization_boundary/non_payment_receipt.json",
    "mvp_artifact_externalization_boundary/non_network_receipt.json",
    "l6_mvp_artifact_strategic_residual_loop/l6_1_cieu_like_fixture.json",
    "l6_mvp_artifact_strategic_residual_loop/l6_1_strategic_residual_delta.json",
    "l6_mvp_artifact_strategic_residual_loop/l6_1_meta_learning_update_candidate.json",
    "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
    "l6_mvp_artifact_sandbox_readiness/l6_1_next_milestone_recommendation.json",
    "l6_mvp_artifact_sandbox_readiness/l6_1_blockers.json",
]

TEMPLATE_FILES = [
    "sandbox_mvp_artifact_templates/narrative_artifact_template.md",
    "sandbox_mvp_artifact_templates/governance_assurance_artifact_template.md",
    "sandbox_mvp_artifact_templates/methodology_artifact_template.md",
    "sandbox_mvp_artifact_templates/tool_assurance_artifact_template.md",
    "sandbox_mvp_artifact_templates/grant_or_rfp_skeleton_template.md",
    "sandbox_mvp_artifact_templates/internal_diagnostic_report_template.md",
]

BLOCKED_FLAGS = [
    "network_enabled",
    "external_action_enabled",
    "publication_enabled",
    "outreach_enabled",
    "payment_enabled",
    "revenue_execution_enabled",
    "mcp_tool_execution_enabled",
    "live_execution_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
]

BLOCKED_CASE_FIELDS = [
    "execution_authorized",
    "external_observation_authorized",
    "publication_authorized",
    "outreach_authorized",
    "payment_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "canonical_update_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
    "direct_y_star_mutation_authorized",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)


def test_builder_runs() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert "Built L6.1 MVP artifact sandbox artifacts" in result.stdout


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRS:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_JSON:
        assert (ROOT / path).is_file(), path
        load_json(path)


def test_milestone_contract_and_safety_flags() -> None:
    contract = load_json("l6_meta_development_mvp_artifact_sandbox/l6_1_milestone_contract.json")
    assert contract["milestone_id"] == "L6.1"
    assert contract["input_milestone"] == "L6.0"
    assert contract["mode"] == "sandbox_only"
    assert contract["artifact_generation_authorized"] is True
    assert contract["requires_review_before_externalization"] is True
    for field in [
        "external_execution_authorized",
        "publication_authorized",
        "outreach_authorized",
        "payment_authorized",
        "network_authorized",
        "revenue_execution_authorized",
        "mcp_execution_authorized",
        "canonical_update_authorized",
        "direct_y_star_mutation_authorized",
        "brain_writeback_authorized",
        "memory_ingestion_authorized",
    ]:
        assert contract[field] is False
    for field in BLOCKED_FLAGS:
        assert contract["safety_flags"][field] is False


def test_input_selector_references_l6_0_and_structural_selection() -> None:
    refs = load_json("l6_mvp_artifact_input_selector/l6_0_input_reference_map.json")
    required_refs = {
        "open_value_hypothesis_generator/generated_value_hypotheses.json",
        "redeemability_selection_engine/hypothesis_selection_ranking.json",
        "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json",
        "governed_meta_development_experiment_portfolio/governed_experiment_portfolio.json",
        "value_conversion_physics/value_conversion_physics_schema.json",
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json",
    }
    assert required_refs.issubset(set(refs["input_refs"].values()))

    selected = load_json("l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json")
    hypotheses = selected["selected_hypotheses"]
    assert 1 <= len(hypotheses) <= 3
    assert selected["structural_selection_only"] is True
    assert selected["selected_by_category"] is False
    assert selected["hardcoded_opportunity_class_used"] is False
    required_variables = {
        "conversion_path_length",
        "time_to_first_signal",
        "payer_or_recipient_clarity",
        "acceptance_criteria_clarity",
        "advantage_fit",
        "external_action_dependency",
    }
    for hypothesis in hypotheses:
        assert required_variables.issubset(hypothesis["selection_variables"])
        assert hypothesis["artifact_generation_authorized"] is True
        assert hypothesis["external_execution_authorized"] is False
        assert hypothesis["review_required_before_externalization"] is True


def test_allowed_and_disallowed_forms_are_bounded() -> None:
    allowed = load_json("mvp_artifact_generation_contract/mvp_artifact_allowed_forms.json")
    for item in allowed["allowed_forms"]:
        assert item["example_only"] is True
        assert item["not_exhaustive"] is True
        assert item["not_authorized_for_external_use"] is True
    disallowed = load_json("mvp_artifact_generation_contract/mvp_artifact_disallowed_forms.json")
    for form in [
        "published content",
        "sent email/message",
        "submitted grant/RFP/bounty",
        "customer-facing proposal",
        "invoice/payment link",
        "MCP execution",
        "public release",
    ]:
        assert form in disallowed["disallowed_forms"]


def test_templates_contain_sandbox_only_markers() -> None:
    for path in TEMPLATE_FILES:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "SANDBOX ONLY" in text
        assert "NOT FOR PUBLICATION" in text
        assert "OUTREACH" in text
        assert "PAYMENT" in text
        assert "EXTERNAL USE" in text
        for field in [
            "hypothesis_id",
            "source_assets",
            "value_surface",
            "intended_internal_proof",
            "recipient_archetype",
            "acceptance_criteria",
            "evidence_needed",
            "claim_boundaries",
            "missing_evidence",
            "review_gate",
            "externalization_status: blocked",
        ]:
            assert field in text


def test_generated_cases_are_traceable_and_non_executing() -> None:
    index = load_json("selected_mvp_artifact_cases/selected_case_index.json")
    assert 1 <= index["case_count"] <= 3
    for case in index["cases"]:
        case_id = case["case_id"]
        base = f"selected_mvp_artifact_cases/{case_id}"
        contract = load_json(f"{base}/case_contract.json")
        trace = load_json(f"{base}/source_hypothesis_trace.json")
        acceptance = load_json(f"{base}/artifact_acceptance_criteria.json")
        evidence = load_json(f"{base}/artifact_evidence_needed.json")
        claim = load_json(f"{base}/artifact_claim_boundary.json")
        receipt = load_json(f"{base}/artifact_non_execution_receipt.json")
        artifact = (ROOT / base / "generated_artifact.md").read_text(encoding="utf-8")

        assert contract["source_hypothesis_id"] == trace["source_hypothesis_id"]
        assert acceptance["acceptance_criteria"]
        assert evidence["evidence_needed"]
        assert claim["claim_boundaries"]
        assert "SANDBOX ONLY" in artifact
        assert receipt["artifact_generated"] is True
        assert receipt["externalization_status"] == "blocked"
        for field in BLOCKED_CASE_FIELDS:
            assert contract[field] is False
        for field in [
            "network_used",
            "external_observation_executed",
            "publication_performed",
            "outreach_performed",
            "payment_performed",
            "revenue_execution_performed",
            "mcp_execution_performed",
            "live_behavior_executed",
            "canonical_update_performed",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "direct_y_star_mutation_performed",
        ]:
            assert receipt[field] is False


def test_validation_matrix_is_structural_not_authority_scoring() -> None:
    validation = load_json("mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json")
    assert validation["validation_mode"] == "structural_review_only"
    assert validation["l6_1_flags"]["l6_1_internal_artifact_generation_enabled"] is True
    rendered = json.dumps(validation).lower()
    for forbidden in ["truth_score", "semantic_score", "market_success_score"]:
        assert forbidden not in rendered
    for result in validation["case_results"]:
        assert result["semantic_truth_scoring_used"] is False
        assert result["market_success_authority_used"] is False


def test_review_gate_and_externalization_boundary_block_now() -> None:
    gate = load_json("mvp_artifact_review_gate/review_gate_contract.json")
    assert gate["l6_1_artifacts_approved_for_external_use"] is False
    assert gate["externalization_requires_future_milestone"] is True
    for field in BLOCKED_CASE_FIELDS:
        assert gate[field] is False

    blocker = load_json("mvp_artifact_externalization_boundary/externalization_blocker.json")
    assert blocker["publication_blocked_now"] is True
    assert blocker["outreach_blocked_now"] is True
    assert blocker["payment_blocked_now"] is True
    assert blocker["network_blocked_now"] is True
    assert blocker["external_execution_blocked_now"] is True
    assert blocker["revenue_execution_blocked_now"] is True


def test_strategic_residual_fixture_and_meta_learning_are_review_only() -> None:
    fixture = load_json("l6_mvp_artifact_strategic_residual_loop/l6_1_cieu_like_fixture.json")
    assert fixture["event_mode"] == "l6_1_mvp_artifact_sandbox_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert fixture["l6_execution_enabled"] is False

    update = load_json(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_meta_learning_update_candidate.json"
    )
    assert update["eligible_for_review_queue"] is True
    for field in [
        "eligible_for_direct_brain_writeback",
        "eligible_for_direct_memory_ingestion",
        "eligible_for_candidate_auto_approval",
        "eligible_for_direct_strategy_mutation",
        "approved",
        "applied",
    ]:
        assert update[field] is False


def test_readiness_blocks_external_execution_and_points_to_l6_2() -> None:
    readiness = load_json("l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json")
    assert readiness["l6_1_artifact_sandbox_complete"] is True
    assert readiness["ready_for_l6_2_external_observation_boundary_design"] is True
    assert readiness["next_recommended_milestone"] == "L6.2 Governed External Observation Boundary v0"
    for field in [
        "ready_for_external_execution",
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
    run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    result = run_command(
        ["python3", "console_read_model/cli/team_console.py", "meta-development-mvp-artifact-sandbox"]
    )
    assert "L6.1 MVP artifact sandbox defined: True" in result.stdout
    assert "ready for external execution: False" in result.stdout
    assert "ready for revenue execution: False" in result.stdout
