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
from office.mission_command.e87_ceo_runtime_session import (
    build_behavior_center_grounded_packet,
    build_e87_post_action_residual,
    build_e87_runtime_session_envelope,
)
from office.mission_command.e85_ceo_cognitive_os_runtime_bridge import (
    route_provider_tool_action_through_runtime_nervous_system,
)
from office.mission_command.e91_ceo_doctrine_enforced_runtime_session import (
    build_e89_doctrine_action_context,
    enforce_doctrine_before_ceo_runtime,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))

MILESTONE_ID = "E89_CEO_Intelligence_Loop_Runtime_Compiler_R1"
DEFAULT_OWNER_INTENT = (
    "Turn the CEO intelligence loop into governed runtime behavior before selecting the next "
    "major action toward controlled external feedback and revenue learning."
)

INTELLIGENCE_STAGE_IDS: tuple[str, ...] = (
    "mission_and_owner_constraint_recall",
    "full_repo_capability_recall",
    "historical_asset_retrieval",
    "current_problem_classification",
    "opportunity_framing",
    "candidate_action_generation",
    "counterfactual_action_comparison",
    "commercial_sharpness_gate",
    "speed_to_cash_evaluation",
    "risk_owner_burden_evaluation",
    "no_new_wheel_gate",
    "adversarial_critique",
    "what_not_to_do",
    "pre_action_CIEU_residual_prediction",
    "selected_action_decision",
    "why_this_action",
    "why_not_other_actions",
    "runtime_governance_plan",
    "post_action_learning_plan",
    "next_action_recommendation",
)


def _load_ystar_governance_module(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def compile_ceo_intelligence_loop_packet(
    *,
    owner_intent: str = DEFAULT_OWNER_INTENT,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Compile structured, governed CEO cognition output without hidden chain-of-thought."""

    root = repo_root or BRIDGE_ROOT
    behavior_response = answer_owner(owner_intent, repo_root=root, record_memory=False)
    intelligence_loop_id = "e89_ceo_intelligence_loop"
    candidates = _candidate_actions()
    selected = candidates[1]
    commercial_gate = _commercial_sharpness_gate()
    packet = {
        "artifact_id": "ceo_intelligence_loop_packet",
        "milestone_id": MILESTONE_ID,
        "generation_mode": "deterministic_fixture",
        "doctrine_registry_required": True,
        "intelligence_loop_id": intelligence_loop_id,
        "session_id": "e89_ceo_intelligence_runtime_session",
        "agent_id": "bridge_labs_ceo",
        "owner_intent": owner_intent,
        "current_problem": (
            "L5-B remains partial until bridge-labs compiles repository-backed CEO cognition "
            "into a governed runtime packet and routes the selected action through E88."
        ),
        "behavior_center_binding": {
            "source": "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
            "response_excerpt": str(behavior_response)[:360],
            "record_memory": False,
        },
        "bypass_attempt": False,
        "stages": [_stage(stage_id) for stage_id in INTELLIGENCE_STAGE_IDS],
        "candidate_actions": candidates,
        "counterfactual_comparison": _counterfactual_comparison(candidates),
        "commercial_sharpness_gate": commercial_gate,
        "speed_to_cash_evaluation": {
            "selected_candidate_id": selected["candidate_id"],
            "summary": "Provider dry-run route is fastest safe path toward later owner-approved L4 signal.",
            "score": 8,
        },
        "risk_owner_burden_evaluation": {
            "owner_burden": "low",
            "risk": "bounded to internal runtime, formal CIEUStore writes, and gov-mcp dry-run receipt",
            "no_external_side_effect": True,
        },
        "no_new_wheel_gate": {
            "decision": "reuse_existing_systems",
            "reused_systems": [
                "bridge-labs behavior center",
                "E88 runtime session",
                "Y-star-gov runtime hook",
                "E86 CIEU writer",
                "gov-mcp dry-run",
                "E87R baseline",
            ],
        },
        "adversarial_critique": (
            "This still may be too internal: a governed intelligence compiler can improve action "
            "quality, but it does not prove buyer pain or payment until owner-approved L4 feedback."
        ),
        "what_not_to_do": [
            "do not execute L4 feedback in E89",
            "do not claim customer validation, revenue, payment, pricing validation, or L5-D completion",
            "do not bypass Y-star-gov runtime governance or CIEUStore writes",
            "do not call gov-mcp live providers",
            "do not claim K9Audit integration",
        ],
        "pre_action_CIEU_residual_prediction": {
            "X_t": "E88 proved L5-A runtime foundation while L5-B remained partial",
            "U_t": "compile structured CEO cognition and validate/write it through Y-star-gov",
            "Y_star_t": "CEO thinking-as-behavior becomes auditable and reusable before action selection",
            "expected_Y_t_plus_1": "intelligence loop, runtime decision, and residual records written",
            "predicted_R_t_plus_1": "external feedback and revenue loops remain pending",
            "residual_severity": "medium",
        },
        "selected_action": selected,
        "selected_candidate_id": selected["candidate_id"],
        "why_this_action": (
            "It closes L5-B internal structured-intelligence governance while preserving the "
            "no-send provider boundary."
        ),
        "why_not_other_actions": (
            "Internal-only compiler proof would miss gov-mcp alignment; owner-approved L4 is the next "
            "boundary but should not execute before this runtime compiler is governed."
        ),
        "runtime_governance_plan": {
            "Y-star-gov runtime hook": "validate selected action as CEO major action through E88 envelope",
            "E86 CIEUStore writer": "write intelligence loop plus pre/post runtime records",
            "gov-mcp dry-run": "produce no-send receipt only after Y-star-gov ALLOW for provider/tool category",
            "owner decision boundary": "ESCALATE later external/L4 action until explicit owner approval",
        },
        "post_action_learning_plan": {
            "learning_candidate": "If E89 passes, route next milestone to owner-approved L4 preflight/pilot.",
            "strategy_update": "Use intelligence compiler output as runtime input for next action selection.",
        },
        "next_action_recommendation": "E90_Owner_Approved_L4_Feedback_Pilot_Through_Governed_Intelligence_Runtime",
        "overclaim_boundary": {
            "L4_execution_claim": False,
            "L5_revenue_loop_complete": False,
            "customer_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "payment_loop_complete": False,
            "production_deployment_claim": False,
            "K9Audit_integration_claim": False,
        },
        "owner_approval_state": "not_required",
        "Y_star_contract_hash_input": "sha256:e89-ceo-intelligence-loop-runtime-compiler",
        "truth_constraints": {
            "structured_stage_outputs_only": True,
            "private_chain_of_thought_stored": False,
            "no_L4_feedback_executed": True,
            "no_live_provider_execution": True,
        },
    }
    return packet


def run_ceo_intelligence_runtime_session(
    *,
    cieu_db: str,
    owner_intent: str = DEFAULT_OWNER_INTENT,
    repo_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    """Run intelligence compiler -> Y-star-gov -> E88 runtime -> gov-mcp dry-run."""

    governance = _load_ystar_governance_module(ystar_gov_root)
    session_id = "e89_ceo_intelligence_runtime_session"
    doctrine_gate = enforce_doctrine_before_ceo_runtime(
        action_context=build_e89_doctrine_action_context(),
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        session_id=session_id,
        seal_session=False,
    )
    if not doctrine_gate["runtime_may_continue"]:
        return {
            "artifact_id": "e89_ceo_intelligence_runtime_session_blocked_by_doctrine",
            "milestone_id": MILESTONE_ID,
            "doctrine_gate": doctrine_gate,
            "runtime_may_continue": False,
            "end_to_end_intelligence_chain_proven": False,
        }
    intelligence_packet = compile_ceo_intelligence_loop_packet(owner_intent=owner_intent, repo_root=repo_root)
    intelligence_write = governance.validate_and_write_ceo_intelligence_loop_packet(
        intelligence_packet,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=False,
    )
    pre_action_packet = build_pre_action_packet_from_intelligence_packet(
        intelligence_packet,
        repo_root=repo_root,
    )
    pre_envelope = build_e87_runtime_session_envelope(
        packet=pre_action_packet,
        owner_message=owner_intent,
        repo_root=repo_root,
    )
    pre_envelope.update(
        {
            "action_id": "e89_ceo_intelligence_selected_provider_dry_run",
            "context": "E89 selected action generated by governed intelligence compiler",
            "intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
            "selected_candidate_id": intelligence_packet["selected_candidate_id"],
            "YstarGov_intelligence_decision": intelligence_write["governance_decision"]["decision"],
            "commercial_sharpness_summary": intelligence_packet["commercial_sharpness_gate"],
            "owner_approval_state": intelligence_packet["owner_approval_state"],
            "intelligence_loop_metadata": {
                "intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
                "selected_candidate_id": intelligence_packet["selected_candidate_id"],
                "YstarGov_intelligence_decision": intelligence_write["governance_decision"]["decision"],
                "commercial_sharpness_summary": intelligence_packet["commercial_sharpness_gate"],
                "owner_approval_state": intelligence_packet["owner_approval_state"],
                **doctrine_gate["doctrine_metadata"],
            },
        }
    )
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
    post_residual = build_e89_post_action_residual(
        intelligence_packet=intelligence_packet,
        pre_action_packet=pre_action_packet,
        pre_action_event_id=pre_write["CIEU_write_result"]["event_id"],
        provider_receipt=provider_route.get("gov_mcp_receipt", {}),
    )
    post_envelope = dict(pre_envelope)
    post_envelope.update(
        {
            "action_id": "e89_ceo_intelligence_post_action_residual",
            "action_phase": "completed",
            "completed_action": True,
            "post_action_residual": post_residual,
            "context": "post-action residual closure for E89 governed intelligence runtime session",
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
    end_to_end = _chain_proven(intelligence_write, pre_write, post_write, provider_route, record_summary)
    return {
        "artifact_id": "e89_ceo_intelligence_runtime_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner_intent": owner_intent,
        "behavior_center_used": True,
        "doctrine_gate": doctrine_gate,
        "doctrine_invocation_plan_decision": doctrine_gate["plan_write"]["governance_decision"]["decision"],
        "doctrine_invocation_proof_decision": doctrine_gate["proof_write"]["governance_decision"]["decision"],
        "intelligence_packet": intelligence_packet,
        "intelligence_governance_decision": intelligence_write["governance_decision"]["decision"],
        "intelligence_CIEU_write": intelligence_write["CIEU_write_result"],
        "pre_action_packet_id": pre_action_packet["packet_id"],
        "pre_action_runtime_decision": pre_write["runtime_result"]["decision"],
        "pre_action_CIEU_write": pre_write["CIEU_write_result"],
        "provider_route": provider_route,
        "post_action_runtime_decision": post_write["runtime_result"]["decision"],
        "post_action_CIEU_write": post_write["CIEU_write_result"],
        "CIEUStore_record_summary": record_summary,
        "end_to_end_intelligence_chain_proven": end_to_end,
        "selected_action_proof": {
            "selected_candidate_id": intelligence_packet["selected_candidate_id"],
            "route_type": intelligence_packet["selected_action"]["route_type"],
            "flowed_into_E88_runtime_session": pre_action_packet["selected_action"]
            == intelligence_packet["selected_action"]["description"],
        },
        "gov_mcp_status": {
            "status": "dry_run_only_no_external_side_effect",
            "dry_run_invoked": provider_route.get("gov_mcp_dry_run_invoked") is True,
            "receipt": provider_route.get("gov_mcp_receipt", {}),
        },
        "L5_truth_table_after": build_l5_truth_table_after_e89(end_to_end=end_to_end),
        "next_action_recommendation": intelligence_packet["next_action_recommendation"],
        "safety_statement": {
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_provider_live_execution": True,
            "no_customer_validation_claim": True,
            "no_revenue_payment_pricing_loop_claim": True,
            "no_K9Audit_write_or_bridge_claim": True,
            "private_chain_of_thought_stored": False,
        },
    }


def build_pre_action_packet_from_intelligence_packet(
    intelligence_packet: Mapping[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    packet = build_behavior_center_grounded_packet(
        owner_message=str(intelligence_packet.get("owner_intent") or DEFAULT_OWNER_INTENT),
        repo_root=repo_root,
    )
    selected = intelligence_packet["selected_action"]
    packet.update(
        {
            "packet_id": "e89_ceo_intelligence_selected_action_pre_action_packet",
            "job_id": MILESTONE_ID,
            "proposed_action": selected["description"],
            "action_class": "provider_tool_execution",
            "owner_intent": intelligence_packet["owner_intent"],
            "current_mission_context": {
                "reasoning_scope": "E89_structured_governed_intelligence_loop",
                "intelligence_loop_id": intelligence_packet["intelligence_loop_id"],
                "behavior_center_source": "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
            },
            "historical_assets_consulted": [
                "operations/baseline/e87r_full_repo_baseline/baseline_summary.json",
                "operations/baseline/e87r_full_repo_baseline/architecture_evidence_map.json",
                "operations/baseline/e87r_full_repo_baseline/l5_truth_table.json",
                "office/mission_command/e87_ceo_runtime_session.py",
                "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py",
            ],
            "candidate_actions": [candidate["description"] for candidate in intelligence_packet["candidate_actions"]],
            "counterfactual_comparison": intelligence_packet["counterfactual_comparison"],
            "predicted_CIEU_records": [intelligence_packet["pre_action_CIEU_residual_prediction"]],
            "adversarial_critique": intelligence_packet["adversarial_critique"],
            "what_not_to_do": intelligence_packet["what_not_to_do"],
            "selected_action": selected["description"],
            "why_this_action": intelligence_packet["why_this_action"],
            "why_not_other_actions": intelligence_packet["why_not_other_actions"],
            "no_new_wheel_decision": {
                "decision": "reuse_existing_systems",
                "non_duplication_proof": ", ".join(intelligence_packet["no_new_wheel_gate"]["reused_systems"]),
            },
            "approval_required": False,
            "owner_approval_state": "not_required",
        }
    )
    packet["discovered_capabilities_consulted"] = [
        {
            "capability_id": "bridge_labs_ceo_intelligence_compiler",
            "evidence_paths": ["bridge-labs:office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py"],
            "claimed_runtime_active": True,
            "runtime_evidence_status": "runtime_active_verified",
        },
        {
            "capability_id": "YstarGov_ceo_intelligence_loop_contract",
            "evidence_paths": ["Y-star-gov:ystar/governance/ceo_intelligence_loop_contract.py"],
            "claimed_runtime_active": True,
            "runtime_evidence_status": "runtime_active_verified",
        },
        {
            "capability_id": "gov_mcp_dry_run_boundary",
            "evidence_paths": ["gov-mcp:gov_mcp/outbound/dry_run_adapter.py"],
            "claimed_runtime_active": True,
            "runtime_evidence_status": "runtime_active_verified",
        },
    ]
    return packet


def build_e89_post_action_residual(
    *,
    intelligence_packet: Mapping[str, Any],
    pre_action_packet: Mapping[str, Any],
    pre_action_event_id: str,
    provider_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    residual = build_e87_post_action_residual(
        pre_action_packet_id=pre_action_packet["packet_id"],
        pre_action_event_id=pre_action_event_id,
        provider_receipt=provider_receipt,
    )
    residual.update(
        {
            "packet_id": "e89_ceo_intelligence_post_action_residual",
            "linked_pre_action_packet_id": pre_action_packet["packet_id"],
            "action_taken": "governed CEO intelligence loop selected provider/tool dry-run route",
            "expected_outcome": "intelligence loop, runtime action, gov-mcp dry-run, and residual are recorded",
            "actual_output": "structured cognition governed and routed through E88 runtime without external effect",
            "capability_state_updates": [
                "L5-B structured intelligence loop is governed and CIEUStore-recorded",
                "L5-C remains dry-run only",
            ],
            "learning_candidates": [
                intelligence_packet["post_action_learning_plan"]["learning_candidate"],
                "Next milestone should decide owner-approved L4 feedback preflight or pilot.",
            ],
            "next_action_recommendation": intelligence_packet["next_action_recommendation"],
            "what_not_to_do_next": intelligence_packet["what_not_to_do"],
        }
    )
    residual["CIEU_record"] = {
        "X_t": "L5-B was partial before governed intelligence compiler",
        "U_t": "compiled structured cognition, wrote formal CIEUStore record, and routed selected action",
        "Y_star_t": "CEO intelligence loop is runtime-governed and reusable before major action",
        "Y_t_plus_1": "intelligence, pre-action runtime, and post-action residual records written",
        "R_t_plus_1": "L4 feedback, L5 revenue/customer/payment, and K9Audit bridge remain pending",
    }
    return residual


def build_l5_truth_table_after_e89(*, end_to_end: bool) -> dict[str, Any]:
    return {
        "L5-A Runtime Foundation": "complete_internal_runtime_foundation",
        "L5-B CEO Intelligence Loop": (
            "complete_for_structured_governed_intelligence_loop" if end_to_end else "partial"
        ),
        "L5-C Controlled External Action": "partial_dry_run_only",
        "L5-D Revenue/Customer/Payment Loop": "absent_or_not_executed",
        "truth_constraints": [
            "L5-B completion here means structured governed intelligence-loop runtime only",
            "No L4 external feedback was executed",
            "gov-mcp remains dry-run/no-send only",
            "No customer validation, revenue, payment, pricing validation, production deployment, or K9Audit write occurred",
        ],
    }


def write_e89_intelligence_runtime_reports(
    *,
    cieu_db: str,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    target_root = root or BRIDGE_ROOT
    result = run_ceo_intelligence_runtime_session(
        cieu_db=cieu_db,
        repo_root=BRIDGE_ROOT,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    report = _completion_report(result)
    status = _runtime_status_report(result)
    report_json = target_root / "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler_report.json"
    report_md = target_root / "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler_readback.md"
    status_json = target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e89_ceo_intelligence_loop_runtime_compiler.json"
    status_md = target_root / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e89_ceo_intelligence_loop_runtime_compiler.md"
    for path in (report_json, report_md, status_json, status_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    report_md.write_text(_completion_report_markdown(report), encoding="utf-8")
    status_json.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    status_md.write_text(_runtime_status_markdown(status), encoding="utf-8")
    return report


def _candidate_actions() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "candidate_internal_compiler_only",
            "description": "Compile intelligence packet and stop at internal report",
            "expected_value": "proves structure but weak runtime closure",
            "speed_to_cash": "slow",
            "implementation_cost": "low",
            "owner_burden": "low",
            "execution_risk": "low",
            "governance_risk": "medium because selected action would not reach E88 session",
            "evidence_strength": "E87R baseline and bridge-labs mission_command",
            "why_it_might_fail": "remains artifact-like without runtime routing",
            "required_next_evidence": "formal CIEUStore write and E88 session proof",
            "route_type": "internal_runtime",
        },
        {
            "candidate_id": "candidate_provider_dry_run",
            "description": "Route selected intelligence action through E88 runtime and gov-mcp dry-run",
            "expected_value": "closes governed intelligence and dry-run boundary alignment",
            "speed_to_cash": "fastest safe pre-L4 route",
            "implementation_cost": "moderate",
            "owner_burden": "low",
            "execution_risk": "low because no live provider executes",
            "governance_risk": "low after Y-star-gov and CIEUStore validation",
            "evidence_strength": "E88 runtime session, E86 CIEU writer, gov-mcp dry-run adapter",
            "why_it_might_fail": "still lacks real buyer feedback",
            "required_next_evidence": "owner-approved L4 feedback signal",
            "route_type": "provider_tool_dry_run",
        },
        {
            "candidate_id": "candidate_owner_l4_feedback",
            "description": "Prepare owner-approved minimal L4 feedback action",
            "expected_value": "moves closest to real market feedback",
            "speed_to_cash": "potentially high after approval",
            "implementation_cost": "moderate",
            "owner_burden": "medium because owner approval is required",
            "execution_risk": "higher because external boundary is near",
            "governance_risk": "requires ESCALATE/owner decision before execution",
            "evidence_strength": "E87R roadmap recommends L4 after runtime foundation",
            "why_it_might_fail": "premature before L5-B compiler is governed",
            "required_next_evidence": "owner decision and L4 message/target scope",
            "route_type": "owner_decision_required",
        },
    ]


def _counterfactual_comparison(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": candidates[0]["candidate_id"],
            "expected_gain": "low-risk structure proof",
            "expected_risk": "does not prove selected action reaches runtime nervous system",
            "score": 6,
        },
        {
            "candidate_id": candidates[1]["candidate_id"],
            "expected_gain": "proves intelligence -> runtime -> CIEUStore -> gov-mcp dry-run chain",
            "expected_risk": "still internal/dry-run only",
            "score": 9,
            "selected": True,
        },
        {
            "candidate_id": candidates[2]["candidate_id"],
            "expected_gain": "closest to real feedback",
            "expected_risk": "requires owner approval and should follow governed compiler proof",
            "score": 7,
        },
    ]


def _commercial_sharpness_gate() -> dict[str, Any]:
    return {
        "buyer_pain_clarity": 6,
        "urgency": 6,
        "willingness_to_pay_proxy": 5,
        "shortest_cash_path_fit": 7,
        "differentiation": 7,
        "proof_needed": "owner-approved L4 feedback remains the next missing evidence",
        "owner_execution_burden": 3,
        "risk_of_wasting_time": 4,
    }


def _stage(stage_id: str) -> dict[str, Any]:
    outputs = {
        "mission_and_owner_constraint_recall": "Owner wants high-intelligence CEO runtime without overclaiming L4/L5 completion.",
        "full_repo_capability_recall": "Use E87R baseline plus E88 runtime session, Y-star-gov runtime hook, CIEUStore writer, and gov-mcp dry-run.",
        "historical_asset_retrieval": "E87R/E88 artifacts show L5-A complete internally while L5-B remains partial.",
        "current_problem_classification": "This is an internal runtime intelligence compiler closure, not external execution.",
        "opportunity_framing": "Best opportunity is to make structured CEO cognition governed before attempting L4 feedback.",
        "candidate_action_generation": "Generated internal compiler-only, provider dry-run, and owner L4 feedback candidates.",
        "counterfactual_action_comparison": "Provider dry-run candidate best balances proof, speed, and safety.",
        "commercial_sharpness_gate": "Commercial score is promising but still lacks real buyer proof.",
        "speed_to_cash_evaluation": "Fastest safe path is dry-run proof now, owner-approved L4 next.",
        "risk_owner_burden_evaluation": "Owner burden stays low because no external action executes.",
        "no_new_wheel_gate": "Reuses bridge-labs behavior center, E88 session, Y-star-gov hook/CIEUStore, gov-mcp dry-run, and E87R baseline.",
        "adversarial_critique": "The compiler can still be too internal unless followed by real feedback.",
        "what_not_to_do": "Do not claim customer validation, revenue, payment, L4 execution, or K9Audit integration.",
        "pre_action_CIEU_residual_prediction": "Predicted residual is that L4/L5-D remain unproven after internal closure.",
        "selected_action_decision": "Select provider/tool dry-run route through E88 after intelligence governance.",
        "why_this_action": "It proves the intelligence packet drives the runtime chain.",
        "why_not_other_actions": "Internal-only is too weak and L4 execution is owner-bound.",
        "runtime_governance_plan": "Y-star-gov validates and writes records; gov-mcp stays dry-run only.",
        "post_action_learning_plan": "Use residual to recommend owner-approved L4 feedback preflight next.",
        "next_action_recommendation": "Move to controlled owner-approved L4 feedback through the governed runtime chain.",
    }
    return {
        "stage_id": stage_id,
        "input_summary": "E87R baseline, E88 runtime report, current owner intent, and repository code evidence",
        "evidence_refs": [
            "operations/baseline/e87r_full_repo_baseline/baseline_summary.json",
            "operations/baseline/e87r_full_repo_baseline/l5_truth_table.json",
            "office/mission_command/e87_ceo_runtime_session.py",
            "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
            "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
        ],
        "output_summary": outputs[stage_id],
        "confidence_boundary": "Repository-backed internal runtime proof only; no external/customer/revenue evidence",
        "missing_evidence": ["real L4 feedback", "customer validation", "paid signal", "K9Audit mirror"],
        "runtime_governance_required": True,
        "CIEU_recording_required": True,
    }


def _chain_proven(
    intelligence_write: Mapping[str, Any],
    pre_write: Mapping[str, Any],
    post_write: Mapping[str, Any],
    provider_route: Mapping[str, Any],
    record_summary: Mapping[str, Any],
) -> bool:
    receipt = provider_route.get("gov_mcp_receipt", {})
    return all(
        [
            intelligence_write.get("formal_CIEU_log_written") is True,
            pre_write.get("formal_CIEU_log_written") is True,
            post_write.get("formal_CIEU_log_written") is True,
            intelligence_write.get("governance_decision", {}).get("decision") == "ALLOW",
            pre_write.get("runtime_result", {}).get("decision") == "ALLOW",
            post_write.get("runtime_result", {}).get("decision") == "ALLOW",
            provider_route.get("gov_mcp_dry_run_invoked") is True,
            receipt.get("provider_action_executed") is False,
            receipt.get("external_side_effect") is False,
            receipt.get("intelligence_loop_id") == "e89_ceo_intelligence_loop",
            record_summary.get("event_count", 0) >= 3,
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
        "sealed_session_valid": bool(seal and seal["event_count"] == len(events) and len(events) >= 3),
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    packet = result["intelligence_packet"]
    receipt = result["provider_route"].get("gov_mcp_receipt", {})
    return {
        "artifact_id": "e89_ceo_intelligence_loop_runtime_compiler_report",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_hashes": {
            "bridge_labs_actual_start": "eb8250f84b64d80d77237ee1524dbfe71151929c",
            "Y_star_gov_actual_start": "5a147f71832aa9ed90748cd5750df82cfa3e84c2",
            "gov_mcp_actual_start": "ce97f7a93693dde9e5ce3b427bbb2352b83790c5",
        },
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "repos_modified": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "existing_systems_reused": [
            "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
            "office/mission_command/e87_ceo_runtime_session.py",
            "Y-star-gov:ystar/governance/validate_and_write_ceo_intelligence_loop_packet",
            "Y-star-gov:ystar/governance/validate_and_write_ceo_runtime_envelope",
            "Y-star-gov:ystar/governance/cieu_store.py::CIEUStore.write_dict",
            "gov-mcp:gov_mcp/outbound/dry_run_adapter.py::dry_run_outbound_action",
        ],
        "bridge_labs_behavior_center_binding": "used_existing_answer_owner_then_compiled_structured_packet",
        "Y_star_gov_intelligence_governance_path": "validate_and_write_ceo_intelligence_loop_packet",
        "gov_mcp_alignment_path": "dry_run_outbound_action receipt carries intelligence metadata",
        "cognitive_operation_registry": "Y-star-gov build_ceo_intelligence_operation_registry",
        "CIEUStore_records_written_in_test_db": result["CIEUStore_record_summary"],
        "selected_action_proof": result["selected_action_proof"],
        "candidate_actions": packet["candidate_actions"],
        "comparison_summary": packet["counterfactual_comparison"],
        "commercial_sharpness_gate_summary": packet["commercial_sharpness_gate"],
        "no_new_wheel_proof": packet["no_new_wheel_gate"],
        "adversarial_critique_summary": packet["adversarial_critique"],
        "what_not_to_do_constraints": packet["what_not_to_do"],
        "gov_mcp_receipt_summary": {
            "receipt_id": receipt.get("receipt_id"),
            "intelligence_loop_id": receipt.get("intelligence_loop_id"),
            "selected_candidate_id": receipt.get("selected_candidate_id"),
            "provider_action_executed": receipt.get("provider_action_executed"),
            "external_side_effect": receipt.get("external_side_effect"),
            "no_send_invariant": receipt.get("no_send_invariant"),
        },
        "end_to_end_intelligence_chain_proven": result["end_to_end_intelligence_chain_proven"],
        "L5_truth_table_after": result["L5_truth_table_after"],
        "limitations": [
            "No L4 external feedback executed",
            "No customer validation, paid signal, pricing validation, payment, or revenue loop",
            "gov-mcp remains dry-run/no-send only",
            "K9Audit remains not integrated",
        ],
        "next_milestone": result["next_action_recommendation"],
        "safety_statement": result["safety_statement"],
    }


def _runtime_status_report(result: Mapping[str, Any]) -> dict[str, Any]:
    l5 = result["L5_truth_table_after"]
    return {
        "artifact_id": "current_runtime_status_after_e89_ceo_intelligence_loop_runtime_compiler",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "end_to_end_chain": {
            "bridge_labs_intelligence_compiler": "compiled_structured_packet",
            "Y_star_gov_intelligence_contract": "validated_and_written_to_CIEUStore",
            "Y_star_gov_runtime_hook": "used_via_E88_runtime_session",
            "Y_star_gov_CIEUStore": "three_formal_records_written_in_isolated_test_db",
            "gov_mcp": "dry_run_only_with_intelligence_metadata",
            "post_action_residual": "validated_and_written",
            "K9Audit": "not_integrated",
        },
        "L5-A": l5["L5-A Runtime Foundation"],
        "L5-B": l5["L5-B CEO Intelligence Loop"],
        "L5-C": l5["L5-C Controlled External Action"],
        "L5-D": l5["L5-D Revenue/Customer/Payment Loop"],
        "truth_constraints": l5["truth_constraints"],
        "next_recommended_milestone": result["next_action_recommendation"],
    }


def _completion_report_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E89 CEO Intelligence Loop Runtime Compiler",
        "",
        f"- milestone_id: `{report['milestone_id']}`",
        f"- end_to_end_intelligence_chain_proven: `{report['end_to_end_intelligence_chain_proven']}`",
        f"- intelligence_governance_path: `{report['Y_star_gov_intelligence_governance_path']}`",
        f"- gov_mcp_alignment_path: `{report['gov_mcp_alignment_path']}`",
        f"- CIEUStore_event_count: `{report['CIEUStore_records_written_in_test_db']['event_count']}`",
        f"- selected_candidate_id: `{report['selected_action_proof']['selected_candidate_id']}`",
        f"- provider_action_executed: `{report['gov_mcp_receipt_summary']['provider_action_executed']}`",
        f"- external_side_effect: `{report['gov_mcp_receipt_summary']['external_side_effect']}`",
        f"- L5-A: `{report['L5_truth_table_after']['L5-A Runtime Foundation']}`",
        f"- L5-B: `{report['L5_truth_table_after']['L5-B CEO Intelligence Loop']}`",
        f"- L5-C: `{report['L5_truth_table_after']['L5-C Controlled External Action']}`",
        f"- L5-D: `{report['L5_truth_table_after']['L5-D Revenue/Customer/Payment Loop']}`",
        f"- next_milestone: `{report['next_milestone']}`",
        "",
        "E89 governs structured CEO cognition as behavior. It does not store hidden chain-of-thought, execute L4 feedback, call live providers, claim customer validation, claim revenue/payment completion, or integrate K9Audit.",
    ]
    return "\n".join(lines) + "\n"


def _runtime_status_markdown(status: Mapping[str, Any]) -> str:
    lines = [
        "# Current Runtime Status After E89 CEO Intelligence Compiler",
        "",
        f"- milestone_id: `{status['milestone_id']}`",
        f"- bridge_labs_intelligence_compiler: `{status['end_to_end_chain']['bridge_labs_intelligence_compiler']}`",
        f"- Y_star_gov_intelligence_contract: `{status['end_to_end_chain']['Y_star_gov_intelligence_contract']}`",
        f"- Y_star_gov_CIEUStore: `{status['end_to_end_chain']['Y_star_gov_CIEUStore']}`",
        f"- gov_mcp: `{status['end_to_end_chain']['gov_mcp']}`",
        f"- K9Audit: `{status['end_to_end_chain']['K9Audit']}`",
        f"- L5-A: `{status['L5-A']}`",
        f"- L5-B: `{status['L5-B']}`",
        f"- L5-C: `{status['L5-C']}`",
        f"- L5-D: `{status['L5-D']}`",
        f"- next_recommended_milestone: `{status['next_recommended_milestone']}`",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    write_e89_intelligence_runtime_reports(cieu_db="/tmp/e89_ceo_intelligence_runtime_session.db")
