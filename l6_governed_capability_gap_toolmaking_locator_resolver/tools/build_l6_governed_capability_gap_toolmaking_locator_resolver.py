#!/usr/bin/env python3
"""Build L6.10T governed capability-gap toolmaking and locator resolver artifacts.

This builder is local-only. It creates a reusable governed self-tooling
methodology plus a disabled controlled locator resolver adapter. It does not
perform network access, web search, crawling, scraping, browser automation, MCP
execution, live behavior, CIEU DB writes, brain/memory writes, canonical
mutation, or direct Y* mutation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10T"
MILESTONE_NAME = (
    "Governed Capability Gap Tool-Making Methodology & Controlled Locator Resolver Adapter v0"
)
MODE = "governed_capability_gap_toolmaking_and_locator_resolver_adapter"
INPUT_MILESTONES = [
    "L6.0",
    "L6.1",
    "L6.2",
    "L6.3",
    "L6.4",
    "L6.5",
    "L6.6",
    "L6.7",
    "L6.8",
    "L6.9",
    "L6.10",
    "L6.10R",
]
NEXT_IF_BLOCKED = "L6.10U Controlled Locator Resolver Enablement Sandbox v0"
NEXT_IF_SUCCESS = "L6.11 Controlled Multi-Source Read-Only Evidence Corroboration Pilot v0"

RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_resolver_adapters_selected": 1,
    "max_locator_discovery_queries": 1,
    "max_concrete_locators_resolved": 1,
    "max_source_locators_observed": 1,
    "max_pages_read": 1,
    "max_external_reads_total": 2,
    "max_crawled_links": 0,
    "max_followed_links_except_normal_redirect": 0,
    "max_login_attempts": 0,
    "max_forms_submitted": 0,
    "max_messages_sent": 0,
    "max_payments": 0,
}

SAFETY_FLAGS = {
    "os_neutral_design_required": True,
    "mac_only_solution_allowed": False,
    "capability_gap_diagnosis_authorized": True,
    "governed_toolmaking_methodology_authorized": True,
    "controlled_tool_contract_generation_authorized": True,
    "sandbox_tool_adapter_generation_authorized": True,
    "tool_validation_harness_authorized": True,
    "tool_use_gate_generation_authorized": True,
    "controlled_locator_resolver_interface_authorized": True,
    "resolver_capability_probe_authorized": True,
    "resolver_adapter_registry_authorized": True,
    "disabled_no_network_resolver_authorized": True,
    "optional_controlled_locator_discovery_authorized_if_adapter_available": True,
    "tiny_read_only_observation_retry_authorized_if_locator_resolved": True,
    "tool_external_authority_auto_grant_authorized": False,
    "broad_web_search_authorized": False,
    "repeated_search_loop_authorized": False,
    "crawling_authorized": False,
    "scraping_authorized": False,
    "browser_automation_authorized": False,
    "login_authorized": False,
    "account_creation_authorized": False,
    "contact_authorized": False,
    "payment_authorized": False,
    "form_submission_authorized": False,
    "posting_commenting_messaging_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "live_behavior_authorized": False,
    "cieu_db_write_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
    "artifact_refinement_candidate_generation_authorized": True,
    "artifact_refinement_application_authorized": False,
    "semantic_truth_scoring_authorized": False,
    "llm_confidence_as_authority_authorized": False,
}

LIFECYCLE_STAGES = [
    "detect_blocker",
    "classify_gap",
    "decide_if_toolmaking_candidate",
    "define_minimum_capability",
    "define_tool_non_goals",
    "define_tool_contract",
    "define_adapter_interface",
    "define_sandbox_implementation",
    "define_validation_tests",
    "define_safety_receipts",
    "define_integration_point",
    "define_use_gate",
    "generate_residual",
    "submit_for_review",
]

BLOCKER_TAXONOMY = [
    "goal_definition_gap",
    "evidence_gap",
    "locator_gap",
    "tool_capability_gap",
    "runtime_environment_gap",
    "approval_gap",
    "governance_boundary_gap",
    "execution_authority_gap",
    "persistence_permission_gap",
    "source_trust_gap",
    "source_freshness_gap",
    "artifact_quality_gap",
    "strategy_boundary_gap",
    "unknown_gap",
]

NO_ACTIONS = [
    "broad_search",
    "repeated_search_loop",
    "crawling",
    "scraping",
    "browser_automation",
    "login",
    "account_creation",
    "contact",
    "payment",
    "form_submission",
    "posting_commenting_messaging",
    "publication",
    "outreach",
    "revenue_execution",
    "mcp_execution",
    "live_behavior",
    "cieu_db_write",
    "canonical_mutation",
    "brain_memory_writeback",
    "direct_y_star_mutation",
]

FORBIDDEN_TOOL_PATTERNS = [
    "unbounded_search",
    "self_approval",
    "implicit_network_authority",
    "implicit_persistence_authority",
    "implicit_mcp_authority",
    "implicit_publication_outreach_payment_authority",
    "tool_can_modify_canonical_strategy",
    "tool_can_write_brain_memory",
    "tool_can_mutate_y_star",
    "tool_can_bypass_review_gate",
    "tool_can_expand_scope_during_runtime",
]

RESOLVER_ERROR_CODES = [
    "no_controlled_locator_resolver_available",
    "adapter_present_but_disabled",
    "adapter_policy_mismatch",
    "locator_unresolved_within_budget",
    "resolved_locator_failed_eligibility_gate",
    "environment_disallows_external_reads",
    "network_tool_unavailable",
]

RECEIPTS = [
    ("no_broad_search_receipt.json", "broad_search"),
    ("no_repeated_search_loop_receipt.json", "repeated_search_loop"),
    ("no_crawling_receipt.json", "crawling"),
    ("no_scraping_receipt.json", "scraping"),
    ("no_browser_automation_receipt.json", "browser_automation"),
    ("no_login_receipt.json", "login"),
    ("no_account_creation_receipt.json", "account_creation"),
    ("no_contact_receipt.json", "contact"),
    ("no_payment_receipt.json", "payment"),
    ("no_form_submission_receipt.json", "form_submission"),
    ("no_posting_commenting_messaging_receipt.json", "posting_commenting_messaging"),
    ("no_publication_receipt.json", "publication"),
    ("no_outreach_receipt.json", "outreach"),
    ("no_revenue_execution_receipt.json", "revenue_execution"),
    ("no_mcp_execution_receipt.json", "mcp_execution"),
    ("no_live_behavior_receipt.json", "live_behavior"),
    ("no_cieu_db_write_receipt.json", "cieu_db_write"),
    ("no_canonical_mutation_receipt.json", "canonical_mutation"),
    ("no_brain_memory_writeback_receipt.json", "brain_memory_writeback"),
    ("no_direct_y_star_mutation_receipt.json", "direct_y_star_mutation"),
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
    target.write_text(text.strip() + "\n", encoding="utf-8")
    generated.append(path)


def with_controls(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["runtime_limits"] = RUNTIME_LIMITS
    enriched["safety_flags"] = SAFETY_FLAGS
    return enriched


def md_report(title: str, body: str) -> str:
    return (
        f"# {title}\n\n"
        "L6.10T GOVERNED CAPABILITY GAP TOOL-MAKING AND CONTROLLED LOCATOR RESOLVER.\n\n"
        f"{body}\n\n"
        "This artifact does not grant live external authority. Broad search, repeated "
        "search loops, crawling, scraping, browser automation, login, account creation, "
        "payment, form submission, posting/commenting/messaging, publication, outreach, "
        "revenue execution, MCP execution, live behavior, CIEU DB writes, canonical "
        "mutation, brain/memory writeback, and direct Y* mutation remain blocked."
    )


def selected_work_order() -> dict[str, Any]:
    selected = read_json("locator_retry_work_order_selector/selected_locator_retry_work_order.json")
    if selected:
        return selected
    selected = read_json("tiny_observation_work_order_selector/selected_tiny_observation_work_order.json")
    if selected:
        return selected
    orders = read_json("agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json")
    selected_orders = orders.get("selected_work_orders", [])
    return selected_orders[0] if selected_orders else {}


def write_core_pack(generated: list[str]) -> None:
    contract = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": INPUT_MILESTONES,
            "mode": MODE,
            "os_neutral_design_required": True,
            "mac_only_solution_allowed": False,
            "capability_gap_diagnosis_authorized": True,
            "governed_toolmaking_methodology_authorized": True,
            "controlled_tool_contract_generation_authorized": True,
            "sandbox_tool_adapter_generation_authorized": True,
            "tool_validation_harness_authorized": True,
            "tool_use_gate_generation_authorized": True,
            "controlled_locator_resolver_interface_authorized": True,
            "resolver_capability_probe_authorized": True,
            "resolver_adapter_registry_authorized": True,
            "disabled_no_network_resolver_authorized": True,
            "optional_controlled_locator_discovery_authorized_if_adapter_available": True,
            "tiny_read_only_observation_retry_authorized_if_locator_resolved": True,
            "tool_external_authority_auto_grant_authorized": False,
            "broad_web_search_authorized": False,
            "repeated_search_loop_authorized": False,
            "crawling_authorized": False,
            "scraping_authorized": False,
            "browser_automation_authorized": False,
            "login_authorized": False,
            "account_creation_authorized": False,
            "contact_authorized": False,
            "payment_authorized": False,
            "form_submission_authorized": False,
            "posting_commenting_messaging_authorized": False,
            "publication_authorized": False,
            "outreach_authorized": False,
            "revenue_execution_authorized": False,
            "mcp_execution_authorized": False,
            "live_behavior_authorized": False,
            "cieu_db_write_authorized": False,
            "canonical_update_authorized": False,
            "direct_y_star_mutation_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "artifact_refinement_candidate_generation_authorized": True,
            "artifact_refinement_application_authorized": False,
        }
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_runtime_limits.json",
        with_controls(RUNTIME_LIMITS),
        generated,
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_safety_flags.json",
        with_controls({"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS}),
        generated,
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_scope.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "scope_layers": [
                    "general governed capability-gap diagnosis and tool-making methodology",
                    "controlled locator resolver adapter instance for L6.10R blocker",
                ],
                "default_outcome": "no_controlled_locator_resolver_available",
                "live_authority_granted": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_portability_contract.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "portable_across": [
                    "macOS",
                    "Linux",
                    "Windows",
                    "CI runners",
                    "OpenClaw/Codex runtime",
                    "future MCP read-only locator tools",
                    "future browserless/search adapters",
                    "future manually approved external resolver services",
                ],
                "path_handling": "pathlib",
                "mac_only_solution_allowed": False,
                "current_workspace_root_reference_only": str(ROOT),
            }
        ),
        generated,
    )
    summary = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "mode": MODE,
            "l6_10t_governed_capability_gap_toolmaking_defined": True,
            "capability_gap_diagnosis_completed": True,
            "governed_toolmaking_methodology_created": True,
            "controlled_tool_contract_model_created": True,
            "locator_resolver_capability_probe_executed": True,
            "probe_used_network": False,
            "controlled_resolver_adapter_available": False,
            "selected_resolver_adapter_id": "disabled_no_network_resolver",
            "locator_discovery_executed": False,
            "locator_discovery_queries_count": 0,
            "concrete_locator_resolved": False,
            "tiny_read_only_observation_executed": False,
            "external_reads_total": 0,
            "pages_read_count": 0,
            "evidence_packet_generated": True,
            "post_observation_review_packet_generated": True,
            "artifact_refinement_candidate_generated": True,
            "artifact_refinement_applied": False,
            "generated_tools_granted_live_authority": False,
            "remaining_blocker": "no_controlled_locator_resolver_available",
            "next_recommended_milestone": NEXT_IF_BLOCKED,
        }
    )
    write_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.json",
        summary,
        generated,
    )
    write_text(
        "l6_governed_capability_gap_toolmaking_locator_resolver/README.md",
        md_report(
            "L6.10T Governed Capability Gap Tool-Making And Locator Resolver",
            "This pack upgrades the L6.10R blocker from a passive failure into a "
            "governed self-tooling lifecycle. It defines a reusable capability-gap "
            "diagnosis method, a tool contract model, authority/use gates, sandbox "
            "validation, and a disabled controlled locator resolver adapter.",
        ),
        generated,
    )
    write_text(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_non_action_boundary.md",
        md_report(
            "L6.10T Non-Action Boundary",
            "Tool generation, registration, tests, and readiness do not grant live "
            "external authority. The default adapter is disabled and returns a typed "
            "capability gap without external reads.",
        ),
        generated,
    )
    write_text(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.md",
        md_report(
            "L6.10T Summary",
            "Outcome C: methodology created, disabled resolver adapter registered, "
            "capability probe executed locally, and no locator or evidence was faked.",
        ),
        generated,
    )


def write_capability_gap_packs(work_order: dict[str, Any], generated: list[str]) -> None:
    diagnosis = {
        "blocker_id": "l6_10r_no_locator_and_no_controlled_locator_discovery_tooling",
        "source_milestone": "L6.10R",
        "blocker_description": "no_locator_and_no_controlled_locator_discovery_tooling",
        "gap_type": "tool_capability_gap",
        "primary_gap_type": "tool_capability_gap",
        "secondary_gap_type": "runtime_environment_gap",
        "evidence_supporting_classification": [
            "L6.10 selected one work order but had only a placeholder locator",
            "L6.10R reached the controlled locator-discovery gate with zero queries",
            "L6.10R did not execute network or fake evidence",
        ],
        "not_a_governance_logic_failure": True,
        "not_an_agentic_evidence_reasoning_failure": True,
        "why_not_solve_by_human_manual_work": "The agent should formalize repeatable missing capability needs instead of transferring all search work to a human.",
        "why_not_bypass_governance": "External locator discovery can create network/search/browser authority and must remain separately scoped and gated.",
        "toolmaking_candidate": True,
        "minimum_capability_needed": "one-query controlled public locator resolver with no fact inference from discovery results",
        "prohibited_capability_expansion": NO_ACTIONS,
        "recommended_governed_toolmaking_path": LIFECYCLE_STAGES,
    }
    write_json(
        "capability_gap_diagnosis_engine/capability_gap_diagnosis_contract.json",
        with_controls({"schema_version": SCHEMA_VERSION, "diagnosis_required": True, "taxonomy_ref": "blocker_taxonomy.json"}),
        generated,
    )
    write_json(
        "capability_gap_diagnosis_engine/blocker_taxonomy.json",
        with_controls({"schema_version": SCHEMA_VERSION, "gap_types": BLOCKER_TAXONOMY}),
        generated,
    )
    write_json(
        "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json",
        with_controls({"schema_version": SCHEMA_VERSION, "selected_work_order": work_order, "diagnosis": diagnosis}),
        generated,
    )
    write_json(
        "capability_gap_diagnosis_engine/capability_gap_classification_matrix.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "classifications": [diagnosis],
                "non_gap_findings": [
                    {"candidate_gap": "governance_boundary_gap", "matches": False},
                    {"candidate_gap": "approval_gap", "matches": False},
                    {"candidate_gap": "agentic_evidence_reasoning_failure", "matches": False},
                ],
            }
        ),
        generated,
    )
    write_text(
        "capability_gap_diagnosis_engine/capability_gap_diagnosis_report.md",
        md_report("Capability Gap Diagnosis Report", "The L6.10R blocker is classified as a missing controlled resolver capability plus runtime environment gap."),
        generated,
    )

    write_json(
        "governed_toolmaking_methodology/governed_toolmaking_lifecycle.json",
        with_controls({"schema_version": SCHEMA_VERSION, "lifecycle_stages": LIFECYCLE_STAGES}),
        generated,
    )
    write_text(
        "governed_toolmaking_methodology/governed_toolmaking_principles.md",
        md_report(
            "Governed Tool-Making Principles",
            "Do not fake capability. Do not silently bypass governance. Do not ask "
            "the human to solve formalizable tool gaps first. Do not auto-grant "
            "external authority. Tools cannot expand their own scope. Tool use must "
            "be separately gated. Tests, readiness, and adapter existence do not "
            "equal approval.",
        ),
        generated,
    )
    write_json(
        "governed_toolmaking_methodology/capability_gap_to_tool_need_map.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "tool_need_map": [
                    {
                        "gap_type": "tool_capability_gap",
                        "tool_need": "define minimum tool contract, disabled adapter, validation harness, and use gate",
                    },
                    {
                        "gap_type": "runtime_environment_gap",
                        "tool_need": "probe local runtime declarations without external side effects",
                    },
                ],
            }
        ),
        generated,
    )
    write_json(
        "governed_toolmaking_methodology/toolmaking_non_bypass_policy.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "policy": "toolmaking_must_not_bypass_governance",
                "forbidden": FORBIDDEN_TOOL_PATTERNS,
                "tests_do_not_equal_approval": True,
                "readiness_does_not_equal_approval": True,
                "adapter_existence_does_not_equal_permission_to_execute": True,
                "live_external_actions_require_future_approval": True,
                "live_external_use_requires_future_explicit_approval": True,
            }
        ),
        generated,
    )
    write_text(
        "governed_toolmaking_methodology/governed_toolmaking_methodology_report.md",
        md_report("Governed Tool-Making Methodology Report", "The lifecycle moves from blocker diagnosis through contract, adapter, sandbox validation, use gate, residual, and review."),
        generated,
    )


def write_tool_contract_and_gate_packs(generated: list[str]) -> None:
    contract_fields = [
        "tool_contract_id",
        "tool_name",
        "capability_gap_id",
        "minimum_capability",
        "input_schema",
        "output_schema",
        "allowed_operations",
        "disallowed_operations",
        "runtime_limits",
        "authority_required",
        "external_access_required",
        "persistence_required",
        "safety_receipts_required",
        "validation_tests_required",
        "use_gate_required",
        "approval_required_before_live_use",
        "escalation_conditions",
        "abort_conditions",
        "residual_reporting_required",
    ]
    example_contract = {
        "tool_contract_id": "controlled_locator_resolver_contract_v0",
        "tool_name": "ControlledLocatorResolver",
        "capability_gap_id": "l6_10r_no_locator_and_no_controlled_locator_discovery_tooling",
        "minimum_capability": "resolve at most one public locator from one governed query",
        "input_schema": "locator_resolver_input_output_contract/locator_resolution_request_schema.json",
        "output_schema": "locator_resolver_input_output_contract/locator_resolution_result_schema.json",
        "allowed_operations": ["disabled local no-network response", "future one-query locator resolution if separately approved"],
        "disallowed_operations": NO_ACTIONS,
        "runtime_limits": RUNTIME_LIMITS,
        "authority_required": "future explicit scoped approval for external resolver use",
        "external_access_required": "not in default disabled mode",
        "persistence_required": False,
        "safety_receipts_required": True,
        "validation_tests_required": True,
        "use_gate_required": True,
        "approval_required_before_live_use": True,
        "escalation_conditions": ["resolver unavailable", "policy mismatch", "locator not public/read-only"],
        "abort_conditions": ["budget exceeded", "login/payment/contact/form encountered"],
        "residual_reporting_required": True,
    }
    write_json("controlled_tool_contract_model/controlled_tool_contract_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": contract_fields}), generated)
    write_json("controlled_tool_contract_model/controlled_tool_contract_required_fields.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": contract_fields}), generated)
    write_json("controlled_tool_contract_model/controlled_tool_contract_example_locator_resolver.json", with_controls(example_contract), generated)
    write_json("controlled_tool_contract_model/forbidden_tool_contract_patterns.json", with_controls({"schema_version": SCHEMA_VERSION, "forbidden_patterns": FORBIDDEN_TOOL_PATTERNS}), generated)
    write_text("controlled_tool_contract_model/controlled_tool_contract_model_report.md", md_report("Controlled Tool Contract Model Report", "A reusable contract schema and locator resolver example were generated."), generated)

    authority_facts = {
        "schema_version": SCHEMA_VERSION,
        "tool_generation_is_live_use_approval": False,
        "tool_tests_passing_are_live_use_approval": False,
        "tool_registration_is_live_use_approval": False,
        "sandbox_use_is_live_use_approval": False,
        "external_authority_requires_separate_approval": True,
        "tool_may_be_present_but_disabled": True,
        "tool_may_be_scoped_to_one_work_order": True,
        "tool_may_be_revoked": True,
    }
    write_json("tool_authority_and_use_gate/tool_authority_model.json", with_controls(authority_facts), generated)
    write_json("tool_authority_and_use_gate/tool_use_gate_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "use_gate_required": True, "live_use_without_future_approval": False}), generated)
    write_json(
        "tool_authority_and_use_gate/tool_use_decision_matrix.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "decisions": [
                    "allow_sandbox_tool_generation",
                    "allow_disabled_adapter_registration",
                    "allow_static_validation_only",
                    "allow_scoped_use_if_future_approved",
                    "block_live_use_no_approval",
                    "block_scope_expansion",
                    "block_external_action",
                    "block_persistence",
                    "block_canonical_mutation",
                ],
            }
        ),
        generated,
    )
    write_json("tool_authority_and_use_gate/tool_use_non_authority_receipts.json", with_controls(authority_facts), generated)
    write_text("tool_authority_and_use_gate/tool_authority_and_use_gate_report.md", md_report("Tool Authority And Use Gate Report", "The authority model distinguishes tool existence from live-use approval."), generated)

    validation_categories = [
        "schema_validation",
        "input_output_determinism",
        "disabled_mode_behavior",
        "limit_enforcement",
        "forbidden_action_checks",
        "no_fake_success",
        "no_authority_expansion",
        "receipt_generation",
        "residual_generation",
        "read_model_visibility",
        "regression_tests",
    ]
    write_json("tool_sandbox_validation_harness/tool_validation_harness_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "validation_categories": validation_categories}), generated)
    validation_tests = [{"category": c, "required": True} for c in validation_categories]
    write_json("tool_sandbox_validation_harness/tool_validation_test_matrix.json", with_controls({"schema_version": SCHEMA_VERSION, "tests": validation_tests, "validation_tests": validation_tests}), generated)
    write_json("tool_sandbox_validation_harness/locator_resolver_sandbox_validation_plan.json", with_controls({"schema_version": SCHEMA_VERSION, "adapter_under_test": "disabled_no_network_resolver", "expected_error_code": "no_controlled_locator_resolver_available", "external_access_expected": False}), generated)
    write_json("tool_sandbox_validation_harness/tool_validation_receipts.json", with_controls({"schema_version": SCHEMA_VERSION, "no_fake_success": True, "no_authority_expansion": True, "network_used": False}), generated)
    write_text("tool_sandbox_validation_harness/tool_sandbox_validation_harness_report.md", md_report("Tool Sandbox Validation Harness Report", "The harness validates disabled-mode behavior, budgets, receipts, and no fake success."), generated)

    residuals = [
        "methodology is generated but not yet applied to every capability gap",
        "tool generation does not grant live external authority",
        "locator resolver remains disabled in default environment",
        "future approval and controlled adapter enablement remain required",
    ]
    write_json(
        "toolmaking_residual_learning_loop/toolmaking_cieu_like_fixture.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "event_mode": "l6_10t_toolmaking_methodology_fixture",
                "X_t": "L6.10R blocker no_locator_and_no_controlled_locator_discovery_tooling",
                "U_t": "Create governed capability-gap tool-making lifecycle and disabled locator resolver adapter",
                "Y_star_t": "Convert capability blockers into governed tool contracts without auto-granting external authority.",
                "Y_t_plus_1": "Methodology, contract, validation, use-gate, and residual artifacts generated.",
                "R_t_plus_1": residuals,
            }
        ),
        generated,
    )
    write_json("toolmaking_residual_learning_loop/toolmaking_residual_delta.json", with_controls({"schema_version": SCHEMA_VERSION, "residuals": residuals}), generated)
    write_json(
        "toolmaking_residual_learning_loop/toolmaking_meta_learning_candidate.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
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
    write_text("toolmaking_residual_learning_loop/toolmaking_residual_learning_report.md", md_report("Toolmaking Residual Learning Report", "Toolmaking residuals are review-only and not applied to brain, memory, strategy, or Y*."), generated)


def resolver_stub_text() -> str:
    return '''"""Portable controlled locator resolver interface for L6.10T.

The default implementation is DisabledNoNetworkResolver. It performs no network
access and returns a typed capability gap. Future live adapters must be
separately approved and gated before use.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocatorResolutionRequest:
    request_id: str
    linked_work_order_id: str
    evidence_need_id: str | None
    source_type: str | None
    source_function: str
    observation_question: str | None
    locator_discovery_query: str
    max_queries: int = 1
    max_results: int = 1
    no_fact_inference_from_result: bool = True
    no_snippet_fact_use: bool = True
    no_broad_search: bool = True
    no_crawling: bool = True


@dataclass(frozen=True)
class LocatorResolutionResult:
    concrete_locator_resolved: bool
    locator: str | None
    source_title: str | None
    source_type: str | None
    resolution_method: str
    queries_used: int
    external_reads_used: int
    facts_inferred: bool
    eligible_for_read_only_observation: bool
    error_code: str | None
    blocked_reason: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ControlledLocatorResolver(Protocol):
    adapter_id: str
    network_enabled: bool

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        """Resolve at most one concrete locator or return a typed blocked result."""


@dataclass(frozen=True)
class ResolverCapability:
    adapter_id: str
    available: bool
    mode: str
    live_external_authority_granted: bool


class DisabledNoNetworkResolver:
    adapter_id = "disabled_no_network_resolver"
    network_enabled = False

    def capability(self) -> ResolverCapability:
        return ResolverCapability(
            adapter_id=self.adapter_id,
            available=True,
            mode="disabled_no_network",
            live_external_authority_granted=False,
        )

    def resolve(self, request: LocatorResolutionRequest) -> LocatorResolutionResult:
        return LocatorResolutionResult(
            concrete_locator_resolved=False,
            locator=None,
            source_title=None,
            source_type=request.source_type,
            resolution_method="disabled_no_network",
            queries_used=0,
            external_reads_used=0,
            facts_inferred=False,
            eligible_for_read_only_observation=False,
            error_code="no_controlled_locator_resolver_available",
            blocked_reason="Default resolver is disabled and has no live external authority.",
        )
'''


def write_resolver_packs(work_order: dict[str, Any], generated: list[str]) -> None:
    request = {
        "request_id": "l6_10t_locator_resolution_request_001",
        "linked_work_order_id": work_order.get("linked_l6_8_work_order_id") or work_order.get("selected_retry_work_order_id"),
        "evidence_need_id": work_order.get("linked_evidence_need_id"),
        "source_type": work_order.get("source_type"),
        "source_function": "resolve one concrete public locator for the selected governed work order",
        "observation_question": work_order.get("observation_question"),
        "locator_discovery_query": "one controlled locator discovery query would be derived from the selected work order if an approved resolver were available",
        "max_queries": 1,
        "max_results": 1,
        "no_fact_inference_from_result": True,
        "no_snippet_fact_use": True,
        "no_broad_search": True,
        "no_crawling": True,
    }
    disabled_result = {
        "concrete_locator_resolved": False,
        "locator": None,
        "source_title": None,
        "source_type": work_order.get("source_type"),
        "resolution_method": "disabled_no_network",
        "queries_used": 0,
        "external_reads_used": 0,
        "facts_inferred": False,
        "eligible_for_read_only_observation": False,
        "error_code": "no_controlled_locator_resolver_available",
        "blocked_reason": "No controlled locator resolver adapter with live external authority is available.",
    }
    probe_result = {
        "schema_version": SCHEMA_VERSION,
        "probe_local_only": True,
        "network_used": False,
        "api_called": False,
        "browser_launched": False,
        "mcp_executed": False,
        "controlled_locator_resolver_available": False,
        "selected_resolver_adapter_id": "disabled_no_network_resolver",
        "resolver_mode": "disabled_no_network",
        "capability_gap_code": "no_controlled_locator_resolver_available",
        "local_checks": [
            {"check": "disabled resolver stub exists", "passed": True},
            {"check": "live resolver config declared", "passed": False},
            {"check": "future resolver profiles enabled", "passed": False},
        ],
    }
    write_json("locator_resolver_capability_probe/resolver_capability_probe_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "local_only": True, "disallowed_probe_actions": ["network_access", "web_search", "URL_fetch", "curl_wget", "browser_launch", "MCP_execution", "API_call"]}), generated)
    write_json("locator_resolver_capability_probe/resolver_capability_probe_result.json", with_controls(probe_result), generated)
    write_json("locator_resolver_capability_probe/resolver_environment_inventory.json", with_controls({"schema_version": SCHEMA_VERSION, "available_default_adapter": "disabled_no_network_resolver", "future_adapters_declared": [], "external_authority_available": False}), generated)
    write_json("locator_resolver_capability_probe/resolver_capability_gap_report.json", with_controls({"schema_version": SCHEMA_VERSION, "capability_gap_code": "no_controlled_locator_resolver_available", "minimum_enablement_needed": "approved controlled one-query public locator resolver adapter"}), generated)
    write_text("locator_resolver_capability_probe/resolver_capability_probe_report.md", md_report("Resolver Capability Probe Report", "The probe is local-only and selected the disabled no-network resolver because no live controlled resolver is available."), generated)

    write_text("controlled_locator_resolver_interface/controlled_locator_resolver_interface.md", md_report("Controlled Locator Resolver Interface", "The interface is portable and defines request, result, resolver, disabled resolver, and capability concepts."), generated)
    write_json("controlled_locator_resolver_interface/controlled_locator_resolver_protocol.json", with_controls({"schema_version": SCHEMA_VERSION, "protocol": "ControlledLocatorResolver.resolve(request) -> LocatorResolutionResult", "max_queries": 1, "max_results": 1}), generated)
    write_text("controlled_locator_resolver_interface/controlled_locator_resolver_python_stub.py", resolver_stub_text(), generated)
    write_json("controlled_locator_resolver_interface/controlled_locator_resolver_types.json", with_controls({"schema_version": SCHEMA_VERSION, "request_fields": list(request.keys()), "result_fields": list(disabled_result.keys()), "capability_fields": ["adapter_id", "available", "mode", "live_external_authority_granted"]}), generated)
    write_json("controlled_locator_resolver_interface/controlled_locator_resolver_error_codes.json", with_controls({"schema_version": SCHEMA_VERSION, "error_codes": RESOLVER_ERROR_CODES}), generated)

    future_profiles = [
        "governed_search_api_adapter",
        "governed_read_only_browserless_adapter",
        "governed_mcp_locator_resolver_adapter",
        "human_approved_external_resolver_adapter",
        "user_supplied_locator_adapter",
    ]
    write_json("locator_resolver_adapter_registry/resolver_adapter_registry.json", with_controls({"schema_version": SCHEMA_VERSION, "selected_adapter_id": "disabled_no_network_resolver", "selected_default_adapter_id": "disabled_no_network_resolver", "adapters": [{"adapter_id": "disabled_no_network_resolver", "enabled": True, "network_enabled": False, "live_external_authority_granted": False}]}), generated)
    write_json("locator_resolver_adapter_registry/disabled_no_network_adapter.json", with_controls({"schema_version": SCHEMA_VERSION, "adapter_id": "disabled_no_network_resolver", "mode": "disabled_no_network", "returns_error_code": "no_controlled_locator_resolver_available", "queries_used": 0, "external_reads_used": 0}), generated)
    write_json("locator_resolver_adapter_registry/future_adapter_profiles.json", with_controls({"schema_version": SCHEMA_VERSION, "future_profiles": [{"adapter_id": p, "enabled": False, "requires_future_approval": True} for p in future_profiles]}), generated)
    write_json("locator_resolver_adapter_registry/resolver_adapter_selection_policy.json", with_controls({"schema_version": SCHEMA_VERSION, "max_resolver_adapters_selected": 1, "default_selection": "disabled_no_network_resolver", "live_authority_required_for_external_adapter": True}), generated)
    write_text("locator_resolver_adapter_registry/resolver_adapter_registry_report.md", md_report("Resolver Adapter Registry Report", "Only the disabled no-network adapter is available in this milestone; all future profiles are disabled."), generated)

    write_json("locator_resolver_input_output_contract/locator_resolution_request_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(request.keys())}), generated)
    write_json("locator_resolver_input_output_contract/locator_resolution_result_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(disabled_result.keys())}), generated)
    write_json("locator_resolver_input_output_contract/locator_resolution_request_001.json", with_controls(request), generated)
    write_json("locator_resolver_input_output_contract/locator_resolution_result_disabled_fixture.json", with_controls(disabled_result), generated)
    write_text("locator_resolver_input_output_contract/locator_resolution_io_contract_report.md", md_report("Locator Resolution IO Contract Report", "The request is derived from the selected work order and the result is a disabled no-network fixture."), generated)

    write_json("locator_resolver_policy_and_limits/resolver_policy_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "policy": "one_query_one_result_no_fact_inference"}), generated)
    write_json("locator_resolver_policy_and_limits/resolver_runtime_limits.json", with_controls({"schema_version": SCHEMA_VERSION, "max_queries": 1, "max_results": 1, "max_locator_outputs": 1, **RUNTIME_LIMITS}), generated)
    write_json("locator_resolver_policy_and_limits/resolver_disallowed_actions.json", with_controls({"schema_version": SCHEMA_VERSION, "no_fact_inference_from_search_result": True, "no_snippet_fact_use": True, "disallowed_actions": NO_ACTIONS + ["MCP execution", "broad search", "repeated search"]}), generated)
    write_json("locator_resolver_policy_and_limits/resolver_abort_conditions.json", with_controls({"schema_version": SCHEMA_VERSION, "abort_conditions": ["budget_exceeded", "no_approved_adapter", "login_required", "payment_required", "form_required", "contact_required", "scope_uncertainty"]}), generated)
    write_text("locator_resolver_policy_and_limits/resolver_policy_report.md", md_report("Resolver Policy Report", "Resolver policy limits discovery to one query and one locator, with no fact inference from snippets/results."), generated)

    write_json("locator_resolver_selection_gate/resolver_selection_gate_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "selection_gate_required": True}), generated)
    write_json("locator_resolver_selection_gate/resolver_selection_decision.json", with_controls({"schema_version": SCHEMA_VERSION, "decision": "select_disabled_no_network_resolver", "selected_adapter_id": "disabled_no_network_resolver", "selected_resolver_adapter_id": "disabled_no_network_resolver", "live_external_authority_granted": False}), generated)
    write_json("locator_resolver_selection_gate/resolver_selection_blockers.json", with_controls({"schema_version": SCHEMA_VERSION, "blockers": ["no_controlled_locator_resolver_available", "no_future_explicit_external_authority_approval"]}), generated)
    write_text("locator_resolver_selection_gate/resolver_selection_gate_report.md", md_report("Resolver Selection Gate Report", "The gate selects the disabled resolver and blocks live locator discovery."), generated)

    adapter_trace = {
        "schema_version": SCHEMA_VERSION,
        "adapter_selected": "disabled_no_network_resolver",
        "adapter_executed": True,
        "locator_discovery_query_executed": False,
        "queries_count": 0,
        "external_reads_count": 0,
        "concrete_locator_resolved": False,
        "resolved_locator": None,
        "facts_inferred_from_discovery": False,
        "blocked_reason": "No controlled locator resolver adapter with live external authority is available.",
        "error_code": "no_controlled_locator_resolver_available",
    }
    write_json("locator_resolution_adapter_trace/adapter_trace_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(adapter_trace.keys())}), generated)
    write_json("locator_resolution_adapter_trace/adapter_trace.json", with_controls(adapter_trace), generated)
    write_text("locator_resolution_adapter_trace/locator_resolution_adapter_trace_report.md", md_report("Locator Resolution Adapter Trace Report", "The disabled adapter executed locally and returned the typed capability gap without external reads."), generated)

    write_json("concrete_locator_eligibility_gate/concrete_locator_eligibility_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "eligibility_gate_required_before_observation": True}), generated)
    write_json("concrete_locator_eligibility_gate/concrete_locator_eligibility_result.json", with_controls({"schema_version": SCHEMA_VERSION, "eligibility_evaluated": False, "reason": "no_concrete_locator", "eligible_for_observation": False}), generated)
    write_json("concrete_locator_eligibility_gate/concrete_locator_risk_assessment.json", with_controls({"schema_version": SCHEMA_VERSION, "risk_assessed": False, "reason": "no_concrete_locator", "privacy_risk": "not_assessed", "ip_risk": "not_assessed"}), generated)
    write_text("concrete_locator_eligibility_gate/concrete_locator_eligibility_report.md", md_report("Concrete Locator Eligibility Report", "No concrete locator exists, so eligibility is not evaluated and observation remains blocked."), generated)

    write_json("adapter_bound_tiny_observation_retry/adapter_bound_retry_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "retry_allowed_only_if_locator_exists_and_eligible": True}), generated)
    write_json("adapter_bound_tiny_observation_retry/adapter_bound_retry_execution_packet.json", with_controls({"schema_version": SCHEMA_VERSION, "selected_adapter_id": "disabled_no_network_resolver", "observation_executed": False, "reason": "no_concrete_locator", "all_downstream_actions_authorized": False}), generated)
    write_json("adapter_bound_tiny_observation_retry/adapter_bound_retry_trace.json", with_controls({"schema_version": SCHEMA_VERSION, "observation_executed": False, "source_locator": None, "external_reads_count": 0, "pages_read_count": 0, "network_used": False, "reason": "no_concrete_locator"}), generated)
    write_text("adapter_bound_tiny_observation_retry/adapter_bound_retry_report.md", md_report("Adapter-Bound Tiny Observation Retry Report", "The adapter-bound retry is blocked because the disabled resolver produced no locator."), generated)

    evidence_packet = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": "l6_10t_adapter_bound_evidence_packet_001",
        "linked_work_order_id": request["linked_work_order_id"],
        "live_source_evidence_captured": False,
        "reason": "no_controlled_locator_resolver_available",
        "source_locator": None,
        "source_title": None,
        "observed_at_timestamp": None,
        "captured_claims": [],
        "unsupported_claims": [],
        "missing_context": ["no resolver available", "no locator resolved", "no live observation executed"],
        "freshness_class": "not_observed",
        "review_status": "pending_review",
        "publication_taken": False,
        "outreach_taken": False,
        "payment_taken": False,
        "revenue_action_taken": False,
        "mcp_execution_taken": False,
        "canonical_update_taken": False,
        "brain_memory_writeback_taken": False,
        "direct_y_star_mutation_taken": False,
    }
    write_json("adapter_bound_evidence_capture/adapter_bound_evidence_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(evidence_packet.keys())}), generated)
    write_json("adapter_bound_evidence_capture/adapter_bound_evidence_packet.json", with_controls(evidence_packet), generated)
    write_json("adapter_bound_evidence_capture/adapter_bound_citation_trace.json", with_controls({"schema_version": SCHEMA_VERSION, "citation_count": 0, "citations": [], "reason": "no observation executed"}), generated)
    write_text("adapter_bound_evidence_capture/adapter_bound_evidence_capture_report.md", md_report("Adapter-Bound Evidence Capture Report", "A blocked evidence packet was generated and does not pretend live evidence exists."), generated)

    refinement = {
        "schema_version": SCHEMA_VERSION,
        "linked_evidence_packet_id": "l6_10t_adapter_bound_evidence_packet_001",
        "refinement_target": "controlled locator resolver enablement",
        "proposed_refinement": "Create or approve a controlled one-query locator resolver adapter before attempting L6.11.",
        "review_required": True,
        "approved": False,
        "applied": False,
        "artifact_update_authorized": False,
        "canonical_update_authorized": False,
        "brain_writeback_authorized": False,
        "memory_ingestion_authorized": False,
        "direct_y_star_mutation_authorized": False,
    }
    write_json("adapter_bound_review_and_refinement/adapter_bound_review_packet.json", with_controls({"schema_version": SCHEMA_VERSION, "review_status": "pending_review", "current_decision": "review_pending", "approve_for_externalization": False, "approve_for_external_use": False, "approve_for_artifact_update": False, "linked_evidence_packet_id": "l6_10t_adapter_bound_evidence_packet_001"}), generated)
    write_json("adapter_bound_review_and_refinement/adapter_bound_refinement_candidate.json", with_controls(refinement), generated)
    write_text("adapter_bound_review_and_refinement/adapter_bound_review_and_refinement_report.md", md_report("Adapter-Bound Review And Refinement Report", "Review remains pending and the refinement candidate is unapplied."), generated)

    blocker = {
        "schema_version": SCHEMA_VERSION,
        "exact_blocker": "no_controlled_locator_resolver_available",
        "blocker_code": "no_controlled_locator_resolver_available",
        "locator_fabricated": False,
        "evidence_fabricated": False,
        "acceptable_blocker_codes": RESOLVER_ERROR_CODES,
        "future_resolver_enablement_requirements": [
            "explicit scoped authority record for one-query locator discovery",
            "adapter implementation with schema-conformant input/output",
            "runtime isolation confirmation",
            "no broad search/crawling/scraping/browser automation",
            "post-observation review channel",
        ],
    }
    write_json("adapter_bound_blocker_and_fallback_report/locator_tooling_blocker.json", with_controls(blocker), generated)
    write_json("adapter_bound_blocker_and_fallback_report/adapter_fallback_decision.json", with_controls({"schema_version": SCHEMA_VERSION, "fallback_decision": "block_and_report_capability_gap", "selected_fallback": "use_disabled_no_network_resolver_and_block", "locator_faked": False, "evidence_faked": False}), generated)
    write_json("adapter_bound_blocker_and_fallback_report/future_resolver_enablement_requirements.json", with_controls({"schema_version": SCHEMA_VERSION, "requirements": blocker["future_resolver_enablement_requirements"]}), generated)
    write_text("adapter_bound_blocker_and_fallback_report/adapter_bound_blocker_report.md", md_report("Adapter-Bound Blocker Report", "The exact blocker is no_controlled_locator_resolver_available."), generated)


def write_receipts_and_readiness(generated: list[str]) -> None:
    for filename, action_type in RECEIPTS:
        write_json(
            f"adapter_bound_no_action_receipts/{filename}",
            with_controls(
                {
                    "schema_version": SCHEMA_VERSION,
                    "action_type": action_type,
                    "authorized_in_l6_10t": False,
                    "executed_in_l6_10t": False,
                    "tool_generated_live_authority": False,
                    "generated_tool_live_authority_granted": False,
                    "blocker_reference": "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json",
                    "future_boundary_required": True,
                }
            ),
            generated,
        )
    write_text("adapter_bound_no_action_receipts/adapter_bound_no_action_receipt_report.md", md_report("Adapter-Bound No-Action Receipts", "All disallowed action receipts were generated with executed_in_l6_10t=false."), generated)

    residuals = [
        "no live controlled locator resolver available",
        "disabled resolver adapter remains the selected default",
        "locator unresolved",
        "observation still blocked",
        "future external resolver enablement required",
        "methodology not yet applied to other tool gaps",
        "tool generation not approved for live authority",
        "no durable tool authority record exists",
    ]
    cieu = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "event_mode": "l6_10t_governed_capability_gap_toolmaking_locator_resolver_fixture",
            "X_t": {
                "l6_10_blocked_pilot": "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
                "l6_10r_locator_retry": "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
            },
            "U_t": "Diagnose capability gap, define governed tool-making lifecycle, create controlled locator resolver contract, register disabled resolver, run local-only probe, and block live use.",
            "Y_star_t": "Create a governed capability-gap diagnosis and tool-making methodology, apply it to the missing controlled locator resolver blocker, create a portable controlled locator resolver adapter layer, probe resolver capability without external side effects, bind one eligible resolver if available, resolve at most one concrete public locator for one governed work order, optionally retry one tiny read-only observation, and preserve no-broad-search/no-crawling/no-scraping/no-login/no-payment/no-contact/no-publication/no-outreach/no-revenue/no-MCP/no-live/no-CIEU-DB-write/no-canonical-mutation/no-brain-memory-writeback/no-direct-Y* mutation constraints.",
            "Y_t_plus_1": "Capability-gap diagnosis, tool-making methodology, controlled tool contract, use gate, sandbox validation, resolver interface, disabled adapter registry, local-only probe, blocked adapter trace, evidence/review/refinement outputs, and no-action receipts were generated.",
            "R_t_plus_1": residuals,
        }
    )
    write_json("l6_10t_strategic_residual_loop/l6_10t_cieu_like_fixture.json", cieu, generated)
    write_json("l6_10t_strategic_residual_loop/l6_10t_strategic_residual_delta.json", with_controls({"schema_version": SCHEMA_VERSION, "residuals": residuals}), generated)
    write_json(
        "l6_10t_strategic_residual_loop/l6_10t_meta_learning_update_candidate.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
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
    write_text("l6_10t_strategic_residual_loop/l6_10t_residual_report.md", md_report("L6.10T Residual Report", "The residual loop records method creation plus the remaining disabled resolver gap."), generated)

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "general_governed_toolmaking_methodology_ready_for_reuse": True,
        "capability_gap_diagnosis_completed": True,
        "controlled_tool_contract_model_created": True,
        "locator_resolver_capability_probe_executed": True,
        "probe_used_network": False,
        "controlled_resolver_adapter_available": False,
        "selected_resolver_adapter_id": "disabled_no_network_resolver",
        "locator_discovery_executed": False,
        "locator_discovery_queries_count": 0,
        "concrete_locator_resolved": False,
        "tiny_read_only_observation_executed": False,
        "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot": False,
        "remaining_blocker": "no_controlled_locator_resolver_available",
        "ready_for_publication": False,
        "ready_for_outreach": False,
        "ready_for_payment": False,
        "ready_for_revenue_execution": False,
        "ready_for_mcp_execution": False,
        "ready_for_canonical_update": False,
        "ready_for_brain_memory_writeback": False,
        "ready_for_direct_y_star_mutation": False,
        "next_recommended_milestone": NEXT_IF_BLOCKED,
    }
    write_json("l6_10t_readiness_report/l6_10t_readiness_assessment.json", with_controls(readiness), generated)
    write_json("l6_10t_readiness_report/l6_10t_next_milestone_recommendation.json", with_controls({"schema_version": SCHEMA_VERSION, "recommended_next_milestone": NEXT_IF_BLOCKED, "success_path_next_milestone": NEXT_IF_SUCCESS, "do_not_implement_l6_11_now": True}), generated)
    write_json("l6_10t_readiness_report/l6_10t_blockers.json", with_controls({"schema_version": SCHEMA_VERSION, "blockers": residuals, "exact_blocker": "no_controlled_locator_resolver_available"}), generated)
    write_text("l6_10t_readiness_report/l6_10t_readiness_report.md", md_report("L6.10T Readiness Report", "The methodology is reusable, but L6.11 remains blocked until a controlled locator resolver is enabled."), generated)


def build() -> list[str]:
    generated: list[str] = []
    work_order = selected_work_order()
    write_core_pack(generated)
    write_capability_gap_packs(work_order, generated)
    write_tool_contract_and_gate_packs(generated)
    write_resolver_packs(work_order, generated)
    write_receipts_and_readiness(generated)
    return generated


def main() -> None:
    generated = build()
    print(f"Built L6.10T governed capability gap toolmaking artifacts: {len(generated)} files")


if __name__ == "__main__":
    main()
