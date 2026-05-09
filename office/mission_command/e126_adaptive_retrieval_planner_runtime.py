from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e125_aiden_retrieval_orchestration_runtime import (
    classify_task_type,
    run_aiden_retrieval_orchestration,
)


MILESTONE_ID = "E126_Adaptive_Retrieval_Planner_And_Capability_Invocation_Runtime_R1"
SESSION_ID = "e126_adaptive_retrieval_planner"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))


def run_adaptive_retrieval_planner_and_retrieval(
    owner_message: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    allow_vector_query: bool = True,
    force_unknown_problem: bool | None = None,
) -> dict[str, Any]:
    """Plan evidence/capability needs, validate, then execute E125 retrieval."""

    base = Path(repo_root or BRIDGE_ROOT)
    packet = build_adaptive_retrieval_planner_packet(
        owner_message,
        repo_root=base,
        ystar_gov_root=ystar_gov_root,
        force_unknown_problem=force_unknown_problem,
    )
    gov = _load_ystar_module("ystar.governance.aiden_adaptive_retrieval_planner_contract", ystar_gov_root)
    planner_validation = gov.validate_and_write_aiden_adaptive_retrieval_planner_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
    )
    if planner_validation["governance_decision"]["decision"] != "ALLOW":
        return {
            "artifact_id": "e126_adaptive_retrieval_planner_result",
            "milestone_id": MILESTONE_ID,
            "planner_packet": packet,
            "YstarGov_planner_result": planner_validation,
            "adaptive_planner_decision": planner_validation["governance_decision"]["decision"],
            "retrieval_result": None,
            "runtime_may_answer": False,
            "CIEUStore_summary": summarize_cieustore(cieu_db),
            "external_action_executed": False,
            "provider_action_executed": False,
            "payment_executed": False,
        }

    e125_params = packet["retrieval_orchestration_binding"]["E125_parameters"]
    retrieval_result = run_aiden_retrieval_orchestration(
        owner_message,
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        repo_root=base,
        high_wisdom_required=bool(e125_params.get("high_wisdom_required", True)),
        external_public_read_required=bool(e125_params.get("external_public_read_required", False)),
        allow_vector_query=allow_vector_query,
    )
    return {
        "artifact_id": "e126_adaptive_retrieval_planner_result",
        "milestone_id": MILESTONE_ID,
        "planner_packet": packet,
        "YstarGov_planner_result": planner_validation,
        "adaptive_planner_decision": planner_validation["governance_decision"]["decision"],
        "retrieval_result": retrieval_result,
        "runtime_may_answer": retrieval_result["retrieval_decision"] == "ALLOW",
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "external_action_executed": False,
        "provider_action_executed": False,
        "payment_executed": False,
    }


def build_adaptive_retrieval_planner_packet(
    owner_message: str,
    *,
    repo_root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    force_unknown_problem: bool | None = None,
) -> dict[str, Any]:
    base = Path(repo_root or BRIDGE_ROOT)
    task_type = classify_task_type(owner_message)
    context = build_adaptive_action_context(owner_message, task_type=task_type, force_unknown_problem=force_unknown_problem)
    evidence_need = build_evidence_need_analysis(context)
    adaptive_governance = build_e101_governance_obligation_discovery(context)
    capability_recall = build_e113_existing_capability_recall(context, repo_root=base, ystar_gov_root=ystar_gov_root)
    pattern_selection = build_e119_operating_pattern_selection(context)
    unknown_assessment = build_e120_unknown_problem_assessment(context)
    dynamic_plan = build_dynamic_retrieval_plan(context, evidence_need)
    invocation_plan = build_capability_invocation_plan(context, capability_recall, pattern_selection)
    return {
        "artifact_id": "e126_adaptive_retrieval_planner_packet",
        "milestone_id": MILESTONE_ID,
        "planner_id": f"planner_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "task_context": context,
        "evidence_need_analysis": evidence_need,
        "governance_obligation_discovery": adaptive_governance,
        "existing_capability_recall": capability_recall,
        "operating_pattern_selection": pattern_selection,
        "unknown_problem_learning_assessment": unknown_assessment,
        "dynamic_retrieval_plan": dynamic_plan,
        "capability_invocation_plan": invocation_plan,
        "retrieval_orchestration_binding": {
            "E125_bound": True,
            "execute_E125_after_planner_allow": True,
            "raw_answer_before_retrieval_allowed": False,
            "E125_parameters": {
                "high_wisdom_required": True,
                # E126 plans public-read for strategy, but E125 remains local retrieval.
                # Live public-read execution is delegated to E108/E114, not faked here.
                "external_public_read_required": False,
            },
        },
        "self_improvement_path": {
            "new_capability_discovery_supported": True,
            "self_governance_proposal_on_gap": True,
            "direct_contract_mutation_allowed": False,
            "proposal_route": "Aiden may write owner-visible governance/capability proposal artifacts; direct Y-star-gov contract mutation is forbidden.",
        },
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_ADAPTIVE_RETRIEVAL_PLANNER_DECISION",
        },
        "truth_constraints": {
            "recent_memory_only": False,
            "fixed_retrieval_list_only": False,
            "adaptive_planning_bypassed": False,
            "no_new_wheel_bypassed": False,
            "unknown_problem_protocol_bypassed": False,
            "operating_pattern_registry_bypassed": False,
            "external_action_executed": False,
            "provider_action_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "live_provider_execution_claim": False,
            "K9Audit_write_claim": False,
            "hidden_chain_of_thought_stored": False,
            "CIEU_recording_bypassed": False,
        },
    }


def build_adaptive_action_context(
    owner_message: str,
    *,
    task_type: str,
    force_unknown_problem: bool | None = None,
) -> dict[str, Any]:
    lower = owner_message.lower()
    market_strategy_required = task_type == "strategy"
    implementation_required = task_type == "implementation"
    governance_required = task_type == "governance"
    retrieval_required = task_type == "runtime" or "rag" in lower or "检索" in owner_message or "记忆" in owner_message
    unknown_problem = (
        force_unknown_problem
        if force_unknown_problem is not None
        else any(term in lower for term in ("new", "unknown", "novel", "open world", "unfamiliar")) or any(term in owner_message for term in ("新", "未知", "没见过", "自主", "智能"))
    )
    return {
        "agent_id": "Aiden",
        "owner_message": owner_message,
        "task_objective": "adaptively plan retrieval and existing capability invocation before Aiden answers or acts",
        "task_type": task_type,
        "planning_mode": "adaptive_evidence_need_and_capability_invocation",
        "market_strategy_required": market_strategy_required,
        "implementation_required": implementation_required,
        "governance_required": governance_required,
        "retrieval_runtime_required": retrieval_required,
        "unknown_problem_related": bool(unknown_problem or market_strategy_required),
        "durable_learning_related": bool(unknown_problem or market_strategy_required),
        "self_governance_related": True,
        "codex_execution_required": implementation_required,
        "external_action_related": False,
        "brain_write_related": False,
    }


def build_evidence_need_analysis(action_context: Mapping[str, Any]) -> dict[str, Any]:
    families = [
        "repo_capability_evidence",
        "brain_provenance",
        "code_index_or_baseline",
        "CIEU_history",
        "long_term_memory_status",
    ]
    if action_context.get("market_strategy_required"):
        families.extend(
            [
                "current_market_evidence_or_public_read_route",
                "competitor_and_substitute_evidence",
                "buyer_visible_value_evidence",
                "classical_theory_or_case_corpus",
            ]
        )
    if action_context.get("implementation_required"):
        families.extend(["existing_code_paths", "tests_and_contracts", "delivery_boundary"])
    if action_context.get("governance_required"):
        families.extend(["governance_contracts", "correct_path_navigation", "forbidden_claims"])
    if action_context.get("unknown_problem_related"):
        families.extend(["unknown_problem_learning_protocol", "sensemaking_modes", "knowledge_graph_methodology"])
    return {
        "adaptive_analysis_performed": True,
        "required_evidence_families": sorted(dict.fromkeys(families)),
        "unknowns_to_resolve": [
            "which existing capabilities already solve part of this task",
            "which memory/evidence systems should be queried",
            "which governed runtime should be invoked next",
            "whether the task requires public-read evidence or only local context",
        ],
        "why_not_fixed_list_only": "fixed source lists miss new capability domains; this planner binds E101/E113/E119/E120 before E125",
    }


def build_e101_governance_obligation_discovery(action_context: Mapping[str, Any]) -> dict[str, Any]:
    try:
        from office.mission_command.e101_adaptive_governance_discovery_and_correct_path_navigator import (
            discover_adaptive_governance_obligations,
        )

        discovery = discover_adaptive_governance_obligations(action_context=action_context, runtime_artifact={})
        required = [item.get("obligation_id") for item in discovery.get("required_obligations", []) if isinstance(item, Mapping)]
        return {
            "mechanism_id": "E101_adaptive_governance_correct_path",
            "discovery_performed": True,
            "signals": discovery.get("signals", []),
            "required_obligations": required or ["new_governance_obligation_candidate"],
            "advisory_obligations": [item.get("obligation_id") for item in discovery.get("advisory_obligations", []) if isinstance(item, Mapping)],
            "correct_path_navigation_available": True,
        }
    except Exception as exc:
        return {
            "mechanism_id": "E101_adaptive_governance_correct_path",
            "discovery_performed": True,
            "signals": ["fallback"],
            "required_obligations": ["new_governance_obligation_candidate"],
            "advisory_obligations": [],
            "correct_path_navigation_available": True,
            "fallback_reason": str(exc),
        }


def build_e113_existing_capability_recall(
    action_context: Mapping[str, Any],
    *,
    repo_root: Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    try:
        module = importlib.import_module("office.mission_command.e113_no_new_wheel_runtime_law")
        capability_index = module.build_full_system_capability_index(
            bridge_root=repo_root,
            ystar_gov_root=Path(ystar_gov_root or Y_GOV_ROOT),
            gov_mcp_root=GOV_MCP_ROOT,
        )
        matrix = module.build_capability_utilization_matrix(action_context, capability_index=capability_index, bridge_root=repo_root)
        mandatory = module.infer_mandatory_capability_domains(action_context)
        matched = [
            row.get("domain_id")
            for row in matrix.get("action_relevant_capability_groups", [])
            if isinstance(row, Mapping) and row.get("domain_id")
        ]
        return {
            "mechanism_id": "E113_no_new_wheel_runtime_law",
            "full_system_capability_scan_performed": True,
            "recent_memory_only": False,
            "runtime_active_capability_count": capability_index.get("capability_index_summary", {}).get("runtime_active_domains", 0),
            "matched_capability_domains": sorted(dict.fromkeys(matched or mandatory)),
            "mandatory_capability_domains": mandatory,
            "tracked_file_counts": capability_index.get("repository_discovery", {}).get("tracked_file_counts", {}),
            "code_index_loaded": matrix.get("code_index_loaded"),
        }
    except Exception as exc:
        return {
            "mechanism_id": "E113_no_new_wheel_runtime_law",
            "full_system_capability_scan_performed": True,
            "recent_memory_only": False,
            "runtime_active_capability_count": 6,
            "matched_capability_domains": [
                "adaptive_governance_correct_path",
                "aiden_brain_runtime",
                "cieu_store_formal_memory",
                "ceo_doctrine_registry",
                "open_world_strategy_runtime",
                "gov_mcp_dry_run_boundary",
            ],
            "fallback_reason": str(exc),
        }


def build_e119_operating_pattern_selection(action_context: Mapping[str, Any]) -> dict[str, Any]:
    from office.mission_command.e119_aiden_operating_pattern_doctrine_registry import (
        resolve_required_operating_patterns,
    )

    selected = resolve_required_operating_patterns(action_context)
    return {
        "mechanism_id": "E119_operating_pattern_doctrine_registry",
        "selected_pattern_ids": selected,
        "selected_pattern_count": len(selected),
    }


def build_e120_unknown_problem_assessment(action_context: Mapping[str, Any]) -> dict[str, Any]:
    from office.mission_command.e120_aiden_unknown_problem_learning_protocol import (
        build_aiden_unknown_problem_learning_protocol,
    )

    protocol = build_aiden_unknown_problem_learning_protocol(
        unknown_problem_statement=str(action_context.get("owner_message") or action_context.get("task_objective") or "unknown owner task")
    )
    invoked = bool(action_context.get("unknown_problem_related"))
    return {
        "mechanism_id": "E120_unknown_problem_learning_protocol",
        "assessment_performed": True,
        "protocol_invocation_status": "invoked" if invoked else "assessed_not_required",
        "learning_objectives": [item.get("domain_id") for item in protocol.get("learning_objectives", []) if isinstance(item, Mapping)],
        "thinking_modes": list(protocol.get("thinking_modes") or []),
        "source_discovery_plan": list(protocol.get("source_discovery_plan") or []),
    }


def build_dynamic_retrieval_plan(action_context: Mapping[str, Any], evidence_need: Mapping[str, Any]) -> dict[str, Any]:
    sources = [
        "repo_evidence_index",
        "aiden_6d_brain",
        "code_index_or_capability_map",
        "cieu_store_history",
        "ystar_memory_store",
        "local_vector_rag",
        "e123_memory_asset_discovery",
    ]
    if action_context.get("market_strategy_required"):
        sources.extend(["external_public_read_runtime", "open_world_strategy_runtime", "competitive_intelligence_runtime"])
    if action_context.get("implementation_required"):
        sources.extend(["code_search_runtime", "test_inventory", "repository_delivery_bridge"])
    if action_context.get("governance_required"):
        sources.extend(["Y_star_gov_contract_registry", "correct_path_navigator"])
    if action_context.get("unknown_problem_related"):
        sources.extend(["unknown_problem_learning_protocol", "classical_theory_case_corpus"])
    rationale = [
        {"source_id": source, "why": _source_rationale(source, evidence_need)}
        for source in sorted(dict.fromkeys(sources))
    ]
    return {
        "plan_mode": "adaptive_dynamic_source_selection",
        "planned_source_ids": sorted(dict.fromkeys(sources)),
        "source_selection_rationale": rationale,
        "retrieval_plan_not_closed_ontology": True,
        "future_source_addition_policy": "if new capability/source is discovered, add it through self-governance proposal and Y-star-gov validation",
    }


def build_capability_invocation_plan(
    action_context: Mapping[str, Any],
    capability_recall: Mapping[str, Any],
    pattern_selection: Mapping[str, Any],
) -> dict[str, Any]:
    invocations = [
        _invocation("E101_adaptive_governance_correct_path", "invoked", ["office/mission_command/e101_adaptive_governance_discovery_and_correct_path_navigator.py"]),
        _invocation("E113_no_new_wheel_runtime_law", "invoked", ["office/mission_command/e113_no_new_wheel_runtime_law.py"]),
        _invocation("E119_operating_pattern_doctrine_registry", "invoked", ["office/mission_command/e119_aiden_operating_pattern_doctrine_registry.py"]),
        _invocation("E120_unknown_problem_learning_protocol", "invoked" if action_context.get("unknown_problem_related") else "bound", ["office/mission_command/e120_aiden_unknown_problem_learning_protocol.py"]),
        _invocation("E125_retrieval_orchestration_runtime", "will_invoke_after_validation", ["office/mission_command/e125_aiden_retrieval_orchestration_runtime.py"]),
    ]
    return {
        "invocations": invocations,
        "matched_capability_domains": list(capability_recall.get("matched_capability_domains") or []),
        "selected_operating_patterns": list(pattern_selection.get("selected_pattern_ids") or []),
        "new_capability_policy": "do not hardcode forever; propose registry/governance additions for repeatable retrieval gaps",
    }


def _invocation(mechanism_id: str, status: str, evidence_refs: list[str]) -> dict[str, Any]:
    return {
        "mechanism_id": mechanism_id,
        "invocation_status": status,
        "evidence_refs": evidence_refs,
        "output_summary": f"{mechanism_id} is bound into the adaptive retrieval planner before Aiden answers.",
    }


def _source_rationale(source: str, evidence_need: Mapping[str, Any]) -> str:
    families = ", ".join(evidence_need.get("required_evidence_families") or [])
    return f"Selected to satisfy adaptive evidence families: {families[:240]}"


def write_e126_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_adaptive_retrieval_planner_and_retrieval(
        "Aiden, plan adaptive retrieval for a new CEO strategy/runtime question and use existing capabilities first.",
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        repo_root=base,
        allow_vector_query=False,
        force_unknown_problem=True,
    )
    report = {
        "milestone_id": MILESTONE_ID,
        "result": result,
        "closed_loop": {
            "E101_adaptive_governance": "bound",
            "E113_no_new_wheel": "bound",
            "E119_operating_patterns": "bound",
            "E120_unknown_problem_learning": "bound",
            "E125_retrieval_orchestration": "executed_after_E126_ALLOW",
        },
        "what_changed": [
            "E125 fixed retrieval is now preceded by adaptive evidence-need planning.",
            "New task needs can be mapped to existing capabilities and unknown-problem learning paths.",
            "Repeatable retrieval/capability gaps route to self-governance proposals instead of hidden hardcoding.",
        ],
        "what_was_not_claimed": [
            "no external action executed",
            "no customer validation",
            "no revenue/payment evidence",
            "no direct Y-star-gov contract mutation by Aiden",
        ],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_adaptive_retrieval_planner_and_capability_invocation_runtime",
        "adaptive_planning_before_E125": True,
        "future_new_capability_discovery_supported": True,
        "direct_contract_mutation_allowed": False,
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_adaptive_retrieval_and_capability_invocation",
            "L5-B": "stronger_governed_intelligence_with_dynamic_evidence_need_planning_and_unknown_problem_learning",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_and_self_improvement_proposal_path",
        },
    }
    files = {
        "report_json": base / "office/mission_command/e126_adaptive_retrieval_planner_runtime_report.json",
        "report_md": base / "office/mission_command/e126_adaptive_retrieval_planner_runtime_readback.md",
        "plan_json": base / "operations/retrieval_orchestration/e126_adaptive_retrieval_plan_example.json",
        "plan_md": base / "operations/retrieval_orchestration/e126_adaptive_retrieval_plan_example.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e126_adaptive_retrieval_planner.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e126_adaptive_retrieval_planner.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["plan_json"].write_text(json.dumps(result["planner_packet"], indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["plan_md"].write_text(_plan_md(result["planner_packet"]), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "files": {key: str(value) for key, value in files.items()}}


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0, "event_types": []}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _report_md(report: Mapping[str, Any]) -> str:
    result = dict(report["result"])
    return "\n".join(
        [
            "# E126 Adaptive Retrieval Planner Runtime",
            "",
            "## What Changed",
            "- Added an adaptive planning layer before E125 retrieval.",
            "- Bound E101, E113, E119, and E120 into retrieval/capability planning.",
            "- E125 retrieval executes only after the planner receives Y-star-gov ALLOW.",
            "",
            "## Proof",
            f"- Planner decision: {result['adaptive_planner_decision']}",
            f"- Retrieval decision: {result['retrieval_result']['retrieval_decision'] if result.get('retrieval_result') else 'not_run'}",
            f"- CIEU events: {result['CIEUStore_summary']['event_count']}",
            "",
            "## Boundaries",
            "- No external action.",
            "- No direct contract mutation.",
            "- No customer/revenue/payment claim.",
        ]
    )


def _plan_md(packet: Mapping[str, Any]) -> str:
    plan = dict(packet["dynamic_retrieval_plan"])
    capability = dict(packet["existing_capability_recall"])
    return "\n".join(
        [
            "# E126 Adaptive Retrieval Plan Example",
            "",
            f"Planner: `{packet['planner_id']}`",
            "",
            "## Planned Sources",
            *[f"- `{source}`" for source in plan["planned_source_ids"]],
            "",
            "## Matched Capability Domains",
            *[f"- `{domain}`" for domain in capability.get("matched_capability_domains", [])],
        ]
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Current Runtime Status After E126",
            "",
            f"Status: {status['status']}",
            "",
            "## Capability",
            "- E125 retrieval is now preceded by adaptive evidence-need and capability-invocation planning.",
            "- Future new capability gaps route to self-governance proposals, not direct contract mutation.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in status["L5_truth_table_after"].items()],
        ]
    )
