from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    FixtureGlobalPublicReadProvider,
    PublicReadProvider,
)
from office.mission_command.e110_labs_universal_operating_control_plane import (
    build_operation_context,
    run_e110_controlled_aiden_strategy_session,
)
from office.mission_command.e92_ceo_principal_codex_executor_boundary import (
    build_ceo_implementation_order,
    build_codex_handoff_prompt_from_order,
)


MILESTONE_ID = "E111_Aiden_Host_Runtime_And_Autonomy_Control_Plane_R1"
HOST_RUNTIME_ID = "aiden_host_ceo_operating_daemon_v1"
SESSION_ID = "e111_aiden_host_runtime_cycle"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def build_aiden_company_mission_anchor() -> dict[str, Any]:
    return {
        "mission_id": "ystar_bridge_labs_autonomous_agent_company_os",
        "mission_statement": (
            "Build a high-intelligence, governance-bound CEO agent company runtime that can "
            "understand owner intent, discover value targets, recall capabilities and history, "
            "compare routes, choose the shortest credible cash path, act safely through governed "
            "orders and dry-run boundaries, learn from residuals, and move toward revenue without "
            "false customer/revenue/payment claims."
        ),
        "must_optimize_for": [
            "autonomous_value_discovery",
            "governed_value_creation",
            "residual_learning",
            "shortest_credible_cash_path",
            "low_owner_burden_for_low_risk_internal_work",
            "owner_gated_external_or_payment_actions",
        ],
        "must_not_claim": [
            "customer_validation_without_customer_evidence",
            "revenue_or_payment_without_transaction_evidence",
            "K9Audit_integration_without_write_bridge",
            "live_provider_execution_without_owner_approval",
            "L5-D completion_before_real_feedback_and_cash_loop",
        ],
    }


def build_first_principles_operating_model() -> dict[str, Any]:
    return {
        "model_id": "aiden_first_principles_company_operating_model_v1",
        "principles": [
            {
                "principle_id": "market_pull_before_internal_convenience",
                "rule": "Start from real buyer pain, substitutes, budget owner, urgency, and right-to-win before choosing implementation work.",
            },
            {
                "principle_id": "safety_enables_autonomy",
                "rule": "Low-risk internal work should proceed through deterministic controls; high-risk external/payment/customer actions become owner-gated packets.",
            },
            {
                "principle_id": "ceo_decides_codex_executes",
                "rule": "Aiden owns strategy and CEOImplementationOrder; Codex executes only the validated order and returns receipts.",
            },
            {
                "principle_id": "memory_is_governed_evidence",
                "rule": "Important decisions and residuals must be written through CIEUStore, not recent chat memory.",
            },
            {
                "principle_id": "do_not_rebuild_existing_systems",
                "rule": "Every cycle must orchestrate existing bridge-labs, Y-star-gov, gov-mcp, brain, doctrine, and Codex-boundary systems before creating new machinery.",
            },
            {
                "principle_id": "truth_over_motion",
                "rule": "No customer validation, payment, revenue, live provider, or K9Audit integration claim is allowed without real proof.",
            },
        ],
    }


def build_existing_capability_orchestration_map() -> dict[str, Any]:
    capabilities = [
        _cap("E110_labs_universal_operating_control_plane", "bridge-labs", "office/mission_command/e110_labs_universal_operating_control_plane.py", "non-bypassable front door for Labs behavior"),
        _cap("E89_ceo_intelligence_loop_runtime_compiler", "bridge-labs", "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py", "structured governed CEO cognition"),
        _cap("E90_ceo_strategic_intelligence_benchmark", "bridge-labs", "office/mission_command/e90_ceo_strategic_intelligence_benchmark.py", "deterministic strategy quality benchmark"),
        _cap("E108_live_global_open_world_strategy_runtime", "bridge-labs", "office/mission_command/e108_live_global_open_world_strategy_runtime.py", "open-world public-read value discovery and route ranking"),
        _cap("E92_CEOImplementationOrder", "bridge-labs", "office/mission_command/e92_ceo_principal_codex_executor_boundary.py", "CEO principal to Codex executor order boundary"),
        _cap("E101_adaptive_governance_correct_path_navigator", "bridge-labs", "office/mission_command/e101_adaptive_governance_discovery_and_correct_path_navigator.py", "adaptive governance discovery and repair navigation"),
        _cap("E94_behavior_center_brain_binding", "bridge-labs", "office/aiden_meeting_room/governed_gateway.py", "owner-facing behavior center with brain/governance path"),
        _cap("Y_star_gov_deterministic_governance", "Y-star-gov", "ystar/governance", "governance reflex center and deterministic validators"),
        _cap("CIEUStore_formal_memory", "Y-star-gov", "ystar/governance/cieu_store.py", "formal memory/evidence records"),
        _cap("gov_mcp_dry_run_no_send_boundary", "gov-mcp", "gov_mcp/outbound/dry_run_adapter.py", "provider/tool execution boundary with no-send receipts"),
    ]
    return {
        "map_id": "aiden_existing_capability_orchestration_map_v1",
        "principle": "orchestrate existing systems; do not create a second CEO, governance engine, provider executor, or ledger",
        "capabilities": capabilities,
    }


def build_autonomy_policy() -> dict[str, Any]:
    return {
        "policy_id": "aiden_autonomy_tier_policy_v1",
        "default_posture": "maximize safe autonomous progress for low-risk internal work; escalate only when authority, external side effects, or irreversible risk requires owner approval",
        "tiers": [
            {
                "tier_id": "autonomous_internal_low_risk",
                "allowed": True,
                "examples": ["repo read", "internal analysis", "report generation", "CIEU candidate/record write in test DB", "deterministic planning"],
                "requires": ["E110_gate", "Y-star-gov_validation", "CIEU_record", "post_action_residual"],
            },
            {
                "tier_id": "codex_executor_order_required",
                "allowed": True,
                "examples": ["code/test/report work in allowed repos"],
                "requires": ["CEOImplementationOrder", "Y-star-gov_order_validation", "CIEU_order_write", "CodexExecutionReceipt"],
            },
            {
                "tier_id": "gov_mcp_dry_run_only",
                "allowed": True,
                "examples": ["provider/tool preflight", "receipt simulation"],
                "requires": ["gov-mcp dry-run/no-send receipt", "provider_action_executed=false", "external_side_effect=false"],
            },
            {
                "tier_id": "owner_decision_required",
                "allowed": False,
                "examples": ["customer outreach", "publication", "L4 feedback execution", "scope/strategy authority change"],
                "requires": ["owner decision packet", "no-send default", "AI transparency", "opt-out where applicable"],
            },
            {
                "tier_id": "hard_deny",
                "allowed": False,
                "examples": ["payment execution", "live provider action without approval", "credential access", "false customer/revenue/K9Audit claims"],
                "requires": ["remove unsafe action", "return to governance navigator"],
            },
        ],
    }


def classify_autonomy_tier(action_context: Mapping[str, Any]) -> dict[str, Any]:
    if action_context.get("payment_related") is True or action_context.get("live_provider_execution_requested") is True:
        return _tier("hard_deny", "payment/live provider actions are irreversible or externally risky without explicit owner approval")
    if action_context.get("customer_contact") is True or action_context.get("publication") is True or action_context.get("L4_feedback_execution") is True:
        return _tier("owner_decision_required", "external/customer/public actions require owner decision packet and no-send default")
    if action_context.get("provider_tool_boundary") is True:
        return _tier("gov_mcp_dry_run_only", "provider/tool boundary may only produce no-send dry-run receipts")
    if action_context.get("codex_execution") is True or action_context.get("repo_mutation") is True:
        return _tier("codex_executor_order_required", "repo/code delivery must use CEOImplementationOrder and CodexExecutionReceipt")
    return _tier("autonomous_internal_low_risk", "internal analysis/planning/report/memory work may proceed through governance without pushing work back to owner")


def build_next_internal_value_creation_action(strategy_result: Mapping[str, Any]) -> dict[str, Any]:
    strategy = strategy_result.get("strategy") if isinstance(strategy_result.get("strategy"), Mapping) else {}
    selected = strategy.get("selected_strategy") if isinstance(strategy.get("selected_strategy"), Mapping) else {}
    selected_path = selected.get("current_best_first_cash_path") or "selected governed first-cash path"
    tier = classify_autonomy_tier({"repo_mutation": True, "codex_execution": True})
    return {
        "action_id": "e111_prepare_selected_value_target_no_send_execution_pack",
        "title": "Prepare a no-send value-target execution pack for the selected first-cash path",
        "description": (
            "Convert Aiden's selected strategy into internal artifacts only: buyer-pain hypothesis, competitor/substitute table, "
            "proof checklist, owner-gated L4 packet draft, and CodexImplementationOrder for the next engineering/reporting step."
        ),
        "selected_value_target": selected_path,
        "route_type": "codex_executor_order",
        "autonomy_tier": tier["tier_id"],
        "why_this_is_low_risk": "It creates internal evidence and owner-decision artifacts only; it does not contact customers or providers.",
        "external_action_candidate": False,
        "customer_contact": False,
        "publication": False,
        "payment_related": False,
        "provider_tool_boundary": False,
        "live_provider_execution_requested": False,
        "owner_decision_required_before_external_use": True,
        "expected_outputs": [
            "selected value-target evidence pack",
            "owner-gated L4 feedback packet draft",
            "CodexExecutionReceipt after implementation",
            "post-action residual learning candidate",
        ],
    }


def build_host_runtime_packet(
    *,
    owner_intent: str,
    strategy_result: Mapping[str, Any],
    order: Mapping[str, Any],
    order_write: Mapping[str, Any],
    prompt_generation_result: Mapping[str, Any],
) -> dict[str, Any]:
    strategy = strategy_result.get("strategy") if isinstance(strategy_result.get("strategy"), Mapping) else {}
    receipt = strategy_result.get("CEO_runtime_receipt") if isinstance(strategy_result.get("CEO_runtime_receipt"), Mapping) else {}
    control_gate = strategy_result.get("control_gate") if isinstance(strategy_result.get("control_gate"), Mapping) else {}
    selected = strategy.get("selected_strategy") if isinstance(strategy.get("selected_strategy"), Mapping) else {}
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    next_action = build_next_internal_value_creation_action(strategy_result)
    return {
        "artifact_id": "aiden_host_runtime_cycle_packet",
        "milestone_id": MILESTONE_ID,
        "host_runtime_id": HOST_RUNTIME_ID,
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "owner_intent": owner_intent,
        "mission_anchor": build_aiden_company_mission_anchor(),
        "first_principles_operating_model": build_first_principles_operating_model(),
        "existing_capability_orchestration_map": build_existing_capability_orchestration_map(),
        "autonomy_policy": build_autonomy_policy(),
        "universal_control_gate": {
            "Y_star_gov_universal_control_decision": receipt.get("Y_star_gov_universal_control_decision"),
            "runtime_may_continue": control_gate.get("runtime_may_continue") is True,
            "required_capabilities": [
                item.get("capability_id")
                for item in control_gate.get("control_packet", {}).get("required_capabilities", [])
                if isinstance(item, Mapping)
            ],
        },
        "value_discovery_cycle": {
            "market_strategy_decision": receipt.get("Y_star_gov_live_global_decision"),
            "math_model_decision": receipt.get("Y_star_gov_math_model_decision"),
            "open_world_scan_performed": scan.get("live_public_read_performed") is True,
            "scan_mode": receipt.get("scan_mode"),
            "evidence_count": receipt.get("evidence_count"),
            "route_candidate_count": receipt.get("route_candidate_count"),
            "selected_value_target": selected.get("current_best_first_cash_path"),
            "selected_route_id": selected.get("selected_route_id"),
            "anti_anchor_proven": scan.get("anchor_proximity_audit", {}).get("globally_ranked_against_non_adjacent_domains"),
        },
        "CEO_implementation_order": dict(order),
        "CEO_implementation_order_write": dict(order_write),
        "Codex_handoff_prompt_generation": {
            "decision": prompt_generation_result.get("prompt_generation_decision", {}).get("decision"),
            "generated_after_validated_cieu_written_order": prompt_generation_result.get("generated_after_validated_cieu_written_order") is True,
        },
        "next_action_recommendation": next_action,
        "post_cycle_residual_plan": {
            "residual_required": True,
            "future_evidence_to_compare": [
                "whether selected route survives owner-approved buyer feedback",
                "whether competitor/substitute risk was underestimated",
                "whether Codex implementation stayed inside CEOImplementationOrder",
            ],
            "learning_update_destination": "Y-star-gov CIEUStore plus Aiden brain after governed memory write path exists",
        },
        "truth_constraints": {
            "external_action_executed": False,
            "provider_action_executed": False,
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def run_aiden_host_runtime_cycle(
    *,
    cieu_db: str | Path,
    owner_intent: str = "Operate Y*Bridge Labs as an autonomous governed AI agent company and find the next safest value-creation target.",
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
    seal_session: bool = True,
) -> dict[str, Any]:
    selected_provider = provider
    if selected_provider is None and not allow_live_network:
        selected_provider = FixtureGlobalPublicReadProvider()
    cieu_path = str(cieu_db)
    strategy_result = run_e110_controlled_aiden_strategy_session(
        cieu_db=cieu_path,
        owner_intent=owner_intent,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        provider=selected_provider,
        allow_live_network=allow_live_network,
        seal_session=False,
    )
    next_action = build_next_internal_value_creation_action(strategy_result)
    strategy = strategy_result.get("strategy") if isinstance(strategy_result.get("strategy"), Mapping) else {}
    selected_strategy = strategy.get("selected_strategy") if isinstance(strategy.get("selected_strategy"), Mapping) else {}
    order = build_ceo_implementation_order(
        owner_intent=owner_intent,
        selected_strategy=selected_strategy,
        selected_action=next_action,
        order_id="e111_aiden_host_runtime_next_value_creation_order",
    )
    order.update(
        {
            "milestone_id": MILESTONE_ID,
            "allowed_repos": ["bridge-labs", "Y-star-gov", "gov-mcp"],
            "allowed_paths": [
                "office/mission_command/e111_*",
                "office/aiden_meeting_room/chat_router.py",
                "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e111_*",
                "tests/office/test_e111_*",
                "ystar/governance/aiden_host_runtime_contract.py",
                "tests/governance/test_aiden_host_runtime_contract.py",
            ],
            "likely_files_to_modify": [
                "office/mission_command/e111_aiden_host_runtime_and_autonomy_control_plane.py",
                "ystar/governance/aiden_host_runtime_contract.py",
                "tests/office/test_e111_aiden_host_runtime_and_autonomy_control_plane.py",
                "tests/governance/test_aiden_host_runtime_contract.py",
            ],
            "completion_criteria": [
                "Aiden host runtime cycle is validated by Y-star-gov",
                "E110 universal control is invoked before value discovery",
                "CEOImplementationOrder is validated and written before Codex prompt generation",
                "no external action, customer validation, revenue/payment, live provider execution, or K9Audit write occurs",
            ],
        }
    )
    governance = _load_ystar_governance(ystar_gov_root)
    order_write = governance.validate_and_write_ceo_implementation_order(
        order,
        cieu_db=cieu_path,
        session_id=SESSION_ID,
        seal_session=False,
    )
    prompt_generation_result = build_codex_handoff_prompt_from_order(
        order,
        order_write=order_write,
        cieu_db=cieu_path,
        ystar_gov_root=ystar_gov_root,
        session_id=SESSION_ID,
    )
    host_packet = build_host_runtime_packet(
        owner_intent=owner_intent,
        strategy_result=strategy_result,
        order=order,
        order_write=order_write,
        prompt_generation_result=prompt_generation_result,
    )
    host_governance = _load_ystar_module("ystar.governance.aiden_host_runtime_contract", ystar_gov_root)
    host_write = host_governance.validate_and_write_aiden_host_runtime_cycle(
        host_packet,
        cieu_db=cieu_path,
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = summarize_cieustore(cieu_path)
    proven = (
        strategy_result.get("end_to_end_controlled_strategy_proven") is True
        and order_write.get("governance_decision", {}).get("decision") == "ALLOW"
        and prompt_generation_result.get("prompt_generation_decision", {}).get("decision") == "ALLOW"
        and host_write.get("governance_decision", {}).get("decision") == "ALLOW"
        and summary["event_count"] >= 5
    )
    return {
        "artifact_id": "e111_aiden_host_runtime_cycle_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "host_runtime_id": HOST_RUNTIME_ID,
        "owner_intent": owner_intent,
        "strategy_result": strategy_result,
        "CEO_implementation_order": order,
        "order_write": order_write,
        "codex_handoff_prompt_generation": prompt_generation_result,
        "host_runtime_packet": host_packet,
        "host_runtime_write": host_write,
        "CIEUStore_summary": summary,
        "host_runtime_cycle_proven": proven,
        "next_action_recommendation": host_packet["next_action_recommendation"],
        "safety_statement": {
            "Aiden_is_CEO_principal": True,
            "Codex_is_executor_only": True,
            "low_risk_internal_autonomy_supported": True,
            "external_actions_owner_gated": True,
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_payment_claim": True,
            "gov_mcp_live_execution": False,
            "K9Audit_not_integrated": True,
        },
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation",
            "L5-B": "complete_for_structured_governed_intelligence_loop_with_host_runtime_autonomy_control",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
        },
    }


def write_e111_host_runtime_reports(
    *,
    cieu_db: str | Path,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    result = run_aiden_host_runtime_cycle(
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        provider=provider or FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )
    report = _completion_report(result)
    status = _runtime_status(result)
    files = {
        "report_json": base / "office/mission_command/e111_aiden_host_runtime_and_autonomy_control_plane_report.json",
        "report_md": base / "office/mission_command/e111_aiden_host_runtime_and_autonomy_control_plane_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e111_aiden_host_runtime_and_autonomy_control_plane.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e111_aiden_host_runtime_and_autonomy_control_plane.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_markdown(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return report


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT event_type, decision FROM cieu_events ORDER BY seq_global").fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    packet = result["host_runtime_packet"]
    return {
        "milestone_id": MILESTONE_ID,
        "host_runtime_id": result["host_runtime_id"],
        "host_runtime_cycle_proven": result["host_runtime_cycle_proven"],
        "mission_anchor": packet["mission_anchor"],
        "first_principles_operating_model": packet["first_principles_operating_model"],
        "existing_systems_orchestrated": [
            item["capability_id"] for item in packet["existing_capability_orchestration_map"]["capabilities"]
        ],
        "autonomy_policy": packet["autonomy_policy"],
        "universal_control_decision": packet["universal_control_gate"]["Y_star_gov_universal_control_decision"],
        "value_discovery_cycle": packet["value_discovery_cycle"],
        "CEOImplementationOrder_status": result["order_write"]["governance_decision"]["decision"],
        "Codex_prompt_generation_status": result["codex_handoff_prompt_generation"]["prompt_generation_decision"]["decision"],
        "Y_star_gov_host_runtime_decision": result["host_runtime_write"]["governance_decision"]["decision"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "next_action_recommendation": result["next_action_recommendation"],
        "safety_statement": result["safety_statement"],
        "L5_truth_table_after": result["L5_truth_table_after"],
        "what_was_not_claimed": [
            "no L4 feedback executed",
            "no customer validation",
            "no revenue/payment signal",
            "no live provider execution",
            "no K9Audit integration",
        ],
    }


def _runtime_status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "host_runtime_cycle_proven": result["host_runtime_cycle_proven"],
        "runtime_status": "host_level_ceo_operating_loop_structurally_enforceable",
        "L5-A": result["L5_truth_table_after"]["L5-A"],
        "L5-B": result["L5_truth_table_after"]["L5-B"],
        "L5-C": result["L5_truth_table_after"]["L5-C"],
        "L5-D": result["L5_truth_table_after"]["L5-D"],
        "remaining_blockers": [
            "real owner-approved L4 feedback still pending",
            "live provider execution still disabled",
            "customer/revenue/payment loop still absent",
            "K9Audit write bridge still not integrated",
        ],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    return (
        "# E111 Aiden Host Runtime And Autonomy Control Plane\n\n"
        f"- Host runtime cycle proven: {str(report['host_runtime_cycle_proven']).lower()}\n"
        f"- Universal control decision: {report['universal_control_decision']}\n"
        f"- CEOImplementationOrder status: {report['CEOImplementationOrder_status']}\n"
        f"- Codex prompt generation status: {report['Codex_prompt_generation_status']}\n"
        f"- Y-star-gov host runtime decision: {report['Y_star_gov_host_runtime_decision']}\n"
        f"- CIEU events: {report['CIEUStore_summary']['event_count']}\n\n"
        "## Meaning\n\n"
        "Aiden is now modeled as a host-level CEO operating loop: mission anchor, first-principles operating model, "
        "existing capability orchestration, autonomy tiers, E110 value discovery, CEOImplementationOrder, Codex prompt governance, "
        "Y-star-gov validation, CIEUStore write, and next-action recommendation.\n\n"
        "No external action, customer validation, revenue/payment signal, live provider execution, or K9Audit integration is claimed.\n"
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E111\n\n"
        f"- Runtime status: {status['runtime_status']}\n"
        f"- L5-A: {status['L5-A']}\n"
        f"- L5-B: {status['L5-B']}\n"
        f"- L5-C: {status['L5-C']}\n"
        f"- L5-D: {status['L5-D']}\n"
    )


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    return _load_ystar_module("ystar.governance", ystar_gov_root)


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _cap(capability_id: str, owner_repo: str, source_path: str, role: str) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "owner_repo": owner_repo,
        "source_paths": [source_path],
        "runtime_status": "runtime_active",
        "role": role,
    }


def _tier(tier_id: str, reason: str) -> dict[str, Any]:
    return {"tier_id": tier_id, "reason": reason}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "HOST_RUNTIME_ID",
    "MILESTONE_ID",
    "SESSION_ID",
    "build_aiden_company_mission_anchor",
    "build_autonomy_policy",
    "build_existing_capability_orchestration_map",
    "build_first_principles_operating_model",
    "build_host_runtime_packet",
    "build_next_internal_value_creation_action",
    "classify_autonomy_tier",
    "run_aiden_host_runtime_cycle",
    "summarize_cieustore",
    "write_e111_host_runtime_reports",
]
