from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

L6_8_DIRS = [
    "l6_agentic_evidence_discovery_trust_engine",
    "evidence_need_inference_engine",
    "autonomous_source_hypothesis_generator",
    "source_type_value_model",
    "evidence_trust_judgment_model",
    "evidence_value_of_information_model",
    "source_prioritization_and_ranking_engine",
    "evidence_conflict_and_corrobation_model",
    "observation_work_order_generator",
    "pre_observation_rejection_filter",
    "agentic_evidence_decision_gate",
    "agentic_evidence_no_action_receipts",
    "l6_agentic_evidence_strategic_residual_loop",
    "l6_agentic_evidence_readiness_report",
]

BLOCKED_AUTH_FIELDS = [
    "real_external_observation_authorized",
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
    "durable_real_approval_record_created",
    "real_approval_granted",
]

BLOCKED_SAFETY_FLAGS = [
    "network_enabled",
    "api_enabled",
    "scraping_enabled",
    "browser_fetch_enabled",
    "search_enabled",
    "external_action_enabled",
    "external_observation_execution_enabled",
    "agent_external_fetch_enabled",
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
    "semantic_truth_scoring_enabled",
    "llm_confidence_as_authority_enabled",
]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def all_l6_8_json_paths() -> list[Path]:
    paths: list[Path] = []
    for dirname in L6_8_DIRS:
        paths.extend(sorted((ROOT / dirname).rglob("*.json")))
    return paths


def test_l6_8_directories_exist_and_json_parse() -> None:
    for dirname in L6_8_DIRS:
        assert (ROOT / dirname).is_dir(), dirname
    json_paths = all_l6_8_json_paths()
    assert json_paths
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))


def test_milestone_contract_is_agentic_design_sandbox_only() -> None:
    contract = load_json(
        "l6_agentic_evidence_discovery_trust_engine/l6_8_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.8"
    assert contract["milestone_name"] == (
        "Agentic External Evidence Discovery & Trust Judgment Engine v0"
    )
    assert contract["input_milestones"] == [
        "L6.0",
        "L6.1",
        "L6.2",
        "L6.3",
        "L6.4",
        "L6.5",
        "L6.6",
        "L6.7",
    ]
    assert contract["mode"] == "agentic_evidence_discovery_design_and_sandbox"
    assert contract["autonomous_evidence_need_inference_authorized"] is True
    assert contract["autonomous_source_hypothesis_generation_authorized"] is True
    assert contract["autonomous_evidence_value_judgment_authorized"] is True
    assert contract["autonomous_trust_assessment_authorized"] is True
    assert contract["observation_work_order_generation_authorized"] is True
    assert contract["future_controlled_read_only_observation_pilot_candidate_allowed"] is True
    for field in BLOCKED_AUTH_FIELDS:
        assert contract[field] is False, field
    for field in BLOCKED_SAFETY_FLAGS:
        assert contract["safety_flags"][field] is False, field


def test_evidence_needs_are_inferred_from_l6_artifacts() -> None:
    needs = load_json("evidence_need_inference_engine/inferred_evidence_needs.json")
    assert needs["inferred_from_l6_artifacts"] is True
    assert needs["manual_user_search_required"] is False
    assert needs["evidence_need_count"] == len(needs["evidence_needs"])
    assert needs["evidence_need_count"] >= 8
    required_fields = {
        "evidence_need_id",
        "linked_l6_artifact",
        "uncertainty_or_gap",
        "decision_relevance",
        "expected_evidence_type",
        "freshness_requirement",
        "trust_requirement",
        "consequence_if_missing",
        "whether_real_observation_required_in_future",
        "current_execution_authorized",
    }
    for need in needs["evidence_needs"]:
        assert required_fields.issubset(need)
        assert need["linked_l6_artifact"]
        assert need["decision_relevance"]
        assert need["current_execution_authorized"] is False


def test_source_hypotheses_are_generated_from_needs_not_opportunity_categories() -> None:
    index = load_json("autonomous_source_hypothesis_generator/source_hypothesis_index.json")
    needs = {
        need["evidence_need_id"]
        for need in load_json("evidence_need_inference_engine/inferred_evidence_needs.json")[
            "evidence_needs"
        ]
    }
    assert index["source_hypothesis_count"] == len(index["source_hypotheses"])
    assert index["source_hypothesis_count"] >= 4
    assert index["hardcoded_opportunity_categories_used"] is False
    assert index["source_categories_exhaustive"] is False
    forbidden_categories = re.compile(r"\b(youtube|bounty|grant|consulting|audit)\b", re.I)
    for ref in index["source_hypotheses"]:
        source = load_json(ref["path"])
        assert source["linked_evidence_need_id"] in needs
        assert source["hardcoded_opportunity_category_used"] is False
        assert source["source_categories_exhaustive"] is False
        assert source["real_observation_authorized_now"] is False
        assert source["interaction_required_expected"] is False
        assert source["login_required_expected"] is False
        assert source["payment_required_expected"] is False
        assert source["contact_required_expected"] is False
        assert not forbidden_categories.search(source["source_function"])


def test_source_value_model_has_required_structural_dimensions_and_rejections() -> None:
    dimensions = set(load_json("source_type_value_model/source_value_dimension_registry.json")["dimensions"])
    assert {
        "relevance_to_decision",
        "primary_source_status",
        "authority_or_provenance",
        "freshness_likelihood",
        "specificity",
        "evidence_yield",
        "corroboration_value",
        "contradiction_discovery_value",
        "accessibility_read_only",
        "low_interaction_requirement",
        "low_privacy_risk",
        "low_ip_risk",
        "low_scope_drift_risk",
        "low_overclaim_risk",
        "usefulness_for_artifact_refinement",
        "usefulness_for_future_publication_review",
        "usefulness_for_future_outreach_review",
        "usefulness_for_future_revenue_experiment_review",
    }.issubset(dimensions)
    rejection = set(load_json("source_type_value_model/source_type_rejection_criteria.json")["rejection_criteria"])
    assert {
        "requires login",
        "requires payment",
        "requires account creation",
        "requires contact",
        "requires form submission",
        "accesses private/sensitive data",
        "requires scraping",
        "requires browser automation",
        "requires MCP execution",
    }.issubset(rejection)


def test_trust_judgment_model_is_structural_and_candidate_only() -> None:
    contract = load_json("evidence_trust_judgment_model/evidence_trust_judgment_contract.json")
    dimensions = set(load_json("evidence_trust_judgment_model/trust_dimension_registry.json")["dimensions"])
    matrix = load_json("evidence_trust_judgment_model/trust_judgment_matrix.json")
    assert contract["trust_judgment_mode"] == "structural_pre_observation_candidate_only"
    assert contract["semantic_truth_scoring_used"] is False
    assert contract["llm_confidence_used_as_authority"] is False
    assert contract["market_success_score_used"] is False
    assert {
        "source_provenance",
        "primary_vs_secondary_source",
        "source_date_available",
        "freshness_status",
        "claim_specificity",
        "evidence_traceability",
        "independence_from_interested_party",
        "corroboration_potential",
        "conflict_potential",
        "scope_match",
        "uncertainty_disclosure",
        "privacy_ip_cleanliness",
        "reviewability",
    }.issubset(dimensions)
    for judgment in matrix["trust_judgments"]:
        assert judgment["candidate_only"] is True
        assert judgment["pre_observation"] is True
        assert judgment["not_live_verified"] is True
        assert judgment["not_current_truth"] is True
        assert judgment["review_required"] is True


def test_value_of_information_model_is_not_revenue_or_truth_scoring() -> None:
    contract = load_json("evidence_value_of_information_model/value_of_information_contract.json")
    dimensions = set(load_json("evidence_value_of_information_model/voi_dimension_registry.json")["dimensions"])
    matrix = load_json("evidence_value_of_information_model/evidence_need_voi_matrix.json")
    assert contract["not_revenue_scoring"] is True
    assert contract["semantic_truth_scoring_used"] is False
    assert contract["llm_confidence_used_as_authority"] is False
    assert {
        "uncertainty_reduction",
        "decision_impact",
        "artifact_refinement_impact",
        "externalization_risk_reduction",
        "strategy_relevance_without_strategy_mutation",
        "future_publication_readiness_impact",
        "future_outreach_readiness_impact",
        "future_revenue_experiment_readiness_impact",
        "cost_to_observe",
        "risk_to_observe",
        "time_sensitivity",
        "reversibility",
        "evidence_reusability",
        "compounding_learning_value",
    }.issubset(dimensions)
    assert matrix["rows"]


def test_source_prioritization_ranks_without_authorizing_observation() -> None:
    ranked = load_json("source_prioritization_and_ranking_engine/ranked_source_hypotheses.json")
    assert ranked["ranked_count"] == len(ranked["ranked_source_hypotheses"])
    assert ranked["ranked_count"] >= 1
    assert [item["rank"] for item in ranked["ranked_source_hypotheses"]] == list(
        range(1, ranked["ranked_count"] + 1)
    )
    for item in ranked["ranked_source_hypotheses"]:
        assert item["linked_evidence_need_id"]
        assert item["priority_reason"]
        assert item["trust_tier_candidate"]
        assert item["value_of_information_class"]
        assert item["read_only_feasibility"] in {
            "high",
            "medium",
            "low",
            "candidate_feasible_with_future_approval",
        }
        assert item["real_observation_authorized_now"] is False


def test_conflict_corroboration_model_exists_and_bounds_claim_use() -> None:
    contract = load_json("evidence_conflict_and_corrobation_model/conflict_corroboration_contract.json")
    requirements = load_json(
        "evidence_conflict_and_corrobation_model/corroboration_requirement_registry.json"
    )
    conflict_plan = load_json("evidence_conflict_and_corrobation_model/conflict_detection_plan.json")
    assert contract["purpose"]
    assert "single-source evidence" in contract["purpose"]
    assert "independent corroboration" in " ".join(requirements["rules"]).lower()
    assert conflict_plan["conflict_action"] == "quarantine_or_review_before_artifact_refinement"
    assert "stale source conflicts with newer source" in conflict_plan["conflict_triggers"]
    assert "unsupported inference detected" in conflict_plan["conflict_triggers"]


def test_observation_work_orders_exist_and_require_future_approval() -> None:
    index = load_json("observation_work_order_generator/observation_work_order_index.json")
    assert index["work_order_count"] == len(index["work_orders"])
    assert 1 <= index["work_order_count"] <= 3
    for ref in index["work_orders"]:
        work_order = load_json(ref["path"])
        assert work_order["source_locator_placeholder"].startswith("PLACEHOLDER LOCATOR ONLY")
        assert "NOT FETCHED" in work_order["source_locator_placeholder"]
        assert work_order["read_only_requirement"] is True
        assert work_order["real_observation_authorized_now"] is False
        assert work_order["future_approval_required"] is True
        for field in [
            "login_required_allowed",
            "payment_required_allowed",
            "contact_required_allowed",
            "form_submission_allowed",
            "automation_allowed",
            "mcp_execution_allowed",
            "publication_allowed",
            "outreach_allowed",
            "revenue_action_allowed",
        ]:
            assert work_order[field] is False, field


def test_pre_observation_rejection_filter_exists() -> None:
    rules = set(load_json("pre_observation_rejection_filter/rejection_rule_registry.json")["rejection_rules"])
    rejected_sources = load_json("pre_observation_rejection_filter/rejected_source_hypotheses.json")
    rejected_work_orders = load_json("pre_observation_rejection_filter/rejected_work_orders.json")
    assert {
        "requires login",
        "requires payment",
        "requires account creation",
        "requires contact",
        "requires form submission",
        "requires scraping",
        "requires browser automation",
        "requires MCP execution",
        "accesses private/sensitive data",
        "high overclaim risk",
        "low value of information",
    }.issubset(rules)
    assert rejected_sources["rejected_count"] >= 1
    assert rejected_work_orders["rejected_work_order_count"] >= 1


def test_agentic_evidence_decision_gate_blocks_real_observation_now() -> None:
    matrix = load_json("agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json")
    work_orders = load_json("agentic_evidence_decision_gate/observation_work_order_decisions.json")
    pilot_candidates = load_json("agentic_evidence_decision_gate/future_pilot_candidate_decisions.json")
    allowed_decisions = {
        "generate_future_observation_work_order",
        "defer_source_hypothesis",
        "reject_source_hypothesis",
        "require_corroboration_plan",
        "require_freshness_check",
        "require_human_review_before_future_observation",
        "block_real_observation_now",
    }
    assert {decision["decision"] for decision in matrix["decisions"]}.issubset(allowed_decisions)
    assert any(decision["block_real_observation_now"] is True for decision in matrix["decisions"])
    for decision in matrix["decisions"]:
        assert decision["real_observation_authorized_now"] is False
    for decision in work_orders["work_order_decisions"]:
        assert decision["real_observation_authorized_now"] is False
        assert decision["future_approval_required"] is True
    for decision in pilot_candidates["future_pilot_candidate_decisions"]:
        assert decision["future_controlled_read_only_observation_pilot_candidate"] is True
        assert decision["real_observation_authorized_now"] is False


def test_no_action_receipts_exist_and_all_executed_flags_are_false() -> None:
    receipt_paths = sorted((ROOT / "agentic_evidence_no_action_receipts").glob("*.json"))
    assert receipt_paths
    for path in receipt_paths:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert receipt["authorized_in_l6_8"] is False, path.name
        assert receipt["executed_in_l6_8"] is False, path.name
        assert receipt["future_boundary_required"] == (
            "L6.9 Controlled Read-Only Agentic Evidence Discovery Pilot Approval v0"
        )


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    fixture = load_json("l6_agentic_evidence_strategic_residual_loop/l6_8_cieu_like_fixture.json")
    candidate = load_json(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_meta_learning_update_candidate.json"
    )
    assert {"X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"}.issubset(fixture)
    assert fixture["event_mode"] == "l6_8_agentic_external_evidence_discovery_trust_judgment_fixture"
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_direct_strategy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_recommends_l6_9_and_blocks_network_and_search() -> None:
    readiness = load_json("l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json")
    assert readiness["l6_8_agentic_evidence_discovery_and_trust_judgment_engine_complete"] is True
    assert (
        readiness["ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval"]
        is True
    )
    assert readiness["next_recommended_milestone"] == (
        "L6.9 Controlled Read-Only Agentic Evidence Discovery Pilot Approval v0"
    )
    for field in [
        "ready_for_actual_network_observation_now",
        "ready_for_autonomous_web_search_now",
        "ready_for_scraping",
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
            "agentic-evidence-discovery-trust-engine",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.8 Agentic Evidence Discovery Trust Engine" in result.stdout
    assert "real external observation authorized: False" in result.stdout
    assert "ready for actual network observation now: False" in result.stdout


def test_l6_8_builder_has_no_network_execution_imports_or_curl_wget_calls() -> None:
    builder = ROOT / (
        "l6_agentic_evidence_discovery_trust_engine/tools/"
        "build_l6_agentic_evidence_discovery_trust_engine.py"
    )
    text = builder.read_text(encoding="utf-8")
    forbidden_import = re.compile(
        r"^\s*(?:import|from)\s+"
        r"(requests|httpx|urllib\.request|aiohttp|selenium|playwright|socket|subprocess)\b",
        re.MULTILINE,
    )
    forbidden_shell_fetch = re.compile(r"\b(?:curl|wget)\b")
    assert not forbidden_import.search(text)
    assert not forbidden_shell_fetch.search(text)
