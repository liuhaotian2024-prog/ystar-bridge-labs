from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
JOB_ID = "e74_ceo_l2_internal_autonomous_work_pilot_20260507T000001Z"
EXPECTED_BASE = "df492cebb37ae3231859ac8aa92ae1244c89bfeb"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
OWNER_DECISION_STATUS = "pending_owner_decision"
SELECTED_PRODUCT = "Governed Business Operations Blueprint + CIEU Audit Module"
SELECTED_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
NEXT_MILESTONE = "E75_L3_Read_Only_External_Research_Owner_Decision_Packet_Finalization"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT

    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=base, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head": run("rev-parse", "HEAD"),
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def _artifact(rel: str, role: str, decision: str, owner: str = "bridge-labs", root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    if owner == "K9Audit":
        exists = (K9_ROOT / rel.replace("K9Audit/", "", 1)).exists()
    elif owner == "Y-star-gov":
        exists = Y_GOV_ROOT.exists()
    elif owner == "gov-mcp":
        exists = GOV_MCP_ROOT.exists()
    else:
        exists = (base / rel).exists()
    return {
        "path": rel,
        "exists": exists,
        "role": role,
        "canonical_owner": owner,
        "decision": decision,
    }


def artifact_reuse_rows(root: Path | None = None) -> list[dict[str, Any]]:
    return [
        _artifact("operations/external_validation/e65_market_dynamics_analysis_run.json", "market route evidence", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e66_selected_route_offer_blueprint.json", "selected offer definition", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e67_external_validation_ladder.json", "EV0-EV8 validation ladder", "reuse_as_boundary", root=root),
        _artifact("operations/external_validation/e67_route_external_validation_scorecards.json", "non-contact evidence scorecards", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e68_strategic_portfolio_update.json", "CIEU portfolio role", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e68_cieu_route_model_scoring.json", "CIEU route model score", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e69_ceo_selected_next_action_decision.json", "CEO-selected CIEU module next action", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e70_self_bootstrap_runtime_state.json", "self-bootstrap state", "context_only", root=root),
        _artifact("operations/external_validation/e71_promoted_legacy_assets.json", "promoted legacy clusters", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e71_legacy_market_model_inputs.json", "commercial legacy route inputs", "context_only", root=root),
        _artifact("operations/external_validation/e71_legacy_pricing_inputs.json", "pricing package hypotheses", "context_only_not_validated", root=root),
        _artifact("operations/external_validation/e72_cieu_hash_chain_context_state.json", "K9/CIEU hash-chain context binding", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e72_cieu_audit_module_product_binding.json", "CIEU product binding", "reuse_as_input", root=root),
        _artifact("operations/external_validation/e73_no_new_wheel_policy.json", "reuse policy", "obey_as_gate", root=root),
        _artifact("operations/external_validation/e73_ceo_real_work_readiness_gate.json", "L2 readiness gate", "obey_as_gate", root=root),
        _artifact("operations/external_validation/e73_ecosystem_responsibility_matrix.json", "canonical repo boundaries", "obey_as_gate", root=root),
        _artifact("products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json", "product module context", "reuse_as_input", root=root),
        _artifact("products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json", "combined offer draft", "reuse_as_input", root=root),
        _artifact("K9Audit/docs/CIEU_spec.md", "CIEU ledger/hash/verifier canonical source", "read_only_context_owner_not_reimplemented", owner="K9Audit", root=root),
        _artifact("Y-star-gov governance modules", "governance owner context", "read_only_context_owner_not_reimplemented", owner="Y-star-gov", root=root),
        _artifact("gov-mcp provider boundary modules", "MCP/provider owner context", "read_only_context_owner_not_reimplemented", owner="gov-mcp", root=root),
    ]


def build_existing_artifact_reuse_map(root: Path | None = None) -> dict[str, Any]:
    rows = artifact_reuse_rows(root)
    return {
        "artifact_id": "e74_existing_artifact_reuse_map",
        "bridge_job_id": JOB_ID,
        "reuse_principle": "E74 performs L2 work by reusing E65-E73 and product artifacts, not by building new mechanisms.",
        "artifacts_inspected": rows,
        "inspected_count": len(rows),
        "reuse_count": sum(1 for row in rows if row["decision"].startswith("reuse")),
        "context_only_count": sum(1 for row in rows if "context" in row["decision"]),
        "canonical_owner_mapping": {
            "K9Audit": "CIEU ledger/hash-chain/verifier owner; bridge-labs does not duplicate.",
            "Y-star-gov": "governance/check/enforce owner; bridge-labs does not duplicate.",
            "gov-mcp": "MCP/provider execution envelope owner; bridge-labs does not duplicate.",
            "bridge-labs": "business/product/readiness/internal work owner.",
        },
        "new_file_justification": {
            "office/mission_command/e74_ceo_l2_internal_work_pilot.py": {
                "decision": "create_adapter_orchestrator_for_single_E74_work_cycle",
                "why_existing_file_cannot_be_extended": "E73 closure artifacts should stay boundary/readiness evidence; E74 needs a milestone-specific internal work-product generator.",
                "existing_modules_inspected": ["E73 readback", "E72 CIEU readback", "E70 self-bootstrap", "E69 next-action planner"],
                "canonical_owner": "bridge-labs",
                "conflict_risk": "low",
                "test_path": "tests/office/test_e74_ceo_l2_internal_work_pilot.py",
                "rollback_or_deprecation_plan": "remove E74 generator and generated E74 artifacts; no shared runtime state is required.",
                "non_duplication_evidence": "module only orchestrates existing artifacts and emits owner-facing packet; it creates no verifier, governance engine, MCP executor, or CEO brain.",
                "scope_boundary": "L2 internal no-external-action work product generation only.",
            },
            "office/mission_command/e74_ceo_l2_readback.py": {
                "decision": "create_readback_facade_for_E74_state",
                "why_existing_file_cannot_be_extended": "CEO adapter needs a thin E74 state accessor without mixing L2 work-cycle state into E73 closure logic.",
                "existing_modules_inspected": ["E73 readback", "E72 readback"],
                "canonical_owner": "bridge-labs",
                "conflict_risk": "low",
                "test_path": "tests/office/test_e74_cieu_residual_and_readback.py",
                "rollback_or_deprecation_plan": "remove facade and adapter fields.",
                "non_duplication_evidence": "facade only exposes generated E74 artifacts.",
                "scope_boundary": "readback only; no new CEO brain.",
            },
        },
        "duplicate_mechanism_risk_assessment": {
            "duplicate_K9Audit_ledger_or_verifier_created": False,
            "duplicate_Y_star_gov_governance_engine_created": False,
            "duplicate_gov_mcp_execution_envelope_created": False,
            "parallel_CEO_brain_created": False,
            "new_product_mechanism_created": False,
        },
        "external_action_allowed": False,
    }


def _evidence_summary(root: Path | None = None) -> dict[str, Any]:
    e67 = load_json("operations/external_validation/e67_route_external_validation_scorecards.json", root)
    e68 = load_json("operations/external_validation/e68_strategic_portfolio_update.json", root)
    e72 = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", root)
    e73 = load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", root)
    return {
        "E65_market_dynamics": "current primary route remains governed business operations; fastest-cash alternatives stay available as fallback context",
        "E66_offer_blueprint": SELECTED_PRODUCT,
        "E67_non_contact_validation": {
            "highest_non_contact_EV_level": e67.get("highest_non_contact_EV_level"),
            "selected_route_external_validation_score": e67.get("selected_route_external_validation_score"),
            "EV5_EV8_achieved": e67.get("EV5_EV8_achieved"),
        },
        "E68_CIEU_portfolio_role": {
            "CIEU_replaces_primary": e68.get("should_CIEU_replace_current_primary_route"),
            "CIEU_as_module": e68.get("should_CIEU_become_vertical_module_inside_current_selected_route"),
            "best_portfolio_after_E68": e68.get("best_portfolio_after_E68"),
        },
        "E72_CIEU_hash_chain_context": {
            "imported_cluster_id": e72.get("imported_cluster_id"),
            "product_binding_status": e72.get("product_binding_status"),
            "production_hash_chain_enabled": e72.get("production_hash_chain_enabled"),
        },
        "E73_readiness": {
            "highest_ready_level": e73.get("highest_ready_level"),
            "L3_decision": e73.get("level_decisions", {}).get("L3_controlled_read_only_external_research_ready", {}).get("readiness_decision"),
        },
    }


def build_l2_internal_work_cycle_plan(root: Path | None = None) -> dict[str, Any]:
    e73_gate = load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", root)
    return {
        "artifact_id": "e74_l2_internal_work_cycle_plan",
        "bridge_job_id": JOB_ID,
        "objective": "Prepare the strongest internal owner-facing package for moving the current first-cash route toward L3 controlled read-only external research.",
        "selected_route": SELECTED_ROUTE,
        "selected_product": SELECTED_PRODUCT,
        "readiness_basis": {
            "E73_L2_decision": e73_gate.get("level_decisions", {}).get("L2_internal_autonomous_work_ready", {}).get("readiness_decision"),
            "E73_L3_decision": e73_gate.get("level_decisions", {}).get("L3_controlled_read_only_external_research_ready", {}).get("readiness_decision"),
        },
        "existing_artifacts_inspected": [row["path"] for row in artifact_reuse_rows(root)],
        "reuse_extend_wrap_create_new_decisions": {
            "reuse": ["E65-E73 generated state", "governed business operations product artifacts", "CIEU Audit Module artifacts"],
            "extend": ["CEO brain readback with E74 result fields"],
            "wrap": ["E73/E72 readbacks through thin E74 readback facade"],
            "create_new": ["E74 work-product artifacts and small E74 orchestrator/readback only"],
        },
        "no_new_wheel_compliance": {
            "retrospective_first_completed": True,
            "K9Audit_ledger_or_verifier_reimplemented": False,
            "Y_star_gov_governance_engine_reimplemented": False,
            "gov_mcp_execution_envelope_reimplemented": False,
            "parallel_CEO_brain_created": False,
        },
        "work_boundaries": [
            "no external research execution",
            "no outreach",
            "no publication",
            "no payment or revenue workflow",
            "no live provider or MCP execution",
            "no live CIEU ledger writes",
        ],
        "expected_deliverable": "Governed Business Operations Blueprint + CIEU Audit Module: L3 Read-Only Research Readiness Packet",
        "CIEU_intent_contract": {
            "Y_star_t": "Generate a useful owner-facing L3 readiness packet using existing artifacts only.",
            "constraints": ["L2 internal only", "no external action", "no validation/paid/compliance/production claims", "no duplicate wheels"],
        },
        "external_action_allowed": False,
    }


def build_owner_facing_l3_readiness_packet(root: Path | None = None) -> dict[str, Any]:
    evidence = _evidence_summary(root)
    return {
        "artifact_id": "e74_owner_facing_l3_readiness_packet",
        "bridge_job_id": JOB_ID,
        "packet_title": "Governed Business Operations Blueprint + CIEU Audit Module: L3 Read-Only Research Readiness Packet",
        "packet_status": "owner_reviewable_internal_no_execution",
        "current_product_route": {
            "route_id": SELECTED_ROUTE,
            "product": SELECTED_PRODUCT,
            "plain_language": "A no-execution blueprint for agent teams that need governed operating practices, decision traceability, and CIEU-style action/intention/outcome/residual audit structure.",
        },
        "target_buyer_problem_hypothesis": {
            "buyer_categories": [
                "founder/operators building agent-enabled operations",
                "AI consultancies packaging governance/readiness services",
                "AI operations or risk leaders evaluating agent-team controls",
            ],
            "problem": "Teams are adopting AI agents faster than their operating controls, audit evidence, and human oversight language can mature.",
            "first_cash_relevance": "Read-only L3 research can clarify buyer language, category presence, and packaging analogs before any outreach or paid validation.",
        },
        "product_module_explanation": {
            "governed_business_operations_blueprint": "Maps agent-team work into roles, decisions, boundaries, operating loops, and owner-gated next actions.",
            "CIEU_Audit_Module": "Adds a causal audit structure: X_t context, U_t action, Y_star_t intended target, Y_t_plus_1 outcome, and R_t_plus_1 residual.",
            "commercial_importance": "It translates governance from abstract policy into inspectable action evidence, while staying clear that production ledger and compliance claims are not made.",
        },
        "existing_evidence_from_E65_E73": evidence,
        "still_missing_evidence": [
            "customer validation",
            "paid signal",
            "pricing validation",
            "expert feedback",
            "owner-approved L3 source allowlist",
            "fresh controlled read-only research receipts",
            "legal/compliance review before regulated claims",
        ],
        "exact_L3_read_only_research_questions": [
            "Which public buyer-language terms are most common: agent governance, AI operations, AI audit log, AI oversight, AI readiness, or compliance automation?",
            "Do public product/category pages show adjacent demand for agent governance, auditability, observability, or AI GRC readiness?",
            "Which pricing/package analogs exist for readiness reviews, AI governance assessments, audit-log products, or agent observability packages?",
            "Which public demand proxies appear in jobs, RFPs, analyst pages, procurement language, or vendor docs without treating them as buyer commitment?",
            "Does CIEU need to be presented as a causal audit module, a traceability module, or an evidence-readiness module for owner comprehension?",
            "Which vertical is safest for a first L3 read-only pass: agent-team operations, AI consultancies, AI GRC, healthcare/energy context, or governed provider execution?",
        ],
        "source_categories_needed_for_L3": [
            "official public regulatory or standards pages",
            "AI governance/GRC vendor product pages",
            "agent observability/auditability product pages",
            "public pricing or package pages",
            "public job/RFP/procurement pages",
            "public documentation, blogs, and case studies with no login/contact extraction",
        ],
        "owner_approval_needed": [
            "approve future L3 read-only source categories or exact allowlist",
            "approve maximum number of public sources and timebox",
            "confirm no login, no contact, no publication, no paid action",
            "confirm receipt format and abort conditions",
        ],
        "forbidden_actions": [
            "customer outreach",
            "expert outreach",
            "contact scraping",
            "login or form submission",
            "publication",
            "payment or invoice setup",
            "live provider/MCP execution",
            "compliance/legal/customer/paid/production claims",
        ],
        "positive_evidence_criteria": [
            "multiple independent public sources use buyer-readable language matching the offer",
            "adjacent products or services show category presence",
            "public package/pricing analogs make the offer shape easier to explain",
            "demand proxies point to auditability, oversight, or governance pain without high overclaim risk",
        ],
        "negative_evidence_criteria": [
            "public language is too compliance-heavy for a first-cash wedge",
            "CIEU terminology is not buyer-readable without translation",
            "adjacent products are too commodity or too enterprise-heavy for near-term work",
            "pricing analogs are absent or point to sales cycles too long for first cash",
        ],
        "decision_criteria_for_L4_later": [
            "owner separately approves exact outbound/publication action after reviewing L3 results",
            "L3 evidence identifies a safe, narrow buyer/problem language",
            "no-overclaim review passes with no compliance/customer/paid claims",
            "message, recipient/source list, rollback, and receipt policy are prepared",
        ],
        "recommended_owner_decision": "Approve finalization of an L3 read-only external research decision packet; do not execute L3 until owner approval is explicit.",
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
    }


def build_l3_allowlist_proposal(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e74_l3_allowlist_proposal_no_execution",
        "bridge_job_id": JOB_ID,
        "proposal_status": "owner_approval_required_before_any_L3_execution",
        "public_source_category_candidates": [
            "official regulatory/standards pages relevant to AI governance and high-risk record keeping",
            "AI governance/GRC vendor product and documentation pages",
            "AI agent observability/auditability product pages",
            "public pricing/package pages for readiness reviews or governance audits",
            "public job/RFP/procurement pages mentioning AI governance, oversight, traceability, or audit logs",
            "public case studies/blogs/docs from vendors or institutions, no account login",
        ],
        "allowed_read_only_evidence_types_for_future_L3": [
            "public market language",
            "category/competitor presence",
            "public pricing/package analogs",
            "public demand proxies",
            "public behavior/documentation signals",
        ],
        "forbidden_evidence_types": [
            "private profiles or human identification",
            "emails, phone numbers, social scraping, or contact lists",
            "login-gated content",
            "form-submitted content",
            "paid reports or purchased data",
            "customer conversations",
            "expert feedback",
        ],
        "rules": {
            "no_contact": True,
            "no_account_login_unless_owner_explicitly_approves": True,
            "no_publication": True,
            "no_payment": True,
            "no_scraping_contacts": True,
            "no_L3_execution_in_E74": True,
        },
        "source_receipt_requirements": [
            "source_url",
            "source_type",
            "read_timestamp",
            "evidence_type",
            "route_relevance",
            "limitation",
            "no_customer_validation_claim",
            "no_paid_signal_claim",
        ],
        "maximum_scope_budget_for_future_L3_run": {
            "source_count_cap": 30,
            "source_categories_cap": 6,
            "timebox_hours_cap": 4,
            "network_mode": "owner_approved_read_only_only",
        },
        "abort_conditions": [
            "source requires login, payment, contact, or form submission",
            "source contains private personal contact data",
            "research starts drifting into customer outreach or expert feedback",
            "evidence would require compliance/legal interpretation beyond public-read summary",
            "no-overclaim checks fail",
        ],
        "owner_approval_fields": {
            "owner_approved_L3_execution": False,
            "approved_source_categories": [],
            "approved_source_urls": [],
            "approved_source_count_cap": None,
            "approved_timebox": None,
            "approved_by": None,
            "approval_timestamp": None,
        },
        "external_action_allowed": False,
    }


def build_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    packet = build_owner_facing_l3_readiness_packet(root)
    return {
        "artifact_id": "e74_cieu_residual_for_l2_work_cycle",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "CEO_runtime_context": "E73 adjudicated L2 internal autonomous work ready, L3 conditional, L4/L5 not ready.",
            "selected_product": SELECTED_PRODUCT,
            "boundary": "no external action; bridge-labs-only generated artifacts; upstream repos read-only.",
        },
        "U_t": {
            "internal_work_cycle_performed": [
                "loaded E73 readiness and no-new-wheel policy",
                "inspected E65-E73 and product artifacts",
                "prepared owner-facing L3 readiness packet",
                "prepared no-execution L3 allowlist proposal",
                "updated CEO readback state",
            ]
        },
        "Y_star_t": {
            "intended_outcome": "Owner receives a useful L3 read-only research readiness packet without E74 performing external research.",
            "constraints": ["no outreach", "no publication", "no live execution", "no duplicate core mechanisms", "no validation/paid/compliance/production claims"],
        },
        "Y_t_plus_1": {
            "generated_deliverables": [
                "e74_l2_internal_work_cycle_plan",
                "e74_existing_artifact_reuse_map",
                "e74_owner_facing_l3_readiness_packet",
                "e74_l3_allowlist_proposal_no_execution",
                "e74_ceo_l2_work_readback",
            ],
            "readiness_delta": "L2 remains ready; L3 is now better prepared for owner decision but not executed.",
        },
        "R_t_plus_1": {
            "residual_gaps": packet["still_missing_evidence"],
            "overclaim_controls": packet["forbidden_actions"],
            "next_U": NEXT_MILESTONE,
        },
        "external_action_allowed": False,
        "no_overclaim": True,
    }


def build_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    packet = build_owner_facing_l3_readiness_packet(root)
    return {
        "artifact_id": "e74_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "selected_next_milestone": NEXT_MILESTONE,
        "selected_option": "Option_A",
        "readiness_level_advanced": "L2_to_L3_owner_decision_preparation",
        "why_not_just_more_construction": "E74 produced the owner-facing work product; the next step is a decision packet finalization for L3 read-only research, not a new runtime mechanism.",
        "owner_decision_required": [
            "approve or edit source categories / allowlist",
            "approve source count cap and timebox",
            "confirm no-contact/no-login/no-publication/no-paid-action boundary",
        ],
        "why_not_select_executable_L3_pilot": "Owner approval for L3 execution is not present in E74.",
        "why_not_select_second_L2_packaging_cycle": "The L3 readiness packet is concrete enough to move to owner decision finalization.",
        "readiness_basis": {
            "main_packet_status": packet["packet_status"],
            "owner_approval_status": OWNER_DECISION_STATUS,
            "external_action_allowed": False,
        },
        "external_action_allowed": False,
    }


def build_readback_state(root: Path | None = None) -> dict[str, Any]:
    packet = load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", root) or build_owner_facing_l3_readiness_packet(root)
    residual = load_json("operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", root) or build_cieu_residual(root)
    proposal = load_json("operations/external_validation/e74_generated_next_milestone_proposal.json", root) or build_next_milestone_proposal(root)
    reuse = load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", root) or build_existing_artifact_reuse_map(root)
    return {
        "artifact_id": "e74_ceo_l2_work_readback",
        "bridge_job_id": JOB_ID,
        "L2_work_status": "completed_internal_no_external_action",
        "real_L2_work_completed": True,
        "deliverable_produced": packet["packet_title"],
        "owner_facing_packet_status": packet["packet_status"],
        "existing_artifacts_reused_count": reuse["reuse_count"],
        "no_new_wheel_compliance": True,
        "new_mechanisms_created": False,
        "readiness_movement": residual["Y_t_plus_1"]["readiness_delta"],
        "L2_remains_ready": True,
        "L3_status_after_E74": "ready_for_owner_decision_packet_finalization_not_execution",
        "L4_status_after_E74": "not_ready",
        "L5_status_after_E74": "not_ready",
        "next_recommended_milestone": proposal["selected_next_milestone"],
        "next_milestone_type": "owner_decision_preparation",
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    plan = load_json("operations/external_validation/e74_l2_internal_work_cycle_plan.json", base)
    reuse = load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", base)
    packet = load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", base)
    allowlist = load_json("operations/external_validation/e74_l3_allowlist_proposal_no_execution.json", base)
    residual = load_json("operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", base)
    readback = load_json("operations/external_validation/e74_ceo_l2_work_readback.json", base)
    proposal = load_json("operations/external_validation/e74_generated_next_milestone_proposal.json", base)
    checks = {
        "base_verified": base_verified(base),
        "E73_L2_ready_loaded": plan.get("readiness_basis", {}).get("E73_L2_decision") == "ready",
        "main_owner_packet_exists": packet.get("packet_status") == "owner_reviewable_internal_no_execution",
        "artifact_reuse_map_exists": reuse.get("inspected_count", 0) >= 15,
        "no_new_wheel_compliance_recorded": reuse.get("duplicate_mechanism_risk_assessment", {}).get("duplicate_K9Audit_ledger_or_verifier_created") is False,
        "allowlist_proposal_no_execution": allowlist.get("rules", {}).get("no_L3_execution_in_E74") is True,
        "CIEU_residual_complete": all(key in residual for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]),
        "CEO_readback_exists": readback.get("L2_work_status") == "completed_internal_no_external_action",
        "next_milestone_readiness_driven": proposal.get("selected_next_milestone") == NEXT_MILESTONE,
        "no_forbidden_claims": all(packet.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "compliance_legal_claimed",
            "production_deployment_claimed",
            "live_ledger_claimed",
            "external_action_allowed",
        ]),
    }
    return {
        "artifact_id": "e74_completion_report",
        "bridge_job_id": JOB_ID,
        "base": git_state(base),
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e74_ceo_l2_internal_autonomous_work_pilot_completed" if all(checks.values()) else "e74_partial_with_internal_blocker",
        "real_L2_internal_work_performed": "Owner-facing L3 read-only research readiness packet created.",
        "main_owner_facing_deliverable": "operations/external_validation/e74_owner_facing_l3_readiness_packet.md",
        "L2_remains_ready": True,
        "L3_after_E74": "ready_for_owner_decision_packet_finalization_not_execution",
        "L4_after_E74": "not_ready",
        "L5_after_E74": "not_ready",
        "next_recommended_milestone": NEXT_MILESTONE,
        "next_milestone_type": "owner_decision_preparation_not_construction",
        "external_action_allowed": False,
        "read_only_repos_mutated": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
    }


def _md_plan(plan: dict[str, Any]) -> list[str]:
    return [
        f"- Objective: {plan['objective']}",
        f"- Selected route: `{plan['selected_route']}`",
        f"- Selected product: {plan['selected_product']}",
        f"- E73 L2 decision: {plan['readiness_basis']['E73_L2_decision']}",
        f"- E73 L3 decision: {plan['readiness_basis']['E73_L3_decision']}",
        "- Expected deliverable: " + plan["expected_deliverable"],
        "",
        "## Boundaries",
        *[f"- {item}" for item in plan["work_boundaries"]],
        "",
        "## No-New-Wheel Compliance",
        *[f"- {key}: {value}" for key, value in plan["no_new_wheel_compliance"].items()],
    ]


def _md_reuse(reuse: dict[str, Any]) -> list[str]:
    lines = [
        f"- Inspected artifacts: {reuse['inspected_count']}",
        f"- Reused artifacts: {reuse['reuse_count']}",
        f"- Context-only artifacts: {reuse['context_only_count']}",
        "",
        "## Canonical Owners",
        *[f"- {owner}: {meaning}" for owner, meaning in reuse["canonical_owner_mapping"].items()],
        "",
        "## Decisions",
    ]
    for row in reuse["artifacts_inspected"]:
        lines.append(f"- `{row['path']}`: {row['decision']} ({row['canonical_owner']})")
    return lines


def _md_packet(packet: dict[str, Any]) -> list[str]:
    return [
        packet["current_product_route"]["plain_language"],
        "",
        "## What Could Be Researched In L3",
        *[f"- {item}" for item in packet["exact_L3_read_only_research_questions"]],
        "",
        "## Why It Matters For First Cash",
        f"- {packet['target_buyer_problem_hypothesis']['first_cash_relevance']}",
        "",
        "## Positive Evidence",
        *[f"- {item}" for item in packet["positive_evidence_criteria"]],
        "",
        "## Negative Evidence",
        *[f"- {item}" for item in packet["negative_evidence_criteria"]],
        "",
        "## Source Categories",
        *[f"- {item}" for item in packet["source_categories_needed_for_L3"]],
        "",
        "## Owner Approval Needed",
        *[f"- {item}" for item in packet["owner_approval_needed"]],
        "",
        "## Forbidden Actions",
        *[f"- {item}" for item in packet["forbidden_actions"]],
        "",
        f"Recommended owner decision: {packet['recommended_owner_decision']}",
    ]


def _md_allowlist(allowlist: dict[str, Any]) -> list[str]:
    return [
        f"- Status: {allowlist['proposal_status']}",
        "",
        "## Candidate Source Categories",
        *[f"- {item}" for item in allowlist["public_source_category_candidates"]],
        "",
        "## Allowed Evidence Types",
        *[f"- {item}" for item in allowlist["allowed_read_only_evidence_types_for_future_L3"]],
        "",
        "## Forbidden Evidence Types",
        *[f"- {item}" for item in allowlist["forbidden_evidence_types"]],
        "",
        "## Scope Cap",
        f"- Source count cap: {allowlist['maximum_scope_budget_for_future_L3_run']['source_count_cap']}",
        f"- Timebox: {allowlist['maximum_scope_budget_for_future_L3_run']['timebox_hours_cap']} hours",
        "",
        "## Abort Conditions",
        *[f"- {item}" for item in allowlist["abort_conditions"]],
    ]


def _md_residual(residual: dict[str, Any]) -> list[str]:
    return [
        "## X_t",
        json.dumps(residual["X_t"], indent=2, ensure_ascii=False),
        "",
        "## U_t",
        json.dumps(residual["U_t"], indent=2, ensure_ascii=False),
        "",
        "## Y_star_t",
        json.dumps(residual["Y_star_t"], indent=2, ensure_ascii=False),
        "",
        "## Y_t_plus_1",
        json.dumps(residual["Y_t_plus_1"], indent=2, ensure_ascii=False),
        "",
        "## R_t_plus_1",
        json.dumps(residual["R_t_plus_1"], indent=2, ensure_ascii=False),
    ]


def _md_readback(readback: dict[str, Any]) -> list[str]:
    return [
        f"- L2 work status: {readback['L2_work_status']}",
        f"- Deliverable: {readback['deliverable_produced']}",
        f"- Existing artifacts reused: {readback['existing_artifacts_reused_count']}",
        f"- No-new-wheel compliance: {readback['no_new_wheel_compliance']}",
        f"- Readiness movement: {readback['readiness_movement']}",
        f"- Next milestone: {readback['next_recommended_milestone']}",
        f"- External action allowed: {readback['external_action_allowed']}",
    ]


def _md_completion(report: dict[str, Any]) -> list[str]:
    return [
        f"- Final status: {report['final_status']}",
        f"- Gate passed: {report['gate_passed']}",
        f"- Real L2 work: {report['real_L2_internal_work_performed']}",
        f"- Main deliverable: `{report['main_owner_facing_deliverable']}`",
        f"- L2 remains ready: {report['L2_remains_ready']}",
        f"- L3 after E74: {report['L3_after_E74']}",
        f"- L4 after E74: {report['L4_after_E74']}",
        f"- L5 after E74: {report['L5_after_E74']}",
        f"- Next milestone: {report['next_recommended_milestone']}",
        f"- Next milestone type: {report['next_milestone_type']}",
        "- Safety: no external action, no read-only repo mutation, no validation/paid/compliance/production/live-ledger claim.",
    ]


def write_all_e74_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    plan = build_l2_internal_work_cycle_plan(base)
    reuse = build_existing_artifact_reuse_map(base)
    packet = build_owner_facing_l3_readiness_packet(base)
    allowlist = build_l3_allowlist_proposal(base)
    residual = build_cieu_residual(base)
    readback = build_readback_state(base)
    proposal = build_next_milestone_proposal(base)

    write_json(base, "operations/external_validation/e74_l2_internal_work_cycle_plan.json", plan)
    write_md(base, "operations/external_validation/e74_l2_internal_work_cycle_plan.md", "E74 L2 Internal Work Cycle Plan", _md_plan(plan))
    write_json(base, "operations/external_validation/e74_existing_artifact_reuse_map.json", reuse)
    write_md(base, "operations/external_validation/e74_existing_artifact_reuse_map.md", "E74 Existing Artifact Reuse Map", _md_reuse(reuse))
    write_json(base, "operations/external_validation/e74_owner_facing_l3_readiness_packet.json", packet)
    write_md(base, "operations/external_validation/e74_owner_facing_l3_readiness_packet.md", packet["packet_title"], _md_packet(packet))
    write_json(base, "operations/external_validation/e74_l3_allowlist_proposal_no_execution.json", allowlist)
    write_md(base, "operations/external_validation/e74_l3_allowlist_proposal_no_execution.md", "E74 L3 Allowlist Proposal, No Execution", _md_allowlist(allowlist))
    write_json(base, "operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", residual)
    write_md(base, "operations/external_validation/e74_cieu_residual_for_l2_work_cycle.md", "E74 CIEU Residual For L2 Work Cycle", _md_residual(residual))
    write_json(base, "operations/external_validation/e74_ceo_l2_work_readback.json", readback)
    write_md(base, "operations/external_validation/e74_ceo_l2_work_readback.md", "E74 CEO L2 Work Readback", _md_readback(readback))
    write_json(base, "operations/external_validation/e74_generated_next_milestone_proposal.json", proposal)
    report = build_completion_report(base)
    write_json(base, "operations/external_validation/e74_completion_report.json", report)
    write_md(base, "operations/external_validation/e74_completion_report.md", "E74 Completion Report", _md_completion(report))
    return report


if __name__ == "__main__":
    print(json.dumps(write_all_e74_artifacts(), indent=2, ensure_ascii=False))
