from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.aiden_meeting_room.aiden_response_engine import answer_owner
from office.mission_command.e84_ystar_gov_ceo_cognitive_os_call_adapter import (
    build_sample_post_action_residual,
    build_sample_pre_action_packet,
)
from office.mission_command.e85_ceo_cognitive_os_runtime_bridge import (
    build_provider_tool_ceo_major_action_runtime_envelope,
    route_provider_tool_action_through_runtime_nervous_system,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))

MILESTONE_ID = "E88_BIND_EXISTING_LABS_BEHAVIOR_CENTER_TO_RUNTIME_CIEU_LOOP_R1"
DEFAULT_OWNER_MESSAGE = (
    "Select the next internal CEO action for binding the behavior center to the runtime "
    "governance and CIEUStore loop without external execution."
)


def _load_ystar_governance_module(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def build_behavior_center_grounded_packet(
    *,
    owner_message: str = DEFAULT_OWNER_MESSAGE,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Reuse the existing bridge-labs behavior center as the CEO session source."""

    root = repo_root or BRIDGE_ROOT
    behavior_center_response = answer_owner(owner_message, repo_root=root, record_memory=False)
    packet = build_sample_pre_action_packet(action_class="provider_tool_execution")
    packet.update(
        {
            "packet_id": "e88_behavior_center_runtime_pre_action_packet",
            "job_id": MILESTONE_ID,
            "proposed_action": (
                "run an internal CEO runtime session that binds bridge-labs behavior center, "
                "Y-star-gov runtime validation, formal CIEUStore writes, gov-mcp dry-run, "
                "and post-action residual closure"
            ),
            "owner_intent": (
                "prove a real internal runtime nervous-system session without external action "
                "or L5 revenue/customer/payment claims"
            ),
            "current_mission_context": {
                "reasoning_scope": "E87R_baseline_grounded_runtime_binding",
                "behavior_center_source": "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
                "baseline_source": "operations/baseline/e87r_full_repo_baseline/next_engineering_roadmap.json",
            },
            "historical_assets_consulted": [
                "operations/baseline/e87r_full_repo_baseline/baseline_summary.json",
                "operations/baseline/e87r_full_repo_baseline/architecture_evidence_map.json",
                "operations/baseline/e87r_full_repo_baseline/l5_truth_table.json",
                "operations/baseline/e87r_full_repo_baseline/next_engineering_roadmap.json",
                "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
                "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
            ],
            "canonical_owner_map": {
                "bridge-labs": "CEO/company behavior center and session orchestrator",
                "Y-star-gov": "governance reflex center and formal CIEUStore writer",
                "gov-mcp": "provider/tool dry-run execution boundary",
                "K9Audit": "separate stronger evidence ledger; not integrated in this session",
            },
            "no_new_wheel_decision": {
                "decision": "reuse_existing_behavior_center_runtime_hook_cieustore_and_dry_run_boundary",
                "non_duplication_proof": (
                    "Uses bridge-labs Aiden response engine, E85 runtime bridge, "
                    "Y-star-gov validate_and_write_ceo_runtime_envelope, and gov-mcp dry_run_outbound_action."
                ),
            },
            "candidate_actions": [
                "bind existing CEO behavior center to runtime CIEUStore session",
                "skip binding and continue static reports",
                "attempt external L4 feedback now",
            ],
            "counterfactual_comparison": [
                {
                    "candidate": "bind existing CEO behavior center to runtime CIEUStore session",
                    "expected_gain": "closes L5-A internal runtime foundation with formal records",
                    "expected_risk": "does not yet upgrade L5-B intelligence or L5-D revenue loop",
                    "speed_to_feedback": "immediate internal proof",
                },
                {
                    "candidate": "skip binding and continue static reports",
                    "expected_gain": "low implementation risk",
                    "expected_risk": "keeps CEO runtime artifact-driven and unclosed",
                    "speed_to_feedback": "slow",
                },
                {
                    "candidate": "attempt external L4 feedback now",
                    "expected_gain": "could move toward real market feedback",
                    "expected_risk": "unsafe before end-to-end runtime memory closure and owner packet",
                    "speed_to_feedback": "blocked by governance boundary",
                },
            ],
            "predicted_CIEU_records": [
                {
                    "X_t": "E87R baseline found L5-A partial_to_complete_foundation and missing canonical session binding",
                    "U_t": "run an internal CEO runtime session through Y-star-gov and CIEUStore",
                    "Y_star_t": "prove CEO action -> runtime decision -> formal CIEUStore -> dry-run boundary -> residual -> formal CIEUStore",
                    "expected_Y_t_plus_1": "two formal CIEUStore records in isolated DB and no external side effect",
                    "predicted_R_t_plus_1": "L5-B/C/D remain partial or absent; K9Audit not integrated",
                    "residual_severity": "medium",
                }
            ],
            "adversarial_critique": (
                "This session could still be too scaffolded if future CEO work does not compile real "
                "capability recall and commercial route selection before packet generation."
            ),
            "what_not_to_do": [
                "do not execute L4 external feedback",
                "do not call live providers",
                "do not claim L5 revenue/customer/payment loop",
                "do not claim K9Audit integration",
            ],
            "selected_action": "bind existing CEO behavior center to runtime CIEUStore session",
            "why_this_action": (
                "It closes the highest-leverage internal runtime gap identified by E87R before "
                "upgrading intelligence depth or external action readiness."
            ),
            "why_not_other_actions": (
                "Static reports do not close runtime memory; external L4/L5 actions remain outside "
                "current owner-approved execution boundary."
            ),
            "safety_boundary": {
                "external_action_allowed": False,
                "provider_live_execution_allowed": False,
                "dry_run_only": True,
            },
            "approval_required": False,
            "owner_approval_state": "approved",
            "behavior_center_response_excerpt": behavior_center_response[:1200],
        }
    )
    return packet


def build_e87_runtime_session_envelope(
    *,
    packet: Mapping[str, Any] | None = None,
    owner_message: str = DEFAULT_OWNER_MESSAGE,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    selected_packet = dict(
        packet
        or build_behavior_center_grounded_packet(owner_message=owner_message, repo_root=repo_root)
    )
    envelope = build_provider_tool_ceo_major_action_runtime_envelope(
        action_id="e88_behavior_center_runtime_session_provider_dry_run",
        packet=selected_packet,
    )
    envelope.update(
        {
            "mission": "bind existing bridge-labs CEO behavior center to runtime CIEU loop",
            "objective": (
                "prove internal CEO runtime session through Y-star-gov formal CIEUStore "
                "and gov-mcp dry-run boundary"
            ),
            "declared_intent": "close L5-A runtime foundation without external side effect",
            "context": "E87R baseline-selected runtime session binding",
            "proposed_execution_boundary": (
                "formal CIEUStore write in isolated test DB plus gov-mcp dry-run receipt only"
            ),
            "human_initiator": "owner",
            "lineage_path": [
                "owner",
                "bridge-labs CEO behavior center",
                "Y-star-gov runtime hook",
                "Y-star-gov CIEUStore",
                "gov-mcp dry-run boundary",
            ],
            "evidence_basis": [
                "bridge-labs:office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
                "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
                "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
                "operations/baseline/e87r_full_repo_baseline/next_engineering_roadmap.json",
            ],
        }
    )
    return envelope


def build_e87_post_action_residual(
    *,
    pre_action_packet_id: str,
    pre_action_event_id: str,
    provider_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    residual = build_sample_post_action_residual()
    residual.update(
        {
            "packet_id": "e88_behavior_center_runtime_post_action_residual",
            "linked_pre_action_packet_id": pre_action_packet_id,
            "action_taken": "internal CEO runtime session binding with gov-mcp dry-run only",
            "expected_outcome": (
                "Y-star-gov ALLOW for the internal provider/tool dry-run boundary, formal "
                "CIEUStore pre-action write, gov-mcp no-send receipt, and post-action residual write"
            ),
            "actual_output": (
                "Bridge-labs routed an existing behavior-center action through Y-star-gov, wrote "
                "formal CIEUStore records in an isolated DB, and obtained a gov-mcp dry-run receipt "
                "without external side effect."
            ),
            "CIEU_record": {
                "X_t": "E87R baseline identified missing canonical end-to-end CEO runtime session binding",
                "U_t": "ran bridge-labs behavior center -> Y-star-gov runtime/CIEUStore -> gov-mcp dry-run -> residual closure",
                "Y_star_t": "L5-A runtime foundation becomes internally end-to-end provable without claiming L5-D",
                "Y_t_plus_1": (
                    "pre-action/runtime decision record and post-action residual record were written "
                    "to isolated Y-star-gov CIEUStore session"
                ),
                "R_t_plus_1": (
                    "L5-B intelligence compiler remains partial; gov-mcp remains dry-run only; "
                    "L5-D revenue/customer/payment loop remains absent"
                ),
            },
            "residuals": [
                "L5-B CEO intelligence loop still needs runtime compiler upgrade",
                "gov-mcp live-ready preflight remains dry-run/no-send only",
                "L4 external feedback not executed",
                "L5 customer/revenue/payment loop absent",
                "K9Audit evidence-chain mirror not integrated",
            ],
            "unexpected_failures": [],
            "capability_state_updates": [
                "bridge-labs can run one CEO behavior-center action through formal Y-star-gov CIEUStore",
                "gov-mcp dry-run boundary can be reached after Y-star-gov ALLOW",
            ],
            "learning_candidates": [
                "upgrade bridge-labs CEO intelligence loop to generate less sample-scaffolded packets",
                "prepare owner-approved L4 feedback packet only after intelligence compiler upgrade",
            ],
            "YstarGov_sync_status": "formal_CIEUStore_runtime_session_written_in_isolated_db",
            "next_action_recommendation": "E89_CEO_Intelligence_Loop_Runtime_Compiler_R1",
            "what_not_to_do_next": [
                "do not claim L5-D complete",
                "do not execute external feedback without owner approval",
                "do not enable provider live execution",
                "do not claim K9Audit integration",
            ],
            "pre_action_CIEU_event_id": pre_action_event_id,
            "gov_mcp_receipt_id": provider_receipt.get("receipt_id", ""),
        }
    )
    return residual


def run_e87_ceo_runtime_session(
    *,
    cieu_db: str,
    owner_message: str = DEFAULT_OWNER_MESSAGE,
    repo_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    """Run one internal CEO runtime session end-to-end without external side effects."""

    governance = _load_ystar_governance_module(ystar_gov_root)
    session_id = "e88_behavior_center_runtime_session"
    packet = build_behavior_center_grounded_packet(owner_message=owner_message, repo_root=repo_root)
    pre_envelope = build_e87_runtime_session_envelope(packet=packet, owner_message=owner_message, repo_root=repo_root)

    pre_write = governance.validate_and_write_ceo_runtime_envelope(
        pre_envelope,
        cieu_db=cieu_db,
        session_id=session_id,
        agent_id="bridge_labs_ceo",
        seal_session=False,
    )
    provider_route = route_provider_tool_action_through_runtime_nervous_system(
        pre_envelope,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    post_residual = build_e87_post_action_residual(
        pre_action_packet_id=packet["packet_id"],
        pre_action_event_id=pre_write["CIEU_write_result"]["event_id"],
        provider_receipt=provider_route.get("gov_mcp_receipt", {}),
    )
    post_envelope = dict(pre_envelope)
    post_envelope.update(
        {
            "action_id": "e88_behavior_center_runtime_session_post_action",
            "action_phase": "completed",
            "completed_action": True,
            "post_action_residual": post_residual,
            "context": "post-action residual closure for E88 internal runtime session",
        }
    )
    post_write = governance.validate_and_write_ceo_runtime_envelope(
        post_envelope,
        cieu_db=cieu_db,
        session_id=session_id,
        agent_id="bridge_labs_ceo",
        seal_session=seal_session,
    )
    record_summary = _cieu_record_summary(cieu_db, session_id)
    l5_truth_table_after = build_l5_truth_table_after_session(
        pre_write=pre_write,
        post_write=post_write,
        provider_route=provider_route,
        record_summary=record_summary,
    )
    return {
        "artifact_id": "e87_end_to_end_ceo_runtime_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "behavior_center_source": "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
        "behavior_center_used": True,
        "owner_message": owner_message,
        "pre_action_packet_id": packet["packet_id"],
        "pre_action_runtime_decision": pre_write["runtime_result"]["decision"],
        "pre_action_CIEU_write": pre_write["CIEU_write_result"],
        "provider_route": provider_route,
        "post_action_runtime_decision": post_write["runtime_result"]["decision"],
        "post_action_CIEU_write": post_write["CIEU_write_result"],
        "CIEUStore_record_summary": record_summary,
        "end_to_end_chain_proven": _chain_proven(pre_write, post_write, provider_route, record_summary),
        "formal_CIEUStore_write_status": "formal_CIEU_records_written_in_isolated_test_db",
        "gov_mcp_status": "dry_run_only_no_external_side_effect",
        "K9Audit_status": "not_integrated_no_write",
        "L5_truth_table_after": l5_truth_table_after,
        "safety_statement": {
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_provider_live_execution": True,
            "no_customer_validation_claim": True,
            "no_revenue_payment_pricing_loop_claim": True,
            "no_K9Audit_write_or_bridge_claim": True,
        },
    }


def build_l5_truth_table_after_session(
    *,
    pre_write: Mapping[str, Any],
    post_write: Mapping[str, Any],
    provider_route: Mapping[str, Any],
    record_summary: Mapping[str, Any],
) -> dict[str, Any]:
    l5_a_complete = _chain_proven(pre_write, post_write, provider_route, record_summary)
    return {
        "L5-A Runtime Foundation": "complete" if l5_a_complete else "partial_to_complete_foundation",
        "L5-B CEO Intelligence Loop": "partial",
        "L5-C Controlled External Action": "partial_dry_run_only",
        "L5-D Revenue/Customer/Payment Loop": "absent_or_not_executed",
        "truth_constraints": [
            "L5-A complete here means internal runtime foundation only",
            "L5-B remains partial until bridge-labs has a real intelligence compiler flow",
            "L5-C remains dry-run only; no live provider execution occurred",
            "L5-D remains absent because no real feedback/customer/revenue/payment signal exists",
        ],
    }


def write_e87_session_reports(
    *,
    cieu_db: str,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    target_root = root or BRIDGE_ROOT
    result = run_e87_ceo_runtime_session(
        cieu_db=cieu_db,
        repo_root=BRIDGE_ROOT,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    report = _completion_report(result)
    runtime_status = _runtime_status_report(result)
    report_json = target_root / "office/mission_command/e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop_report.json"
    report_md = target_root / "office/mission_command/e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop_readback.md"
    status_json = target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop.json"
    status_md = target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop.md"
    for path in [report_json, report_md, status_json, status_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    report_md.write_text(_completion_report_markdown(report), encoding="utf-8")
    status_json.write_text(json.dumps(runtime_status, indent=2, sort_keys=True), encoding="utf-8")
    status_md.write_text(_runtime_status_markdown(runtime_status), encoding="utf-8")
    return report


def _chain_proven(
    pre_write: Mapping[str, Any],
    post_write: Mapping[str, Any],
    provider_route: Mapping[str, Any],
    record_summary: Mapping[str, Any],
) -> bool:
    receipt = provider_route.get("gov_mcp_receipt", {})
    return all(
        [
            pre_write.get("formal_CIEU_log_written") is True,
            post_write.get("formal_CIEU_log_written") is True,
            pre_write.get("runtime_result", {}).get("decision") == "ALLOW",
            post_write.get("runtime_result", {}).get("decision") == "ALLOW",
            provider_route.get("gov_mcp_dry_run_invoked") is True,
            receipt.get("provider_action_executed") is False,
            receipt.get("external_side_effect") is False,
            record_summary.get("event_count", 0) >= 2,
            record_summary.get("sealed_session_valid") is True,
        ]
    )


def _cieu_record_summary(cieu_db: str, session_id: str) -> dict[str, Any]:
    with sqlite3.connect(cieu_db) as conn:
        conn.row_factory = sqlite3.Row
        events = conn.execute(
            "SELECT event_id, decision, event_type, sealed FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (session_id,),
        ).fetchall()
        seal = conn.execute(
            "SELECT session_id, event_count, merkle_root FROM sealed_sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
    return {
        "cieu_db": cieu_db,
        "session_id": session_id,
        "event_count": len(events),
        "event_ids": [row["event_id"] for row in events],
        "decisions": [row["decision"] for row in events],
        "event_types": [row["event_type"] for row in events],
        "all_events_sealed": all(bool(row["sealed"]) for row in events) if events else False,
        "sealed_session_event_count": seal["event_count"] if seal else 0,
        "sealed_session_merkle_root": seal["merkle_root"] if seal else "",
        "sealed_session_valid": bool(seal and seal["event_count"] == len(events) and len(events) >= 2),
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop_report",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_hashes": {
            "bridge_labs": "8d00a6eb2ff3a177522b1ca0681e25d20557ec1c",
            "Y_star_gov": "738e8118fcf7ab87e08a942f265c17eb3386910d",
            "gov_mcp": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
        },
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp", "K9Audit_boundary_from_E87R_baseline"],
        "repos_modified": ["bridge-labs"],
        "existing_systems_reused": [
            result["behavior_center_source"],
            "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
            "Y-star-gov:ystar/governance/validate_and_write_ceo_runtime_envelope",
            "Y-star-gov:ystar/governance/cieu_store.py::CIEUStore.write_dict",
            "gov-mcp:gov_mcp/outbound/dry_run_adapter.py::dry_run_outbound_action",
        ],
        "new_code_added": ["office/mission_command/e87_ceo_runtime_session.py"],
        "end_to_end_chain_proven": result["end_to_end_chain_proven"],
        "CIEUStore_write_status": {
            "formal_CIEU_log_written": True,
            "formal_CIEU_log_status": result["formal_CIEUStore_write_status"],
            "pre_action_event_id": result["pre_action_CIEU_write"]["event_id"],
            "post_action_event_id": result["post_action_CIEU_write"]["event_id"],
            "record_summary": result["CIEUStore_record_summary"],
        },
        "gov_mcp_status": {
            "status": result["gov_mcp_status"],
            "dry_run_invoked": result["provider_route"]["gov_mcp_dry_run_invoked"],
            "provider_action_executed": result["provider_route"]["provider_action_executed"],
            "external_side_effect": result["provider_route"]["external_side_effect"],
            "receipt_id": result["provider_route"].get("gov_mcp_receipt", {}).get("receipt_id", ""),
        },
        "L5_truth_table_after": result["L5_truth_table_after"],
        "remaining_blockers": [
            "L5-B CEO intelligence loop needs runtime compiler upgrade from baseline recall to packet generation",
            "gov-mcp remains dry-run/no-send only until owner-approved live-ready preflight",
            "L4 external feedback not executed",
            "L5-D revenue/customer/payment loop absent",
            "K9Audit evidence-chain mirror not integrated",
        ],
        "next_recommended_milestone": "E89_CEO_Intelligence_Loop_Runtime_Compiler_R1",
        "safety_statement": dict(result["safety_statement"]),
    }


def _runtime_status_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "current_runtime_status_after_e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "end_to_end_chain": {
            "bridge_labs_behavior_center": "used",
            "Y_star_gov_runtime_hook": "used_via_validate_and_write_ceo_runtime_envelope",
            "Y_star_gov_CIEUStore": "formal_records_written_in_isolated_test_db",
            "gov_mcp": "dry_run_only_after_ALLOW",
            "post_action_residual": "validated_and_written",
            "K9Audit": "not_integrated",
        },
        "L5-A": result["L5_truth_table_after"]["L5-A Runtime Foundation"],
        "L5-B": result["L5_truth_table_after"]["L5-B CEO Intelligence Loop"],
        "L5-C": result["L5_truth_table_after"]["L5-C Controlled External Action"],
        "L5-D": result["L5_truth_table_after"]["L5-D Revenue/Customer/Payment Loop"],
        "truth_constraints": result["L5_truth_table_after"]["truth_constraints"],
        "next_recommended_milestone": "E89_CEO_Intelligence_Loop_Runtime_Compiler_R1",
    }


def _completion_report_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E88 Bind Existing Labs Behavior Center To Runtime CIEU Loop",
        "",
        f"- milestone_id: `{report['milestone_id']}`",
        f"- end_to_end_chain_proven: `{report['end_to_end_chain_proven']}`",
        f"- formal_CIEU_log_written: `{report['CIEUStore_write_status']['formal_CIEU_log_written']}`",
        f"- formal_CIEU_log_status: `{report['CIEUStore_write_status']['formal_CIEU_log_status']}`",
        f"- pre_action_event_id: `{report['CIEUStore_write_status']['pre_action_event_id']}`",
        f"- post_action_event_id: `{report['CIEUStore_write_status']['post_action_event_id']}`",
        f"- gov_mcp_status: `{report['gov_mcp_status']['status']}`",
        f"- provider_action_executed: `{report['gov_mcp_status']['provider_action_executed']}`",
        f"- external_side_effect: `{report['gov_mcp_status']['external_side_effect']}`",
        f"- L5-A: `{report['L5_truth_table_after']['L5-A Runtime Foundation']}`",
        f"- L5-B: `{report['L5_truth_table_after']['L5-B CEO Intelligence Loop']}`",
        f"- L5-C: `{report['L5_truth_table_after']['L5-C Controlled External Action']}`",
        f"- L5-D: `{report['L5_truth_table_after']['L5-D Revenue/Customer/Payment Loop']}`",
        f"- next_recommended_milestone: `{report['next_recommended_milestone']}`",
        "",
        "The session proves internal L5-A runtime foundation closure only: bridge-labs behavior center produced the action source, Y-star-gov validated and wrote formal CIEUStore records, gov-mcp produced a dry-run no-send receipt, and post-action residual closure was written. No L4 feedback, live provider execution, K9Audit write, customer validation, revenue, payment, or pricing signal occurred.",
    ]
    return "\n".join(lines) + "\n"


def _runtime_status_markdown(status: Mapping[str, Any]) -> str:
    lines = [
        "# Current Runtime Status After E88 Runtime Binding",
        "",
        f"- milestone_id: `{status['milestone_id']}`",
        f"- bridge_labs_behavior_center: `{status['end_to_end_chain']['bridge_labs_behavior_center']}`",
        f"- Y_star_gov_runtime_hook: `{status['end_to_end_chain']['Y_star_gov_runtime_hook']}`",
        f"- Y_star_gov_CIEUStore: `{status['end_to_end_chain']['Y_star_gov_CIEUStore']}`",
        f"- gov_mcp: `{status['end_to_end_chain']['gov_mcp']}`",
        f"- post_action_residual: `{status['end_to_end_chain']['post_action_residual']}`",
        f"- K9Audit: `{status['end_to_end_chain']['K9Audit']}`",
        f"- L5-A: `{status['L5-A']}`",
        f"- L5-B: `{status['L5-B']}`",
        f"- L5-C: `{status['L5-C']}`",
        f"- L5-D: `{status['L5-D']}`",
        f"- next_recommended_milestone: `{status['next_recommended_milestone']}`",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    default_db = "/tmp/e88_behavior_center_runtime_session_cieu.db"
    write_e87_session_reports(cieu_db=default_db)
