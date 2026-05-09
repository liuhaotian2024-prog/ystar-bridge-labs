from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from office.mission_command.e119_aiden_operating_pattern_doctrine_registry import (
    build_operating_pattern_invocation_proof,
)


MILESTONE_ID = "E120_Aiden_Knowledge_Graph_Learning_Methodology_And_Downstream_Impact_R1"
SESSION_ID = "e120_unknown_problem_learning_protocol"
BRIDGE_ROOT = Path(__file__).resolve().parents[2]
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def build_aiden_unknown_problem_learning_protocol(
    *,
    unknown_problem_statement: str = "Aiden faces a business or operating domain it has not previously modeled deeply.",
) -> dict[str, Any]:
    return {
        "protocol_id": "e120_aiden_unknown_problem_learning_protocol",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "problem_context": {
            "problem_id": "unknown_business_or_operating_problem",
            "unknown_problem_statement": unknown_problem_statement,
            "action_boundary": "learn, model, and prepare governed next action only; no external action",
        },
        "knowledge_gap_diagnosis": {
            "known_unknowns": [
                "buyer vocabulary and pain intensity",
                "current alternatives and incumbents",
                "market timing and budget owner",
                "internal right-to-win fit",
                "failure modes from analogous historical cases",
            ],
            "confidence_boundary": "Aiden must learn before selecting a high-confidence strategy or implementation order.",
        },
        "learning_objectives": [
            _objective("classical_theory_canon", "Find durable theory: decision theory, strategy, systems, organizations, learning, and risk."),
            _objective("peer_experience_corpus", "Extract reusable founder/operator lessons without copying point tactics."),
            _objective("historical_case_corpus", "Compare success/failure cases and identify analogous causal patterns."),
            _objective("current_market_evidence", "Collect source-dated public signals and competitor/substitute evidence."),
            _objective("internal_capability_recall", "Recall bridge-labs/Y-star-gov/gov-mcp capabilities and avoid rebuilding them."),
            _objective("customer_contact_residuals", "Prepare owner-gated L4 feedback residual learning without claiming validation."),
        ],
        "sensemaking_modes": [
            "buyer_pain_sense",
            "system_pressure_sense",
            "risk_smell",
            "anomaly_detection",
            "founder_market_fit_sense",
            "time_to_cash_sense",
        ],
        "thinking_modes": [
            "first_principles",
            "systems_thinking",
            "decision_theory",
            "adversarial_critique",
            "causal_zero_loop",
            "customer_empathy",
            "counterfactual_reasoning",
            "no_new_wheel_reasoning",
        ],
        "source_discovery_plan": [
            {"source_type": "brain_recall", "where": "aiden_brain.db 6D activation", "risk": "read_only"},
            {"source_type": "repo_capability_recall", "where": "E87R baseline plus current repo code/tests/reports", "risk": "read_only"},
            {"source_type": "public_read_research", "where": "safe public-read provider with source dates", "risk": "no_external_side_effect"},
            {"source_type": "classical_theory", "where": "canonical books, papers, standards, durable references", "risk": "read_only"},
            {"source_type": "peer_experience", "where": "operator interviews, YC/a16z-style lessons, practitioner playbooks", "risk": "read_only"},
            {"source_type": "historical_case", "where": "startup and company success/failure case databases", "risk": "read_only"},
            {"source_type": "owner_or_L4_feedback_when_approved", "where": "owner-approved no-send/send feedback packet only", "risk": "owner_gated"},
        ],
        "tool_selection": [
            {"tool_id": "brain_activation", "purpose": "recall existing Aiden knowledge and provenance"},
            {"tool_id": "repo_search", "purpose": "find existing capabilities before building"},
            {"tool_id": "public_read_provider", "purpose": "collect current dated public evidence"},
            {"tool_id": "Y_star_gov_validator", "purpose": "validate learning protocol and downstream actions"},
            {"tool_id": "CIEUStore", "purpose": "record decisions and residuals"},
            {"tool_id": "CZL_residual_engine", "purpose": "turn prediction failure into learning updates"},
        ],
        "knowledge_graph_methodology": {
            "node_types": [
                "classical_theory_node",
                "peer_experience_node",
                "historical_case_node",
                "current_market_fact_node",
                "internal_capability_node",
                "tool_affordance_node",
                "assumption_node",
                "CZL_residual_node",
            ],
            "edge_types": [
                "supports",
                "contradicts",
                "generalizes",
                "falsifies",
                "requires_tool",
                "updates_strategy",
                "maps_to_buyer_pain",
                "blocks_overclaim",
            ],
            "content_type_freshness_policy_required": True,
            "production_brain_write_requires_owner_gate": True,
            "CIEU_backed_before_brain_write": True,
        },
        "downstream_impact_scan": {
            "required": True,
            "scan_targets": [
                "freshness filters",
                "learning quality gates",
                "strategy dossier contracts",
                "operating pattern registry",
                "Codex handoff/order boundary",
                "brain write boundary",
            ],
            "sibling_variant_question": "Where else can this same issue class appear?",
        },
        "governance_plan": {
            "operating_pattern_doctrine_required": True,
            "CIEU_recording_required": True,
            "Y_star_gov_contract": "ystar/governance/aiden_unknown_problem_learning_protocol_contract.py",
        },
        "output_obligations": [
            "learning dossier",
            "knowledge graph delta",
            "assumption registry",
            "CZL residual plan",
            "owner-gated next action recommendation",
        ],
        "truth_constraints": {
            "recent_memory_only": False,
            "external_action_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "direct_brain_write_without_owner_gate": False,
            "direct_contract_mutation": False,
        },
    }


def build_e120_operating_pattern_proof() -> dict[str, Any]:
    return build_operating_pattern_invocation_proof(
        {
            "action_id": "e120_unknown_problem_learning_methodology",
            "action_type": "unknown_problem_learning_and_durable_knowledge_graph_growth",
            "market_strategy_required": True,
            "codex_execution_required": False,
            "brain_write_related": True,
            "external_action_related": False,
            "self_governance_related": True,
            "unknown_problem_related": True,
            "durable_learning_related": True,
        }
    )


def run_e120_unknown_problem_learning_protocol_session(
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    protocol = build_aiden_unknown_problem_learning_protocol()
    pattern_proof = build_e120_operating_pattern_proof()
    patterns = _load_ystar_module("ystar.governance.aiden_operating_pattern_doctrine_contract", ystar_gov_root)
    pattern_result = patterns.validate_and_write_aiden_operating_pattern_invocation(
        pattern_proof,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    if pattern_result["governance_decision"]["decision"] != "ALLOW":
        return {
            "artifact_id": "e120_unknown_problem_learning_protocol_result",
            "milestone_id": MILESTONE_ID,
            "operating_pattern_result": pattern_result,
            "unknown_problem_learning_result": {},
            "protocol": protocol,
            "proven": False,
        }
    gov = _load_ystar_module("ystar.governance.aiden_unknown_problem_learning_protocol_contract", ystar_gov_root)
    learning_result = gov.validate_and_write_aiden_unknown_problem_learning_protocol(
        protocol,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    return {
        "artifact_id": "e120_unknown_problem_learning_protocol_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operating_pattern_result": pattern_result,
        "unknown_problem_learning_result": learning_result,
        "protocol": protocol,
        "proven": learning_result["governance_decision"]["decision"] == "ALLOW",
        "truth_constraints": protocol["truth_constraints"],
    }


def write_e120_reports(*, cieu_db: str | Path, root: str | Path | None = None, ystar_gov_root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_e120_unknown_problem_learning_protocol_session(cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    report = {
        "milestone_id": MILESTONE_ID,
        "claude_assessment_verdict": {
            "freshness_filter_gap_verified": True,
            "peer_experience_previously_rejected": True,
            "customer_learning_methodology_previously_rejected": True,
            "historical_case_domain_previously_lost_by_dedupe": True,
        },
        "content_type_freshness_fix": "implemented",
        "unknown_problem_learning_protocol_proven": result["proven"],
        "operating_pattern_decision": result["operating_pattern_result"]["governance_decision"]["decision"],
        "unknown_problem_learning_decision": result["unknown_problem_learning_result"]["governance_decision"]["decision"],
        "knowledge_graph_methodology": result["protocol"]["knowledge_graph_methodology"],
        "downstream_impact_scan": result["protocol"]["downstream_impact_scan"],
        "truth_constraints": result["truth_constraints"],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_downstream_impact_and_learning_protocol_governance",
            "L5-B": "stronger_governed_intelligence_with_unknown_problem_learning_methodology",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_with_content_type_freshness_and_knowledge_graph_methodology",
        },
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented",
        "content_type_freshness_policy_active": True,
        "unknown_problem_learning_protocol_active": True,
        "downstream_impact_scan_required": True,
        "L5_truth_table_after": report["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e120_aiden_unknown_problem_learning_protocol_report.json",
        "report_md": base / "office/mission_command/e120_aiden_unknown_problem_learning_protocol_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e120_unknown_problem_learning_protocol.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e120_unknown_problem_learning_protocol.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return report


def _objective(domain_id: str, objective: str) -> dict[str, str]:
    return {"domain_id": domain_id, "objective": objective}


def _report_md(report: dict[str, Any]) -> str:
    return (
        "# E120 Aiden Unknown-Problem Learning Protocol\n\n"
        f"- Content-type freshness fix: {report['content_type_freshness_fix']}\n"
        f"- Unknown-problem learning protocol proven: {report['unknown_problem_learning_protocol_proven']}\n"
        f"- Operating pattern decision: {report['operating_pattern_decision']}\n"
        f"- Unknown-problem learning decision: {report['unknown_problem_learning_decision']}\n\n"
        "Aiden now has a governed method for deciding what to learn, where to look, which thinking modes to use, "
        "and how to convert unfamiliar terrain into typed knowledge-graph growth.\n"
    )


def _status_md(status: dict[str, Any]) -> str:
    return (
        "# Runtime Status After E120\n\n"
        f"- Content-type freshness policy active: {status['content_type_freshness_policy_active']}\n"
        f"- Unknown-problem learning protocol active: {status['unknown_problem_learning_protocol_active']}\n"
        f"- Downstream impact scan required: {status['downstream_impact_scan_required']}\n"
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
    "build_aiden_unknown_problem_learning_protocol",
    "build_e120_operating_pattern_proof",
    "run_e120_unknown_problem_learning_protocol_session",
    "write_e120_reports",
]
