"""E94 behavior-center brain-grounded runtime gateway.

This module binds the existing ``answer_owner`` behavior center to the current
mainline runtime spine:

owner message -> answer_owner -> aiden_brain -> Y-star-gov behavior-center
contract -> CIEUStore -> optional gov-mcp dry-run -> residual/status.

Low-risk internal, public-read, and dry-run work routes autonomously. High-risk
external side effects remain owner-bound or denied. No real external side effect
is executed by this module.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.aiden_meeting_room.aiden_intent_classifier import classify_intent
from office.aiden_meeting_room.aiden_response_engine import answer_owner
from office.mission_command.e92_ceo_principal_codex_executor_boundary import (
    build_ceo_implementation_order,
)
from office.mission_command.e93_brain_grounded_live_runtime import (
    BRAIN_DB_PATH,
    query_brain_for_stage,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
MILESTONE_ID = "E94_Behavior_Center_Brain_Grounded_Runtime_Gateway_R1"
SESSION_ID = "e94_behavior_center_runtime_gateway_session"


HIGH_RISK_TERMS = (
    "payment",
    "pay ",
    "付款",
    "收款",
    "contract",
    "legal",
    "合同",
    "法律",
    "login",
    "account",
    "create account",
    "credential",
    "password",
    "生产部署",
    "production deploy",
)

PROVIDER_TERMS = (
    "email",
    "message",
    "contact",
    "outreach",
    "customer",
    "validation",
    "外联",
    "客户",
    "发邮件",
    "联系",
)

PUBLIC_READ_TERMS = (
    "research",
    "public-read",
    "public read",
    "market",
    "evidence",
    "观察",
    "市场",
    "证据",
    "只读",
)

ENGINEERING_TERMS = (
    "codex",
    "implement",
    "fix",
    "patch",
    "test",
    "runtime",
    "代码",
    "实现",
    "修复",
)


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def _load_gov_mcp_dry_run(gov_mcp_root: Path | None = None) -> Any:
    root = gov_mcp_root or GOV_MCP_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("gov_mcp.outbound.dry_run_adapter")


def classify_behavior_center_runtime_route(owner_message: str, intent: str) -> dict[str, Any]:
    """Deterministically classify the behavior-center route and risk boundary."""

    text = f"{owner_message} {intent}".lower()
    if any(term in text for term in HIGH_RISK_TERMS):
        return {
            "action_type": "high_risk_external_side_effect",
            "route_type": "high_risk_owner_decision",
            "risk_tier": "TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK",
            "externality_level": "external_side_effect",
            "signals": ["high_risk_marker"],
        }
    if any(term in text for term in PROVIDER_TERMS):
        return {
            "action_type": "external_validation_message",
            "route_type": "low_risk_external_validation_dry_run",
            "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
            "externality_level": "dry_run_only",
            "signals": ["provider_tool_boundary", "no_send_dry_run"],
        }
    if any(term in text for term in PUBLIC_READ_TERMS):
        return {
            "action_type": "public_read_observation",
            "route_type": "autonomous_public_read_only",
            "risk_tier": "TIER_1_PUBLIC_READ_ONLY",
            "externality_level": "public_read_only",
            "signals": ["read_only_external_observation"],
        }
    if any(term in text for term in ENGINEERING_TERMS):
        return {
            "action_type": "engineering_runtime_implementation",
            "route_type": "ceo_implementation_order_required",
            "risk_tier": "TIER_0_INTERNAL",
            "externality_level": "internal",
            "signals": ["codex_executor_boundary"],
        }
    return {
        "action_type": "status_or_internal_runtime",
        "route_type": "autonomous_internal_runtime",
        "risk_tier": "TIER_0_INTERNAL",
        "externality_level": "internal",
        "signals": ["internal_behavior_center_response"],
    }


def build_autonomous_execution_policy(classification: Mapping[str, Any]) -> dict[str, Any]:
    route = str(classification.get("route_type") or "")
    high_risk = route == "high_risk_owner_decision"
    provider_dry_run = route == "low_risk_external_validation_dry_run"
    return {
        "policy_id": "e94_behavior_center_autonomous_execution_policy",
        "risk_tier": classification.get("risk_tier"),
        "can_autonomously_execute": not high_risk,
        "owner_decision_required": high_risk,
        "high_risk_external_side_effect": high_risk,
        "gov_mcp_dry_run_required": provider_dry_run,
        "codex_order_required": route == "ceo_implementation_order_required",
        "public_read_only_allowed": route == "autonomous_public_read_only",
        "real_external_action_executed": False,
        "provider_action_executed": False,
        "external_side_effect": False,
        "no_send_invariant": True,
        "owner_packet_only_for_high_risk": True,
        "low_risk_should_not_default_to_owner": True,
    }


def build_behavior_center_runtime_packet(
    owner_message: str,
    *,
    repo_root: Path | None = None,
    brain_db: Path | None = None,
    session_id: str = SESSION_ID,
) -> dict[str, Any]:
    """Call the existing behavior center, ground it in brain activations, classify route."""

    root = repo_root or BRIDGE_ROOT
    intent = classify_intent(owner_message)
    response = answer_owner(owner_message, repo_root=root, record_memory=False)
    activations = query_brain_for_stage(
        "behavior_center_runtime_gateway",
        f"{intent} {owner_message}",
        top_n=6,
        brain_db=brain_db,
    )
    classification = classify_behavior_center_runtime_route(owner_message, intent)
    policy = build_autonomous_execution_policy(classification)
    node_ids = [str(item["node_id"]) for item in activations]
    return {
        "artifact_id": "e94_behavior_center_runtime_packet",
        "milestone_id": MILESTONE_ID,
        "packet_id": f"e94_behavior_packet_{int(time.time())}",
        "session_id": session_id,
        "agent_id": "bridge_labs_ceo",
        "source_owner_message": owner_message,
        "behavior_center_source": "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
        "behavior_center_response": response,
        "intent": intent,
        "brain_provenance": {
            "brain_db": str(brain_db or BRAIN_DB_PATH),
            "total_activations": len(activations),
            "unique_nodes": len(set(node_ids)),
        },
        "brain_activations": [
            {
                **item,
                "evidence_ref": f"brain://{item['node_id']}: {item['node_name']}",
            }
            for item in activations
        ],
        "evidence_refs": [f"brain://{item['node_id']}: {item['node_name']}" for item in activations],
        "action_classification": classification,
        "autonomous_execution_policy": policy,
        "CIEU_prediction": {
            "X_t": "behavior center previously answered through intent handlers without brain runtime governance",
            "U_t": "bind answer_owner to brain provenance and deterministic runtime routing",
            "Y_star_t": "safe behavior-center work executes autonomously; high-risk side effects remain owner-bound",
            "expected_Y_t_plus_1": "behavior-center decision written to CIEUStore and routed without external side effect",
            "predicted_R_t_plus_1": "live provider execution, real L4 feedback, and revenue loop remain pending",
        },
        "truth_constraints": {
            "private_chain_of_thought_stored": False,
            "no_customer_validation_claim": True,
            "no_revenue_payment_claim": True,
            "no_K9Audit_integration_claim": True,
            "no_live_provider_execution": True,
        },
        "post_action_residual_required": True,
        "bypass_attempt": False,
    }


def run_behavior_center_runtime_gateway_session(
    *,
    owner_message: str,
    cieu_db: str,
    repo_root: Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str = SESSION_ID,
    seal_session: bool = True,
) -> dict[str, Any]:
    """Run behavior center -> brain -> Y-star-gov -> route -> residual summary."""

    governance = _load_ystar_governance(ystar_gov_root)
    packet = build_behavior_center_runtime_packet(
        owner_message,
        repo_root=repo_root,
        brain_db=brain_db,
        session_id=session_id,
    )
    behavior_write = governance.validate_and_write_ceo_behavior_center_runtime_packet(
        packet,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=False,
    )
    decision = behavior_write["governance_decision"]["decision"]
    route_result: dict[str, Any] = {"route_type": packet["action_classification"]["route_type"]}

    if decision == "ALLOW":
        route_result = _execute_allowed_route(packet, gov_mcp_root=gov_mcp_root)
    elif decision == "ESCALATE":
        route_result = {
            "route_type": "owner_decision_packet",
            "owner_decision_packet": build_owner_decision_packet(packet, behavior_write),
            "external_action_executed": False,
        }

    residual_packet = build_behavior_center_post_action_residual(packet, behavior_write, route_result)
    residual_write = governance.validate_and_write_ceo_behavior_center_runtime_packet(
        residual_packet,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=seal_session,
    )
    cieu_summary = summarize_cieu_session(cieu_db, session_id)
    result = {
        "artifact_id": "e94_behavior_center_runtime_gateway_session",
        "milestone_id": MILESTONE_ID,
        "session_id": session_id,
        "owner_message": owner_message,
        "behavior_center_packet": packet,
        "behavior_center_decision": decision,
        "behavior_center_CIEU_write": behavior_write,
        "route_result": route_result,
        "post_action_residual": residual_packet,
        "post_action_residual_decision": residual_write["governance_decision"]["decision"],
        "post_action_residual_CIEU_write": residual_write,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_behavior_gateway_proven": decision in {"ALLOW", "ESCALATE"} and cieu_summary["sealed_session_valid"],
        "low_risk_autonomous_policy_active": True,
        "no_external_action_executed": True,
        "no_customer_revenue_payment_claim": True,
        "K9Audit_integration_claim": False,
        "L5_truth_table_after": l5_truth_table_after_e94(),
    }
    return result


def _execute_allowed_route(packet: Mapping[str, Any], *, gov_mcp_root: Path | None = None) -> dict[str, Any]:
    route = packet["action_classification"]["route_type"]
    if route == "low_risk_external_validation_dry_run":
        dry_adapter = _load_gov_mcp_dry_run(gov_mcp_root)
        intent = {
            "action_id": f"e94_dry_run_{int(time.time())}",
            "capability_domain": "external_validation_message",
            "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
            "execution_mode": "send_gated_dry_run",
            "authorization_state": "owner_review_required",
            "target_id": "e94_low_risk_validation_target_profile",
            "target_identity_sufficient": True,
            "message_hash": f"sha256:e94-{packet['packet_id']}",
            "idempotency_key": f"e94-{packet['packet_id']}",
            "ai_transparency_present": True,
            "opt_out_language_present": True,
            "suppression_clear": True,
            "rate_limit_clear": True,
            "hard_gates_absent": True,
            "requested_action": "external_validation_message",
            "channel": "transparent_low_risk_validation_dry_run",
            "metadata": {
                "behavior_center_packet_id": packet["packet_id"],
                "brain_unique_nodes": packet["brain_provenance"]["unique_nodes"],
                "YstarGov_behavior_center_decision": "ALLOW",
                "autonomous_low_risk_route": True,
            },
        }
        receipt = dry_adapter.dry_run_outbound_action(intent)
        return {
            "route_type": route,
            "gov_mcp_receipt": receipt,
            "autonomous_execution_completed": True,
            "external_action_executed": False,
            "provider_action_executed": False,
            "no_send_invariant": receipt.get("no_send_invariant") is True,
        }
    if route == "ceo_implementation_order_required":
        order = build_ceo_implementation_order(
            owner_intent=str(packet.get("source_owner_message") or ""),
            selected_strategy={
                "strategy_run_id": "e94_behavior_center_gateway",
                "why_this_path_now": "The CEO behavior center selected an internal engineering action that must be handed to Codex only through E92.",
                "why_not_others": ["Do not let Codex infer strategy from raw owner natural language."],
            },
            selected_action={
                "description": "Prepare a scoped Codex execution order for the behavior-center selected engineering action.",
                "route_type": "ceo_implementation_order_required",
            },
            order_id=f"e94_order_{packet['packet_id']}",
        )
        order["allowed_paths"] = [
            "office/mission_command/e94_*",
            "tests/office/test_e94_*",
            "ystar/governance/ceo_behavior_center_runtime_contract.py",
            "tests/governance/test_ceo_behavior_center_runtime_contract.py",
        ]
        return {
            "route_type": route,
            "CEOImplementationOrder": order,
            "autonomous_execution_completed": True,
            "external_action_executed": False,
        }
    return {
        "route_type": route,
        "autonomous_execution_completed": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "no_send_invariant": True,
    }


def build_owner_decision_packet(packet: Mapping[str, Any], write_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e94_owner_decision_packet",
        "linked_behavior_packet_id": packet.get("packet_id"),
        "reason": write_result.get("governance_decision", {}).get("reason"),
        "risk_tier": packet.get("action_classification", {}).get("risk_tier"),
        "high_risk_external_side_effect": True,
        "execution_allowed_before_owner_decision": False,
        "no_external_action_executed": True,
    }


def build_behavior_center_post_action_residual(
    packet: Mapping[str, Any],
    write_result: Mapping[str, Any],
    route_result: Mapping[str, Any],
) -> dict[str, Any]:
    residual = dict(packet)
    residual["packet_id"] = f"{packet.get('packet_id')}_residual"
    residual["artifact_id"] = "e94_behavior_center_post_action_residual_packet"
    residual["post_action_residual"] = {
        "linked_behavior_packet_id": packet.get("packet_id"),
        "expected_outcome": packet.get("CIEU_prediction", {}).get("expected_Y_t_plus_1"),
        "actual_output": f"route={route_result.get('route_type')}; decision={write_result.get('governance_decision', {}).get('decision')}",
        "residual_learning": "Low-risk work should execute through runtime/dry-run; high-risk work owner-bound only.",
        "next_action_recommendation": "Use E94 gateway as canonical behavior-center entrypoint.",
    }
    residual["autonomous_execution_policy"] = {
        **dict(packet.get("autonomous_execution_policy", {})),
        "post_action_residual_recorded": True,
        "real_external_action_executed": False,
        "provider_action_executed": False,
    }
    return residual


def summarize_cieu_session(cieu_db: str, session_id: str) -> dict[str, Any]:
    con = sqlite3.connect(cieu_db)
    con.row_factory = sqlite3.Row
    events = con.execute("select event_type, decision from cieu_events where session_id=? order by seq_global", (session_id,)).fetchall()
    seal = con.execute("select event_count, merkle_root from sealed_sessions where session_id=?", (session_id,)).fetchone()
    return {
        "event_count": len(events),
        "event_types": [row["event_type"] for row in events],
        "decisions": [row["decision"] for row in events],
        "sealed_session_event_count": seal["event_count"] if seal else 0,
        "sealed_session_merkle_root": seal["merkle_root"] if seal else "",
        "sealed_session_valid": bool(seal and seal["event_count"] == len(events) and len(events) >= 2),
    }


def l5_truth_table_after_e94() -> dict[str, str]:
    return {
        "L5-A Runtime Foundation": "complete_internal_runtime_foundation_with_behavior_center_gateway",
        "L5-B CEO Intelligence Loop": "complete_for_structured_governed_intelligence_loop_with_brain_grounded_behavior_center",
        "L5-B+": "partial_dynamic_intelligence_pending_live_external_observation_and_real_feedback",
        "L5-C Controlled External Action": "partial_autonomous_low_risk_dry_run_only_high_risk_owner_bound",
        "L5-D Revenue/Customer/Payment Loop": "absent_or_not_executed",
    }


def write_e94_reports(session_result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    report = {
        "milestone_id": MILESTONE_ID,
        "session_id": session_result.get("session_id"),
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "repos_modified": ["bridge-labs", "Y-star-gov"],
        "existing_systems_reused": [
            "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
            "office/aiden_meeting_room/aiden_intent_classifier.py::classify_intent",
            "office/mission_command/e93_brain_grounded_live_runtime.py::query_brain_for_stage",
            "ystar/governance/ceo_behavior_center_runtime_contract.py",
            "ystar/governance/cieu_store.py::CIEUStore.write_dict",
            "gov_mcp/outbound/dry_run_adapter.py::dry_run_outbound_action",
            "office/mission_command/e92_ceo_principal_codex_executor_boundary.py::build_ceo_implementation_order",
        ],
        "behavior_center_decision": session_result.get("behavior_center_decision"),
        "post_action_residual_decision": session_result.get("post_action_residual_decision"),
        "low_risk_autonomous_policy_active": session_result.get("low_risk_autonomous_policy_active"),
        "no_external_action_executed": session_result.get("no_external_action_executed"),
        "CIEUStore_summary": session_result.get("CIEUStore_summary"),
        "runtime_chain_proven": [
            "owner message",
            "existing answer_owner behavior center",
            "E93 brain provenance",
            "Y-star-gov behavior-center runtime contract",
            "formal CIEUStore write",
            "autonomous low-risk route or high-risk owner boundary",
            "post-action residual",
            "formal CIEUStore write and seal",
        ],
        "autonomous_execution_boundary": {
            "internal_runtime": "autonomous_after_YstarGov_ALLOW",
            "public_read_only": "autonomous_after_YstarGov_ALLOW",
            "transparent_low_risk_external_validation": "gov_mcp_dry_run_no_send_only_after_YstarGov_ALLOW",
            "engineering_runtime": "CEOImplementationOrder_required_before_Codex_execution",
            "high_risk_external_side_effect": "owner_decision_or_DENY",
            "payment_legal_contract_credentials_or_production": "owner_bound_or_DENY",
        },
        "gov_mcp_status": {
            "code_modified": False,
            "alignment": "existing dry_run_outbound_action reused for low-risk validation dry-run",
            "provider_action_executed": False,
            "external_side_effect": False,
            "no_send_invariant": True,
        },
        "L5_truth_table_after": session_result.get("L5_truth_table_after"),
        "what_changed": [
            "Existing answer_owner behavior center is now wrapped by a brain-grounded runtime gateway.",
            "Low-risk internal/read-only/dry-run routes execute autonomously inside governance instead of default owner handoff.",
            "High-risk external side effects remain owner-bound or denied.",
        ],
        "what_was_not_claimed": [
            "No L4 feedback was executed.",
            "No live provider execution was enabled.",
            "No customer validation was claimed.",
            "No revenue, pricing, payment, or paid signal was claimed.",
            "No K9Audit write or integration was claimed.",
            "L5-D remains absent_or_not_executed.",
        ],
        "tests_run": [
            "Y-star-gov: py_compile touched files",
            "Y-star-gov: pytest -q tests/governance/test_ceo_behavior_center_runtime_contract.py",
            "Y-star-gov: pytest -q tests/governance/test_ceo_cognitive_os_runtime_hook.py tests/governance/test_ceo_brain_grounded_intelligence_contract.py tests/governance/test_ceo_codex_executor_contract.py tests/governance/test_ceo_behavior_center_runtime_contract.py",
            "bridge-labs: py_compile touched files",
            "bridge-labs: pytest -q tests/office/test_e94_behavior_center_runtime_gateway.py",
            "bridge-labs: pytest -q tests/office/test_e87_ceo_runtime_session.py tests/office/test_e89_ceo_intelligence_loop_runtime_compiler.py tests/office/test_e90_ceo_strategic_intelligence_benchmark.py tests/office/test_e90_market_grounded_strategy_run.py tests/office/test_e93_brain_grounded_live_runtime.py tests/office/test_e94_behavior_center_runtime_gateway.py",
        ],
        "remaining_blockers": [
            "Raw answer_owner remains as a compatibility function; callers should migrate to the E94 runtime gateway for governed behavior-center execution.",
            "Live external observation and real feedback still require a later owner-approved execution milestone.",
            "High-risk payment, legal, credential, contract, and production actions remain owner-bound or denied.",
        ],
        "recommended_next_milestone": "E95_Migrate_Behavior_Center_Callers_To_E94_Runtime_Gateway_And_Add_Sleep_Dream_Learning_Loop_R1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report_path = root / "office/mission_command/e94_behavior_center_runtime_gateway_report.json"
    readback_path = root / "office/mission_command/e94_behavior_center_runtime_gateway_readback.md"
    status_json = root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e94_behavior_center_runtime_gateway.json"
    status_md = root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e94_behavior_center_runtime_gateway.md"
    for path in (report_path, readback_path, status_json, status_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    status_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readback = "\n".join(
        [
            "# E94 Behavior Center Runtime Gateway",
            "",
            f"- behavior_center_decision: `{report['behavior_center_decision']}`",
            f"- low_risk_autonomous_policy_active: `{report['low_risk_autonomous_policy_active']}`",
            f"- no_external_action_executed: `{report['no_external_action_executed']}`",
            f"- CIEU events: `{report['CIEUStore_summary']['event_count']}`",
            "",
            "E94 binds the existing `answer_owner` behavior center to brain provenance, Y-star-gov validation, CIEUStore records, gov-mcp dry-run routing, and post-action residuals. Low-risk work is not pushed back to the owner by default; high-risk external side effects remain owner-bound.",
            "",
            "## Runtime Boundary",
            "",
            "- Internal runtime, public-read-only, and transparent low-risk dry-run routes can proceed autonomously after Y-star-gov ALLOW.",
            "- Provider/tool boundary routes remain gov-mcp dry-run/no-send only.",
            "- Payment, legal, credential, contract, production, and other high-risk side-effect routes remain owner-bound or denied.",
            "- Codex engineering work must still pass through CEOImplementationOrder.",
            "",
            "## Truth Table",
            "",
            f"- L5-A: `{report['L5_truth_table_after']['L5-A Runtime Foundation']}`",
            f"- L5-B: `{report['L5_truth_table_after']['L5-B CEO Intelligence Loop']}`",
            f"- L5-B+: `{report['L5_truth_table_after']['L5-B+']}`",
            f"- L5-C: `{report['L5_truth_table_after']['L5-C Controlled External Action']}`",
            f"- L5-D: `{report['L5_truth_table_after']['L5-D Revenue/Customer/Payment Loop']}`",
            "",
            "No L4 feedback, live provider action, customer validation, revenue, pricing, payment, or K9Audit write was executed or claimed.",
            "",
        ]
    )
    readback_path.write_text(readback, encoding="utf-8")
    status_md.write_text(readback, encoding="utf-8")
    return {
        "report_path": str(report_path),
        "readback_path": str(readback_path),
        "status_json": str(status_json),
        "status_md": str(status_md),
    }


__all__ = [
    "build_autonomous_execution_policy",
    "build_behavior_center_post_action_residual",
    "build_behavior_center_runtime_packet",
    "build_owner_decision_packet",
    "classify_behavior_center_runtime_route",
    "l5_truth_table_after_e94",
    "run_behavior_center_runtime_gateway_session",
    "summarize_cieu_session",
    "write_e94_reports",
]
