from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e119_aiden_operating_pattern_doctrine_registry import (
    build_operating_pattern_invocation_proof,
)


MILESTONE_ID = "E119_Learning_To_Governance_Extrapolation_And_Self_Governance_Proposal_R1"
SESSION_ID = "e119_learning_to_governance_extrapolation"
BRIDGE_ROOT = Path(__file__).resolve().parents[2]
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def build_e119_self_governance_update_proposal() -> dict[str, Any]:
    return {
        "proposal_id": "e119_point_fix_to_class_level_governance_proposal",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_residual": {
            "residual_id": "e119_audit_driven_point_fix_residual",
            "CZL_R_t_plus_1": 1.0,
            "observed_gap": "Aiden/Codex repeatedly fixed named audit findings without always generalizing the failure class.",
            "learning_update": "Future strategy, learning, and governance outputs must identify the issue class and same-class variants.",
        },
        "class_of_issue": {
            "issue_class_id": "point_fix_without_generalization",
            "description": "A point failure is repaired but the governing class of similar future failures remains unmodeled.",
            "generalization_boundary": "applies across strategy dossiers, idle brain learning, production brain write preflight, and future governance proposals",
        },
        "observed_point_failures": [
            {
                "failure_id": "reused_deep_strategy_evidence",
                "evidence_ref": "E115 audit: 14 dimensions reused the same evidence bundle",
                "repair_status": "E117 locked evidence diversity",
            },
            {
                "failure_id": "self_assigned_competitor_current_date",
                "evidence_ref": "E117 audit: competitor homepage rows could receive today's public_signal_date",
                "repair_status": "E118 locked source-dated public evidence basis",
            },
            {
                "failure_id": "boolean_owner_approval_for_brain_write",
                "evidence_ref": "E118 audit: owner approval was a boolean without out-of-band proof",
                "repair_status": "E118 added approval + backup gate; future out-of-band approval remains next step",
            },
        ],
        "extrapolation_to_other_cases": [
            {
                "case_id": "single_source_learning_fact",
                "why_same_class": "a single fresh source can look valid while lacking corroboration",
                "preventive_rule": "require corroboration status or mark fact as hypothesis before high-confidence brain use",
            },
            {
                "case_id": "internal_asset_as_market_value",
                "why_same_class": "an internal capability can masquerade as buyer-visible value",
                "preventive_rule": "require buyer-visible proof and why_buyer_cares for right-to-win claims",
            },
            {
                "case_id": "planning_residual_as_market_truth",
                "why_same_class": "internal residual closure can be mistaken for real customer validation",
                "preventive_rule": "separate planning residual closure from real market residual closure",
            },
            {
                "case_id": "raw_prompt_as_governed_order",
                "why_same_class": "field presence can hide missing CEOImplementationOrder governance",
                "preventive_rule": "require linked CEOImplementationOrder before Codex prompt generation",
            },
        ],
        "current_contract_refs": [
            "ystar/governance/ceo_deep_strategic_intelligence_contract.py",
            "ystar/governance/aiden_idle_learning_contract.py",
            "ystar/governance/aiden_self_governance_update_proposal_contract.py",
        ],
        "proposed_contract_amendment": {
            "target_contract": "cross_runtime_extrapolation_gate",
            "proposed_rule": (
                "Any Aiden strategy, learning, residual, or governance-improvement artifact that repairs a failure "
                "must include class_of_issue, at least three extrapolated same-class cases, and a proposed_class_level_fix."
            ),
            "correct_path_navigation": "if missing, REQUIRE_REVISION with navigation to generalize the point failure before proceeding",
            "auto_apply": False,
        },
        "owner_review_policy": {
            "owner_explicit_approval_required": True,
            "proposal_only_until_approved": True,
            "Aiden_direct_contract_mutation_allowed": False,
        },
        "implementation_plan": [
            "invoke Aiden operating pattern doctrine registry",
            "validate proposal through Y-star-gov",
            "write proposal CIEU record",
            "write pending owner-visible proposal artifact",
            "wait for owner approval before any future contract patch generation",
        ],
        "tests_required": [
            "missing extrapolation gate requires revision",
            "direct contract write attempt denies",
            "valid proposal writes CIEU record",
            "pending proposal artifact is owner-visible and does not modify Y-star-gov",
        ],
        "operating_pattern_doctrine_updates": {
            "status": "mechanized_as_runtime_obligations",
            "registry_path": "office/mission_command/e119_aiden_operating_pattern_doctrine_registry.py",
            "governance_contract_path": "ystar/governance/aiden_operating_pattern_doctrine_contract.py",
            "patterns_mechanized": [
                "full_repo_and_baseline_first",
                "no_new_wheel_preflight",
                "capability_utilization_sweep",
                "class_level_extrapolation_gate",
                "correct_path_navigation",
                "evidence_quality_and_freshness_gate",
                "regression_test_and_cieu_closure",
                "brain_provenance_required",
                "competitive_landscape_current_signal",
                "buyer_visible_value_translation",
                "residual_truth_scope_split",
                "CEOImplementationOrder_before_Codex_prompt",
                "CodexExecutionReceipt_return_path",
                "production_brain_write_owner_backup_gate",
                "learning_quality_scoring_v2",
                "gov_mcp_no_send_preflight",
                "owner_boundary_minimization_and_escalation",
                "proposal_only_no_direct_contract_mutation",
                "owner_review_before_contract_patch",
            ],
        },
        "CIEU_linkage": {
            "target_event_type": "AIDEN_SELF_GOVERNANCE_UPDATE_PROPOSAL_DECISION",
            "formal_CIEU_log_path": "ystar.governance.cieu_store.CIEUStore.write_dict",
        },
        "truth_constraints": {
            "direct_contract_write_attempted": False,
            "contract_patch_applied": False,
            "external_action_executed": False,
            "provider_action_executed": False,
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def write_pending_governance_proposal(proposal: Mapping[str, Any], *, root: str | Path | None = None) -> Path:
    base = Path(root or BRIDGE_ROOT)
    pending = base / "operations/governance_proposals/pending"
    pending.mkdir(parents=True, exist_ok=True)
    path = pending / f"{proposal['proposal_id']}.json"
    path.write_text(json.dumps(proposal, indent=2, sort_keys=True), encoding="utf-8")
    return path


def run_e119_learning_to_governance_extrapolation_session(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    write_pending: bool = True,
    seal_session: bool = False,
) -> dict[str, Any]:
    proposal = build_e119_self_governance_update_proposal()
    action_context = {
        "action_id": "e119_learning_to_governance_extrapolation",
        "action_type": "self_governance_plus_learning_runtime",
        "market_strategy_required": True,
        "codex_execution_required": True,
        "brain_write_related": True,
        "external_action_related": True,
        "self_governance_related": True,
    }
    pattern_proof = build_operating_pattern_invocation_proof(action_context)
    pattern_gov = _load_ystar_module("ystar.governance.aiden_operating_pattern_doctrine_contract", ystar_gov_root)
    pattern_result = pattern_gov.validate_and_write_aiden_operating_pattern_invocation(
        pattern_proof,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    if pattern_result["governance_decision"]["decision"] != "ALLOW":
        return {
            "artifact_id": "e119_learning_to_governance_extrapolation_result",
            "milestone_id": MILESTONE_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "proposal": proposal,
            "Aiden_operating_pattern_result": pattern_result,
            "YstarGov_self_governance_proposal_result": {},
            "pending_proposal_path": "",
            "self_governance_proposal_proven": False,
            "truth_constraints": dict(proposal["truth_constraints"]),
            "blocked_reason": "operating_pattern_doctrine_not_satisfied",
        }
    gov = _load_ystar_module("ystar.governance.aiden_self_governance_update_proposal_contract", ystar_gov_root)
    governance = gov.validate_and_write_aiden_self_governance_update_proposal(
        proposal,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    pending_path = ""
    if write_pending and governance["governance_decision"]["decision"] == "ALLOW":
        pending_path = str(write_pending_governance_proposal(proposal, root=root))
    return {
        "artifact_id": "e119_learning_to_governance_extrapolation_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "proposal": proposal,
        "Aiden_operating_pattern_result": pattern_result,
        "YstarGov_self_governance_proposal_result": governance,
        "pending_proposal_path": pending_path,
        "self_governance_proposal_proven": governance["governance_decision"]["decision"] == "ALLOW" and bool(pending_path),
        "truth_constraints": dict(proposal["truth_constraints"]),
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_self_governance_proposal_boundary",
            "L5-B": "stronger_structured_governed_intelligence_with_extrapolation_gate_and_self_governance_proposals",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_learning_to_governance_proposal_loop_proven_owner_approval_required",
        },
    }


def write_e119_reports(*, cieu_db: str | Path, root: str | Path | None = None, ystar_gov_root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_e119_learning_to_governance_extrapolation_session(
        cieu_db=cieu_db,
        root=base,
        ystar_gov_root=ystar_gov_root,
        write_pending=True,
        seal_session=False,
    )
    report = {
        "milestone_id": MILESTONE_ID,
        "self_governance_proposal_proven": result["self_governance_proposal_proven"],
        "pending_proposal_path": result["pending_proposal_path"],
        "Y_star_gov_decision": result["YstarGov_self_governance_proposal_result"]["governance_decision"]["decision"],
        "operating_pattern_decision": result["Aiden_operating_pattern_result"]["governance_decision"]["decision"],
        "operating_patterns_mechanized": result["proposal"]["operating_pattern_doctrine_updates"]["patterns_mechanized"],
        "class_of_issue": result["proposal"]["class_of_issue"],
        "extrapolated_case_count": len(result["proposal"]["extrapolation_to_other_cases"]),
        "curriculum_expansion": [
            "classical_theory_canon",
            "peer_experience_corpus",
            "historical_case_corpus",
            "customer_contact_residuals",
        ],
        "truth_constraints": result["truth_constraints"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_proposal_loop",
        "extrapolation_gate_required": True,
        "operating_pattern_doctrine_required": True,
        "self_governance_direct_contract_write_allowed": False,
        "owner_approval_required_for_contract_change": True,
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e119_learning_to_governance_extrapolation_report.json",
        "report_md": base / "office/mission_command/e119_learning_to_governance_extrapolation_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e119_learning_to_governance_extrapolation.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e119_learning_to_governance_extrapolation.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return report


def _report_md(report: Mapping[str, Any]) -> str:
    return (
        "# E119 Learning To Governance Extrapolation\n\n"
        f"- Self-governance proposal proven: {report['self_governance_proposal_proven']}\n"
        f"- Y-star-gov decision: {report['Y_star_gov_decision']}\n"
        f"- Operating pattern decision: {report['operating_pattern_decision']}\n"
        f"- Operating patterns mechanized: {len(report['operating_patterns_mechanized'])}\n"
        f"- Pending proposal path: {report['pending_proposal_path']}\n"
        f"- Extrapolated cases: {report['extrapolated_case_count']}\n\n"
        "Aiden can now propose class-level governance updates for owner review, but it cannot directly mutate Y-star-gov contracts.\n"
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E119\n\n"
        f"- Extrapolation gate required: {status['extrapolation_gate_required']}\n"
        f"- Operating pattern doctrine required: {status['operating_pattern_doctrine_required']}\n"
        f"- Direct contract write allowed: {status['self_governance_direct_contract_write_allowed']}\n"
        f"- Owner approval required: {status['owner_approval_required_for_contract_change']}\n"
        f"- L5-E: {status['L5_truth_table_after']['L5-E']}\n"
    )


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    loaded = sys.modules.get(module_name)
    loaded_file = str(getattr(loaded, "__file__", "")) if loaded is not None else ""
    if loaded is not None and root.exists() and loaded_file and not loaded_file.startswith(str(root)):
        del sys.modules[module_name]
    return importlib.import_module(module_name)


__all__ = [
    "MILESTONE_ID",
    "build_e119_self_governance_update_proposal",
    "run_e119_learning_to_governance_extrapolation_session",
    "write_e119_reports",
    "write_pending_governance_proposal",
]
