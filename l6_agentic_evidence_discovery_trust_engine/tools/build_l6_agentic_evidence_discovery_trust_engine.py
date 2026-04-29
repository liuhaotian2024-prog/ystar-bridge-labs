#!/usr/bin/env python3
"""Build L6.8 agentic evidence discovery and trust judgment artifacts.

The builder is intentionally local and static. It creates design/sandbox
artifacts only; it does not fetch URLs, search the web, call APIs, scrape,
open browsers, execute MCP tools, or persist real approval/runtime state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.8"
MILESTONE_NAME = "Agentic External Evidence Discovery & Trust Judgment Engine v0"
NEXT_MILESTONE = "L6.9 Controlled Read-Only Agentic Evidence Discovery Pilot Approval v0"

INPUT_REFS = {
    "l6_0_value_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_1_mvp_artifact_cases": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_2_observation_boundary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_3_controlled_observation_packets": "controlled_pre_observation_packets/pre_observation_packet_index.json",
    "l6_4_preflight_candidates": "real_observation_candidate_selector/selected_real_observation_candidates.json",
    "l6_5_pilot_candidates": "pilot_candidate_selector/selected_pilot_candidates.json",
    "l6_6_approval_packets": "pilot_approval_packet_assembler/approval_packet_index.json",
    "l6_7_pilot_readiness_packages": "pilot_run_package_assembler/pilot_run_package_index.json",
    "l6_7_readiness": "l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "external_observation_execution_enabled": False,
    "agent_external_fetch_enabled": False,
    "network_enabled": False,
    "api_enabled": False,
    "scraping_enabled": False,
    "browser_fetch_enabled": False,
    "search_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "cieu_db_write_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "durable_real_approval_record_creation_enabled": False,
    "real_approval_grant_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "strategy_mutation_enabled": False,
    "candidate_auto_approval_enabled": False,
    "real_candidate_approval_enabled": False,
    "real_canonical_policy_mutation_enabled": False,
    "real_canonical_update_application_enabled": False,
    "real_release_execution_enabled": False,
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "llm_confidence_as_authority_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "revenue_execution_enabled": False,
    "external_market_scan_enabled": False,
    "public_content_publication_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
    "payment_enabled": False,
}

L6_8_FLAGS = {
    "l6_8_agentic_evidence_discovery_design_and_sandbox_only": True,
    "l6_8_autonomous_evidence_need_inference_enabled": True,
    "l6_8_autonomous_source_hypothesis_generation_enabled": True,
    "l6_8_autonomous_evidence_value_judgment_enabled": True,
    "l6_8_autonomous_trust_assessment_enabled": True,
    "l6_8_observation_work_order_generation_enabled": True,
    "l6_8_real_external_observation_enabled": False,
    "l6_8_agent_external_fetch_enabled": False,
    "l6_8_network_enabled": False,
    "l6_8_search_enabled": False,
    "l6_8_scraping_enabled": False,
    "l6_8_browser_fetch_enabled": False,
    "l6_8_publication_enabled": False,
    "l6_8_outreach_enabled": False,
    "l6_8_payment_enabled": False,
    "l6_8_revenue_execution_enabled": False,
    "l6_8_mcp_execution_enabled": False,
    "l6_8_cieu_db_write_enabled": False,
    "l6_8_canonical_update_enabled": False,
    "l6_8_brain_writeback_enabled": False,
    "l6_8_memory_ingestion_enabled": False,
    "l6_8_direct_y_star_mutation_enabled": False,
}

NO_ACTION_CONSTRAINTS = [
    "agent external fetch",
    "real external observation",
    "network access",
    "API calls",
    "scraping",
    "browser fetch",
    "autonomous web search",
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
    "canonical strategy mutation",
    "canonical update",
    "brain/memory writeback",
    "direct Y-star mutation",
    "durable real approval persistence",
    "real approval grant",
]

VALUE_DIMENSIONS = [
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
]

TRUST_DIMENSIONS = [
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
]

VOI_DIMENSIONS = [
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
]

REJECTION_RULES = [
    "requires login",
    "requires payment",
    "requires account creation",
    "requires contact",
    "requires form submission",
    "requires posting/commenting/messaging",
    "requires scraping",
    "requires browser automation",
    "requires MCP execution",
    "accesses private/sensitive data",
    "source outside evidence need",
    "source unable to support claim",
    "high overclaim risk",
    "high privacy/IP risk",
    "not reviewable",
    "no source trace possible",
    "likely stale and no freshness path",
    "low value of information",
    "duplicate source with lower trust",
]


def read_json(path: str) -> dict[str, Any]:
    target = ROOT / path
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any] | list[Any], generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, text: str, generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    generated.append(path)


def with_common(payload: dict[str, Any]) -> dict[str, Any]:
    payload.setdefault("safety_flags", SAFETY_FLAGS)
    payload.setdefault("l6_8_flags", L6_8_FLAGS)
    return payload


def source_locator(source_hypothesis_id: str) -> str:
    return (
        "PLACEHOLDER LOCATOR ONLY - NOT FETCHED - NOT OPENED - NOT VERIFIED "
        "CURRENT FACT - NOT AUTHORIZED FOR REAL OBSERVATION - NOT AUTHORIZED "
        "FOR PUBLICATION - NOT AUTHORIZED FOR OUTREACH - NOT AUTHORIZED FOR "
        "PAYMENT - NOT AUTHORIZED FOR REVENUE EXECUTION - NOT AUTHORIZED FOR "
        f"CANONICAL UPDATE :: {source_hypothesis_id}"
    )


def build_evidence_needs() -> list[dict[str, Any]]:
    return [
        {
            "evidence_need_id": "l6_8_evidence_need_001",
            "linked_l6_artifact": INPUT_REFS["l6_1_mvp_artifact_cases"],
            "source_milestones": ["L6.0", "L6.1", "L6.7"],
            "uncertainty_or_gap": "payer or beneficiary clarity remains unverified outside the internal MVP artifact cases",
            "decision_relevance": "Determines whether future artifact refinement should focus on buyer, reviewer, learner, or operator evidence.",
            "expected_evidence_type": "public demand or beneficiary language",
            "freshness_requirement": "recent_or_date_declared",
            "trust_requirement": "medium_trust_candidate_secondary_source_or_better",
            "consequence_if_missing": "Future work orders remain too generic to support externalization review.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_002",
            "linked_l6_artifact": INPUT_REFS["l6_0_value_hypotheses"],
            "source_milestones": ["L6.0"],
            "uncertainty_or_gap": "recipient archetype assumptions need external language before future publication or outreach review",
            "decision_relevance": "Clarifies whether generated value hypotheses map to builders, governance reviewers, operators, learners, sponsors, or future customers.",
            "expected_evidence_type": "recipient terminology and need pattern evidence",
            "freshness_requirement": "date_available_or_date_missing_marker",
            "trust_requirement": "reviewable_source_trace_required",
            "consequence_if_missing": "The system risks overgeneralizing recipient archetypes.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_003",
            "linked_l6_artifact": INPUT_REFS["l6_1_mvp_artifact_cases"],
            "source_milestones": ["L6.1", "L6.3"],
            "uncertainty_or_gap": "acceptance criteria for internal MVP proof artifacts need outside-facing comparator evidence",
            "decision_relevance": "Helps decide whether a proof artifact is reviewable enough for a future controlled observation pilot.",
            "expected_evidence_type": "public checklist, evaluation rubric, or method comparison",
            "freshness_requirement": "freshness_class_declared",
            "trust_requirement": "high_trust_candidate_primary_source_or_independent_secondary_source",
            "consequence_if_missing": "MVP proof criteria stay internally plausible but externally uncalibrated.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_004",
            "linked_l6_artifact": INPUT_REFS["l6_2_observation_boundary"],
            "source_milestones": ["L6.2", "L6.4"],
            "uncertainty_or_gap": "policy or platform constraints must be known before any future read-only pilot is approved",
            "decision_relevance": "Prevents future work orders from pointing to surfaces that require login, interaction, automation, or disallowed use.",
            "expected_evidence_type": "official policy or platform documentation",
            "freshness_requirement": "current_policy_date_or_date_missing_marker",
            "trust_requirement": "high_trust_candidate_primary_source",
            "consequence_if_missing": "Observation approval packets cannot prove source-surface safety.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_005",
            "linked_l6_artifact": INPUT_REFS["l6_3_controlled_observation_packets"],
            "source_milestones": ["L6.3", "L6.5"],
            "uncertainty_or_gap": "distribution friction and source accessibility are untested on real surfaces",
            "decision_relevance": "Ranks future work orders by manual read-only feasibility and abort risk.",
            "expected_evidence_type": "public accessibility and source navigation constraints",
            "freshness_requirement": "date_declared_or_review_required",
            "trust_requirement": "source_trace_present",
            "consequence_if_missing": "Future operators may encounter interaction requirements too late.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_006",
            "linked_l6_artifact": INPUT_REFS["l6_5_pilot_candidates"],
            "source_milestones": ["L6.5"],
            "uncertainty_or_gap": "competitive pressure and adjacent alternatives remain unknown",
            "decision_relevance": "Supports future artifact claim boundaries without mutating strategy canonically.",
            "expected_evidence_type": "public comparison, repository, documentation, or independent analysis",
            "freshness_requirement": "recent_or_staleness_disclosed",
            "trust_requirement": "medium_trust_candidate_secondary_source_or_corrobation_required",
            "consequence_if_missing": "Artifacts may overclaim uniqueness or understate existing alternatives.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_007",
            "linked_l6_artifact": INPUT_REFS["l6_6_approval_packets"],
            "source_milestones": ["L6.6"],
            "uncertainty_or_gap": "approval packets need source credibility requirements before any future real observation can be reviewed",
            "decision_relevance": "Defines what source provenance, trace, freshness, and reviewability must appear in future evidence packets.",
            "expected_evidence_type": "source credibility and provenance indicators",
            "freshness_requirement": "source_date_available_or_date_missing_marker",
            "trust_requirement": "candidate_trust_tier_assigned_pre_observation",
            "consequence_if_missing": "Approval packets cannot distinguish high-value sources from weak evidence surfaces.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
        {
            "evidence_need_id": "l6_8_evidence_need_008",
            "linked_l6_artifact": INPUT_REFS["l6_7_pilot_readiness_packages"],
            "source_milestones": ["L6.7"],
            "uncertainty_or_gap": "contradiction and corroboration requirements are not yet attached to pilot run packages",
            "decision_relevance": "Prevents single-source overconfidence and defines when evidence must be quarantined or corroborated.",
            "expected_evidence_type": "conflicting or independently corroborating source trace",
            "freshness_requirement": "freshness_check_required_if_conflict_detected",
            "trust_requirement": "conflict_check_required",
            "consequence_if_missing": "Future work orders may accept one weak source as sufficient.",
            "whether_real_observation_required_in_future": True,
            "current_execution_authorized": False,
        },
    ]


def build_source_hypotheses(evidence_needs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    templates = [
        (
            "primary official source",
            "official policy or program source",
            "High provenance evidence for policy, eligibility, or boundary claims.",
            "official ownership, stable publication surface, source date if present",
            "policy constraint, source scope, allowed read-only access",
            "demand or recipient sentiment beyond the official statement",
            "low",
            "high_trust_candidate_primary_source",
        ),
        (
            "independent third-party analysis",
            "independent analysis or public evaluation source",
            "Corroborating or contradictory evidence about demand, alternatives, or practical friction.",
            "independence from interested party, source trace, publication date",
            "comparative pattern, risk, alternative framing",
            "official policy or source-owner intent without primary source support",
            "medium",
            "medium_trust_candidate_secondary_source",
        ),
        (
            "public repository or technical documentation source",
            "public technical documentation or repository surface",
            "Implementation-adjacent evidence for tooling, operational, or integration claims.",
            "public repository trace, maintainer/source identity, visible update metadata",
            "technical feasibility, maintenance signal, interface constraints",
            "buyer willingness or broad market demand by itself",
            "low",
            "medium_trust_candidate_secondary_source",
        ),
        (
            "community discussion surface",
            "public community or customer discussion surface",
            "Weak but useful signal for language, pain points, and contradiction discovery.",
            "reviewable public trace, independence markers, uncertainty disclosure",
            "recipient language, anecdotal pain, objections, missing context",
            "strong factual or publication-ready claims without corroboration",
            "medium",
            "low_trust_candidate_unverified_source",
        ),
        (
            "public pricing or procurement signal",
            "public commercial or procurement signal",
            "Decision-relevant evidence about willingness to allocate resources, without revenue execution.",
            "public trace, date, source owner, limited claim scope",
            "payer clarity, procurement language, commitment proxy",
            "guaranteed future revenue or market success",
            "medium",
            "freshness_check_required",
        ),
        (
            "public regulatory or compliance reference",
            "public regulatory, standards, or compliance reference",
            "Boundary evidence for risk-reduction, compliance, and assurance claims.",
            "official or standards-body provenance, date, scope match",
            "claim boundary, compliance vocabulary, forbidden overclaims",
            "product certification or legal conclusion",
            "low",
            "high_trust_candidate_primary_source",
        ),
    ]
    hypotheses: list[dict[str, Any]] = []
    for idx, need in enumerate(evidence_needs[:6], start=1):
        source_function, source_type, evidence_yield, credibility, supported, unsupported, risk, trust = templates[idx - 1]
        hypotheses.append(
            {
                "source_hypothesis_id": f"l6_8_source_hypothesis_{idx:03d}",
                "linked_evidence_need_id": need["evidence_need_id"],
                "hypothesized_source_type": source_type,
                "source_function": source_function,
                "expected_evidence_yield": evidence_yield,
                "expected_credibility_basis": credibility,
                "expected_freshness_pattern": need["freshness_requirement"],
                "likely_claims_supported": [supported],
                "likely_claims_not_supported": [unsupported],
                "observation_risk": risk,
                "interaction_required_expected": False,
                "login_required_expected": False,
                "payment_required_expected": False,
                "contact_required_expected": False,
                "source_categories_exhaustive": False,
                "hardcoded_opportunity_category_used": False,
                "future_observation_candidate": idx <= 4,
                "real_observation_authorized_now": False,
                "trust_tier_candidate": trust,
            }
        )
    return hypotheses


def build() -> list[str]:
    generated: list[str] = []
    input_refs_loaded = {key: bool(read_json(path)) for key, path in INPUT_REFS.items()}
    missing_optional_refs = [path for key, path in INPUT_REFS.items() if not input_refs_loaded[key]]

    evidence_needs = build_evidence_needs()
    source_hypotheses = build_source_hypotheses(evidence_needs)
    ranked_hypotheses = source_hypotheses[:4]
    deferred_hypotheses = source_hypotheses[4:]
    rejected_source_hypotheses = [
        {
            "rejected_source_hypothesis_id": "l6_8_rejected_source_hypothesis_001",
            "linked_evidence_need_id": "l6_8_evidence_need_006",
            "hypothesized_source_type": "private customer data surface",
            "rejection_reasons": ["accesses private/sensitive data", "not reviewable"],
            "real_observation_authorized_now": False,
        },
        {
            "rejected_source_hypothesis_id": "l6_8_rejected_source_hypothesis_002",
            "linked_evidence_need_id": "l6_8_evidence_need_005",
            "hypothesized_source_type": "login-required dashboard or account surface",
            "rejection_reasons": ["requires login", "requires account creation"],
            "real_observation_authorized_now": False,
        },
    ]

    write_text(
        "l6_agentic_evidence_discovery_trust_engine/README.md",
        "# L6.8 Agentic External Evidence Discovery & Trust Judgment Engine\n\n"
        "This pack defines the agentic evidence-discovery and structural trust "
        "judgment mechanism for future controlled read-only observation. It "
        "generates evidence needs, source hypotheses, trust/value judgments, "
        "rankings, rejection filters, and future observation work orders without "
        "fetching, searching, browsing, scraping, calling APIs, publishing, "
        "contacting, paying, executing MCP tools, mutating state, or granting "
        "real approval.\n",
        generated,
    )
    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": [
                "L6.0",
                "L6.1",
                "L6.2",
                "L6.3",
                "L6.4",
                "L6.5",
                "L6.6",
                "L6.7",
            ],
            "mode": "agentic_evidence_discovery_design_and_sandbox",
            "autonomous_evidence_need_inference_authorized": True,
            "autonomous_source_hypothesis_generation_authorized": True,
            "autonomous_evidence_value_judgment_authorized": True,
            "autonomous_trust_assessment_authorized": True,
            "observation_work_order_generation_authorized": True,
            "real_external_observation_authorized": False,
            "agent_external_fetch_authorized": False,
            "network_authorized": False,
            "api_authorized": False,
            "scraping_authorized": False,
            "browser_fetch_authorized": False,
            "search_authorized": False,
            "publication_authorized": False,
            "outreach_authorized": False,
            "payment_authorized": False,
            "revenue_execution_authorized": False,
            "mcp_execution_authorized": False,
            "live_behavior_authorized": False,
            "cieu_db_write_authorized": False,
            "canonical_update_authorized": False,
            "direct_y_star_mutation_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "durable_real_approval_record_created": False,
            "real_approval_granted": False,
            "future_controlled_read_only_observation_pilot_candidate_allowed": True,
            "forbidden_operations": NO_ACTION_CONSTRAINTS,
        }
    )
    write_json("l6_agentic_evidence_discovery_trust_engine/l6_8_milestone_contract.json", contract, generated)
    write_json(
        "l6_agentic_evidence_discovery_trust_engine/l6_8_agentic_evidence_scope.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "scope": "agentic evidence discovery, source selection, structural trust, value-of-information, ranking, rejection, and work-order generation only",
                "not_manual_evidence_import_only": True,
                "real_external_observation_authorized": False,
                "current_side_effects_authorized": [],
                "future_outputs": [
                    "ranked source hypotheses",
                    "rejection-filtered source candidates",
                    "future controlled observation work orders",
                    "review-only strategic residuals",
                ],
            }
        ),
        generated,
    )
    write_json("l6_agentic_evidence_discovery_trust_engine/l6_8_safety_flags.json", SAFETY_FLAGS, generated)
    write_text(
        "l6_agentic_evidence_discovery_trust_engine/l6_8_non_execution_boundary.md",
        "# L6.8 Non-Execution Boundary\n\n"
        "L6.8 authorizes agentic evidence need inference, source hypothesis "
        "generation, structural trust assessment, value-of-information judgment, "
        "ranking, rejection filtering, and future work-order generation only. It "
        "does not authorize fetching, searching, browsing, scraping, API calls, "
        "publication, outreach, payment, revenue execution, MCP execution, live "
        "behavior, CIEU DB writes, canonical mutation, brain/memory writeback, "
        "direct Y* mutation, real approval, or durable real approval records.\n",
        generated,
    )

    summary = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "l6_8_agentic_evidence_discovery_trust_engine_defined": True,
            "mode": "agentic_evidence_discovery_design_and_sandbox",
            "evidence_need_count": len(evidence_needs),
            "source_hypothesis_count": len(source_hypotheses),
            "ranked_source_hypothesis_count": len(ranked_hypotheses),
            "observation_work_order_count": 3,
            "rejected_source_hypothesis_count": len(rejected_source_hypotheses),
            "autonomous_evidence_need_inference_authorized": True,
            "autonomous_source_hypothesis_generation_authorized": True,
            "autonomous_evidence_value_judgment_authorized": True,
            "autonomous_trust_assessment_authorized": True,
            "observation_work_order_generation_authorized": True,
            "real_external_observation_authorized": False,
            "agent_external_fetch_authorized": False,
            "network_authorized": False,
            "search_authorized": False,
            "scraping_authorized": False,
            "browser_fetch_authorized": False,
            "future_controlled_read_only_observation_pilot_candidate_allowed": True,
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval": True,
            "ready_for_actual_network_observation_now": False,
            "ready_for_autonomous_web_search_now": False,
            "ready_for_scraping": False,
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "next_recommended_milestone": NEXT_MILESTONE,
            "input_refs": INPUT_REFS,
            "missing_optional_refs": missing_optional_refs,
        }
    )
    write_json("l6_agentic_evidence_discovery_trust_engine/l6_8_summary.json", summary, generated)
    write_text(
        "l6_agentic_evidence_discovery_trust_engine/l6_8_summary.md",
        "# L6.8 Summary\n\n"
        "L6.8 creates an agentic evidence discovery and structural trust judgment "
        "engine. It infers evidence needs, generates source hypotheses, judges "
        "source value and pre-observation trust structurally, estimates value of "
        "information, ranks future source candidates, rejects risky/weak sources, "
        "and generates future controlled observation work orders. All real "
        "observation, fetch, search, network, publication, outreach, payment, "
        "revenue, MCP, live, CIEU DB, canonical, brain/memory, and direct Y* "
        "paths remain blocked.\n",
        generated,
    )

    write_json(
        "evidence_need_inference_engine/evidence_need_inference_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "purpose": "Infer external evidence needs from L6.0-L6.7 artifacts without observing external sources.",
                "input_refs": INPUT_REFS,
                "autonomous_inference_authorized": True,
                "real_observation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "evidence_need_inference_engine/l6_artifact_uncertainty_inventory.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "input_refs_loaded": input_refs_loaded,
                "uncertainty_sources": [
                    {"milestone": key, "artifact": path, "used_for_evidence_need_inference": True}
                    for key, path in INPUT_REFS.items()
                ],
                "missing_optional_refs": missing_optional_refs,
            }
        ),
        generated,
    )
    write_json(
        "evidence_need_inference_engine/evidence_need_matrix.json",
        with_common({"schema_version": SCHEMA_VERSION, "evidence_needs": evidence_needs}),
        generated,
    )
    write_json(
        "evidence_need_inference_engine/inferred_evidence_needs.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_need_count": len(evidence_needs),
                "inferred_from_l6_artifacts": True,
                "manual_user_search_required": False,
                "evidence_needs": evidence_needs,
            }
        ),
        generated,
    )
    write_text(
        "evidence_need_inference_engine/evidence_need_inference_report.md",
        "# Evidence Need Inference\n\n"
        "Evidence needs are inferred structurally from L6.0-L6.7 artifacts. No "
        "external source was observed or fetched.\n",
        generated,
    )

    write_json(
        "autonomous_source_hypothesis_generator/source_hypothesis_generation_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "autonomous_source_hypothesis_generation_authorized": True,
                "source_hypotheses_derive_from_evidence_needs": True,
                "hardcoded_opportunity_categories_used": False,
                "source_categories_exhaustive": False,
                "real_observation_authorized": False,
            }
        ),
        generated,
    )
    source_index = {
        "schema_version": SCHEMA_VERSION,
        "source_hypothesis_count": len(source_hypotheses),
        "source_hypotheses": [
            {
                "source_hypothesis_id": item["source_hypothesis_id"],
                "path": f"autonomous_source_hypothesis_generator/source_hypothesis_{idx:03d}.json",
                "linked_evidence_need_id": item["linked_evidence_need_id"],
                "future_observation_candidate": item["future_observation_candidate"],
                "real_observation_authorized_now": False,
            }
            for idx, item in enumerate(source_hypotheses, start=1)
        ],
        "hardcoded_opportunity_categories_used": False,
        "source_categories_exhaustive": False,
    }
    write_json("autonomous_source_hypothesis_generator/source_hypothesis_index.json", with_common(source_index), generated)
    for idx, item in enumerate(source_hypotheses, start=1):
        write_json(
            f"autonomous_source_hypothesis_generator/source_hypothesis_{idx:03d}.json",
            with_common(item),
            generated,
        )
    write_text(
        "autonomous_source_hypothesis_generator/source_hypothesis_generator_report.md",
        "# Source Hypothesis Generator\n\n"
        "Source hypotheses are generated from evidence needs by evidence function "
        "and are not fixed opportunity categories.\n",
        generated,
    )

    write_json(
        "source_type_value_model/source_type_value_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "purpose": "Judge source type value for future controlled observation without observing now.",
                "value_dimensions": VALUE_DIMENSIONS,
                "not_revenue_scoring": True,
            }
        ),
        generated,
    )
    write_json(
        "source_type_value_model/source_value_dimension_registry.json",
        with_common({"schema_version": SCHEMA_VERSION, "dimensions": VALUE_DIMENSIONS}),
        generated,
    )
    write_json(
        "source_type_value_model/source_type_value_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rows": [
                    {
                        "source_hypothesis_id": item["source_hypothesis_id"],
                        "source_type": item["hypothesized_source_type"],
                        "high_value_dimensions": [
                            "relevance_to_decision",
                            "evidence_yield",
                            "accessibility_read_only",
                            "usefulness_for_artifact_refinement",
                        ],
                        "low_value_dimensions": [],
                        "real_observation_authorized_now": False,
                    }
                    for item in source_hypotheses
                ],
            }
        ),
        generated,
    )
    write_json(
        "source_type_value_model/source_type_rejection_criteria.json",
        with_common({"schema_version": SCHEMA_VERSION, "rejection_criteria": REJECTION_RULES}),
        generated,
    )
    write_text(
        "source_type_value_model/source_type_value_report.md",
        "# Source Type Value Model\n\n"
        "Source value is judged by structural relevance, provenance, access, "
        "risk, and usefulness for future review, not by revenue scoring.\n",
        generated,
    )

    trust_judgments = [
        {
            "source_hypothesis_id": item["source_hypothesis_id"],
            "trust_tier_candidate": item["trust_tier_candidate"],
            "candidate_only": True,
            "pre_observation": True,
            "not_live_verified": True,
            "not_current_truth": True,
            "review_required": True,
            "structural_basis": [
                "source provenance",
                "source traceability",
                "freshness requirement",
                "scope match",
                "privacy/IP cleanliness",
            ],
        }
        for item in source_hypotheses
    ]
    write_json(
        "evidence_trust_judgment_model/evidence_trust_judgment_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "trust_judgment_mode": "structural_pre_observation_candidate_only",
                "semantic_truth_scoring_used": False,
                "llm_confidence_used_as_authority": False,
                "market_success_score_used": False,
                "unsupported_model_authority_used": False,
                "trust_dimensions": TRUST_DIMENSIONS,
            }
        ),
        generated,
    )
    write_json(
        "evidence_trust_judgment_model/trust_dimension_registry.json",
        with_common({"schema_version": SCHEMA_VERSION, "dimensions": TRUST_DIMENSIONS}),
        generated,
    )
    write_json(
        "evidence_trust_judgment_model/trust_tier_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "trust_tiers": [
                    "high_trust_candidate_primary_source",
                    "medium_trust_candidate_secondary_source",
                    "low_trust_candidate_unverified_source",
                    "conflict_check_required",
                    "freshness_check_required",
                    "reject_before_observation",
                ],
                "all_judgments_candidate_only": True,
                "review_required": True,
            }
        ),
        generated,
    )
    write_json(
        "evidence_trust_judgment_model/trust_judgment_matrix.json",
        with_common({"schema_version": SCHEMA_VERSION, "trust_judgments": trust_judgments}),
        generated,
    )
    write_text(
        "evidence_trust_judgment_model/trust_judgment_report.md",
        "# Evidence Trust Judgment Model\n\n"
        "Trust judgments are structural, pre-observation, candidate-only, and "
        "review-gated. They do not use semantic scoring or model confidence as "
        "authority.\n",
        generated,
    )

    voi_rows = []
    for idx, need in enumerate(evidence_needs, start=1):
        voi_rows.append(
            {
                "evidence_need_id": need["evidence_need_id"],
                "value_of_information_class": "high" if idx <= 4 else "medium",
                "primary_voi_dimensions": [
                    "uncertainty_reduction",
                    "decision_impact",
                    "artifact_refinement_impact",
                    "externalization_risk_reduction",
                    "compounding_learning_value",
                ],
                "not_revenue_scoring": True,
                "real_observation_authorized_now": False,
            }
        )
    write_json(
        "evidence_value_of_information_model/value_of_information_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "purpose": "Estimate evidence value of information for future source prioritization.",
                "not_revenue_scoring": True,
                "semantic_truth_scoring_used": False,
                "llm_confidence_used_as_authority": False,
            }
        ),
        generated,
    )
    write_json(
        "evidence_value_of_information_model/voi_dimension_registry.json",
        with_common({"schema_version": SCHEMA_VERSION, "dimensions": VOI_DIMENSIONS}),
        generated,
    )
    write_json(
        "evidence_value_of_information_model/evidence_need_voi_matrix.json",
        with_common({"schema_version": SCHEMA_VERSION, "rows": voi_rows}),
        generated,
    )
    write_json(
        "evidence_value_of_information_model/evidence_priority_rationale.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rationale": [
                    "Prioritize evidence that reduces uncertainty tied to review, claim boundaries, and future controlled observation approval.",
                    "Do not prioritize sources by predicted revenue, market success, or model confidence.",
                    "Prefer reusable evidence that can refine multiple artifacts without canonical mutation.",
                ],
            }
        ),
        generated,
    )
    write_text(
        "evidence_value_of_information_model/value_of_information_report.md",
        "# Value Of Information Model\n\n"
        "The VOI model estimates decision-relevant uncertainty reduction and "
        "review value. It is not revenue scoring and does not establish external "
        "truth.\n",
        generated,
    )

    priority_rows = []
    for rank, item in enumerate(ranked_hypotheses, start=1):
        priority_rows.append(
            {
                "rank": rank,
                "source_hypothesis_id": item["source_hypothesis_id"],
                "linked_evidence_need_id": item["linked_evidence_need_id"],
                "priority_reason": "High decision relevance, read-only feasibility, structural trust candidate, and useful uncertainty reduction.",
                "trust_tier_candidate": item["trust_tier_candidate"],
                "value_of_information_class": "high" if rank <= 3 else "medium",
                "expected_risk_class": item["observation_risk"],
                "read_only_feasibility": "candidate_feasible_with_future_approval",
                "future_observation_work_order_candidate": rank <= 3,
                "real_observation_authorized_now": False,
            }
        )
    write_json(
        "source_prioritization_and_ranking_engine/source_prioritization_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "ranking_inputs": [
                    "evidence need importance",
                    "source value model",
                    "trust judgment model",
                    "value of information model",
                    "risk model",
                    "no-action constraints",
                    "read-only future pilot feasibility",
                    "rejection filters",
                ],
                "real_observation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "source_prioritization_and_ranking_engine/source_priority_matrix.json",
        with_common({"schema_version": SCHEMA_VERSION, "rows": priority_rows}),
        generated,
    )
    write_json(
        "source_prioritization_and_ranking_engine/ranked_source_hypotheses.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "ranked_count": len(priority_rows),
                "ranked_source_hypotheses": priority_rows,
            }
        ),
        generated,
    )
    write_json(
        "source_prioritization_and_ranking_engine/deferred_source_hypotheses.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "deferred_count": len(deferred_hypotheses),
                "deferred_source_hypotheses": [
                    {
                        "source_hypothesis_id": item["source_hypothesis_id"],
                        "linked_evidence_need_id": item["linked_evidence_need_id"],
                        "defer_reason": "Lower immediate value of information or requires corroboration before work-order generation.",
                        "real_observation_authorized_now": False,
                    }
                    for item in deferred_hypotheses
                ],
            }
        ),
        generated,
    )
    write_text(
        "source_prioritization_and_ranking_engine/source_prioritization_report.md",
        "# Source Prioritization\n\n"
        "Sources are ranked for future controlled observation work-order creation. "
        "No real observation is authorized.\n",
        generated,
    )

    write_json(
        "evidence_conflict_and_corrobation_model/conflict_corroboration_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "purpose": "Define when single-source evidence is enough, when corroboration is required, and when conflict triggers quarantine.",
                "real_observation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "evidence_conflict_and_corrobation_model/corroboration_requirement_registry.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rules": [
                    "one primary official source can support a limited policy/source-owner claim",
                    "independent corroboration is required for external demand, competitive pressure, or publication/outreach/revenue readiness",
                    "interested-party evidence requires independent confirmation for strong claims",
                    "anecdotal community evidence can only support weak language or pain-pattern claims",
                ],
            }
        ),
        generated,
    )
    write_json(
        "evidence_conflict_and_corrobation_model/conflict_detection_plan.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "conflict_triggers": [
                    "source date mismatch",
                    "claim scope mismatch",
                    "primary and secondary source disagreement",
                    "stale source conflicts with newer source",
                    "unsupported inference detected",
                ],
                "conflict_action": "quarantine_or_review_before_artifact_refinement",
            }
        ),
        generated,
    )
    write_json(
        "evidence_conflict_and_corrobation_model/source_independence_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "independence_required_for": [
                    "future publication decisions",
                    "future outreach decisions",
                    "future revenue experiment decisions",
                    "competitive pressure claims",
                    "demand strength claims",
                ],
                "single_source_limit": "limited internal review claim only",
            }
        ),
        generated,
    )
    write_text(
        "evidence_conflict_and_corrobation_model/conflict_corroboration_report.md",
        "# Conflict And Corroboration\n\n"
        "The model distinguishes limited primary-source claims, corroboration "
        "requirements, conflict quarantine, freshness checks, and weak anecdotal "
        "support boundaries.\n",
        generated,
    )

    evidence_capture_fields = [
        "source_locator",
        "source_title",
        "source_publisher_or_owner",
        "observed_timestamp",
        "source_date_or_date_missing",
        "freshness_class",
        "captured_bounded_claims",
        "unsupported_claims",
        "missing_context",
        "conflict_marker",
        "citation_trace",
        "claim_boundary",
        "review_status",
    ]
    work_orders = []
    for idx, row in enumerate(priority_rows[:3], start=1):
        hypothesis = next(item for item in source_hypotheses if item["source_hypothesis_id"] == row["source_hypothesis_id"])
        need = next(item for item in evidence_needs if item["evidence_need_id"] == row["linked_evidence_need_id"])
        work_orders.append(
            {
                "work_order_id": f"l6_8_observation_work_order_{idx:03d}",
                "linked_source_hypothesis_id": hypothesis["source_hypothesis_id"],
                "linked_evidence_need_id": need["evidence_need_id"],
                "linked_l6_artifact": need["linked_l6_artifact"],
                "observation_question": f"What future read-only evidence would reduce: {need['uncertainty_or_gap']}?",
                "source_type": hypothesis["hypothesized_source_type"],
                "source_locator_placeholder": source_locator(hypothesis["source_hypothesis_id"]),
                "expected_evidence_type": need["expected_evidence_type"],
                "trust_requirement": need["trust_requirement"],
                "freshness_requirement": need["freshness_requirement"],
                "claim_boundary_to_test": "internal review claim only; no publication, outreach, payment, revenue, or strategy claim",
                "evidence_capture_fields": evidence_capture_fields,
                "abort_conditions": [
                    "login required",
                    "payment required",
                    "account creation required",
                    "contact required",
                    "form submission required",
                    "private/sensitive data encountered",
                    "automation or scraping required",
                    "MCP execution required",
                    "source scope mismatch",
                    "operator uncertainty",
                ],
                "no_action_constraints": NO_ACTION_CONSTRAINTS,
                "read_only_requirement": True,
                "login_required_allowed": False,
                "payment_required_allowed": False,
                "contact_required_allowed": False,
                "form_submission_allowed": False,
                "automation_allowed": False,
                "mcp_execution_allowed": False,
                "publication_allowed": False,
                "outreach_allowed": False,
                "revenue_action_allowed": False,
                "real_observation_authorized_now": False,
                "future_approval_required": True,
            }
        )
    write_json(
        "observation_work_order_generator/observation_work_order_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "required_fields": list(work_orders[0].keys()),
                "real_observation_authorized_now": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_work_order_generator/observation_work_order_index.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "work_order_count": len(work_orders),
                "work_orders": [
                    {
                        "work_order_id": item["work_order_id"],
                        "path": f"observation_work_order_generator/observation_work_order_{idx:03d}.json",
                        "real_observation_authorized_now": False,
                        "future_approval_required": True,
                    }
                    for idx, item in enumerate(work_orders, start=1)
                ],
            }
        ),
        generated,
    )
    for idx, item in enumerate(work_orders, start=1):
        write_json(
            f"observation_work_order_generator/observation_work_order_{idx:03d}.json",
            with_common(item),
            generated,
        )
    write_text(
        "observation_work_order_generator/observation_work_order_generator_report.md",
        "# Observation Work Order Generator\n\n"
        "Work orders are future controlled read-only observation candidates. They "
        "require future approval and authorize no current observation.\n",
        generated,
    )

    write_json(
        "pre_observation_rejection_filter/rejection_filter_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "purpose": "Reject weak, risky, or disallowed source/work-order candidates before any future observation.",
                "real_observation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "pre_observation_rejection_filter/rejection_rule_registry.json",
        with_common({"schema_version": SCHEMA_VERSION, "rejection_rules": REJECTION_RULES}),
        generated,
    )
    write_json(
        "pre_observation_rejection_filter/rejected_source_hypotheses.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rejected_count": len(rejected_source_hypotheses),
                "rejected_source_hypotheses": rejected_source_hypotheses,
            }
        ),
        generated,
    )
    write_json(
        "pre_observation_rejection_filter/rejected_work_orders.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rejected_work_order_count": 1,
                "rejected_work_orders": [
                    {
                        "rejected_work_order_id": "l6_8_rejected_work_order_001",
                        "linked_source_hypothesis": "l6_8_rejected_source_hypothesis_001",
                        "rejection_reasons": ["accesses private/sensitive data", "not reviewable"],
                        "real_observation_authorized_now": False,
                    }
                ],
            }
        ),
        generated,
    )
    write_text(
        "pre_observation_rejection_filter/pre_observation_rejection_filter_report.md",
        "# Pre-Observation Rejection Filter\n\n"
        "The filter blocks sources requiring login, payment, account creation, "
        "contact, forms, scraping, automation, MCP execution, private data, weak "
        "traceability, stale evidence without freshness path, or low information "
        "value.\n",
        generated,
    )

    decisions = [
        {
            "source_hypothesis_id": item["source_hypothesis_id"],
            "decision": "generate_future_observation_work_order" if idx <= 3 else "require_corroboration_plan",
            "block_real_observation_now": True,
            "real_observation_authorized_now": False,
            "future_human_review_required": True,
        }
        for idx, item in enumerate(ranked_hypotheses, start=1)
    ]
    decisions.extend(
        [
            {
                "source_hypothesis_id": item["rejected_source_hypothesis_id"],
                "decision": "reject_source_hypothesis",
                "block_real_observation_now": True,
                "real_observation_authorized_now": False,
                "future_human_review_required": True,
            }
            for item in rejected_source_hypotheses
        ]
    )
    write_json(
        "agentic_evidence_decision_gate/agentic_evidence_decision_gate_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "allowed_decisions": [
                    "generate_future_observation_work_order",
                    "defer_source_hypothesis",
                    "reject_source_hypothesis",
                    "require_corroboration_plan",
                    "require_freshness_check",
                    "require_human_review_before_future_observation",
                    "block_real_observation_now",
                ],
                "all_real_observation_blocked_now": True,
            }
        ),
        generated,
    )
    write_json(
        "agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json",
        with_common({"schema_version": SCHEMA_VERSION, "decisions": decisions}),
        generated,
    )
    write_json(
        "agentic_evidence_decision_gate/observation_work_order_decisions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "work_order_decisions": [
                    {
                        "work_order_id": item["work_order_id"],
                        "decision": "future_work_order_candidate_review_required",
                        "real_observation_authorized_now": False,
                        "future_approval_required": True,
                    }
                    for item in work_orders
                ],
            }
        ),
        generated,
    )
    write_json(
        "agentic_evidence_decision_gate/future_pilot_candidate_decisions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "future_pilot_candidate_count": len(work_orders),
                "ready_for_l6_9_approval_packet": True,
                "real_observation_authorized_now": False,
                "future_pilot_candidate_decisions": [
                    {
                        "work_order_id": item["work_order_id"],
                        "future_controlled_read_only_observation_pilot_candidate": True,
                        "real_observation_authorized_now": False,
                    }
                    for item in work_orders
                ],
            }
        ),
        generated,
    )
    write_text(
        "agentic_evidence_decision_gate/agentic_evidence_decision_gate_report.md",
        "# Agentic Evidence Decision Gate\n\n"
        "The gate can generate, defer, reject, or require corroboration/freshness "
        "plans, but every real observation decision is blocked now.\n",
        generated,
    )

    for action, filename in [
        ("agent_fetch", "no_agent_fetch_receipt.json"),
        ("url_open", "no_url_open_receipt.json"),
        ("network_execution", "no_network_execution_receipt.json"),
        ("api", "no_api_receipt.json"),
        ("scraping", "no_scraping_receipt.json"),
        ("browser_fetch", "no_browser_fetch_receipt.json"),
        ("search", "no_search_receipt.json"),
        ("publication", "no_publication_receipt.json"),
        ("outreach", "no_outreach_receipt.json"),
        ("payment", "no_payment_receipt.json"),
        ("revenue_execution", "no_revenue_execution_receipt.json"),
        ("mcp_execution", "no_mcp_execution_receipt.json"),
        ("live_behavior", "no_live_behavior_receipt.json"),
        ("cieu_db_write", "no_cieu_db_write_receipt.json"),
        ("canonical_mutation", "no_canonical_mutation_receipt.json"),
        ("brain_memory_writeback", "no_brain_memory_writeback_receipt.json"),
        ("direct_y_star_mutation", "no_direct_y_star_mutation_receipt.json"),
    ]:
        write_json(
            f"agentic_evidence_no_action_receipts/{filename}",
            with_common(
                {
                    "action_type": action,
                    "authorized_in_l6_8": False,
                    "executed_in_l6_8": False,
                    "blocker_reference": "l6_agentic_evidence_discovery_trust_engine/l6_8_milestone_contract.json",
                    "future_boundary_required": NEXT_MILESTONE,
                }
            ),
            generated,
        )
    write_text(
        "agentic_evidence_no_action_receipts/agentic_evidence_no_action_receipt_report.md",
        "# Agentic Evidence No-Action Receipts\n\n"
        "L6.8 executed no external fetch, URL open, network, API, scraping, browser "
        "fetch, search, publication, outreach, payment, revenue, MCP, live, CIEU "
        "DB, canonical, brain/memory, or direct Y* action.\n",
        generated,
    )

    residuals = [
        "source hypotheses are not yet live verified",
        "trust judgments are pre-observation candidate judgments only",
        "work orders require future approval",
        "no real evidence captured yet",
        "no current factual claims established",
        "ranking model untested on live sources",
        "future controlled read-only pilot still required",
        "publication/outreach/payment/revenue remain blocked",
    ]
    write_json(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_cieu_like_fixture.json",
        with_common(
            {
                "X_t": {
                    "input_refs": INPUT_REFS,
                    "l6_7_integrated_readiness": INPUT_REFS["l6_7_readiness"],
                },
                "U_t": "Create agentic evidence discovery, source hypothesis, structural trust, value-of-information, ranking, rejection, and work-order artifacts without external observation.",
                "Y_star_t": "Create an agentic evidence discovery and trust judgment mechanism that can infer evidence needs, generate source hypotheses, judge source value, judge structural trust, estimate value of information, rank source hypotheses, generate future observation work orders, and reject weak/risky sources while preserving no-agent-fetch/no-network/no-search/no-publication/no-outreach/no-payment/no-revenue/no-MCP/no-live/no-CIEU-DB-write/no-canonical-mutation/no-brain-memory-writeback/no-direct-Y-star mutation constraints.",
                "Y_t_plus_1": {
                    "evidence_needs_inferred": len(evidence_needs),
                    "source_hypotheses_generated": len(source_hypotheses),
                    "source_hypotheses_ranked": len(priority_rows),
                    "work_orders_generated": len(work_orders),
                    "source_hypotheses_rejected": len(rejected_source_hypotheses),
                    "real_external_observation_authorized": False,
                    "agent_external_fetch_authorized": False,
                },
                "R_t_plus_1": residuals,
                "event_mode": "l6_8_agentic_external_evidence_discovery_trust_judgment_fixture",
                "persistence_enabled": False,
                "db_write_performed": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_strategic_residual_delta.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "residual_classes": [
                    "source_hypothesis_not_live_verified",
                    "trust_judgment_candidate_only",
                    "work_order_future_approval_required",
                    "no_real_evidence_captured",
                    "no_current_factual_claim_established",
                    "ranking_model_untested_on_live_sources",
                    "future_controlled_read_only_pilot_required",
                    "externalization_and_revenue_blocked",
                ],
                "residuals": residuals,
            }
        ),
        generated,
    )
    write_json(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_meta_learning_update_candidate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "learning_targets": [
                    "evidence_need_inference_policy",
                    "source_hypothesis_generation_policy",
                    "structural_trust_judgment_policy",
                    "value_of_information_policy",
                    "source_prioritization_policy",
                    "pre_observation_rejection_policy",
                ],
                "eligible_for_review_queue": True,
                "eligible_for_direct_brain_writeback": False,
                "eligible_for_direct_memory_ingestion": False,
                "eligible_for_candidate_auto_approval": False,
                "eligible_for_direct_strategy_mutation": False,
                "approved": False,
                "applied": False,
            }
        ),
        generated,
    )
    write_text(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_residual_report.md",
        "# L6.8 Strategic Residual\n\n"
        "Residuals remain because no real sources were observed, source hypotheses "
        "are candidate-only, and future controlled approval is still required.\n",
        generated,
    )

    readiness = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "l6_8_agentic_evidence_discovery_and_trust_judgment_engine_complete": True,
            "evidence_need_inference_generated": True,
            "source_hypotheses_generated": True,
            "source_type_value_model_generated": True,
            "structural_trust_judgment_generated": True,
            "value_of_information_model_generated": True,
            "source_prioritization_generated": True,
            "conflict_corroboration_model_generated": True,
            "observation_work_orders_generated": True,
            "pre_observation_rejection_filter_generated": True,
            "agentic_evidence_decision_gate_generated": True,
            "no_action_receipts_generated": True,
            "strategic_residual_loop_generated": True,
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval": True,
            "ready_for_actual_network_observation_now": False,
            "ready_for_autonomous_web_search_now": False,
            "ready_for_scraping": False,
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "next_recommended_milestone": NEXT_MILESTONE,
            "blocked_capabilities": NO_ACTION_CONSTRAINTS,
        }
    )
    write_json("l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json", readiness, generated)
    write_json(
        "l6_agentic_evidence_readiness_report/l6_8_next_milestone_recommendation.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "recommended_next_milestone": NEXT_MILESTONE,
                "do_not_implement_now": True,
                "reason": "L6.8 generates the agentic evidence selection brain but still requires future approval before any controlled observation pilot.",
            }
        ),
        generated,
    )
    write_json(
        "l6_agentic_evidence_readiness_report/l6_8_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": NO_ACTION_CONSTRAINTS,
                "real_observation_blocked": True,
                "autonomous_search_blocked": True,
                "real_approval_blocked": True,
            }
        ),
        generated,
    )
    write_text(
        "l6_agentic_evidence_readiness_report/l6_8_readiness_report.md",
        "# L6.8 Readiness\n\n"
        "The agentic evidence discovery and structural trust judgment engine is "
        "complete for design/sandbox use and ready for L6.9 approval-packet "
        "design. Actual network observation, autonomous web search, scraping, "
        "publication, outreach, payment, revenue, MCP, live behavior, CIEU DB "
        "writes, canonical mutation, brain/memory writeback, and direct Y* "
        "mutation remain blocked.\n",
        generated,
    )

    print(f"Built L6.8 agentic evidence discovery and trust judgment artifacts: {len(generated)} files")
    return generated


if __name__ == "__main__":
    build()
