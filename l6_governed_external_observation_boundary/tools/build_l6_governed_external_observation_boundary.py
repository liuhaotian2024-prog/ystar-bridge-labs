#!/usr/bin/env python3
"""Build deterministic L6.2 governed external observation boundary outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

BOUNDARY = ROOT / "l6_governed_external_observation_boundary"
DEFINITION = ROOT / "external_observation_definition_and_scope"
PACKET = ROOT / "pre_observation_packet_schema"
SOURCE_POLICY = ROOT / "external_source_registry_and_policy"
GATE = ROOT / "external_observation_permission_gate"
MANUAL_IMPORT = ROOT / "manual_external_evidence_import_sandbox"
LINKER = ROOT / "observation_to_mvp_artifact_linker"
CLAIMS = ROOT / "observation_claim_boundary_and_freshness"
RECEIPTS = ROOT / "external_observation_no_action_receipts"
RESIDUAL = ROOT / "l6_external_observation_strategic_residual_loop"
READINESS = ROOT / "l6_external_observation_boundary_readiness"

SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.2"
MILESTONE_NAME = "Governed External Observation Boundary v0"
NEXT_MILESTONE = "L6.3 Controlled External Observation Sandbox v0"
STATIC_MARKER = (
    "STATIC FIXTURE ONLY - NOT FETCHED - NOT CURRENT FACT - "
    "NOT VERIFIED EXTERNAL DATA - NOT AUTHORIZED FOR EXTERNAL ACTION - "
    "NOT AUTHORIZED FOR PUBLICATION - NOT AUTHORIZED FOR OUTREACH - "
    "NOT AUTHORIZED FOR PAYMENT - NOT AUTHORIZED FOR REVENUE EXECUTION"
)

INPUT_REFS = {
    "l6_0_engine_summary": (
        "l6_meta_development_generative_selection_engine/"
        "l6_generative_selection_engine_summary.json"
    ),
    "l6_0_generated_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_0_selection_ranking": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "l6_0_design_readiness": (
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"
    ),
    "l6_1_summary": "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
    "l6_1_selected_hypotheses": (
        "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json"
    ),
    "l6_1_case_index": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_1_externalization_blocker": (
        "mvp_artifact_externalization_boundary/externalization_blocker.json"
    ),
    "l6_1_review_gate": "mvp_artifact_review_gate/review_gate_contract.json",
    "l6_1_readiness": "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
    "l5_13_live_boundary_readiness": "live_boundary_readiness/live_boundary_readiness.json",
    "l5_13_no_go_decision": "system_no_go_decision_packet/system_no_go_decision_packet.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "external_observation_execution_enabled": False,
    "network_enabled": False,
    "api_enabled": False,
    "scraping_enabled": False,
    "browser_fetch_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
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
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "revenue_execution_enabled": False,
    "external_market_scan_enabled": False,
    "public_content_publication_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
    "payment_enabled": False,
}

L6_2_FLAGS = {
    "l6_2_boundary_only": True,
    "l6_2_sandbox_only": True,
    "l6_2_static_fixture_generation_enabled": True,
    "l6_2_manual_evidence_import_contract_enabled": True,
    "l6_2_real_external_observation_enabled": False,
    "l6_2_network_enabled": False,
    "l6_2_api_enabled": False,
    "l6_2_scraping_enabled": False,
    "l6_2_browser_fetch_enabled": False,
    "l6_2_publication_enabled": False,
    "l6_2_outreach_enabled": False,
    "l6_2_payment_enabled": False,
    "l6_2_revenue_execution_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "real_external_observation_authorized": False,
    "network_authorized": False,
    "api_authorized": False,
    "scraping_authorized": False,
    "browser_fetch_authorized": False,
    "external_action_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "payment_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
}

PACKET_FIELDS = [
    "packet_id",
    "observation_intent",
    "linked_l6_hypothesis_id",
    "linked_l6_1_artifact_case_id",
    "intended_external_surface",
    "source_type",
    "source_locator_placeholder",
    "proposed_observation_method",
    "data_requested",
    "claim_to_validate_or_refine",
    "expected_evidence_type",
    "freshness_requirement",
    "trust_tier_requirement",
    "privacy_risk",
    "ip_risk",
    "login_required",
    "account_required",
    "contact_required",
    "payment_required",
    "write_or_post_required",
    "automation_required",
    "mcp_required",
    "network_required",
    "execution_required",
    "publication_required",
    "outreach_required",
    "no_action_guarantee",
    "evidence_capture_plan",
    "citation_or_source_trace_plan",
    "review_required",
    "approval_required_before_real_observation",
]

SOURCE_TYPES = [
    "official_policy_source",
    "official_program_source",
    "public_market_source",
    "public_platform_source",
    "public_repository_source",
    "public_document_source",
    "user_supplied_document",
    "user_supplied_summary",
    "manually_imported_note",
    "manually_imported_screenshot_summary",
    "future_approved_read_only_search_result",
]

FUTURE_OBSERVATION_MODES = [
    "reading public pages",
    "reviewing grant/RFP/bounty pages",
    "reviewing market signals",
    "reviewing platform policy pages",
    "reviewing customer-provided public materials",
    "manually imported notes",
    "manually imported screenshots/summaries",
    "user-provided documents",
    "future approved read-only search",
]

DISALLOWED_L6_2_MODES = [
    "network fetch",
    "API calls",
    "scraping",
    "login-required access",
    "account creation",
    "form submission",
    "customer contact",
    "publication",
    "payment",
    "purchasing",
    "posting",
    "commenting",
    "subscribing",
    "messaging",
    "MCP execution",
    "live behavior execution",
]

GATE_DECISIONS = [
    "block_real_observation_l6_2",
    "allow_static_fixture_only",
    "require_review_before_observation",
    "require_approval_before_observation",
    "deny_due_to_external_action",
    "deny_due_to_network_required_now",
    "deny_due_to_contact_required",
    "deny_due_to_payment_required",
    "deny_due_to_publication_required",
    "deny_due_to_mcp_execution_required",
    "deny_due_to_login_or_account_required",
    "deny_due_to_privacy_or_ip_risk",
    "deny_due_to_missing_trace_plan",
]


class BuildError(Exception):
    """Raised when safe generated artifacts cannot be built."""


def read_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BuildError(f"Refusing to read outside repo: {relative_path}") from exc
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: Any, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")
    generated.append(relative_path)


def write_text(relative_path: str, text: str, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated.append(relative_path)


def with_common(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "safety_flags": SAFETY_FLAGS,
        "l6_2_flags": L6_2_FLAGS,
    }


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs = {}
    gaps = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def selected_case_refs() -> list[dict[str, Any]]:
    case_index = read_json(INPUT_REFS["l6_1_case_index"]) or {}
    cases = case_index.get("cases", [])
    if cases:
        return cases[:3]
    return [
        {
            "case_id": "case_001",
            "source_hypothesis_id": "hypothesis_placeholder",
            "artifact_kind": "static_boundary_placeholder",
        }
    ]


def dry_run_packets(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets = []
    source_cycle = [
        "user_supplied_summary",
        "manually_imported_note",
        "future_approved_read_only_search_result",
    ]
    for index, case in enumerate(cases, start=1):
        packet_id = f"l6_2_pre_observation_packet_{index:03d}"
        packets.append(
            {
                "fixture_marker": STATIC_MARKER,
                "packet_id": packet_id,
                "observation_intent": (
                    "Refine the internal MVP artifact evidence boundary without "
                    "performing any live observation."
                ),
                "linked_l6_hypothesis_id": case.get("source_hypothesis_id"),
                "linked_l6_1_artifact_case_id": case.get("case_id"),
                "intended_external_surface": "future_external_surface_placeholder",
                "source_type": source_cycle[(index - 1) % len(source_cycle)],
                "source_locator_placeholder": f"source-locator-placeholder-{index:03d}",
                "proposed_observation_method": "static_fixture_or_future_manual_import_only",
                "data_requested": [
                    "source date if supplied by user",
                    "claim support excerpt if supplied by user",
                    "context limitations",
                ],
                "claim_to_validate_or_refine": "recipient need and acceptance criteria placeholder",
                "expected_evidence_type": "manual_summary_or_static_fixture",
                "freshness_requirement": "date_available_or_date_missing_marker_required",
                "trust_tier_requirement": "structural_source_trace_required",
                "privacy_risk": "low_placeholder_but_review_required",
                "ip_risk": "low_placeholder_but_review_required",
                "login_required": False,
                "account_required": False,
                "contact_required": False,
                "payment_required": False,
                "write_or_post_required": False,
                "automation_required": False,
                "mcp_required": False,
                "network_required": False,
                "execution_required": False,
                "publication_required": False,
                "outreach_required": False,
                "no_action_guarantee": True,
                "evidence_capture_plan": {
                    "capture_mode": "manual_or_static_fixture_only",
                    "url_fetch_performed": False,
                    "content_fetched": False,
                    "external_action_authorized": False,
                },
                "citation_or_source_trace_plan": {
                    "source_locator_recorded_as_locator_only": True,
                    "source_date_required_if_available": True,
                    "unsupported_inferences_marked": True,
                    "review_required": True,
                },
                "review_required": True,
                "approval_required_before_real_observation": True,
                **BLOCKED_AUTHORIZATIONS,
            }
        )
    return packets


def receipt(action_type: str) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "authorized_in_l6_2": False,
        "executed_in_l6_2": False,
        "blocker_reference": "l6_governed_external_observation_boundary/l6_2_milestone_contract.json",
        "future_boundary_required": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
    }


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    cases = selected_case_refs()
    packets = dry_run_packets(cases)
    case_ids = [case.get("case_id") for case in cases]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1"],
            "mode": "boundary_only",
            "sandbox_only": True,
            "static_fixture_generation_authorized": True,
            "manual_evidence_import_contract_authorized": True,
            "requires_review_before_any_real_observation": True,
            "required_outputs": [
                "external observation definition",
                "Pre-Observation packet schema",
                "source registry and trust/freshness policy",
                "permission gate decisions",
                "manual evidence import sandbox",
                "observation-to-MVP artifact linker",
                "claim boundary and freshness policy",
                "no-action receipts",
                "strategic residual fixture",
                "readiness assessment",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json("l6_governed_external_observation_boundary/l6_2_milestone_contract.json", contract, generated)
    write_json(
        "l6_governed_external_observation_boundary/l6_2_boundary_scope.json",
        with_common(
            {
                "milestone_id": MILESTONE_ID,
                "scope_status": "boundary_only_static_fixture_only",
                "in_scope": [
                    "define future external observation governance",
                    "define packet schemas",
                    "define source and trust policies",
                    "generate static dry-run packets",
                    "generate manual import contracts",
                    "link possible future evidence to L6.1 artifacts as candidates only",
                ],
                "out_of_scope": DISALLOWED_L6_2_MODES
                + [
                    "real external observation",
                    "current market claims",
                    "canonical update",
                    "brain or memory writeback",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_governed_external_observation_boundary/l6_2_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_2_flags": L6_2_FLAGS},
        generated,
    )
    write_text(
        "l6_governed_external_observation_boundary/README.md",
        "# L6.2 Governed External Observation Boundary\n\n"
        "Boundary-only artifacts for future external observation. L6.2 does not fetch, "
        "scrape, publish, contact, pay, execute, mutate, or write memory.\n",
        generated,
    )
    write_text(
        "l6_governed_external_observation_boundary/l6_2_non_execution_boundary.md",
        "# L6.2 Non-Execution Boundary\n\n"
        f"{STATIC_MARKER}\n\n"
        "No network, API, scraping, browser fetch, publication, outreach, payment, "
        "revenue execution, MCP execution, live behavior, canonical update, brain "
        "writeback, memory ingestion, or direct Y* mutation is authorized.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_2_external_observation_boundary_defined": True,
        "boundary_only": True,
        "sandbox_only": True,
        "pre_observation_packet_schema_defined": True,
        "source_registry_defined": True,
        "permission_gate_defined": True,
        "manual_import_sandbox_defined": True,
        "observation_to_artifact_linker_defined": True,
        "claim_boundary_policy_defined": True,
        "no_action_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "static_fixture_generation_authorized": True,
        "manual_evidence_import_contract_authorized": True,
        "real_external_observation_authorized": False,
        "network_authorized": False,
        "publication_authorized": False,
        "outreach_authorized": False,
        "payment_authorized": False,
        "revenue_execution_authorized": False,
        "mcp_execution_authorized": False,
        "ready_for_l6_3_controlled_external_observation_sandbox": True,
        "ready_for_real_network_observation": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "input_refs": refs,
        "missing_optional_refs": missing_refs,
        "warning": (
            "L6.2 defines external observation governance only. No external "
            "observation, network, scraping, publication, outreach, payment, "
            "revenue, MCP, live behavior, writeback, or canonical mutation occurred."
        ),
    }
    write_json("l6_governed_external_observation_boundary/l6_2_summary.json", summary, generated)
    write_text(
        "l6_governed_external_observation_boundary/l6_2_summary.md",
        "# L6.2 Summary\n\n"
        "- Boundary defined: true\n"
        "- Real external observation authorized: false\n"
        "- Static fixtures authorized: true\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    write_json(
        "external_observation_definition_and_scope/external_observation_definition.json",
        with_common(
            {
                "definition_id": "l6_2_external_observation_definition",
                "external_observation_means": (
                    "A future governed read-only act of collecting or receiving "
                    "external evidence to refine internal hypotheses."
                ),
                "external_observation_does_not_mean": [
                    "publication",
                    "outreach",
                    "payment",
                    "customer contact",
                    "revenue execution",
                    "canonical mutation",
                    "brain or memory writeback",
                    "approval to execute",
                ],
                "real_external_observation_authorized_now": False,
            }
        ),
        generated,
    )
    write_json(
        "external_observation_definition_and_scope/observation_vs_action_boundary.json",
        with_common(
            {
                "observation_is_read_or_receive_only_future_mode": True,
                "action_boundary": {
                    "observe_does_not_publish": True,
                    "observe_does_not_contact": True,
                    "observe_does_not_pay": True,
                    "observe_does_not_submit": True,
                    "observe_does_not_mutate": True,
                    "observe_does_not_approve": True,
                },
                "l6_2_all_real_observation_blocked": True,
            }
        ),
        generated,
    )
    write_json(
        "external_observation_definition_and_scope/allowed_future_observation_modes.json",
        {
            "schema_version": SCHEMA_VERSION,
            "mode_status": "future_only_not_authorized_in_l6_2",
            "allowed_future_observation_modes": [
                {
                    "mode": mode,
                    "future_only": True,
                    "authorized_in_l6_2": False,
                    "requires_future_review": True,
                }
                for mode in FUTURE_OBSERVATION_MODES
            ],
            "safety_flags": SAFETY_FLAGS,
        },
        generated,
    )
    write_json(
        "external_observation_definition_and_scope/disallowed_l6_2_observation_modes.json",
        {
            "schema_version": SCHEMA_VERSION,
            "disallowed_l6_2_observation_modes": DISALLOWED_L6_2_MODES,
            "all_disallowed_modes_authorized": False,
            "safety_flags": SAFETY_FLAGS,
        },
        generated,
    )
    write_text(
        "external_observation_definition_and_scope/external_observation_scope_report.md",
        "# External Observation Scope Report\n\n"
        "L6.2 distinguishes future read-only observation from action. Every real "
        "external observation mode remains blocked in this milestone.\n",
        generated,
    )

    write_json(
        "pre_observation_packet_schema/pre_observation_packet_schema.json",
        {
            "schema_version": SCHEMA_VERSION,
            "schema_id": "l6_2_pre_observation_packet_schema",
            "required_fields": PACKET_FIELDS,
            "field_types": {field: "structural_value" for field in PACKET_FIELDS},
            "real_observation_authorized_by_schema": False,
            "safety_flags": SAFETY_FLAGS,
        },
        generated,
    )
    write_json(
        "pre_observation_packet_schema/pre_observation_packet_required_fields.json",
        {"schema_version": SCHEMA_VERSION, "required_fields": PACKET_FIELDS},
        generated,
    )
    write_json(
        "pre_observation_packet_schema/pre_observation_packet_examples.json",
        {
            "schema_version": SCHEMA_VERSION,
            "example_status": "dry_run_static_examples_only",
            "examples": packets,
        },
        generated,
    )
    invalid_examples = [
        {
            **packets[0],
            "packet_id": "invalid_network_required",
            "network_required": True,
            "expected_gate_decision": "deny_due_to_network_required_now",
        },
        {
            **packets[0],
            "packet_id": "invalid_contact_required",
            "contact_required": True,
            "expected_gate_decision": "deny_due_to_contact_required",
        },
        {
            **packets[0],
            "packet_id": "invalid_missing_trace_plan",
            "citation_or_source_trace_plan": None,
            "expected_gate_decision": "deny_due_to_missing_trace_plan",
        },
    ]
    write_json(
        "pre_observation_packet_schema/invalid_pre_observation_packet_examples.json",
        {"schema_version": SCHEMA_VERSION, "examples": invalid_examples},
        generated,
    )
    write_text(
        "pre_observation_packet_schema/pre_observation_packet_report.md",
        "# Pre-Observation Packet Report\n\n"
        "Packets are dry-run/static examples only and cannot authorize real observation.\n",
        generated,
    )

    write_json(
        "external_source_registry_and_policy/source_type_registry.json",
        {
            "schema_version": SCHEMA_VERSION,
            "source_type_status": "source_types_not_opportunity_categories",
            "source_types": [
                {
                    "source_type": source_type,
                    "not_strategy_category": True,
                    "real_fetch_authorized_in_l6_2": False,
                }
                for source_type in SOURCE_TYPES
            ],
        },
        generated,
    )
    write_json(
        "external_source_registry_and_policy/source_trust_tier_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "trust_policy_mode": "structural_indicators_only",
            "allowed_trust_indicators": [
                "official source vs third-party source",
                "date available vs date missing",
                "source locator present vs missing",
                "evidence captured vs not captured",
                "claim supported vs unsupported",
                "source conflict present vs absent",
                "review required",
            ],
            "forbidden_authority_modes": [
                "LLM confidence as authority",
                "semantic authority score",
                "market success score",
            ],
            "semantic_truth_scoring_enabled": False,
        },
        generated,
    )
    write_json(
        "external_source_registry_and_policy/source_freshness_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "freshness_classes": [
                "date_available_currentness_unverified",
                "date_available_stale_possible",
                "date_missing",
                "future_recheck_required",
                "manual_claim_only",
            ],
            "freshness_is_not_truth_authority": True,
            "review_required_for_stale_or_missing_date": True,
        },
        generated,
    )
    write_json(
        "external_source_registry_and_policy/source_risk_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "risk_dimensions": [
                "privacy_risk",
                "ip_risk",
                "login_required",
                "account_required",
                "contact_required",
                "payment_required",
                "write_or_post_required",
                "automation_required",
            ],
            "high_risk_result": "deny_or_require_future_boundary",
        },
        generated,
    )
    write_json(
        "external_source_registry_and_policy/evidence_trace_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "trace_requirements": [
                "source locator or source missing marker",
                "capture mode",
                "capture date if available",
                "claim boundary",
                "unsupported inference marker",
                "review status",
            ],
            "url_fetch_performed_in_l6_2": False,
        },
        generated,
    )
    write_text(
        "external_source_registry_and_policy/source_registry_report.md",
        "# Source Registry Report\n\n"
        "Source entries are structural source types, not fixed opportunity classes or strategy categories.\n",
        generated,
    )

    matrix = [
        {
            "condition": "safe_static_fixture_packet",
            "decision": "allow_static_fixture_only",
            "real_observation_authorized": False,
        },
        {
            "condition": "otherwise_valid_future_packet",
            "decision": "block_real_observation_l6_2",
            "real_observation_authorized": False,
        },
        {
            "condition": "network_required_now",
            "decision": "deny_due_to_network_required_now",
            "real_observation_authorized": False,
        },
        {
            "condition": "contact_required",
            "decision": "deny_due_to_contact_required",
            "real_observation_authorized": False,
        },
        {
            "condition": "missing_trace_plan",
            "decision": "deny_due_to_missing_trace_plan",
            "real_observation_authorized": False,
        },
    ]
    write_json(
        "external_observation_permission_gate/observation_permission_gate_contract.json",
        with_common(
            {
                "gate_id": "l6_2_external_observation_permission_gate",
                "gate_mode": "deterministic_boundary_gate",
                "decisions": GATE_DECISIONS,
                "l6_2_default_decision": "block_real_observation_l6_2",
                "real_observation_authorized_in_l6_2": False,
            }
        ),
        generated,
    )
    write_json(
        "external_observation_permission_gate/observation_gate_decision_matrix.json",
        {"schema_version": SCHEMA_VERSION, "decision_matrix": matrix},
        generated,
    )
    write_json(
        "external_observation_permission_gate/valid_blocked_observation_packet_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "packet_decisions": [
                {
                    "packet_id": packet["packet_id"],
                    "decision": "allow_static_fixture_only",
                    "real_observation_authorized": False,
                    "review_required_before_observation": True,
                }
                for packet in packets
            ],
        },
        generated,
    )
    write_json(
        "external_observation_permission_gate/invalid_observation_packet_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "packet_decisions": [
                {
                    "packet_id": packet["packet_id"],
                    "decision": packet["expected_gate_decision"],
                    "real_observation_authorized": False,
                }
                for packet in invalid_examples
            ],
        },
        generated,
    )
    write_text(
        "external_observation_permission_gate/observation_permission_gate_report.md",
        "# Observation Permission Gate Report\n\n"
        "Every L6.2 real observation path is blocked. Safe packets can only become static fixture plans.\n",
        generated,
    )

    manual_contract = with_common(
        {
            "contract_id": "l6_2_manual_external_evidence_import_contract",
            "manual_import_mode": "future_user_supplied_or_static_fixture_only",
            "allowed_future_inputs": [
                "user-pasted text",
                "user-uploaded file",
                "user-provided source summary",
                "user-provided screenshot description",
                "user-provided public URL as locator only",
            ],
            "url_fetch_authorized": False,
            "external_action_authorized": False,
            "review_required": True,
        }
    )
    write_json("manual_external_evidence_import_sandbox/manual_import_contract.json", manual_contract, generated)
    write_json(
        "manual_external_evidence_import_sandbox/manual_import_packet_schema.json",
        {
            "schema_version": SCHEMA_VERSION,
            "required_fields": [
                "import_packet_id",
                "supplied_by_user",
                "source_locator_provided",
                "source_content_available",
                "freshness_declared",
                "source_date_declared",
                "evidence_scope",
                "claim_boundary",
                "missing_context",
                "review_required",
                "external_action_authorized",
            ],
        },
        generated,
    )
    manual_examples = [
        {
            "fixture_marker": STATIC_MARKER,
            "import_packet_id": "manual_import_static_fixture_001",
            "supplied_by_user": False,
            "source_locator_provided": True,
            "source_content_available": False,
            "freshness_declared": "not_current_fact",
            "source_date_declared": "date_missing_static_fixture",
            "evidence_scope": "example only",
            "claim_boundary": "cannot support current external claim",
            "missing_context": ["source content", "capture date", "review"],
            "review_required": True,
            "external_action_authorized": False,
            "url_fetched": False,
        }
    ]
    write_json(
        "manual_external_evidence_import_sandbox/manual_import_static_fixture_examples.json",
        {"schema_version": SCHEMA_VERSION, "examples": manual_examples},
        generated,
    )
    write_json(
        "manual_external_evidence_import_sandbox/manual_import_evidence_registry.json",
        {
            "schema_version": SCHEMA_VERSION,
            "registry_mode": "static_fixture_registry",
            "evidence_items": manual_examples,
            "all_items_current_facts": False,
            "url_fetch_performed": False,
        },
        generated,
    )
    write_json(
        "manual_external_evidence_import_sandbox/manual_import_validation_matrix.json",
        {
            "schema_version": SCHEMA_VERSION,
            "validation_mode": "structural_only",
            "checks": [
                "required fields present",
                "source locator marked locator-only when no content is supplied",
                "freshness declared",
                "claim boundary present",
                "missing context listed",
                "review required",
                "external action authorization false",
                "URL fetch false",
            ],
            "semantic_truth_scoring_enabled": False,
        },
        generated,
    )
    write_text(
        "manual_external_evidence_import_sandbox/manual_import_report.md",
        "# Manual Import Report\n\n"
        "Manual import is a future contract only. L6.2 does not fetch URL locators or import live evidence.\n",
        generated,
    )

    refinements = [
        "acceptance criteria clarification",
        "recipient archetype clarification",
        "payer clarity",
        "evidence needed refinement",
        "claim boundary refinement",
        "freshness requirement refinement",
        "distribution friction assessment",
        "competitive pressure assessment",
        "external dependency assessment",
        "proof question refinement",
    ]
    write_json(
        "observation_to_mvp_artifact_linker/observation_to_artifact_link_contract.json",
        with_common(
            {
                "contract_id": "l6_2_observation_to_artifact_link_contract",
                "link_mode": "candidate_refinement_only",
                "direct_artifact_mutation_authorized": False,
                "canonical_update_authorized": False,
                "brain_writeback_authorized": False,
                "memory_ingestion_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_to_mvp_artifact_linker/l6_1_artifact_case_reference_map.json",
        {
            "schema_version": SCHEMA_VERSION,
            "case_refs": [
                {
                    "case_id": case.get("case_id"),
                    "source_hypothesis_id": case.get("source_hypothesis_id"),
                    "case_contract_ref": f"selected_mvp_artifact_cases/{case.get('case_id')}/case_contract.json",
                }
                for case in cases
            ],
        },
        generated,
    )
    write_json(
        "observation_to_mvp_artifact_linker/observation_refinement_targets.json",
        {"schema_version": SCHEMA_VERSION, "refinement_targets": refinements},
        generated,
    )
    write_json(
        "observation_to_mvp_artifact_linker/artifact_update_candidate_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_policy": {
                "eligible_for_review_queue": True,
                "approved": False,
                "applied": False,
                "direct_artifact_mutation_authorized": False,
                "canonical_update_authorized": False,
                "brain_writeback_authorized": False,
                "memory_ingestion_authorized": False,
            },
        },
        generated,
    )
    write_text(
        "observation_to_mvp_artifact_linker/observation_to_artifact_link_report.md",
        "# Observation to MVP Artifact Link Report\n\n"
        "Observation evidence may only create review candidates. No L6.1 artifact or canonical strategy is mutated.\n",
        generated,
    )

    write_json(
        "observation_claim_boundary_and_freshness/claim_boundary_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "required_claim_fields": [
                "source trace",
                "date or date_missing marker",
                "freshness class",
                "claim scope",
                "claim limitation",
                "unsupported inference marker",
                "conflict marker if applicable",
                "review status",
            ],
            "semantic_truth_scoring_enabled": False,
        },
        generated,
    )
    write_json(
        "observation_claim_boundary_and_freshness/freshness_window_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "freshness_windows": [
                "same_day_if_future_approved",
                "seven_day_if_future_approved",
                "thirty_day_if_future_approved",
                "stale_requires_recheck",
                "date_missing_requires_marker",
            ],
            "current_fact_claims_authorized_in_l6_2": False,
        },
        generated,
    )
    write_json(
        "observation_claim_boundary_and_freshness/evidence_claim_mapping.json",
        {
            "schema_version": SCHEMA_VERSION,
            "mapping_mode": "claim_to_source_trace_structural_mapping",
            "example_mappings": [
                {
                    "claim_id": "static_fixture_claim_001",
                    "source_trace": "manual_import_static_fixture_001",
                    "freshness_class": "date_missing",
                    "claim_scope": "example only",
                    "unsupported_inference_marker": True,
                    "review_status": "not_reviewed",
                }
            ],
        },
        generated,
    )
    write_json(
        "observation_claim_boundary_and_freshness/unsupported_claim_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "unsupported_claim_handling": "mark_unsupported_and_block_externalization",
            "current_market_claims_without_source_allowed": False,
        },
        generated,
    )
    write_json(
        "observation_claim_boundary_and_freshness/conflicting_source_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "conflict_handling": "mark_conflict_and_require_review",
            "auto_resolution_authorized": False,
        },
        generated,
    )
    write_text(
        "observation_claim_boundary_and_freshness/claim_boundary_report.md",
        "# Claim Boundary Report\n\n"
        "Observation-derived claims require trace, freshness, limitation, unsupported inference, conflict, and review markers.\n",
        generated,
    )

    receipt_map = {
        "no_network_receipt.json": "network",
        "no_api_receipt.json": "api",
        "no_scraping_receipt.json": "scraping",
        "no_publication_receipt.json": "publication",
        "no_outreach_receipt.json": "outreach",
        "no_payment_receipt.json": "payment",
        "no_revenue_execution_receipt.json": "revenue_execution",
        "no_mcp_execution_receipt.json": "mcp_execution",
        "no_live_behavior_receipt.json": "live_behavior",
        "no_canonical_mutation_receipt.json": "canonical_mutation",
        "no_brain_memory_writeback_receipt.json": "brain_memory_writeback",
        "no_direct_y_star_mutation_receipt.json": "direct_y_star_mutation",
    }
    for filename, action_type in receipt_map.items():
        write_json(f"external_observation_no_action_receipts/{filename}", receipt(action_type), generated)
    write_text(
        "external_observation_no_action_receipts/no_action_receipt_report.md",
        "# No-Action Receipt Report\n\n"
        "L6.2 produced boundary artifacts only. All external-world and mutation actions are not authorized and not executed.\n",
        generated,
    )

    write_json(
        "l6_external_observation_strategic_residual_loop/l6_2_cieu_like_fixture.json",
        {
            "schema_version": SCHEMA_VERSION,
            "event_mode": "l6_2_governed_external_observation_boundary_fixture",
            "persistence_enabled": False,
            "db_write_performed": False,
            "X_t": {
                "l6_0_selection_context": refs.get("l6_0_selection_ranking"),
                "l6_1_mvp_artifact_sandbox_state": refs.get("l6_1_readiness"),
                "l6_2_constraints": "boundary_only_no_external_observation",
            },
            "U_t": "Create governed external observation boundary artifacts without executing observation.",
            "Y_star_t": (
                "Create a governed boundary for future external observation that "
                "preserves no-network/no-action/no-publication/no-outreach/"
                "no-payment/no-revenue/no-MCP/no-live/no-canonical-mutation/"
                "no-brain-memory-writeback/no-direct-Y* mutation constraints."
            ),
            "Y_t_plus_1": {
                "external_observation_boundary_created": True,
                "pre_observation_packet_schema_created": True,
                "source_registry_created": True,
                "permission_gate_created": True,
                "manual_import_sandbox_created": True,
                "no_action_receipts_created": True,
                "real_external_observation_executed": False,
            },
            "R_t_plus_1": [
                "observation policy still too conservative",
                "no real source evidence available yet",
                "source trust/freshness policy not tested on live data",
                "manual import workflow not yet exercised with user-supplied evidence",
                "external observation still requires future approval boundary",
                "artifact refinement remains candidate-only",
                "no current-market claims can be made",
            ],
            "safety_flags": SAFETY_FLAGS,
        },
        generated,
    )
    write_json(
        "l6_external_observation_strategic_residual_loop/l6_2_strategic_residual_delta.json",
        {
            "schema_version": SCHEMA_VERSION,
            "residual_classes": {
                "external_observation_boundary_gap": "future approval required",
                "source_trust_gap": "not tested on live evidence",
                "freshness_policy_gap": "no live source dates observed",
                "manual_import_gap": "not exercised with user-provided evidence",
                "artifact_linkage_gap": "candidate-only refinements",
                "claim_boundary_gap": "no current external claims authorized",
                "execution_boundary_gap": "all external execution remains blocked",
            },
        },
        generated,
    )
    write_json(
        "l6_external_observation_strategic_residual_loop/l6_2_meta_learning_update_candidate.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_id": "l6_2_external_observation_boundary_meta_learning_candidate",
            "learning_targets": [
                "external_observation_boundary_policy",
                "pre_observation_packet_policy",
                "source_trust_freshness_policy",
                "manual_import_policy",
                "observation_to_artifact_link_policy",
            ],
            "eligible_for_review_queue": True,
            "eligible_for_direct_brain_writeback": False,
            "eligible_for_direct_memory_ingestion": False,
            "eligible_for_candidate_auto_approval": False,
            "eligible_for_direct_strategy_mutation": False,
            "approved": False,
            "applied": False,
        },
        generated,
    )
    write_text(
        "l6_external_observation_strategic_residual_loop/l6_2_residual_report.md",
        "# L6.2 Residual Report\n\n"
        "The residual is structural: no live source evidence was observed and no external action was taken.\n",
        generated,
    )

    readiness = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "l6_2_external_observation_boundary_complete": True,
            "pre_observation_packet_schema_generated": True,
            "source_registry_generated": True,
            "permission_gate_generated": True,
            "manual_import_sandbox_generated": True,
            "observation_to_artifact_linker_generated": True,
            "claim_boundary_policy_generated": True,
            "no_action_receipts_generated": True,
            "strategic_residual_loop_generated": True,
            "ready_for_l6_3_controlled_external_observation_sandbox": True,
            "ready_for_real_network_observation": False,
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "next_recommended_milestone": NEXT_MILESTONE,
            "blocked_capabilities": [
                "real network observation",
                "publication",
                "outreach",
                "payment",
                "revenue execution",
                "MCP execution",
                "canonical update",
                "brain/memory writeback",
            ],
        }
    )
    write_json(
        "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json",
        readiness,
        generated,
    )
    write_json(
        "l6_external_observation_boundary_readiness/l6_2_next_milestone_recommendation.json",
        {
            "schema_version": SCHEMA_VERSION,
            "recommended_next_milestone": NEXT_MILESTONE,
            "do_not_implement_in_l6_2": True,
            "recommended_scope": "controlled external observation sandbox design with explicit no-action controls",
        },
        generated,
    )
    write_json(
        "l6_external_observation_boundary_readiness/l6_2_blockers.json",
        {
            "schema_version": SCHEMA_VERSION,
            "blockers": [
                "no future approval boundary for real observation yet",
                "no controlled external observation sandbox yet",
                "no URL fetch permission",
                "no source freshness validation against live data",
                "no external action boundary release",
            ],
        },
        generated,
    )
    write_text(
        "l6_external_observation_boundary_readiness/l6_2_readiness_report.md",
        "# L6.2 Readiness Report\n\n"
        "The governed external observation boundary is complete for static/sandbox "
        "reasoning. The next step is L6.3 Controlled External Observation Sandbox v0. "
        "Real network observation remains blocked.\n",
        generated,
    )

    return generated


def main() -> int:
    generated = generate()
    print(f"Built L6.2 governed external observation boundary artifacts ({len(generated)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
